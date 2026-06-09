#!/usr/bin/env python3
"""
build_items.py -- PoE2 v0.5 item layer builder

Downloads PoB community data export (repoe-fork/pob-data), normalizes it into
clean JSON datasets for uniques, bases, runes/soul cores, and jewels, then
renders a static HTML browser for searching/filtering.

Usage:
    python3 scripts/build_items.py [--skip-download]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
RAW_DIR = REPO_ROOT / "data" / "_raw"
DATA_DIR = REPO_ROOT / "data"
PAGES_DIR = REPO_ROOT / "pages"

BASE_URL = "https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2"
GITHUB_API = "https://api.github.com/repos/repoe-fork/pob-data/contents/pob-data/poe2/TimelessJewelData"

# All item slots. Empty 2-byte unique files (claw, flail, sword) are skipped
# gracefully during parse -- no need to exclude from the download list.
ITEM_SLOTS = [
    "amulet", "belt", "body", "boots", "bow", "crossbow",
    "dagger", "claw", "flail", "mace", "sceptre", "spear",
    "staff", "sword", "wand", "focus", "quiver", "shield",
    "gloves", "helmet", "ring", "jewel", "flask", "talisman",
]

WEAPON_SLOTS = {
    "bow", "crossbow", "dagger", "claw", "flail", "mace",
    "sceptre", "spear", "staff", "sword", "wand", "talisman",
}
ARMOUR_SLOTS = {"body", "boots", "gloves", "helmet", "shield", "focus"}
JEWELLERY_SLOTS = {"amulet", "belt", "ring", "quiver"}

_UA = "build-items-script/1.0"


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def _fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
    except Exception as e:
        raise RuntimeError(f"fetch failed: {url}: {e}") from e
    print(f"  fetched {url.split('/')[-1]} ({dest.stat().st_size:,}B)")


def _fetch_json_api(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        raise RuntimeError(f"api fetch failed: {url}: {e}") from e


def download_all() -> None:
    print("=== Downloading raw data ===")
    for slot in ITEM_SLOTS:
        _fetch(f"{BASE_URL}/Uniques/{slot}.json", RAW_DIR / "Uniques" / f"{slot}.json")
        _fetch(f"{BASE_URL}/Bases/{slot}.json", RAW_DIR / "Bases" / f"{slot}.json")
    for fname in ["ModRunes.json", "ClusterJewels.json", "ModJewel.json", "Misc.json"]:
        _fetch(f"{BASE_URL}/{fname}", RAW_DIR / fname)
    # Discover and fetch TimelessJewelData files via GitHub contents API
    print("  fetching TimelessJewelData file list via GitHub API...")
    contents = _fetch_json_api(GITHUB_API)
    timeless_dir = RAW_DIR / "TimelessJewelData"
    for entry in contents:
        if entry.get("type") == "file":
            _fetch(entry["download_url"], timeless_dir / entry["name"])


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(f"ERROR: cannot read {path}: {e}") from e


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote {path.relative_to(REPO_ROOT)} ({path.stat().st_size:,}B)")
    except OSError as e:
        raise SystemExit(f"ERROR writing {path}: {e}") from e


# ---------------------------------------------------------------------------
# Unique item text parser
#
# PoB stores each unique as a single multi-line string with this structure:
#
#   Name
#   Base Type
#   [Source: ...]           optional
#   [League: ...]           optional
#   [Variant: label]        zero or more -- defines variant labels
#   [Has Alt Variant ...]   optional
#   [Selected Variant: N]   optional
#   [Sockets: ...]          optional
#   [Limited to: N]         optional
#   [Grants Skill: ...]     optional
#   Implicits: N
#   <N implicit mod lines>
#   <explicit mod lines>
#
# Each mod line may be prefixed with {variant:N,M} and/or {tags:...}.
# We keep the current (last) variant's mods, stripping variant/tag prefixes.
# ---------------------------------------------------------------------------

_VARIANT_PREFIX = re.compile(r"^\{variant:[^}]+\}")
_TAGS_PREFIX = re.compile(r"^\{tags:[^}]+\}")
_BRACES_PREFIX = re.compile(r"^\{[^}]+\}")


def _strip_prefixes(line: str) -> str:
    """Remove leading {variant:...} and {tags:...} annotation tokens."""
    while True:
        m = _BRACES_PREFIX.match(line)
        if not m:
            break
        line = line[m.end():]
    return line.strip()


def _line_variant_nums(line: str) -> set[int]:
    """Return set of variant indices from {variant:1,2,...} prefix, or empty set for 'all'."""
    m = _VARIANT_PREFIX.match(line)
    if not m:
        return set()
    inner = m.group(0)[9:-1]  # strip '{variant:' and '}'
    parts = [p.strip() for p in inner.split(",")]
    nums: set[int] = set()
    for p in parts:
        try:
            nums.add(int(p))
        except ValueError:
            pass
    return nums


def parse_unique_text(text: str, slot: str) -> dict[str, Any]:
    """
    Parse one PoB unique item text block into a normalized dict.
    For multi-variant items, use the last (most current) variant.
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return {}

    name = lines[0].strip()
    base_type = lines[1].strip()

    source = ""
    league = ""
    variant_labels: list[str] = []
    sockets = ""
    limited_to: int | None = None
    grants_skill: list[str] = []
    implicits_count = 0
    raw_mod_lines: list[str] = []

    _HEADER_PREFIXES = (
        "Source:", "League:", "Variant:", "Has Alt Variant",
        "Selected Variant", "Selected Alt Variant",
        "Sockets:", "Limited to:", "Grants Skill:", "Implicits:",
    )

    idx = 2
    found_implicits_line = False
    while idx < len(lines):
        line = lines[idx]
        if line.startswith("Source:"):
            source = line[7:].strip()
        elif line.startswith("League:"):
            league = line[7:].strip()
        elif line.startswith("Variant:"):
            variant_labels.append(line[8:].strip())
        elif line.startswith("Has Alt Variant") or line.startswith("Selected Variant") or line.startswith("Selected Alt Variant"):
            pass
        elif line.startswith("Sockets:"):
            sockets = line[8:].strip()
        elif line.startswith("Limited to:"):
            try:
                limited_to = int(line[11:].strip())
            except ValueError:
                pass
        elif line.startswith("Grants Skill:"):
            grants_skill.append(line[13:].strip())
        elif line.startswith("Implicits:"):
            try:
                implicits_count = int(line[10:].strip())
            except ValueError:
                implicits_count = 0
            idx += 1
            found_implicits_line = True
            break
        elif line.strip() and not any(line.startswith(p) for p in _HEADER_PREFIXES):
            # First non-header, non-empty line that looks like a mod -- stop
            # scanning headers and treat everything from here as mod lines.
            break
        idx += 1

    # Everything from idx onward is mod content.
    # When no Implicits: line was present, implicits_count stays 0
    # and all mods are treated as explicits.
    raw_mod_lines = [l for l in lines[idx:] if l.strip()]

    # Determine current variant index (1-based; 0 = no variants)
    current_variant = len(variant_labels)  # last variant is always current

    def _include_line(line: str) -> bool:
        """Return True if this mod line applies to the current variant."""
        m = _VARIANT_PREFIX.match(line)
        if not m:
            return True  # no variant tag = applies to all
        nums = _line_variant_nums(line)
        if not nums:
            return True
        return current_variant in nums

    included = [_strip_prefixes(l) for l in raw_mod_lines if _include_line(l) and l.strip()]
    included = [l for l in included if l]

    implicits = included[:implicits_count]
    explicits = included[implicits_count:]

    # Build requirements from base type name heuristics -- uniques don't have
    # separate req fields in this format; requirements come from the base type.
    # We leave these as empty dicts -- the base lookup in the optimizer can
    # fill them in from bases.json.
    requirements: dict[str, int] = {}

    tags: list[str] = []
    if sockets:
        tags.append(f"sockets:{sockets}")
    if limited_to is not None:
        tags.append(f"limited:{limited_to}")

    item: dict[str, Any] = {
        "name": name,
        "slot": slot,
        "baseType": base_type,
        "requirements": requirements,
        "implicits": implicits,
        "explicits": explicits,
        "source": source,
        "league": league,
        "tags": tags,
    }
    if grants_skill:
        item["grantsSkill"] = grants_skill
    if sockets:
        item["sockets"] = sockets
    if limited_to is not None:
        item["limitedTo"] = limited_to
    return item


