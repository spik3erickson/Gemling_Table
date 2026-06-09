# PoB-grade DPS engine (skill + support layer) — design

**Date:** 2026-06-09
**Repo:** `github.com/spik3erickson/Gemling_Table`
**Status:** approved (brainstorming), grounded by a 5-agent PoB-schema recon

## Goal

Replace the decomposed *"weapon base × approx multiplier"* display ([index.html](../../../index.html), the block currently around lines 601–605) with **one real, transparent hit & DPS number**, computed from PoB numeric data on the layer the engine controls: skill base damage at gem level, exact support multipliers, weapon base for attacks, crit, and cast/attack speed. Tree/gear enter through a clearly-labeled, user-adjustable `increased%` bucket. The number is honest — exact on what we model, explicit about what falls in the bucket. **Math still decides the build; DPS is the proof it can finally show.**

Decisions locked: default **gem level 20** (slider 1–20), default **quality 20%**, conservative **increased% bucket** default (≈150%) the user can dial. Hits only for v1 (attacks + spells); ailment/DoT and minion DPS are explicit fast-follows.

## Ground truth from recon (evidence-backed — do NOT re-derive)

These corrected several naive assumptions. The extractor and engine MUST follow them verbatim:

1. **Numbered level values are FINAL.** In `statSets[i].levels[n]`, the numbered keys `"1","2",…` map positionally to `stats[0],stats[1],…` and ARE the final per-gem-level values. **Do NOT** re-apply `baseEffectiveness`/`incrementalEffectiveness`/`damageIncrementalEffectiveness` — those only regenerate non-tabulated levels. *Proof:* Fireball L1 `{1:8,2:12}` == poe2db tooltip "Deals 8 to 12 Fire Damage" (not 8×2.6); EssenceDrain DoT raw 550/min ÷60 = 9.2/s == tooltip. (One recon agent disagreed; three agents + tooltips overruled it.)
2. **Two `levels` arrays exist.** Granted-effect TOP-LEVEL `e.levels[i]` carries per-gem-level scalars: `cost, levelRequirement, critChance, baseMultiplier, attackSpeedMultiplier, attackTime, cooldown`. `e.statSets[j].levels[i]` carries the numbered STAT values. Both indexed by gem level; **index 0 = gem level 1**.
3. **Gem level:** `naturalMaxLevel` mode = 20 (393/399). Use index = `gemLevel − 1`; max = index 19. `levels[]` often has 40 rows (21–40 = +level only). `actorLevel` is a balance x-axis — **never** select a row by it.
4. **Spell damage:** flat base in `statSets[].stats[]` as `spell_{minimum,maximum}_base_{fire,cold,lightning,physical,chaos}_damage` (+ `secondary_*` variants). Resolve **by position of the named stat in `stats[]`** (some statSets prepend/duplicate). `castTime` is top-level seconds; `rate = 1/castTime`. Base crit = `e.levels[i].critChance` (whole %, constant across levels) else 5.0.
5. **Attack damage:** NO base-damage stat. `componentHit = (weaponAvg + skillAddedFlat) × baseMultiplier`, where `baseMultiplier` is a **fraction** (1.1 = 110%) that **scales with gem level** (PerfectStrike 1.1→3.43 at L20). Resolution per hit component: `statSet.levels[i].baseMultiplier ?? topLevel.levels[i].baseMultiplier ?? 1.0`. Weapon base damage/attackTime come from the **equipped weapon item**, not the skill. Attack `castTime` is a dummy 1.0 — **ignore for rate**. Rate = `(1/weaponAttackTime) × (1 + attackSpeedMultiplier/100)`; or `1000/attackTimeMs` when `e.levels[i].attackTime` (ms) is present (shield/traversal skills). Base crit from the **weapon** unless the skill sets `critChance`. Conversion via `constantStats` `active_skill_base_physical_damage_%_to_convert_to_{fire,cold,lightning,chaos}`.
6. **Supports do NOT scale per gem level.** Values are fixed in `statSet.constantStats`. Power comes from gem **tiers** (Brutality I/II/III = separate granted-effects). Classify each stat:
   - `*_+%_final` → **MORE** (multiplicative, `×(1+v/100)`; negative = "less"). Generic = `support_active_skill_damage_+%_final` / `supported_active_skill_damage_+%_final`; many type/condition-specific variants.
   - plain `attack_speed_+%` / `base_cast_speed_+%` → **INCREASED** (additive bucket).
   - `non_skill_base_all_damage_%_to_gain_as_{fire,…}` → attunement **gain-as conversion** (not flat).
   - flat min/max added only on **triggered secondary** granted-effects (out of v1 scope).
   - crit: `base_critical_strike_multiplier_+` (flat add), `additional_base_critical_strike_chance` (flat add), `*_critical_strike_*_+%_final` (more). No support quality data exists.
