#!/usr/bin/env python3
"""Extract GTA San Andreas sky colours from timecyc.dat.

timecyc.dat is the game's colour-grading table. Each weather block holds 8
time-of-day rows; columns 4 and 5 (tab-separated groups) are sky-top and
sky-bottom RGB. We take EXTRASUNNY_LA, the clear-weather Los Santos grading.

Output feeds the HUD page, which interpolates between these by the visitor's
local hour so the sky behind the HUD matches their actual time of day.

Usage:
    extract-timecyc.py <timecyc.dat> <out.json> [WEATHER_BLOCK]
"""
import json
import sys

# The 8 rows in every weather block, in file order.
HOURS = [0, 5, 6, 7, 12, 19, 20, 22]


def extract(path, block='EXTRASUNNY_LA'):
    lines = open(path, encoding='latin-1').read().replace('\r', '').split('\n')

    start = None
    for i, ln in enumerate(lines):
        if ln.startswith('//') and block in ln:
            start = i + 1
            break
    if start is None:
        sys.exit(f"weather block {block!r} not found")

    rows = []
    for ln in lines[start:]:
        s = ln.strip()
        if s.startswith('////'):
            break                      # next weather block
        if not s or s.startswith('//'):
            continue                   # time label or blank
        groups = [g.strip() for g in ln.split('\t') if g.strip()]
        if len(groups) < 5:
            continue
        top = [int(v) for v in groups[3].split()]
        bot = [int(v) for v in groups[4].split()]
        rows.append((top, bot))
        if len(rows) == len(HOURS):
            break

    if len(rows) != len(HOURS):
        sys.exit(f"expected {len(HOURS)} rows in {block}, got {len(rows)}")

    return {
        "source": f"timecyc.dat {block}",
        "keys": [
            {"hour": h, "top": t, "bottom": b}
            for h, (t, b) in zip(HOURS, rows)
        ],
    }


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    blk = sys.argv[3] if len(sys.argv) > 3 else 'EXTRASUNNY_LA'
    data = extract(sys.argv[1], blk)
    json.dump(data, open(sys.argv[2], 'w'), indent=1)
    for k in data['keys']:
        print(f"  {k['hour']:>2}:00  top=rgb{tuple(k['top'])}  bottom=rgb{tuple(k['bottom'])}")