# ---------------------------------------------------------------------------
# Bases parser
# ---------------------------------------------------------------------------

def _slot_category(slot: str) -> str:
    if slot in WEAPON_SLOTS:
        return "weapon"
    if slot in ARMOUR_SLOTS:
        return "armour"
    if slot in JEWELLERY_SLOTS:
        return "jewellery"
    if slot == "jewel":
        return "jewel"
    if slot == "flask":
        return "flask"
    return "other"


def _parse_requirements(req_raw: Any) -> dict[str, int]:
    """Normalize req field which may be a dict or an empty list."""
    if not isinstance(req_raw, dict):
        return {}
    out: dict[str, int] = {}
    for key in ("level", "str", "dex", "int"):
        if key in req_raw:
            try:
                out[key] = int(req_raw[key])
            except (ValueError, TypeError):
                pass
    return out


def _parse_weapon_stats(w: dict[str, Any]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    if "PhysicalMin" in w:
        stats["physDamageMin"] = w["PhysicalMin"]
    if "PhysicalMax" in w:
        stats["physDamageMax"] = w["PhysicalMax"]
    if "CritChanceBase" in w:
        stats["critChance"] = w["CritChanceBase"]
    if "AttackRateBase" in w:
        stats["attackSpeed"] = w["AttackRateBase"]
    if "Range" in w:
        stats["range"] = w["Range"]
    if "ReloadTimeBase" in w:
        stats["reloadTime"] = w["ReloadTimeBase"]
    # Extra damage types (e.g. cold/fire base damage)
    damage_types: dict[str, Any] = {}
    for key in w:
        if key not in ("PhysicalMin", "PhysicalMax", "CritChanceBase",
                       "AttackRateBase", "Range", "ReloadTimeBase"):
            damage_types[key] = w[key]
    if damage_types:
        stats["damageTypes"] = damage_types
    return stats


def _parse_armour_stats(a: dict[str, Any]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    for src_key, dst_key in [
        ("Armour", "armour"),
        ("Evasion", "evasion"),
        ("EnergyShield", "energyShield"),
        ("Ward", "ward"),
        ("Block", "block"),
        ("MovementPenalty", "movementPenalty"),
    ]:
        if src_key in a:
            stats[dst_key] = a[src_key]
    return stats


def parse_base(name: str, data: dict[str, Any], slot: str) -> dict[str, Any]:
    category = _slot_category(slot)
    req = _parse_requirements(data.get("req", {}))

    # Implicits -- can be a string or missing
    implicit_raw = data.get("implicit", "")
    implicits = [implicit_raw] if implicit_raw else []

    implicit_mod_types: list[Any] = data.get("implicitModTypes", [])
    tags_dict: dict[str, bool] = data.get("tags", {})
    item_type = data.get("type", "")
    sub_type = data.get("subType", "")
    socket_limit = data.get("socketLimit")
    quality = data.get("quality")

    base: dict[str, Any] = {
        "name": name,
        "slot": slot,
        "category": category,
        "itemClass": item_type,
        "subType": sub_type,
        "requirements": req,
        "implicits": implicits,
        "tags": [k for k, v in tags_dict.items() if v],
    }

    if socket_limit is not None:
        base["socketLimit"] = socket_limit
    if quality is not None:
        base["baseQuality"] = quality

    # Type-specific stats
    raw: dict[str, Any] = {}

    if "weapon" in data and isinstance(data["weapon"], dict):
        base["weaponStats"] = _parse_weapon_stats(data["weapon"])
    else:
        raw_weapon = {k: v for k, v in data.items()
                      if k not in ("implicitModTypes", "quality", "req", "socketLimit",
                                   "tags", "type", "subType", "implicit", "armour",
                                   "charm", "weapon")}
        if raw_weapon:
            raw.update(raw_weapon)

    if "armour" in data and isinstance(data["armour"], dict):
        base["armourStats"] = _parse_armour_stats(data["armour"])

    if "charm" in data and isinstance(data["charm"], dict):
        base["charmStats"] = data["charm"]

    # Implicit mod type tags for future StatDescriptions join
    if implicit_mod_types:
        base["implicitModTypes"] = implicit_mod_types

    if raw:
        base["raw"] = raw

    return base


# ---------------------------------------------------------------------------
# Runes / Soul Cores parser
# ---------------------------------------------------------------------------

def _extract_mod_texts(subtype_data: dict[str, Any]) -> list[str]:
    """Extract human-readable mod text lines from a rune subtype dict."""
    texts: list[str] = []
    for k, v in subtype_data.items():
        if k.isdigit() and isinstance(v, str) and v.strip():
            texts.append(v.strip())
    return texts


def parse_rune(name: str, data: dict[str, Any]) -> dict[str, Any]:
    effects: dict[str, list[str]] = {}
    item_type = "Unknown"
    rank: int | None = None

    for subtype_key, subtype_data in data.items():
        if not isinstance(subtype_data, dict):
            continue
        mods = _extract_mod_texts(subtype_data)
        effects[subtype_key] = mods
        if item_type == "Unknown":
            item_type = subtype_data.get("type", "Unknown")
        if rank is None and subtype_data.get("rank"):
            r = subtype_data["rank"]
            rank = r[0] if r else None

    return {
        "name": name,
        "type": item_type,
        "rank": rank,
        "effects": effects,
    }


# ---------------------------------------------------------------------------
# Jewels parser
# ---------------------------------------------------------------------------

def _parse_cluster_jewel_skill(skill_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": skill_data.get("name", ""),
        "tag": skill_data.get("tag", ""),
        "stats": skill_data.get("stats", []),
        "enchant": skill_data.get("enchant", []),
    }


def parse_jewels(
    bases_data: dict[str, Any],
    uniques_raw: list[str],
    cluster_data: dict[str, Any],
    mod_jewel_data: dict[str, Any],
    timeless_data: dict[str, list[str]],
) -> dict[str, Any]:

    # Regular bases
    regular_bases: list[dict[str, Any]] = []
    for name, data in bases_data.items():
        req = _parse_requirements(data.get("req", {}))
        tags_dict: dict[str, bool] = data.get("tags", {})
        regular_bases.append({
            "name": name,
            "itemClass": data.get("type", "Jewel"),
            "requirements": req,
            "tags": [k for k, v in tags_dict.items() if v],
        })

    # Unique jewels -- same text format as other uniques
    unique_jewels: list[dict[str, Any]] = []
    for text in uniques_raw:
        if not isinstance(text, str) or not text.strip():
            continue
        parsed = parse_unique_text(text, "jewel")
        if parsed.get("name"):
            unique_jewels.append(parsed)

    # Cluster jewels -- extract jewel types with their skill lists
    cluster_list: list[dict[str, Any]] = []
    jewels_dict = cluster_data.get("jewels", {})
    for jewel_name, jewel_info in jewels_dict.items():
        if not isinstance(jewel_info, dict):
            continue
        skills_raw = jewel_info.get("skills", {})
        cluster_list.append({
            "name": jewel_name,
            "size": jewel_info.get("size", ""),
            "sizeIndex": jewel_info.get("sizeIndex"),
            "minNodes": jewel_info.get("minNodes"),
            "maxNodes": jewel_info.get("maxNodes"),
            "notableCount": len(jewel_info.get("notableIndicies", [])),
            "skills": [_parse_cluster_jewel_skill(s) for s in skills_raw.values()],
        })

    # Timeless jewel summary
    timeless_summary: dict[str, Any] = {
        "description": "Timeless jewels convert nearby passives based on legion type and seed.",
        "source_files": list(timeless_data.keys()),
        "node_count": len(timeless_data.get("nodes_index", [])),
    }
    # Legion passives node count from LegionPassives.json
    lp = timeless_data.get("legion_passives", {})
    if isinstance(lp, dict):
        nodes_list = lp.get("nodes", [])
        if isinstance(nodes_list, list):
            timeless_summary["node_count"] = len(nodes_list)
        # Legion types from additions
        additions = lp.get("additions", {})
        if isinstance(additions, dict):
            timeless_summary["legion_types"] = list(additions.keys()) if additions else []

    # ModJewel entries (crafted jewel mods)
    crafted_mods: list[dict[str, Any]] = []
    id_only_mods: list[str] = []
    for mod_id, mod_data in mod_jewel_data.items():
        if not isinstance(mod_data, dict):
            continue
        # Extract human-readable text
        texts = [v for k, v in mod_data.items() if k.isdigit() and isinstance(v, str) and v.strip()]
        if texts:
            crafted_mods.append({
                "id": mod_id,
                "type": mod_data.get("type", ""),
                "group": mod_data.get("group", ""),
                "level": mod_data.get("level", 0),
                "mods": texts,
            })
        else:
            id_only_mods.append(mod_id)

    return {
        "regular_bases": regular_bases,
        "unique_jewels": unique_jewels,
        "cluster": cluster_list,
        "timeless": timeless_summary,
        "crafted_mods": crafted_mods,
        "_id_only_crafted_mods": id_only_mods,
    }


# ---------------------------------------------------------------------------
# Main build functions
# ---------------------------------------------------------------------------

def build_uniques(slots: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    all_uniques: list[dict[str, Any]] = []
    per_slot: dict[str, int] = {}

    for slot in slots:
        path = RAW_DIR / "Uniques" / f"{slot}.json"
        if not path.exists():
            print(f"  WARNING: missing {path.name}", file=sys.stderr)
            per_slot[slot] = 0
            continue
        raw = load_json(path)
        if not isinstance(raw, list) or len(raw) == 0:
            per_slot[slot] = 0
            continue

        count = 0
        for text in raw:
            if not isinstance(text, str) or not text.strip():
                continue
            parsed = parse_unique_text(text, slot)
            if parsed.get("name"):
                all_uniques.append(parsed)
                count += 1

        if count == 0 and len(raw) > 0:
            print(f"  WARNING: {slot} unique file had {len(raw)} entries but parsed 0 items", file=sys.stderr)
        per_slot[slot] = count

    all_uniques.sort(key=lambda x: x["name"])
    return all_uniques, per_slot


def build_bases(slots: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    all_bases: list[dict[str, Any]] = []
    per_slot: dict[str, int] = {}

    for slot in slots:
        path = RAW_DIR / "Bases" / f"{slot}.json"
        if not path.exists():
            print(f"  WARNING: missing {path.name}", file=sys.stderr)
            per_slot[slot] = 0
            continue
        raw = load_json(path)
        if not isinstance(raw, dict) or len(raw) == 0:
            per_slot[slot] = 0
            continue

        count = 0
        for name, data in raw.items():
            if not isinstance(data, dict):
                continue
            parsed = parse_base(name, data, slot)
            if parsed.get("name"):
                all_bases.append(parsed)
                count += 1

        per_slot[slot] = count

    all_bases.sort(key=lambda x: x["name"])
    return all_bases, per_slot


def build_runes() -> list[dict[str, Any]]:
    path = RAW_DIR / "ModRunes.json"
    raw = load_json(path)
    if not isinstance(raw, dict):
        print("  WARNING: ModRunes.json is not a dict", file=sys.stderr)
        return []
    runes = [parse_rune(name, data) for name, data in raw.items() if isinstance(data, dict)]
    runes.sort(key=lambda r: r["name"])
    return runes


def build_jewels_dataset() -> dict[str, Any]:
    bases_data = load_json(RAW_DIR / "Bases" / "jewel.json")
    uniques_raw = load_json(RAW_DIR / "Uniques" / "jewel.json")
    cluster_data = load_json(RAW_DIR / "ClusterJewels.json")
    mod_jewel_data = load_json(RAW_DIR / "ModJewel.json")

    timeless_dir = RAW_DIR / "TimelessJewelData"
    timeless_data: dict[str, Any] = {}
    lp_path = timeless_dir / "LegionPassives.json"
    if lp_path.exists():
        timeless_data["legion_passives"] = load_json(lp_path)
    ti_path = timeless_dir / "LegionTradeIds.json"
    if ti_path.exists():
        timeless_data["legion_trade_ids"] = load_json(ti_path)
    ni_path = timeless_dir / "NodeIndexMapping.json"
    if ni_path.exists():
        timeless_data["nodes_index"] = load_json(ni_path)

    if not isinstance(bases_data, dict):
        bases_data = {}
    if not isinstance(uniques_raw, list):
        uniques_raw = []

    return parse_jewels(bases_data, uniques_raw, cluster_data, mod_jewel_data, timeless_data)


# ---------------------------------------------------------------------------
# ID-only mod detection
# ---------------------------------------------------------------------------

def find_id_only_slots(slots: list[str]) -> list[str]:
    """
    Report slots whose Bases files have non-empty implicitModTypes but NO
    human-readable 'implicit' text -- these will need a StatDescriptions join
    to resolve mod ids.
    """
    id_only: list[str] = []
    for slot in slots:
        path = RAW_DIR / "Bases" / f"{slot}.json"
        if not path.exists():
            continue
        raw = load_json(path)
        if not isinstance(raw, dict):
            continue
        for name, data in raw.items():
            if not isinstance(data, dict):
                continue
            mod_types = data.get("implicitModTypes", [])
            has_types = any(bool(t) for t in mod_types if isinstance(t, list))
            has_text = bool(data.get("implicit", ""))
            if has_types and not has_text:
                id_only.append(slot)
                break
    return id_only


# ---------------------------------------------------------------------------
# Spot-checks
# ---------------------------------------------------------------------------

def run_spot_checks(
    uniques: list[dict[str, Any]],
    bases: list[dict[str, Any]],
    runes: list[dict[str, Any]],
    jewels: dict[str, Any],
    per_slot_uniques: dict[str, int],
    per_slot_bases: dict[str, int],
) -> None:
    print("\n=== SPOT CHECKS ===\n")

    # 1. Body armour unique
    body_uniques = [u for u in uniques if u["slot"] == "body"]
    if body_uniques:
        u = body_uniques[0]
        print(f"Body armour unique: {u['name']}")
        print(f"  baseType: {u['baseType']}")
        print(f"  implicits ({len(u['implicits'])}): {u['implicits'][:3]}")
        print(f"  explicits ({len(u['explicits'])}): {u['explicits'][:3]}")
        if u.get("source"):
            print(f"  source: {u['source']}")
        if u.get("league"):
            print(f"  league: {u['league']}")
    else:
        print("WARNING: no body armour uniques found")

    print()

    # 2. Ring unique
    ring_uniques = [u for u in uniques if u["slot"] == "ring"]
    if ring_uniques:
        u = ring_uniques[0]
        print(f"Ring unique: {u['name']}")
        print(f"  baseType: {u['baseType']}")
        print(f"  implicits: {u['implicits']}")
        print(f"  explicits ({len(u['explicits'])}): {u['explicits'][:4]}")
    else:
        print("WARNING: no ring uniques found")

    print()

    # 3. Crossbow base
    cb_bases = [b for b in bases if b["slot"] == "crossbow"]
    if cb_bases:
        b = cb_bases[0]
        print(f"Crossbow base: {b['name']}")
        print(f"  itemClass: {b['itemClass']}")
        print(f"  requirements: {b['requirements']}")
        ws = b.get("weaponStats", {})
        print(f"  weaponStats: phys={ws.get('physDamageMin')}-{ws.get('physDamageMax')}, "
              f"aps={ws.get('attackSpeed')}, crit={ws.get('critChance')}, "
              f"range={ws.get('range')}")
    else:
        print("WARNING: no crossbow bases found")

    print()

    # 4. Rune with different weapon vs armour mods
    split_rune = next(
        (r for r in runes
         if len(r["effects"]) >= 2 and len(set(tuple(v) for v in r["effects"].values())) > 1),
        None,
    )
    if split_rune:
        print(f"Rune with weapon/armour split: {split_rune['name']} (type: {split_rune['type']})")
        for subtype, mods in split_rune["effects"].items():
            print(f"  [{subtype}]: {mods}")
    else:
        # Fall back to first rune
        if runes:
            r = runes[0]
            print(f"Rune (no split found, showing first): {r['name']}")
            for subtype, mods in r["effects"].items():
                print(f"  [{subtype}]: {mods[:2]}")

    print()

    # 5. Zero-item slot warnings
    for slot, count in per_slot_uniques.items():
        path = RAW_DIR / "Uniques" / f"{slot}.json"
        if path.exists() and count == 0:
            try:
                raw = load_json(path)
                if isinstance(raw, list) and len(raw) > 0:
                    print(f"WARNING: {slot} unique had {len(raw)} raw entries but 0 parsed")
            except Exception:
                pass

    # 6. Jewels summary
    print(f"Jewels: {len(jewels['regular_bases'])} bases, "
          f"{len(jewels['unique_jewels'])} uniques, "
          f"{len(jewels['cluster'])} cluster types, "
          f"timeless node_count={jewels['timeless'].get('node_count', '?')}")


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PoE2 Items Catalog v0.5</title>
<style>
  :root {
    --bg: #0d0d12;
    --surface: #17171f;
    --surface2: #1f1f2a;
    --border: #2a2a3a;
    --text: #c8c8c8;
    --muted: #888;
    --accent: #74cabf;
    --accent2: #af6025;
    --unique-color: #af6025;
    --base-color: #74cabf;
    --rune-color: #a070e0;
    --jewel-color: #60b0ff;
    --str-color: #e05030;
    --dex-color: #70ff70;
    --int-color: #7070ff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; }
  header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  header h1 { font-size: 18px; color: var(--accent); font-weight: 600; }
  header .counts { color: var(--muted); font-size: 12px; }
  .layout { display: grid; grid-template-columns: 320px 1fr; height: calc(100vh - 50px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .filters { padding: 12px; border-bottom: 1px solid var(--border); display: flex; flex-direction: column; gap: 8px; }
  .filters input, .filters select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 4px; font-size: 13px; width: 100%; }
  .filters input:focus, .filters select:focus { outline: none; border-color: var(--accent); }
  .filter-row { display: flex; gap: 6px; }
  .filter-row select { flex: 1; }
  .item-list { flex: 1; overflow-y: auto; }
  .item-row { padding: 7px 12px; border-bottom: 1px solid var(--border); cursor: pointer; }
  .item-row:hover { background: var(--surface2); }
  .item-row.active { background: var(--surface2); border-left: 3px solid var(--accent); }
  .item-row .item-name { font-weight: 500; font-size: 13px; }
  .item-row .item-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .badge { font-size: 10px; padding: 1px 5px; border-radius: 3px; font-weight: 600; display: inline-block; }
  .badge-unique { background: rgba(175,96,37,0.18); color: var(--unique-color); }
  .badge-base { background: rgba(116,202,191,0.13); color: var(--base-color); }
  .badge-rune { background: rgba(160,112,224,0.15); color: var(--rune-color); }
  .badge-jewel { background: rgba(96,176,255,0.15); color: var(--jewel-color); }
  .detail { flex: 1; overflow-y: auto; padding: 20px; }
  .detail .empty { color: var(--muted); text-align: center; padding: 60px 20px; }
  .d-title { font-size: 22px; color: var(--accent); font-weight: 700; margin-bottom: 4px; }
  .d-sub { font-size: 13px; color: var(--muted); margin-bottom: 16px; }
  .section { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 12px; }
  .section h3 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 10px; }
  .kv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 6px 16px; }
  .kv { display: flex; flex-direction: column; }
  .kv .k { font-size: 11px; color: var(--muted); }
  .kv .v { font-size: 13px; }
  .mod-list { display: flex; flex-direction: column; gap: 3px; }
  .mod { font-size: 13px; color: #b0c8b0; line-height: 1.4; }
  .mod.implicit { color: #b0a0c8; }
  .tag-list { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
  .tag { background: var(--surface2); border: 1px solid var(--border); padding: 2px 7px; border-radius: 12px; font-size: 11px; color: #aaa; }
  .rune-subtype { margin-bottom: 8px; }
  .rune-subtype .st-label { font-size: 11px; color: var(--rune-color); font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
  .no-results { color: var(--muted); padding: 20px; text-align: center; }
  .stat-row { display: flex; justify-content: space-between; font-size: 13px; padding: 2px 0; border-bottom: 1px solid var(--border); }
  .stat-row:last-child { border-bottom: none; }
  .stat-row .stat-k { color: var(--muted); }
  .stat-row .stat-v { font-weight: 500; }
</style>
</head>
<body>
<header>
  <h1>PoE2 Items Catalog <span style="color:var(--muted);font-weight:400">v0.5</span></h1>
  <div class="counts" id="count-display"></div>
</header>
<div class="layout">
  <div class="sidebar">
    <div class="filters">
      <input type="search" id="search" placeholder="Search items, bases, runes..." autocomplete="off">
      <div class="filter-row">
        <select id="filter-kind">
          <option value="">All types</option>
          <option value="unique">Uniques</option>
          <option value="base">Bases</option>
          <option value="rune">Runes</option>
          <option value="jewel">Jewels</option>
        </select>
        <select id="filter-slot">
          <option value="">All slots</option>
        </select>
      </div>
      <select id="filter-cat">
        <option value="">All categories</option>
        <option value="weapon">Weapon</option>
        <option value="armour">Armour</option>
        <option value="jewellery">Jewellery</option>
        <option value="flask">Flask</option>
        <option value="jewel">Jewel</option>
      </select>
    </div>
    <div class="item-list" id="item-list"></div>
  </div>
  <div class="detail" id="detail">
    <div class="empty">Select an item to view details</div>
  </div>
</div>

<script>
const UNIQUES = __UNIQUES__;
const BASES = __BASES__;
const RUNES = __RUNES__;
const JEWELS = __JEWELS__;
const COUNTS = __COUNTS__;

// Build a flat list of display items
const ALL = [];
UNIQUES.forEach(u => ALL.push({...u, _kind:'unique', _cat: slotCat(u.slot)}));
BASES.forEach(b => ALL.push({...b, _kind:'base'}));
RUNES.forEach(r => ALL.push({...r, _kind:'rune', slot:'', _cat:'rune'}));
JEWELS.regular_bases.forEach(j => ALL.push({...j, _kind:'jewel', _cat:'jewel', slot:'jewel'}));
JEWELS.unique_jewels.forEach(j => ALL.push({...j, _kind:'jewel', _cat:'jewel', slot:'jewel', _sub:'unique'}));

function slotCat(slot) {
  const w = ['bow','crossbow','dagger','claw','flail','mace','sceptre','spear','staff','sword','wand','talisman'];
  const a = ['body','boots','gloves','helmet','shield','focus'];
  const j = ['amulet','belt','ring','quiver'];
  if (w.includes(slot)) return 'weapon';
  if (a.includes(slot)) return 'armour';
  if (j.includes(slot)) return 'jewellery';
  if (slot === 'jewel') return 'jewel';
  if (slot === 'flask') return 'flask';
  return 'other';
}

// Populate slot filter
const allSlots = [...new Set(ALL.map(x => x.slot).filter(Boolean))].sort();
const slotSel = document.getElementById('filter-slot');
allSlots.forEach(s => {
  const o = document.createElement('option');
  o.value = s; o.textContent = s;
  slotSel.appendChild(o);
});

// Count display
document.getElementById('count-display').textContent =
  `${COUNTS.uniques} uniques | ${COUNTS.bases} bases | ${COUNTS.runes} runes | ${COUNTS.jewels} jewels`;

let activeItem = null;

function renderList() {
  const q = document.getElementById('search').value.toLowerCase();
  const kindF = document.getElementById('filter-kind').value;
  const slotF = document.getElementById('filter-slot').value;
  const catF = document.getElementById('filter-cat').value;

  const filtered = ALL.filter(x => {
    if (kindF && x._kind !== kindF && !(kindF === 'jewel' && x._kind === 'jewel')) return false;
    if (slotF && x.slot !== slotF) return false;
    if (catF) {
      const cat = x._cat || x.category || slotCat(x.slot || '');
      if (cat !== catF) return false;
    }
    if (q) {
      const text = (x.name + ' ' + (x.baseType||'') + ' ' + (x.slot||'') + ' ' + (x.itemClass||'')).toLowerCase();
      if (!text.includes(q)) return false;
    }
    return true;
  });

  const list = document.getElementById('item-list');
  list.innerHTML = '';
  if (!filtered.length) {
    list.innerHTML = '<div class="no-results">No results</div>';
    return;
  }
  filtered.forEach(x => {
    const div = document.createElement('div');
    div.className = 'item-row' + (activeItem && activeItem.name === x.name && activeItem._kind === x._kind ? ' active' : '');
    const cat = x._cat || x.category || slotCat(x.slot || '');
    div.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px">
        <span class="item-name">${esc(x.name)}</span>
        <span class="badge badge-${x._kind}">${x._kind}</span>
      </div>
      <div class="item-meta">${esc(x.slot || '')} ${x.slot ? '|' : ''} ${esc(cat)}</div>`;
    div.addEventListener('click', () => { activeItem = x; renderList(); renderDetail(x); });
    list.appendChild(div);
  });
}

function renderDetail(x) {
  const d = document.getElementById('detail');
  if (x._kind === 'unique') { d.innerHTML = renderUnique(x); return; }
  if (x._kind === 'base') { d.innerHTML = renderBase(x); return; }
  if (x._kind === 'rune') { d.innerHTML = renderRune(x); return; }
  if (x._kind === 'jewel') { d.innerHTML = renderJewelItem(x); return; }
}

function renderUnique(u) {
  const reqs = u.requirements || {};
  const reqParts = [];
  if (reqs.level) reqParts.push(`Level ${reqs.level}`);
  if (reqs.str) reqParts.push(`<span style="color:var(--str-color)">${reqs.str} Str</span>`);
  if (reqs.dex) reqParts.push(`<span style="color:var(--dex-color)">${reqs.dex} Dex</span>`);
  if (reqs.int) reqParts.push(`<span style="color:var(--int-color)">${reqs.int} Int</span>`);
  const implicits = (u.implicits||[]).map(m => `<div class="mod implicit">${esc(m)}</div>`).join('');
  const explicits = (u.explicits||[]).map(m => `<div class="mod">${esc(m)}</div>`).join('');
  const tags = (u.tags||[]).map(t => `<span class="tag">${esc(t)}</span>`).join('');
  return `
    <div class="d-title" style="color:var(--unique-color)">${esc(u.name)}</div>
    <div class="d-sub">${esc(u.baseType||'')} &mdash; ${esc(u.slot)}</div>
    <div class="section"><h3>Properties</h3>
      <div class="kv-grid">
        ${reqParts.length ? `<div class="kv"><span class="k">Requirements</span><span class="v">${reqParts.join(', ')}</span></div>` : ''}
        ${u.source ? `<div class="kv"><span class="k">Source</span><span class="v" style="font-size:12px">${esc(u.source)}</span></div>` : ''}
        ${u.league ? `<div class="kv"><span class="k">League</span><span class="v">${esc(u.league)}</span></div>` : ''}
        ${u.limitedTo ? `<div class="kv"><span class="k">Limited To</span><span class="v">${u.limitedTo}</span></div>` : ''}
        ${u.sockets ? `<div class="kv"><span class="k">Sockets</span><span class="v">${esc(u.sockets)}</span></div>` : ''}
      </div>
      ${tags ? `<div class="tag-list">${tags}</div>` : ''}
    </div>
    ${implicits ? `<div class="section"><h3>Implicits</h3><div class="mod-list">${implicits}</div></div>` : ''}
    ${explicits ? `<div class="section"><h3>Explicit Mods</h3><div class="mod-list">${explicits}</div></div>` : ''}
    ${u.grantsSkill ? `<div class="section"><h3>Grants Skill</h3><div class="mod-list">${(u.grantsSkill||[]).map(s=>`<div class="mod">${esc(s)}</div>`).join('')}</div></div>` : ''}`;
}

function renderBase(b) {
  const reqs = b.requirements || {};
  const ws = b.weaponStats || {};
  const as_ = b.armourStats || {};
  const cs = b.charmStats || {};
  const tags = (b.tags||[]).map(t => `<span class="tag">${esc(t)}</span>`).join('');
  const implicits = (b.implicits||[]).map(m => `<div class="mod implicit">${esc(m)}</div>`).join('');

  let statsHtml = '';
  if (Object.keys(ws).length) {
    const rows = [
      ws.physDamageMin != null ? ['Physical Damage', `${ws.physDamageMin}-${ws.physDamageMax}`] : null,
      ws.critChance != null ? ['Critical Hit Chance', `${ws.critChance}%`] : null,
      ws.attackSpeed != null ? ['Attacks per Second', ws.attackSpeed] : null,
      ws.range != null ? ['Range', ws.range] : null,
      ws.reloadTime != null ? ['Reload Time', `${ws.reloadTime}s`] : null,
    ].filter(Boolean);
    statsHtml = `<div class="section"><h3>Weapon Stats</h3>${rows.map(([k,v]) =>
      `<div class="stat-row"><span class="stat-k">${k}</span><span class="stat-v">${v}</span></div>`).join('')}</div>`;
  }
  if (Object.keys(as_).length) {
    const rows = [
      as_.armour != null ? ['Armour', as_.armour] : null,
      as_.evasion != null ? ['Evasion', as_.evasion] : null,
      as_.energyShield != null ? ['Energy Shield', as_.energyShield] : null,
      as_.ward != null ? ['Ward', as_.ward] : null,
      as_.block != null ? ['Block Chance', `${as_.block}%`] : null,
    ].filter(Boolean);
    statsHtml = `<div class="section"><h3>Defence Stats</h3>${rows.map(([k,v]) =>
      `<div class="stat-row"><span class="stat-k">${k}</span><span class="stat-v">${v}</span></div>`).join('')}</div>`;
  }
  if (Object.keys(cs).length) {
    const parts = Object.entries(cs).map(([k,v]) => `<div class="stat-row"><span class="stat-k">${esc(k)}</span><span class="stat-v">${esc(String(v))}</span></div>`).join('');
    statsHtml = `<div class="section"><h3>Charm Stats</h3>${parts}</div>`;
  }

  return `
    <div class="d-title">${esc(b.name)}</div>
    <div class="d-sub">${esc(b.itemClass||'')}${b.subType ? ' &mdash; ' + esc(b.subType) : ''} &mdash; ${esc(b.slot)}</div>
    <div class="section"><h3>Requirements</h3>
      <div class="kv-grid">
        ${reqs.level ? `<div class="kv"><span class="k">Level</span><span class="v">${reqs.level}</span></div>` : ''}
        ${reqs.str ? `<div class="kv"><span class="k">Strength</span><span class="v" style="color:var(--str-color)">${reqs.str}</span></div>` : ''}
        ${reqs.dex ? `<div class="kv"><span class="k">Dexterity</span><span class="v" style="color:var(--dex-color)">${reqs.dex}</span></div>` : ''}
        ${reqs.int ? `<div class="kv"><span class="k">Intelligence</span><span class="v" style="color:var(--int-color)">${reqs.int}</span></div>` : ''}
        ${b.socketLimit != null ? `<div class="kv"><span class="k">Socket Limit</span><span class="v">${b.socketLimit}</span></div>` : ''}
      </div>
      ${tags ? `<div class="tag-list">${tags}</div>` : ''}
    </div>
    ${statsHtml}
    ${implicits ? `<div class="section"><h3>Implicit</h3><div class="mod-list">${implicits}</div></div>` : ''}`;
}

function renderRune(r) {
  const subtypes = Object.entries(r.effects||{});
  const effectsHtml = subtypes.map(([st, mods]) => `
    <div class="rune-subtype">
      <div class="st-label">${esc(st)}</div>
      ${mods.map(m => `<div class="mod">${esc(m)}</div>`).join('')}
    </div>`).join('');
  return `
    <div class="d-title" style="color:var(--rune-color)">${esc(r.name)}</div>
    <div class="d-sub">${esc(r.type)}${r.rank != null ? ' &mdash; Rank ' + r.rank : ''}</div>
    <div class="section"><h3>Effects by Item Type</h3>${effectsHtml || '<div class="mod" style="color:var(--muted)">No effects parsed</div>'}</div>`;
}

function renderJewelItem(j) {
  const reqs = j.requirements || {};
  const tags = (j.tags||[]).map(t => `<span class="tag">${esc(t)}</span>`).join('');
  const implicits = (j.implicits||[]).map(m => `<div class="mod implicit">${esc(m)}</div>`).join('');
  const explicits = (j.explicits||[]).map(m => `<div class="mod">${esc(m)}</div>`).join('');
  const isUnique = !!j._sub;
  return `
    <div class="d-title" style="color:var(--jewel-color)">${esc(j.name)}</div>
    <div class="d-sub">${isUnique ? 'Unique Jewel' : 'Base Jewel'} &mdash; ${esc(j.itemClass||'Jewel')}</div>
    ${tags ? `<div class="section"><h3>Tags</h3><div class="tag-list">${tags}</div></div>` : ''}
    ${implicits ? `<div class="section"><h3>Implicits</h3><div class="mod-list">${implicits}</div></div>` : ''}
    ${explicits ? `<div class="section"><h3>Mods</h3><div class="mod-list">${explicits}</div></div>` : ''}`;
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

['search','filter-kind','filter-slot','filter-cat'].forEach(id =>
  document.getElementById(id).addEventListener('input', renderList));

renderList();
</script>
</body>
</html>
"""


def render_html(
    uniques: list[dict[str, Any]],
    bases: list[dict[str, Any]],
    runes: list[dict[str, Any]],
    jewels: dict[str, Any],
    counts: dict[str, Any],
) -> str:
    html = HTML_TEMPLATE
    # Inline data -- strip internal _raw keys from jewels before embedding
    jewels_embed = {
        k: v for k, v in jewels.items() if not k.startswith("_")
    }
    html = html.replace("__UNIQUES__", json.dumps(uniques, separators=(",", ":")))
    html = html.replace("__BASES__", json.dumps(bases, separators=(",", ":")))
    html = html.replace("__RUNES__", json.dumps(runes, separators=(",", ":")))
    html = html.replace("__JEWELS__", json.dumps(jewels_embed, separators=(",", ":")))
    html = html.replace("__COUNTS__", json.dumps(counts, separators=(",", ":")))
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build PoE2 v0.5 item layer datasets")
    parser.add_argument("--skip-download", action="store_true",
                        help="Use cached data/_raw/ files instead of re-downloading")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_download:
        download_all()
    else:
        print("=== Skipping download, using cached data/_raw/ ===")

    print("\n=== Building datasets ===")

    # Uniques
    uniques, per_slot_uniques = build_uniques(ITEM_SLOTS)
    print(f"  Uniques total: {len(uniques)}")
    for slot, c in sorted(per_slot_uniques.items()):
        if c:
            print(f"    {slot}: {c}")

    # Bases
    bases, per_slot_bases = build_bases(ITEM_SLOTS)
    print(f"  Bases total: {len(bases)}")
    for slot, c in sorted(per_slot_bases.items()):
        if c:
            print(f"    {slot}: {c}")

    # Runes
    runes = build_runes()
    rune_types: dict[str, int] = {}
    for r in runes:
        rune_types[r["type"]] = rune_types.get(r["type"], 0) + 1
    print(f"  Runes/soul cores total: {len(runes)} -- {rune_types}")

    # Jewels
    jewels = build_jewels_dataset()
    jewel_counts = {
        "bases": len(jewels["regular_bases"]),
        "uniques": len(jewels["unique_jewels"]),
        "cluster_types": len(jewels["cluster"]),
        "crafted_mods": len(jewels.get("crafted_mods", [])),
    }
    print(f"  Jewels: {jewel_counts}")

    # ID-only mod detection
    id_only_slots = find_id_only_slots(ITEM_SLOTS)
    if id_only_slots:
        print(f"\n  NOTE: slots with id-only implicit mods (need StatDescriptions join): {id_only_slots}")
    else:
        print("  All base implicit mods resolved to human-readable text.")

    counts: dict[str, Any] = {
        "uniques": len(uniques),
        "bases": len(bases),
        "runes": len(runes),
        "jewels": sum(jewel_counts.values()),
        "per_slot_uniques": per_slot_uniques,
        "per_slot_bases": per_slot_bases,
        "rune_type_breakdown": rune_types,
        "jewel_detail": jewel_counts,
    }

    # Write outputs
    print("\n=== Writing outputs ===")

    uniques_out = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        "count": len(uniques),
        "per_slot": per_slot_uniques,
        "items": uniques,
    }
    write_json(DATA_DIR / "uniques.json", uniques_out)

    bases_out = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        "count": len(bases),
        "per_slot": per_slot_bases,
        "items": bases,
    }
    write_json(DATA_DIR / "bases.json", bases_out)

    runes_out = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        "count": len(runes),
        "type_breakdown": rune_types,
        "items": runes,
    }
    write_json(DATA_DIR / "runes.json", runes_out)

    jewels_out = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        **{k: v for k, v in jewels.items() if not k.startswith("_")},
    }
    write_json(DATA_DIR / "jewels.json", jewels_out)

    index = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        "counts": {
            "uniques": len(uniques),
            "bases": len(bases),
            "runes": len(runes),
            "jewel_bases": jewel_counts["bases"],
            "jewel_uniques": jewel_counts["uniques"],
            "cluster_types": jewel_counts["cluster_types"],
            "rune_types": rune_types,
        },
        "files": [
            "data/uniques.json",
            "data/bases.json",
            "data/runes.json",
            "data/jewels.json",
            "pages/items_catalog.html",
        ],
        "id_only_slots": id_only_slots,
        "notes": (
            "id_only_slots lists base item slots whose implicit mods are stored as "
            "stat-id references only and need a StatDescriptions join to resolve to "
            "human-readable text. All other mods are already in text form."
        ),
    }
    write_json(DATA_DIR / "items_index.json", index)

    # HTML
    html_content = render_html(uniques, bases, runes, jewels, counts)
    html_path = PAGES_DIR / "items_catalog.html"
    try:
        html_path.write_text(html_content, encoding="utf-8")
        print(f"  wrote {html_path.relative_to(REPO_ROOT)} ({html_path.stat().st_size:,}B)")
    except OSError as e:
        print(f"  ERROR writing HTML: {e}", file=sys.stderr)

    # Spot checks
    run_spot_checks(uniques, bases, runes, jewels, per_slot_uniques, per_slot_bases)

    print("\n=== Done ===")
    print(f"Counts: uniques={len(uniques)}, bases={len(bases)}, runes={len(runes)}, "
          f"jewel_bases={jewel_counts['bases']}, jewel_uniques={jewel_counts['uniques']}, "
          f"cluster_types={jewel_counts['cluster_types']}")


if __name__ == "__main__":
    main()
