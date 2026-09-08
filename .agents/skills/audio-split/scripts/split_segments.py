import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

from srt_timestamps import parse_srt, snap_cut

REFERENCE_DURATION = Decimal(30)
REFERENCE_BYTES = 10_000_000
MP3_PADDING_BUDGET = Decimal('0.08')


def number(value, label, positive=False):
    if len(value) > 64 or re.fullmatch(r'(?:\d+(?:\.\d*)?|\.\d+)', value) is None:
        raise ValueError(f'{label} must be a finite decimal number')
    result = Decimal(value)
    if result < 0 or (positive and result == 0):
        raise ValueError(f'{label} must be {"positive" if positive else "nonnegative"}')
    return result


def seconds(value):
    return format(value, '.9f').rstrip('0').rstrip('.') or '0'


def run(arguments):
    result = subprocess.run(arguments, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(f'{Path(arguments[0]).name} failed: {result.stderr.strip()}')
    return result.stdout


def probe_audio(path):
    metadata = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    audio = [item for item in metadata.get('streams', []) if item.get('codec_type') == 'audio']
    if not audio:
        raise ValueError(f'{path} has no audio stream')
    try:
        duration = Decimal(metadata.get('format', {}).get('duration', 'NaN'))
    except InvalidOperation as error:
        raise ValueError(f'could not read audio duration for {path}') from error
    if not duration.is_finite() or duration <= 0:
        raise ValueError(f'invalid audio duration for {path}')
    return duration


def validate_cuts(cuts, total):
    previous = Decimal(0)
    for cut in cuts:
        if not previous < cut < total:
            raise ValueError('cut points must be strictly increasing and inside the audio duration')
        previous = cut


def snap_backward(value, cues):
    while True:
        starts = [start for start, end, _ in cues if start < value < end]
        if not starts:
            return value
        value = min(starts)


def automatic_cuts(total, budget, overlap, cues):
    previous = Decimal(0)
    cuts: list[Decimal] = []
    while True:
        start = snap_backward(max(Decimal(0), previous - overlap), cues)
        if total - start <= budget:
            return cuts
        end = snap_backward(start + budget, cues)
        if end <= previous:
            raise ValueError('subtitle cue or overlap cannot fit inside the encoded duration limit')
        cuts.append(end)
        if len(cuts) >= 10000:
            raise ValueError('requested duration/overlap would create more than 10000 clips')
        previous = end


def boundaries(total, cuts, overlap, cues, budget=None):
    validate_cuts(cuts, total)
    previous = Decimal(0)
    segments = []
    for end in [*cuts, total]:
        start = snap_backward(max(Decimal(0), previous - overlap), cues)
        if end <= start or (budget is not None and end - start > budget):
            raise ValueError('subtitle snapping or overlap exceeds the encoded duration limit; use max-duration mode or revise cuts')
        segments.append((start, end))
        previous = end
    return segments


def arguments():
    parser = argparse.ArgumentParser(description='Split audio with validated encoded duration and size limits')
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--outdir')
    parser.add_argument('-b', '--boundary', action='append', default=[])
    parser.add_argument('-m', '--max-duration')
    parser.add_argument('-n', '--count')
    parser.add_argument('-s', '--srt')
    parser.add_argument('--overlap', default='0')
    parser.add_argument('--wav', action='store_true')
    parser.add_argument('--reference', action='store_true', help='enforce 30 seconds and 10 MB per encoded clip')
    parser.add_argument('--max-bytes', type=int, help='optional stricter encoded file-size cap')
    parser.add_argument('positional', nargs='*')
    args = parser.parse_intermixed_args()
    values = list(args.positional)
    args.input = args.input or (values.pop(0) if values else None)
    args.outdir = args.outdir or (values.pop(0) if values else None)
    args.boundary.extend(values)
    return args


def prepare(args):
    if not args.input or not args.outdir:
        raise ValueError('input audio file and output directory are required')
    source = Path(args.input).resolve()
    if not source.is_file():
        raise ValueError(f'file not found: {source}')
    overlap = number(args.overlap, 'overlap')
    maximum = number(args.max_duration, 'max duration', True) if args.max_duration is not None else None
    cuts = [number(value, 'cut point', True) for value in args.boundary]
    mode_count = int(maximum is not None) + int(args.count is not None) + int(bool(cuts))
    if mode_count > 1:
        raise ValueError('max-duration, count and explicit cut points are mutually exclusive')
    reference = args.reference or (maximum is not None and maximum <= REFERENCE_DURATION)
    if args.reference:
        if maximum is not None and maximum > REFERENCE_DURATION:
            raise ValueError('reference maximum cannot exceed 30 seconds')
        maximum = maximum or REFERENCE_DURATION
    size_limit = REFERENCE_BYTES if reference else None
    if args.max_bytes is not None:
        if args.max_bytes <= 0 or (reference and args.max_bytes > REFERENCE_BYTES):
            raise ValueError('max-bytes must be positive and cannot relax the 10 MB reference cap')
        size_limit = args.max_bytes
    budget = maximum - (Decimal(0) if args.wav else MP3_PADDING_BUDGET) if maximum is not None else None
    if budget is not None and (budget <= 0 or overlap >= budget):
        raise ValueError('overlap and codec padding must leave positive duration inside the maximum')
    for name in ('ffmpeg', 'ffprobe'):
        if shutil.which(name) is None:
            raise ValueError(f'{name} is required')
    total = probe_audio(source)
    cues = parse_srt(args.srt) if args.srt else []
    if any(end > total for _, end, _ in cues):
        raise ValueError('subtitle timestamps extend beyond the source audio')
    if args.count is not None:
        if not re.fullmatch(r'[1-9]\d*', args.count) or int(args.count) > 10000:
            raise ValueError('count must be an integer from 1 to 10000')
        count = int(args.count)
        cuts = [total * index / count for index in range(1, count)]
    elif not cuts and budget is not None:
        cuts = automatic_cuts(total, budget, overlap, cues)
    validate_cuts(cuts, total)
    if cues:
        cuts = [snap_cut(cut, cues) for cut in cuts]
    segments = boundaries(total, cuts, overlap, cues, budget)
    return source, segments, maximum, size_limit


def split(args):
    source, segments, maximum, size_limit = prepare(args)
    output = Path(args.outdir).absolute()
    output.mkdir(parents=True, exist_ok=True)
    extension = 'wav' if args.wav else 'mp3'
    targets = [output / f'seg{index}.{extension}' for index in range(1, len(segments) + 1)]
    targets.append(output / 'manifest.txt')
    for target in targets:
        if target.is_symlink() or target.resolve() == source or target.is_dir():
            raise ValueError(f'unsafe output target: {target}')
    with tempfile.TemporaryDirectory(prefix='.audio-split-', dir=output) as directory:
        staging = Path(directory)
        manifest = []
        for index, (start, end) in enumerate(segments, 1):
            candidate = staging / f'seg{index}.{extension}'
            codec = ['-c:a', 'pcm_s16le'] if args.wav else ['-c:a', 'libmp3lame', '-b:a', '320k']
            run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-ss', seconds(start), '-i', str(source),
                 '-map', '0:a:0', '-t', seconds(end - start), '-ac', '2', '-ar', '44100', *codec, str(candidate)])
            actual = probe_audio(candidate)
            size = candidate.stat().st_size
            if maximum is not None and actual > maximum:
                raise ValueError(f'{candidate.name}: actual encoded duration {actual}s exceeds {maximum}s; use WAV or a smaller maximum')
            if size_limit is not None and size > size_limit:
                raise ValueError(f'{candidate.name}: actual encoded size {size} bytes exceeds {size_limit} bytes')
            run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', str(candidate), '-map', '0:a:0', '-f', 'null', '-'])
            manifest.append(f'{candidate.name} offset={seconds(start)}s duration={seconds(actual)}s '
                            f'source_end={seconds(end)}s bytes={size}')
            if actual > REFERENCE_DURATION or size > REFERENCE_BYTES:
                manifest.append(f'WARNING: {candidate.name} exceeds the 30s/10MB reference limits; use --reference -m 30')
        (staging / 'manifest.txt').write_text('\n'.join(manifest) + '\n', encoding='utf-8')
        for target in targets:
            os.replace(staging / target.name, target)
    print('\n'.join(manifest))
    print(f'Segments: {len(segments)}\nManifest: {output / "manifest.txt"}')


def main():
    args = arguments()
    try:
        split(args)
    except (ValueError, OSError, InvalidOperation) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
