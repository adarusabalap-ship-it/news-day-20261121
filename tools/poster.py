#!/usr/bin/env python3
"""page.py - draws Saturday 21 November 2026 as one poster of world news.

Run:  python tools/page.py entry.png

Six panels, each one of that day's stories: the picture carries a label big
enough to read at thumbnail size, and the headline under it says what
happened in the words the day's edition used. A short band at the foot names
the rest of the day. Every string is the edition's own -- same headline, same
summary, same outlets, same region -- so nothing here is invented.

Drawn from primitives only: cream paper, black ink, one accent per region. No
photography, no network, no fonts beyond the system's, so the same call always
writes the same bytes.
"""

import datetime
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24
BAND_H = 58
RIGHT = W - M - 1
EDGE = RIGHT - M + 1

PAPER = (247, 243, 232)
INK = (22, 20, 17)
SOFT = (86, 79, 69)
FAINT = (126, 118, 105)
RULE = (38, 34, 28)
RED = (168, 22, 32)
WHITE = (255, 255, 255)

REGION = {
    "middle-east": ((168, 22, 32), "MIDDLE EAST"),
    "asia": ((14, 100, 110), "ASIA"),
    "europe": ((38, 84, 146), "EUROPE"),
    "americas": ((88, 48, 128), "AMERICAS"),
    "africa": ((158, 102, 22), "AFRICA"),
    "oceania": ((18, 112, 86), "OCEANIA"),
    "world": ((56, 54, 58), "WORLD"),
}

# The day, as the edition tells it: (n, region, headline, summary, outlets)
STORIES = [
    (1, "middle-east", "Bahrain says an Iranian strike set a site on fire",
     "No one hurt, Bahrain says; Iran claims it hit 2 US radars. Separately, UKMTO says 2 tankers were hit off Oman.",
     "Bahrain \u00b7 UKMTO"),
    (2, "asia", "EU and Indonesia sign trade pact after a decade of talks",
     "Signed in Brussels with an investment pact; duties go on 98.5% of EU tariff lines and 90.4% of Indonesia's.",
     "European Commission"),
    (3, "americas", "Mexico captures 'El Chapo Isidro'; 11 die in clashes",
     "FBI top-10 fugitive Fausto Isidro Meza Flores held in Guasave; officials say 4 soldiers and 7 gunmen died.",
     "AP \u00b7 Reuters"),
    (4, "europe", "Drone-hit Russian ship burns off Finland",
     "16 crew taken off. Finland suspects Kyiv.", "Reuters \u00b7 BBC"),
    (5, "world", "Bitcoin swings 8% in one day",
     "From a $25,500 low, the lowest since 2024.", "CoinGecko"),
    (6, "world", "COP31 runs a full day over, still no deal",
     "Final vote moved to Sunday morning.", "Reuters \u00b7 AFP"),
    (7, "world", "BepiColombo fires burn to orbit Mercury",
     "37-minute burn from 18:24 UTC.", "ESA"),
    (8, "americas", "M6.7 quake shakes central Peru",
     "8 hurt, officials say; felt in Lima.", "USGS"),
    (9, "asia", "Taiwan says 21 Chinese jets held a patrol",
     "15 crossed the Strait median line.", "Taipei"),
    (10, "europe", "Ukrainian drones hit Russia's Ust-Luga port",
     "Estonia scrambles NATO jets.", "Kyiv Post \u00b7 ERR"),
    (11, "americas", "Bolsonaro moved to intensive care",
     "Ex-president, 71, has a bowel obstruction.", "Reuters"),
    (12, "oceania", "India 486 for 4 against New Zealand",
     "KL Rahul 136, Shubman Gill 98 in Wellington.", "ICC"),
    (13, "europe", "UN talks set a 2-year path on killer robots",
     "No mandate yet for a binding treaty.", "AFP \u00b7 Reuters"),
    (14, "middle-east", "Iran: says it shot down 2 US drones over Hormuz",
     "", "The Economic Times"),
    (15, "middle-east", "Gaza: civil defence says Israeli fire killed 4",
     "", "RTE"),
    (16, "middle-east", "Lebanon: Aoun says the state alone will hold arms",
     "", "Reuters"),
    (17, "middle-east", "Israel: Eisenkot invites Likud to coalition talks",
     "", "ABP News"),
    (18, "europe", "NATO: Rutte vows to defend 'every inch' of Poland",
     "", "DPA"),
    (19, "europe", "EU: Costa proposes a EUR 1.582tn 2028-34 budget",
     "", "European Commission"),
    (20, "europe", "France: police count 82,500 at cost-of-living marches",
     "", "AFP"),
    (21, "europe", "Dublin: Ireland beat world champions South Africa 20-17",
     "", "RTE \u00b7 BBC"),
    (22, "asia", "Banda Sea: M6.8 quake felt in Darwin; no tsunami",
     "", "USGS \u00b7 ABC"),
    (23, "asia", "India: toxic liquor kills at least 16 in Manipur",
     "", "Khaama Press"),
    (24, "asia", "Japan: snow cuts off 1,400 in a Fukushima village",
     "", "The Peninsula"),
    (25, "asia", "Thailand: emergency plan on arsenic in two rivers",
     "", "Bangkok Post"),
    (26, "africa", "Nigeria: bandits kill 6 in a Niger State village",
     "", "Daily Post"),
    (27, "africa", "Abuja: CAF adopts Kishwahili, backs Infantino",
     "", "CAF"),
    (28, "africa", "Uganda: army chief says a $3bn rail deal is off",
     "", "Reuters"),
    (29, "americas", "US: Trump backs a 10% credit card rate cap",
     "", "AP"),
    (30, "americas", "US: Trump confirms a hack of the FBI crime database",
     "", "AP \u00b7 ABC"),
    (31, "americas", "Florida: St. Johns River tops its 1953 record",
     "", "AP"),
    (32, "americas", "Brazil: Flamengo clinch a second straight title",
     "", "Reuters"),
    (33, "americas", "Brazil: lab mosquitoes cut dengue 69% in a trial",
     "", "Tech Times"),
    (34, "oceania", "Australia: beat England by 3 wickets in a T20",
     "", "AP"),
    (35, "europe", "London: Leeds win 4-1 at Chelsea",
     "", "ESPN"),
]

