#!/usr/bin/env python3
"""page.py - draws "Saturday 21 November 2026" as one page of world news.

Run:  python tools/page.py entry.png

Every string on this page is one of the day's own stories, as make.fun's
edition of 2026-11-21 carries it: same headline, same summary, same outlets,
same region. The layout only decides what a reader sees first -- a masthead
that names the day, three lead panels, four cards, the numbers of the day and
the remaining stories as one-liners, so a reader who missed Saturday can still
tell what happened.

Everything is drawn from primitives: cream paper, black ink, one red accent
and one colour per region. No photography, no network, no fonts beyond the
system's, so the same call always writes the same bytes.
"""

import datetime
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 16
RIGHT = W - M - 1
EDGE = RIGHT - M + 1

PAPER = (247, 243, 232)
INK = (22, 20, 17)
SOFT = (86, 79, 69)
FAINT = (128, 120, 107)
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

NUMBERS = [
    ("6.7", "Magnitude of the quake that shook central Peru; officials say 8 were hurt.", "USGS", 8),
    ("98.5%", "Share of EU tariff lines that go duty-free for Indonesia under the pact.", "EUROPEAN COMMISSION", 2),
    ("11", "Killed in the Sinaloa clashes as a cartel leader was captured.", "AP \u00b7 REUTERS", 3),
    ("21", "Chinese jets in a patrol Taiwan says it tracked; 15 crossed the median line.", "TAIPEI", 9),
    ("8%", "Bitcoin's move in a day, to a $25,500 low, its lowest since 2024.", "COINGECKO", 5),
    ("16", "Crew taken off a Russian cargo ship set on fire by drones.", "REUTERS \u00b7 BBC", 4),
]

FD = "C:/Windows/Fonts/"
_cache = {}


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


def caps(d, xy, s, f, fill, track=1.1):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += tw(d, ch, f) + track
    return x


def caps_width(d, s, f, track=1.1):
    return sum(tw(d, ch, f) + track for ch in s) - track


def para(d, xy, s, f, fill, maxw, leading, maxlines=99):
    x, y = xy
    lines = wrap(d, s, f, maxw)[:maxlines]
    for ln in lines:
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

def frame(d, box, fill):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=RULE, width=1)


def art_gulf(d, box):
    """The Gulf: two strikes inland, two tankers hit off the coast."""
    x0, y0, x1, y1 = box
    frame(d, box, (24, 62, 86))
    d.rectangle([x0 + 1, y0 + 34, x1 - 1, y1 - 1], fill=(28, 92, 116))
    d.polygon([(x0 + 1, y0 + 4), (x0 + 100, y0 + 4), (x0 + 100, y0 + 21),
               (x0 + 52, y0 + 33), (x0 + 1, y0 + 29)], fill=(206, 178, 126))
    d.polygon([(x0 + 126, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y1 - 26),
               (x0 + 170, y1 - 19), (x0 + 126, y1 - 10)], fill=(206, 178, 126))
    for dx in (0, 30):
        pts = []
        for i in range(21):
            t = i / 20.0
            pts.append((x0 + 66 + dx + t * 122, y0 + 26 + t * 36 - (t - t * t) * 62))
        d.line(pts, fill=(236, 86, 62), width=3, joint="curve")
        d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
                  fill=(236, 86, 62))
    d.polygon([(x0 + 40, y0 + 22), (x0 + 47, y0 + 4), (x0 + 53, y0 + 18),
               (x0 + 60, y0 + 2), (x0 + 66, y0 + 22)], fill=(242, 150, 46))
    for sx in (x0 + 146, x0 + 218):
        d.rectangle([sx, y1 - 20, sx + 32, y1 - 12], fill=(228, 228, 222))
        d.rectangle([sx + 21, y1 - 27, sx + 29, y1 - 20], fill=(228, 228, 222))
        d.line([sx - 3, y1 - 20, sx + 35, y1 - 20], fill=(16, 16, 16), width=2)


