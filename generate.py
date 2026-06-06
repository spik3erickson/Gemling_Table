"""Generate README.md (grouped, scannable table of every PoE2 skill gem
quality effect) from gemling_quality.json.

Reads:  gemling_quality.json
Writes: README.md
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "gemling_quality.json"
DST = HERE / "README.md"


# Skill names that override pure tag-based categorization
NAME_OVERRIDES: dict[str, str] = {
    # Meta / triggered gems
    "Cast on Critical": "meta",
    "Cast on Elemental Ailment": "meta",
    "Cast on Minion Death": "meta",
    "Cast on Freeze": "meta",
    "Cast on Ignite": "meta",
    "Cast on Shock": "meta",
    "Mirage Archer": "meta",
    "Spellslinger": "meta",
    # Heralds
    "Herald of Ash": "herald",
    "Herald of Thunder": "herald",
    "Herald of Plague": "herald",
    # Marks
    "Bloodhound's Mark": "mark",
    "Sniper's Mark": "mark",
    "Voltaic Mark": "mark",
    # Curses
    "Despair": "curse",
    "Enfeeble": "curse",
    "Vulnerability": "curse",
    "Conductivity": "curse",
    "Elemental Weakness": "curse",
    "Flammability": "curse",
    "Hypothermia": "curse",
    "Temporal Chains": "curse",
    "Blasphemy": "curse",
    # Warcries
    "Ancestral Cry": "warcry",
    "Infernal Cry": "warcry",
    "Seismic Cry": "warcry",
    "Fortifying Cry": "warcry",
    # Auras / Persistents / Presences
    "Withering Presence": "aura",
    "Overwhelming Presence": "aura",
    "Pain Offering": "aura",
    "Bone Offering": "aura",
    "Soul Offering": "aura",
    "Arctic Armour": "aura",
    "Eternal Rage": "aura",
    "Mana Remnants": "aura",
    "Time of Need": "aura",
    "Discipline": "aura",
    "Impurity": "aura",
    "Malice": "aura",
    "Purity of Fire": "aura",
    "Purity of Ice": "aura",
    "Purity of Lightning": "aura",
    "Sigil of Power": "aura",
    "Grim Feast": "aura",
    "Siphon Elements": "aura",
    "Alchemist's Boon": "aura",
    "Plague Bearer": "aura",
    "Magma Barrier": "aura",
    "Berserk": "aura",
    "Combat Frenzy": "aura",
    "Cull The Weak": "aura",
    "Scavenged Plating": "aura",
    "Iron Ward": "aura",
    "Resonating Shield": "aura",
    "Shield Wall": "aura",
    # Totems
    "Shockwave Totem": "totem",
    "Dark Effigy": "totem",
    "Ancestral Warrior Totem": "totem",
    "Frost Bomb": "totem",
    "Frost Wall": "totem",
    # Minions / Summons
    "Raise Zombie": "minion",
    "Raging Spirits": "minion",
    "Raven Flock": "minion",
    "Skeletal Arsonist": "minion",
    "Skeletal Brute": "minion",
    "Skeletal Cleric": "minion",
    "Skeletal Frost Mage": "minion",
    "Skeletal Reaver": "minion",
    "Skeletal Sniper": "minion",
    "Skeletal Storm Mage": "minion",
    "Skeletal Warrior": "minion",
    "Bind Spectre": "minion",
    "Sacrifice": "minion",
    "Tame Beast": "minion",
    "Ravenous Swarm": "minion",
    "Feast of Flesh": "minion",
    "Spiraling Conspiracy": "minion",
    # Movement
    "Blink": "movement",
    "Shield Charge": "movement",
    "Leap Slam": "movement",
    "Thunderous Leap": "movement",
    "Lightning Warp": "movement",
    "Rhoa Mount": "movement",
    "Disengage": "movement",
}


CATEGORY_ORDER = [
    ("meta", "Meta & Triggered Skills",
        "Cast-on triggers and meta gems. Quality often affects reservation cost or trigger frequency."),
    ("curse", "Curses",
        "Hexes you cast onto enemies. Several curses share the same `(0—50)% reduced Mana Cost` quality bonus."),
    ("mark", "Marks",
        "Single-target marks. Quality affects cost or reapplication."),
    ("herald", "Heralds",
        "Persistent reservation buffs that empower a specific damage type."),
    ("warcry", "Warcries",
        "Shout effects that buff you or debuff enemies in an area."),
    ("aura", "Auras, Presences & Persistent Buffs",
        "Persistent reservation skills (auras, presences, offerings, body buffs)."),
    ("totem", "Totems & Placed Objects",
        "Stationary helpers. Several gems add to the totem limit."),
    ("minion", "Minions & Summons",
        "Summoned units. Quality often adds minion-wide damage/life/AS."),
    ("movement", "Movement Skills",
        "Mobility and traversal."),
    ("spell", "Spell Skills",
        "Direct-cast spells (projectiles, novas, walls, etc.)."),
    ("attack", "Attack Skills",
        "Weapon-based attacks: slams, strikes, bow and spear skills."),
    ("other", "Other",
        "Anything that didn't fit elsewhere."),
]

CATEGORY_INDEX = {key: i for i, (key, _, _) in enumerate(CATEGORY_ORDER)}


def classify(gem: dict) -> str:
    name = gem["name"]
    if name in NAME_OVERRIDES:
        return NAME_OVERRIDES[name]

    tags = set()
    for sec in gem.get("sections") or []:
        for blk in sec.get("blocks") or []:
            for t in blk.get("tags") or []:
                tags.add(t)

    if "Curse" in tags:
        return "curse"
    if "Mark" in tags:
        return "mark"
    if "Herald" in tags:
        return "herald"
    if "Warcry" in tags:
        return "warcry"
    if "Trigger" in tags or "Meta" in tags:
        return "meta"
    if "Totem" in tags:
        return "totem"
    if "Minion" in tags or "Companion" in tags:
        return "minion"
    if "Aura" in tags or "Buff" in tags or "Persistent" in tags:
        return "aura"
    if "Travel" in tags:
        return "movement"
    if "Spell" in tags:
        return "spell"
    if "Attack" in tags or "Melee" in tags or "Slam" in tags or "Strike" in tags:
        return "attack"
    if "Projectile" in tags:
        # Bow/spear projectiles usually attack-tagged; if we got here without an
        # attack tag, treat as spell projectile.
        return "spell"
    # Fallback: any damage-element-tagged gem that isn't an attack is a spell.
    if tags & {"Fire", "Cold", "Lightning", "Chaos", "Physical"}:
        return "spell"
    return "other"


# ── Quality math helpers ─────────────────────────────────────────────────────

# Pull the (0—N) range from a gemling string so we can compute a quality
# scaling cheat-sheet number. We grab the LAST numeric range in the string —
# that's usually the headline value.
RANGE = re.compile(r"\((?P<lo>-?\d+(?:\.\d+)?)—(?P<hi>-?\d+(?:\.\d+)?)\)")


def scale_at(text: str | None, quality_pct: int) -> str:
    """Return a short '@ N% quality' string for the FIRST range in `text`."""
    if not text:
        return "—"
    m = RANGE.search(text)
    if not m:
        return "—"
    lo, hi = float(m.group("lo")), float(m.group("hi"))
    # Default in-game cap is 20% quality. Scale linearly past that.
    scaled = lo + (hi - lo) * (quality_pct / 20.0)
    # Format: integer if it round-trips cleanly
    if scaled.is_integer():
        out = str(int(scaled))
    else:
        out = f"{scaled:.2f}".rstrip("0").rstrip(".")
    return out


def md_escape(s: str | None) -> str:
    if not s:
        return "—"
    return s.replace("|", "\\|").replace("\n", " ").strip()


def link(name: str, url: str) -> str:
    return f"[{md_escape(name)}]({url})"


# ── Page builders ────────────────────────────────────────────────────────────

def render_quality_cheatsheet() -> list[str]:
    return [
        "## How quality scales",
        "",
        "Every quality effect on a skill gem is shown as a range like `(0—N)`. "
        "`N` is the value at the standard **20% quality** cap; scaling is linear. "
        "Use this rule of thumb:",
        "",
        "| Listed range | @ 10% q | @ 20% q | @ 30% q | @ 40% q | @ 50% q |",
        "|---|---:|---:|---:|---:|---:|",
        "| `(0—10)` | 5 | 10 | 15 | 20 | 25 |",
        "| `(0—20)` | 10 | 20 | 30 | 40 | 50 |",
        "| `(0—30)` | 15 | 30 | 45 | 60 | 75 |",
        "| `(0—40)` | 20 | 40 | 60 | 80 | 100 |",
        "| `(0—50)` | 25 | 50 | 75 | 100 | 125 |",
        "| `(0—100)` | 50 | 100 | 150 | 200 | 250 |",
        "",
        "Effects expressed as a **chance** clamp at 100%. Negative-range effects "
        "(e.g. `(-1—0)` seconds) reduce a value linearly toward zero.",
        "",
    ]


def render_category(
    key: str, title: str, blurb: str, gems: list[dict]
) -> list[str]:
    out: list[str] = []
    out.append(f"## {title}")
    out.append("")
    out.append(f"_{blurb}_  ({len(gems)} gems)")
    out.append("")
    out.append("| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |")
    out.append("|---|---|---|---|")
    for g in sorted(gems, key=lambda x: x["name"].lower()):
        gemling = g.get("gemling_effect") or "—"
        generic = g.get("generic_quality_mod") or "—"
        # Show the 30%-quality scaled value for whichever line is present
        primary = g.get("gemling_effect") or g.get("generic_quality_mod")
        scaled = scale_at(primary, 30)
        out.append(
            f"| {link(g['name'], g['url'])} | {md_escape(gemling)} "
            f"| {md_escape(generic)} | {scaled} |"
        )
    out.append("")
    return out


def render_no_gemling(gems: list[dict]) -> list[str]:
    out: list[str] = []
    out.append(f"## Gems with no gemling line ({len(gems)})")
    out.append("")
    out.append(
        "These gems only display the generic `qualityMod` line. There is no "
        "lighter-blue `secondaryQualityMod` (gemling) on these pages — what "
        "you see is what you get."
    )
    out.append("")
    out.append("| Gem | Generic quality mod | @ 30% q |")
    out.append("|---|---|---|")
    for g in sorted(gems, key=lambda x: x["name"].lower()):
        generic = g.get("generic_quality_mod") or "—"
        scaled = scale_at(generic, 30)
        out.append(f"| {link(g['name'], g['url'])} | {md_escape(generic)} | {scaled} |")
    out.append("")
    return out


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))

    with_gemling = [g for g in data if g.get("gemling_effect")]
    no_gemling = [g for g in data if not g.get("error") and not g.get("gemling_effect")]
    errors = [g for g in data if g.get("error")]

    # Bucket with-gemling gems by category
    by_cat: dict[str, list[dict]] = {key: [] for key, _, _ in CATEGORY_ORDER}
    for g in with_gemling:
        by_cat.setdefault(classify(g), []).append(g)

    lines: list[str] = []
    lines.append("# PoE2 Skill Gem Quality Effects")
    lines.append("")
    lines.append(
        "A complete reference of every skill gem in Path of Exile 2 and its "
        "quality effects, scraped from "
        "[poe2db.tw](https://poe2db.tw/us/Skill_Gems). "
        f"**{len(data)}** gems total · **{len(with_gemling)}** with a gemling line · "
        f"**{len(no_gemling)}** without."
    )
    lines.append("")
    lines.append(
        "Each gem can show two lines under *Additional Effects From Quality:* — "
        "a generic line and a brighter **gemling** line (the gem-specific bonus). "
        "Both are listed here, side by side."
    )
    lines.append("")

    # TOC
    lines.append("## Contents")
    lines.append("")
    for key, title, _ in CATEGORY_ORDER:
        n = len(by_cat.get(key, []))
        if n == 0:
            continue
        slug = title.lower().replace(" & ", "--").replace(" ", "-").replace(",", "")
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        lines.append(f"- [{title}](#{slug}) ({n})")
    if no_gemling:
        lines.append(f"- [Gems with no gemling line](#gems-with-no-gemling-line-{len(no_gemling)}) ({len(no_gemling)})")
    lines.append("- [How quality scales](#how-quality-scales)")
    lines.append("")

    lines.extend(render_quality_cheatsheet())

    for key, title, blurb in CATEGORY_ORDER:
        gems = by_cat.get(key, [])
        if not gems:
            continue
        lines.extend(render_category(key, title, blurb, gems))

    if no_gemling:
        lines.extend(render_no_gemling(no_gemling))

    if errors:
        lines.append(f"## Errors ({len(errors)})")
        lines.append("")
        lines.append("Pages that failed to scrape. These are usually templated/placeholder URLs on the source.")
        lines.append("")
        lines.append("| Listed name | URL | Error |")
        lines.append("|---|---|---|")
        for g in errors:
            lines.append(
                f"| {md_escape(g['name'])} | <{g['url']}> | {md_escape(g['error'])} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "_Data sourced from [poe2db.tw](https://poe2db.tw/us/Skill_Gems). "
        "Numbers are accurate as of the most recent scrape; gem balance changes "
        "with patches. Submit a PR or open an issue if anything's stale._"
    )
    lines.append("")

    DST.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {DST} ({DST.stat().st_size:,} bytes, {len(lines)} lines)")


if __name__ == "__main__":
    main()
