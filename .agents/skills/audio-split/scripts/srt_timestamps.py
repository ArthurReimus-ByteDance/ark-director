import argparse
import re
import sys
from decimal import Decimal, InvalidOperation
from itertools import pairwise
from pathlib import Path

TIMESTAMP = re.compile(r'(\d+):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d+):(\d{2}):(\d{2})[,.](\d{3})')


def parse_time(parts):
    hours, minutes, seconds, milliseconds = map(int, parts)
    if minutes >= 60 or seconds >= 60:
        raise ValueError('subtitle minutes and seconds must be below 60')
    return Decimal(hours * 3600 + minutes * 60 + seconds) + Decimal(milliseconds) / 1000


def parse_srt(path):
    content = Path(path).read_text(encoding='utf-8-sig')
    cues = []
    for block in re.split(r'\n\s*\n', content.strip()):
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        timing_index = 1 if lines[0].strip().isdigit() else 0
        if timing_index >= len(lines):
            raise ValueError('subtitle cue is missing a timestamp')
        match = TIMESTAMP.fullmatch(lines[timing_index].strip())
        if match is None:
            raise ValueError(f'malformed subtitle timing: {lines[timing_index]}')
        start = parse_time(match.groups()[:4])
        end = parse_time(match.groups()[4:])
        if end <= start:
            raise ValueError('subtitle cue end must follow its start')
        text = ' '.join(lines[timing_index + 1:]).strip()
        cues.append((start, end, text))
    return sorted(cues, key=lambda cue: cue[0])


def merged_intervals(cues):
    merged: list[tuple[Decimal, Decimal]] = []
    for start, end, _ in sorted(cues, key=lambda cue: cue[0]):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def snap_cut(cut, cues):
    for start, end in merged_intervals(cues):
        if start < cut < end:
            return start if cut - start <= end - cut else end
    return cut


def snap_cuts(cuts, cues):
    result = [snap_cut(cut, cues) for cut in cuts]
    if any(cut <= 0 for cut in result) or any(left >= right for left, right in pairwise(result)):
        raise ValueError('subtitle snapping must preserve positive, strictly increasing cut points')
    return result


def manifest_boundaries(path):
    segments = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.startswith('WARNING:') or not line.strip():
            continue
        match = re.fullmatch(r'\S+ offset=([\d.]+)s duration=[\d.]+s source_end=([\d.]+)s bytes=\d+', line)
        if match is None:
            raise ValueError('manifest requires offset, duration, source_end, and bytes for each segment')
        start, end = map(Decimal, match.groups())
        if start < 0 or end <= start:
            raise ValueError('manifest contains invalid source boundaries')
        segments.append((start, end))
    if not segments:
        raise ValueError('manifest contains no segments')
    return segments


def cmd_table(cuts, cues, segments=None):
    if not cues:
        return
    last_end = max(end for _, end, _ in cues)
    if any(cut >= last_end for cut in cuts):
        raise ValueError('table cuts must precede the final subtitle end')
    if segments is None:
        ends = [Decimal(0), *cuts, last_end]
        segments = list(pairwise(ends))
    for index, (segment_start, end) in enumerate(segments, 1):
        entries = []
        for start, cue_end, text in cues:
            if cue_end > segment_start and start < end:
                entries.append((max(start - segment_start, Decimal(0)), min(cue_end, end) - segment_start, text))
        if entries:
            print(f'\n=== Segment {index} (abs {segment_start:.2f}s - {end:.2f}s) ===')
            for relative_start, relative_end, text in entries:
                print(f'[{relative_start:.1f}s:{relative_end:.1f}s] {text}')


def main():
    parser = argparse.ArgumentParser(description='SRT-aware dubbing split helpers')
    parser.add_argument('mode', choices=['snap', 'table'])
    parser.add_argument('srt')
    parser.add_argument('--manifest', help='use actual offsets/source ends from split_segments output (table mode)')
    parser.add_argument('cuts', nargs='*')
    args = parser.parse_args()
    try:
        cues = parse_srt(args.srt)
        if args.manifest and (args.mode != 'table' or args.cuts):
            raise ValueError('--manifest requires table mode without explicit cuts')
        cuts = [Decimal(value) for value in args.cuts]
        if any(not cut.is_finite() or cut <= 0 for cut in cuts):
            raise ValueError('cut points must be positive finite numbers')
        cuts = snap_cuts(cuts, cues)
        if args.mode == 'snap':
            for cut in cuts:
                print(f'{cut:.3f}')
        else:
            cmd_table(cuts, cues, manifest_boundaries(args.manifest) if args.manifest else None)
    except (ValueError, OSError, InvalidOperation) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
