#!/usr/bin/env python3
"""Generate the animated SVG cards used by the profile README.

Run:  python3 scripts/build_cards.py
Every card is self-contained SVG with CSS keyframe animations, which GitHub
renders when the SVG is embedded with <img>. Motion is disabled for viewers
with prefers-reduced-motion.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
BG, BORDER, PILL = "#0d1117", "#21262d", "#30363d"
TITLE, BODY, MUTED = "#e6edf3", "#8b949e", "#6e7681"

BASE_CSS = """
  .in { animation: rise .7s cubic-bezier(.2,.7,.2,1) both; }
  @keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  .bar { animation: glow 3.2s ease-in-out infinite; }
  @keyframes glow { 0%,100% { opacity: .55; } 50% { opacity: 1; } }
  .sweep { animation: sweep 5s linear infinite; }
  @keyframes sweep { from { transform: translateX(-160px); } to { transform: translateX(var(--w)); } }
  .dot { animation: blink 1.6s ease-in-out infinite; }
  @keyframes blink { 0%,100% { opacity: .25; } 50% { opacity: 1; } }
  @media (prefers-reduced-motion: reduce) {
    .in, .bar, .sweep, .dot { animation: none !important; }
    .sweep { display: none; }
  }
"""


def svg(w, h, label, body, extra_css=""):
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(label)}">
  <style>{BASE_CSS.replace('var(--w)', f'{w + 160}px')}{extra_css}</style>
  <defs>
    <linearGradient id="shine" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset=".5" stop-color="#ffffff" stop-opacity=".05"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14"/></clipPath>
  </defs>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{BG}" stroke="{BORDER}"/>
  <g clip-path="url(#clip)"><rect class="sweep" x="0" y="0" width="160" height="{h}" fill="url(#shine)"/></g>
{body}
</svg>
"""


def t(x, y, s, size=13.5, fill=BODY, weight=400, cls="in", delay=0.0, anchor="start", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'  <text class="{cls}" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" font-family="{FONT}" text-anchor="{anchor}"{sp}>{escape(s)}</text>\n')


def pill_width(label, size=11.5):
    return int(len(label) * size * 0.6 + 24)


def pills(x, y, labels, delay0, size=11.5, color="#adbac7", maxw=None):
    out, cx = "", x
    for i, lab in enumerate(labels):
        w = pill_width(lab, size)
        if maxw and cx + w > maxw:
            break
        d = delay0 + i * 0.08
        out += (f'  <g class="in" style="animation-delay:{d:.2f}s">'
                f'<rect x="{cx}" y="{y}" width="{w}" height="24" rx="12" stroke="{PILL}"/>'
                f'<text x="{cx + w/2}" y="{y+16}" font-size="{size}" fill="{color}" font-family="{FONT}" '
                f'text-anchor="middle">{escape(lab)}</text></g>\n')
        cx += w + 8
    return out


# ---------------------------------------------------------------- project cards
PROJECTS = {
    "recompensarte": dict(
        title="Recompensarte", accent="#f78166", status="Live",
        lines=["Loyalty & rewards platform for local businesses:",
               "digital cards, POS, bookings, rallies and wallet passes."],
        tags=["Loyalty", "POS", "Next.js", "Firebase"]),
    "notchhub": dict(
        title="NotchHub", accent="#58a6ff", status="Swift",
        lines=["Turns the macOS notch into a shared dashboard where",
               "a family of apps publish live status and quick actions."],
        tags=["macOS", "SwiftUI", "AppKit", "SPM"]),
    "macsweeper": dict(
        title="Mac Sweeper", accent="#3fb950", status="Swift",
        lines=["Deep-clean for macOS: caches, logs, Xcode & Docker",
               "leftovers, large files and login items, done safely."],
        tags=["macOS", "Cleanup", "Dev tools", "SwiftUI"]),
    "siliconai": dict(
        title="Silicon AI", accent="#d2a8ff", status="On-device",
        lines=["Fully local AI assistant for Apple Silicon. Chat, vision",
               "and voice with MLX. No cloud, encrypted history."],
        tags=["MLX", "Local LLM", "Whisper", "SwiftUI"]),
}

