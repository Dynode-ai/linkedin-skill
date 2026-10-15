#!/usr/bin/env python3
"""Generate docs/assets/demo.svg: an animated terminal replay of /linkedin:audit.

The transcript is condensed from a real eval run (fictional persona "Maya Chen").
Edit LINES below and re-run: python docs/tools/make_demo_svg.py
Pure SVG + CSS animation, so it plays inside a GitHub README (no scripts needed).
"""
import os
from xml.sax.saxutils import escape

W, PAD, LH, FS = 1000, 28, 25, 15
T = 19.0  # loop length in seconds
COL = {
    "fg": "#e6edf3", "dim": "#8b949e", "prompt": "#a78bfa", "claude": "#d97757", "ok": "#3fb950",
    "bad": "#f85149", "accent": "#79c0ff", "chip_bad": "#3d1d20", "chip_ok": "#12301c", "bg": "#0d1117", "bar": "#161b22",
}

# Each line: (appear_at_seconds, [(text, color_key, bold)], extra)
# extra: "type" for the typed command line, "blank" for spacing.
LINES = [
    (0.4, [("❯ ", "prompt", True), ("/linkedin:audit profile.pdf jd-freshcart.txt", "fg", False)], "type"),
    (2.9, [("⏺ ", "claude", False), ("Read profile.pdf and 1 target job description", "fg", False)], None),
    (3.7, [("⏺ ", "claude", False), ("Scored with the 100-point rubric · 17 keywords checked", "fg", False)], None),
    (4.4, [], "blank"),
    (4.7, [("  Profile score", "dim", False), ("  27/100  Invisible  ", "bad", True), ("→", "dim", False), ("  ~80 after fixes  ", "ok", True)], "chips"),
    (5.4, [], "blank"),
    (5.6, [("  Do these first", "fg", True)], None),
    (6.1, [("  1 ", "accent", True), ("Replace your headline", "fg", False), ("  ·  High impact · 2 min", "dim", False)], None),
    (6.6, [("  2 ", "accent", True), ("Lead your Northwind role with the forecast model", "fg", False), ("  ·  30 min", "dim", False)], None),
    (7.1, [("  3 ", "accent", True), ("Pin the skills recruiters filter on", "fg", False), ("  ·  10 min", "dim", False)], None),
    (7.6, [], "blank"),
    (7.9, [("  New headline ", "fg", True), ("(140/220 chars, checked)", "dim", False)], None),
    (8.5, [("  Machine Learning Engineer | Demand Forecasting & Time Series |", "accent", False)], None),
    (8.7, [("  Python, SQL, LightGBM | Built the retail forecast behind weekly replenishment", "accent", False)], None),
    (9.4, [], "blank"),
    (9.7, [("  ✓ ", "ok", True), ("Report  ", "fg", True), ("linkedin/reports/audit-2026-10-16/index.html", "dim", False)], None),
    (10.2, [("  ✓ ", "ok", True), ("Memory  ", "fg", True), ("brief.md · profile.md · stories.md  (no facts invented)", "dim", False)], None),
    (10.9, [("  Next: ", "dim", False), ("/linkedin:follow", "prompt", True)], None),
]

CHAR_W = FS * 0.6  # monospace advance
TOP = 64
H = TOP + LH * len(LINES) + PAD + 8


def pct(t):
    return max(0.0, min(100.0, 100.0 * t / T))


def keyframes(name, t):
    a, b = pct(t), pct(t + 0.25)
    return (f"@keyframes {name}{{0%,{a:.2f}%{{opacity:0}}{b:.2f}%,93%{{opacity:1}}97%,100%{{opacity:0}}}}"
            f".{name}{{opacity:0;animation:{name} {T}s linear infinite}}")


