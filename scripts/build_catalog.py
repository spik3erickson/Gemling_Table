#!/usr/bin/env python3
"""
build_catalog.py — PoE2 v0.5 gem catalog builder

Downloads raw PoB data export files from repoe-fork/pob-data, normalizes them
into clean JSON datasets, computes support compatibility, and renders a static
HTML browser.

Usage:
    python3 docs/poe2/build_catalog.py [--skip-download]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
RAW_DIR = SCRIPT_DIR / "_raw"
OUT_DIR = SCRIPT_DIR

BASE_URL = "https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2"

ACTIVE_FILES = [
    "Skills/act_dex.json",
    "Skills/act_int.json",
    "Skills/act_str.json",
    "Skills/minion.json",
    "Skills/other.json",
    "Skills/spectre.json",
]
SUPPORT_FILES = [
    "Skills/sup_dex.json",
    "Skills/sup_int.json",
    "Skills/sup_str.json",
]
GEMS_FILE = "Gems.json"

GLOBAL_LUA_URL = (
    "https://raw.githubusercontent.com/PathOfBuildingCommunity/PathOfBuilding-PoE2"
    "/dev/src/Data/Global.lua"
)

# ---------------------------------------------------------------------------
# SkillType enum — embedded from Global.lua (fetched during download phase)
# Populated by parse_skill_type_enum()
# ---------------------------------------------------------------------------
SKILL_TYPE_ENUM: dict[int, str] = {}


def download_file(url: str, dest: Path, ua: str = "build-catalog-script/1.0") -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-fsSL", "--max-time", "30", "-A", ua, "-o", str(dest), url]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {result.stderr.decode()}")
    print(f"  fetched {url} -> {dest.name} ({dest.stat().st_size:,}B)")


def download_all() -> None:
    print("=== Downloading raw data ===")
    for rel in [GEMS_FILE] + ACTIVE_FILES + SUPPORT_FILES:
        dest = RAW_DIR / Path(rel).name
        download_file(f"{BASE_URL}/{rel}", dest)
    lua_dest = RAW_DIR / "Global.lua"
    download_file(GLOBAL_LUA_URL, lua_dest)


def parse_skill_type_enum(lua_path: Path) -> dict[int, str]:
    """
    Parse `SkillType = { Name = number, ... }` from Global.lua.
    Returns {number: Name}.
    """
    result: dict[int, str] = {}
    try:
        text = lua_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  WARNING: could not read Global.lua: {e}", file=sys.stderr)
        return result

    in_block = False
    for line in text.splitlines():
        if re.match(r"^SkillType\s*=\s*\{", line):
            in_block = True
            continue
        if in_block:
            if line.strip() == "}":
                break
            m = re.match(r"^\s*(\w+)\s*=\s*(\d+)", line)
            if m:
                result[int(m.group(2))] = m.group(1)
    print(f"  parsed {len(result)} SkillType enum entries")
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(f"ERROR: cannot read {path}: {e}")


def skill_type_names(ids: list[int]) -> list[str]:
    return [SKILL_TYPE_ENUM.get(i, str(i)) for i in ids]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SkillGem:
    id: str
    gameId: str
    name: str
    gemFamily: str
    gemType: str
    attribute: str
    tier: int
    naturalMaxLevel: int
    reqStr: int
    reqInt: int
    reqDex: int
    tags: dict[str, bool]
    tagString: str
    grantedEffectId: str
    skillTypes: list[int]
    skillTypeNames: list[str]
    description: str


@dataclass
class SupportGem:
    id: str
    gameId: str
    name: str
    gemFamily: str
    tier: int
    reqStr: int
    reqInt: int
    reqDex: int
    tags: dict[str, bool]
    tagString: str
    grantedEffectId: str
    requireSkillTypes: list[int]
    excludeSkillTypes: list[int]
    addSkillTypes: list[int]
    requireSkillTypeNames: list[str]
    excludeSkillTypeNames: list[str]
    description: str


def derive_attribute(req_str: int, req_int: int, req_dex: int) -> str:
    attrs = []
    if req_str > 0:
        attrs.append("str")
    if req_int > 0:
        attrs.append("int")
    if req_dex > 0:
        attrs.append("dex")
    if len(attrs) == 0:
        return "none"
    if len(attrs) == 1:
        return attrs[0]
    return "/".join(attrs)


# ---------------------------------------------------------------------------
# Build skill_gems.json
# ---------------------------------------------------------------------------

def build_skill_gems(
    gems: dict[str, Any],
    active_ges: dict[str, Any],
) -> tuple[list[SkillGem], list[str]]:
    """
    Returns (skill_gem_list, unresolved_gem_ids).
    Skill gems = everything in Gems.json with gemType != "Support".
    """
    skill_list: list[SkillGem] = []
    unresolved: list[str] = []

    for gem_id, gem in gems.items():
        if gem.get("gemType") == "Support":
            continue

        ge_id = gem.get("grantedEffectId", "")
        ge = active_ges.get(ge_id)
        if ge is None:
            unresolved.append(f"{gem.get('name','?')} (grantedEffectId={ge_id!r})")
            skill_types_raw: dict[str, bool] = {}
            description = ""
        else:
            skill_types_raw = ge.get("skillTypes", {})
            description = ge.get("description", "")

        skill_type_ids = sorted(int(k) for k in skill_types_raw)

        skill_list.append(SkillGem(
            id=gem_id,
            gameId=gem.get("gameId", ""),
            name=gem.get("name", ""),
            gemFamily=gem.get("gemFamily", ""),
            gemType=gem.get("gemType", ""),
            attribute=derive_attribute(
                gem.get("reqStr", 0),
                gem.get("reqInt", 0),
                gem.get("reqDex", 0),
            ),
            tier=gem.get("Tier", 0),
            naturalMaxLevel=gem.get("naturalMaxLevel", 1),
            reqStr=gem.get("reqStr", 0),
            reqInt=gem.get("reqInt", 0),
            reqDex=gem.get("reqDex", 0),
            tags=gem.get("tags", {}),
            tagString=gem.get("tagString", ""),
            grantedEffectId=ge_id,
            skillTypes=skill_type_ids,
            skillTypeNames=skill_type_names(skill_type_ids),
            description=description,
        ))

    skill_list.sort(key=lambda g: g.name)
    return skill_list, unresolved


# ---------------------------------------------------------------------------
# Build support_gems.json
# ---------------------------------------------------------------------------

def build_support_gems(
    gems: dict[str, Any],
    support_ges: dict[str, Any],
) -> tuple[list[SupportGem], int, int]:
    """
    Returns (support_gem_list, kept_count, dropped_count).

    Matching strategy: each support gem entry has grantedEffectId, so join
    directly on that first. If a GE is hidden=True or lacks requireSkillTypes
    AND excludeSkillTypes AND addSkillTypes (pure internal), drop it.
    """
    kept: list[SupportGem] = []
    dropped = 0

    for gem_id, gem in gems.items():
        if gem.get("gemType") != "Support":
            continue

        ge_id = gem.get("grantedEffectId", "")
        ge = support_ges.get(ge_id)
        if ge is None:
            dropped += 1
            continue

        if ge.get("hidden", False):
            dropped += 1
            continue

        # A "real" player support has at least some skill-type filtering defined
        # (requireSkillTypes, excludeSkillTypes, or addSkillTypes).
        req = ge.get("requireSkillTypes", [])
        excl = ge.get("excludeSkillTypes", [])
        add = ge.get("addSkillTypes", [])
        # Some supports have empty require (works on everything) but still have
        # exclude/add — those are valid. Only drop if ALL three are missing AND
        # there's no name (truly internal). Use name presence as secondary guard.
        if not ge.get("name"):
            dropped += 1
            continue

        kept.append(SupportGem(
            id=gem_id,
            gameId=gem.get("gameId", ""),
            name=gem.get("name", ""),
            gemFamily=gem.get("gemFamily", ""),
            tier=gem.get("Tier", 0),
            reqStr=gem.get("reqStr", 0),
            reqInt=gem.get("reqInt", 0),
            reqDex=gem.get("reqDex", 0),
            tags=gem.get("tags", {}),
            tagString=gem.get("tagString", ""),
            grantedEffectId=ge_id,
            requireSkillTypes=list(req),
            excludeSkillTypes=list(excl),
            addSkillTypes=list(add),
            requireSkillTypeNames=skill_type_names(list(req)),
            excludeSkillTypeNames=skill_type_names(list(excl)),
            description=ge.get("description", ""),
        ))

    kept.sort(key=lambda g: g.name)
    return kept, len(kept), dropped


# ---------------------------------------------------------------------------
# Build support_compatibility.json
# ---------------------------------------------------------------------------

def is_compatible(skill: SkillGem, support: SupportGem) -> bool:
    """
    PoB applicability semantics:
      PASS if:
        (requireSkillTypes is empty) OR (skill.skillTypes & require != empty)
      AND:
        (skill.skillTypes & exclude) is empty
    """
    s_types = set(skill.skillTypes)
    req = set(support.requireSkillTypes)
    excl = set(support.excludeSkillTypes)

    if req and not (s_types & req):
        return False
    if s_types & excl:
        return False
    return True


def build_compatibility(
    skill_gems: list[SkillGem],
    support_gems: list[SupportGem],
) -> dict[str, Any]:
    by_support: dict[str, list[str]] = {}
    by_skill: dict[str, list[str]] = {}

    for sg in skill_gems:
        by_skill[sg.name] = []

    for sup in support_gems:
        compatible_skills: list[str] = []
        for sk in skill_gems:
            if is_compatible(sk, sup):
                compatible_skills.append(sk.name)
                by_skill[sk.name].append(sup.name)
        by_support[sup.name] = compatible_skills

    return {"by_support": by_support, "by_skill": by_skill}


# ---------------------------------------------------------------------------
# Spirit and Meta subsets
# ---------------------------------------------------------------------------

def build_spirit_gems(skill_gems: list[SkillGem]) -> list[dict[str, Any]]:
    """
    Spirit gems = persistent reservation/buff skills.
    Rule: skill has Persistent (140) in skillTypes AND at least one of
    HasReservation(12), Aura(39), or Herald(52) in skillTypes.
    Also include gems with tags.persistent && (tags.aura||tags.herald||tags.buff).
    """
    persistent_id = 140
    has_reservation_id = 12
    aura_id = 39
    herald_id = 52

    spirit: list[dict[str, Any]] = []
    for gem in skill_gems:
        st = set(gem.skillTypes)
        tag_persistent = gem.tags.get("persistent", False)
        tag_qualifies = gem.tags.get("aura", False) or gem.tags.get("herald", False) or gem.tags.get("buff", False)

        is_spirit = False
        if persistent_id in st and (has_reservation_id in st or aura_id in st or herald_id in st):
            is_spirit = True
        elif tag_persistent and tag_qualifies:
            is_spirit = True

        if is_spirit:
            spirit.append(asdict(gem))

    return spirit


def build_meta_gems(skill_gems: list[SkillGem]) -> list[dict[str, Any]]:
    """
    Meta gems = gemType=="Meta" OR tags.meta OR Meta(122) in skillTypes.
    """
    meta_id = 122
    meta: list[dict[str, Any]] = []
    for gem in skill_gems:
        if (
            gem.gemType == "Meta"
            or gem.tags.get("meta", False)
            or meta_id in gem.skillTypes
        ):
            meta.append(asdict(gem))
    return meta


# ---------------------------------------------------------------------------
# Verification / spot-checks
# ---------------------------------------------------------------------------

def run_verification(
    skill_gems: list[SkillGem],
    support_gems: list[SupportGem],
    compatibility: dict[str, Any],
    unresolved: list[str],
) -> None:
    print("\n=== VERIFICATION ===\n")

    # Unresolved skill gems
    if unresolved:
        print(f"WARNING: {len(unresolved)} skill gems with no matching granted-effect:")
        for u in unresolved:
            print(f"  - {u}")
    else:
        print("OK: all skill gems resolved a granted-effect.")

    # Find Fireball for spot-checks
    fireball = next((g for g in skill_gems if g.name == "Fireball"), None)
    if fireball is None:
        print("WARNING: Fireball not found in skill gems")
    else:
        print(f"\nSpot-check: Fireball")
        print(f"  skillTypes: {fireball.skillTypes}")
        print(f"  skillTypeNames: {fireball.skillTypeNames}")
        fb_supports = compatibility["by_skill"].get("Fireball", [])
        print(f"  compatible supports ({len(fb_supports)}): {fb_supports[:10]}{'...' if len(fb_supports)>10 else ''}")

        # Melee-only support should NOT appear for Fireball
        melee_supports = [
            s for s in support_gems
            if 20 in s.requireSkillTypes  # Melee = 20
            and not (1 in s.requireSkillTypes)  # not also Attack+Spell
        ]
        if melee_supports:
            ms = melee_supports[0]
            compat = is_compatible(fireball, ms)
            print(f"\n  Check: '{ms.name}' (melee-only) compatible with Fireball? {compat} (expected False)")
            if compat:
                print(f"    WARNING: melee-only support IS compatible with Fireball — check data")
            else:
                print(f"    OK: melee-only support correctly excluded from Fireball")
        else:
            print("  (no melee-only supports found to test)")

    # Find a "generic" support that works on Spells
    # Look for one whose require includes 7 (Damage) or 2 (Spell)
    spell_supports = [
        s for s in support_gems
        if 7 in s.requireSkillTypes or 2 in s.requireSkillTypes
    ]
    if spell_supports and fireball:
        ss = spell_supports[0]
        compat = is_compatible(fireball, ss)
        print(f"\nSpot-check 2: '{ss.name}' (require={ss.requireSkillTypes}) compatible with Fireball?")
        print(f"  Result: {compat} (expected True for spell-compatible support)")
        if not compat:
            print("  WARNING: expected True but got False")
        else:
            print("  OK")

    # Spot-check 3: find a support with Fireball in its list
    if fireball:
        fb_sup_names = compatibility["by_skill"].get("Fireball", [])
        print(f"\nSpot-check 3: one support that IS compatible with Fireball:")
        if fb_sup_names:
            s_name = fb_sup_names[0]
            sup_obj = next((s for s in support_gems if s.name == s_name), None)
            if sup_obj:
                print(f"  '{s_name}': require={sup_obj.requireSkillTypes}, exclude={sup_obj.excludeSkillTypes}")
                compat = is_compatible(fireball, sup_obj)
                print(f"  Recomputed: {compat} (expected True) — {'OK' if compat else 'FAIL'}")

    print()


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PoE2 Gem Catalog v0.5</title>
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
    --skill-color: #74cabf;
    --support-color: #d4a017;
    --str-color: #e05030;
    --dex-color: #70ff70;
    --int-color: #7070ff;
    --none-color: #888;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; }
  header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; align-items: center; gap: 16px; }
  header h1 { font-size: 18px; color: var(--accent); font-weight: 600; }
  header .counts { color: var(--muted); font-size: 12px; }
  .layout { display: grid; grid-template-columns: 320px 1fr; height: calc(100vh - 48px); }
  .sidebar { background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .filters { padding: 12px; border-bottom: 1px solid var(--border); display: flex; flex-direction: column; gap: 8px; }
  .filters input, .filters select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 4px; font-size: 13px; width: 100%; }
  .filters input:focus, .filters select:focus { outline: none; border-color: var(--accent); }
  .filter-row { display: flex; gap: 6px; }
  .filter-row select { flex: 1; }
  .gem-list { flex: 1; overflow-y: auto; }
  .gem-item { padding: 8px 12px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; flex-direction: column; gap: 2px; }
  .gem-item:hover { background: var(--surface2); }
  .gem-item.active { background: var(--surface2); border-left: 3px solid var(--accent); }
  .gem-item .gem-name { font-weight: 500; font-size: 13px; }
  .gem-item .gem-meta { font-size: 11px; color: var(--muted); display: flex; gap: 8px; }
  .gem-item .gem-type-badge { font-size: 10px; padding: 1px 5px; border-radius: 3px; font-weight: 600; }
  .type-skill { background: rgba(116,202,191,0.15); color: var(--skill-color); }
  .type-support { background: rgba(212,160,23,0.15); color: var(--support-color); }
  .attr-str { color: var(--str-color); }
  .attr-dex { color: var(--dex-color); }
  .attr-int { color: var(--int-color); }
  .attr-none { color: var(--none-color); }
  .detail { flex: 1; overflow-y: auto; padding: 20px; }
  .detail .empty { color: var(--muted); text-align: center; padding: 60px 20px; }
  .gem-detail-title { font-size: 22px; color: var(--accent); font-weight: 700; margin-bottom: 4px; }
  .gem-detail-type { font-size: 13px; color: var(--muted); margin-bottom: 16px; }
  .section { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 14px; }
  .section h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 10px; }
  .desc { line-height: 1.5; color: #aaa; font-size: 13px; }
  .kv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; }
  .kv { display: flex; flex-direction: column; }
  .kv .k { font-size: 11px; color: var(--muted); }
  .kv .v { font-size: 13px; }
  .tag-list { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { background: var(--surface2); border: 1px solid var(--border); padding: 2px 7px; border-radius: 12px; font-size: 11px; color: #aaa; }
  .skill-type-list { display: flex; flex-wrap: wrap; gap: 4px; }
  .st-badge { background: rgba(116,202,191,0.1); border: 1px solid rgba(116,202,191,0.3); color: var(--accent); padding: 2px 7px; border-radius: 12px; font-size: 11px; }
  .compat-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 6px; }
  .compat-item { background: var(--surface2); border: 1px solid var(--border); padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
  .compat-item:hover { border-color: var(--accent); color: var(--accent); }
  .compat-count { color: var(--accent); font-weight: 700; }
  .no-results { color: var(--muted); padding: 20px; text-align: center; }
  .req-line { display: flex; gap: 8px; font-size: 12px; }
  .req-line .req-item { display: flex; align-items: center; gap: 3px; }
</style>
</head>
<body>
<header>
  <h1>PoE2 Gem Catalog <span style="color:var(--muted);font-weight:400">v0.5</span></h1>
  <div class="counts" id="count-display"></div>
</header>
<div class="layout">
  <div class="sidebar">
    <div class="filters">
      <input type="search" id="search" placeholder="Search gems..." autocomplete="off">
      <div class="filter-row">
        <select id="filter-type">
          <option value="">All types</option>
          <option value="skill">Skill gems</option>
          <option value="support">Support gems</option>
        </select>
        <select id="filter-attr">
          <option value="">All attrs</option>
          <option value="str">Str</option>
          <option value="dex">Dex</option>
          <option value="int">Int</option>
          <option value="none">None</option>
        </select>
      </div>
      <select id="filter-tag">
        <option value="">All tags</option>
      </select>
    </div>
    <div class="gem-list" id="gem-list"></div>
  </div>
  <div class="detail" id="detail">
    <div class="empty">Select a gem to view details and compatibility</div>
  </div>
</div>

<script>
const SKILL_GEMS = __SKILL_GEMS__;
const SUPPORT_GEMS = __SUPPORT_GEMS__;
const COMPAT = __COMPAT__;
const COUNTS = __COUNTS__;

// Build lookup maps
const skillByName = Object.fromEntries(SKILL_GEMS.map(g => [g.name, g]));
const supportByName = Object.fromEntries(SUPPORT_GEMS.map(g => [g.name, g]));

// All gems combined for display
const ALL_GEMS = [
  ...SKILL_GEMS.map(g => ({...g, _kind: 'skill'})),
  ...SUPPORT_GEMS.map(g => ({...g, _kind: 'support', attribute: deriveAttr(g)})),
];

function deriveAttr(g) {
  const attrs = [];
  if (g.reqStr > 0) attrs.push('str');
  if (g.reqInt > 0) attrs.push('int');
  if (g.reqDex > 0) attrs.push('dex');
  return attrs.length ? attrs.join('/') : 'none';
}

// Collect all tags
const allTags = new Set();
ALL_GEMS.forEach(g => { if (g.tags) Object.keys(g.tags).forEach(t => allTags.add(t)); });
const tagSelect = document.getElementById('filter-tag');
[...allTags].sort().forEach(t => {
  const o = document.createElement('option');
  o.value = t; o.textContent = t;
  tagSelect.appendChild(o);
});

// Count display
document.getElementById('count-display').textContent =
  `${COUNTS.skill_gems} skills | ${COUNTS.support_gems} supports | ${COUNTS.spirit_gems} spirit | ${COUNTS.meta_gems} meta`;

let activeGem = null;
let filteredGems = [];

function renderList() {
  const q = document.getElementById('search').value.toLowerCase();
  const typeF = document.getElementById('filter-type').value;
  const attrF = document.getElementById('filter-attr').value;
  const tagF = document.getElementById('filter-tag').value;

  filteredGems = ALL_GEMS.filter(g => {
    if (q && !g.name.toLowerCase().includes(q) && !g.tagString.toLowerCase().includes(q)) return false;
    if (typeF === 'skill' && g._kind !== 'skill') return false;
    if (typeF === 'support' && g._kind !== 'support') return false;
    const attr = g._kind === 'skill' ? g.attribute : deriveAttr(g);
    if (attrF && !attr.includes(attrF)) return false;
    if (tagF && !(g.tags && g.tags[tagF])) return false;
    return true;
  });

  const list = document.getElementById('gem-list');
  list.innerHTML = '';

  if (!filteredGems.length) {
    list.innerHTML = '<div class="no-results">No gems match</div>';
    return;
  }

  filteredGems.forEach(g => {
    const attr = g._kind === 'skill' ? g.attribute : deriveAttr(g);
    const attrClass = 'attr-' + (attr.includes('/') ? 'none' : attr);
    const div = document.createElement('div');
    div.className = 'gem-item' + (activeGem && activeGem.id === g.id ? ' active' : '');
    div.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;">
        <span class="gem-name">${g.name}</span>
        <span class="gem-type-badge type-${g._kind}">${g._kind}</span>
      </div>
      <div class="gem-meta">
        <span class="${attrClass}">${attr.toUpperCase()}</span>
        <span>${g.gemType || ''}</span>
        <span>${g.tagString || ''}</span>
      </div>`;
    div.addEventListener('click', () => selectGem(g));
    list.appendChild(div);
  });
}

function selectGem(g) {
  activeGem = g;
  renderList();
  renderDetail(g);
}

function renderDetail(g) {
  const detail = document.getElementById('detail');
  const attr = g._kind === 'skill' ? g.attribute : deriveAttr(g);
  const attrClass = 'attr-' + (attr.includes('/') ? 'none' : attr);

  let compatHtml = '';
  if (g._kind === 'skill') {
    const supNames = (COMPAT.by_skill[g.name] || []);
    compatHtml = `
      <div class="section">
        <h3>Compatible Supports <span class="compat-count">(${supNames.length})</span></h3>
        ${supNames.length ? `<div class="compat-list">${supNames.map(n =>
          `<div class="compat-item" onclick="selectGemByName('${escHtml(n)}','support')">${escHtml(n)}</div>`
        ).join('')}</div>` : '<div class="desc">No compatible supports found</div>'}
      </div>`;
  } else {
    const skillNames = (COMPAT.by_support[g.name] || []);
    const req = g.requireSkillTypes || [];
    const excl = g.excludeSkillTypes || [];
    const add = g.addSkillTypes || [];
    compatHtml = `
      <div class="section">
        <h3>Support Rules</h3>
        <div class="kv-grid">
          <div class="kv"><span class="k">Require Skill Types</span><span class="v">${req.length ? escHtml(g.requireSkillTypeNames.join(', ')) : 'any'}</span></div>
          <div class="kv"><span class="k">Exclude Skill Types</span><span class="v">${excl.length ? escHtml(g.excludeSkillTypeNames.join(', ')) : 'none'}</span></div>
          <div class="kv"><span class="k">Add Skill Types</span><span class="v">${add.length ? add.join(', ') : 'none'}</span></div>
        </div>
      </div>
      <div class="section">
        <h3>Compatible Skills <span class="compat-count">(${skillNames.length})</span></h3>
        ${skillNames.length ? `<div class="compat-list">${skillNames.map(n =>
          `<div class="compat-item" onclick="selectGemByName('${escHtml(n)}','skill')">${escHtml(n)}</div>`
        ).join('')}</div>` : '<div class="desc">No compatible skills found</div>'}
      </div>`;
  }

  const tags = g.tags ? Object.keys(g.tags).filter(t => g.tags[t]) : [];
  const skillTypesHtml = g.skillTypes ? `
    <div class="section">
      <h3>Skill Types</h3>
      <div class="skill-type-list">${(g.skillTypeNames || g.skillTypes || []).map(n =>
        `<span class="st-badge">${escHtml(String(n))}</span>`
      ).join('')}</div>
    </div>` : '';

  detail.innerHTML = `
    <div class="gem-detail-title">${escHtml(g.name)}</div>
    <div class="gem-detail-type">
      <span class="gem-type-badge type-${g._kind}">${g._kind}</span>
      <span style="margin-left:8px;" class="${attrClass}">${attr.toUpperCase()}</span>
      <span style="color:var(--muted);margin-left:8px;">${g.gemType || ''}</span>
    </div>
    <div class="section">
      <h3>Properties</h3>
      <div class="kv-grid">
        <div class="kv"><span class="k">Gem Family</span><span class="v">${escHtml(g.gemFamily || '-')}</span></div>
        <div class="kv"><span class="k">Tier</span><span class="v">${g.tier ?? '-'}</span></div>
        <div class="kv"><span class="k">Max Level</span><span class="v">${g.naturalMaxLevel ?? '-'}</span></div>
        <div class="kv"><span class="k">Tags</span><span class="v">${tags.map(t => `<span class="tag">${escHtml(t)}</span>`).join(' ') || '-'}</span></div>
        <div class="kv"><span class="k">Req Str</span><span class="v attr-str">${g.reqStr || 0}</span></div>
        <div class="kv"><span class="k">Req Dex</span><span class="v attr-dex">${g.reqDex || 0}</span></div>
        <div class="kv"><span class="k">Req Int</span><span class="v attr-int">${g.reqInt || 0}</span></div>
      </div>
    </div>
    ${g.description ? `<div class="section"><h3>Description</h3><div class="desc">${escHtml(g.description)}</div></div>` : ''}
    ${skillTypesHtml}
    ${compatHtml}
  `;
}

function selectGemByName(name, kind) {
  const gem = kind === 'skill'
    ? ALL_GEMS.find(g => g._kind === 'skill' && g.name === name)
    : ALL_GEMS.find(g => g._kind === 'support' && g.name === name);
  if (gem) {
    // Clear filters and scroll to
    document.getElementById('search').value = '';
    document.getElementById('filter-type').value = kind;
    document.getElementById('filter-attr').value = '';
    document.getElementById('filter-tag').value = '';
    selectGem(gem);
    renderList();
    // Scroll to active item
    setTimeout(() => {
      const active = document.querySelector('.gem-item.active');
      if (active) active.scrollIntoView({ block: 'nearest' });
    }, 50);
  }
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

['search','filter-type','filter-attr','filter-tag'].forEach(id => {
  document.getElementById(id).addEventListener('input', renderList);
});

renderList();
</script>
</body>
</html>
"""


