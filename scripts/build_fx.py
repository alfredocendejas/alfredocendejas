#!/usr/bin/env python3
"""Animated hero pieces for the profile: a self-typing terminal and a neural
network where pulses travel from the tech stack to shipped products.

Run:  python3 scripts/build_fx.py
Uses SMIL (<animate>/<animateMotion>), which runs inside <img>-embedded SVGs in
Chrome, Safari and Firefox. Base attributes hold the final state, so a viewer
without SMIL still sees the full content.
"""
import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"
OUT.mkdir(parents=True, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
BG, BORDER = "#0d1117", "#21262d"


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


# ======================================================================= terminal
# (kind, text segments). Segments are (text, color). "cmd" lines are typed.
GREEN, WHITE, GREY, BLUE, PURPLE, ORANGE = "#3fb950", "#e6edf3", "#8b949e", "#58a6ff", "#d2a8ff", "#f78166"
SCRIPT = [
    ("cmd", "whoami"),
    ("out", [("Alfredo Cendejas", WHITE), (" · Senior Tech Project Manager · Founder @ Milktech", GREY)]),
    ("cmd", "cat ~/.location"),
    ("out", [("Jalisco, Mexico", WHITE), ("  (EN / ES)", GREY)]),
    ("cmd", "ls ~/projects"),
    ("out", [("recompensarte/  ", ORANGE), ("notchhub/  ", BLUE), ("mac-sweeper/  ", GREEN), ("silicon-ai/", PURPLE)]),
    ("cmd", "uptime"),
    ("out", [("up 8+ years", WHITE), (" · 60+ projects shipped · 1M+ users served", GREY)]),
    ("cmd", "echo $FOCUS"),
    ("out", [("AI agents · on-device LLMs · Web3 · native macOS", BLUE)]),
]

CHAR_W = 8.45      # advance of a 14px monospace glyph (slightly generous)
LINE_H = 24
TYPE_PER_CHAR = 0.075
PAUSE_CMD = 0.35   # before typing starts
PAUSE_OUT = 0.55   # after output appears
HOLD = 4.0         # final screen stays this long
FADE = 0.6

W = 860
TOP = 58
H = TOP + LINE_H * len(SCRIPT) + 26

# timeline
t = 0.6
events = []
for kind, payload in SCRIPT:
    if kind == "cmd":
        t += PAUSE_CMD
        start = t
        t += TYPE_PER_CHAR * len(payload)
        events.append((kind, payload, start, t))
    else:
        t += 0.12
        events.append((kind, payload, t, t))
        t += PAUSE_OUT
final_prompt_at = t
T = t + HOLD + FADE  # full cycle


def kt(sec):
    return max(0.0, min(1.0, sec / T))


def discrete_anim(attr, timeline):
    """timeline: list of (seconds, value) in order; first must be at 0."""
    keys = [f(kt(s)) for s, _ in timeline]
    vals = [str(v) for _, v in timeline]
    return (f'<animate attributeName="{attr}" dur="{f(T)}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{";".join(keys)}" values="{";".join(vals)}"/>')


fade_at = T - FADE
body = []
body.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{BORDER}"/>')
body.append(f'<path d="M1 15a14 14 0 0 1 14-14h{W-30}a14 14 0 0 1 14 14v21H1z" fill="#161b22"/>')
body.append(f'<line x1="1" y1="36" x2="{W-1}" y2="36" stroke="{BORDER}"/>')
for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    body.append(f'<circle cx="{22 + i*20}" cy="18.5" r="6" fill="{c}"/>')
body.append(f'<text x="{W/2}" y="23" font-size="12.5" fill="{GREY}" font-family="{SANS}" text-anchor="middle">alfredo@milktech — ~ — zsh</text>')

defs = []
lines = []
x0 = 26
prompt = [("➜ ", GREEN), ("~ ", BLUE)]
prompt_w = 4 * CHAR_W

for i, (kind, payload, start, end) in enumerate(events):
    y = TOP + i * LINE_H
    if kind == "cmd":
        full = (len(payload) + 1) * CHAR_W
        cid = f"c{i}"
        steps = [(0, 0), (start, 0)]
        n = len(payload)
        for k in range(1, n + 1):
            steps.append((start + (end - start) * k / n, f(k * CHAR_W + 1)))
        steps.append((fade_at, f(full)))
        steps.append((T, 0))
        # dedupe identical times
        clean = []
        for s, v in steps:
            if clean and abs(clean[-1][0] - s) < 1e-6:
                clean[-1] = (s, v)
            else:
                clean.append((s, v))
        defs.append(f'<clipPath id="{cid}"><rect x="{f(x0 + prompt_w)}" y="{y-16}" width="{f(full)}" height="22">'
                    f'{discrete_anim("width", clean)}</rect></clipPath>')
        vis = discrete_anim("opacity", [(0, 0), (max(start - PAUSE_CMD, 0.001), 1), (fade_at, 1), (T, 0)])
        spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in prompt)
        lines.append(f'<g opacity="1">{vis}<text x="{x0}" y="{y}" font-size="14" font-family="{MONO}" xml:space="preserve">{spans}</text>'
                     f'<text x="{f(x0 + prompt_w)}" y="{y}" font-size="14" fill="{WHITE}" font-family="{MONO}" '
                     f'clip-path="url(#{cid})" xml:space="preserve">{escape(payload)}</text></g>')
    else:
        vis = discrete_anim("opacity", [(0, 0), (start, 1), (fade_at, 1), (T, 0)])
        spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in payload)
        lines.append(f'<text x="{x0}" y="{y}" font-size="14" font-family="{MONO}" xml:space="preserve">{vis}{spans}</text>')