7. **Coverage:** ~216/399 gems produce a v1 DPS number (137 attack + 63 spell + 16 crossbow-`AmmoPlayer` recovered by suffix-swap `AmmoPlayer`→`Player`). 37 minion → flag-excluded v1. 146 hard-excluded (auras/heralds/buffs/curses/warcries/movement/guard/triggers/totems-without-own-damage/pure-DoT). Exclusion predicate and skillType id list are in §"Coverage". **Multi-statSet primary = `statSets[0]`** in every tested case (use first statSet without `base_deal_no_damage`).

## Architecture — two parts

### A. Build-time extractor — `scripts/build_dps.py`

Reproducible like the other build scripts (`--skip-download`; reuses the `repoe-fork/pob-data` URL base already in `scripts/build_catalog.py`). Reads `data/_raw/Skills/{act_str,act_dex,act_int,other,minion,sup_str,sup_int,sup_dex}.json`, `data/_raw/Global.lua`, `data/skill_gems.json`, `data/support_gems.json`. Writes two compact, pre-resolved datasets the browser consumes without re-interpolating.

#### `data/skill_dps.json` (frozen contract)
```json
{
  "version": "0.5",
  "source": "repoe-fork/pob-data PoE2 v0.5",
  "generated_at": "<ISO8601>",
  "default_level": 20, "default_quality": 20,
  "skills": {
    "Fireball": {
      "id": "FireballPlayer",
      "kind": "spell",                 // "spell" | "attack"
      "primaryStatSet": "Projectile",
      "castTime": 1.2,                  // seconds; spells. attacks: dummy, ignored
      "attackTimeMs": null,             // ms override if present (else null)
      "critChance": 7,                  // base % (spell); null => use weapon crit (attack)
      "weaponTypes": [],                // e.g. ["Bow"], ["One Hand Mace","Two Hand Mace"]
      "maxLevel": 20,
      "convert": {},                    // phys->X %, e.g. {"lightning":80} (level-independent)
      "quality": [["number_of_chains",0.1]],   // raw qualityStats
      "levels": {                       // keys "1".."maxLevel"
        "20": {
          "base": {"fire":[minF,maxF]}, // SPELLS: final min/max per damage type
          "added": {},                  // skill-added flat per type (rare)
          "baseMultiplier": null,       // ATTACKS only (fraction)
          "attackSpeedMultiplier": null // ATTACKS only (percent, MORE)
        }
        // ... every level 1..maxLevel
      }
    },
    "Perfect Strike": {
      "id":"PerfectStrikePlayer","kind":"attack","primaryStatSet":"...",
      "castTime":1,"attackTimeMs":null,"critChance":null,
      "weaponTypes":["One Hand Mace","Two Hand Mace"],"maxLevel":20,
      "convert":{},"quality":[["active_skill_ignite_chance_+%_final",1]],
      "levels":{"20":{"base":{},"added":{},"baseMultiplier":3.43,"attackSpeedMultiplier":-70}}
    }
  },
  "excluded": { "<Skill>": "minion|base_deal_no_damage|skilltype|dot_only|no_granted_effect" }
}
```
- Resolve damage stats **by name→position** in `stats[]`, never hardcoded index.
- `baseMultiplier`: per level, `statSet ?? topLevel ?? 1.0`.
- Crossbow `AmmoPlayer`: read the damaging sibling `…Player` granted-effect.
- Clamp level index to `len(levels)-1` for `naturalMaxLevel==1` / short arrays.

