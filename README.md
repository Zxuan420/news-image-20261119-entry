# news-image-20261119-entry

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Zxuan420/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Zxuan420/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A pure Python (standard library only) program that draws one 1024x1024 image summing up the world's news of Thursday 19 November 2026: the Trump-Xi-Putin trilateral summit in Shenzhen and its peace declaration, the World Court ruling Myanmar committed genocide against the Rohingya, tanker attacks in the Strait of Hormuz, a migrant boat sinking off Senegal, and Mongolia's president resigning — plus the day's other big stories in a footer strip. Flat newspaper-front-page style with a small embedded bitmap font, fully deterministic.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Details
- Canvas: 1024x1024 RGB PNG
- Zero external dependencies (uses standard library `struct`, `zlib`, `math`, `os`).
- Fully deterministic: identical byte output across runs.
- No network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=rkyytyv2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
