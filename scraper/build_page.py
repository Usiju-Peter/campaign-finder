"""Assemble public/index.html (chosen look) and public/directions/{a,b,c}.html from scraper/page.html.
usage: python scraper/build_page.py [default_look=a]"""
import os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
page = open(os.path.join(ROOT, "scraper", "page.html"), encoding="utf-8").read()

BASE = """
#dash-root { max-width: 1480px; margin: 0 auto; padding-block: 0 48px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
body { margin: 0; background: var(--color-bg); color: var(--color-fg); font: 14px/1.45 var(--font-anthropic-sans); }
.dash-select { font: inherit; color: var(--color-fg); background-color: var(--color-bg); border: 1px solid var(--color-border-line); border-radius: var(--cds-radius); padding: 6px 8px; }
:root { --cds-font-size-caption:12.5px; --cds-font-size-body:14px; --cds-font-size-heading:17px; --cds-font-size-title:34px; --cds-font-weight-medium:600;
  --cds-gap-xs:4px; --cds-gap-sm:8px; --cds-gap-md:14px; --cds-gap-lg:22px; --cds-pad-lg:18px; }
.cf-hero { margin-top: 16px; padding: 30px 28px 26px; border-radius: var(--cds-radius); }
"""

LOOKS = {
 # A: Money desk: deep navy trading-desk feel, gold for money, mono numbers
 "a": dict(name="Money desk", fonts="Manrope:wght@400;600;800&family=IBM+Plex+Mono:wght@500;600", colors=["#f2b84b", "#4cc9f0", "#b388ff", "#3ecf8e"], css="""
:root { color-scheme: dark; --color-fg:#e8eef7; --color-fg-muted:#8a9bb4; --color-bg:#0a1220; --color-panel:#101b2d; --color-border-line:#1e2b42;
  --color-ok:#3ecf8e; --color-warn:#f2b84b; --color-bad:#ff6b6b; --font-anthropic-sans: Manrope, system-ui, sans-serif; --font-anthropic-serif: 'IBM Plex Mono', ui-monospace, monospace;
  --cds-radius:12px; --cds-chart-grid:#18243a; --cds-chart-axis:#2a3a56; --cds-text-secondary:#8a9bb4; --cds-surface-popover:#15233a; --cds-border:#2a3a56; --cds-shadow-popover:0 10px 30px rgba(0,0,0,.45); }
.cf-hero { background: radial-gradient(900px 300px at 10% 0%, rgba(242,184,75,.16), transparent 60%), linear-gradient(180deg, #0e1a2e, #0a1220); border: 1px solid #1e2b42; }
.cf-hero h1 { font-family: Manrope, sans-serif !important; font-weight: 800 !important; letter-spacing: -.02em; font-size: 40px !important; }
.cf-eyebrow { color: #f2b84b !important; }
.cf-take b { color: #f2b84b !important; }
.cf-kpi .cf-v, .cf-pick-big { color: #f2b84b; font-weight: 600; }
.cf-kpi { border-top: 2px solid #f2b84b !important; }
.cf-pick { background: linear-gradient(180deg, #13223a, #101b2d) !important; }
.cf-pick:hover { box-shadow: 0 10px 30px rgba(0,0,0,.4), 0 0 0 1px #f2b84b55; }
.cf-pick-bar i { background: linear-gradient(90deg, #f2b84b, #3ecf8e) !important; }
.cf-table th { text-transform: uppercase; letter-spacing: .06em; font-size: 10.5px; }
.cf-table td { font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
.cf-table td:first-child { font-family: Manrope, sans-serif; font-size: 13px; }
.cf-chip:has(input:checked) { border-color: #f2b84b; color: #f2b84b; }
.cf-plat-tiktok, .cf-plat-x { background: #2b3a55; }
"""),
 # B: Creator studio: bright, bold, social-app energy
 "b": dict(name="Creator studio", fonts="Space+Grotesk:wght@500;700&family=Inter:wght@400;600", colors=["#6c3cf4", "#ff5c7a", "#12a37a", "#f5a524"], css="""
:root { color-scheme: light; --color-fg:#1a1433; --color-fg-muted:#6b6488; --color-bg:#f6f5ff; --color-panel:#ffffff; --color-border-line:#e7e3f7;
  --color-ok:#12a37a; --color-warn:#d9860b; --color-bad:#e5484d; --font-anthropic-sans: Inter, system-ui, sans-serif; --font-anthropic-serif: 'Space Grotesk', Inter, sans-serif;
  --cds-radius:18px; --cds-chart-grid:#efedf9; --cds-chart-axis:#d9d4ef; --cds-text-secondary:#6b6488; --cds-surface-popover:#fff; --cds-border:#e7e3f7; --cds-shadow-popover:0 12px 30px rgba(60,30,140,.16); }
.cf-hero { background-color: #6c3cf4; color: #fff;
  background-image: linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px); background-size: 28px 28px;
  }
.cf-hero h1 { font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; font-size: 44px !important; letter-spacing: -.03em; color: #fff; }
.cf-hero .cf-eyebrow { color: #ffd2dc !important; } .cf-hero .cf-take, .cf-hero .cf-hint { color: #e4dcff !important; } .cf-hero .cf-take b { color: #fff !important; }
.cf-panel, .cf-pick { box-shadow: 0 2px 0 #e7e3f7, 0 10px 24px rgba(60,30,140,.06); border-color: transparent !important; }
.cf-kpi .cf-v { font-weight: 700; color: #6c3cf4; }
.cf-pick-big { font-weight: 700; color: #6c3cf4; }
.cf-pick:hover { box-shadow: 0 16px 34px rgba(108,60,244,.18); }
.cf-pick-rank { background: #ff5c7a; color: #fff !important; border-radius: 99px; padding: 2px 9px; font-weight: 700; }
.cf-pick-bar i { background: linear-gradient(90deg, #6c3cf4, #ff5c7a) !important; }
.cf-chip:has(input:checked) { background: #6c3cf4; border-color: #6c3cf4; color: #fff; }
.cf-chip input { accent-color: #fff; }
.cf-btn { border-radius: 99px; }
.cf-charts h2, .cf-tablehead h2, .cf-sechead h2 { font-family: 'Space Grotesk', sans-serif; font-size: 20px; }
"""),
 # C: Field guide: calm, cool editorial, deep green + amber
 "c": dict(name="Field guide", fonts="DM+Serif+Display&family=DM+Sans:wght@400;600", colors=["#0f6b4f", "#c98a1b", "#4a6fa5", "#a04f7a"], css="""
:root { color-scheme: light; --color-fg:#13201a; --color-fg-muted:#5f6e66; --color-bg:#f2f5f3; --color-panel:#ffffff; --color-border-line:#dde5e0;
  --color-ok:#0f6b4f; --color-warn:#b5770e; --color-bad:#b8432f; --font-anthropic-sans: 'DM Sans', system-ui, sans-serif; --font-anthropic-serif: 'DM Serif Display', Georgia, serif;
  --cds-radius:6px; --cds-chart-grid:#e9eeeb; --cds-chart-axis:#cbd5cf; --cds-text-secondary:#5f6e66; --cds-surface-popover:#fff; --cds-border:#dde5e0; --cds-shadow-popover:0 8px 24px rgba(19,32,26,.12); }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark; --color-fg:#e6eee9; --color-fg-muted:#9aaba2; --color-bg:#0f1613; --color-panel:#151e1a;
  --color-border-line:#26332d; --cds-chart-grid:#1c2622; --cds-chart-axis:#33423b; --cds-text-secondary:#9aaba2; --cds-surface-popover:#1a2420; --cds-border:#26332d; } }
:root[data-theme="dark"] { color-scheme: dark; --color-fg:#e6eee9; --color-fg-muted:#9aaba2; --color-bg:#0f1613; --color-panel:#151e1a;
  --color-border-line:#26332d; --cds-chart-grid:#1c2622; --cds-chart-axis:#33423b; --cds-text-secondary:#9aaba2; --cds-surface-popover:#1a2420; --cds-border:#26332d; }
.cf-hero { border: 1px solid var(--color-border-line); border-bottom: 3px double var(--color-border-line); background: var(--color-panel); }
.cf-hero h1 { font-size: 52px !important; letter-spacing: -.01em; }
.cf-eyebrow { color: var(--color-ok) !important; font-weight: 600; }
.cf-panel, .cf-pick { box-shadow: none; }
.cf-kpi { border-left: 3px solid var(--color-ok) !important; border-radius: 0 6px 6px 0 !important; }
.cf-kpi .cf-v, .cf-pick-big { font-size: 38px; }
.cf-pick-rank { font-family: 'DM Serif Display', serif; font-size: 22px !important; color: var(--color-warn) !important; }
.cf-pick:hover { border-color: var(--color-ok) !important; }
.cf-charts h2, .cf-tablehead h2, .cf-sechead h2 { font-family: 'DM Serif Display', serif; font-weight: 400; font-size: 24px; }
.cf-chip:has(input:checked) { border-color: var(--color-ok); color: var(--color-ok); }
"""),
}

