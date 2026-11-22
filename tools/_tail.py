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
        d.text((x0 + 3, ty + 1), str(n), font=font("arialbd.ttf", 11), fill=WHITE)
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
    d.rectangle([M, foot_y, M + 84, foot_y + 17], fill=RED)
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

    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, Path(out_path).stat().st_size))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
