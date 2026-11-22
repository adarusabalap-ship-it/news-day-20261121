#!/usr/bin/env python3
"""build.py - draws "Saturday 21 November 2026" as one page of world news.

Run:  python tools/build.py entry.png

Every string on the page is taken from the day's own edition
(make.fun /api/news/editions/2026-11-21): the 35 stories it carries, in its
order, with its regions, places and outlets. Nothing here invents a fact, a
number or a source; the layout only decides what a reader sees first.

The composition is deliberately flat: cream paper, black ink, one red accent
and one colour per region, so a reader at thumbnail size still finds the date,
the three biggest stories and the shape of the day.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EDITION = HERE.parent / "edition.json"

W = H = 1024
M = 16
RIGHT = W - M - 1
EDGE = RIGHT - M + 1

PAPER = (247, 243, 232)
INK = (22, 20, 17)
SOFT = (86, 79, 69)
FAINT = (126, 118, 105)
RULE = (38, 34, 28)
RED = (168, 22, 32)
WHITE = (255, 255, 255)
CREAM = (255, 252, 245)

# One colour per region, used on the story number, the panel rule and the
# stat block, so colour alone says where a story happened.
REGION = {
    "europe": ((38, 84, 146), "EUROPE"),
    "middle-east": ((168, 22, 32), "MIDDLE EAST"),
    "asia": ((14, 104, 112), "ASIA"),
    "africa": ((162, 104, 24), "AFRICA"),
    "americas": ((88, 48, 128), "AMERICAS"),
    "oceania": ((18, 116, 88), "OCEANIA"),
    "world": ((56, 54, 58), "WORLD"),
}

FD = "C:/Windows/Fonts/"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FD + name, size)
    return _cache[key]


def tw(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def wrap(d, s, f, maxw):
    out, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def fit(d, s, name, size, maxw, maxlines, minsize=9):
    """Largest size at which s wraps into <= maxlines lines within maxw."""
    while size > minsize:
        f = font(name, size)
        if len(wrap(d, s, f, maxw)) <= maxlines:
            return f, size
        size -= 1
    return font(name, minsize), minsize


def caps(d, xy, s, f, fill, track=1.2, anchor_left=True):
    """Draw small-caps style text with letter tracking."""
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += tw(d, ch, f) + track
    return x


def caps_width(d, s, f, track=1.2):
    return sum(tw(d, ch, f) + track for ch in s) - track


def para(d, xy, s, f, fill, maxw, leading, maxlines=99):
    x, y = xy
    lines = wrap(d, s, f, maxw)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- the edition

def load():
    ed = json.loads(EDITION.read_text(encoding="utf-8"))
    stories = {s["n"]: s for s in ed["stories"]}
    return ed, stories


def region_colour(story):
    return REGION.get(story.get("region") or "world", REGION["world"])[0]


def region_name(story):
    return REGION.get(story.get("region") or "world", REGION["world"])[1]


# --------------------------------------------------------------- illustration

def frame(d, box, fill, line=RULE):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=line, width=1)


def art_gulf(d, box):
    """A gulf crossed by two strikes, two tankers hit: the day's lead."""
    x0, y0, x1, y1 = box
    frame(d, box, (30, 74, 96))
    # water
    d.rectangle([x0 + 1, y0 + 44, x1 - 1, y1 - 1], fill=(30, 92, 116))
    # land: Iran to the north, Arabia to the south
    d.polygon([(x0 + 1, y0 + 1), (x0 + 96, y0 + 1), (x0 + 96, y0 + 26),
               (x0 + 52, y0 + 40), (x0 + 1, y0 + 34)], fill=(206, 178, 126))
    d.polygon([(x0 + 128, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y1 - 30),
               (x0 + 176, y1 - 22), (x0 + 128, y1 - 12)], fill=(206, 178, 126))
    # two missile arcs from the north coast to the far shore
    for dx in (0, 26):
        pts = []
        for i in range(21):
            t = i / 20
            px = x0 + 70 + dx + t * 120
            py = y0 + 30 + t * 44 - (t - t * t) * 74
            pts.append((px, py))
        d.line(pts, fill=(232, 78, 56), width=3, joint="curve")
        d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
                  fill=(232, 78, 56))
    # fire on the shore
    d.polygon([(x0 + 42, y0 + 24), (x0 + 50, y0 + 6), (x0 + 56, y0 + 20),
               (x0 + 62, y0 + 4), (x0 + 68, y0 + 24)], fill=(240, 146, 44))
    # two tankers
    for sx in (x0 + 150, x0 + 226):
        d.rectangle([sx, y1 - 22, sx + 34, y1 - 13], fill=(226, 226, 220))
        d.rectangle([sx + 22, y1 - 29, sx + 30, y1 - 22], fill=(226, 226, 220))
        d.line([sx - 2, y1 - 22, sx + 36, y1 - 22], fill=(20, 20, 20), width=2)
    d.text((x1 - 44, y0 + 4), "2", font=font("georgiab.ttf", 30), fill=(255, 236, 200))