FD = "C:/Windows/Fonts/"
_cache = {}
RECORD_CAPS = []


def font(name, size):
    key = (name, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FD + name, int(size))
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


def fit(d, s, name, size, maxw, maxlines, minsize=8):
    while size > minsize:
        f = font(name, size)
        if len(wrap(d, s, f, maxw)) <= maxlines:
            return f, size
        size -= 1
    return font(name, minsize), minsize


def fit_caps(d, s, name, size, maxw, minsize=9, track=0.0):
    """Shrink a one-line caption until it fits the measure."""
    while size > minsize:
        f = font(name, size)
        if caps_width(d, s, f, track) <= maxw:
            return f, size
        size -= 1
    return font(name, minsize), minsize


SUPPRESS = False


def caps(d, xy, s, f, fill, track=1.1):
    """Letter-spaced caps: one glyph per call, recorded once as a whole string."""
    global SUPPRESS
    x, y = xy
    start = x
    SUPPRESS = True
    try:
        for ch in s:
            d.text((x, y), ch, font=f, fill=fill)
            x += tw(d, ch, f) + track
    finally:
        SUPPRESS = False
    RECORD_CAPS.append((s, (int(start), y, int(x - track), y + f.size + 2)))
    return x


def caps_width(d, s, f, track=1.1):
    return sum(tw(d, ch, f) + track for ch in s) - track


def clip_to(d, s, f, maxw):
    """Shorten to fit, cutting at a word boundary and marking the cut."""
    if tw(d, s, f) <= maxw:
        return s
    ell = "\u2026"
    words = s.split()
    while words:
        trial = " ".join(words)
        if tw(d, trial + ell, f) <= maxw:
            return trial + ell
        words.pop()
    return ""


def para(d, xy, s, f, fill, maxw, leading, maxlines=99):
    x, y = xy
    for ln in wrap(d, s, f, maxw)[:maxlines]:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def by_n(n):
    for st in STORIES:
        if st[0] == n:
            return st
    raise KeyError(n)


def colour(st):
    return REGION.get(st[1], REGION["world"])[0]


def region_label(st):
    return REGION.get(st[1], REGION["world"])[1]


# --------------------------------------------------------------- illustrations
# Each takes the box it must fill and works in fractions of that box, so the
# same drawing holds whether it is a thumbnail or a panel.

def frame(d, box, fill):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=RULE, width=1)


def plate(d, box, xy, s, f, fg, bg, pad=7):
    """A solid plate behind a label, so the words survive a small screen."""
    x, y = xy
    w = tw(d, s, f)
    h = d.textbbox((0, 0), s, font=f)[3]
    d.rectangle([x, y, x + w + 2 * pad, y + h + 2 * pad], fill=bg)
    d.text((x + pad, y + pad - d.textbbox((0, 0), s, font=f)[1]), s, font=f, fill=fg)
    return x + w + 2 * pad, y + h + 2 * pad