def art_trade(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (26, 44, 92))
    d.rectangle([x0 + 20, y0 + 12, x0 + 126, y0 + 62], fill=(22, 42, 122))
    cx, cy = x0 + 73, y0 + 37
    for i in range(12):
        a = math.radians(i * 30)
        px, py = cx + math.cos(a) * 17, cy + math.sin(a) * 17
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=(242, 198, 62))
    d.rectangle([x0 + 140, y0 + 12, x0 + 246, y0 + 36], fill=(208, 36, 46))
    d.rectangle([x0 + 140, y0 + 36, x0 + 246, y0 + 60], fill=(248, 246, 240))
    d.line([x0 + 20, y0 + 70, x0 + 246, y0 + 70], fill=(242, 198, 62), width=2)
    d.text((x0 + 20, y0 + 74), "98.5%", font=font("georgiab.ttf", 24), fill=(255, 246, 214))
    d.text((x0 + 92, y0 + 80), "of EU tariff lines duty-free",
           font=font("arial.ttf", 11), fill=(222, 230, 244))


def art_cop(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (18, 62, 52))
    d.text((x0 + 12, y0 + 5), "NOVEMBER", font=font("arialbd.ttf", 10), fill=(206, 222, 200))
    bw, bh = 16, 13
    for i in range(21):
        col, row = i % 7, i // 7
        bx = x0 + 12 + col * (bw + 3)
        by = y0 + 21 + row * (bh + 3)
        last = i == 20
        d.rectangle([bx, by, bx + bw, by + bh],
                    fill=(214, 84, 44) if last else (232, 236, 222))
        d.text((bx + 4, by), str(i + 1), font=font("arialbd.ttf", 7),
               fill=WHITE if last else (52, 56, 44))
    d.line([x0 + 12, y0 + 70, x1 - 12, y0 + 70], fill=(120, 160, 120), width=1)
    d.text((x0 + 12, y0 + 74), "+1 DAY OVER", font=font("arialbd.ttf", 10), fill=(240, 200, 170))


def art_quake(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (226, 206, 176))
    cx, cy = x0 + 40, y1 - 8
    for r in (14, 26, 40, 55):
        d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6],
                  outline=(150, 66, 30), width=2)
    d.polygon([(cx - 56, y1 - 1), (cx - 16, y0 + 10), (cx + 6, y0 + 22),
               (cx + 36, y1 - 1)], fill=(206, 178, 126))
    d.text((x0 + 84, y0 + 2), "M6.7", font=font("georgiab.ttf", 26), fill=(152, 30, 24))
    d.text((x0 + 86, y0 + 34), "PERU", font=font("arialbd.ttf", 10), fill=(120, 100, 76))


def art_mercury(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (30, 38, 72))
    cy = (y0 + y1) / 2.0
    d.ellipse([x0 + 150, cy - 18, x0 + 188, cy + 18], fill=(188, 176, 160))
    d.ellipse([x0 + 158, cy - 12, x0 + 168, cy - 2], fill=(208, 198, 182))
    pts = []
    for i in range(41):
        t = i / 40.0
        pts.append((x0 + 10 + t * 132, cy - 20 + t * 22 - (t - t * t) * 34))
    d.line(pts, fill=(96, 168, 220), width=2)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 8, pts[-1][1] - 5),
               (pts[-1][0] - 8, pts[-1][1] + 5)], fill=(242, 172, 62))
    d.text((x0 + 10, y0 + 2), "37 MIN", font=font("georgiab.ttf", 22), fill=(242, 216, 162))
    d.text((x0 + 10, y0 + 30), "ENGINE BURN", font=font("arialbd.ttf", 9), fill=(150, 168, 200))


