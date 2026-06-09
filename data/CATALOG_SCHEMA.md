# PoE2 v0.5 Gem Catalog

Normalized gem dataset for Path of Exile 2 (v0.5), derived from the
[repoe-fork/pob-data](https://github.com/repoe-fork/pob-data) PoB community
data export (itself derived from GGG game files).

## Files

| File | Description |
|------|-------------|
| `skill_gems.json` | 399 active/skill gems with skill types and descriptions |
| `support_gems.json` | 538 real player support gems with compatibility rules |
| `support_compatibility.json` | Precomputed compatibility matrix (by_skill + by_support) |
| `spirit_gems.json` | 118 spirit-reserving gems (subset of skill_gems) |
| `meta_gems.json` | 29 meta/trigger gems (subset of skill_gems) |
| `gem_catalog.json` | Combined index + counts + schema documentation |
| `gem_catalog.html` | Self-contained static browser (search/filter/compat UI) |
| `build_catalog.py` | Reproducible build script |
| `_raw/` | Downloaded source files (gitignored) |

## Rebuild

```bash
python3 docs/poe2/build_catalog.py          # fresh download + build
python3 docs/poe2/build_catalog.py --skip-download  # use cached _raw/
```

Requires Python 3.10+ and `curl` in PATH. No third-party deps.

## Data Sources

- **Gems.json** — 965 gem item entries (canonical gem list)
- **Skills/act_*.json, minion.json, other.json, spectre.json** — Active skill granted-effects
- **Skills/sup_*.json** — Support granted-effects
- **Global.lua** (PathOfBuilding-PoE2) — SkillType enum (278 entries, id -> name)

Base URL: `https://raw.githubusercontent.com/repoe-fork/pob-data/master/pob-data/poe2/`

## Counts

| Dataset | Count | Notes |
|---------|-------|-------|
| skill_gems | 399 | All non-Support gemType entries |
| support_gems | 538 | support:true GEs, not hidden, has name |
| support_dropped | 28 | hidden:true or no GE found in export |
| spirit_gems | 118 | Subset of skill_gems (reservation skills) |
| meta_gems | 29 | Subset of skill_gems (trigger/meta skills) |

The task spec mentioned ~181 supports -- that figure is the count within
`sup_int.json` alone. The correct total across all three attribute files is 538.

## Field Schema

### skill_gems.json entries

```
id              string  Metadata key (e.g. "Metadata/Items/Gems/...")
gameId          string  In-game asset path
name            string  Display name
gemFamily       string  Shared family across tiers (e.g. "Fireball")
gemType         string  Spell | Attack | Buff | Warcry | Minion | ...
attribute       string  "str" | "dex" | "int" | "str/int" | "none" | etc.
tier            int     0 = base, 1-4 = tier upgrades
naturalMaxLevel int     Default max level cap
reqStr          int
reqInt          int
reqDex          int
tags            object  {tagName: true, ...}
tagString       string  Comma-separated display tags
grantedEffectId string  FK into active granted-effect files
skillTypes      list    Numeric SkillType ids (from granted-effect)
skillTypeNames  list    Human-readable names (from Global.lua enum)
description     string  In-game skill description
```

### support_gems.json entries

```
id                     string  Metadata key
gameId                 string
name                   string
gemFamily              string
tier                   int
reqStr, reqInt, reqDex int
tags                   object
tagString              string
grantedEffectId        string  FK into support granted-effect files
requireSkillTypes      list    Numeric ids -- skill must match ANY of these
excludeSkillTypes      list    Numeric ids -- skill must NOT match any of these
addSkillTypes          list    Numeric ids -- types added to skill when supported
requireSkillTypeNames  list    Human-readable require names
excludeSkillTypeNames  list    Human-readable exclude names
description            string
```

### support_compatibility.json

```json
{
  "by_support": { "SupportName": ["SkillName", ...], ... },
  "by_skill":   { "SkillName": ["SupportName", ...], ... }
}
```

## Compatibility Algorithm

Derived from PoB's applicability semantics:

A support gem **S** can support an active skill **A** if and only if:

1. `S.requireSkillTypes` is empty, **OR** `A.skillTypes AND S.requireSkillTypes` is non-empty
2. **AND** `A.skillTypes AND S.excludeSkillTypes` is empty

The `require` check is an **OR** (any intersection): a skill needs to have at
least one of the required types, not all of them.

### Example

**Fireball** has skillTypes: Spell(2), Projectile(3), Damage(7), Area(8), Fire(28), ...

**Bloodlust** requireSkillTypes: [Melee(20)] -- Fireball does NOT have Melee.
Result: **incompatible** (correct -- Bloodlust is melee-only).

**Admixture** requireSkillTypes: [Attack(1), Damage(7), CrossbowSkill(116)]
Fireball has Damage(7) -- intersection is non-empty.
Admixture excludeSkillTypes: [DegenOnlySpellDamage(49)] -- Fireball does not have this.
Result: **compatible** (Fireball can cause Damaging Hits, which satisfies Admixture's rule).

## Spirit Gems Rule

```
Persistent(140) IN skillTypes
AND (HasReservation(12) OR Aura(39) OR Herald(52)) IN skillTypes
```

Or, as fallback via tags:
```
tags.persistent AND (tags.aura OR tags.herald OR tags.buff)
```

In PoE2 v0.5, all skills that reserve Spirit are "spirit gems". This includes
auras, heralds, buffs, and many triggered/on-hit skills that require persistent
spirit reservation.

## Meta Gems Rule

```
gemType == "Meta"
OR tags.meta == true
OR Meta(122) IN skillTypes
```

Meta gems are trigger-style skills (Cast on Critical, Spell Totem, etc.) that
modify or proxy the behavior of linked skills.

## Data Gaps

- **Enervating Nova** (Spell, Int) has grantedEffectId `EnervatingNovaPlayer`
  which is absent from all active GE files in the current PoB export. This gem
  appears in Gems.json with full metadata but no skillTypes/description from
  the GE files. It is included in skill_gems.json with empty skillTypes.
- The SkillType enum has 278 entries; all numeric ids seen in the data mapped
  successfully to names.
- No timestamps are included (build environment has no reliable date source).
