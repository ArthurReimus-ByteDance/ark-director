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

MUX_TOLERANCE = Decimal('0.1')
SAMPLE_TOLERANCE = Decimal(1) / Decimal(44100)


def decimal_argument(value, label, positive=False):
    if len(value) > 64 or re.fullmatch(r'(?:\d+(?:\.\d*)?|\.\d+)', value) is None:
        raise ValueError(f'{label} must be a finite decimal number')
    number = Decimal(value)
    if number < 0 or (positive and number == 0):
        raise ValueError(f'{label} must be {"positive" if positive else "nonnegative"}')
    if number > Decimal(2147483647):
        raise ValueError(f'{label} exceeds the supported numeric range')
    return number


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(f'{Path(command[0]).name} failed: {result.stderr.strip()}')
    return result.stdout


def require_tools():
    for name in ('ffmpeg', 'ffprobe'):
        if shutil.which(name) is None:
            raise ValueError(f'{name} is required')


def input_file(value):
    path = Path(value).resolve()
    if not path.is_file():
        raise ValueError(f'file not found: {value}')
    return path


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def stream(metadata, kind, path):
    matches = [item for item in metadata.get('streams', []) if item.get('codec_type') == kind]
    if not matches:
        raise ValueError(f'{path} has no {kind} stream')
    return matches[0]


def positive_duration(value, path):
    try:
        duration = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f'could not read duration for {path}') from error
    if not duration.is_finite() or duration <= 0:
        raise ValueError(f'invalid duration for {path}')
    return duration


def format_duration(metadata, path):
    return positive_duration(metadata.get('format', {}).get('duration'), path)


def stream_duration(metadata, path, kind):
    media_stream = stream(metadata, kind, path)
    if media_stream.get('duration') not in (None, 'N/A'):
        return positive_duration(media_stream['duration'], path)
    packets = json.loads(run([
        'ffprobe', '-v', 'error', '-select_streams', f'{kind[0]}:0', '-show_packets',
        '-show_entries', 'packet=pts_time,duration_time', '-of', 'json', str(path),
    ])).get('packets', [])
    spans = []
    for packet in packets:
        if packet.get('pts_time') is None or packet.get('duration_time') is None:
            raise ValueError(f'{kind} duration cannot be verified for {path}: missing packet timing')
        start = Decimal(packet['pts_time'])
        duration = positive_duration(packet['duration_time'], path)
        if not start.is_finite():
            raise ValueError(f'invalid packet timestamp for {path}')
        spans.append((start, start + duration))
    if not spans:
        raise ValueError(f'{kind} duration cannot be verified for {path}: no packets')
    return max(end for _, end in spans) - min(start for start, _ in spans)


def output_file(value, inputs):
    output = Path(value).absolute()
    if output.resolve() in inputs:
        raise ValueError('output must differ from every input file')
    if output.is_symlink():
        raise ValueError('output must not be a symlink')
    if not output.suffix:
        raise ValueError('output filename must have a media extension')
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def verify_duration(actual, target, tolerance, label):
    if abs(actual - target) > tolerance:
        raise ValueError(f'{label} duration {actual}s differs from target {target}s by more than {tolerance}s')


