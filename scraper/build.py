"""Turn the scraped pages into the dashboard data.

python scraper/build.py candidates  -> work/candidates.json (which campaign pages to open)
python scraper/build.py build       -> public/data/campaigns.json, data/history/<time>.json, data/first_seen.json
Standard library only.
"""
import json, os, re, sys, glob, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WORK, PUB, HIST = os.path.join(ROOT, "work"), os.path.join(ROOT, "public", "data"), os.path.join(ROOT, "data", "history")
for d in (WORK, PUB, HIST): os.makedirs(d, exist_ok=True)
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

def num(s, k): return float(s.replace(",", "")) * (1000 if k == "K" else 1e6 if k == "M" else 1)
CARD = re.compile(r"^(.*?) \W (\d+)([a-z]+) (.*?) \$([\d.,]+)([KM]?) ?/ ?\$([\d.,]+)([KM]?) ([\d.,]+)([KM]?) \$([\d.,]+)(?:\W\$([\d.,]+))?/1K")
UNIT = {"h": 1 / 24, "d": 1, "w": 7, "mo": 30, "y": 365}

def parse_card(text):
    m = CARD.search(text)
    if not m: return None
    return dict(org=m.group(1), age=f"{m.group(2)}{m.group(3)}", age_days=round(int(m.group(2)) * UNIT.get(m.group(3), 30)),
                title=m.group(4), paid=num(m.group(5), m.group(6)), budget=num(m.group(7), m.group(8)),
                creators=num(m.group(9), m.group(10)), rate=float((m.group(12) or m.group(11)).replace(",", "")))

def candidates():
    L = json.load(open(os.path.join(WORK, "list.json"), encoding="utf-8"))
    out = []
    for c in L:
        p = parse_card(c["text"])
        if p is None or (p["budget"] - p["paid"] >= 1500 and p["paid"] < 0.85 * p["budget"]):
            out.append(c["href"])
    json.dump(out, open(os.path.join(WORK, "candidates.json"), "w"))
    print("candidates:", len(out))

def parse_detail(t):
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    if "Back" not in lines: return None
    b = lines.index("Back")
    m = re.search(r"Budget\s*\$([\d,.]+)\s*/\s*\$([\d,.]+)", t)
    paid, bud = (float(m.group(1).replace(",", "")), float(m.group(2).replace(",", ""))) if m else (None, None)
    plats = re.findall(r"\n(YouTube|Instagram|TikTok|X|Twitter|Facebook|Snapchat)\n\s*\n?Per (1K views|approved post)\s*\n\s*\n?\$([\d.,]+)", t)
    maxp = re.findall(r"Max payout\s*\n\s*\n?\$([\d,.]+)", t)
    minp = re.findall(r"Min payout\s*\n\s*\n?\$([\d,.]+)", t)
    low = t.lower(); flags = set()
    if re.search(r"casino|gambl|\bbet(ting)?\b|roobet|stake\.com|sportsbook|poker|blackjack", low): flags.add("gambling")
    if re.search(r"\bface\b|on camera|on-camera|show your face|facecam|face cam", low): flags.add("face")
    if re.search(r"\b(usa|u\.s\.|united states|us audience|us-based|us viewers|tier[- ]?1|tier one|american)\b", low): flags.add("us")
    geo = sorted({a for a, _ in re.findall(r"(\d{2,3})\s*%[^.\n]{0,60}(us|usa|u\.s|tier|united states|america|uk|london|countr)", low)})
    if re.search(r"france|french|español|spanish|latam|brazil|portugu|deutsch|german|philippin|indonesia|netherlands|dutch|\bph/|italia|japan|arabic", low): flags.add("non_en")
    if re.search(r"\bugc\b", low): flags.add("ugc")
    if re.search(r"clipping|clips? from|clip ", low): flags.add("clip")
    if "podcast" in low: flags.add("podcast")
    cats = ("Podcasts", "Relationships & Dating", "Entertainment", "Gaming", "Music", "Personal brand", "Finance", "Tech", "Sports", "Lifestyle",
            "Education", "Comedy", "Business", "Beauty", "Fashion", "Health & Wellness", "Health & Fitness", "Food", "Crypto", "Travel", "Other")
    cat = next((l for l in lines[b:b + 12] if l in cats), "")
    return dict(org=lines[b + 1], title=lines[b + 2], paid=paid, budget=bud, cat=cat, flags=flags, geo=",".join(geo) + "%" if geo else "",
                plats=[(p, k, float(v.replace(",", ""))) for p, k, v in plats],
                maxp=float(maxp[0].replace(",", "")) if maxp else None, minp=float(minp[0].replace(",", "")) if minp else None)