def art_trade(d, box):
    """Two flags, one agreement: the EU and Indonesia."""
    x0, y0, x1, y1 = box
    frame(d, box, (24, 44, 88))
    d.rectangle([x0 + 26, y0 + 16, x0 + 150, y0 + 78], fill=(20, 40, 120))
    cx, cy = x0 + 88, y0 + 47
    for i in range(12):
        import math
        a = math.radians(i * 30)
        px, py = cx + math.cos(a) * 22, cy + math.sin(a) * 22
        d.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4], fill=(240, 196, 60))
    d.rectangle([x0 + 166, y0 + 16, x0 + 290, y0 + 45], fill=(206, 34, 44))
    d.rectangle([x0 + 166, y0 + 45, x0 + 290, y0 + 74], fill=(248, 246, 240))
    # the agreement itself: a signed line and a rising bar
    d.line([x0 + 26, y0 + 90, x0 + 290, y0 + 90], fill=(240, 196, 60), width=2)
    d.text((x0 + 26, y0 + 94), "98.5%", font=font("georgiab.ttf", 26), fill=(255, 246, 214))
    d.text((x0 + 104, y0 + 100), "of EU tariff lines go duty-free",
           font=font("arial.ttf", 12), fill=(224, 232, 244))


def art_cop(d, box):
    """Twelve days scheduled, a thirteenth run: COP31."""
    x0, y0, x1, y1 = box
    frame(d, box, (18, 62, 52))
    d.text((x0 + 18, y0 + 8), "NOVEMBER", font=font("arialbd.ttf", 12), fill=(214, 226, 208))
    bw, bh = 22, 17
    for i in range(13):
        col, row = i % 7, i // 7
        bx = x0 + 18 + col * (bw + 3)
        by = y0 + 26 + row * (bh + 3)
        last = i == 12
        d.rectangle([bx, by, bx + bw, by + bh], fill=(214, 78, 40) if last else (240, 240, 228))
        d.text((bx + 5, by + 2), str(9 + i), font=font("arialbd.ttf", 10),
               fill=(255, 255, 255) if last else (40, 40, 36))
    d.text((x0 + 196, y0 + 20), "+1", font=font("georgiab.ttf", 40), fill=(240, 150, 60))
    d.text((x0 + 198, y0 + 62), "DAY OVER", font=font("arialbd.ttf", 13), fill=(240, 216, 190))


def art_quake(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (238, 232, 216))
    cx, cy = x0 + 44, y1 - 6
    for r in (16, 30, 46, 64):
        d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62],
                  outline=(196, 96, 40), width=2)
    d.polygon([(cx - 62, y1 - 1), (cx - 18, y0 + 12), (cx + 6, y0 + 26),
               (cx + 40, y1 - 1)], fill=(206, 178, 126))
    d.text((x0 + 96, y0 + 6), "M6.7", font=font("georgiab.ttf", 30), fill=(150, 30, 24))
    d.text((x0 + 98, y0 + 42), "PERU", font=font("arialbd.ttf", 11), fill=(120, 100, 76))


