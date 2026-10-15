# Regenerating the README visuals

Everything in `docs/assets/` is generated from real skill output, so you can rebuild it after a redesign.

| Asset | Source | How |
|---|---|---|
| `demo.svg` | `make_demo_svg.py` | `python docs/tools/make_demo_svg.py` |
| `hero-light.png`, `hero-dark.png`, `social-preview.png` | `hero.html` | Screenshot at 1280×440 (`?t=light` / `?t=dark`), or 1280×640 with `&social=1` |
| `audit-report.png`, `feed-preview.png`, `carousel.png`, `dashboard*.png` | `frame.html?src=<page>&w=<w>&h=<h>&title=<url text>[&scroll=<px>][&dark=1]` | Screenshot of a skill output page wrapped in the frame |

Serve the repo root locally (e.g. `python -m http.server 8765`) so pages can load their `data.js`. Then use headless Chrome:

```bash
chrome --headless=new --hide-scrollbars --force-device-scale-factor=2 --default-background-color=00000000 \
  --virtual-time-budget=6000 --window-size=1280,440 --screenshot=docs/assets/hero-light.png \
  "http://localhost:8765/docs/tools/hero.html?t=light"
```

For `frame.html`, the window size is the iframe size plus 96 px wide and 136 px tall.
