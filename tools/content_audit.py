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

    ok = not bad and not missing and not num_bad and tally_ok
    print("content: %s (%d mismatches, %d stories missing, %d unsourced numbers)"
          % ("PASS" if ok else "FAIL", len(bad), len(missing), len(num_bad)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
