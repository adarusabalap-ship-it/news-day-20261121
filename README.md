# news-day-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/adarusabalap-ship-it/news-day-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/adarusabalap-ship-it/news-day-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One poster that sums up Saturday 21 November 2026: eight drawn panels, each one story of that day, under one masthead that names the date. The stories, headlines and figures are the ones the day's news services reported; every string in the picture comes from that edition, and the drawing is system-font type and flat vector shapes only, so the same run always writes the same bytes.

The eight panels cover all six continents the edition reports from plus the wider world: an Iranian strike setting a site on fire in Bahrain, the EU and Indonesia signing a trade pact, Mexico taking a cartel leader, COP31 running a day over, an M6.7 quake in central Peru, Ukrainian drones hitting Russia's Ust-Luga port, India 486 for 4 against New Zealand, and bandits killing six in a Nigerian village. A footer rail lists the remaining 27 of the edition's 35 stories.

All three of the edition's own tier-"lead" stories are among the panels and carry a LEAD chip: Bahrain, the trade pact, and the Mexican capture. The other five panels are the edition's "card" stories, one per region, so Africa gets a face rather than only a footer line.

Two bands sit above the panels: the region tally of the whole edition and the day in six hard numbers. Each panel then carries its region, and the UTC hour the edition first had that story, in one rail above its headline — six of the eight have a first report inside the day, and the two that do not carry no time rather than an invented one.

## Checks

- `python tools/layout_audit.py` measures every drawn string with `textbbox` and fails on any overlap, any text off the measure, any caption overflowing its band, and any string it could not measure.
- `python tools/content_audit.py` matches every headline, summary and source against the edition, re-derives the region tally, checks each clock time against that story's own first report and rejects any hour whose report falls outside the day, and refuses either to mark a story the edition does not tier as a lead or to leave one of the edition's leads unmarked.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program copies `entry.png` (1024x1024, under 1 MiB) to the output directory after checking its signature and size, so a build that would fail the gate fails here first. It uses the Python standard library only and touches no network.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