def mix(args):
    target = decimal_argument(args.source_duration, 'source duration', positive=True)
    segments = []
    for entry in args.segments:
        filename, separator, offset_text = entry.rpartition(':')
        if not separator or not filename:
            raise ValueError('segments must use file:offset_ms syntax')
        offset = decimal_argument(offset_text, 'segment offset')
        if offset >= target * 1000:
            raise ValueError('segment offset must precede the target duration')
        segments.append((input_file(filename), offset))
    require_tools()
    for path, _ in segments:
        metadata = probe(path)
        stream(metadata, 'audio', path)
        format_duration(metadata, path)
    output = output_file(args.output, [path for path, _ in segments])
    if output.suffix.lower() != '.wav':
        raise ValueError('mix output must use the .wav extension')
    arguments = ['ffmpeg', '-v', 'error', '-nostdin', '-y']
    filters = []
    for index, (path, offset) in enumerate(segments):
        arguments.extend(['-i', str(path)])
        filters.append(f'[{index}:a:0]adelay={offset}:all=1[a{index}]')
    inputs = ''.join(f'[a{index}]' for index in range(len(segments)))
    filters.append(f'{inputs}amix=inputs={len(segments)}:duration=longest:dropout_transition=0:'
                   f'normalize=0,apad=whole_dur={target}[out]')
    with tempfile.TemporaryDirectory(prefix='.audio-mix-', dir=output.parent) as directory:
        candidate = Path(directory) / 'mixed.wav'
        run([*arguments, '-filter_complex', ';'.join(filters), '-map', '[out]', '-ac', '2',
             '-ar', '44100', '-t', str(target), '-c:a', 'pcm_s16le', str(candidate)])
        metadata = probe(candidate)
        stream(metadata, 'audio', candidate)
        actual = format_duration(metadata, candidate)
        verify_duration(actual, target, SAMPLE_TOLERANCE, 'mixed audio')
        run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', str(candidate), '-map', '0:a:0', '-f', 'null', '-'])
        os.replace(candidate, output)
    print(f'Output: {output}\nDuration: {actual}s\nSegments: {len(segments)}')


def mux(args):
    source_audio = input_file(args.source_audio)
    generated_audio = input_file(args.generated_audio)
    source_video = input_file(args.source_video)
    require_tools()
    for audio in (source_audio, generated_audio):
        metadata = probe(audio)
        stream(metadata, 'audio', audio)
        print(f'Input audio: {audio} duration={format_duration(metadata, audio)}s')
    video_metadata = probe(source_video)
    target = stream_duration(video_metadata, source_video, 'video')
    output = output_file(args.output, [source_audio, generated_audio, source_video])
    with tempfile.TemporaryDirectory(prefix='.audio-mux-', dir=output.parent) as directory:
        padded_audio = Path(directory) / 'padded.wav'
        candidate = Path(directory) / f'muxed{output.suffix}'
        run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', str(generated_audio), '-map', '0:a:0',
             '-af', f'apad=whole_dur={target}', '-t', str(target), '-ac', '2', '-ar', '44100',
             '-c:a', 'pcm_s16le', str(padded_audio)])
        verify_duration(format_duration(probe(padded_audio), padded_audio), target, SAMPLE_TOLERANCE, 'padded audio')
        run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', str(source_video), '-i', str(padded_audio),
             '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', str(candidate)])
        metadata = probe(candidate)
        kinds = [item.get('codec_type') for item in metadata.get('streams', [])]
        if sorted(kinds) != ['audio', 'video']:
            raise ValueError('muxed output must contain exactly one audio stream and one video stream')
        audio = stream(metadata, 'audio', candidate)
        if audio.get('codec_name') != 'aac':
            raise ValueError('muxed output must contain AAC audio')
        if stream(metadata, 'video', candidate).get('codec_name') != stream(video_metadata, 'video', source_video).get('codec_name'):
            raise ValueError('muxed video codec differs from source')
        actual = format_duration(metadata, candidate)
        verify_duration(actual, target, MUX_TOLERANCE, 'muxed container')
        verify_duration(stream_duration(metadata, candidate, 'video'), target, MUX_TOLERANCE, 'muxed video')
        verify_duration(stream_duration(metadata, candidate, 'audio'), target, MUX_TOLERANCE, 'muxed audio')
        run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', str(candidate),
             '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'])
        os.replace(candidate, output)
    print(f'Output: {output}\nVideo target: {target}s\nDuration: {actual}s\nCodec timing tolerance: {MUX_TOLERANCE}s')


def main():
    parser = argparse.ArgumentParser(description='Validated audio mixing and video muxing')
    commands = parser.add_subparsers(dest='command', required=True)
    mixing = commands.add_parser('mix')
    mixing.add_argument('source_duration')
    mixing.add_argument('output')
    mixing.add_argument('segments', nargs='+')
    muxing = commands.add_parser('mux')
    muxing.add_argument('source_audio')
    muxing.add_argument('generated_audio')
    muxing.add_argument('source_video')
    muxing.add_argument('output')
    args = parser.parse_args()
    try:
        (mix if args.command == 'mix' else mux)(args)
    except (ValueError, OSError, InvalidOperation) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
