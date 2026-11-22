#!/usr/bin/env python3
"""audit.py - mechanical layout audit of the poster.

Run:  python tools/audit.py

Answers, without a human eye:
  1. does any drawn illustration paint outside the box it was given?
  2. does any two pieces of text overlap?
  3. does any text leave the printable area?
  4. does any caption band's text overflow the band?
Exit code 1 when something fails, so it can gate the build.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

import poster

RECORDS = []
_orig_text = ImageDraw.ImageDraw.text


def recording_text(self, xy, text, *a, **kw):
    box = _orig_text(self, xy, text, *a, **kw)
    if str(text).strip() and not poster.SUPPRESS:
        # PIL's text() returns None, so measure the box ourselves: trusting its
        # return value records nothing and makes every overlap check vacuous.
        try:
            bbox = self.textbbox(xy, str(text), font=kw.get("font"), anchor=kw.get("anchor"))
        except Exception:
            bbox = None
        RECORDS.append((str(text), bbox))
    return box


def audit_art():
    """Anything pasted through draw_art must stay inside its box."""
    bad = []
    for n in poster.ART:
        x0, y0, x1, y1 = 20, 20, 220, 120
        img = Image.new("RGB", (300, 200), poster.PAPER)
        poster.draw_art(img, n, (x0, y0, x1, y1))
        px = img.load()
        for y in range(200):
            for x in range(300):
                if px[x, y] == poster.PAPER:
                    continue
                if x < x0 or x > x1 or y < y0 or y > y1:
                    bad.append((n, x, y))
                    break
            else:
                continue
            break
    return bad


def audit_page():
    ImageDraw.ImageDraw.text = recording_text
    try:
        RECORDS.clear()
        out = Path("audit-poster.png")
        poster.main(str(out))
    finally:
        ImageDraw.ImageDraw.text = _orig_text
    out.unlink(missing_ok=True)

    M, RIGHT = poster.M, poster.RIGHT
    outside = []
    measured = [r for r in RECORDS if r[1] is not None] + \
               [r for r in poster.RECORD_CAPS if r[1] is not None]
    for txt, box in measured:
        x0, y0, x1, y1 = box
        if x0 < M - 1 or x1 > RIGHT + 2 or y1 > 1024 - M + 3 or y0 < 4:
            outside.append((txt, box))

    overlaps = []
    for i in range(len(measured)):
        ta, ba = measured[i]
        for j in range(i + 1, len(measured)):
            tb, bb = measured[j]
            ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
            oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
            if ox > 2 and oy > 2:
                overlaps.append((ta, tb, ox, oy))
    unmeasured = len(RECORDS) - len([r for r in RECORDS if r[1] is not None])
    return outside, overlaps, unmeasured


def audit_bands():
    """Caption text must sit inside its coloured band, with room to spare."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    pw = (poster.EDGE - 32) // 3
    bad = []
    for n in poster.PANELS:
        big, small = poster.CAPTION[n]
        f1, s1 = poster.fit_caps(d, big, "arialbd.ttf", 21, pw - 22, 11)
        f2, s2 = poster.fit_caps(d, small, "arialbd.ttf", 21, pw - 22, 11)
        used = 5 + s1 + 6 + s2
        if used > poster.BAND_H - 2:
            bad.append((n, "overflow", used, poster.BAND_H))
        for label, f in ((big, f1), (small, f2)):
            wide = poster.tw(d, label, f)
            if wide > pw - 20:
                bad.append((n, label, wide, pw - 20))
    return bad


def main():
    art = audit_art()
    outside, overlaps, unmeasured = audit_page()
    bands = audit_bands()

    for n, x, y in art:
        print("ART SPILL  #%d at (%d,%d) outside its box" % (n, x, y))
    for txt, box in outside:
        print("OUTSIDE    %r bbox=%s" % (txt[:44], box))
    for ta, tb, ox, oy in overlaps:
        print("OVERLAP    %r / %r  by %dx%d px" % (ta[:32], tb[:32], ox, oy))
    for b in bands:
        print("BAND       %r" % (b,))
    if unmeasured:
        print("UNMEASURED %d text calls had no box" % unmeasured)

    ok = not art and not outside and not overlaps and not bands and not unmeasured
    print("audit: %s (%d spills, %d outside, %d overlaps, %d band)"
          % ("PASS" if ok else "FAIL", len(art), len(outside), len(overlaps), len(bands)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