def art_port(d, box):
    """Ust-Luga: cranes and a quay on the right, the label on clear water left."""
    x0, y0, x1, y1 = box
    frame(d, box, (22, 38, 60))
    d.rectangle([x0 + 1, y1 - 16, x1 - 1, y1 - 1], fill=(16, 44, 68))
    for cx in (x0 + 168, x0 + 214, x0 + 252):
        d.line([cx, y1 - 16, cx, y0 + 14], fill=(196, 176, 130), width=3)
        d.line([cx - 13, y0 + 14, cx + 13, y0 + 14], fill=(196, 176, 130), width=3)
        d.line([cx - 13, y0 + 14, cx - 4, y0 + 4], fill=(196, 176, 130), width=2)
    for dx, dy in ((0, 0), (14, 6)):
        d.polygon([(x0 + 232 + dx, y0 + 26 + dy), (x0 + 222 + dx, y0 + 42 + dy),
                   (x0 + 242 + dx, y0 + 42 + dy)], fill=(230, 98, 62))
    d.text((x0 + 11, y0 + 2), "PORT", font=font("georgiab.ttf", 18), fill=(240, 226, 194))
    d.text((x0 + 11, y0 + 24), "HIT BY DRONES", font=font("arialbd.ttf", 8.5),
           fill=(196, 210, 226))


def art_cricket(d, box):
    x0, y0, x1, y1 = box
    frame(d, box, (22, 84, 62))
    d.rectangle([x0 + 1, y1 - 14, x1 - 1, y1 - 1], fill=(150, 178, 96))
    for cx in (x0 + 26, x0 + 34, x0 + 42):
        d.line([cx, y0 + 8, cx, y1 - 14], fill=(244, 240, 224), width=3)
    d.ellipse([x0 + 150, y0 + 8, x0 + 162, y0 + 20], fill=(214, 60, 46))
    d.text((x0 + 70, y0 + 2), "486/4", font=font("georgiab.ttf", 23), fill=(250, 246, 226))
    d.text((x0 + 72, y0 + 29), "INDIA, DAY 3", font=font("arialbd.ttf", 8.5), fill=(206, 226, 196))
    for k in range(6):
        bx2 = x0 + 12 + k * 13
        d.rectangle([bx2, y1 - 12, bx2 + 9, y1 - 4], fill=(238, 240, 214))


ART = {1: art_gulf, 2: art_trade, 6: art_cop, 8: art_quake,
       7: art_mercury, 10: art_port, 12: art_cricket}