def art_mercury(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (16, 20, 40))
    cy = (y0 + y1) / 2
    d.ellipse([x0 + 150, cy - 20, x0 + 192, cy + 20], fill=(186, 174, 158))
    d.ellipse([x0 + 158, cy - 14, x0 + 170, cy - 2], fill=(206, 196, 180))
    pts = []
    for i in range(41):
        t = i / 40
        pts.append((x0 + 12 + t * 138, cy - 26 + t * 26 - (t - t * t) * 40))
    d.line(pts, fill=(96, 168, 220), width=2)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 9, pts[-1][1] - 6),
               (pts[-1][0] - 9, pts[-1][1] + 6)], fill=(240, 170, 60))
    d.text((x0 + 12, y0 + 6), "37 MIN", font=font("georgiab.ttf", 24), fill=(240, 214, 160))
    d.text((x0 + 12, y0 + 34), "ENGINE BURN", font=font("arialbd.ttf", 10), fill=(150, 168, 200))


def art_port(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (24, 40, 62))
    for i, cx in enumerate((x0 + 40, x0 + 88, x0 + 136)):
        d.line([cx, y1 - 6, cx, y0 + 22], fill=(196, 176, 130), width=4)
        d.line([cx - 18, y0 + 22, cx + 18, y0 + 22], fill=(196, 176, 130), width=4)
        d.line([cx - 10, y0 + 32, cx + 10, y0 + 32], fill=(196, 176, 130), width=3)
    for cx in (x0 + 168, x0 + 196):
        d.polygon([(cx, y0 + 16), (cx - 12, y0 + 34), (cx + 12, y0 + 34)],
                  fill=(228, 96, 60))
    d.rectangle([x0 + 1, y1 - 20, x1 - 1, y1 - 1], fill=(18, 46, 70))
    d.text((x0 + 12, y0 + 6), "PORT", font=font("georgiab.ttf", 22), fill=(240, 224, 190))
    d.text((x0 + 12, y0 + 32), "HIT BY DRONES", font=font("arialbd.ttf", 10), fill=(196, 210, 226))


def art_cricket(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (22, 84, 62))
    d.rectangle([x0 + 1, y1 - 22, x1 - 1, y1 - 1], fill=(150, 178, 96))
    for cx in (x0 + 40, x0 + 52, x0 + 64):
        d.line([cx, y0 + 12, cx, y1 - 22], fill=(244, 240, 224), width=3)
    d.ellipse([x0 + 150, y0 + 12, x0 + 166, y0 + 28], fill=(214, 60, 46))
    d.text((x0 + 92, y0 + 6), "486/4", font=font("georgiab.ttf", 26), fill=(250, 246, 226))
    d.text((x0 + 94, y0 + 36), "INDIA, DAY 3", font=font("arialbd.ttf", 10), fill=(206, 226, 196))


ART = {
    1: art_gulf,
    2: art_trade,
    6: art_cop,
    3: art_quake,
    7: art_mercury,
    10: art_port,
    12: art_cricket,
}


# ------------------------------------------------------------------ the page

def stat_block(d, box, value, label, source, colour):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x0 + 4, y1], fill=colour)
    f = font("georgiab.ttf", 26)
    d.text((x0 + 12, y0 - 2), value, font=f, fill=INK)
    para(d, (x0 + 12, y0 + 26), label, font("arial.ttf", 10), SOFT, x1 - x0 - 14, 12, 2)
    caps(d, (x0 + 12, y1 - 11), source, font("arialbd.ttf", 7.5), FAINT)