# final prompt with blinking cursor
y = TOP + len(events) * LINE_H
vis = discrete_anim("opacity", [(0, 0), (final_prompt_at, 1), (fade_at, 1), (T, 0)])
spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in prompt)
lines.append(f'<g>{vis}<text x="{x0}" y="{y}" font-size="14" font-family="{MONO}" xml:space="preserve">{spans}</text>'
             f'<rect x="{f(x0 + prompt_w + 1)}" y="{y-13}" width="8" height="16" fill="{GREEN}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect></g>')

terminal = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="Terminal: whoami, Alfredo Cendejas, Senior Tech Project Manager, Founder at Milktech">\n'
            f'<defs>{"".join(defs)}</defs>\n' + "\n".join(body) + "\n" + "\n".join(lines) + "\n</svg>\n")
(OUT / "terminal.svg").write_text(terminal)

# ======================================================================= network
random.seed(7)
W, H = 860, 330
INPUTS = ["Claude", "MLX", "Next.js", "Swift", "Solidity", "Firebase"]
OUTPUTS = [("Recompensarte", ORANGE), ("NotchHub", BLUE), ("Mac Sweeper", GREEN), ("Silicon AI", PURPLE)]
HIDDEN = [5, 5]

cols_x = [150, 340, 520, 700]
top, bottom = 52, H - 40


def column(n, x):
    if n == 1:
        return [(x, (top + bottom) / 2)]
    gap = (bottom - top) / (n - 1)
    return [(x, top + gap * i) for i in range(n)]


layers = [column(len(INPUTS), cols_x[0])] + [column(n, cols_x[1 + i]) for i, n in enumerate(HIDDEN)] + [column(len(OUTPUTS), cols_x[3])]

parts = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
         f'<text x="26" y="30" font-size="10.5" font-weight="700" letter-spacing="1.2" fill="#6e7681" font-family="{SANS}">STACK</text>',
         f'<text x="{W-26}" y="30" font-size="10.5" font-weight="700" letter-spacing="1.2" fill="#6e7681" font-family="{SANS}" text-anchor="end">SHIPPED</text>']

# edges
edges = []
for a, b in zip(layers, layers[1:]):
    for p in a:
        for q in b:
            edges.append((p, q))
            parts.append(f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" stroke="#30363d" stroke-width="1" stroke-opacity=".55"/>')

# pulses: random full paths input -> h1 -> h2 -> output
pdefs = []
for k in range(14):
    path = [random.choice(layer) for layer in layers]
    out_idx = layers[-1].index(path[-1])
    color = OUTPUTS[out_idx][1]
    d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in path)
    dur = random.uniform(2.6, 3.6)
    begin = random.uniform(0, 6)
    pid = f"p{k}"
    pdefs.append(f'<path id="{pid}" d="{d}"/>')
    parts.append(
        f'<circle r="3.2" fill="{color}" opacity="0">'
        f'<animateMotion dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite" rotate="auto"><mpath href="#{pid}"/></animateMotion>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.85;1" dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        f'</circle>')
    parts.append(
        f'<circle r="8" fill="{color}" opacity="0">'
        f'<animateMotion dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion>'
        f'<animate attributeName="opacity" values="0;.18;.18;0" keyTimes="0;.08;.85;1" dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        f'</circle>')

# nodes
for li, layer in enumerate(layers):
    for ni, (x, y) in enumerate(layer):
        if li == len(layers) - 1:
            color = OUTPUTS[ni][1]
        elif li == 0:
            color = "#adbac7"
        else:
            color = "#6e7681"
        r = 7 if li in (0, len(layers) - 1) else 5
        delay = (li * 0.4 + ni * 0.23) % 2.4
        parts.append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{r+5}" fill="{color}" opacity=".08">'
            f'<animate attributeName="r" values="{r+3};{r+8};{r+3}" dur="2.4s" begin="{f(delay)}s" repeatCount="indefinite"/></circle>')
        parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r-4 if r > 5 else 1.5}" fill="{color}"/>')

for (x, y), lab in zip(layers[0], INPUTS):
    parts.append(f'<text x="{f(x-18)}" y="{f(y+4.5)}" font-size="13" fill="#c9d1d9" font-family="{SANS}" text-anchor="end">{escape(lab)}</text>')
for (x, y), (lab, c) in zip(layers[-1], OUTPUTS):
    parts.append(f'<text x="{f(x+18)}" y="{f(y+4.5)}" font-size="13" font-weight="600" fill="{c}" font-family="{SANS}">{escape(lab)}</text>')

network = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="Neural network: Claude, MLX, Next.js, Swift, Solidity and Firebase flowing into Recompensarte, NotchHub, Mac Sweeper and Silicon AI">\n'
           f'<defs>{"".join(pdefs)}</defs>\n' + "\n".join(parts) + "\n</svg>\n")
(OUT / "network.svg").write_text(network)

print(f"terminal.svg cycle {T:.1f}s, network.svg with {len(edges)} edges")