def draw_art(img, n, box):
    """Draw an illustration clipped to its box, however far its strokes reach."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0 + 1, y1 - y0 + 1
    tile = Image.new("RGB", (w, h), PAPER)
    ART[n](ImageDraw.Draw(tile), (0, 0, w - 1, h - 1))
    img.paste(tile, (x0, y0))

# ------------------------------------------------------------------- the page

LEADS = [1, 2, 6]
CARDS = [8, 7, 10, 12]


def rich_head(headline):
    """A brief gets its dateline in bold, the rest in roman."""
    if ": " in headline:
        head, rest = headline.split(": ", 1)
        return [("b", head + ":"), ("r", rest)]
    return [("r", headline)]


def rich_wrap(d, parts, f_bold, f_reg, maxw):
    words = []
    for style, text in parts:
        for w in text.split():
            words.append((style, w))
    lines, cur, curw = [], [], 0.0
    for style, w in words:
        f = f_bold if style == "b" else f_reg
        ww = tw(d, w, f)
        sp = tw(d, " ", f_reg) if cur else 0.0
        if cur and curw + sp + ww > maxw:
            lines.append(cur)
            cur, curw = [(style, w)], ww
        else:
            cur.append((style, w))
            curw += sp + ww
    if cur:
        lines.append(cur)
    return lines


def main(out_path):
    day = datetime.date(2026, 11, 21)
    date_line = "%s %d %s %d" % (day.strftime("%A"), day.day, day.strftime("%B"), day.year)
    regions = len({s[1] for s in STORIES})

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # rail
    caps(d, (M, 15), "ONE DAY OF WORLD NEWS, ONE PICTURE", font("arialbd.ttf", 10), RED)
    tail = "%d STORIES  \u00b7  %d REGIONS  \u00b7  ALL FROM ONE SATURDAY" % (len(STORIES), regions)
    f_tail = font("arialbd.ttf", 10)
    caps(d, (RIGHT - caps_width(d, tail, f_tail), 15), tail, f_tail, INK)
    d.line([M, 33, RIGHT, 33], fill=RULE, width=2)

    # masthead
    f_date, dsize = fit(d, date_line, "georgiab.ttf", 78, EDGE, 1)
    d.text((M, 38), date_line, font=f_date, fill=INK)
    d.line([M, 126, RIGHT, 126], fill=RULE, width=1)
    stand = ("Bahrain says an Iranian strike set a site on fire  \u00b7  the EU signs a trade "
             "pact with Indonesia  \u00b7  COP31 runs a day over")
    d.text((M, 132), stand, font=font("georgiai.ttf", 15), fill=SOFT)
    d.line([M, 158, RIGHT, 158], fill=RULE, width=1)

    # three lead panels
    gap = 14
    pw = (EDGE - 2 * gap) // 3
    art_h = 96
    y_art = 168
    y_end = 0
    for i, n in enumerate(LEADS):
        st = by_n(n)
        x0 = M + i * (pw + gap)
        x1 = x0 + pw
        col = colour(st)
        draw_art(img, n, (x0, y_art, x1, y_art + art_h))
        d.rectangle([x0, y_art + art_h, x1, y_art + art_h + 5], fill=col)
        ty = y_art + art_h + 13
        d.rectangle([x0, ty, x0 + 17, ty + 17], fill=col)
        d.text((x0 + 4, ty + 1), str(i + 1), font=font("arialbd.ttf", 12), fill=WHITE)
        caps(d, (x0 + 23, ty + 4), region_label(st), font("arialbd.ttf", 9.5), col)
        hl = st[2]
        f_h, hs = fit(d, hl, "georgiab.ttf", 25, pw, 3)
        ty += 26
        for ln in wrap(d, hl, f_h, pw):
            d.text((x0, ty), ln, font=f_h, fill=INK)
            ty += int(hs * 1.1)
        ty = para(d, (x0, ty + 6), st[3], font("arial.ttf", 12), SOFT, pw, 15, 4)
        caps(d, (x0, ty + 5), st[4].upper(), font("arialbd.ttf", 8.5), FAINT)
        y_end = max(y_end, ty + 20)

    # four cards
    y2 = y_end + 22
    gap2 = 12
    cw = (EDGE - 3 * gap2) // 4
    for i, n in enumerate(CARDS):
        st = by_n(n)
        x0 = M + i * (cw + gap2)
        x1 = x0 + cw
        col = colour(st)
        draw_art(img, n, (x0, y2, x1, y2 + 54))
        d.rectangle([x0, y2 + 54, x1, y2 + 58], fill=col)
        ty = y2 + 67
        d.rectangle([x0, ty, x0 + 15, ty + 15], fill=col)
        d.text((x0 + 3, ty + 1), str(i + 4), font=font("arialbd.ttf", 11), fill=WHITE)
        caps(d, (x0 + 20, ty + 3), region_label(st), font("arialbd.ttf", 8.5), col)
        hl = st[2]
        f_h, hs = fit(d, hl, "georgiab.ttf", 17.5, cw, 3)
        ty += 22
        for ln in wrap(d, hl, f_h, cw):
            d.text((x0, ty), ln, font=f_h, fill=INK)
            ty += int(hs * 1.13)
        ty = para(d, (x0, ty + 4), st[3], font("arial.ttf", 11), SOFT, cw, 13, 4)
        caps(d, (x0, ty + 4), st[4].upper(), font("arialbd.ttf", 7.5), FAINT)
        y_end = max(y_end, ty + 16)

    # the rest of the day, in readable type
    briefs = [s for s in STORIES if s[0] not in LEADS and s[0] not in CARDS]
    y3 = y_end + 26
    d.line([M, y3 - 14, RIGHT, y3 - 14], fill=RULE, width=2)
    caps(d, (M, y3), "ALSO ON SATURDAY", font("arialbd.ttf", 11.5), INK)
    note = "%d MORE STORIES, SAME DAY" % len(briefs)
    f_note = font("arialbd.ttf", 9.5)
    caps(d, (RIGHT - caps_width(d, note, f_note), y3 + 1), note, f_note, FAINT)
    d.line([M, y3 + 19, RIGHT, y3 + 19], fill=RULE, width=1)

    foot_y = 926
    top = y3 + 30
    band = foot_y - top
    cols, cgap = 3, 18
    cwide = (EDGE - (cols - 1) * cgap) // cols

    packed = []
    f_r = f_b = None
    size = lead = 0.0
    for size in (13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0):
        f_r = font("arial.ttf", size)
        f_b = font("arialbd.ttf", size)
        lead = size * 1.26
        items = []
        for st in briefs:
            lines = rich_wrap(d, rich_head(st[2]), f_b, f_r, cwide - 13)
            items.append((st, lines, len(lines) * lead + size * 0.6))
        if max(len(l) for _, l, _ in items) > 3:
            continue
        packed, cur, h = [], [], 0.0
        for it in items:
            if h + it[2] > band and cur:
                packed.append(cur)
                cur, h = [], 0.0
            cur.append(it)
            h += it[2]
        if cur:
            packed.append(cur)
        if len(packed) <= cols:
            break

    for j, column in enumerate(packed):
        cx = M + j * (cwide + cgap)
        cy = float(top)
        for st, lines, h in column:
            col = colour(st)
            d.rectangle([cx, cy + 2, cx + 3, cy + lead * len(lines) - 5], fill=col)
            for ln in lines:
                px = cx + 10
                for k, (style, w) in enumerate(ln):
                    f = f_b if style == "b" else f_r
                    if k:
                        px += tw(d, " ", f_r)
                    d.text((px, cy), w, font=f, fill=INK)
                    px += tw(d, w, f)
                cy += lead
            cy += size * 0.6

    # date check + footer
    d.line([M, foot_y - 8, RIGHT, foot_y - 8], fill=RULE, width=1)
    d.rectangle([M, foot_y, M + 84, foot_y + 17], fill=SOFT)
    caps(d, (M + 8, foot_y + 4), "DATE CHECK", font("arialbd.ttf", 9.5), WHITE)
    check = ("Every story here happened, or was first reported, on Saturday 21 November 2026 in some "
             "time zone, and each one is dated to that day. Nothing is stated beyond what its outlets "
             "report: where only one side's account carries the news, the line says so. Left out on "
             "purpose: stories first reported on another day, and anything still to come.")
    para(d, (M + 96, foot_y - 1), check, font("arial.ttf", 10), SOFT, RIGHT - M - 96, 13.5, 3)
    d.line([M, foot_y + 46, RIGHT, foot_y + 46], fill=RULE, width=1)
    caps(d, (M, foot_y + 55), "SOURCES  AP \u00b7 REUTERS \u00b7 AFP \u00b7 BBC \u00b7 UKMTO \u00b7 USGS \u00b7 ESA "
                              "\u00b7 EUROPEAN COMMISSION \u00b7 ICC  \u2014  ORIGINAL DRAWINGS",
         font("arialbd.ttf", 8), FAINT)
    done = "35 STORIES, ONE DAY, ONE PAGE"
    caps(d, (RIGHT - caps_width(d, done, font("arialbd.ttf", 8)), foot_y + 55), done,
         font("arialbd.ttf", 8), RED)

    print("diag: y_end=%d y3=%d top=%d band=%d size=%.1f cols=%d" %
          (y_end, y3, top, band, size, len(packed)))
    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, Path(out_path).stat().st_size))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
