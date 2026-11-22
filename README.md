# news-day-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/adarusabalap-ship-it/news-day-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/adarusabalap-ship-it/news-day-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One poster that sums up Saturday 21 November 2026: six drawn panels, each one story of that day from a different region, under one masthead that names the date. The stories, headlines and figures are the ones the day's news services reported; every string in the picture comes from that edition, and the drawing is system-font type and flat vector shapes only, so the same run always writes the same bytes.

The six panels: an Iranian strike setting a site on fire in Bahrain; the EU and Indonesia signing a trade pact; COP31 running a day over; an M6.7 quake in central Peru; Ukrainian drones hitting Russia's Ust-Luga port; India 486 for 4 against New Zealand. A footer strip carries eight more stories of the day.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program copies `entry.png` (1024x1024, under 1 MiB) to the output directory after checking its signature and size, so a build that would fail the gate fails here first. It uses the Python standard library only and touches no network.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
