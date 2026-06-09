#!/usr/bin/env python3
"""
build_corruptions.py -- PoE2 vaal/corruption implicit dataset builder

Downloads ModCorrupted.json from repoe-fork/pob-data and produces
data/corruptions.json keyed by item class for use in build tools.

Usage:
    python3 scripts/build_corruptions.py [--skip-download]

Output: data/corruptions.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
RAW_DIR = REPO_ROOT / "data" / "_raw"
OUT_FILE = REPO_ROOT / "data" / "corruptions.json"

BASE_URL = "https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2"
MOD_CORRUPTED_URL = f"{BASE_URL}/ModCorrupted.json"
VERSION = "0.5"

# ---------------------------------------------------------------------------
# PoB uses snake_case tag names. Map them to human-readable item class labels.
# Tags that are sub-categories of armour type are also included so the UI can
# display the correct defence-type breakdown when relevant.
# ---------------------------------------------------------------------------
TAG_TO_LABEL: dict[str, str] = {
    "amulet":           "Amulet",
    "ring":             "Ring",
    "belt":             "Belt",
    "helmet":           "Helmet",
    "body_armour":      "Body Armour",
    "gloves":           "Gloves",
    "boots":            "Boots",
    "shield":           "Shield",
    "focus":            "Focus",
    "quiver":           "Quiver",
    # armour sub-types (defence combos)
    "armour":           "Armour (any)",
    "str_armour":       "Armour (Str -- pure armour)",
    "dex_armour":       "Armour (Dex -- pure evasion)",
    "int_armour":       "Armour (Int -- pure ES)",
    "str_dex_armour":   "Armour (Str/Dex -- armour+evasion)",
    "str_int_armour":   "Armour (Str/Int -- armour+ES)",
    "dex_int_armour":   "Armour (Dex/Int -- evasion+ES)",
    # weapons
    "weapon":           "Weapon (any)",
    "one_hand_weapon":  "One-Handed Weapon",
    "two_hand_weapon":  "Two-Handed Weapon",
    "bow":              "Bow",
    "crossbow":         "Crossbow",
    "wand":             "Wand",
    "sceptre":          "Sceptre",
    "staff":            "Staff",
    "warstaff":         "Warstaff",
    "mace":             "Mace",
    "axe":              "Axe",
    "sword":            "Sword",
    "dagger":           "Dagger",
    "spear":            "Spear",
    "flail":            "Flail",
    # misc
    "jewel":            "Jewel",
}

# Canonical display order for the by_item_class output.
DISPLAY_ORDER: list[str] = [
    "Amulet", "Ring", "Belt",
    "Helmet", "Body Armour", "Gloves", "Boots",
    "Shield", "Focus", "Quiver",
    "Armour (any)",
    "Armour (Str -- pure armour)", "Armour (Dex -- pure evasion)",
    "Armour (Int -- pure ES)", "Armour (Str/Dex -- armour+evasion)",
    "Armour (Str/Int -- armour+ES)", "Armour (Dex/Int -- evasion+ES)",
    "Weapon (any)",
    "One-Handed Weapon", "Two-Handed Weapon",
    "Bow", "Crossbow", "Wand", "Sceptre",
    "Staff", "Warstaff",
    "Mace", "Axe", "Sword", "Dagger", "Spear", "Flail",
    "Jewel",
    "Unknown (no active weight)",
]


@dataclass
class CorruptionEntry:
    mod_id: str
    text: str
    weight: int
    mod_tags: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-fsSL", "--max-time", "30", "-A", "build-corruptions/1.0",
           "-o", str(dest), url]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {result.stderr.decode()}")
    print(f"  fetched {url} -> {dest.name} ({dest.stat().st_size:,}B)")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def extract_text(mod: dict[str, Any]) -> str:
    """
    Pull the human-readable stat line(s) from a mod entry.
    PoB encodes them as integer-keyed fields ("1", "2", ...).
    Fall back to tradeHashes values if those are absent.
    """
    lines: list[str] = []
    i = 1
    while str(i) in mod:
        lines.append(mod[str(i)])
        i += 1
    if not lines:
        for trade_lines in mod.get("tradeHashes", {}).values():
            lines.extend(trade_lines)
    return "\n".join(lines) if lines else ""


def build_by_class(raw: dict[str, Any]) -> tuple[dict[str, list[dict]], list[str]]:
    """
    Returns (by_item_class dict, list of mod_ids that had no active weight key).

    Heuristic for item class membership:
      - weightKey / weightVal encode spawn tag -> weight pairs.
      - A tag is "active" when its weight > 0.
      - The tag "default" is excluded; it acts as a fallback/catch-all zero slot.
      - SpecialCorruption* mods with an empty weightKey list have no spawn tag in
        the data at all -- they are noted in the "unknown" bucket and documented in
        notes rather than guessed.
    """
    by_class: dict[str, list[dict]] = {}
    no_weight_ids: list[str] = []

    for mod_id, mod in raw.items():
        text = extract_text(mod)
        weight_keys: list[str] = mod.get("weightKey", [])
        weight_vals: list[int] = mod.get("weightVal", [])
        mod_tags: list[str] = mod.get("modTags", [])

        active: list[tuple[str, int]] = [
            (k, v)
            for k, v in zip(weight_keys, weight_vals)
            if k != "default" and v > 0
        ]

        if not active:
            no_weight_ids.append(mod_id)
            bucket = "Unknown (no active weight)"
            by_class.setdefault(bucket, []).append({
                "mod_id": mod_id,
                "text": text,
                "weight": 0,
                "mod_tags": mod_tags,
                "flag": "no_active_weight_in_source",
            })
            continue

        for tag, weight in active:
            label = TAG_TO_LABEL.get(tag, f"unknown_tag:{tag}")
            entry = {
                "mod_id": mod_id,
                "text": text,
                "weight": weight,
                "mod_tags": mod_tags,
            }
            by_class.setdefault(label, []).append(entry)

    # Sort entries within each class by weight desc, then mod_id for stability
    for label in by_class:
        by_class[label].sort(key=lambda e: (-e["weight"], e["mod_id"]))

    # Reorder keys by canonical display order
    ordered: dict[str, list[dict]] = {}
    seen = set(by_class.keys())
    for label in DISPLAY_ORDER:
        if label in seen:
            ordered[label] = by_class[label]
    # Append any unexpected labels not in DISPLAY_ORDER
    for label in by_class:
        if label not in ordered:
            ordered[label] = by_class[label]

    return ordered, no_weight_ids


def build_notes(no_weight_ids: list[str]) -> str:
    lines = [
        "Item class membership is derived from weightKey/weightVal pairs in ModCorrupted.json. "
        "A tag is considered active when its weight > 0; the 'default' tag is always excluded. "
        "Armour sub-type tags (str_armour, dex_armour, etc.) reflect PoB's defence-combo encoding "
        "and are separate from the generic 'armour' tag which covers all slot armour pieces. "
        "The 'weapon' tag covers all weapon slots; specific weapon-type tags are more granular. ",
    ]
    if no_weight_ids:
        lines.append(
            f"The following {len(no_weight_ids)} mod(s) have no active weight in the source data "
            f"(all weights are 0 or the weightKey list is empty) and are bucketed under "
            f"'Unknown (no active weight)': {', '.join(sorted(no_weight_ids))}. "
            "These may be disabled/unreleased corruptions or PoB placeholders."
        )
    lines.append(
        "Unique-specific transforming corruption outcomes (e.g. alternate unique forms) "
        "are NOT encoded in ModCorrupted.json or the Uniques/*.json files in this PoB data export. "
        "The Uniques/*.json files store item stat text as raw strings with no corruption-transform "
        "field; no unique-specific corruption data is derivable from this source."
    )
    return " ".join(lines)


def print_report(by_class: dict[str, list[dict]], no_weight_ids: list[str]) -> None:
    print("\n=== Corruption dataset report ===")
    print(f"{'Item class':<45} {'Count':>5}")
    print("-" * 52)
    total = 0
    for label, entries in by_class.items():
        c = len(entries)
        total += c
        print(f"  {label:<43} {c:>5}")
    print("-" * 52)
    print(f"  {'TOTAL (class-slot rows)':<43} {total:>5}")
    print(f"\nUnique mod IDs in source: 127")
    print(f"Mods with no active weight (id-only / unresolved): {len(no_weight_ids)}")
    if no_weight_ids:
        for mid in sorted(no_weight_ids):
            print(f"  {mid}")

    print("\n=== Sample corruption lines ===")
    samples = {
        "Amulet": 3,
        "Ring": 3,
        "Bow": 3,
        "Jewel": 3,
    }
    for label, n in samples.items():
        entries = by_class.get(label, [])
        print(f"\n  {label}:")
        for e in entries[:n]:
            print(f"    [{e['weight']}w] {e['text']!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build PoE2 corruption implicit dataset")
    parser.add_argument("--skip-download", action="store_true",
                        help="Use cached _raw/ModCorrupted.json if present")
    args = parser.parse_args()

    raw_path = RAW_DIR / "ModCorrupted.json"

    if not args.skip_download or not raw_path.exists():
        print("=== Downloading ModCorrupted.json ===")
        download_file(MOD_CORRUPTED_URL, raw_path)
    else:
        print(f"  using cached {raw_path}")

    raw: dict[str, Any] = load_json(raw_path)
    print(f"  loaded {len(raw)} corruption mod entries")

    by_class, no_weight_ids = build_by_class(raw)

    output = {
        "version": VERSION,
        "source": "repoe-fork/pob-data poe2/ModCorrupted.json",
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "by_item_class": by_class,
        "unique_corruptions": None,
        "notes": build_notes(no_weight_ids),
    }

    try:
        OUT_FILE.write_text(json.dumps(output, indent=2))
    except OSError as exc:
        raise SystemExit(f"Cannot write {OUT_FILE}: {exc}") from exc

    size_kb = OUT_FILE.stat().st_size / 1024
    print(f"\n  wrote {OUT_FILE} ({size_kb:.1f} KB)")

    print_report(by_class, no_weight_ids)


if __name__ == "__main__":
    main()
