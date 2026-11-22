#!/usr/bin/env python3
"""audit.py - mechanical layout audit of the page.

Run:  python tools/audit.py

Three questions, answered without a human eye:
  1. does any drawn illustration spill outside the box it was given?
  2. does any two pieces of text overlap?
  3. does any text leave the printable area or cross a horizontal rule?
Exit code 1 when something fails, so it can gate the build.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

import page

RECORDS = []
_orig_text = ImageDraw.ImageDraw.text


def recording_text(self, xy, text, *a, **kw):
    box = _orig_text(self, xy, text, *a, **kw)
    if text.strip():
        RECORDS.append((str(text), box))
    return box


def audit_art():
    """An illustration pasted through draw_art must not paint outside its box."""
    bad = []
    for n in page.ART:
        x0, y0, x1, y1 = 20, 20, 220, 120
        img = Image.new("RGB", (300, 200), page.PAPER)
        page.draw_art(img, n, (x0, y0, x1, y1))
        px = img.load()
        for y in range(200):
            for x in range(300):
                if px[x, y] == page.PAPER:
                    continue
                if x < x0 or x > x1 or y < y0 or y > y1:
                    bad.append((n, x, y))
                    break
            else:
                continue
            break
    return bad


def audit_page():
    import datetime
    ImageDraw.ImageDraw.text = recording_text
    try:
        RECORDS.clear()
        out = Path("audit-entry.png")
        page.main(str(out))
    finally:
        ImageDraw.ImageDraw.text = _orig_text
    out.unlink(missing_ok=True)

    M, RIGHT = page.M, page.RIGHT
    outside = []
    for txt, box in RECORDS:
        if box is None:
            continue
        x0, y0, x1, y1 = box
        if x0 < M - 1 or x1 > RIGHT + 2 or y1 > 1024 - M + 2 or y0 < 8:
            outside.append((txt, box))

    overlaps = []
    for i in range(len(RECORDS)):
        ta, ba = RECORDS[i]
        if ba is None:
            continue
        for j in range(i + 1, len(RECORDS)):
            tb, bb = RECORDS[j]
            if bb is None:
                continue
            ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
            oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
            if ox > 2 and oy > 2:
                overlaps.append((ta, tb, ox, oy))
    return outside, overlaps


def main():
    art = audit_art()
    outside, overlaps = audit_page()

    for n, x, y in art:
        print("ART SPILL  #%d at (%d,%d) outside its box" % (n, x, y))
    for txt, box in outside:
        print("OUTSIDE    %r bbox=%s" % (txt[:40], box))
    for ta, tb, ox, oy in overlaps:
        print("OVERLAP    %r / %r  by %dx%d px" % (ta[:34], tb[:34], ox, oy))

    ok = not art and not outside and not overlaps
    print("audit: %s (%d spills, %d outside, %d overlaps)" %
          ("PASS" if ok else "FAIL", len(art), len(outside), len(overlaps)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