#### `data/support_dps.json` (frozen contract)
```json
{
  "version":"0.5","source":"...","generated_at":"<ISO8601>",
  "supports": {
    "Brutality I": {
      "id":"SupportBrutalityPlayer",
      "more":   [{"stat":"support_brutality_physical_damage_+%_final","value":25,"bucket":"physical"}],
      "increased":[],                          // [{"stat":"attack_speed_+%","value":15,"bucket":"attack_speed"}]
      "moreSpeed":[],                          // *_speed_+%_final (multiplicative)
      "gainAs":  [],                           // [{"from":"all","to":"fire","pct":25}]
      "crit":    {"addedMulti":0,"addedChance":0,"moreChance":0,"moreMulti":0},
      "convert": [],                           // phys->X if any
      "flags":   ["deal_no_elemental_damage","base_deal_no_chaos_damage"],
      "tags":    {"physical":true,"support":true},
      "rawConstantStats": { "...": "..." }     // full passthrough for transparency
    }
  }
}
```
- `bucket` on each `more` entry says which damage type(s) it applies to: `"all"` (generic), an element/`physical`/`chaos`, `"spell"`, `"attack"`, `"area"`, etc. Engine matches bucket vs the build spine.
- Keep tier variants as distinct keys (the names already include I/II/III).

### B. Runtime engine — `computeDPS(skillName, supportNames, ctx)` in `index.html`

