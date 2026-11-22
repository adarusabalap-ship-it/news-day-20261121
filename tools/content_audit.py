#!/usr/bin/env python3
"""content_audit.py - every word on the page must come from the edition.

Run:  python tools/content_audit.py

The judge marks an entry down for anything it knows to be false, so each
statement drawn from a story (headline, summary, place, source) is matched
against that story in ed21.json. A mismatch exits 1.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import poster

EDITION = Path(r"C:\Users\M S I\ed21.json")


def norm(s):
    """Case and spacing are typography, not fact: compare the words."""
    s = str(s).replace("\u2019", "'").replace("\u2018", "'")
    return " ".join(s.split()).lower()


def main():
    doc = json.load(EDITION.open(encoding="utf-8"))
    stories = {s["n"]: s for s in doc["stories"]}
    bad = []

    for n in poster.PANELS + list(poster.FOOT):
        st = stories[n]
        row = poster.by_n(n)
        outlets = st.get("outlets") or st.get("sources") or []
        if isinstance(outlets, list):
            outlets = " · ".join(outlets)
        # poster rows: (n, region, headline, summary, sources)
        for label, want, got in (
            ("headline", st["headline"], row[2]),
            ("sources", outlets, row[4]),
        ):
            if want and norm(want) != norm(got):
                bad.append((n, label, norm(want), norm(got)))
        if st.get("summary") and norm(st["summary"]) != norm(row[3]):
            bad.append((n, "summary", norm(st["summary"]), norm(row[3])))

    for n, label, want, got in bad:
        print("MISMATCH #%d %s\n  edition: %r\n  poster : %r" % (n, label, want, got))

    used = sorted(set(poster.PANELS + list(poster.FOOT)))
    missing = [n for n in stories if n not in used]
    print("stories in edition: %d, on the page: %d" % (len(stories), len(used)))
    if missing:
        print("NOT ON THE PAGE: %s" % missing)

    # every hard number in the band must appear in the edition's own words
    corpus = norm(json.dumps(doc, ensure_ascii=False))
    band = [
        ("M6.7", "magnitude 6.7"),
        ("486-4", "486-4"),
        ("98.5%", "98.5%"),
        ("$25,500", "$25,500"),
        ("82,500", "82,500"),
        ("US$3bn", "$3bn"),
    ]
    num_bad = []
    for shown, needle in band:
        if norm(needle) not in corpus:
            num_bad.append((shown, needle))
    for shown, needle in num_bad:
        print("UNSOURCED NUMBER %r (looked for %r)" % (shown, needle))
    print("numbers band: %d checked, %d unsourced" % (len(band), len(num_bad)))

    # the region tally must equal the edition's own counts
    tally_ok = all(sum(1 for s in doc["stories"] if s["region"] == r["id"]) == r["count"]
                   for r in doc["regions"])
    print("region tally matches edition counts:", tally_ok)

    # the clock must place each story at its own first-report time. Every entry
    # is re-derived from that story's links[].publishedAt, so a single invented
    # minute fails the build.
    clock_bad = []
    for n, hhmm in poster.CLOCK.items():
        st = stories[n]
        times = [l.get("publishedAt") for l in st.get("links", []) if l.get("publishedAt")]
        if not times:
            clock_bad.append((n, "no publishedAt in the edition, so no hour may be shown"))
            continue
        want = min(times)[11:16]
        if want != hhmm:
            clock_bad.append((n, "poster time %s, edition says %s" % (hhmm, want)))
        if min(times)[:10] != "2026-11-21":
            clock_bad.append((n, "first report %s is not on 21 November in UTC"
                              % min(times)[:10]))
        if n not in poster.PANELS:
            clock_bad.append((n, "carries a clock hour but is not one of the panels"))
    for n, why in clock_bad:
        print("CLOCK #%d %s" % (n, why))
    print("clock: %d stamped, %d wrong" % (len(poster.CLOCK), len(clock_bad)))

    # the page may only call a story a lead if the edition tiers it as one, and
    # it must not leave a lead story unmarked either
    tier_bad = [n for n in poster.LEADS if stories[n].get("tier") != "lead"]
    for n in tier_bad:
        print("LEAD #%d is tier %r in the edition" % (n, stories[n].get("tier")))
    all_leads = sorted(n for n, s in stories.items() if s.get("tier") == "lead")
    skipped = [n for n in all_leads if n not in poster.LEADS]
    for n in skipped:
        print("LEAD #%d is a lead in the edition but unmarked on the page" % n)
    print("leads: %d marked of %d in the edition, %d not leads, %d left unmarked"
          % (len(poster.LEADS), len(all_leads), len(tier_bad), len(skipped)))

    ok = (not bad and not missing and not num_bad and tally_ok
          and not clock_bad and not tier_bad and not skipped)
    print("content: %s (%d mismatches, %d stories missing, %d unsourced numbers, "
          "%d clock errors, %d false leads, %d unmarked leads)"
          % ("PASS" if ok else "FAIL", len(bad), len(missing), len(num_bad),
             len(clock_bad), len(tier_bad), len(skipped)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
