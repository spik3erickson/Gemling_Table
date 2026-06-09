"""Build the PoE2 v0.5 gemling-quality reference from poe2db's Advanced Thaumaturgy page.

The Gemling Legionnaire ascendancy notable *Advanced Thaumaturgy* ("Gem Quality
grants Socketed Skills an additional effect") lists, in one page, the secondary
quality (gemling) effect for every skill gem in the game. That single page is the
authoritative v0.5 source for the gemling column — far better than scraping ~190
individual gem pages.

This script:
  1. downloads (or reuses) the Advanced Thaumaturgy page,
  2. parses all skill rows -> name, url, attribute colour, gemling effect,
  3. backfills the *generic* quality mod by name from the prior per-gem scrape
     (gemling_quality.json) — null where unknown / new in 0.5,
  4. writes gemling_quality_0_5.json, gemling_quality.md, gemling_quality.html.

Usage:  python3 build_gemling_v0_5.py
Deps:   requests (or curl fallback), beautifulsoup4
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).parent
SRC_URL = "https://poe2db.tw/us/Advanced_Thaumaturgy"
CACHE = HERE / "_adv_thaum_v0_5.html"
OLD_JSON = HERE / "gemling_quality.json"          # prior per-gem scrape (for generic mods)
OUT_JSON = HERE / "gemling_quality_0_5.json"
OUT_MD = HERE / "gemling_quality.md"
OUT_HTML = HERE / "gemling_quality.html"

COLOUR_ATTR = {"gem_red": "str", "gem_green": "dex", "gem_blue": "int"}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def fetch_html() -> str:
    if CACHE.exists():
        return CACHE.read_text(encoding="utf-8")
    # curl keeps the dependency surface tiny and handles brotli/gzip cleanly
    html = subprocess.check_output(
        ["curl", "-s", "-A", UA, "--compressed", SRC_URL], text=True
    )
    CACHE.write_text(html, encoding="utf-8")
    return html


def parse_skills(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict] = []
    for blk in soup.select("div.d-flex.border-top.rounded"):
        sec = blk.select_one("div.secondaryQualityMod")
        if not sec:
            continue
        # The name anchor is the /us/ link with no <img> child (the img one is the icon).
        name_a = next(
            (a for a in blk.select('a[href^="/us/"]')
             if a.find("img") is None and a.get_text(strip=True)),
            None,
        )
        if not name_a:
            continue
        colour = next((c for c in (name_a.get("class") or []) if c.startswith("gem_")), "")
        for br in sec.find_all("br"):
            br.replace_with("  ·  ")
        txt = re.sub(r"\s+", " ", sec.get_text(" ", strip=True)).strip()
        txt = re.sub(r"\(\s*0\s*—\s*", "(0—", txt)
        txt = re.sub(r"\)\s+%", ")%", txt)
        txt = re.sub(r"(\d)\s+%", r"\1%", txt)
        txt = re.sub(r"\s+·\s+", "  ·  ", txt)
        rows.append({
            "name": name_a.get_text(strip=True),
            "url": "https://poe2db.tw" + name_a["href"],
            "attribute": COLOUR_ATTR.get(colour, "?"),
            "gemling_effect": txt,
        })
    # de-dup, keep first occurrence
    seen: set[str] = set()
    return [r for r in rows if not (r["name"] in seen or seen.add(r["name"]))]


def disp(name: str) -> str:
    return name.replace(": {0}", "")


def build() -> None:
    skills = parse_skills(fetch_html())
    old_generic = {e["name"]: e.get("generic_quality_mod") for e in json.loads(OLD_JSON.read_text())} \
        if OLD_JSON.exists() else {}
    for s in skills:
        s["generic_quality_mod"] = old_generic.get(s["name"])
        s["new_in_0_5"] = s["name"] not in old_generic
    skills.sort(key=lambda r: r["name"].lower())

    OUT_JSON.write_text(json.dumps({
        "version": "0.5",
        "source": SRC_URL,
        "note": ("Gemling effect = the secondaryQualityMod (Gemling Legionnaire ascendancy: "
                 "\"Gem Quality grants Socketed Skills an additional effect\"). Generic quality "
                 "mod backfilled by name from the prior per-gem scrape; null where unknown / new in 0.5."),
        "count": len(skills),
        "skills": skills,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    n_new = sum(1 for s in skills if s["new_in_0_5"])
    md = [
        "# PoE2 v0.5 — Skill Gem Gemling Quality Effects\n",
        f"Source: <{SRC_URL}> — the **Gemling Legionnaire** ascendancy notable *Advanced "
        "Thaumaturgy* (\"Gem Quality grants Socketed Skills an additional effect\"). Lists, for "
        "every skill, the **gemling effect**: the `secondaryQualityMod` line a Gemling Legionnaire "
        "unlocks from gem quality.\n",
        f"**{len(skills)}** skills · **{n_new}** new in 0.5 · **{len(skills)-n_new}** carried over · "
        f"generic quality mod backfilled for **{sum(1 for s in skills if s['generic_quality_mod'])}** by name.\n",
        "> *Gemling effect* = the bonus a Gemling Legionnaire gets from gem quality. *Generic "
        "quality mod* = the standard bonus every other class gets (backfilled; blank = unknown / new in 0.5).\n",
        "| # | Gem | Attr | Gemling effect (Gemling Legionnaire) | Generic quality mod | New 0.5 |",
        "|---:|---|---|---|---|:---:|",
    ]
    for i, s in enumerate(skills, 1):
        md.append(f"| {i} | [{disp(s['name'])}]({s['url']}) | {s['attribute'].upper()} | "
                  f"{s['gemling_effect']} | {s['generic_quality_mod'] or '—'} | "
                  f"{'🆕' if s['new_in_0_5'] else ''} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    render_html(skills, n_new)
    print(f"{len(skills)} skills · {n_new} new in 0.5 -> "
          f"{OUT_JSON.name}, {OUT_MD.name}, {OUT_HTML.name}")


def render_html(skills: list[dict], n_new: int) -> None:
    rows = json.dumps([{
        "n": disp(s["name"]), "u": s["url"], "a": s["attribute"],
        "g": s["gemling_effect"], "q": s["generic_quality_mod"] or "", "new": s["new_in_0_5"],
    } for s in skills])
    OUT_HTML.write_text(_HTML_TEMPLATE.replace("/*DATA*/", rows)
                        .replace("{COUNT}", str(len(skills)))
                        .replace("{SRC}", SRC_URL), encoding="utf-8")


_HTML_TEMPLATE = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>PoE2 0.5 — Gemling Quality Effects</title>
<style>
:root{--bg:#0e0f13;--card:#171922;--line:#262a36;--txt:#e6e8ef;--mut:#9aa0b4;--int:#5b9cff;--dex:#3fbf6f;--str:#e0564f;--acc:#c9a227}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
header{padding:20px 24px;border-bottom:1px solid var(--line)}h1{margin:0 0 4px;font-size:20px}
.sub{color:var(--mut);font-size:13px}.sub a{color:var(--acc)}
.bar{position:sticky;top:0;background:var(--bg);padding:12px 24px;border-bottom:1px solid var(--line);display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:5}
input,select{background:var(--card);border:1px solid var(--line);color:var(--txt);padding:8px 10px;border-radius:8px;font-size:13px}
input{flex:1;min-width:220px}.count{color:var(--mut);font-size:12px;margin-left:auto}
table{width:100%;border-collapse:collapse}th,td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{position:sticky;top:57px;background:var(--card);font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
tr:hover td{background:#12141c}a.gem{color:var(--txt);text-decoration:none;font-weight:600}a.gem:hover{color:var(--acc)}
.str{color:var(--str)}.dex{color:var(--dex)}.int{color:var(--int)}
.new{color:#0e0f13;background:var(--acc);font-weight:700;padding:1px 6px;border-radius:5px;font-size:11px}
.g{max-width:42ch}.q{max-width:36ch;color:var(--mut)}td.idx{color:var(--mut);text-align:right}
</style></head><body>
<header><h1>Path of Exile 2 — v0.5 Gemling Quality Effects</h1>
<div class=sub>Gemling Legionnaire bonus per skill · source: <a href="{SRC}" target=_blank>poe2db Advanced Thaumaturgy</a> · {COUNT} skills</div></header>
<div class=bar>
<input id=q placeholder="Search skill or effect…">
<select id=attr><option value="">All attributes</option><option value=str>STR (red)</option><option value=dex>DEX (green)</option><option value=int>INT (blue)</option></select>
<select id=nw><option value="">All</option><option value=1>New in 0.5</option><option value=0>Carried over</option></select>
<span class=count id=cnt></span></div>
<table><thead><tr><th>#</th><th>Gem</th><th>Attr</th><th>Gemling effect</th><th>Generic quality mod</th></tr></thead><tbody id=tb></tbody></table>
<script>
const D=/*DATA*/;const tb=document.getElementById('tb'),cnt=document.getElementById('cnt');
const q=document.getElementById('q'),fa=document.getElementById('attr'),fn=document.getElementById('nw');
const AL={str:'STR',dex:'DEX',int:'INT','?':'—'};
function render(){
 const s=q.value.toLowerCase(),a=fa.value,nw=fn.value;let i=0,h='';
 for(const r of D){
  if(a&&r.a!==a)continue; if(nw!==''&&String(r.new?1:0)!==nw)continue;
  if(s&&!(r.n.toLowerCase().includes(s)||r.g.toLowerCase().includes(s)||r.q.toLowerCase().includes(s)))continue;
  i++;h+=`<tr><td class=idx>${i}</td><td><a class=gem href="${r.u}" target=_blank>${r.n}</a> ${r.new?'<span class=new>0.5</span>':''}</td>`+
       `<td class="${r.a}">${AL[r.a]}</td><td class=g>${r.g}</td><td class=q>${r.q||'—'}</td></tr>`;
 }
 tb.innerHTML=h;cnt.textContent=i+' / '+D.length+' skills';
}
[q,fa,fn].forEach(e=>e.addEventListener('input',render));render();
</script></body></html>"""


if __name__ == "__main__":
    build()