def render_html(
    skill_gems: list[SkillGem],
    support_gems: list[SupportGem],
    compatibility: dict[str, Any],
    counts: dict[str, int],
) -> str:
    html = HTML_TEMPLATE
    html = html.replace("__SKILL_GEMS__", json.dumps([asdict(g) for g in skill_gems], separators=(",", ":")))
    html = html.replace("__SUPPORT_GEMS__", json.dumps([asdict(g) for g in support_gems], separators=(",", ":")))
    html = html.replace("__COMPAT__", json.dumps(compatibility, separators=(",", ":")))
    html = html.replace("__COUNTS__", json.dumps(counts, separators=(",", ":")))
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build PoE2 gem catalog")
    parser.add_argument("--skip-download", action="store_true", help="Use cached _raw/ files")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_download:
        download_all()
    else:
        print("=== Skipping download, using cached files ===")

    # Parse SkillType enum
    global SKILL_TYPE_ENUM
    lua_path = RAW_DIR / "Global.lua"
    SKILL_TYPE_ENUM = parse_skill_type_enum(lua_path)

    # Load Gems.json
    print("\n=== Loading gem data ===")
    gems_path = RAW_DIR / "Gems.json"
    gems: dict[str, Any] = load_json(gems_path)
    print(f"  Gems.json: {len(gems)} entries")

    # Load all active granted-effects (merge all act_* + minion + other + spectre)
    active_ges: dict[str, Any] = {}
    for fname in [Path(f).name for f in ACTIVE_FILES]:
        p = RAW_DIR / fname
        if p.exists():
            data: dict[str, Any] = load_json(p)
            active_ges.update(data)
            print(f"  {fname}: {len(data)} entries")
        else:
            print(f"  WARNING: {fname} not found", file=sys.stderr)
    print(f"  Total active GEs: {len(active_ges)}")

    # Load all support granted-effects
    support_ges: dict[str, Any] = {}
    for fname in [Path(f).name for f in SUPPORT_FILES]:
        p = RAW_DIR / fname
        if p.exists():
            data = load_json(p)
            support_ges.update(data)
            print(f"  {fname}: {len(data)} entries")
        else:
            print(f"  WARNING: {fname} not found", file=sys.stderr)
    print(f"  Total support GEs: {len(support_ges)}")

    # Build outputs
    print("\n=== Building datasets ===")
    skill_gems, unresolved = build_skill_gems(gems, active_ges)
    print(f"  Skill gems: {len(skill_gems)}")
    if unresolved:
        print(f"  Unresolved (no GE match): {len(unresolved)}")

    support_gems, kept, dropped = build_support_gems(gems, support_ges)
    print(f"  Support gems: {kept} kept, {dropped} dropped (hidden/internal)")

    compatibility = build_compatibility(skill_gems, support_gems)
    spirit_gems = build_spirit_gems(skill_gems)
    meta_gems = build_meta_gems(skill_gems)
    print(f"  Spirit gems: {len(spirit_gems)}")
    print(f"  Meta gems: {len(meta_gems)}")

    counts = {
        "skill_gems": len(skill_gems),
        "support_gems": kept,
        "support_dropped": dropped,
        "spirit_gems": len(spirit_gems),
        "meta_gems": len(meta_gems),
    }

    # Write JSON outputs
    print("\n=== Writing JSON outputs ===")

    def write_json(path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote {path} ({path.stat().st_size:,}B)")

    write_json(OUT_DIR / "skill_gems.json", [asdict(g) for g in skill_gems])
    write_json(OUT_DIR / "support_gems.json", [asdict(g) for g in support_gems])
    write_json(OUT_DIR / "support_compatibility.json", compatibility)
    write_json(OUT_DIR / "spirit_gems.json", spirit_gems)
    write_json(OUT_DIR / "meta_gems.json", meta_gems)

    catalog = {
        "version": "0.5",
        "source": "repoe-fork/pob-data PoB export",
        "counts": counts,
        "generated_from": [GEMS_FILE] + ACTIVE_FILES + SUPPORT_FILES,
        "skill_type_enum_source": GLOBAL_LUA_URL,
        "spirit_gem_rule": (
            "skillTypes contains Persistent(140) AND (HasReservation(12) OR Aura(39) OR Herald(52)), "
            "OR tags.persistent && (tags.aura || tags.herald || tags.buff)"
        ),
        "meta_gem_rule": "gemType=='Meta' OR tags.meta OR skillTypes contains Meta(122)",
        "compatibility_rule": (
            "A support S can support active A iff: "
            "(S.requireSkillTypes is empty OR A.skillTypes & S.requireSkillTypes != empty) "
            "AND (A.skillTypes & S.excludeSkillTypes is empty)"
        ),
        "files": {
            "skill_gems": "skill_gems.json",
            "support_gems": "support_gems.json",
            "support_compatibility": "support_compatibility.json",
            "spirit_gems": "spirit_gems.json",
            "meta_gems": "meta_gems.json",
            "catalog_index": "gem_catalog.json",
            "browser": "gem_catalog.html",
        },
    }
    write_json(OUT_DIR / "gem_catalog.json", catalog)

    # Render HTML
    html_content = render_html(skill_gems, support_gems, compatibility, counts)
    html_path = OUT_DIR / "gem_catalog.html"
    try:
        html_path.write_text(html_content, encoding="utf-8")
        print(f"  wrote {html_path} ({html_path.stat().st_size:,}B)")
    except OSError as e:
        print(f"  ERROR writing HTML: {e}", file=sys.stderr)

    # Verification
    run_verification(skill_gems, support_gems, compatibility, unresolved)

    print("=== Done ===")
    print(f"Counts: {counts}")


if __name__ == "__main__":
    main()
