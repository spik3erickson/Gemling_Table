# PoE2 v0.5 — Skill Gem Gemling Quality Effects

The **gemling effect** every skill gem gains under a Gemling Legionnaire's *Advanced Thaumaturgy* ("Gem Quality grants Socketed Skills an additional effect"), alongside the generic quality bonus every other class gets. Source: [poe2db Advanced Thaumaturgy](https://poe2db.tw/us/Advanced_Thaumaturgy).

**260** skills · **110** new in 0.5 · grouped by type from Path-of-Building gem tags.

> This repo also ships a full machine-readable **gem catalog** with support↔skill compatibility — see [What else is here](#what-else-is-in-this-repo).

## Contents

- [Meta & Triggered Skills](#meta--triggered-skills) (33)
- [Curses](#curses) (5)
- [Marks](#marks) (3)
- [Heralds](#heralds) (5)
- [Warcries](#warcries) (3)
- [Auras, Presences & Persistent Buffs](#auras-presences--persistent-buffs) (33)
- [Totems & Placed Objects](#totems--placed-objects) (4)
- [Minions & Summons](#minions--summons) (23)
- [Movement Skills](#movement-skills) (9)
- [Spell Skills](#spell-skills) (45)
- [Attack Skills](#attack-skills) (93)
- [Other](#other) (4)
- [How quality scales](#how-quality-scales)
- [What else is in this repo](#what-else-is-in-this-repo)

## How quality scales

Quality effects show as a range `(0—N)`; `N` is the value at the standard **20% quality** cap and scaling is linear (a Gemling Legionnaire pushes quality far past 20%):

| Listed range | @ 20% q | @ 30% q | @ 40% q | @ 50% q |
|---|---:|---:|---:|---:|
| `(0—10)` | 10 | 15 | 20 | 25 |
| `(0—20)` | 20 | 30 | 40 | 50 |
| `(0—30)` | 30 | 45 | 60 | 75 |
| `(0—40)` | 40 | 60 | 80 | 100 |
| `(0—50)` | 50 | 75 | 100 | 125 |

Chance-based effects clamp at 100%. Negative ranges (e.g. `(-1—0)`) reduce toward zero.

## Meta & Triggered Skills

_Cast-on triggers and meta gems. Quality often affects reservation cost or trigger frequency._  (33 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Ancestral Cry](https://poe2db.tw/us/Ancestral_Cry) | 🔴 STR | Grants (0—10)% more Fire damage | +(0—20)% increased Warcry duration per Endurance Charge consumed | 15 |  |
| [Ancestral Warrior Totem](https://poe2db.tw/us/Ancestral_Warrior_Totem) | 🔴 STR | (0—50)% increased totem life | +(0—2) seconds to Totem duration | 75 |  |
| [Animus Splinters](https://poe2db.tw/us/Animus_Splinters) | — | (0—20)% increased Skill Effect Duration | — | 30 | 🆕 |
| [Barrier Invocation](https://poe2db.tw/us/Barrier_Invocation) | — | Socketed Spells deal (0—20)% increased Damage when triggered | — | 30 | 🆕 |
| [Blasphemy](https://poe2db.tw/us/Blasphemy) | 🔵 INT | Socketed Curses have (0—20)% increased Magnitudes | (0—10)% increased Reservation Efficiency | 30 |  |
| [Bloodhound's Mark](https://poe2db.tw/us/Bloodhounds_Mark) | 🟢 DEX | Deals (0—20)% more Physical damage | Marked target receives Heavy Stun buildup equal to (0—50)% of Blood Loss | 30 |  |
| [Cast on Critical](https://poe2db.tw/us/Cast_on_Critical) | 🔵 INT | Buff grants (0—20)% increased Critical Hit chance | (0—10)% increased Reservation Efficiency | 30 |  |
| [Cast on Dodge](https://poe2db.tw/us/Cast_on_Dodge) | — | Buff grants +(0—1) metre to Dodge Roll distance | — | 1.5 | 🆕 |
| [Cast on Elemental Ailment](https://poe2db.tw/us/Cast_on_Elemental_Ailment) | 🔵 INT | (0—40)% increased Reservation Efficiency | (0—15)% increased Energy gained | 60 |  |
| [Cast on Minion Death](https://poe2db.tw/us/Cast_on_Minion_Death) | 🔵 INT | Socketed Spells deal (0—20)% increased Damage when triggered | (0—20)% increased Energy gained | 30 |  |
| [Elemental Invocation](https://poe2db.tw/us/Elemental_Invocation) | — | Socketed Spells deal (0—20)% increased Damage when triggered | — | 30 | 🆕 |
| [Escape Shot](https://poe2db.tw/us/Escape_Shot) | 🟢 DEX | (0—40)% increased Damage with Hits against Frozen Enemies | (0—120)% more Freeze Buildup | 60 |  |
| [Explosive Transmutation](https://poe2db.tw/us/Explosive_Transmutation) | — | (0—30)% increased Runic Ward Cost Efficiency | — | 45 | 🆕 |
| [Feral Invocation](https://poe2db.tw/us/Feral_Invocation) | — | (0—40)% increased Reservation Efficiency | — | 60 | 🆕 |
| [Ferocious Roar](https://poe2db.tw/us/Ferocious_Roar) | — | Socketed Skills have (0—40)% increased Cooldown Recovery Rate | — | 60 | 🆕 |
| [Fortifying Cry](https://poe2db.tw/us/Fortifying_Cry) | 🔴 STR | (0—20)% more Guard gained | Shockwave radius is (0—0.4) metres | 30 |  |
| [Hand of Chayula](https://poe2db.tw/us/Hand_of_Chayula) | — | (0—50)% reduced Mana Cost | — | 75 | 🆕 |
| [Ice-Tipped Arrows](https://poe2db.tw/us/Ice-Tipped_Arrows) | 🟢 DEX | Empowers + (0—2) Attacks | (0—10)% increased Cooldown Recovery Rate | 3 |  |
| [Infernal Cry](https://poe2db.tw/us/Infernal_Cry) | 🔴 STR | Warcry radius is (0—3) metres | Empowered Attacks Gain (0—10)% of damage as extra Fire damage | 4.5 |  |
| [Lunar Blessing](https://poe2db.tw/us/Lunar_Blessing) | — | (0—40)% increased Cooldown Recovery Rate | — | 60 | 🆕 |
| [Magma Barrier](https://poe2db.tw/us/Magma_Barrier) | 🔴 STR | Buff grants +(0—5)% to maximum Block Chance | +(0—5)% increased Block chance | 7.5 |  |
| [Mirage Archer](https://poe2db.tw/us/Mirage_Archer) | 🟢 DEX | (0—40)% increased Reservation Efficiency of Skills | +(0—1) seconds to Mirage duration | 60 |  |
| [Mortar Cannon](https://poe2db.tw/us/Mortar_Cannon) | — | Limit (0—1) Totem | — | 1.5 | 🆕 |
| [Pounce](https://poe2db.tw/us/Pounce) | — | Limit (0—4) Summoned Wolves | — | 6 | 🆕 |
| [Rain of Blades](https://poe2db.tw/us/Rain_of_Blades) | — | (0—30)% increased Immobilisation buildup | — | 45 | 🆕 |
| [Reaper's Invocation](https://poe2db.tw/us/Reapers_Invocation) | — | Socketed Spells deal (0—20)% increased Damage when triggered | — | 30 | 🆕 |
| [Repulsion](https://poe2db.tw/us/Repulsion) | — | +(0—20)% more damage against Immobilised enemies | — | 30 | 🆕 |
| [Shattering Palm](https://poe2db.tw/us/Shattering_Palm) | — | (0—20)% more Area of Effect | — | 30 | 🆕 |
| [Spell Totem](https://poe2db.tw/us/Spell_Totem) | — | Spells Cast by Totems have (0—10)% increased Cast Speed per Summoned Totem | — | 15 | 🆕 |
| [Trail of Caltrops](https://poe2db.tw/us/Trail_of_Caltrops) | 🟢 DEX | Deals (0—20)% more Physical damage | +(0—5) to maximum number of Caltrops allowed | 30 |  |
| [Voltaic Barrier](https://poe2db.tw/us/Voltaic_Barrier) | — | Chains +(0—2) times | — | 3 | 🆕 |
| [Walking Calamity](https://poe2db.tw/us/Walking_Calamity) | — | (0—50)% chance to not consume Glory | — | 75 | 🆕 |
| [Wind Dancer](https://poe2db.tw/us/Wind_Dancer) | 🟢 DEX | (0—50)% more damage per stage | +(0—0.4) metres to explosion radius | 75 |  |

## Curses

_Hexes you cast onto enemies. Several curses share a `(0—50)% faster Curse Activation` gemling bonus._  (5 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Despair](https://poe2db.tw/us/Despair) | 🔵 INT | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |  |
| [Elemental Weakness](https://poe2db.tw/us/Elemental_Weakness) | 🔵 INT | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |  |
| [Enfeeble](https://poe2db.tw/us/Enfeeble) | 🔵 INT | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |  |
| [Temporal Chains](https://poe2db.tw/us/Temporal_Chains) | 🔵 INT | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |  |
| [Vulnerability](https://poe2db.tw/us/Vulnerability) | 🔵 INT | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |  |

## Marks

_Single-target marks. Quality affects cost or reapplication._  (3 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Freezing Mark](https://poe2db.tw/us/Freezing_Mark) | — | (0—50)% reduced Mana Cost | — | 75 | 🆕 |
| [Sniper's Mark](https://poe2db.tw/us/Snipers_Mark) | 🟢 DEX | Marked enemy deals (0—10)% less damage | Next Critical Hit against Marked Enemy has (0—15)% increased Critical Damage Bonus | 15 |  |
| [Voltaic Mark](https://poe2db.tw/us/Voltaic_Mark) | 🟢 DEX | (0—50)% reduced Mana Cost | Hits against Marked enemy cause +(0—20)% increased Electrocute buildup | 75 |  |

## Heralds

_Persistent reservation buffs that empower a specific damage type._  (5 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Herald of Ash](https://poe2db.tw/us/Herald_of_Ash) | 🔴 STR | Buff grants (0—20)% increased Fire damage | An additional +(0—5)% of Overkill damage contributes to base Ignite damage | 30 |  |
| [Herald of Blood](https://poe2db.tw/us/Herald_of_Blood) | — | Buff grants (0—15)% increased Physical damage | — | 22.5 | 🆕 |
| [Herald of Ice](https://poe2db.tw/us/Herald_of_Ice) | — | Buff grants (0—20)% increased Cold damage | — | 30 | 🆕 |
| [Herald of Plague](https://poe2db.tw/us/Herald_of_Plague) | 🟢 DEX | (0—30)% more Area of Effect | (0—20)% chance to Hinder enemies on spreading Poison to them | 45 |  |
| [Herald of Thunder](https://poe2db.tw/us/Herald_of_Thunder) | 🟢 DEX | Buff grants (0—20)% increased Lightning damage | Lightning Bolts strike the targets of your next (0—2) Attack Hits after killing a Shocked enemy with Attack damage | 30 |  |

## Warcries

_Shout effects that buff you or debuff enemies in an area._  (3 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Arctic Howl](https://poe2db.tw/us/Arctic_Howl) | — | (0—20)% chance to not count Empowered Attacks | — | 30 | 🆕 |
| [Seismic Cry](https://poe2db.tw/us/Seismic_Cry) | 🔴 STR | Gains (0—20)% of Physical damage as Fire damage | Empowered Attack Aftershocks deal (0—10)% more damage | 30 |  |
| [Skeletal Brute](https://poe2db.tw/us/Skeletal_Brute) | 🔵 INT | Minions have (0—30)% more Maximum Life | Minions cause (0—40)% more Stun buildup | 45 |  |

## Auras, Presences & Persistent Buffs

_Persistent reservation skills (auras, presences, offerings, body buffs)._  (33 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Alchemist's Boon](https://poe2db.tw/us/Alchemists_Boon) | 🟢 DEX | Grants (0—20)% increased Attack speed during any Life Flask Effect  ·  Grants (0—20)% increased cast speed during any Mana Flask Effect | Grants you (0—0.03) Flask charges per second | 30 |  |
| [Archmage](https://poe2db.tw/us/Archmage) | 🔵 INT | Non-Channelling Spells Gain (0—1)% of Damage as extra Lightning damage for each 100 maximum Mana you have  ·  Non-Channelling Spells cost an additional (0—2)% of your maximum Mana | (0—10)% increased Reservation Efficiency | 1.5 |  |
| [Arctic Armour](https://poe2db.tw/us/Arctic_Armour) | 🔵 INT | Buff grants (0—20)% increased Armour per Stage | Gains a Stage every seconds, up to a maximum of (0—1) Stages | 30 |  |
| [Attrition](https://poe2db.tw/us/Attrition) | — | (0—40)% increased Presence Area of Effect | — | 60 | 🆕 |
| [Barkskin](https://poe2db.tw/us/Barkskin) | — | (0—20)% more Skill Effect Duration | — | 30 | 🆕 |
| [Berserk](https://poe2db.tw/us/Berserk) | 🔴 STR | Buff grants +(0—8) to maximum Rage | Grants (0—10)% increased Rage effect | 12 |  |
| [Briarpatch](https://poe2db.tw/us/Briarpatch) | — | Thorny Ground radius is (0—0.6) metres | — | 0.9 | 🆕 |
| [Charge Regulation](https://poe2db.tw/us/Charge_Regulation) | — | Buff grants (0—2)% increased damage per Charge | — | 3 | 🆕 |
| [Combat Frenzy](https://poe2db.tw/us/Combat_Frenzy) | 🟢 DEX | (-1 — 0) seconds to delay on gaining a Frenzy Charge | (0—10)% chance to gain an additional Charge | — |  |
| [Convalescence](https://poe2db.tw/us/Convalescence) | 🔵 INT | (0—30)% increased Cooldown Recovery Rate | +(0—0.5) seconds to Buff duration | 45 |  |
| [Defiance Banner](https://poe2db.tw/us/Defiance_Banner) | — | (0—30)% more Area of Effect | — | 45 | 🆕 |
| [Dread Banner](https://poe2db.tw/us/Dread_Banner) | — | (0—30)% more Area of Effect | — | 45 | 🆕 |
| [Elemental Conflux](https://poe2db.tw/us/Elemental_Conflux) | 🔵 INT | (0—4) second duration between Element randomisations | Buff grants (0—10)% more damage with the affected Element | 6 |  |
| [Emergency Reload](https://poe2db.tw/us/Emergency_Reload) | — | Buff Empowers bolts with (0—10)% more damage | — | 15 | 🆕 |
| [Eternal Rage](https://poe2db.tw/us/Eternal_Rage) | 🔴 STR | (0—15)% increased Spirit Reservation Efficiency | Regenerate (0—0.5) Rage per second | 22.5 |  |
| [Ghost Dance](https://poe2db.tw/us/Ghost_Dance) | — | Maximum (0—1) Ghost Shrouds | — | 1.5 | 🆕 |
| [Iron Ward](https://poe2db.tw/us/Iron_Ward) | 🔴 STR | Deals (0—20)% more Physical damage | (0—50)% more Stun buildup | 30 |  |
| [Leylines](https://poe2db.tw/us/Leylines) | — | Leyline radius is (0—1) metre | — | 1.5 | 🆕 |
| [Lingering Illusion](https://poe2db.tw/us/Lingering_Illusion) | — | (0—40)% increased Spirit Reservation Efficiency | — | 60 | 🆕 |
| [Mana Remnants](https://poe2db.tw/us/Mana_Remnants) | 🔵 INT | Buff grants (0—40)% increased Mana Regeneration Rate | Each Remnant grants (0—40) Mana | 60 |  |
| [Mantra of Destruction](https://poe2db.tw/us/Mantra_of_Destruction) | — | Purple Flames of Chayula Duration is (0—0.05) seconds | — | 0.08 | 🆕 |
| [Plague Bearer](https://poe2db.tw/us/Plague_Bearer) | 🟢 DEX | (0—50)% increased Magnitude of Poison on targets that are not Poisoned | Stores (0—2)% of Expected Poison damage, up to Deals Physical damage equal to the stored Poison | 75 |  |
| [Refutation](https://poe2db.tw/us/Refutation) | — | Buff duration is (0—1) second | — | 1.5 | 🆕 |
| [Remnants of Kalguur](https://poe2db.tw/us/Remnants_of_Kalguur) | — | % chance to spawn a Remnant on Stunning an Enemy | — | — | 🆕 |
| [Savage Fury](https://poe2db.tw/us/Savage_Fury) | — | Gain (0—1) additional Fury on Attack Hit | — | 1.5 | 🆕 |
| [Scavenged Plating](https://poe2db.tw/us/Scavenged_Plating) | 🔴 STR | (0—1)% more Armour per Scavenged Plating | +(0—2) seconds to Scavenged Plating duration | 1.5 |  |
| [Shard Scavenger](https://poe2db.tw/us/Shard_Scavenger) | — | (0—20)% more Skill Effect Duration | — | 30 | 🆕 |
| [Siphon Elements](https://poe2db.tw/us/Siphon_Elements) | 🔵 INT | Remnants created by Supported Skills can be collected from (0—30)% further away | +(0—2)% chance per Power to spawn a Cold Remnant on Freezing a target +(0—2)% chance to spawn a Fire Remnant on Igniting a non-Ignited target +(0—2)% chance to spawn a Lightning Remnant on Shocking a non-Shocked target | 45 |  |
| [Time of Need](https://poe2db.tw/us/Time_of_Need) | 🔴 STR | Buff grants (0—20)% increased Life Regeneration Rate | Blessing recovers (0—40) Life and removes Curses and Elemental Ailments | 30 |  |
| [Toxic Domain](https://poe2db.tw/us/Toxic_Domain) | 🟢 DEX | Effects of Toxic Bloom Linger on you for (0—2) seconds | active skill base area of effect radius [0,3] | 3 |  |
| [Trinity](https://poe2db.tw/us/Trinity) | — | (0—20)% of Physical damage Converted to a random Element | — | 30 | 🆕 |
| [War Banner](https://poe2db.tw/us/War_Banner) | — | (0—30)% more Area of Effect | — | 45 | 🆕 |
| [Withering Presence](https://poe2db.tw/us/Withering_Presence) | 🔵 INT | Withers enemies in your Presence every (-0.5 — 0) seconds | Withered duration is (0—1) second | — |  |

## Totems & Placed Objects

_Stationary helpers. Several gems add to the totem limit._  (4 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Artillery Ballista](https://poe2db.tw/us/Artillery_Ballista) | — | Limit (0—1) Totem | — | 1.5 | 🆕 |
| [Dark Effigy](https://poe2db.tw/us/Dark_Effigy) | 🔵 INT | Limit (0—1) Totem | +(0—0.2) metres to Impact radius | 1.5 |  |
| [Shockwave Totem](https://poe2db.tw/us/Shockwave_Totem) | 🔴 STR | Limit (0—1) Totem | +(0—4) seconds to Totem duration | 1.5 |  |
| [Siege Ballista](https://poe2db.tw/us/Siege_Ballista) | — | Limit (0—1) Totem | — | 1.5 | 🆕 |

## Minions & Summons

_Summoned units. Quality often adds minion-wide damage/life/AS._  (23 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Bone Offering](https://poe2db.tw/us/Bone_Offering) | 🔵 INT | (0—30)% more Skill Effect Duration | Shielded Minions take (0—30)% less Damage for 1 second after Shield is lost | 45 |  |
| [Companion](https://poe2db.tw/us/Companion%3A_%7B0%7D) | 🟢 DEX | (0—20)% more Minion Attack Speed | — | 30 | 🆕 |
| [Eternal March](https://poe2db.tw/us/Eternal_March) | — | (0—40)% increased Cooldown Recovery Rate | — | 60 | 🆕 |
| [Grim Feast](https://poe2db.tw/us/Grim_Feast) | 🔵 INT | Remnants created by Supported Skills can be collected from (0—40)% further away | Remnants store (0—5)% of Minion maximum Life | 60 |  |
| [Pain Offering](https://poe2db.tw/us/Pain_Offering) | 🔵 INT | Aura grants Minions (0—20)% increased Attack and Cast Speed | +(0—2.4) metres to Minion Aura radius | 30 |  |
| [Raging Spirits](https://poe2db.tw/us/Raging_Spirits) | 🔵 INT | Minions deal (0—50)% more damage | Limit (0—2) Summoned Raging Spirits | 75 |  |
| [Raise Zombie](https://poe2db.tw/us/Raise_Zombie) | 🔵 INT | Limit (0—4) Raised Zombies | (0—25)% increased effect of Empowerment on Raised Zombies | 6 |  |
| [Ravenous Swarm](https://poe2db.tw/us/Ravenous_Swarm) | 🔵 INT | Spawn a new Swarm once every (-2 — 0) seconds | +(0—1) metres to swarm Attack radius | — |  |
| [Rhoa Mount](https://poe2db.tw/us/Rhoa_Mount) | 🟢 DEX | (0—30)% increased Reservation Efficiency | Minions have (0—20)% more Maximum Life | 45 |  |
| [Sacrifice](https://poe2db.tw/us/Sacrifice) | 🔵 INT | Minions have (0—40)% increased maximum Life | Minions Revive +(0—5)% more quickly | 60 |  |
| [Skeletal Arsonist](https://poe2db.tw/us/Skeletal_Arsonist) | 🔵 INT | Fires +(0—2) Projectiles | Deals additional Fire damage equal to +(0—4)% of Minion 's maximum Life | 3 |  |
| [Skeletal Cleric](https://poe2db.tw/us/Skeletal_Cleric) | 🔵 INT | Minions take (0—40)% reduced Damage | Revived Skeletons are immune to Damage for (0—3) seconds after being Revived | 60 |  |
| [Skeletal Frost Mage](https://poe2db.tw/us/Skeletal_Frost_Mage) | 🔵 INT | (0—20)% increased Spirit Reservation Efficiency | Minions deal (0—20)% more damage | 30 |  |
| [Skeletal Reaver](https://poe2db.tw/us/Skeletal_Reaver) | 🔵 INT | Break Armour equal to (0—30)% of Physical damage dealt | Minions have (0—20)% increased effect of Rage | 45 |  |
| [Skeletal Sniper](https://poe2db.tw/us/Skeletal_Sniper) | 🔵 INT | Deals (0—50)% more Fire Damage | Minions deal (0—20)% more damage | 75 |  |
| [Skeletal Storm Mage](https://poe2db.tw/us/Skeletal_Storm_Mage) | 🔵 INT | (0—30)% increased Minion Cast Speed | Minions gain (0—20)% of their maximum Life as Extra maximum Energy Shield | 45 |  |
| [Skyfall](https://poe2db.tw/us/Skyfall) | — | (0—20)% increased Damage with Hits against Frozen Enemies | — | 30 | 🆕 |
| [Soul Offering](https://poe2db.tw/us/Soul_Offering) | 🔵 INT | Buff grants you (0—20)% increased Spell damage | +(0—1) second to Spike duration | 30 |  |
| [Tame Beast](https://poe2db.tw/us/Tame_Beast) | 🟢 DEX | (0—50)% reduced Mana Cost | +(0—1.6) seconds to Wisp duration | 75 |  |
| [Unearth](https://poe2db.tw/us/Unearth) | 🔵 INT | (0—50)% more Minion Attack Speed | +(0—5) seconds to Bone Construct duration Minions have (0—50)% increased Movement Speed | 75 |  |
| [Verisium Manifestations](https://poe2db.tw/us/Verisium_Manifestations) | — | +(0—2) to Verisium Manifestation Limit | — | 3 | 🆕 |
| [Wardbound Minions](https://poe2db.tw/us/Wardbound_Minions) | — | +(0—5) s to Minion duration | — | 7.5 | 🆕 |
| [Wolf Pack](https://poe2db.tw/us/Wolf_Pack) | — | (0—20)% more Minion Attack Speed | — | 30 | 🆕 |

## Movement Skills

_Mobility and traversal._  (9 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Blink](https://poe2db.tw/us/Blink) | 🔵 INT | Teleports + (0—2.5) metres | (0—10)% increased Cooldown Recovery Rate | 3.75 |  |
| [Disengage](https://poe2db.tw/us/Disengage) | 🟢 DEX | +(0—1) metres to Melee Strike Range | (0—20)% chance for an additional Shockwave | 1.5 |  |
| [Gathering Storm](https://poe2db.tw/us/Gathering_Storm) | — | (0—30)% chance for Lightning Damage with Hits to be Lucky | — | 45 | 🆕 |
| [Leap Slam](https://poe2db.tw/us/Leap_Slam) | 🔴 STR | (0—20)% more Area of Effect | (0—20)% more Damage with Hits against Enemies with Fully Broken Armour | 30 |  |
| [Rampage](https://poe2db.tw/us/Rampage) | — | (0—20)% more Area of Effect | — | 30 | 🆕 |
| [Shield Charge](https://poe2db.tw/us/Shield_Charge) | 🔴 STR | (0—30)% increased maximum travel distance | Deals up to an additional +(0—40)% more Damage, based on the distance travelled | 45 |  |
| [Stampede](https://poe2db.tw/us/Stampede) | 🔴 STR | (0—20)% more Area of Effect | (0—20)% chance to cause an additional Aftershock | 30 |  |
| [Thunderous Leap](https://poe2db.tw/us/Thunderous_Leap) | 🟢 DEX | (0—40)% chance to cause an additional Aftershock | (0—30)% chance to leave Shocked Ground when Detonating Spears | 60 |  |
| [Vaulting Impact](https://poe2db.tw/us/Vaulting_Impact) | — | (0—50)% more Damage against Heavy Stunned Enemies | — | 75 | 🆕 |

## Spell Skills

_Direct-cast spells (projectiles, novas, walls, etc.)._  (45 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Animus Exchange](https://poe2db.tw/us/Animus_Exchange) | — | Gain Runic Ward equal to (0—5)% of Sacrificed Life | — | 7.5 | 🆕 |
| [Arc](https://poe2db.tw/us/Arc) | 🔵 INT | Projectiles deal (0—3)% more Damage with Hits for each remaining Chain | Chains +(0—2) times | 4.5 |  |
| [Ball Lightning](https://poe2db.tw/us/Ball_Lightning) | 🔵 INT | (-30 — 0)% more Projectile Speed | Bolts target enemies within +(0—0.4) metres | — |  |
| [Barrage](https://poe2db.tw/us/Barrage) | 🟢 DEX | (0—20)% chance to not remove Charges on use | Repeats deal +(0—5)% more Damage | 30 |  |
| [Bitter Dead](https://poe2db.tw/us/Bitter_Dead) | — | (0—10)% chance to not destroy Consumed Corpse | — | 15 | 🆕 |
| [Bone Cage](https://poe2db.tw/us/Bone_Cage) | 🔵 INT | (0—40)% more Magnitude of Bleeding inflicted | Pins Enemies as though dealing +(0—50)% more Damage | 60 |  |
| [Bonestorm](https://poe2db.tw/us/Bonestorm) | 🔵 INT | (0—20)% chance to not remove Charges on use | (0—10)% more Cast Speed | 30 |  |
| [Charged Staff](https://poe2db.tw/us/Charged_Staff) | — | (0—20)% chance to not remove Charges on use | — | 30 | 🆕 |
| [Comet](https://poe2db.tw/us/Comet) | 🔵 INT | (0—40)% increased Damage with Hits against Frozen Enemies | (0—10)% chance to Echo | 60 |  |
| [Contagion](https://poe2db.tw/us/Contagion) | 🔵 INT | (0—50)% more Area of Effect | Contagion targets (0—2) additional Enemies when Cast | 75 |  |
| [Detonate Dead](https://poe2db.tw/us/Detonate_Dead) | 🔵 INT | Converts (0—60)% of Physical damage to Fire damage | +(0—0.4) metres to explosion radius | 90 |  |
| [Detonate Living](https://poe2db.tw/us/Detonate_Living) | — | +(0—0.4) metres to explosion radius | — | 0.6 | 🆕 |
| [Ember Fusillade](https://poe2db.tw/us/Ember_Fusillade) | 🔵 INT | (0—40)% reduced Skill Effect Duration  ·  (0—20)% less Cast Speed | +(0—2)% more Damage for each previous Ember fired in sequence | 60 |  |
| [Entangle](https://poe2db.tw/us/Entangle) | — | +(0—4) to Fissure Limit | — | 6 | 🆕 |
| [Essence Drain](https://poe2db.tw/us/Essence_Drain) | 🔵 INT | Chains +(0—4) times | +(0—1) second to Debuff duration | 6 |  |
| [Eye of Winter](https://poe2db.tw/us/Eye_of_Winter) | 🔵 INT | Projectiles have (0—50)% chance to Return to you | (0—30)% increased Projectile Speed | 75 |  |
| [Fireball](https://poe2db.tw/us/Fireball) | 🔵 INT | + (0—10)% chance to fire 8 additional Projectiles in a circle | +(0—10)% chance to fire 2 additional Projectiles | 15 |  |
| [Firestorm](https://poe2db.tw/us/Firestorm) | 🔵 INT | (0—20)% chance to not remove an Infusion but still count as consuming them | +(0—0.2) metres to impact radius | 30 |  |
| [Flame Wall](https://poe2db.tw/us/Flame_Wall) | 🔵 INT | Deals (0—40)% more Fire Damage | Inflicts (0—20)% more Flammability Magnitude | 60 |  |
| [Flameblast](https://poe2db.tw/us/Flameblast) | 🔵 INT | (0—40)% more Magnitude of Damaging Ailments per Stage | (0—20)% more Cast Speed | 60 |  |
| [Frost Bomb](https://poe2db.tw/us/Frost_Bomb) | 🔵 INT | Limit (0—3) Frost Bomb | +(0—10)% maximum Elemental Exposure applied | 4.5 |  |
| [Frost Darts](https://poe2db.tw/us/Frost_Darts) | 🔵 INT | Forks (0—2) additional Times | +(0—10)% chance to fire 2 additional Projectiles | 3 |  |
| [Frost Wall](https://poe2db.tw/us/Frost_Wall) | 🔵 INT | (0—400)% increased Ice Crystal Life | (0—20)% increased Cooldown Recovery Rate | 600 |  |
| [Frostbolt](https://poe2db.tw/us/Frostbolt) | 🔵 INT | (0—40)% more Projectile Speed | (0—20)% more Projectile Damage after Piercing an Enemy | 60 |  |
| [Frostflame Nova](https://poe2db.tw/us/Frostflame_Nova) | — | (0—20)% increased Damage with Hits against Frozen Enemies | — | 30 | 🆕 |
| [Grim Pillars](https://poe2db.tw/us/Grim_Pillars) | — | +(0—0.4) metres to eruption radius | — | 0.6 | 🆕 |
| [Hexblast](https://poe2db.tw/us/Hexblast) | 🔵 INT | (0—40)% more Critical Hit Chance | (0—10)% more Damage per 1 second of remaining duration on removed Curse | 60 |  |
| [Hollow Shell](https://poe2db.tw/us/Hollow_Shell) | — | +(0—2) seconds to Guard duration | — | 3 | 🆕 |
| [Ice Nova](https://poe2db.tw/us/Ice_Nova) | 🔵 INT | (0—40)% chance to not remove an Infusion but still count as consuming them | (0—20)% more Damage with Hits against Enemies that are Chilled | 60 |  |
| [Incinerate](https://poe2db.tw/us/Incinerate) | 🔵 INT | + (0—2) seconds of Maximum fuel | (0—20)% more Ignite duration | 3 |  |
| [Lightning Conduit](https://poe2db.tw/us/Lightning_Conduit) | 🔵 INT | (0—4) additional bolts if a Shocked enemy is in the target area | (0—20)% more Lightning Damage | 6 |  |
| [Lightning Warp](https://poe2db.tw/us/Lightning_Warp) | 🔵 INT | (0—40)% more Cast Speed | (0—10)% increased Magnitude of Shock inflicted | 60 |  |
| [Living Bomb](https://poe2db.tw/us/Living_Bomb) | 🔵 INT | Deals (0—50)% more Fire Damage  ·  Explodes after enemy is dealt damage equal to (0—200)% of its Ailment Threshold | Inflicts (0—20)% more Flammability Magnitude | 75 |  |
| [Mana Tempest](https://poe2db.tw/us/Mana_Tempest) | 🔵 INT | (-8 — 0)% of Mana and Life spent while in the storm is  ·  added to this Skill's Mana Cost per Second | Effects of Mana Tempest linger for (0—2) seconds after leaving the Tempest | — |  |
| [Orb of Storms](https://poe2db.tw/us/Orb_of_Storms) | 🔵 INT | Orb expires after firing (0—6) bolts | Chains +(0—3) times | 9 |  |
| [Powered by Verisium](https://poe2db.tw/us/Powered_by_Verisium) | — | (0—20)% chance to gain an additional Infusion | — | 30 | 🆕 |
| [Profane Ritual](https://poe2db.tw/us/Profane_Ritual) | 🔵 INT | (0—100)% more Skill Effect Duration | (0—10)% chance to not destroy Consumed Corpse | 150 |  |
| [Runic Reprieve](https://poe2db.tw/us/Runic_Reprieve) | — | You take (0—10)% of damage from Blocked Hits | — | 15 | 🆕 |
| [Snap](https://poe2db.tw/us/Snap) | 🔵 INT | (0—100)% increased Cooldown Recovery Rate | (0—10)% chance to spawn an additional Infusion Remnant | 150 |  |
| [Spark](https://poe2db.tw/us/Spark) | 🔵 INT | Fires +(0—4) Projectiles | (0—30)% increased Projectile Speed | 6 |  |
| [Thrashing Vines](https://poe2db.tw/us/Thrashing_Vines) | — | (0—30)% chance to Impale Enemies on Hit | — | 45 | 🆕 |
| [Thunderstorm](https://poe2db.tw/us/Thunderstorm) | — | (0—20)% more Area of Effect | — | 30 | 🆕 |
| [Tornado](https://poe2db.tw/us/Tornado) | — | + (0—2) to Limit of Tornadoes | — | 3 | 🆕 |
| [Triskelion Cascade](https://poe2db.tw/us/Triskelion_Cascade) | — | Empowered Skill has (0—5)% more area of effect | — | 7.5 | 🆕 |
| [Volcano](https://poe2db.tw/us/Volcano) | — | (0—20)% more Skill Effect Duration | — | 30 | 🆕 |

## Attack Skills

_Weapon-based attacks: slams, strikes, bow, crossbow and spear skills._  (93 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Armour Breaker](https://poe2db.tw/us/Armour_Breaker) | 🔴 STR | Deals (0—20)% more Physical damage | Break (0—20)% increased Armour | 30 |  |
| [Armour Piercing Rounds](https://poe2db.tw/us/Armour_Piercing_Rounds) | — | (0—20)% more Attack Speed | — | 30 | 🆕 |
| [Blood Hunt](https://poe2db.tw/us/Blood_Hunt) | 🟢 DEX | Enemies lose Life equal to + (0—4)% of Consumed Blood Loss | +(0—0.4) metres to explosion radius | 6 |  |
| [Boneshatter](https://poe2db.tw/us/Boneshatter) | 🔴 STR | Shockwave radius is (0—2) metres | (0—20)% increased Attack Speed | 3 |  |
| [Cluster Grenade](https://poe2db.tw/us/Cluster_Grenade) | — | (0—40)% reduced Detonation Time | — | 60 | 🆕 |
| [Conductive Runes](https://poe2db.tw/us/Conductive_Runes) | — | Runes emerge within a (0—0.6) metre length cone | — | 0.9 | 🆕 |
| [Cross Slash](https://poe2db.tw/us/Cross_Slash) | — | Converts (0—40)% of Physical damage to Cold damage | — | 60 | 🆕 |
| [Cull The Weak](https://poe2db.tw/us/Cull_The_Weak) | 🟢 DEX | (0—20)% chance to gain an additional random Charge when you gain a Charge | (0—20)% chance to gain an additional Charge | 30 |  |
| [Detonating Arrow](https://poe2db.tw/us/Detonating_Arrow) | 🟢 DEX | (0—40)% more Ignite Magnitude | +(0—1) to number of Maximum Stages | 60 |  |
| [Devour](https://poe2db.tw/us/Devour) | — | (0—20)% chance to gain an additional Charge | — | 30 | 🆕 |
| [Earthquake](https://poe2db.tw/us/Earthquake) | 🔴 STR | (0—40)% more Magnitude of Damaging Ailments inflicted | +(0—2) to Jagged Ground patch Limit | 60 |  |
| [Earthshatter](https://poe2db.tw/us/Earthshatter) | 🔴 STR | (0—20)% chance to cause an additional Aftershock | (0—6)% more Damage with Hits for each Spike | 30 |  |
| [Electrocuting Arrow](https://poe2db.tw/us/Electrocuting_Arrow) | 🟢 DEX | Targets with attached Rods take (0—20)% increased damage | Hits against targets with attached Rods gain (0—10)% of Damage as extra Lightning Damage | 30 |  |
| [Elemental Sundering](https://poe2db.tw/us/Elemental_Sundering) | 🟢 DEX | (0—20)% more Critical Hit Chance | +(0—0.2) metres to Pulse radius | 30 |  |
| [Explosive Grenade](https://poe2db.tw/us/Explosive_Grenade) | — | Fires +(0—2) Projectiles | — | 3 | 🆕 |
| [Explosive Shot](https://poe2db.tw/us/Explosive_Shot) | — | +(0—2) Bolts loaded per clip | — | 3 | 🆕 |
| [Explosive Spear](https://poe2db.tw/us/Explosive_Spear) | 🟢 DEX | (0—20)% chance to not remove Charges on use | +(0—0.4) metres to Explosion radius | 30 |  |
| [Falling Thunder](https://poe2db.tw/us/Falling_Thunder) | — | (0—20)% chance to not remove Charges on use | — | 30 | 🆕 |
| [Fangs of Frost](https://poe2db.tw/us/Fangs_of_Frost) | 🟢 DEX | +(0—1) metres to Melee Strike Range | (0—15)% chance to not consume Parried Debuff | 1.5 |  |
| [Flame Breath](https://poe2db.tw/us/Flame_Breath) | — | (0—20)% more Area of Effect | — | 30 | 🆕 |
| [Flash Grenade](https://poe2db.tw/us/Flash_Grenade) | — | Gain (0—10)% damage as Extra Lightning Damage  ·  active skill base all damage % to gain as cold [0,10] | — | 15 | 🆕 |
| [Flicker Strike](https://poe2db.tw/us/Flicker_Strike) | — | (0—20)% chance to not remove Charges on use | — | 30 | 🆕 |
| [Forge Hammer](https://poe2db.tw/us/Forge_Hammer) | 🔴 STR | Gain (0—20)% damage as Extra Fire Damage | (0—10)% increased Cooldown Recovery Rate | 30 |  |
| [Fragmentation Rounds](https://poe2db.tw/us/Fragmentation_Rounds) | — | (0—100)% more reload speed | — | 150 | 🆕 |
| [Freezing Salvo](https://poe2db.tw/us/Freezing_Salvo) | 🟢 DEX | Maximum (0—4) Seals | (0—40)% more Freeze Buildup | 6 |  |
| [Frozen Locus](https://poe2db.tw/us/Frozen_Locus) | — | base number of frozen locus allowed [0,1] | — | — | 🆕 |
| [Furious Slam](https://poe2db.tw/us/Furious_Slam) | — | (0—20)% more Area of Effect | — | 30 | 🆕 |
| [Fury of the Mountain](https://poe2db.tw/us/Fury_of_the_Mountain) | — | (0—20)% more Attack Speed | — | 30 | 🆕 |
| [Galvanic Shards](https://poe2db.tw/us/Galvanic_Shards) | — | +(0—2) Bolts loaded per clip | — | 3 | 🆕 |
| [Gas Arrow](https://poe2db.tw/us/Gas_Arrow) | 🟢 DEX | Deals (0—20)% more Fire Damage | +(0—0.4) metres to impact radius | 30 |  |
| [Gas Grenade](https://poe2db.tw/us/Gas_Grenade) | — | Deals (0—20)% more Fire Damage | — | 30 | 🆕 |
| [Glacial Bolt](https://poe2db.tw/us/Glacial_Bolt) | — | Explosion radius is (0—1) metre | — | 1.5 | 🆕 |
| [Glacial Cascade](https://poe2db.tw/us/Glacial_Cascade) | — | (0—20)% more Attack Speed | — | 30 | 🆕 |
| [Glacial Lance](https://poe2db.tw/us/Glacial_Lance) | 🟢 DEX | (0—20)% chance to not remove Charges on use | active skill base area of effect radius [0,4] | 30 |  |
| [Hailstorm Rounds](https://poe2db.tw/us/Hailstorm_Rounds) | — | Penetrates (0—60)% Cold Resistance | — | 90 | 🆕 |
| [Hammer of the Gods](https://poe2db.tw/us/Hammer_of_the_Gods) | 🔴 STR | (0—50)% chance to not consume Glory | +(0—0.4) metres to impact radius | 75 |  |
| [High Velocity Rounds](https://poe2db.tw/us/High_Velocity_Rounds) | — | Deals (0—20)% more Physical damage | — | 30 | 🆕 |
| [Ice Shards](https://poe2db.tw/us/Ice_Shards) | — | (0—200)% more Freeze Buildup | — | 300 | 🆕 |
| [Ice Shot](https://poe2db.tw/us/Ice_Shot) | 🟢 DEX | (0—40)% reduced Movement Speed Penalty from using Skills while moving | active skill chill effect +% final [0,30] | 60 |  |
| [Ice Strike](https://poe2db.tw/us/Ice_Strike) | — | (0—20)% more Critical Hit Chance | — | 30 | 🆕 |
| [Incendiary Shot](https://poe2db.tw/us/Incendiary_Shot) | — | Fires (0—4) fragments per shot | — | 6 | 🆕 |
| [Killing Palm](https://poe2db.tw/us/Killing_Palm) | — | Recover (0—10)% of maximum Life over four seconds on Culling an Enemy | — | 15 | 🆕 |
| [Lightning Arrow](https://poe2db.tw/us/Lightning_Arrow) | 🟢 DEX | (0—30)% chance for Lightning Damage with Hits to be Lucky | (0—40)% more chance to Shock | 45 |  |
| [Lightning Rod](https://poe2db.tw/us/Lightning_Rod) | 🟢 DEX | (0—20)% more Attack Speed | (0—20)% chance to cause an additional Burst on impact | 30 |  |
| [Lightning Spear](https://poe2db.tw/us/Lightning_Spear) | 🟢 DEX | Benefits from consuming Charges have (0—20)% chance to be doubled | Fires +(0—2) bolts | 30 |  |
| [Lunar Assault](https://poe2db.tw/us/Lunar_Assault) | — | Penetrates (0—20)% Cold Resistance | — | 30 | 🆕 |
| [Magnetic Salvo](https://poe2db.tw/us/Magnetic_Salvo) | 🟢 DEX | (0—20)% more Lightning Damage | Fires up to +(0—4) missiles | 30 |  |
| [Molten Blast](https://poe2db.tw/us/Molten_Blast) | 🔴 STR | Fires +(0—2) Projectiles | (0—30)% chance to inflict Exposure on Hit | 3 |  |
| [Oil Barrage](https://poe2db.tw/us/Oil_Barrage) | — | (0—20)% chance to not remove Charges on use | — | 30 | 🆕 |
| [Oil Grenade](https://poe2db.tw/us/Oil_Grenade) | — | Exposure lowers Total Elemental  ·  Resistances by an additional (0—10)% | — | 15 | 🆕 |
| [Perfect Strike](https://poe2db.tw/us/Perfect_Strike) | 🔴 STR | (0—40)% more Attack Speed | Inflicts (0—20)% more Flammability Magnitude | 60 |  |
| [Permafrost Bolts](https://poe2db.tw/us/Permafrost_Bolts) | — | (0—100)% more reload speed | — | 150 | 🆕 |
| [Plasma Blast](https://poe2db.tw/us/Plasma_Blast) | — | Fires +(0—2) Projectiles | — | 3 | 🆕 |
| [Poisonburst Arrow](https://poe2db.tw/us/Poisonburst_Arrow) | 🟢 DEX | Break Armour equal to (0—20)% of Poison damage | (0—10)% more Magnitude of Poison inflicted | 30 |  |
| [Primal Strikes](https://poe2db.tw/us/Primal_Strikes) | 🟢 DEX | (0—20)% more Critical Hit Chance | (0—20)% increased Attack Speed | 30 |  |
| [Rain of Arrows](https://poe2db.tw/us/Rain_of_Arrows) | 🟢 DEX | Deals (0—20)% more damage | Arrows fall (0—20)% faster | 30 |  |
| [Rake](https://poe2db.tw/us/Rake) | 🟢 DEX | (0—20)% chance to Aggravate Bleeding on targets you Hit with Attacks | base additional damage from distance +% final [0,30] | 30 |  |
| [Rapid Assault](https://poe2db.tw/us/Rapid_Assault) | 🟢 DEX | (0—40)% more Magnitude of Bleeding inflicted | (0—20)% chance to leave an additional spearhead in the target | 60 |  |
| [Rapid Shot](https://poe2db.tw/us/Rapid_Shot) | — | +(0—30) to Maximum Heat | — | 45 | 🆕 |
| [Resonating Shield](https://poe2db.tw/us/Resonating_Shield) | 🔴 STR | (0—100)% increased Stun Threshold while Channelling | Break (0—20)% increased Armour | 150 |  |
| [Rolling Magma](https://poe2db.tw/us/Rolling_Magma) | — | Chains +(0—4) times | — | 6 | 🆕 |
| [Rolling Slam](https://poe2db.tw/us/Rolling_Slam) | 🔴 STR | Break Armour equal to (0—40)% of Physical damage dealt | (0—100)% increased Stun Threshold while using Skill | 60 |  |
| [Shield Wall](https://poe2db.tw/us/Shield_Wall) | 🔴 STR | Gains (0—20)% of Physical damage as Fire damage | (0—40)% more Damage if destroyed by your Skills | 30 |  |
| [Shockburst Rounds](https://poe2db.tw/us/Shockburst_Rounds) | — | (0—30)% more Area of Effect | — | 45 | 🆕 |
| [Shockchain Arrow](https://poe2db.tw/us/Shockchain_Arrow) | 🟢 DEX | (0—20)% more Attack Speed | (0—20)% more Lightning Damage | 30 |  |
| [Siege Cascade](https://poe2db.tw/us/Siege_Cascade) | — | +(0—3) Bolts loaded per clip | — | 4.5 | 🆕 |
| [Siphoning Strike](https://poe2db.tw/us/Siphoning_Strike) | — | (0—50)% chance to gain an additional Charge | — | 75 | 🆕 |
| [Snipe](https://poe2db.tw/us/Snipe) | 🟢 DEX | (0—20)% longer Perfect Timing window  ·  (0—20)% more Attack Speed | Explosion radius is (0—0.4) metres | 30 |  |
| [Spear of Solaris](https://poe2db.tw/us/Spear_of_Solaris) | 🟢 DEX | Deals (0—20)% more Fire Damage | (0—25)% chance to retain 40% of Glory on use | 30 |  |
| [Spearfield](https://poe2db.tw/us/Spearfield) | 🟢 DEX | (0—20)% more Attack Speed | Hazards created by this Skill have (0—10)% chance to rearm after they are triggered | 30 |  |
| [Spiral Volley](https://poe2db.tw/us/Spiral_Volley) | 🟢 DEX | Benefits from consuming Charges have (0—30)% chance to be doubled | Fires +(0—4) Projectiles | 45 |  |
| [Staggering Palm](https://poe2db.tw/us/Staggering_Palm) | — | Fires +(0—2) Projectiles | — | 3 | 🆕 |
| [Storm Lance](https://poe2db.tw/us/Storm_Lance) | 🟢 DEX | Fires +(0—2) Projectiles | base number of overcharged spears allowed [0,1] | 3 |  |
| [Storm Wave](https://poe2db.tw/us/Storm_Wave) | — | Wave length is + (0—4) metres | — | 6 | 🆕 |
| [Stormblast Bolts](https://poe2db.tw/us/Stormblast_Bolts) | — | +(0—2) Bolts loaded per clip | — | 3 | 🆕 |
| [Stormcaller Arrow](https://poe2db.tw/us/Stormcaller_Arrow) | 🟢 DEX | Fires +(0—2) Projectiles | (0—30)% increased Shock Duration | 3 |  |
| [Sunder](https://poe2db.tw/us/Sunder) | 🔴 STR | (0—20)% more Attack Speed | (0—50)% reduced Accuracy penalty based on distance | 30 |  |
| [Supercharged Slam](https://poe2db.tw/us/Supercharged_Slam) | 🔴 STR | (0—300)% more Stun buildup | +(0—1) maximum Stage | 450 |  |
| [Tempest Bell](https://poe2db.tw/us/Tempest_Bell) | — | bell hit limit [0,10] | — | — | 🆕 |
| [Tempest Flurry](https://poe2db.tw/us/Tempest_Flurry) | — | Final Strike targets (0—2) additional nearby enemies | — | 3 | 🆕 |
| [Tornado Shot](https://poe2db.tw/us/Tornado_Shot) | 🟢 DEX | + (0—2) to Limit of Tornadoes | Copied Projectiles deal +(0—15)% more damage | 3 |  |
| [Toxic Growth](https://poe2db.tw/us/Toxic_Growth) | 🟢 DEX | (0—40)% increased Poison Duration | Fires +(0—1) Pustule Limit +(0—1) pustule | 60 |  |
| [Twister](https://poe2db.tw/us/Twister) | 🟢 DEX | (0—20)% more Projectile Speed | (0—20)% chance for an additional twister | 30 |  |
| [Vine Arrow](https://poe2db.tw/us/Vine_Arrow) | 🟢 DEX | (0—40)% more Skill Effect Duration | Plant deals additional Chaos Damage per second equal to (0—10)% of Poison Damage per second | 60 |  |
| [Volcanic Fissure](https://poe2db.tw/us/Volcanic_Fissure) | 🔴 STR | Deals (0—20)% more Fire Damage | (0—20)% chance to cause an additional Aftershock | 30 |  |
| [Voltaic Grenade](https://poe2db.tw/us/Voltaic_Grenade) | — | (0—20)% more Lightning Damage | — | 30 | 🆕 |
| [Wave of Frost](https://poe2db.tw/us/Wave_of_Frost) | — | Enemies Frozen by this Skill take (0—40)% increased damage | — | 60 | 🆕 |
| [Whirling Assault](https://poe2db.tw/us/Whirling_Assault) | — | Deals (0—20)% more Physical damage | — | 30 | 🆕 |
| [Whirling Slash](https://poe2db.tw/us/Whirling_Slash) | 🟢 DEX | (0—10)% more Attack Speed | Collapse deals +(0—40)% more damage per additional stage | 15 |  |
| [Whirlwind Lance](https://poe2db.tw/us/Whirlwind_Lance) | 🟢 DEX | Elemental Whirlwinds Gain + (0—50)% of damage as damage of the corresponding Type | Collapse deals +(0—40)% more damage per additional stage | 75 |  |
| [Wind Blast](https://poe2db.tw/us/Wind_Blast) | — | Break Armour equal to (0—40)% of Physical damage dealt | — | 60 | 🆕 |
| [Wind Serpent's Fury](https://poe2db.tw/us/Wind_Serpents_Fury) | 🟢 DEX | Gains (0—20)% of Damage as Extra Chaos Damage | (0—30)% more Knockback Distance | 30 |  |
| [Wing Blast](https://poe2db.tw/us/Wing_Blast) | — | Deals (0—20)% more Physical damage | — | 30 | 🆕 |

## Other

_Anything that didn't fit elsewhere._  (4 gems)

| Gem | Attr | Gemling effect | Generic quality mod | @30% q | 0.5 |
|---|---|---|---|---|:---:|
| [Bind Spectre](https://poe2db.tw/us/Bind_Spectre) | 🔵 INT | (0—20)% increased Reservation Efficiency | Minions deal (0—20)% more damage | 30 |  |
| [Conductivity](https://poe2db.tw/us/Conductivity) | 🔵 INT | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |  |
| [Flammability](https://poe2db.tw/us/Flammability) | 🔵 INT | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |  |
| [Hypothermia](https://poe2db.tw/us/Hypothermia) | 🔵 INT | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |  |

## What else is in this repo

A normalized **PoE2 v0.5 gem catalog** built from the [Path of Building data export](https://github.com/repoe-fork/pob-data) — the backend for an AI-assisted build creator:

| File | What |
|---|---|
| `data/gemling_quality.json` | The 260-skill gemling table above, machine-readable |
| `data/skill_gems.json` | 399 active gems — tags, attribute, skill types, descriptions |
| `data/support_gems.json` | 571 support gems (538 PoB + 33 Lineage/external-granted) with rules |
| `data/support_compatibility.json` | Which supports work with which skills (both directions) |
| `data/spirit_gems.json`, `data/meta_gems.json` | Spirit / meta gem subsets |
| `data/uniques.json` | 395 unique items across every slot, with mods |
| `data/bases.json` | 1,715 base item types (weapon/armour/jewellery) with stats + requirements |
| `data/runes.json` | 283 runes / soul cores with their item-type-dependent mods |
| `data/jewels.json` | Jewel bases, uniques, cluster + timeless data |
| `pages/gemling_quality.html`, `pages/gem_catalog.html`, `pages/items_catalog.html` | Searchable static browsers |
| `data/CATALOG_SCHEMA.md` | Field schema + compatibility algorithm |

Together (gems + supports + compatibility + uniques + bases + runes + jewels) this is the full ingredient list for an optimizer that takes the gear you already have and generates a build.

Rebuild everything:

```bash
python3 scripts/build_gemling.py    # gemling table from poe2db Advanced Thaumaturgy
python3 scripts/build_catalog.py    # gem catalog from PoB data export
python3 generate.py                 # this README
```

---

_Gemling data from [poe2db.tw](https://poe2db.tw/us/Advanced_Thaumaturgy); catalog from the [PoB community data export](https://github.com/repoe-fork/pob-data). Numbers reflect PoE2 v0.5 and change with patches — open an issue/PR if anything's stale._