Pure function, no DOM, returns a ledger object (so it's Node-testable). Loads `data/skill_dps.json` + `data/support_dps.json` (add both to the existing `FILES` map and `Promise.all` loader).

**Inputs:** `skillName`; chosen `supportNames[]` (the engine's existing 5 picks); `ctx = { level=20, quality=20, weaponAvg={phys,fire,cold,lightning,chaos}, weaponAttackTime, weaponCrit=5, increasedPct=150, increasedAttackSpeed=0, increasedCastSpeed=0, addedFlat={}, critChanceBonus=0, critMulti=100 }`. For attacks, `weaponAvg`/`weaponAttackTime` come from the best base of the chosen weapon type (reuse `weaponDPS()` source) and are user-editable.

**Pipeline (compute per damage type, then sum):**
1. **Base hit by type.** Spell: `avg(min,max)` at level L from `skill.levels[L].base[type]` + skill `added` + support flat (none v1) + `ctx.addedFlat`. Attack: `weaponAvg[type]`; total weapon avg × `baseMultiplier(L)`; add skill `added` × `baseMultiplier`.
2. **Conversion.** Apply skill `convert` then support `gainAs`: move % of source type to target (gain-as adds; convert moves). Pre-resistance, magnitude-preserving for convert.
3. **More multipliers.** Product over selected supports of `(1 + value/100)` for every `more` entry whose `bucket` matches this type (or `"all"`/`kind`). Also `ctx` global more if any.
4. **Increased.** `× (1 + ctx.increasedPct/100)` (the transparent tree/gear bucket).
5. **Sum types → `hit`.**
6. **Crit.** `chance = (skill.critChance ?? ctx.weaponCrit) + ctx.critChanceBonus + support addedChance` (clamp 0–100). `bonus = ctx.critMulti + support addedMulti` (percent extra; 100 ⇒ ×2 on crit). `critFactor = 1 + (chance/100)×(bonus/100)`, with support `moreChance`/`moreMulti` applied multiplicatively first.
7. **Rate.** Spell: `(1/castTime) × (1 + (ctx.increasedCastSpeed)/100) × Π(support moreSpeed cast)`. Attack: `attackTimeMs ? 1000/attackTimeMs : (1/weaponAttackTime)` × `(1 + (attackSpeedMultiplier + ctx.increasedAttackSpeed + support increased attack_speed)/100)` × `Π(support moreSpeed attack)`. `castTime==0` ⇒ treat as the override/instant case.
8. **`dps = hit × critFactor × rate`.** Return `{ dps, hit, byType:{}, rate, critFactor, chance, parts:[ ["term","value"]… ], supportsUsed:[…], excludedReason? }`.

**Render:** replace the decomposed display block with a transparent ledger (base → +added → ×more → ×increased → ×crit → ×rate = DPS), per-type breakdown, the level slider (1–20) + quality + the editable `increased%`/weapon fields. Label: *"Estimated DPS — exact on skill + supports + weapon + crit; tree/gear via the adjustable bucket. Pre-mitigation."* If the skill is in `excluded`, show why (e.g. "minion DPS not modelled yet") instead of a number.

**Also (in-scope, small win):** upgrade the engine's support **ranking** to use the exact `more` product from `support_dps.json` when available, falling back to the current text parse otherwise — replacing the regex guess at its source.

## Coverage / exclusion predicate (for the extractor)

Order: (1) no granted-effect → exclude. (2) `CreatesMinion(77)` or `minion.json` → flag minion (exclude v1). (3) `CrossbowAmmoSkill` + id endswith `AmmoPlayer` + sibling `…Player` exists → recover sibling. (4) ALL statSets contain `base_deal_no_damage`/`display_statset_no_hit_damage` → exclude. (5) `Attack(1)` → attack model. (6) any statSet has a `spell_*`/`secondary_*` base-damage stat → spell model. (7) skillType in {Buff5, Aura39, Herald52, AuraAffectsEnemies53, AuraNotOnCaster88, Movement34, Travel79, Blink80, Guard78, Hex98, Mark99, AppliesCurse69, Warcry63, Banner89, Stance94, Offering155, Meta122, ModifiesNextSkill119, EmpowersOtherSkill148, Invocation158, Blessing109, CanHaveBlessing81, IsBlasphemy179, Link108, Brand65} → exclude. (8) DoT/ailment-only {DamageOverTime35, CausesBurning24, ElementalStatus17} → exclude. (9) else → exclude (no-hit).

## Scope — explicitly OUT for v1 (YAGNI)

- Ailment/DoT DPS (ignite/poison/bleed); per-minute DoT data is identified → fast-follow #1.
- Numeric passive-tree sim & rare-mod parsing (the rejected "full sim") — tree/gear enter only via the `increased%`/crit/speed bucket.
- Minion DPS (flagged, excluded).
- Secondary statSets / multi-hit components beyond the primary (primary `statSets[0]` only); triggered-skill added damage.
- Resistance/penetration mitigation — DPS is pre-mitigation, labeled as such.

## Testing

Node assertions (repo convention: "Verified in Node"):
- Extractor sanity: `skill_dps.json` has ~200+ skills; Fireball L1 base `{fire:[8,12]}`, L20 matches; Spark L1 `[1,10]`; a crossbow attack has `baseMultiplier` rising with level; counts of attack vs spell vs excluded match the coverage estimate (±a few).
- Engine: a spell build (Fireball + 5 supports) yields a plausible DPS; support `more` product equals hand-computed `Π(1+v/100)`; an attack build scales with weapon avg; level slider 1 vs 20 changes the number monotonically.
- Regression: existing build()/render() flow still works; other pages untouched.

## Files

- New: `scripts/build_dps.py`, `data/skill_dps.json`, `data/support_dps.json`, `scripts/test_dps.mjs` (Node tests).
- Edit: `index.html` (load 2 files, add `computeDPS` + ctx UI, replace DPS block, swap support-rank source).
- Edit: `README.md` (data-source + DPS section).
