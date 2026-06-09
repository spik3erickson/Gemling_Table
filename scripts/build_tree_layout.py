#!/usr/bin/env python3
"""
build_tree_layout.py
Reads data/_raw/tree.json (GGG passive tree export) and writes
data/tree_layout.json — a trimmed layout file for the tree.html viewer.

Per-node output:
  id       - string key used in the export (may be numeric string or "root")
  name     - display name
  x, y     - world-space position (float)
  kind     - "keystone" | "notable" | "mastery" | "jewel" | "normal"
  asc      - true if ascendancyId is set
  stats    - cleaned stat strings (markup stripped)
  out      - list of connected node id strings

Run from the repo root:
  python3 scripts/build_tree_layout.py
"""

import json
import re
import sys
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "_raw" / "tree.json"
OUT_PATH = Path(__file__).parent.parent / "data" / "tree_layout.json"


def strip_markup(text: str) -> str:
    """Remove PoE passive tree markup from stat strings.

    Handles:
      [Key|Display]   -> Display
      <underline>{text} -> text
      <tag>text</tag> -> text (generic)
    """
    # [Key|Display] -> Display
    text = re.sub(r'\[([^\]|]+)\|([^\]]+)\]', r'\2', text)
    # [Key] alone (no pipe) -> Key
    text = re.sub(r'\[([^\]|]+)\]', r'\1', text)
    # <underline>{text} -> text
    text = re.sub(r'<\w+>\{([^}]*)\}', r'\1', text)
    # <tag>text</tag>
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def classify(node: dict) -> str:
    if node.get('isKeystone'):
        return 'keystone'
    if node.get('isNotable'):
        return 'notable'
    if node.get('isMastery'):
        return 'mastery'
    if node.get('isJewelSocket'):
        return 'jewel'
    return 'normal'


def main() -> None:
    if not RAW_PATH.exists():
        print(f"ERROR: {RAW_PATH} not found. Run the download step first.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {RAW_PATH} …")
    with RAW_PATH.open(encoding='utf-8') as fh:
        raw = json.load(fh)

    nodes_raw: dict = raw['nodes']
    bounds = {
        'min_x': raw['min_x'],
        'min_y': raw['min_y'],
        'max_x': raw['max_x'],
        'max_y': raw['max_y'],
    }

    # Build a fast lookup of skill int -> string key for edges
    # Some edge 'to' values are ints, node keys are strings
    skill_to_key: dict[int, str] = {}
    for key, node in nodes_raw.items():
        skill = node.get('skill')
        if skill is not None:
            skill_to_key[int(skill)] = key

    missing_xy = 0
    counts: dict[str, int] = {
        'keystone': 0, 'notable': 0, 'mastery': 0, 'jewel': 0, 'normal': 0,
        'asc': 0, 'missing_xy': 0,
    }

    layout_nodes = []
    for key, node in nodes_raw.items():
        x = node.get('x')
        y = node.get('y')
        if x is None or y is None:
            missing_xy += 1
            counts['missing_xy'] += 1
            # Place at origin as fallback (root node has no xy)
            x, y = 0.0, 0.0

        kind = classify(node)
        counts[kind] += 1

        is_asc = bool(node.get('ascendancyId'))
        if is_asc:
            counts['asc'] += 1

        raw_stats = node.get('stats') or []
        stats = [strip_markup(s) for s in raw_stats if s.strip()]

        # Build out list: node.out are string references (already string keys)
        out = list(node.get('out') or [])

        entry = {
            'id': key,
            'name': node.get('name') or '',
            'x': round(float(x), 2),
            'y': round(float(y), 2),
            'kind': kind,
            'asc': is_asc,
            'stats': stats,
            'out': out,
        }
        layout_nodes.append(entry)

    output = {
        'bounds': bounds,
        'nodes': layout_nodes,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open('w', encoding='utf-8') as fh:
        json.dump(output, fh, separators=(',', ':'))

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"\nWrote {OUT_PATH}")
    print(f"  Size: {size_kb:.1f} KB ({OUT_PATH.stat().st_size:,} bytes)")
    print(f"  Total nodes: {len(layout_nodes)}")
    print(f"  Kind breakdown:")
    for k in ('keystone', 'notable', 'mastery', 'jewel', 'normal'):
        print(f"    {k:12s}: {counts[k]}")
    print(f"  Ascendancy nodes: {counts['asc']}")
    print(f"  Missing x/y (placed at 0,0): {counts['missing_xy']}")


if __name__ == '__main__':
    main()
