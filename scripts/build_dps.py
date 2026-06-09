#!/usr/bin/env python3
"""
build_dps.py — PoB-grade DPS engine extractor (PoE2 v0.5)

Reads the raw PoB data export (repoe-fork/pob-data) plus the normalized
joins produced by build_catalog.py, and writes two pre-resolved, compact
datasets the browser consumes WITHOUT re-interpolating:

    data/skill_dps.json    — per-skill per-gem-level base/added/baseMultiplier
    data/support_dps.json  — per-support classified more/increased/crit/etc.

Ground-truth rules (evidence-backed by the 5-agent recon; do NOT re-derive):
  * statSets[i].levels[n] numbered keys "1","2",... are FINAL per-gem-level
    values. NEVER re-apply baseEffectiveness/incrementalEffectiveness.
  * Two `levels` arrays exist: the granted-effect TOP-LEVEL levels[] (cost,
    critChance, baseMultiplier, attackSpeedMultiplier, attackTime, ...) and
    each statSet's levels[] (numbered stat values). Both index 0 = gem level 1.
  * Resolve damage stats by NAME -> position in stats[], never a hardcoded index.
  * Attacks have NO base-damage stat; damage = (weaponAvg + skillAdded) *
    baseMultiplier, where baseMultiplier = statSet ?? topLevel ?? 1.0 per level.
  * Supports do NOT scale per gem level; values live in statSet.constantStats.
    Tiers (I/II/III) are separate granted-effects = separate keys.

Usage:
    python3 scripts/build_dps.py [--skip-download]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths — this script lives in scripts/, data lives in ../data/
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_DIR = SCRIPT_DIR.parent
DATA_DIR = REPO_DIR / "data"
RAW_DIR = DATA_DIR / "_raw"
SKILLS_DIR = RAW_DIR / "Skills"

BASE_URL = "https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2"
GLOBAL_LUA_URL = (
    "https://raw.githubusercontent.com/PathOfBuildingCommunity/PathOfBuilding-PoE2"
    "/dev/src/Data/Global.lua"
)

ACTIVE_SKILL_FILES = ["act_str", "act_dex", "act_int", "other", "minion"]
SUPPORT_SKILL_FILES = ["sup_str", "sup_int", "sup_dex"]

VERSION = "0.5"
SOURCE = "repoe-fork/pob-data PoB community export (base values may lag live game patches)"
DEFAULT_LEVEL = 20
DEFAULT_QUALITY = 20
NATURAL_MAX_FALLBACK = 20

# ---------------------------------------------------------------------------
# SkillType ids used by the coverage / exclusion predicate (recon §coverage).
# Names kept for readability; ids are the contract.
# ---------------------------------------------------------------------------
ST_ATTACK = 1
ST_SPELL = 2
ST_WARCRY = 63
ST_DAMAGE_OVER_TIME = 35
ST_CREATES_MINION = 77
ST_CROSSBOW_AMMO = 117  # CrossbowAmmoSkill (the AmmoPlayer half)

# E3: channel/DoT markers on a statSet that mean "damage source is per-minute DoT, not a hit"
PER_MINUTE_BASE_RE = re.compile(r"^base_\w+_damage_to_deal_per_minute$")

# skillTypes that have no own hit -> hard exclude
EXCLUDE_SKILLTYPES = {
    5,    # Buff
    39,   # Aura
    52,   # Herald
    53,   # AuraAffectsEnemies
    88,   # AuraNotOnCaster
    34,   # Movement
    79,   # Travel
    80,   # Blink
    78,   # Guard
    98,   # Hex
    99,   # Mark
    69,   # AppliesCurse
    63,   # Warcry
    89,   # Banner
    94,   # Stance
    155,  # Offering
    122,  # Meta
    119,  # ModifiesNextSkill
    148,  # EmpowersOtherSkill
    158,  # Invocation
    109,  # Blessing
    81,   # CanHaveBlessing
    179,  # IsBlasphemy
    108,  # Link
    65,   # Brand
}

# DoT / ailment-only skillTypes -> exclude (out of v1 scope)
DOT_SKILLTYPES = {
    35,  # DamageOverTime
    24,  # CausesBurning
    17,  # ElementalStatus
}

# statSet stat strings that mark a statSet as dealing no hit damage
NO_DAMAGE_MARKERS = {
    "base_deal_no_damage",
    "display_statset_no_hit_damage",
}

# ---------------------------------------------------------------------------
# Damage-type / stat-name catalogs (recon verbatim)
# ---------------------------------------------------------------------------
DAMAGE_TYPES = ["fire", "cold", "lightning", "physical", "chaos"]

# spell flat base-damage stat -> (type, "min"|"max")
SPELL_BASE_STATS: dict[str, tuple[str, str]] = {}
for _t in DAMAGE_TYPES:
    SPELL_BASE_STATS[f"spell_minimum_base_{_t}_damage"] = (_t, "min")
    SPELL_BASE_STATS[f"spell_maximum_base_{_t}_damage"] = (_t, "max")
    SPELL_BASE_STATS[f"secondary_minimum_base_{_t}_damage"] = (_t, "min")
    SPELL_BASE_STATS[f"secondary_maximum_base_{_t}_damage"] = (_t, "max")

# skill-added flat damage on attacks (read positionally, scaled only by baseMultiplier)
ATTACK_ADDED_STATS: dict[str, tuple[str, str]] = {}
for _t in DAMAGE_TYPES:
    ATTACK_ADDED_STATS[f"attack_minimum_added_{_t}_damage"] = (_t, "min")
    ATTACK_ADDED_STATS[f"attack_maximum_added_{_t}_damage"] = (_t, "max")

# any spell/secondary base-damage stat marks the "spell model"
SPELL_DAMAGE_STAT_NAMES = set(SPELL_BASE_STATS.keys())

# conversion stat -> target element
CONVERT_STATS = {
    f"active_skill_base_physical_damage_%_to_convert_to_{_t}": _t
    for _t in ("fire", "cold", "lightning", "chaos")
}

# ---------------------------------------------------------------------------
# Download helpers (mirror build_catalog.py conventions; stdlib + curl only)
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path, ua: str = "build-dps-script/1.0") -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-fsSL", "--max-time", "30", "-A", ua, "-o", str(dest), url]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {result.stderr.decode()}")
    print(f"  fetched {url} -> {dest.name} ({dest.stat().st_size:,}B)")


def ensure_raw_files(skip_download: bool) -> None:
    """The _raw/Skills/* files are normally present locally; only fetch if missing.

    With --skip-download we never hit the network and rely on cached files.
    Without it, we still prefer cached files and only download the ones missing.
    """
    targets: list[tuple[str, Path]] = []
    for name in ACTIVE_SKILL_FILES + SUPPORT_SKILL_FILES:
        targets.append((f"{BASE_URL}/Skills/{name}.json", SKILLS_DIR / f"{name}.json"))
    lua_target = (GLOBAL_LUA_URL, RAW_DIR / "Global.lua")

    if skip_download:
        print("=== Skipping download, using cached _raw files ===")
        missing = [str(p) for _, p in targets + [lua_target] if not p.exists()]
        if missing:
            raise SystemExit(
                "ERROR: --skip-download but required raw files missing:\n  "
                + "\n  ".join(missing)
            )
        return

    print("=== Ensuring raw data (download only if missing) ===")
    for url, dest in targets:
        if dest.exists():
            print(f"  cached {dest.name}")
        else:
            download_file(url, dest)
    url, dest = lua_target
    if dest.exists():
        print(f"  cached {dest.name}")
    else:
        download_file(url, dest)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(f"ERROR: cannot read {path}: {e}")


# ---------------------------------------------------------------------------
# Raw data loading
# ---------------------------------------------------------------------------

def load_granted_effects(file_stems: list[str]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for stem in file_stems:
        p = SKILLS_DIR / f"{stem}.json"
        if not p.exists():
            print(f"  WARNING: {p.name} not found", file=sys.stderr)
            continue
        data = load_json(p)
        merged.update(data)
        print(f"  {p.name}: {len(data)} granted-effects")
    return merged


def skilltypes_to_set(raw: Any) -> set[int]:
    """skillTypes may be a dict {id:true} (raw files) or a list of ints (normalized)."""
    if isinstance(raw, dict):
        return {int(k) for k, v in raw.items() if v}
    if isinstance(raw, list):
        return {int(x) for x in raw}
    return set()


def weapon_types_list(raw: Any) -> list[str]:
    """weaponTypes is {Name: true} on the granted-effect; 'None' = unarmed."""
    if not isinstance(raw, dict):
        return []
    names = [k for k, v in raw.items() if v]
    # 'None' is the unarmed/no-weapon marker — keep it out of the type list.
    return [n for n in names if n != "None"]


# ---------------------------------------------------------------------------
# Per-level value resolution
# ---------------------------------------------------------------------------

def numbered_value(level_row: dict[str, Any], position: int) -> float | None:
    """Read the FINAL value at stats[] position `position` from a statSet level row.

    Numbered keys "1","2",... map positionally to stats[0],stats[1],...
    """
    key = str(position + 1)
    v = level_row.get(key)
    if v is None:
        return None
    return v


def stat_positions(stats: list[str], wanted: set[str]) -> dict[int, str]:
    """Map position -> stat-name for the FIRST occurrence of each wanted stat.

    Resolve by name->position; some statSets prepend/duplicate (e.g. Bonestorm
    Explosion has zero-pair then real values). We take the first position that
    yields a non-null numbered value at read time, so collect all occurrences.
    """
    found: dict[int, str] = {}
    for i, name in enumerate(stats):
        if name in wanted:
            found[i] = name
    return found


def resolve_base_multiplier(
    statset_levels: list[dict[str, Any]] | None,
    top_levels: list[dict[str, Any]],
    idx: int,
) -> float:
    """baseMultiplier per level = statSet ?? topLevel ?? 1.0 (recon rule 5)."""
    if statset_levels is not None and idx < len(statset_levels):
        v = statset_levels[idx].get("baseMultiplier")
        if v is not None:
            return v
    if idx < len(top_levels):
        v = top_levels[idx].get("baseMultiplier")
        if v is not None:
            return v
    return 1.0


def first_present_in_top(top_levels: list[dict[str, Any]], field: str) -> Any:
    for row in top_levels:
        if row.get(field) is not None:
            return row[field]
    return None


def pick_primary_statset(statsets: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    """PRIMARY = first statSet that does NOT contain a no-damage marker.

    In every tested multi-statSet case this resolves to statSets[0] (recon).
    Falls back to statSets[0] if all are no-damage.
    """
    for i, ss in enumerate(statsets):
        stats = ss.get("stats", []) or []
        if not (set(stats) & NO_DAMAGE_MARKERS):
            return i, ss
    return 0, statsets[0]


def all_statsets_no_damage(statsets: list[dict[str, Any]]) -> bool:
    if not statsets:
        return True
    for ss in statsets:
        stats = ss.get("stats", []) or []
        if not (set(stats) & NO_DAMAGE_MARKERS):
            return False
    return True


# ---------------------------------------------------------------------------
# Conversion extraction (level-independent) from a statSet's constantStats
# ---------------------------------------------------------------------------

def extract_convert(statset: dict[str, Any]) -> dict[str, float]:
    """phys->X conversion from a statSet's constantStats; first per target wins.

    The primary value (e.g. 80) precedes any duplicated secondary (e.g. 20), so
    taking the first occurrence per target gives the intended whole-skill convert.
    """
    convert: dict[str, float] = {}
    for entry in statset.get("constantStats", []) or []:
        if not isinstance(entry, list) or len(entry) < 2:
            continue
        target = CONVERT_STATS.get(entry[0])
        if target is not None and target not in convert:
            convert[target] = entry[1]
    return convert


# ---------------------------------------------------------------------------
# Skill record builder
# ---------------------------------------------------------------------------

def build_spell_levels(
    primary_ss: dict[str, Any],
    top_levels: list[dict[str, Any]],
    max_index: int,
) -> dict[str, Any]:
    """For each gem level emit base {type:[min,max]} read by name->position."""
    ss_levels = primary_ss.get("levels", []) or []
    stats = primary_ss.get("stats", []) or []
    base_positions = stat_positions(stats, SPELL_DAMAGE_STAT_NAMES)

    out: dict[str, Any] = {}
    n = min(max_index, len(ss_levels) - 1)
    for gem_level in range(1, n + 2):
        idx = gem_level - 1
        if idx >= len(ss_levels):
            break
        row = ss_levels[idx]
        base: dict[str, list[float]] = {}
        for pos, name in base_positions.items():
            dtype, mm = SPELL_BASE_STATS[name]
            val = numbered_value(row, pos)
            if val is None:
                continue
            slot = base.setdefault(dtype, [0.0, 0.0])
            # First non-null occurrence per (type, min/max) wins; skip zero
            # placeholders only if a real value already captured.
            j = 0 if mm == "min" else 1
            if slot[j] == 0.0:
                slot[j] = val
        # Drop all-zero types (zero-pad placeholders)
        base = {t: v for t, v in base.items() if v != [0.0, 0.0]}
        out[str(gem_level)] = {
            "base": base,
            "added": {},
            "baseMultiplier": None,
            "attackSpeedMultiplier": None,
        }
    return out


def build_attack_levels(
    primary_ss: dict[str, Any],
    top_levels: list[dict[str, Any]],
    max_index: int,
) -> dict[str, Any]:
    """For each gem level emit baseMultiplier + attackSpeedMultiplier (+skill added)."""
    ss_levels = primary_ss.get("levels", []) or []
    stats = primary_ss.get("stats", []) or []
    added_positions = stat_positions(stats, set(ATTACK_ADDED_STATS.keys()))

    out: dict[str, Any] = {}
    # Attacks are gated by the top-level levels array length (statSet levels may
    # only carry actorLevel). Use the longer of the two for row availability.
    available = max(len(top_levels), len(ss_levels))
    n = min(max_index, available - 1)
    for gem_level in range(1, n + 2):
        idx = gem_level - 1
        if idx >= available:
            break
        base_mult = resolve_base_multiplier(ss_levels, top_levels, idx)
        asm = None
        if idx < len(top_levels):
            asm = top_levels[idx].get("attackSpeedMultiplier")
        # Skill-added flat (rare) read positionally from the statSet level row.
        added: dict[str, list[float]] = {}
        if added_positions and idx < len(ss_levels):
            row = ss_levels[idx]
            for pos, name in added_positions.items():
                dtype, mm = ATTACK_ADDED_STATS[name]
                val = numbered_value(row, pos)
                if val is None:
                    continue
                slot = added.setdefault(dtype, [0.0, 0.0])
                slot[0 if mm == "min" else 1] = val
            added = {t: v for t, v in added.items() if v != [0.0, 0.0]}
        out[str(gem_level)] = {
            "base": {},
            "added": added,
            "baseMultiplier": base_mult,
            "attackSpeedMultiplier": asm,
        }
    return out


def collect_convert(statsets: list[dict[str, Any]]) -> dict[str, float]:
    """Merge phys->X conversion across statSets (primary-first, first wins)."""
    convert: dict[str, float] = {}
    for ss in statsets:
        for target, value in extract_convert(ss).items():
            if target not in convert:
                convert[target] = value
    return convert


def build_skill_record(
    gem: dict[str, Any],
    effect: dict[str, Any],
    kind: str,
    effect_id: str,
) -> dict[str, Any]:
    top_levels = effect.get("levels", []) or []
    statsets = effect.get("statSets", []) or []
    prim_idx, primary_ss = pick_primary_statset(statsets)

    natural_max = gem.get("naturalMaxLevel") or NATURAL_MAX_FALLBACK
    # Cap maxLevel at naturalMaxLevel; clamp to available rows.
    ss_rows = len(primary_ss.get("levels", []) or [])
    top_rows = len(top_levels)
    available_rows = max(ss_rows, top_rows) if kind == "attack" else ss_rows
    if available_rows == 0:
        available_rows = top_rows
    max_index = min(natural_max - 1, available_rows - 1)
    if max_index < 0:
        max_index = 0

    crit_chance = first_present_in_top(top_levels, "critChance")
    # Spell: critChance if present else 5.0. Attack: null => use weapon crit,
    # unless the skill explicitly sets critChance (non-weapon attacks).
    if kind == "spell":
        crit_out: float | None = crit_chance if crit_chance is not None else 5.0
    else:
        crit_out = crit_chance  # may be None -> engine falls back to weapon crit

    attack_time_ms = first_present_in_top(top_levels, "attackTime")

    if kind == "spell":
        levels = build_spell_levels(primary_ss, top_levels, max_index)
    else:
        levels = build_attack_levels(primary_ss, top_levels, max_index)

    return {
        "id": effect_id,
        "kind": kind,
        "primaryStatSet": primary_ss.get("label", "") or "",
        "castTime": effect.get("castTime"),
        "attackTimeMs": attack_time_ms,
        "critChance": crit_out,
        "weaponTypes": weapon_types_list(effect.get("weaponTypes")),
        "maxLevel": max_index + 1,
        "convert": collect_convert(statsets),
        "quality": effect.get("qualityStats", []) or [],
        "levels": levels,
    }


# ---------------------------------------------------------------------------
# Coverage / exclusion predicate (recon §coverage, order preserved)
# ---------------------------------------------------------------------------

def classify_skill(
    gem: dict[str, Any],
    active_effects: dict[str, Any],
) -> tuple[str, str | None, dict[str, Any] | None, str, bool]:
    """Return (verdict, reason, effect, effect_id, crossbow_recovered).

    verdict in {"spell","attack","exclude"}.
    reason set when excluded; effect is the (possibly suffix-swapped) granted-effect;
    effect_id is the granted-effect id actually used (the sibling id for crossbow);
    crossbow_recovered True when the damaging ...Player sibling was substituted.
    """
    ge_id = gem.get("grantedEffectId", "")
    effect = active_effects.get(ge_id)
    skilltypes = set(gem.get("skillTypes", []) or [])

    # (1) no granted-effect -> exclude
    if effect is None:
        return "exclude", "no_granted_effect", None, ge_id, False

    # (2) minion -> flag-excluded v1
    if ST_CREATES_MINION in skilltypes:
        return "exclude", "minion", None, ge_id, False

    # (3) crossbow AmmoPlayer -> recover sibling ...Player
    if ST_CROSSBOW_AMMO in skilltypes and ge_id.endswith("AmmoPlayer"):
        sibling_id = ge_id[: -len("AmmoPlayer")] + "Player"
        sibling = active_effects.get(sibling_id)
        if sibling is not None:
            sib_types = skilltypes_to_set(sibling.get("skillTypes"))
            # Sibling is a spell only if it actually carries spell base-damage.
            if ST_ATTACK not in sib_types and any(
                set(ss.get("stats", []) or []) & SPELL_DAMAGE_STAT_NAMES
                for ss in sibling.get("statSets", []) or []
            ):
                return "spell", None, sibling, sibling_id, True
            # Default: the damaging sibling is a weapon-scaled Attack.
            return "attack", None, sibling, sibling_id, True

    statsets = effect.get("statSets", []) or []

    # (4) ALL statSets are no-damage -> exclude
    if all_statsets_no_damage(statsets):
        return "exclude", "base_deal_no_damage", None, ge_id, False

    # (4b) E3 pre-empt: warcry-hit and channel/DoT-source skills before the hit
    #      acceptance. Warcry(63) is always excluded (Arctic Howl, Seismic Cry).
    #      DoT-as-damage-source = DamageOverTime(35) on a non-Attack, OR the
    #      primary statSet's damage source is a per-minute base damage stat
    #      (Incinerate, Flame Wall). DoT on an Attack (Tornado Shot, Vine Arrow)
    #      keeps its weapon hit; pure-DoT spells defer to the DoT fast-follow.
    if ST_WARCRY in skilltypes:
        return "exclude", "warcry", None, ge_id, False
    _, prim_for_dot = pick_primary_statset(statsets)
    prim_stats = prim_for_dot.get("stats", []) or []
    primary_is_per_minute = any(PER_MINUTE_BASE_RE.match(s) for s in prim_stats)
    if (ST_DAMAGE_OVER_TIME in skilltypes and ST_ATTACK not in skilltypes) or primary_is_per_minute:
        return "exclude", "dot_or_channel", None, ge_id, False

    # (5) Attack(1) -> attack model
    if ST_ATTACK in skilltypes:
        return "attack", None, effect, ge_id, False

    # (6) any statSet carries a spell/secondary base-damage stat -> spell model
    for ss in statsets:
        if set(ss.get("stats", []) or []) & SPELL_DAMAGE_STAT_NAMES:
            return "spell", None, effect, ge_id, False

    # (7) excluded skillType (aura/buff/curse/meta/...)
    if skilltypes & EXCLUDE_SKILLTYPES:
        return "exclude", "skilltype", None, ge_id, False

    # (8) DoT / ailment-only
    if skilltypes & DOT_SKILLTYPES:
        return "exclude", "dot_only", None, ge_id, False

    # (9) else — no hit
    return "exclude", "no_base_damage_stat_no_hit", None, ge_id, False


# ---------------------------------------------------------------------------
# Support classification (recon §support)
# ---------------------------------------------------------------------------

# Buckets inferred from the more-stat name. Order matters: most specific first.
BUCKET_RULES: list[tuple[str, str]] = [
    ("physical", "physical"),
    ("melee_physical", "physical"),
    ("brutality", "physical"),
    ("heft", "physical"),
    ("spell", "spell"),
    ("controlled_destruction", "spell"),
    ("area", "area"),
    ("concentrate", "area"),
    # two-element attunement penalties apply to ONLY the named pair (not all elements)
    ("cold_and_lightning", "cold+lightning"),
    ("fire_and_lightning", "fire+lightning"),
    ("cold_and_fire", "cold+fire"),
    ("elemental", "element"),  # genuinely all-elemental (fire+cold+lightning)
    ("fire", "fire"),
    ("cold", "cold"),
    ("lightning", "lightning"),
    ("chaos", "chaos"),
    ("attack", "attack"),
    ("projectile", "projectile"),
    ("melee", "melee"),
    ("rage", "all"),
    ("chain", "all"),
    ("hourglass", "all"),
    ("multiple", "all"),
]


def infer_bucket(stat_name: str) -> str:
    """Infer which damage type(s) a more-multiplier applies to from its name."""
    s = stat_name
    # Generic canonical names => 'all'
    if s in ("support_active_skill_damage_+%_final", "supported_active_skill_damage_+%_final"):
        return "all"
    for needle, bucket in BUCKET_RULES:
        if needle in s:
            return bucket
    return "all"


def is_more_stat(name: str) -> bool:
    return name.endswith("_+%_final")


# E2: ONLY firing-rate speed is a MORE on the rate (attack_speed / cast_speed).
# projectile_speed, movement_speed, reload_speed, cooldown_speed are NOT rate
# multipliers and stay in rawConstantStats.
def speed_kind(name: str) -> str | None:
    if "attack_speed_+%_final" in name:
        return "attack"
    if "cast_speed_+%_final" in name:
        return "cast"
    return None


# E1: hit-damage type/generic tokens that make a '*_+%_final' a GUARANTEED hit
# damage multiplier, and the non-damage/over-time tokens that disqualify it.
HIT_DAMAGE_SENSES = (
    "fire", "cold", "lightning", "physical", "chaos",
    "elemental", "spell", "attack", "area", "projectile", "melee",
)
GENERIC_HIT_MORE = {
    "support_active_skill_damage_+%_final",
    "supported_active_skill_damage_+%_final",
}
NON_DAMAGE_MORE_TOKENS = (
    "damage_taken", "damage_over_time", "_effect", "_duration", "_cost",
    "accuracy", "accurary", "area_of_effect", "_aoe", "knockback",
    "chance_to_", "_stun_", "pin_", "reload", "projectile_speed",
    "movement_speed", "cooldown", "_life", "mana", "_speed_+%_final",
)
# tokens that make an otherwise-hit damage more CONDITIONAL (situational ceiling)
CONDITIONAL_MORE_TOKENS = (
    "_vs_", "_if_", "_while_", "_when_", "_per_", "_from_distance",
    "_on_low_life", "_with_momentum", "_from_current_", "_poise",
    "_assault", "_called_shots", "forked", "_chain", "pierced",
    "_per_pierced",
)


def is_hit_damage_more(name: str) -> bool:
    """A guaranteed hit-damage MORE: generic, or *_{hit type}_damage_+%_final,
    AND free of any non-damage / over-time token."""
    if any(tok in name for tok in NON_DAMAGE_MORE_TOKENS):
        return False
    if name in GENERIC_HIT_MORE:
        return True
    return any(f"_{t}_damage_+%_final" in name for t in HIT_DAMAGE_SENSES)


def is_conditional_more(name: str) -> bool:
    return any(tok in name for tok in CONDITIONAL_MORE_TOKENS)


def is_crit_more_stat(name: str) -> bool:
    return is_more_stat(name) and "critical_strike" in name


def classify_support(
    name: str,
    effect: dict[str, Any],
) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "id": effect_id_of(effect, name),
        "more": [],
        "increased": [],
        "moreSpeed": [],
        "gainAs": [],
        "crit": {"addedMulti": 0, "addedChance": 0, "moreChance": 0, "moreMulti": 0},
        "convert": [],
        "flags": [],
        "tags": {},
        "rawConstantStats": {},
    }

    statsets = effect.get("statSets", []) or []
    for ss in statsets:
        # Flag-only stats live in stats[] (no value).
        for flag in ss.get("stats", []) or []:
            if isinstance(flag, str) and flag not in rec["flags"]:
                rec["flags"].append(flag)
        for entry in ss.get("constantStats", []) or []:
            if not isinstance(entry, list) or len(entry) < 2:
                continue
            sname, value = entry[0], entry[1]
            rec["rawConstantStats"][sname] = value
            classify_const_stat(sname, value, rec)

    # tags: a light hint set for the engine (mirror catalog tag style loosely).
    tags = effect.get("tags") or {}
    if isinstance(tags, dict):
        rec["tags"] = {k: True for k, v in tags.items() if v}
    rec["tags"].setdefault("support", True)
    return rec


def classify_const_stat(sname: str, value: Any, rec: dict[str, Any]) -> None:
    # --- conversion (gain-as attunement) ---
    m = re.match(r"non_skill_base_(\w+?)_damage_%_to_gain_as_(\w+)", sname)
    if m:
        src = m.group(1)  # 'all' / 'physical' / element
        # strip trailing condition (e.g. 'fire_with_attacks_vs_burning_enemies')
        to = m.group(2).split("_with_")[0].split("_vs_")[0]
        rec["gainAs"].append({"from": src, "to": to, "pct": value})
        return

    # phys->X conversion (rare on supports, but handle)
    target = CONVERT_STATS.get(sname)
    if target is not None:
        rec["convert"].append({"from": "physical", "to": target, "pct": value})
        return

    # --- crit ---
    if sname == "base_critical_strike_multiplier_+":
        rec["crit"]["addedMulti"] += value
        return
    if sname == "additional_base_critical_strike_chance":
        rec["crit"]["addedChance"] += value
        return
    if is_crit_more_stat(sname):
        if "critical_strike_chance" in sname:
            rec["crit"]["moreChance"] += value
        elif "critical_strike_multiplier" in sname:
            rec["crit"]["moreMulti"] += value
        return

    # --- firing-rate speed (more, multiplicative) — E2: attack/cast only ---
    sk = speed_kind(sname)
    if sk is not None:
        rec["moreSpeed"].append({"stat": sname, "value": value, "kind": sk})
        return

    # --- increased (additive) speed ---
    if sname in ("attack_speed_+%", "base_cast_speed_+%"):
        bucket = "attack_speed" if sname == "attack_speed_+%" else "cast_speed"
        rec["increased"].append({"stat": sname, "value": value, "bucket": bucket})
        return

    # --- more / less HIT damage multiplier — E1: only true hit-damage mores.
    # Non-damage *_+%_final (aoe, duration, cost, chance_to_*, stun, etc.) stay
    # ONLY in rawConstantStats; they must NOT become guaranteed hit multipliers.
    if is_hit_damage_more(sname):
        if value:  # a 0-value more is a no-op (×1.0); keep it in rawConstantStats only
            entry = {
                "stat": sname,
                "value": value,
                "bucket": infer_bucket(sname),
            }
            if is_conditional_more(sname):
                entry["conditional"] = True
            rec["more"].append(entry)
        return

    # other plain '_+%'/'_+%_final' stats (penetration, ailment chance, aoe,
    # duration, cost, ...) stay only in rawConstantStats; they aren't
    # more/increased HIT damage multipliers.


def effect_id_of(effect: dict[str, Any], name: str) -> str:
    return effect.get("_ge_id", "")


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def build_skills(
    skill_gems: list[dict[str, Any]],
    active_effects: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str], dict[str, int]]:
    skills: dict[str, Any] = {}
    excluded: dict[str, str] = {}
    crossbow_names: set[str] = set()

    # Skill records are keyed by name; a few gems share a name (Mace Strike x3,
    # Lightning Bolt x2, Spear Stab x2) and collapse to one record. Count the
    # resulting records, not raw gems, so the summary matches the output.
    for gem in skill_gems:
        name = gem.get("name", "")
        if not name:
            continue
        verdict, reason, effect, effect_id, crossbow = classify_skill(gem, active_effects)
        if verdict == "exclude":
            # Don't let an exclusion overwrite a same-named damaging record.
            if name not in skills:
                excluded[name] = reason or "excluded"
            continue
        # A damaging record wins over a previously-recorded exclusion.
        excluded.pop(name, None)
        crossbow_names.discard(name)
        skills[name] = build_skill_record(gem, effect, verdict, effect_id)
        if crossbow:
            crossbow_names.add(name)

    counts = {
        "attack": sum(1 for v in skills.values() if v["kind"] == "attack"),
        "spell": sum(1 for v in skills.values() if v["kind"] == "spell"),
        "crossbow": len(crossbow_names),
        "excluded": len(excluded),
    }
    return skills, excluded, counts


def build_supports(
    support_gems: list[dict[str, Any]],
    support_effects: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    supports: dict[str, Any] = {}
    # E1 audit: count *_+%_final stats removed-from-more vs kept, and conditional.
    counts = {"more_kept": 0, "removed_from_more": 0, "conditional": 0}
    for gem in support_gems:
        name = gem.get("name", "")
        ge_id = gem.get("grantedEffectId", "")
        if not name or not ge_id:
            continue
        effect = support_effects.get(ge_id)
        if effect is None:
            continue
        # Stamp the granted-effect id for id_of (raw effects don't carry it).
        effect = dict(effect)
        effect["_ge_id"] = ge_id
        rec = classify_support(name, effect)
        supports[name] = rec
        counts["more_kept"] += len(rec["more"])
        counts["conditional"] += sum(1 for e in rec["more"] if e.get("conditional"))
        # a *_+%_final raw stat that is NOT a kept hit-more (and isn't speed/crit)
        # was previously force-fed into 'more'; count those now diverted.
        kept_stats = {e["stat"] for e in rec["more"]}
        for sname in rec["rawConstantStats"]:
            if (
                is_more_stat(sname)
                and sname not in kept_stats
                and speed_kind(sname) is None
                and not is_crit_more_stat(sname)
                and CONVERT_STATS.get(sname) is None
            ):
                counts["removed_from_more"] += 1
    return supports, counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build PoE2 DPS extractor datasets")
    parser.add_argument("--skip-download", action="store_true",
                        help="Use cached _raw/ files (default-preferred; only downloads missing)")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ensure_raw_files(args.skip_download)

    print("\n=== Loading data ===")
    skill_gems = load_json(DATA_DIR / "skill_gems.json")
    support_gems = load_json(DATA_DIR / "support_gems.json")
    print(f"  skill_gems.json: {len(skill_gems)} gems")
    print(f"  support_gems.json: {len(support_gems)} gems")

    print("  active granted-effects:")
    active_effects = load_granted_effects(ACTIVE_SKILL_FILES)
    print(f"  total active: {len(active_effects)}")

    print("  support granted-effects:")
    support_effects = load_granted_effects(SUPPORT_SKILL_FILES)
    print(f"  total support: {len(support_effects)}")

    print("\n=== Building skill_dps ===")
    skills, excluded, counts = build_skills(skill_gems, active_effects)
    attack_count = counts["attack"]
    spell_count = counts["spell"]
    crossbow_count = counts["crossbow"]
    excluded_count = counts["excluded"]
    skill_count = len(skills)
    print(f"  skills: {skill_count} (attack {attack_count}, spell {spell_count}, "
          f"crossbow-recovered {crossbow_count})")
    print(f"  excluded: {excluded_count}")

    print("\n=== Building support_dps ===")
    supports, sup_counts = build_supports(support_gems, support_effects)
    print(f"  supports: {len(supports)}")
    print(f"  more entries kept (hit-damage): {sup_counts['more_kept']}  "
          f"(conditional-flagged: {sup_counts['conditional']})")
    print(f"  *_+%_final removed-from-more (non-damage -> rawConstantStats only): "
          f"{sup_counts['removed_from_more']}")

    now = datetime.now(timezone.utc).isoformat()

    skill_dps = {
        "version": VERSION,
        "source": SOURCE,
        "generated_at": now,
        "default_level": DEFAULT_LEVEL,
        "default_quality": DEFAULT_QUALITY,
        "skills": skills,
        "excluded": excluded,
    }
    support_dps = {
        "version": VERSION,
        "source": SOURCE,
        "generated_at": now,
        "default_level": DEFAULT_LEVEL,
        "default_quality": DEFAULT_QUALITY,
        "supports": supports,
    }

    print("\n=== Writing outputs ===")

    def write_json(path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote {path} ({path.stat().st_size:,}B)")

    write_json(DATA_DIR / "skill_dps.json", skill_dps)
    write_json(DATA_DIR / "support_dps.json", support_dps)

    print("\n=== Summary ===")
    print(f"  skillCount={skill_count} attackCount={attack_count} "
          f"spellCount={spell_count} crossbowRecovered={crossbow_count} "
          f"excludedCount={excluded_count} supportCount={len(supports)}")
    print("=== Done ===")


if __name__ == "__main__":
    main()