for key, p in PROJECTS.items():
    w, h = 480, 160
    a = p["accent"]
    body = f'  <rect class="bar" x="0" y="14" width="4" height="132" rx="2" fill="{a}"/>\n'
    body += t(38, 46, p["title"], 17, TITLE, 700, delay=0.05)
    sw = pill_width(p["status"], 10.5)
    body += (f'  <g class="in" style="animation-delay:.15s"><rect x="{w-28-sw}" y="28" width="{sw}" height="22" rx="11" '
             f'fill="{a}" fill-opacity=".12" stroke="{a}" stroke-opacity=".5"/>'
             f'<circle class="dot" cx="{w-28-sw+12}" cy="39" r="3" fill="{a}"/>'
             f'<text x="{w-28-sw/2+5}" y="43" font-size="10.5" fill="{a}" font-family="{FONT}" text-anchor="middle">'
             f'{escape(p["status"])}</text></g>\n')
    for i, line in enumerate(p["lines"]):
        body += t(38, 76 + i * 21, line, delay=0.25 + i * 0.1)
    body += pills(38, 122, p["tags"], 0.5, maxw=w - 20)
    (OUT / f"{key}.svg").write_text(svg(w, h, p["title"], body))

# ---------------------------------------------------------------- subtitle lines
SUBS = {
    "subtitle-role": ("Senior Tech Project Manager", "· Web3 & AI Solutions", "#58a6ff"),
    "subtitle-founder": ("Founder", "· Milktech", "#3fb950"),
}
for key, (strong, rest, color) in SUBS.items():
    w = int((len(strong) + len(rest)) * 8.2 + 30)
    body_ = (f'  <circle class="dot" cx="7" cy="11" r="4" fill="{color}"/>\n'
             f'  <text class="in" x="20" y="14.5" font-size="13.5" font-family="{FONT}">'
             f'<tspan fill="{TITLE}" font-weight="600">{escape(strong)}</tspan>'
             f'<tspan fill="{BODY}"> {escape(rest)}</tspan></text>\n')
    (OUT / f"{key}.svg").write_text(
        f'<svg width="{w}" height="21" viewBox="0 0 {w} 21" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{escape(strong + " " + rest)}"><style>{BASE_CSS}</style>\n{body_}</svg>\n')

# ---------------------------------------------------------------- stats
STATS = [("8+", "years shipping"), ("60+", "projects delivered"),
         ("1M+", "users at scale"), ("-50%", "delivery time")]
w, h = 860, 120
body = ""
colw = (w - 52) / len(STATS)
for i, (num, lab) in enumerate(STATS):
    cx = 26 + colw * i + colw / 2
    body += t(cx, 62, num, 34, TITLE, 700, delay=0.1 + i * 0.15, anchor="middle")
    body += t(cx, 88, lab.upper(), 10.5, MUTED, 700, delay=0.2 + i * 0.15, anchor="middle", spacing="1.2")
    if i:
        body += f'  <rect class="in" style="animation-delay:{.1+i*.15:.2f}s" x="{26+colw*i}" y="34" width="1" height="62" fill="{BORDER}"/>\n'
(OUT / "stats.svg").write_text(svg(w, h, "8+ years, 60+ projects, 1M+ users, -50% delivery time", body))

# ---------------------------------------------------------------- stack
STACK = [
    ("AI & AGENTS", ["Claude Code", "MCP", "MLX", "Ollama", "OpenAI", "n8n"]),
    ("APPS & FRONTEND", ["TypeScript", "Next.js", "React", "Ionic", "Angular", "Swift", "SwiftUI"]),
    ("BACKEND & DATA", ["Node.js", "Python", "Firebase", "PostgreSQL", "Strapi", "Stripe"]),
    ("CLOUD & OPS", ["Google Cloud", "Vercel", "Docker", "Linux", "Nginx", "GitHub Actions"]),
    ("WEB3", ["Solidity", "Smart contracts", "Wallets", "Tokenization"]),
]
w = 860
h = 30 + len(STACK) * 66
body = ""
for r, (head, items) in enumerate(STACK):
    y = 34 + r * 66
    body += t(26, y, head, 10.5, MUTED, 700, delay=r * 0.12, spacing="1.2")
    body += pills(26, y + 14, items, r * 0.12 + 0.08, size=12.5, color="#c9d1d9", maxw=w - 20)
(OUT / "stack.svg").write_text(svg(w, h, "Tech stack", body))

# ---------------------------------------------------------------- footer links
LINKS = {
    "link-web": ("alfredocendejas.com", "#58a6ff"),
    "link-linkedin": ("LinkedIn", "#58a6ff"),
    "link-x": ("X / Twitter", "#58a6ff"),
    "link-youtube": ("YouTube", "#58a6ff"),
    "link-medium": ("Medium", "#58a6ff"),
}
for key, (lab, color) in LINKS.items():
    lw = int(len(lab) * 7.4 + 22)
    (OUT / f"{key}.svg").write_text(
        f'<svg width="{lw}" height="17" viewBox="0 0 {lw} 17" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{escape(lab)}"><text x="0" y="13" font-size="13" fill="{color}" '
        f'font-family="{FONT}">↗ {escape(lab)}</text></svg>\n')

print("wrote", len(list(OUT.glob("*.svg"))), "cards to", OUT)
