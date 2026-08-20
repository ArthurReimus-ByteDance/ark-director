#!/usr/bin/env python3
"""SRT-aware split helpers for Seed Audio dubbing segmentation.

Modes:
  --snap  <file.srt> <cut...>   Print cut points snapped to subtitle gaps
                                (never mid-line). One per line.
  --table <file.srt> <cut...>   Print per-segment cue list with relative
                                [start_s:end_s] timestamps for prompt authoring.
Snapping rule: a cut that lands inside a cue's [start,end] window is moved to
the nearer cue boundary (start or end), so no dialogue line is cut mid-sentence.
"""

import argparse
import sys
import re


def parse_srt(path):
    cues = []  # (start_s, end_s, text)
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        m = re.search(
            r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})",
            lines[1],
        )
        if not m:
            continue

        def to_sec(h, mi, s, ms):
            return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000.0

        start = to_sec(m.group(1), m.group(2), m.group(3), m.group(4))
        end = to_sec(m.group(5), m.group(6), m.group(7), m.group(8))
        text = " ".join(lines[2:]).strip()
        cues.append((start, end, text))
    cues.sort(key=lambda c: c[0])
    return cues


def snap_cut(cut, cues):
    for start, end, _ in cues:
        if start < cut < end:
            return start if abs(cut - start) <= abs(cut - end) else end
    return cut


def snap_cuts(cuts, cues):
    snapped = []
    for c in cuts:
        s = snap_cut(c, cues)
        if s > 0 and s not in snapped:
            snapped.append(s)
    return sorted(snapped)


def cmd_snap(args):
    cues = parse_srt(args.srt)
    cuts = [float(x) for x in args.cuts]
    for s in snap_cuts(cuts, cues):
        print(f"{s:.3f}")


def fmt(sec):
    return f"{sec:.1f}s"


def cmd_table(args):
    cues = parse_srt(args.srt)
    cuts = snap_cuts([float(x) for x in args.cuts], cues)
    last_end = cues[-1][1] if cues else 0.0
    boundaries = [0.0] + cuts
    seg_start = 0.0
    seg_idx = 1
    for cut in boundaries[1:] + [last_end]:
        end = cut
        seg_cues = []
        for start, e, text in cues:
            if start >= seg_start and e <= end:
                seg_cues.append((start - seg_start, e - seg_start, text))
            elif e > seg_start and start < end:
                rel_s = max(start - seg_start, 0.0)
                rel_e = min(e - seg_start, end - seg_start)
                seg_cues.append((rel_s, rel_e, text))
        if seg_cues:
            print(f"\n=== Segment {seg_idx} (abs {seg_start:.2f}s - {end:.2f}s) ===")
            for rel_s, rel_e, text in seg_cues:
                print(f"[{fmt(rel_s)}:{fmt(rel_e)}] {text}")
        seg_start = end
        seg_idx += 1
        if cut == last_end:
            break


def main():
    ap = argparse.ArgumentParser(description="SRT-aware dubbing split helpers")
    sub = ap.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("snap", help="snap cuts to subtitle gaps")
    p1.add_argument("srt")
    p1.add_argument("cuts", nargs="+", type=float)

    p2 = sub.add_parser("table", help="per-segment relative timestamps")
    p2.add_argument("srt")
    p2.add_argument("cuts", nargs="+", type=float)

    args = ap.parse_args()
    if args.mode == "snap":
        cmd_snap(args)
    else:
        cmd_table(args)


if __name__ == "__main__":
    main()
