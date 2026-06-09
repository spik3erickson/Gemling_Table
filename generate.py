"""Generate README.md — a grouped, scannable table of every PoE2 v0.5 skill gem
quality effect (the Gemling Legionnaire gemling line + the generic quality line).

Categorisation is driven by the real Path-of-Building gem tags/types in
data/skill_gems.json — no hand-maintained override list.

Reads:  data/gemling_quality.json   (gemling effects, per skill, v0.5)
        data/skill_gems.json        (PoB tags + gemType, for categorisation)
Writes: README.md
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
GEMLING = HERE / "data" / "gemling_quality.json"
CATALOG = HERE / "data" / "skill_gems.json"
DST = HERE / "README.md"

CATEGORY_ORDER = [
    ("meta", "Meta & Triggered Skills",
        "Cast-on triggers and meta gems. Quality often affects reservation cost or trigger frequency."),
    ("curse", "Curses",
        "Hexes you cast onto enemies. Several curses share a `(0—50)% faster Curse Activation` gemling bonus."),
    ("mark", "Marks", "Single-target marks. Quality affects cost or reapplication."),
    ("herald", "Heralds", "Persistent reservation buffs that empower a specific damage type."),
    ("warcry", "Warcries", "Shout effects that buff you or debuff enemies in an area."),
    ("aura", "Auras, Presences & Persistent Buffs",
        "Persistent reservation skills (auras, presences, offerings, body buffs)."),
    ("totem", "Totems & Placed Objects", "Stationary helpers. Several gems add to the totem limit."),
    ("minion", "Minions & Summons", "Summoned units. Quality often adds minion-wide damage/life/AS."),
    ("movement", "Movement Skills", "Mobility and traversal."),
    ("spell", "Spell Skills", "Direct-cast spells (projectiles, novas, walls, etc.)."),
    ("attack", "Attack Skills", "Weapon-based attacks: slams, strikes, bow, crossbow and spear skills."),
    ("other", "Other", "Anything that didn't fit elsewhere."),
]


def load_catalog_tags() -> dict:
    """name -> {gemType, tags(set)} from the PoB-derived catalog."""
    out = {}
    for g in json.loads(CATALOG.read_text(encoding="utf-8")):
        tags = {k for k, v in (g.get("tags") or {}).items() if v}
        out[g["name"]] = {"gemType": g.get("gemType"), "tags": tags}
    return out


def classify(name: str, cat: dict) -> str:
    info = cat.get(name)
    if not info:
        return "other"
    gt = (info["gemType"] or "").lower()
    t = info["tags"]
    if gt == "meta" or "meta" in t or "trigger" in t:
        return "meta"
    if "curse" in t:
        return "curse"
    if gt == "mark" or "mark" in t:
        return "mark"
    if "herald" in t:
        return "herald"
    if gt == "warcry" or "warcry" in t:
        return "warcry"
    if gt == "totem" or "totem" in t:
        return "totem"
    if gt == "minion" or "minion" in t or "companion" in t:
        return "minion"
    if "travel" in t or "movement" in t or "blink" in t:
        return "movement"
    if gt in ("buff", "banner", "shapeshift") or "aura" in t or "persistent" in t or "herald" in t:
        return "aura"
    if gt == "spell" or "spell" in t:
        return "spell"
    if gt in ("attack", "channelling") or t & {"attack", "melee", "slam", "strike", "bow", "crossbow", "spear"}:
        return "attack"
    if "projectile" in t:
        return "spell"
    if t & {"fire", "cold", "lightning", "chaos", "physical"}:
        return "spell"
    return "other"


# ── quality scaling helper ──────────────────────────────────────────────────
RANGE = re.compile(r"\((?P<lo>-?\d+(?:\.\d+)?)—(?P<hi>-?\d+(?:\.\d+)?)\)")


def scale_at(text, quality_pct: int) -> str:
    if not text:
        return "—"
    m = RANGE.search(text)
    if not m:
        return "—"
    lo, hi = float(m.group("lo")), float(m.group("hi"))
    scaled = lo + (hi - lo) * (quality_pct / 20.0)
    return str(int(scaled)) if scaled.is_integer() else f"{scaled:.2f}".rstrip("0").rstrip(".")


def esc(s) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip() if s else "—"


ATTR = {"str": "🔴 STR", "dex": "🟢 DEX", "int": "🔵 INT", "?": "—"}


def main() -> None:
    data = json.loads(GEMLING.read_text(encoding="utf-8"))
    skills = data["skills"]
    cat = load_catalog_tags()

    by = {k: [] for k, _, _ in CATEGORY_ORDER}
    for s in skills:
        by.setdefault(classify(s["name"], cat), []).append(s)

    n_new = sum(1 for s in skills if s.get("new_in_0_5"))
    L = []
    L += [
        "# PoE2 v0.5 — Skill Gem Gemling Quality Effects",
        "",
        f"The **gemling effect** every skill gem gains under a Gemling Legionnaire's "
        f"*Advanced Thaumaturgy* (\"Gem Quality grants Socketed Skills an additional effect\"), "
        f"alongside the generic quality bonus every other class gets. "
        f"Source: [poe2db Advanced Thaumaturgy]({data['source']}).",
        "",
        f"**{len(skills)}** skills · **{n_new}** new in 0.5 · grouped by type from "
        f"Path-of-Building gem tags.",
        "",
        "> This repo also ships a full machine-readable **gem catalog** with "
        "support↔skill compatibility — see [What else is here](#what-else-is-in-this-repo).",
        "",
    ]

    # TOC
    L += ["## Contents", ""]
    for key, title, _ in CATEGORY_ORDER:
        n = len(by.get(key, []))
        if not n:
            continue
        slug = re.sub(r"[^a-z0-9\-]", "", title.lower().replace(" & ", "--").replace(" ", "-").replace(",", ""))
        L.append(f"- [{title}](#{slug}) ({n})")
    L += ["- [How quality scales](#how-quality-scales)",
          "- [What else is in this repo](#what-else-is-in-this-repo)", ""]

    # scaling cheatsheet
    L += [
        "## How quality scales", "",
        "Quality effects show as a range `(0—N)`; `N` is the value at the standard **20% quality** "
        "cap and scaling is linear (a Gemling Legionnaire pushes quality far past 20%):", "",
        "| Listed range | @ 20% q | @ 30% q | @ 40% q | @ 50% q |",
        "|---|---:|---:|---:|---:|",
        "| `(0—10)` | 10 | 15 | 20 | 25 |",
        "| `(0—20)` | 20 | 30 | 40 | 50 |",
        "| `(0—30)` | 30 | 45 | 60 | 75 |",
        "| `(0—40)` | 40 | 60 | 80 | 100 |",
        "| `(0—50)` | 50 | 75 | 100 | 125 |",
        "",
        "Chance-based effects clamp at 100%. Negative ranges (e.g. `(-1—0)`) reduce toward zero.",
        "",
    ]

    for key, title, blurb in CATEGORY_ORDER:
        gems = by.get(key, [])
        if not gems:
            continue
        L += [f"## {title}", "", f"_{blurb}_  ({len(gems)} gems)", "",
              "| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |",
              "|---|---|---|---|---|:---:|"]
        for g in sorted(gems, key=lambda x: x["name"].lower()):
            primary = g.get("gemling_effect") or g.get("generic_quality_mod")
            disp = g["name"].replace(": {0}", "")
            L.append(f"| [{esc(disp)}]({g['url']}) | {ATTR.get(g['attribute'],'—')} | "
                     f"{esc(g.get('gemling_effect'))} | {esc(g.get('generic_quality_mod'))} | "
                     f"{scale_at(primary,30)} | {'🆕' if g.get('new_in_0_5') else ''} |")
        L.append("")

    L += [
        "## What else is in this repo", "",
        "A normalized **PoE2 v0.5 gem catalog** built from the "
        "[Path of Building data export](https://github.com/repoe-fork/pob-data) — the backend for an "
        "AI-assisted build creator:", "",
        "| File | What |",
        "|---|---|",
        "| `data/gemling_quality.json` | The 260-skill gemling table above, machine-readable |",
        "| `data/skill_gems.json` | 399 active gems — tags, attribute, skill types, descriptions |",
        "| `data/support_gems.json` | 571 support gems (538 PoB + 33 Lineage/external-granted) with rules |",
        "| `data/support_compatibility.json` | Which supports work with which skills (both directions) |",
        "| `data/spirit_gems.json`, `data/meta_gems.json` | Spirit / meta gem subsets |",
        "| `data/uniques.json` | 395 unique items across every slot, with mods |",
        "| `data/bases.json` | 1,715 base item types (weapon/armour/jewellery) with stats + requirements |",
        "| `data/runes.json` | 283 runes / soul cores with their item-type-dependent mods |",
        "| `data/jewels.json` | Jewel bases, uniques, cluster + timeless data |",
        "| `pages/gemling_quality.html`, `pages/gem_catalog.html`, `pages/items_catalog.html` | Searchable static browsers |",
        "| `data/CATALOG_SCHEMA.md` | Field schema + compatibility algorithm |",
        "",
        "Together (gems + supports + compatibility + uniques + bases + runes + jewels) this is the "
        "full ingredient list for an optimizer that takes the gear you already have and generates a build.",
        "",
        "Rebuild everything:", "",
        "```bash",
        "python3 scripts/build_gemling.py    # gemling table from poe2db Advanced Thaumaturgy",
        "python3 scripts/build_catalog.py    # gem catalog from PoB data export",
        "python3 generate.py                 # this README",
        "```",
        "",
        "---",
        "",
        "_Gemling data from [poe2db.tw](https://poe2db.tw/us/Advanced_Thaumaturgy); catalog from the "
        "[PoB community data export](https://github.com/repoe-fork/pob-data). Numbers reflect PoE2 "
        "v0.5 and change with patches — open an issue/PR if anything's stale._",
        "",
    ]

    DST.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {DST} ({DST.stat().st_size:,} bytes, {len(L)} lines) — "
          f"{len(skills)} skills across {sum(1 for k in by if by[k])} categories")


if __name__ == "__main__":
    main()