def art_strike(d, box):
    """A site burning on land, and two tankers hit out at sea."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (30, 56, 88))
    sea = y0 + int(h * 0.46)
    d.rectangle([x0 + 1, sea, x1 - 1, y1 - 1], fill=(26, 84, 106))

    # coast: the land the site stands on
    land = [(x0 + 1, y0 + 1), (x0 + int(w * 0.56), y0 + 1),
            (x0 + int(w * 0.52), y0 + int(h * 0.30)),
            (x0 + int(w * 0.40), sea + int(h * 0.03)),
            (x0 + int(w * 0.16), sea + int(h * 0.02)),
            (x0 + 1, sea - int(h * 0.06))]
    d.polygon(land, fill=(206, 178, 126))

    # the site, on fire
    bx, by = x0 + int(w * 0.20), y0 + int(h * 0.26)
    bw, bh = int(w * 0.16), int(h * 0.14)
    d.rectangle([bx, by - bh, bx + bw, by], fill=(72, 68, 62))
    d.rectangle([bx + 4, by - bh + 4, bx + bw - 4, by - 3], fill=(96, 90, 80))
    for k, (ox, oy, sc) in enumerate(((0.03, -0.02, 1.0), (0.10, 0.0, 0.7))):
        fx0 = bx + bw * ox
        fy0 = by - bh * 1.02 + bh * oy
        for r, c in ((int(h * 0.10) * sc, (238, 120, 46)),
                     (int(h * 0.07) * sc, (250, 176, 60)),
                     (int(h * 0.04) * sc, (255, 226, 150))):
            d.ellipse([fx0 - r, fy0 - r * 1.2, fx0 + r, fy0 + r * 0.5], fill=c)
    d.rectangle([bx + bw * 0.25, by - bh * 1.35, bx + bw * 0.55, by - bh * 0.7],
                fill=(190, 186, 178))

    # two tankers out in the water, each with an incoming trail
    for tx, tr in ((0.62, 1.0), (0.86, 0.75)):
        cx = x0 + w * tx
        cy = sea + h * 0.26
        lw, lh = w * 0.11, h * 0.055
        d.rectangle([cx - lw, cy, cx + lw, cy + lh], fill=(232, 232, 226))
        d.polygon([(cx - lw, cy), (cx - lw - w * 0.02, cy + lh * 0.5),
                   (cx - lw, cy + lh)], fill=(232, 232, 226))
        d.rectangle([cx - lw * 0.25, cy - lh * 0.85, cx + lw * 0.35, cy],
                    fill=(206, 206, 198))
        d.rectangle([cx + lw * 0.5, cy - lh * 1.5, cx + lw * 0.8, cy],
                    fill=(232, 132, 52))
        d.line([cx - lw * 1.3, cy + lh * 1.1, cx + lw * 1.3, cy + lh * 1.1],
               fill=(196, 226, 232), width=2)

        pts = []
        for i in range(24):
            t = i / 23.0
            pts.append((x0 + w * (0.30 + 0.16 * tr) + t * w * (tx - 0.30 - 0.16 * tr),
                        cy - lh * 1.6 - math.sin(t * math.pi) * h * (0.34 * tr)))
        d.line(pts, fill=(240, 96, 66), width=4, joint="curve")
        d.polygon([(pts[-1][0], pts[-1][1] + 2),
                   (pts[-1][0] - 9, pts[-1][1] - 6),
                   (pts[-1][0] + 9, pts[-1][1] - 6)], fill=(255, 210, 120))


def art_trade(d, box):
    """The EU and Indonesia sign; almost every tariff line goes to zero."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (26, 44, 92))
    fw, fh = int(w * 0.36), int(h * 0.30)
    ex, ey = x0 + int(w * 0.07), y0 + int(h * 0.10)
    d.rectangle([ex, ey, ex + fw, ey + fh], fill=(22, 40, 120), outline=(120, 140, 200))
    cx, cy = ex + fw // 2, ey + fh // 2
    for i in range(12):
        a = math.radians(i * 30)
        px, py = cx + math.cos(a) * fw * 0.30, cy + math.sin(a) * fh * 0.34
        d.ellipse([px - 2.6, py - 2.6, px + 2.6, py + 2.6], fill=(244, 200, 64))
    ix = x0 + int(w * 0.53)
    d.rectangle([ix, ey, ix + fw, ey + fh // 2], fill=(208, 36, 46))
    d.rectangle([ix, ey + fh // 2, ix + fw, ey + fh], fill=(250, 248, 242),
                outline=(150, 150, 145))
    # the deal's own figure: duties go to zero on most lines. Two bars carry
    # the edition's numbers instead of an unlabelled rule that says nothing.
    bx0 = x0 + int(w * 0.07)
    bw_max = int(w * 0.86)
    by = y0 + int(h * 0.60)
    f_lab = font("arialbd.ttf", max(7, int(h * 0.062)))
    for k, (pct, name) in enumerate(((98.5, "EU"), (90.4, "IDN"))):
        yy = by + k * int(h * 0.19)
        d.rectangle([bx0, yy, bx0 + int(bw_max * pct / 100.0), yy + int(h * 0.105)],
                    fill=(244, 200, 64) if k == 0 else (232, 120, 96))
        d.text((bx0, yy - int(h * 0.075)), "%s %.1f%%" % (name, pct), font=f_lab,
               fill=(226, 232, 240))


def art_cop(d, box):
    """COP31 goes a day over; the vote slides to Sunday."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (18, 62, 52))
    f = font("arialbd.ttf", max(9, int(h * 0.075)))
    d.text((x0 + int(w * 0.06), y0 + int(h * 0.06)), "NOVEMBER", font=f, fill=(206, 222, 200))
    cols = 7
    pad = int(w * 0.06)
    cw = (w - 2 * pad - (cols - 1) * 3) // cols
    ch = int(h * 0.155)
    top = y0 + int(h * 0.24)
    for i in range(28):
        c, r = i % cols, i // cols
        bx = x0 + pad + c * (cw + 3)
        by = top + r * (ch + 3)
        if by + ch > y1 - int(h * 0.10):
            break
        past = i >= 21
        d.rectangle([bx, by, bx + cw, by + ch],
                    fill=(214, 84, 44) if i == 20 else
                    ((200, 226, 206) if past else (232, 236, 222)))
        d.text((bx + 3, by + 1), str(i + 1),
               font=font("arialbd.ttf", max(7, int(h * 0.058))),
               fill=WHITE if i >= 20 else (52, 56, 44))


def art_quake(d, box):
    """A magnitude 6.7 quake in central Peru."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (232, 214, 184))
    cy = y0 + h * 0.30
    for r, a in ((0.16, 150), (0.26, 180), (0.36, 205)):
        d.ellipse([x0 + w * 0.5 - w * r, cy - w * r * 0.42,
                   x0 + w * 0.5 + w * r, cy + w * r * 0.42],
                  outline=(150, 66, 30), width=3)
    d.polygon([(x0 + w * 0.5, cy - h * 0.13), (x0 + w * 0.5 + w * 0.05, cy + h * 0.02),
               (x0 + w * 0.5 - w * 0.05, cy + h * 0.02)], fill=(168, 30, 24))
    base = y1 - h * 0.16
    pts = []
    for i in range(121):
        t = i / 120.0
        amp = math.sin(t * 34) * math.sin(t * 3.1) * h * 0.20 * (1 - 0.55 * t)
        pts.append((x0 + w * 0.04 + t * w * 0.92, base - amp))
    d.line(pts, fill=(150, 40, 30), width=3, joint="curve")


def art_mercury(d, box):
    """BepiColombo's 37-minute engine burn onto orbit around Mercury."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (26, 32, 64))
    for i in range(26):
        sx = x0 + w * ((i * 37) % 100) / 100.0
        sy = y0 + h * ((i * 61) % 100) / 100.0 * 0.75
        d.point((sx, sy), fill=(120, 130, 170))
    pr = w * 0.16
    px, py = x0 + w * 0.68, y0 + h * 0.44
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(188, 176, 160))
    d.ellipse([px - pr * 0.45, py - pr * 0.5, px - pr * 0.05, py - pr * 0.1],
              fill=(208, 198, 182))
    pts = []
    for i in range(41):
        t = i / 40.0
        pts.append((x0 + w * 0.06 + t * w * 0.44, py - h * 0.16 + t * h * 0.22
                    - (t - t * t) * h * 0.30))
    d.line(pts, fill=(96, 168, 220), width=3, joint="curve")
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 11, pts[-1][1] - 7),
               (pts[-1][0] - 11, pts[-1][1] + 7)], fill=(242, 172, 62))


def art_port(d, box):
    """Ukrainian drones hit Russia's Ust-Luga port."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (22, 34, 58))
    d.rectangle([x0 + 1, y1 - h * 0.14, x1 - 1, y1 - 1], fill=(14, 26, 46))
    for fx in (0.14, 0.34, 0.54):
        cx = x0 + w * fx
        d.line([cx, y1 - h * 0.14, cx, y0 + h * 0.34], fill=(198, 178, 132), width=4)
        d.line([cx - w * 0.055, y0 + h * 0.34, cx + w * 0.055, y0 + h * 0.34],
               fill=(198, 178, 132), width=4)
        d.line([cx, y0 + h * 0.34, cx + w * 0.09, y0 + h * 0.34], fill=(198, 178, 132), width=4)
        d.line([cx + w * 0.09, y0 + h * 0.34, cx + w * 0.09, y0 + h * 0.46],
               fill=(198, 178, 132), width=2)
        for k in range(3):
            bx = cx + w * 0.02 + k * w * 0.035
            d.rectangle([bx, y1 - h * 0.24, bx + w * 0.03, y1 - h * 0.14],
                        fill=(198, 178, 132))
    for fx, fy in ((0.62, 0.16), (0.78, 0.30), (0.90, 0.12)):
        cx, cy = x0 + w * fx, y0 + h * fy
        d.polygon([(cx, cy), (cx - w * 0.035, cy + h * 0.13),
                   (cx + w * 0.035, cy + h * 0.13)], fill=(232, 96, 62))
    for fx in (0.66, 0.86):
        cx = x0 + w * fx
        d.ellipse([cx - 6, y1 - h * 0.10, cx + 6, y1 - h * 0.02], fill=(232, 96, 62))


def art_cricket(d, box):
    """India 486 for 4 on day three in Wellington."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (22, 84, 62))
    d.rectangle([x0 + 1, y1 - h * 0.30, x1 - 1, y1 - 1], fill=(150, 178, 96))
    for cx in (0.72, 0.78, 0.84):
        d.line([x0 + w * cx, y0 + h * 0.42, x0 + w * cx, y1 - h * 0.30],
               fill=(246, 242, 228), width=4)
    d.line([x0 + w * 0.70, y1 - h * 0.30, x0 + w * 0.86, y1 - h * 0.30],
           fill=(246, 242, 228), width=3)
    d.ellipse([x0 + w * 0.60, y0 + h * 0.60, x0 + w * 0.66, y0 + h * 0.68],
              fill=(214, 60, 46))
    for k in range(5):
        bx = x0 + w * 0.10 + k * w * 0.11
        d.rectangle([bx, y0 + h * 0.72, bx + w * 0.07, y0 + h * 0.86],
                    fill=(232, 240, 218))


def art_capture(d, box):
    """A cartel leader taken in Sinaloa; the clashes that came with it."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (206, 182, 140))
    # desert floor and a low sun
    d.rectangle([x0 + 1, y0 + int(h * 0.58), x1 - 1, y1 - 1], fill=(186, 158, 116))
    sr = h * 0.14
    sx, sy = x0 + w * 0.80, y0 + h * 0.20
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 208, 128))
    # sierra range on the horizon
    d.polygon([(x0 + 1, y0 + int(h * 0.58)), (x0 + int(w * 0.22), y0 + int(h * 0.34)),
               (x0 + int(w * 0.40), y0 + int(h * 0.58))], fill=(150, 120, 88))
    d.polygon([(x0 + int(w * 0.30), y0 + int(h * 0.58)), (x0 + int(w * 0.52), y0 + int(h * 0.40)),
               (x0 + int(w * 0.74), y0 + int(h * 0.58))], fill=(132, 104, 76))
    # a barred window with a figure behind it: "taken" reads at thumbnail size
    # from bars alone, where a handcuff silhouette was read as a magnifying
    # glass. The bars are the focal shape and nothing competes with them.
    wx0, wy0 = x0 + int(w * 0.16), y0 + int(h * 0.30)
    wx1, wy1 = x0 + int(w * 0.62), y0 + int(h * 0.78)
    d.rectangle([wx0, wy0, wx1, wy1], fill=(40, 36, 32))
    # the figure behind the bars
    hcx = (wx0 + wx1) // 2
    hr = int((wy1 - wy0) * 0.17)
    d.ellipse([hcx - hr, wy0 + int((wy1 - wy0) * 0.16) - hr,
               hcx + hr, wy0 + int((wy1 - wy0) * 0.16) + hr], fill=(146, 140, 132))
    d.polygon([(hcx - hr * 2, wy1 - 2), (hcx - hr * 1.2, wy0 + int((wy1 - wy0) * 0.46)),
               (hcx + hr * 1.2, wy0 + int((wy1 - wy0) * 0.46)), (hcx + hr * 2, wy1 - 2)],
              fill=(146, 140, 132))
    # the bars, evenly spaced across the opening
    nb = 4
    bw = max(3, int(w * 0.022))
    for k in range(nb):
        bx = wx0 + int((wx1 - wx0) * (k + 0.5) / nb) - bw // 2
        d.rectangle([bx, wy0 - int(h * 0.02), bx + bw, wy1 + int(h * 0.02)],
                    fill=(206, 198, 184))
    d.rectangle([wx0, wy0, wx1, wy1], outline=(206, 198, 184), width=max(2, int(h * 0.022)))


def art_village(d, box):
    """Bandits killed six in a village in Niger State, Nigeria."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    frame(d, box, (32, 40, 58))
    d.rectangle([x0 + 1, y0 + int(h * 0.72), x1 - 1, y1 - 1], fill=(150, 122, 82))
    # huts with thatch roofs, one with a lit doorway. The harm is carried by the
    # headline and the number, not by a symbol: a red cross was read as a
    # clinic, which would have misstated the story rather than summarised it.
    for fx, fw_, lit in ((0.12, 0.20, False), (0.44, 0.24, True), (0.80, 0.18, False)):
        bx = x0 + w * fx
        bw, bh = w * fw_, h * 0.34
        by = y0 + h * 0.72
        d.rectangle([bx, by - bh, bx + bw, by], fill=(122, 92, 62))
        d.polygon([(bx - w * 0.03, by - bh), (bx + bw / 2, by - bh - h * 0.20),
                   (bx + bw + w * 0.03, by - bh)], fill=(168, 142, 88))
        if lit:
            d.rectangle([bx + bw * 0.38, by - bh * 0.55, bx + bw * 0.62, by],
                        fill=(248, 186, 96))


ART = {1: art_strike, 2: art_trade, 3: art_capture, 6: art_cop, 8: art_quake,
       7: art_mercury, 10: art_port, 12: art_cricket, 26: art_village}


def draw_art(img, n, box):
    """Draw an illustration clipped to its box, however far its strokes reach."""
    global SUPPRESS
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0 + 1), int(y1 - y0 + 1)
    tile = Image.new("RGB", (w, h), PAPER)
    # The drawing renders into its own tile at local coordinates; its labels are
    # part of the picture, not layout text, so keep them out of the audit record.
    SUPPRESS = True
    try:
        ART[n](ImageDraw.Draw(tile), (0, 0, w - 1, h - 1))
    finally:
        SUPPRESS = False
    img.paste(tile, (int(x0), int(y0)))


# caption drawn over each picture: the words that have to survive a thumbnail
CAPTION = {
    1: ("IRAN HITS", "BAHRAIN"),
    2: ("EU\u2013INDONESIA", "TRADE PACT"),
    3: ("CARTEL BOSS", "TAKEN"),
    6: ("COP31:", "+1 DAY"),
    7: ("MERCURY", "ORBIT BURN"),
    8: ("M6.7 QUAKE", "PERU"),
    10: ("DRONES HIT", "UST-LUGA"),
    12: ("INDIA", "486 FOR 4"),
    26: ("NIGERIA", "6 KILLED"),
}

# the hour the edition first had each panel's story, taken from its own
# links[].publishedAt and from nothing else. content_audit re-derives every
# one of these from ed21.json and fails the build on a single wrong minute or
# on any story whose first report falls outside 21 November in UTC.
# 9 and 10 carry no timestamp; 12's first report is 2026-11-20T23:04:57Z, the
# previous day in UTC, so all three carry no hour rather than an invented one.
CLOCK = {
    1: "13:44",
    2: "12:04",
    3: "14:36",
    6: "17:12",
    8: "05:30",
    26: "13:01",
}

# the edition's own tiers, so the page says which stories it judged the day's
# leads rather than presenting every panel as equally important. These are all
# three of the edition's tier-"lead" stories: 1, 2 and 3.
LEADS = [1, 2, 3]

PANELS = [1, 2, 3, 6, 8, 10, 12, 26]
# every remaining story of the edition, so the page covers the whole day
FOOT = [4, 5, 7, 9, 11, 13] + list(range(14, 36))
FOOT = [n for n in FOOT if n not in PANELS]


def main(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # region tally in the top rail: where the day's news actually happened
    d.rectangle([M, 20, M + 3, 32], fill=RED)
    caps(d, (M + 9, 20), "THE WORLD ON ONE DAY", font("arialbd.ttf", 12), RED)
    tally = "  ".join("%s %d" % (lbl, sum(1 for s in STORIES if s[1] == reg))
                      for reg, (_, lbl) in
                      (("europe", REGION["europe"]), ("americas", REGION["americas"]),
                       ("asia", REGION["asia"]), ("middle-east", REGION["middle-east"]),
                       ("africa", REGION["africa"]), ("world", REGION["world"]),
                       ("oceania", REGION["oceania"])))
    f_tail = font("arialbd.ttf", 10.5)
    caps(d, (RIGHT - caps_width(d, tally, f_tail), 21), tally, f_tail, SOFT)
    d.line([M, 42, RIGHT, 42], fill=RULE, width=2)

    # masthead: the date is the one thing that must never be missed
    f_day, _ = fit_caps(d, "SATURDAY", "arialbd.ttf", 24, EDGE, 12, track=6.0)
    caps(d, (M, 54), "SATURDAY", f_day, RED, track=6.0)
    date_line = "21 NOVEMBER 2026"
    f_date, _ = fit(d, date_line, "georgiab.ttf", 108, EDGE, 1)
    d.text((M, 84), date_line, font=f_date, fill=INK)
    sub = ("")

    # the day in six hard numbers, one per region: the space the teaser used
    # to take, spent on the figures a reader remembers instead of repeated
    # headlines. Every numeral is the edition's own.
    NUMBERS = [
        ("americas", "M6.7", "Peru quake, 8 hurt"),
        ("oceania", "486-4", "India at stumps"),
        ("asia", "98.5%", "EU tariff lines"),
        ("world", "$25,500", "Bitcoin's low"),
        ("europe", "82,500", "French marches"),
        ("africa", "US$3bn", "Uganda rail off"),
    ]
    nb_top, nb_h = 176, 66
    ncell = EDGE // len(NUMBERS)
    f_cap = font("arial.ttf", 10)
    for i, (reg, big, cap) in enumerate(NUMBERS):
        cx0 = M + i * ncell
        col = REGION[reg][0]
        d.rectangle([cx0, nb_top, cx0 + ncell - 3, nb_top + 3], fill=col)
        # the numeral carries the cell, so it is sized to fill it; anything
        # under ~10pt turns to grey noise at 300px and reads as garbled text
        f_num = font("georgiab.ttf", 34)
        while tw(d, big, f_num) > ncell - 12 and f_num.size > 16:
            f_num = font("georgiab.ttf", f_num.size - 1)
        d.text((cx0, nb_top + 4), big, font=f_num, fill=INK)
        caps(d, (cx0, nb_top + 44), REGION[reg][1], font("arialbd.ttf", 8), col)
        while tw(d, cap, f_cap) > ncell - 12:
            f_cap = font("arial.ttf", f_cap.size - 1)
        d.text((cx0, nb_top + 53), cap, font=f_cap, fill=SOFT)
        if i:
            d.line([cx0 - 2, nb_top + 6, cx0 - 2, nb_top + nb_h - 4], fill=(214, 206, 190), width=1)
    d.line([M, 246, RIGHT, 246], fill=RULE, width=2)

    # measure, then draw: the two rows must share a height or the grid tears
    gap = 14
    pw = (EDGE - 3 * gap) // 4
    art_h = 132
    band_h = BAND_H
    f_head = font("georgiab.ttf", 15)
    f_deck = font("arial.ttf", 10.5)
    f_kick = font("arialbd.ttf", 9.5)
    f_src = font("arialbd.ttf", 8.5)

    def measure(a_h):
        hs = []
        for n in PANELS:
            st = by_n(n)
            h = a_h + band_h + 8 + 15
            h += int(15 * 1.14) * len(wrap(d, st[2], f_head, pw))
            if st[3]:
                h += 3 + 12 * len(wrap(d, st[3], f_deck, pw)[:1])
            h += 3 + 11
            hs.append(h)
        return [max(hs[0:4]), max(hs[4:8])]

    top = 258
    # the briefs rail sizes itself first; the pictures then take what is left
    f_b = font("arialbd.ttf", 10.5)
    f_r = font("arial.ttf", 10.5)
    cols = 4
    colw = (EDGE - 3 * 14) // 4
    # the briefs stay in three wider columns even though the panels went to
    # four: a 4-up footer column cannot hold a headline without clipping it
    f_cols = 3
    f_colw = (EDGE - 2 * 16) // f_cols
    rows = (len(FOOT) + f_cols - 1) // f_cols
    lead = 13.0
    close_rule = H - M - 26
    foot_h = (rows - 1) * lead + 12
    y_foot = close_rule - 12 - foot_h
    rule = y_foot - 14
    # shrink the pictures until both rows clear the footer band
    while art_h > 70:
        row_h = measure(art_h)
        if top + row_h[0] + gap + row_h[1] <= rule - 10:
            break
        art_h -= 2
    row_h = measure(art_h)
    for i, n in enumerate(PANELS):
        st = by_n(n)
        col = colour(st)
        cx = M + (i % 4) * (pw + gap)
        cy = top if i < 4 else top + row_h[0] + gap

        # the picture, whole: nothing drawn over it
        d.rectangle([cx, cy, cx + pw, cy + art_h], outline=RULE, width=1)
        draw_art(img, n, (cx, cy, cx + pw, cy + art_h))

        # the label as a solid band under the picture, readable at any size
        d.rectangle([cx, cy + art_h, cx + pw, cy + art_h + band_h], fill=col)
        big, small = CAPTION[n]
        f1, s1 = fit_caps(d, big, "arialbd.ttf", 21, pw - 16, 9)
        f2, s2 = fit_caps(d, small, "arialbd.ttf", 21, pw - 16, 9)
        ty = cy + art_h + 5
        d.text((cx + 8, ty), big, font=f1, fill=WHITE)
        d.text((cx + 8, ty + s1 + 5), small, font=f2, fill=(255, 246, 238))

        ty = cy + art_h + band_h + 8
        if n in LEADS:
            # a solid chip, not an outline: at this size a hairline box breaks
            # up in any downscale, and the chip has to survive 300px
            f_l = font("arialbd.ttf", 8.5)
            label = "LEAD"
            lw = caps_width(d, label, f_l, 0.6)
            d.rectangle([cx, ty - 1, cx + lw + 8, ty + f_l.size + 2], fill=col)
            caps(d, (cx + 4, ty), label, f_l, WHITE, track=0.6)
            caps(d, (cx + lw + 13, ty), region_label(st), f_kick, col)
        else:
            caps(d, (cx, ty), region_label(st), f_kick, col)
        # the hour the edition first had this story, in the same rail as the
        # region: the clock the band used to carry, now next to what it times
        if n in CLOCK:
            stamp = "%s UTC" % CLOCK[n]
            f_c = font("arialbd.ttf", 8.5)
            caps(d, (cx + pw - caps_width(d, stamp, f_c, 0.4), ty), stamp, f_c, FAINT, track=0.4)
        ty += 14
        for ln in wrap(d, st[2], f_head, pw):
            d.text((cx, ty), ln, font=f_head, fill=INK)
            ty += int(15 * 1.14)
        # the deck is capped at two lines, and an overlong one is clipped at a
        # word boundary with an ellipsis. A panel with no summary still spends
        # the same vertical space, so every credit line in a row shares a
        # baseline instead of one panel's source drifting up under its headline.
        whole = wrap(d, st[3], f_deck, pw) if st[3] else []
        deck_lines = whole[:2]
        if len(whole) > 2:
            deck_lines[1] = clip_to(d, deck_lines[1] + " " + whole[2], f_deck, pw)
        for k, ln in enumerate(deck_lines):
            d.text((cx, ty + 2 + k * 12), ln, font=f_deck, fill=SOFT)
        ty += 2 + 12 * 2
        caps(d, (cx, ty), st[4].upper(), f_src, FAINT)

    # the rest of the day, anchored to the foot so the page closes cleanly
    d.line([M, y_foot - 14, RIGHT, y_foot - 14], fill=RULE, width=2)
    caps(d, (M, y_foot), "ALSO ON THE DAY", font("arialbd.ttf", 12), INK)
    note = "AP · REUTERS · AFP · BBC · USGS · ESA · EU COMMISSION"
    caps(d, (RIGHT - caps_width(d, note, f_src), y_foot + 2), note, f_src, FAINT)

    for i, n in enumerate(FOOT):
        st = by_n(n)
        cx = M + (i // rows) * (f_colw + 16)
        yy = y_foot + 26 + (i % rows) * lead
        d.rectangle([cx, yy + 3, cx + 3, yy + 9], fill=colour(st))
        head = st[2]
        x = cx + 10
        # clip at a word boundary with an ellipsis: a headline cut mid-word
        # ("...in a tria") reads as a broken render, not as an abbreviation
        if ": " in head:
            actor, rest = head.split(": ", 1)
            d.text((x, yy), actor + ":", font=f_b, fill=INK)
            x += tw(d, actor + ":", f_b) + tw(d, " ", f_r)
            rest = clip_to(d, rest, f_r, cx + f_colw - 2 - x)
            if rest:
                d.text((x, yy), rest, font=f_r, fill=INK)
        else:
            d.text((x, yy), clip_to(d, head, f_r, cx + f_colw - 2 - x), font=f_r, fill=INK)

    # closing line: what the page promises about itself
    d.line([M, H - M - 26, RIGHT, H - M - 26], fill=RULE, width=1)
    check = ("Every story above happened, or was first reported, on Saturday 21 November 2026 "
             "in some time zone.")
    d.text((M, H - M - 13), check, font=font("arial.ttf", 11), fill=SOFT)
    done = "ONE DAY, ONE PICTURE"
    caps(d, (RIGHT - caps_width(d, done, f_src), H - M - 12), done, f_src, RED)

    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes) foot_y=%d" % (out_path, Path(out_path).stat().st_size, y_foot))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