def main(out_path):
    ed, stories = load()
    total = len(stories)
    regions = len({s.get("region") for s in ed["stories"] if s.get("region")})
    day = ed["day"]
    import datetime
    dt = datetime.date.fromisoformat(day)
    date_line = dt.strftime("%A %-d %B %Y") if sys.platform != "win32" else \
        "%s %d %s %d" % (dt.strftime("%A"), dt.day, dt.strftime("%B"), dt.year)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- rail
    caps(d, (M, 18), "ONE DAY OF WORLD NEWS, ONE PICTURE", font("arialbd.ttf", 10), RED)
    tail = "%d STORIES  \u00b7  %d REGIONS  \u00b7  ALL FROM ONE SATURDAY" % (total, regions)
    f_tail = font("arialbd.ttf", 10)
    caps(d, (RIGHT - caps_width(d, tail, f_tail), 18), tail, f_tail, INK)
    d.line([M, 34, RIGHT, 34], fill=RULE, width=2)

    # ---- masthead
    f_date, size = fit(d, date_line, "georgiab.ttf", 78, EDGE, 1)
    d.text((M, 38), date_line, font=f_date, fill=INK)
    d.line([M, 116, RIGHT, 116], fill=RULE, width=1)
    lead = stories[1]
    stand = "Iran strikes a site in Bahrain  \u00b7  the EU signs a trade pact with Indonesia  \u00b7  COP31 runs a day over"
    f_stand = font("georgiai.ttf", 15)
    d.text((M, 122), stand, font=f_stand, fill=SOFT)
    d.line([M, 146, RIGHT, 146], fill=RULE, width=1)

    # ---- three lead panels
    heroes = [1, 2, 6]
    gap = 14
    pw = (EDGE - 2 * gap) // 3
    y_art, h_art = 154, 104
    for i, n in enumerate(heroes):
        st = stories[n]
        x0 = M + i * (pw + gap)
        x1 = x0 + pw
        col = region_colour(st)
        d.rectangle([x0, y_art, x1, y_art + h_art], fill=None)
        ART[n](d, (x0, y_art, x1, y_art + h_art))
        d.rectangle([x0, y_art + h_art, x1, y_art + h_art + 4], fill=col)
        # number + region
        ty = y_art + h_art + 10
        d.rectangle([x0, ty, x0 + 17, ty + 17], fill=col)
        d.text((x0 + 4, ty + 1), str(n), font=font("arialbd.ttf", 12), fill=WHITE)
        caps(d, (x0 + 23, ty + 4), region_name(st), font("arialbd.ttf", 9), col)
        hl = st["headline"].replace("'", "\u2019")
        f_h, hs = fit(d, hl, "georgiab.ttf", 25, pw, 3)
        ty += 24
        for ln in wrap(d, hl, f_h, pw):
            d.text((x0, ty), ln, font=f_h, fill=INK)
            ty += int(hs * 1.12)
        body = st["summary"].replace("'", "\u2019")
        ty = para(d, (x0, ty + 5), body, font("arial.ttf", 12), SOFT, pw, 15, 4)
        caps(d, (x0, ty + 4), " \u00b7 ".join(st["outlets"]).upper(),
             font("arialbd.ttf", 8), FAINT)

    # ---- four more cards
    y2 = 404
    cards = [8, 7, 10, 12]
    gap2 = 12
    cw = (EDGE - 3 * gap2) // 4
    for i, n in enumerate(cards):
        st = stories[n]
        x0 = M + i * (cw + gap2)
        x1 = x0 + cw
        col = region_colour(st)
        ART[n](d, (x0, y2, x1, y2 + 56))
        d.rectangle([x0, y2 + 56, x1, y2 + 59], fill=col)
        ty = y2 + 66
        d.rectangle([x0, ty, x0 + 15, ty + 15], fill=col)
        d.text((x0 + 3, ty + 1), str(n), font=font("arialbd.ttf", 11), fill=WHITE)
        caps(d, (x0 + 20, ty + 4), region_name(st), font("arialbd.ttf", 8), col)
        hl = st["headline"].replace("'", "\u2019")
        f_h, hs = fit(d, hl, "georgiab.ttf", 17, cw, 3)
        ty += 21
        for ln in wrap(d, hl, f_h, cw):
            d.text((x0, ty), ln, font=f_h, fill=INK)
            ty += int(hs * 1.14)
        ty = para(d, (x0, ty + 3), st["summary"].replace("'", "\u2019"),
                  font("arial.ttf", 10.5), SOFT, cw, 12.5, 3)
        caps(d, (x0, ty + 3), " \u00b7 ".join(st["outlets"]).upper(),
             font("arialbd.ttf", 7.5), FAINT)

    # ---- numbers of the day
    y3 = 578
    d.line([M, y3 - 10, RIGHT, y3 - 10], fill=RULE, width=2)
    caps(d, (M, y3), "THE DAY IN NUMBERS", font("arialbd.ttf", 10), RED)
    nums = [
        ("6.7", "Magnitude of the quake that shook central Peru; 8 hurt.", "USGS", 8),
        ("98.5%", "Share of EU tariff lines that go duty-free for Indonesia.", "EUROPEAN COMMISSION", 2),
        ("11", "Killed in the Sinaloa clashes around a cartel leader's capture.", "AP \u00b7 REUTERS", 3),
        ("21", "Chinese jets in a patrol Taiwan says it tracked; 15 crossed the median line.", "TAIPEI", 9),
        ("8%", "Bitcoin's move in a day, to a $25,500 low, its lowest since 2024.", "COINGECKO", 5),
        ("16", "Crew taken off a Russian cargo ship set on fire by drones.", "REUTERS \u00b7 BBC", 4),
    ]
    sw = (EDGE - 2 * 10) // 2
    for i, (val, label, src, n) in enumerate(nums):
        col = region_colour(stories[n])
        cx = M + (i % 2) * (sw + 10)
        cy = y3 + 20 + (i // 2) * 62
        stat_block(d, (cx, cy, cx + sw, cy + 56), val, label, src, col)

    # ---- also on saturday
    xb = M + 2 * sw + 10 + 26
    caps(d, (xb, y3), "ALSO ON SATURDAY", font("arialbd.ttf", 10), INK)
    d.line([xb, y3 + 15, RIGHT, y3 + 15], fill=RULE, width=1)
    briefs = [n for n in sorted(stories) if n not in heroes and n not in cards]
    colw = (RIGHT - xb - 12) // 2
    f_b = font("arial.ttf", 10.5)
    f_bl = font("arialbd.ttf", 10.5)
    rows = (len(briefs) + 1) // 2
    for i, n in enumerate(briefs):
        st = stories[n]
        cx = xb + (i // rows) * (colw + 12)
        cy = y3 + 24 + (i % rows) * 17.4
        col = region_colour(st)
        d.rectangle([cx, cy + 1, cx + 9, cy + 10], fill=col)
        d.text((cx + 12, cy - 2), str(n), font=font("arialbd.ttf", 9), fill=FAINT)
        txt = st["headline"].replace("'", "\u2019")
        # keep one line: trim a trailing clause at a comma, never mid-word
        f_use = f_b
        while tw(d, txt, f_use) > colw - 26 and "," in txt:
            txt = txt[: txt.rfind(",")]
        d.text((cx + 26, cy - 2), txt, font=f_use, fill=INK)

    # ---- date check
    y4 = 812
    d.line([M, y4 - 10, RIGHT, y4 - 10], fill=RULE, width=1)
    d.rectangle([M, y4, M + 96, y4 + 18], fill=RED)
    caps(d, (M + 8, y4 + 4), "DATE CHECK", font("arialbd.ttf", 10), WHITE)
    check = ("Every story on this page happened, or was first reported, on Saturday 21 November 2026 "
             "(UTC), and each is dated to that day only. Claims are shown as reported: where a side's own "
             "account carries the news the line says so (\u201csays\u201d, \u201cclaims\u201d, \u201cofficials say\u201d). "
             "Left out on purpose: stories first reported on another day, and results still to come \u2014 "
             "the COP31 vote was moved to Sunday morning.")
    para(d, (M + 108, y4 - 2), check, font("arial.ttf", 10.5), SOFT, RIGHT - M - 108, 14, 4)
    d.line([M, y4 + 60, RIGHT, y4 + 60], fill=RULE, width=1)

    # ---- footer
    caps(d, (M, y4 + 68), "CONFIRMED  two or more outlets  \u00b7  OFFICIAL  a body on the record  \u00b7  "
                          "REPORTED  one outlet", font("arialbd.ttf", 8.5), SOFT)
    caps(d, (M, y4 + 84), "SOURCES  AP  \u00b7  REUTERS  \u00b7  AFP  \u00b7  BBC  \u00b7  UKMTO  \u00b7  USGS  \u00b7  ESA  \u00b7  "
                          "EUROPEAN COMMISSION  \u00b7  ICC  \u00b7  COINGECKO  \u00b7  ORIGINAL DRAWINGS",
         font("arialbd.ttf", 8.5), FAINT)
    caps(d, (RIGHT - caps_width(d, "35 STORIES, ONE DAY, ONE PAGE", font("arialbd.ttf", 8.5)), y4 + 68),
         "35 STORIES, ONE DAY, ONE PAGE", font("arialbd.ttf", 8.5), RED)

    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, Path(out_path).stat().st_size))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