def main():
    css, body = [], []
    css.append("text{font-family:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace;font-size:%dpx;white-space:pre}" % FS)
    for i, (t, spans, extra) in enumerate(LINES):
        y = TOP + i * LH
        cls = f"l{i}"
        if extra == "blank":
            continue
        css.append(keyframes(cls, t))
        x = PAD
        parts = []
        if extra == "chips":
            # Lay each segment out at a fixed x, and center chip labels inside their boxes,
            # so alignment holds whatever monospace font the viewer has.
            x = PAD + 2 * CHAR_W
            for text, col, bold in spans:
                w = len(text) * CHAR_W
                weight = ' font-weight="700"' if bold else ""
                if col in ("bad", "ok"):
                    parts.append(f'<rect x="{x:.1f}" y="{y - FS - 2}" width="{w:.1f}" height="{FS + 9}" rx="5" fill="{COL["chip_" + col]}"/>')
                    parts.append(f'<text x="{x + w / 2:.1f}" y="{y}" text-anchor="middle" fill="{COL[col]}"{weight}>{escape(text.strip())}</text>')
                    x += w + CHAR_W
                else:
                    parts.append(f'<text x="{x:.1f}" y="{y}" fill="{COL[col]}"{weight}>{escape(text.strip())}</text>')
                    x += len(text.strip()) * CHAR_W + 2 * CHAR_W
            body.append(f'<g class="{cls}">' + "".join(parts) + "</g>")
            continue
        tsp = []
        for text, col, bold in spans:
            weight = ' font-weight="700"' if bold else ""
            tsp.append(f'<tspan fill="{COL[col]}"{weight}>{escape(text)}</tspan>')
        parts.append(f'<text x="{PAD}" y="{y}">{"".join(tsp)}</text>')
        if extra == "type":
            # cover the command and slide the cover right in steps to "type" it
            cmd_len = len(spans[1][0])
            start_x = PAD + len(spans[0][0]) * CHAR_W
            cover_w = cmd_len * CHAR_W + 14
            dur = 1.8
            a, b = pct(t + 0.3), pct(t + 0.3 + dur)
            css.append(f"@keyframes type{{0%,{a:.2f}%{{transform:translateX(0)}}{b:.2f}%,100%{{transform:translateX({cover_w:.1f}px)}}}}"
                       f".cover{{animation:type {T}s steps({cmd_len}) infinite}}")
            parts.append(f'<rect class="cover" x="{start_x - 1:.1f}" y="{y - FS - 2}" width="{cover_w:.1f}" height="{FS + 8}" fill="{COL["bg"]}"/>')
            # blinking cursor that rides on the cover's left edge
            css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
                       f".cursor{{animation:blink 1s steps(1) infinite}}")
            hide = pct(t + 0.3 + dur + 0.4)
            css.append(f"@keyframes cursoroff{{0%,{hide:.2f}%{{visibility:visible}}{hide + 0.01:.2f}%,100%{{visibility:hidden}}}}"
                       f".cursorwrap{{animation:cursoroff {T}s linear infinite}}")
            parts.append(f'<g class="cursorwrap"><g class="cover"><rect class="cursor" x="{start_x:.1f}" y="{y - FS + 1}" width="{CHAR_W:.1f}" height="{FS + 3}" fill="{COL["fg"]}" opacity=".85"/></g></g>')
        body.append(f'<g class="{cls}">' + "".join(parts) + "</g>")
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}g[class^=l]{opacity:1!important}.cover,.cursorwrap{display:none}}")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal demo: /linkedin:audit scores a profile 27/100, lists the top fixes, writes a new headline and saves an HTML report">
<style>{"".join(css)}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{COL["bg"]}" stroke="#30363d"/>
<rect x="1" y="1" width="{W - 2}" height="40" rx="13" fill="{COL["bar"]}"/><rect x="1" y="26" width="{W - 2}" height="15" fill="{COL["bar"]}"/><line x1="1" y1="41" x2="{W - 1}" y2="41" stroke="#30363d"/>
<circle cx="24" cy="20" r="6" fill="#ff5f57"/><circle cx="44" cy="20" r="6" fill="#febc2e"/><circle cx="64" cy="20" r="6" fill="#28c840"/>
<text x="{W / 2}" y="25" text-anchor="middle" fill="{COL["dim"]}" style="font-size:13px">claude  ·  ~/my-linkedin</text>
{"".join(body)}
</svg>
'''
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "demo.svg")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {os.path.normpath(out)} ({len(svg)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
