#!/usr/bin/env python3
"""
build_weapon_skills.py -- PoE2 active skill -> allowed weapon types

Downloads PoB community data (repoe-fork/pob-data poe2/) plus the SkillType
enum from PathOfBuildingCommunity/PathOfBuilding-PoE2 dev branch, then
produces data/weapon_skills.json:

  { version, source, generated_at, skills: { name: { weapons, requiresWeapon,
    requiresShield, notes } } }

Spells with no weapon restriction -> weapons:[] + requiresWeapon:false
Attack skills -> specific weapon slots they allow

Usage:
    python3 scripts/build_weapon_skills.py [--skip-download]
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
RAW_DIR = REPO_ROOT / "data" / "_raw"
DATA_DIR = REPO_ROOT / "data"

BASE_URL = "https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2"
GLOBAL_LUA_URL = (
    "https://raw.githubusercontent.com/"
    "PathOfBuildingCommunity/PathOfBuilding-PoE2/dev/src/Data/Global.lua"
)

SKILL_FILES = ["act_dex", "act_int", "act_str", "minion", "other"]

# PoB weaponTypes strings -> our canonical slot names
WEAPON_TYPE_MAP: dict[str, str] = {
    "Bow": "bow",
    "Crossbow": "crossbow",
    "Spear": "spear",
    "Staff": "staff",
    "One Hand Mace": "mace",
    "Two Hand Mace": "mace",
    "Flail": "flail",
    "One Hand Sword": "sword",
    "Two Hand Sword": "sword",
    "One Hand Axe": "axe",
    "Two Hand Axe": "axe",
    "Dagger": "dagger",
    "Claw": "claw",
    "Talisman": "talisman",
    # "None" and the full-set list are handled separately
}

# PoB skillType numeric ids that imply weapon constraints when weaponTypes absent
SKILL_TYPE_REQUIRES_SHIELD = 10    # RequiresShield
SKILL_TYPE_REQUIRES_BUCKLER = 196  # RequiresBuckler
SKILL_TYPE_NON_WEAPON_ATTACK = 166 # NonWeaponAttack (unarmed / flask)
SKILL_TYPE_CROSSBOW = 116          # CrossbowSkill
SKILL_TYPE_CROSSBOW_AMMO = 117     # CrossbowAmmoSkill
SKILL_TYPE_BOW = 184               # Bow
SKILL_TYPE_SPEAR = 191             # Spear
SKILL_TYPE_MELEE = 20              # Melee
SKILL_TYPE_ATTACK = 1              # Attack

# All 13 real weapon types (non-Talisman, non-None). A skill listing all of
# these has no meaningful restriction for non-shapeshift characters.
_REAL_WEAPON_TYPES = frozenset(
    k for k in WEAPON_TYPE_MAP if k != "Talisman"
)

_UA = "build-weapon-skills/1.0"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class SkillWeapons:
    weapons: list[str] = field(default_factory=list)
    requiresWeapon: bool = False
    requiresShield: bool = False
    notes: str = ""


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------
def _fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
    except OSError as e:
        raise RuntimeError(f"fetch failed: {url}: {e}") from e
    print(f"  fetched {dest.name} ({dest.stat().st_size:,}B)")


def download_all() -> None:
    print("=== Downloading raw data ===")
    _fetch(f"{BASE_URL}/Gems.json", RAW_DIR / "Gems.json")
    for name in SKILL_FILES:
        _fetch(f"{BASE_URL}/Skills/{name}.json", RAW_DIR / "Skills" / f"{name}.json")
    _fetch(GLOBAL_LUA_URL, RAW_DIR / "Global.lua")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(f"ERROR: cannot read {path}: {e}") from e


def load_gems() -> dict[str, dict]:
    """Return {grantedEffectId: gem_record} for all non-Support gems."""
    raw = _load_json(RAW_DIR / "Gems.json")
    result: dict[str, dict] = {}
    for gem in raw.values():
        if gem.get("gemType") == "Support":
            continue
        geid = gem.get("grantedEffectId")
        if geid:
            result[geid] = gem
    return result


def load_skill_effects() -> dict[str, dict]:
    """Return {grantedEffectId: effect_record} merged from all skill files."""
    merged: dict[str, dict] = {}
    for name in SKILL_FILES:
        path = RAW_DIR / "Skills" / f"{name}.json"
        merged.update(_load_json(path))
    return merged


def parse_skill_type_enum(lua_path: Path) -> dict[int, str]:
    """Parse SkillType = { Name = N, ... } from Global.lua into {N: Name}."""
    try:
        text = lua_path.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"ERROR: cannot read {lua_path}: {e}") from e

    id_to_name: dict[int, str] = {}
    in_block = False
    for line in text.splitlines():
        if "SkillType = {" in line:
            in_block = True
            continue
        if in_block:
            if line.strip() == "}":
                break
            m = re.match(r"\s+(\w+)\s*=\s*(\d+)", line)
            if m:
                id_to_name[int(m.group(2))] = m.group(1)
    return id_to_name


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------
def _is_universal_weapon_set(weapon_types: dict[str, Any]) -> bool:
    """True when weaponTypes covers every real weapon (i.e. no restriction).

    A skill is unrestricted if it lists all 13 real weapon types. Talisman and
    None are shapeshift/unarmed markers and do not affect whether a normal
    character can use the skill with any weapon.
    """
    real_keys = frozenset(weapon_types.keys()) - {"Talisman", "None"}
    return real_keys >= _REAL_WEAPON_TYPES


def classify_skill(
    gem: dict,
    effect: dict,
    skill_type_names: dict[int, str],
) -> SkillWeapons:
    """Determine weapon requirements for one active skill."""
    skill_types_raw: dict[str, Any] = effect.get("skillTypes", {})
    skill_type_ids: frozenset[int] = frozenset(int(k) for k in skill_types_raw)
    weapon_types: dict[str, Any] = effect.get("weaponTypes", {})

    result = SkillWeapons()

    # Shield requirement is orthogonal to weapon type
    if SKILL_TYPE_REQUIRES_SHIELD in skill_type_ids or SKILL_TYPE_REQUIRES_BUCKLER in skill_type_ids:
        result.requiresShield = True

    # Universal / empty weaponTypes -> no weapon restriction
    if not weapon_types or _is_universal_weapon_set(weapon_types):
        result.requiresWeapon = False
        result.weapons = []
        return result

    # "None" only (e.g. Concoction skills, unarmed) -> weapon-free attack
    keys = set(weapon_types.keys())
    if keys == {"None"} or keys <= {"None", "Talisman"}:
        result.requiresWeapon = False
        result.weapons = []
        if SKILL_TYPE_NON_WEAPON_ATTACK in skill_type_ids:
            result.notes = "unarmed/flask attack"
        return result

    # Mix of "None"/"Talisman" + specific weapons (e.g. AncestralCry) -> restrict to specifics
    keys.discard("None")
    keys.discard("Talisman")

    # Map to canonical slot names, deduplicate, sort
    slots: set[str] = set()
    unmapped: list[str] = []
    for wt_key in keys:
        if wt_key in WEAPON_TYPE_MAP:
            slots.add(WEAPON_TYPE_MAP[wt_key])
        else:
            unmapped.append(wt_key)

    if unmapped:
        result.notes = f"unmapped weaponTypes: {', '.join(sorted(unmapped))}"

    result.weapons = sorted(slots)
    result.requiresWeapon = bool(slots)
    return result


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------
def build(skip_download: bool) -> None:
    if not skip_download:
        download_all()

    gems = load_gems()
    effects = load_skill_effects()
    skill_type_names = parse_skill_type_enum(RAW_DIR / "Global.lua")

    output_skills: dict[str, dict] = {}
    unclassified: list[tuple[str, str]] = []

    for geid, gem in sorted(gems.items(), key=lambda kv: kv[1].get("name", "")):
        effect = effects.get(geid)
        if effect is None:
            unclassified.append((gem.get("name", geid), f"grantedEffectId {geid!r} absent from all skill files"))
            continue

        sw = classify_skill(gem, effect, skill_type_names)
        name = gem.get("name") or effect.get("name") or geid
        output_skills[name] = asdict(sw)

    # Deduplicate by name: if two gems share a display name keep the one with
    # more information (weapon restriction beats no restriction).
    # (In practice names are unique for active gems, but be safe.)

    result = {
        "version": "0.5",
        "source": "PoB export (repoe-fork/pob-data)",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "skill_count": len(output_skills),
        "skills": output_skills,
    }

    out_path = DATA_DIR / "weapon_skills.json"
    try:
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"ERROR writing {out_path}: {e}") from e
    print(f"\nwrote {out_path.relative_to(REPO_ROOT)} ({out_path.stat().st_size:,}B)")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    skills = output_skills
    total = len(skills)
    with_restriction = sum(1 for s in skills.values() if s["requiresWeapon"])
    spells_any = total - with_restriction
    with_shield = sum(1 for s in skills.values() if s["requiresShield"])

    print(f"\n=== Coverage ===")
    print(f"  total active skills : {total}")
    print(f"  weapon-restricted   : {with_restriction}")
    print(f"  spell/any-weapon    : {spells_any}")
    print(f"  require shield      : {with_shield}")

    print(f"\n=== Spot checks ===")
    _spot(skills, "Electrocuting Arrow", expected_weapons=["bow"])
    _spot(skills, "Galvanic Shards", expected_weapons=["crossbow"])
    _spot(skills, "Shockburst Rounds", expected_weapons=["crossbow"])
    _spot(skills, "Boneshatter", expected_weapons=["mace"])
    _spot(skills, "Earthshatter", expected_weapons=["mace"])
    _spot(skills, "Fireball", expected_weapons=[])

    if unclassified:
        print(f"\n=== Unclassified ({len(unclassified)}) ===")
        for name, reason in unclassified:
            print(f"  {name}: {reason}")
    else:
        print("\n  No unclassified skills.")

    # Breakdown by slot
    from collections import Counter
    slot_counter: Counter[str] = Counter()
    for s in skills.values():
        for w in s["weapons"]:
            slot_counter[w] += 1
    print("\n=== Skills per weapon slot ===")
    for slot, cnt in sorted(slot_counter.items()):
        print(f"  {slot:<14} {cnt}")


def _spot(skills: dict, name: str, expected_weapons: list[str] | None, note: str = "") -> None:
    entry = skills.get(name)
    if entry is None:
        print(f"  MISSING  {name!r}")
        return
    w = entry["weapons"]
    rs = entry["requiresShield"]
    marker = ""
    if expected_weapons is not None and sorted(w) != sorted(expected_weapons):
        marker = " <-- MISMATCH"
    tag = f"weapons={w or 'any'}, requiresShield={rs}"
    if note:
        tag += f", note={note!r}"
    print(f"  {name}: {tag}{marker}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Build PoE2 weapon-skill mapping")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="use cached files in data/_raw/ instead of re-fetching",
    )
    args = parser.parse_args()
    build(args.skip_download)


if __name__ == "__main__":
    main()