GAMB = re.compile(r"casino|gambl|\bbet\b|betting|roobet|stake|shuffle|duel|metawin|blackjack|poker|picklebet|fliff|sportsbook", re.I)
REGION = re.compile(r"\[(FRANCE|GERMANY|NORDICS|UK|SPAIN|BRAZIL|LATAM|ITALY|NL|PH|INDONESIA|JAPAN)\]|france|fran.ais|brazil|philippines|latam|espa.ol|hablando|por cada|vues|deutsch|arabic|\(PH/|SEA \(", re.I)

def build():
    L = json.load(open(os.path.join(WORK, "list.json"), encoding="utf-8"))
    D = {}
    for f in glob.glob(os.path.join(WORK, "details", "*.txt")):
        d = parse_detail(open(f, encoding="utf-8", errors="replace").read())
        if d: D[os.path.basename(f)[:-4]] = d
    fs_path = os.path.join(ROOT, "data", "first_seen.json")
    first_seen = json.load(open(fs_path)) if os.path.exists(fs_path) else {}
    # snapshot from ~24 h ago (closest one at least 20 h old) for spend-per-day
    old = None
    for f in sorted(glob.glob(os.path.join(HIST, "*.json")), reverse=True):
        ts = datetime.datetime.strptime(os.path.basename(f)[:-5], "%Y-%m-%dT%H%MZ").replace(tzinfo=datetime.timezone.utc)
        if (NOW - ts).total_seconds() >= 20 * 3600:
            old = (ts, {r[0]: r for r in json.load(open(f))}); break
    rows, snap = [], []
    for c in L:
        cid = c["href"].split("/")[-1]
        p, d = parse_card(c["text"]), D.get(cid)
        if not p and not d: continue
        org = (p or d)["org"]; title = (p or d)["title"]
        paid = p["paid"] if p else d["paid"] or 0; budget = p["budget"] if p else d["budget"] or 0
        creators = p["creators"] if p else 0
        plats = {x[0]: x for x in (d["plats"] if d else [])}
        rate = p["rate"] if p else max([x[2] for x in plats.values() if x[1] == "1K views"] or [0])
        r1 = lambda n: plats[n][2] if n in plats and plats[n][1] == "1K views" else None
        flags = d["flags"] if d else set(); txt = f"{title} {org}"
        kind = "UGC" if ("ugc" in flags or re.search(r"\bUGC\b", txt)) and "clip" not in flags else ("Slideshow" if re.search("slideshow", txt, re.I) else "Clipping")
        left = max(budget - paid, 0)
        # first time we see a campaign: date it by its launch age when the card shows one
        first_seen.setdefault(cid, (NOW - datetime.timedelta(days=p["age_days"])).isoformat() if p else NOW.isoformat())
        spent_day = None
        if old and cid in old[1]:
            hours = (NOW - old[0]).total_seconds() / 3600
            spent_day = round(max(paid - old[1][cid][3], 0) * 24 / hours)
        rows.append({
            "id": cid, "campaign": title, "org": org, "category": (d or {}).get("cat") or "Not listed", "type": kind,
            "age": p["age"] if p else "?", "age_days": p["age_days"] if p else None,
            "budget": round(budget), "paid": round(paid), "left": round(left), "spent_pct": round(100 * paid / budget, 1) if budget else None,
            "creators": int(creators), "left_per_creator": round(left / max(creators, 1)), "rate": rate,
            "rate_tiktok": r1("TikTok"), "rate_instagram": r1("Instagram"), "rate_youtube": r1("YouTube"), "rate_x": r1("X"),
            "platforms": ", ".join(plats), "per_post": any(x[1] == "approved post" for x in plats.values()),
            "max_payout": d["maxp"] if d else None, "min_payout": d["minp"] if d else None,
            "gambling": bool(GAMB.search(txt)) or "gambling" in flags, "non_english": bool(REGION.search(txt)) or "non_en" in flags,
            "face": "face" in flags, "podcast": "podcast" in flags or bool(re.search("podcast", txt, re.I)),
            "us_rule": "us" in flags or bool(d and d["geo"]), "geo": d["geo"] if d else "", "detail": bool(d),
            "first_seen": first_seen[cid], "spent_per_day": spent_day,
            "url": "https://contentrewards.com/c/campaigns/" + cid,
        })
        snap.append([cid, round(left), int(creators), round(paid)])
    meta = {"updated": NOW.isoformat(), "count": len(rows), "detail_count": len(D),
            "compared_with": old[0].isoformat() if old else None,
            "source": "contentrewards.com Discover (All campaigns): every card, plus the full page of each campaign with $1.5K+ left"}
    json.dump({"rows": rows, "meta": meta}, open(os.path.join(PUB, "campaigns.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(snap, open(os.path.join(HIST, NOW.strftime("%Y-%m-%dT%H%MZ") + ".json"), "w"), separators=(",", ":"))
    json.dump(first_seen, open(fs_path, "w"), separators=(",", ":"))
    print("build:", len(rows), "campaigns,", len(D), "with detail, compared with", meta["compared_with"])

{"candidates": candidates, "build": build}[sys.argv[1]]()
