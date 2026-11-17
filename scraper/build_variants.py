"""Build each skill variant: variants/<slug>/{page.html, look.css, meta.txt} -> public/s/<slug>/index.html, plus a hub at public/s/index.html."""
import os, re, html
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
bp = open(os.path.join(ROOT, "scraper", "build_page.py"), encoding="utf-8").read()
BASE = re.search(r'BASE = """(.*?)"""', bp, re.S).group(1)
SHIM = open(os.path.join(ROOT, "scraper", "shim.js"), encoding="utf-8").read()
V = os.path.join(ROOT, "variants"); OUT = os.path.join(ROOT, "public", "s")
cards = []
for slug in sorted(os.listdir(V)):
    d = os.path.join(V, slug)
    meta = dict(l.split("=", 1) for l in open(os.path.join(d, "meta.txt"), encoding="utf-8").read().splitlines() if "=" in l)
    page = open(os.path.join(d, "page.html"), encoding="utf-8").read()
    css = open(os.path.join(d, "look.css"), encoding="utf-8").read()
    head_extra = open(os.path.join(d, "head.html"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "head.html")) else ""
    base = "" if meta.get("nobase") == "1" else BASE
    out = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Campaign Finder · {html.escape(meta['name'])}</title>
<meta name="description" content="Every Content Rewards campaign, refreshed every 4 hours. Design pass: {html.escape(meta['name'])}.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={meta['fonts']}&display=swap">
<style>{base}{css}</style>{head_extra}
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>window.__COLORS = {meta['colors']}; window.__DATA_URL = '../../data/campaigns.json';</script>
<script>{SHIM}</script>
</head><body><div id="dash-root">
{page}
</div></body></html>"""
    os.makedirs(os.path.join(OUT, slug), exist_ok=True)
    open(os.path.join(OUT, slug, "index.html"), "w", encoding="utf-8").write(out)
    cards.append((slug, meta))
items = "".join(f'<li class="{m["status"]}"><a href="{s}/"><span>{s[:2]}</span><b>{html.escape(m["name"])}</b><i>{"ready" if m["status"] == "done" else "in progress"}</i></a><p>{html.escape(m.get("note", ""))}</p></li>' for s, m in cards)
hub = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Campaign Finder · 11 design passes</title>
<style>body{{margin:0;background:#0a1220;color:#e8eef7;font:15px/1.5 system-ui,sans-serif}}main{{max-width:880px;margin:0 auto;padding:40px 16px}}
h1{{font-size:30px;margin:0 0 6px}}p.lead{{color:#8a9bb4;margin:0 0 28px}}ul{{list-style:none;padding:0;display:grid;gap:10px}}
li a{{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:12px;padding:14px 16px;background:#101b2d;border:1px solid #1e2b42;border-radius:12px;color:inherit;text-decoration:none}}
li a:hover{{border-color:#f2b84b}}li span{{color:#f2b84b;font-family:ui-monospace,monospace}}li i{{font-style:normal;font-size:12px;color:#8a9bb4}}li.done i{{color:#3ecf8e}}
li p{{margin:4px 16px 0 72px;color:#8a9bb4;font-size:13px}}li p:empty{{display:none}}</style></head><body><main>
<h1>Campaign Finder: 11 design passes</h1><p class="lead">Same data and features. Each version is look A (Money desk) improved with one design skill.</p><ul>{items}</ul></main></body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(hub)
print("built", len(cards), "variants + hub")