SHIM = open(os.path.join(ROOT, "scraper", "shim.js"), encoding="utf-8").read()

def build(key, switcher):
    L = LOOKS[key]
    sw = ""
    if switcher:
        links = " · ".join(f'<a href="{k}.html"{" aria-current=page" if k == key else ""}>{k.upper()}: {v["name"]}</a>' for k, v in LOOKS.items())
        sw = f'<nav class="cf-switch">Design directions: {links}</nav><style>.cf-switch{{font:13px/1.4 system-ui;padding:8px 16px;background:#111;color:#bbb;text-align:center}}.cf-switch a{{color:#fff;margin:0 4px}}.cf-switch a[aria-current]{{color:#f2b84b;font-weight:700}}</style>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Campaign Finder</title>
<meta name="description" content="Every Content Rewards campaign, refreshed every 4 hours: budget left, creators, pay rates.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={L['fonts']}&display=swap">
<style>{BASE}{L['css']}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>window.__COLORS = {L['colors']}; window.__DATA_URL = '{'../' if switcher else ''}data/campaigns.json';</script>
<script>{SHIM}</script>
</head><body>{sw}<div id="dash-root">
{page}
</div></body></html>"""

os.makedirs(os.path.join(ROOT, "public", "directions"), exist_ok=True)
for k in LOOKS:
    open(os.path.join(ROOT, "public", "directions", k + ".html"), "w", encoding="utf-8").write(build(k, True))
default = sys.argv[1] if len(sys.argv) > 1 else "a"
# the main page (public/index.html) is now the simple table and is edited by hand; look A lives on at /directions/
print("built directions a, b, c")
