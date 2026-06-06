# PoE2 Skill Gem Quality Effects

A complete reference of every skill gem in Path of Exile 2 and its quality effects, scraped from [poe2db.tw](https://poe2db.tw/us/Skill_Gems). **189** gems total · **150** with a gemling line · **38** without.

Each gem can show two lines under *Additional Effects From Quality:* — a generic line and a brighter **gemling** line (the gem-specific bonus). Both are listed here, side by side.

## Contents

- [Meta & Triggered Skills](#meta--triggered-skills) (10)
- [Curses](#curses) (9)
- [Marks](#marks) (3)
- [Heralds](#heralds) (3)
- [Warcries](#warcries) (4)
- [Auras, Presences & Persistent Buffs](#auras-presences--persistent-buffs) (25)
- [Totems & Placed Objects](#totems--placed-objects) (5)
- [Minions & Summons](#minions--summons) (14)
- [Movement Skills](#movement-skills) (8)
- [Spell Skills](#spell-skills) (48)
- [Attack Skills](#attack-skills) (21)
- [Gems with no gemling line](#gems-with-no-gemling-line-38) (38)
- [How quality scales](#how-quality-scales)

## How quality scales

Every quality effect on a skill gem is shown as a range like `(0—N)`. `N` is the value at the standard **20% quality** cap; scaling is linear. Use this rule of thumb:

| Listed range | @ 10% q | @ 20% q | @ 30% q | @ 40% q | @ 50% q |
|---|---:|---:|---:|---:|---:|
| `(0—10)` | 5 | 10 | 15 | 20 | 25 |
| `(0—20)` | 10 | 20 | 30 | 40 | 50 |
| `(0—30)` | 15 | 30 | 45 | 60 | 75 |
| `(0—40)` | 20 | 40 | 60 | 80 | 100 |
| `(0—50)` | 25 | 50 | 75 | 100 | 125 |
| `(0—100)` | 50 | 100 | 150 | 200 | 250 |

Effects expressed as a **chance** clamp at 100%. Negative-range effects (e.g. `(-1—0)` seconds) reduce a value linearly toward zero.

## Meta & Triggered Skills

_Cast-on triggers and meta gems. Quality often affects reservation cost or trigger frequency._  (10 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Cast on Critical](https://poe2db.tw/us/Cast_on_Critical) | Buff grants (0—20)% increased Critical Hit chance | (0—10)% increased Reservation Efficiency | 30 |
| [Cast on Elemental Ailment](https://poe2db.tw/us/Cast_on_Elemental_Ailment) | (0—40)% increased Reservation Efficiency | (0—15)% increased Energy gained | 60 |
| [Cast on Minion Death](https://poe2db.tw/us/Cast_on_Minion_Death) | Socketed Spells deal (0—20)% increased Damage when triggered | (0—20)% increased Energy gained | 30 |
| [Ember Fusillade](https://poe2db.tw/us/Ember_Fusillade) | (0—40)% reduced Skill Effect Duration (0—20)% less Cast Speed | +(0—2)% more Damage for each previous Ember fired in sequence | 60 |
| [Escape Shot](https://poe2db.tw/us/Escape_Shot) | (0—40)% increased Damage with Hits against Frozen Enemies | (0—120)% more Freeze Buildup | 60 |
| [Ice-Tipped Arrows](https://poe2db.tw/us/Ice-Tipped_Arrows) | Empowers + (0—2) Attacks | (0—10)% increased Cooldown Recovery Rate | 3 |
| [Mirage Archer](https://poe2db.tw/us/Mirage_Archer) | (0—40)% increased Reservation Efficiency of Skills | +(0—1) seconds to Mirage duration | 60 |
| [Spark](https://poe2db.tw/us/Spark) | Fires +(0—4) Projectiles | (0—30)% increased Projectile Speed | 6 |
| [Trail of Caltrops](https://poe2db.tw/us/Trail_of_Caltrops) | Deals (0—20)% more Physical damage | +(0—5) to maximum number of Caltrops allowed | 30 |
| [Wind Dancer](https://poe2db.tw/us/Wind_Dancer) | (0—50)% more damage per stage | +(0—0.4) metres to explosion radius | 75 |

## Curses

_Hexes you cast onto enemies. Several curses share the same `(0—50)% reduced Mana Cost` quality bonus._  (9 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Blasphemy](https://poe2db.tw/us/Blasphemy) | Socketed Curses have (0—20)% increased Magnitudes | (0—10)% increased Reservation Efficiency | 30 |
| [Conductivity](https://poe2db.tw/us/Conductivity) | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |
| [Despair](https://poe2db.tw/us/Despair) | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |
| [Elemental Weakness](https://poe2db.tw/us/Elemental_Weakness) | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |
| [Enfeeble](https://poe2db.tw/us/Enfeeble) | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |
| [Flammability](https://poe2db.tw/us/Flammability) | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |
| [Hypothermia](https://poe2db.tw/us/Hypothermia) | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |
| [Temporal Chains](https://poe2db.tw/us/Temporal_Chains) | (0—50)% faster Curse Activation | (0—10)% increased Curse Magnitudes | 75 |
| [Vulnerability](https://poe2db.tw/us/Vulnerability) | (0—50)% reduced Mana Cost | (0—10)% increased Curse Magnitudes | 75 |

## Marks

_Single-target marks. Quality affects cost or reapplication._  (3 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Bloodhound's Mark](https://poe2db.tw/us/Bloodhounds_Mark) | Deals (0—20)% more Physical damage | Marked target receives Heavy Stun buildup equal to (0—50)% of Blood Loss | 30 |
| [Sniper's Mark](https://poe2db.tw/us/Snipers_Mark) | Marked enemy deals (0—10)% less damage | Next Critical Hit against Marked Enemy has (0—15)% increased Critical Damage Bonus | 15 |
| [Voltaic Mark](https://poe2db.tw/us/Voltaic_Mark) | (0—50)% reduced Mana Cost | Hits against Marked enemy cause +(0—20)% increased Electrocute buildup | 75 |

## Heralds

_Persistent reservation buffs that empower a specific damage type._  (3 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Herald of Ash](https://poe2db.tw/us/Herald_of_Ash) | Buff grants (0—20)% increased Fire damage | An additional +(0—5)% of Overkill damage contributes to base Ignite damage | 30 |
| [Herald of Plague](https://poe2db.tw/us/Herald_of_Plague) | (0—30)% more Area of Effect | (0—20)% chance to Hinder enemies on spreading Poison to them | 45 |
| [Herald of Thunder](https://poe2db.tw/us/Herald_of_Thunder) | Buff grants (0—20)% increased Lightning damage | Lightning Bolts strike the targets of your next (0—2) Attack Hits after killing a Shocked enemy with Attack damage | 30 |

## Warcries

_Shout effects that buff you or debuff enemies in an area._  (4 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Ancestral Cry](https://poe2db.tw/us/Ancestral_Cry) | Grants (0—10)% more Fire damage | +(0—20)% increased Warcry duration per Endurance Charge consumed | 15 |
| [Fortifying Cry](https://poe2db.tw/us/Fortifying_Cry) | (0—20)% more Guard gained | Shockwave radius is (0—0.4) metres | 30 |
| [Infernal Cry](https://poe2db.tw/us/Infernal_Cry) | Warcry radius is (0—3) metres | Empowered Attacks Gain (0—10)% of damage as extra Fire damage | 4.5 |
| [Seismic Cry](https://poe2db.tw/us/Seismic_Cry) | Gains (0—20)% of Physical damage as Fire damage | Empowered Attack Aftershocks deal (0—10)% more damage | 30 |

## Auras, Presences & Persistent Buffs

_Persistent reservation skills (auras, presences, offerings, body buffs)._  (25 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Alchemist's Boon](https://poe2db.tw/us/Alchemists_Boon) | Grants (0—20)% increased Attack speed during any Life Flask Effect Grants (0—20)% increased cast speed during any Mana Flask Effect | Grants you (0—0.03) Flask charges per second | 30 |
| [Archmage](https://poe2db.tw/us/Archmage) | Non-Channelling Spells Gain (0—1)% of Damage as extra Lightning damage for each 100 maximum Mana you have Non-Channelling Spells cost an additional (0—2)% of your maximum Mana | (0—10)% increased Reservation Efficiency | 1.5 |
| [Arctic Armour](https://poe2db.tw/us/Arctic_Armour) | Buff grants (0—20)% increased Armour per Stage | Gains a Stage every seconds, up to a maximum of (0—1) Stages | 30 |
| [Barrage](https://poe2db.tw/us/Barrage) | (0—20)% chance to not remove Charges on use | Repeats deal +(0—5)% more Damage | 30 |
| [Berserk](https://poe2db.tw/us/Berserk) | Buff grants +(0—8) to maximum Rage | Grants (0—10)% increased Rage effect | 12 |
| [Bone Offering](https://poe2db.tw/us/Bone_Offering) | (0—30)% more Skill Effect Duration | Shielded Minions take (0—30)% less Damage for 1 second after Shield is lost | 45 |
| [Combat Frenzy](https://poe2db.tw/us/Combat_Frenzy) | (-1—0) seconds to delay on gaining a Frenzy Charge | (0—10)% chance to gain an additional Charge | 0.5 |
| [Convalescence](https://poe2db.tw/us/Convalescence) | (0—30)% increased Cooldown Recovery Rate | +(0—0.5) seconds to Buff duration | 45 |
| [Cull The Weak](https://poe2db.tw/us/Cull_The_Weak) | (0—20)% chance to gain an additional random Charge when you gain a Charge | (0—20)% chance to gain an additional Charge | 30 |
| [Elemental Conflux](https://poe2db.tw/us/Elemental_Conflux) | (0—4) second duration between Element randomisations | Buff grants (0—10)% more damage with the affected Element | 6 |
| [Eternal Rage](https://poe2db.tw/us/Eternal_Rage) | (0—15)% increased Spirit Reservation Efficiency | Regenerate (0—0.5) Rage per second | 22.5 |
| [Grim Feast](https://poe2db.tw/us/Grim_Feast) | Remnants created by Supported Skills can be collected from (0—40)% further away | Remnants store (0—5)% of Minion maximum Life | 60 |
| [Iron Ward](https://poe2db.tw/us/Iron_Ward) | Deals (0—20)% more Physical damage | (0—50)% more Stun buildup | 30 |
| [Magma Barrier](https://poe2db.tw/us/Magma_Barrier) | Buff grants +(0—5)% to maximum Block Chance | +(0—5)% increased Block chance | 7.5 |
| [Mana Remnants](https://poe2db.tw/us/Mana_Remnants) | Buff grants (0—40)% increased Mana Regeneration Rate | Each Remnant grants (0—40) Mana | 60 |
| [Mana Tempest](https://poe2db.tw/us/Mana_Tempest) | (-8—0)% of Mana and Life spent while in the storm is added to this Skill's Mana Cost per Second | Effects of Mana Tempest linger for (0—2) seconds after leaving the Tempest | 4 |
| [Pain Offering](https://poe2db.tw/us/Pain_Offering) | Aura grants Minions (0—20)% increased Attack and Cast Speed | +(0—2.4) metres to Minion Aura radius | 30 |
| [Plague Bearer](https://poe2db.tw/us/Plague_Bearer) | (0—50)% increased Magnitude of Poison on targets that are not Poisoned | Stores (0—2)% of Expected Poison damage, up to Deals Physical damage equal to the stored Poison | 75 |
| [Resonating Shield](https://poe2db.tw/us/Resonating_Shield) | (0—100)% increased Stun Threshold while Channelling | Break (0—20)% increased Armour | 150 |
| [Scavenged Plating](https://poe2db.tw/us/Scavenged_Plating) | (0—1)% more Armour per Scavenged Plating | +(0—2) seconds to Scavenged Plating duration | 1.5 |
| [Shield Wall](https://poe2db.tw/us/Shield_Wall) | Gains (0—20)% of Physical damage as Fire damage | (0—40)% more Damage if destroyed by your Skills | 30 |
| [Siphon Elements](https://poe2db.tw/us/Siphon_Elements) | Remnants created by Supported Skills can be collected from (0—30)% further away | +(0—2)% chance per Power to spawn a Cold Remnant on Freezing a target +(0—2)% chance to spawn a Fire Remnant on Igniting a non-Ignited target +(0—2)% chance to spawn a Lightning Remnant on Shocking a non-Shocked target | 45 |
| [Soul Offering](https://poe2db.tw/us/Soul_Offering) | Buff grants you (0—20)% increased Spell damage | +(0—1) second to Spike duration | 30 |
| [Time of Need](https://poe2db.tw/us/Time_of_Need) | Buff grants (0—20)% increased Life Regeneration Rate | Blessing recovers (0—40) Life and removes Curses and Elemental Ailments | 30 |
| [Withering Presence](https://poe2db.tw/us/Withering_Presence) | Withers enemies in your Presence every (-0.5—0) seconds | Withered duration is (0—1) second | 0.25 |

## Totems & Placed Objects

_Stationary helpers. Several gems add to the totem limit._  (5 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Ancestral Warrior Totem](https://poe2db.tw/us/Ancestral_Warrior_Totem) | (0—50)% increased totem life | +(0—2) seconds to Totem duration | 75 |
| [Dark Effigy](https://poe2db.tw/us/Dark_Effigy) | Limit (0—1) Totem | +(0—0.2) metres to Impact radius | 1.5 |
| [Frost Bomb](https://poe2db.tw/us/Frost_Bomb) | Limit (0—3) Frost Bomb | +(0—10)% maximum Elemental Exposure applied | 4.5 |
| [Frost Wall](https://poe2db.tw/us/Frost_Wall) | (0—400)% increased Ice Crystal Life | (0—20)% increased Cooldown Recovery Rate | 600 |
| [Shockwave Totem](https://poe2db.tw/us/Shockwave_Totem) | Limit (0—1) Totem | +(0—4) seconds to Totem duration | 1.5 |

## Minions & Summons

_Summoned units. Quality often adds minion-wide damage/life/AS._  (14 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Bind Spectre](https://poe2db.tw/us/Bind_Spectre) | (0—20)% increased Reservation Efficiency | Minions deal (0—20)% more damage | 30 |
| [Raging Spirits](https://poe2db.tw/us/Raging_Spirits) | Minions deal (0—50)% more damage | Limit (0—2) Summoned Raging Spirits | 75 |
| [Raise Zombie](https://poe2db.tw/us/Raise_Zombie) | Limit (0—4) Raised Zombies | (0—25)% increased effect of Empowerment on Raised Zombies | 6 |
| [Ravenous Swarm](https://poe2db.tw/us/Ravenous_Swarm) | Spawn a new Swarm once every (-2—0) seconds | +(0—1) metres to swarm Attack radius | 1 |
| [Sacrifice](https://poe2db.tw/us/Sacrifice) | Minions have (0—40)% increased maximum Life | Minions Revive +(0—5)% more quickly | 60 |
| [Skeletal Arsonist](https://poe2db.tw/us/Skeletal_Arsonist) | Fires +(0—2) Projectiles | Deals additional Fire damage equal to +(0—4)% of Minion 's maximum Life | 3 |
| [Skeletal Brute](https://poe2db.tw/us/Skeletal_Brute) | Minions have (0—30)% more Maximum Life | Minions cause (0—40)% more Stun buildup | 45 |
| [Skeletal Cleric](https://poe2db.tw/us/Skeletal_Cleric) | Minions take (0—40)% reduced Damage | Revived Skeletons are immune to Damage for (0—3) seconds after being Revived | 60 |
| [Skeletal Frost Mage](https://poe2db.tw/us/Skeletal_Frost_Mage) | (0—20)% increased Spirit Reservation Efficiency | Minions deal (0—20)% more damage | 30 |
| [Skeletal Reaver](https://poe2db.tw/us/Skeletal_Reaver) | Break Armour equal to (0—30)% of Physical damage dealt | Minions have (0—20)% increased effect of Rage | 45 |
| [Skeletal Sniper](https://poe2db.tw/us/Skeletal_Sniper) | Deals (0—50)% more Fire Damage | Minions deal (0—20)% more damage | 75 |
| [Skeletal Storm Mage](https://poe2db.tw/us/Skeletal_Storm_Mage) | (0—30)% increased Minion Cast Speed | Minions gain (0—20)% of their maximum Life as Extra maximum Energy Shield | 45 |
| [Tame Beast](https://poe2db.tw/us/Tame_Beast) | (0—50)% reduced Mana Cost | +(0—1.6) seconds to Wisp duration | 75 |
| [Unearth](https://poe2db.tw/us/Unearth) | (0—50)% more Minion Attack Speed | +(0—5) seconds to Bone Construct duration Minions have (0—50)% increased Movement Speed | 75 |

## Movement Skills

_Mobility and traversal._  (8 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Blink](https://poe2db.tw/us/Blink) | Teleports + (0—2.5) metres | (0—10)% increased Cooldown Recovery Rate | 3.75 |
| [Disengage](https://poe2db.tw/us/Disengage) | +(0—1) metres to Melee Strike Range | (0—20)% chance for an additional Shockwave | 1.5 |
| [Leap Slam](https://poe2db.tw/us/Leap_Slam) | (0—20)% more Area of Effect | (0—20)% more Damage with Hits against Enemies with Fully Broken Armour | 30 |
| [Lightning Warp](https://poe2db.tw/us/Lightning_Warp) | (0—40)% more Cast Speed | (0—10)% increased Magnitude of Shock inflicted | 60 |
| [Rhoa Mount](https://poe2db.tw/us/Rhoa_Mount) | (0—30)% increased Reservation Efficiency | Minions have (0—20)% more Maximum Life | 45 |
| [Shield Charge](https://poe2db.tw/us/Shield_Charge) | (0—30)% increased maximum travel distance | Deals up to an additional +(0—40)% more Damage, based on the distance travelled | 45 |
| [Stampede](https://poe2db.tw/us/Stampede) | (0—20)% more Area of Effect | (0—20)% chance to cause an additional Aftershock | 30 |
| [Thunderous Leap](https://poe2db.tw/us/Thunderous_Leap) | (0—40)% chance to cause an additional Aftershock | (0—30)% chance to leave Shocked Ground when Detonating Spears | 60 |

## Spell Skills

_Direct-cast spells (projectiles, novas, walls, etc.)._  (48 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Arc](https://poe2db.tw/us/Arc) | Projectiles deal (0—3)% more Damage with Hits for each remaining Chain | Chains +(0—2) times | 4.5 |
| [Ball Lightning](https://poe2db.tw/us/Ball_Lightning) | (-30—0)% more Projectile Speed | Bolts target enemies within +(0—0.4) metres | 15 |
| [Bone Cage](https://poe2db.tw/us/Bone_Cage) | (0—40)% more Magnitude of Bleeding inflicted | Pins Enemies as though dealing +(0—50)% more Damage | 60 |
| [Bonestorm](https://poe2db.tw/us/Bonestorm) | (0—20)% chance to not remove Charges on use | (0—10)% more Cast Speed | 30 |
| [Comet](https://poe2db.tw/us/Comet) | (0—40)% increased Damage with Hits against Frozen Enemies | (0—10)% chance to Echo | 60 |
| [Contagion](https://poe2db.tw/us/Contagion) | (0—50)% more Area of Effect | Contagion targets (0—2) additional Enemies when Cast | 75 |
| [Detonate Dead](https://poe2db.tw/us/Detonate_Dead) | Converts (0—60)% of Physical damage to Fire damage | +(0—0.4) metres to explosion radius | 90 |
| [Detonating Arrow](https://poe2db.tw/us/Detonating_Arrow) | (0—40)% more Ignite Magnitude | +(0—1) to number of Maximum Stages | 60 |
| [Electrocuting Arrow](https://poe2db.tw/us/Electrocuting_Arrow) | Targets with attached Rods take (0—20)% increased damage | Hits against targets with attached Rods gain (0—10)% of Damage as extra Lightning Damage | 30 |
| [Essence Drain](https://poe2db.tw/us/Essence_Drain) | Chains +(0—4) times | +(0—1) second to Debuff duration | 6 |
| [Explosive Spear](https://poe2db.tw/us/Explosive_Spear) | (0—20)% chance to not remove Charges on use | +(0—0.4) metres to Explosion radius | 30 |
| [Eye of Winter](https://poe2db.tw/us/Eye_of_Winter) | Projectiles have (0—50)% chance to Return to you | (0—30)% increased Projectile Speed | 75 |
| [Fireball](https://poe2db.tw/us/Fireball) | + (0—10)% chance to fire 8 additional Projectiles in a circle | +(0—10)% chance to fire 2 additional Projectiles | 15 |
| [Firestorm](https://poe2db.tw/us/Firestorm) | (0—20)% chance to not remove an Infusion but still count as consuming them | +(0—0.2) metres to impact radius | 30 |
| [Flame Wall](https://poe2db.tw/us/Flame_Wall) | Deals (0—40)% more Fire Damage | Inflicts (0—20)% more Flammability Magnitude | 60 |
| [Flameblast](https://poe2db.tw/us/Flameblast) | (0—40)% more Magnitude of Damaging Ailments per Stage | (0—20)% more Cast Speed | 60 |
| [Freezing Salvo](https://poe2db.tw/us/Freezing_Salvo) | Maximum (0—4) Seals | (0—40)% more Freeze Buildup | 6 |
| [Frost Darts](https://poe2db.tw/us/Frost_Darts) | Forks (0—2) additional Times | +(0—10)% chance to fire 2 additional Projectiles | 3 |
| [Frostbolt](https://poe2db.tw/us/Frostbolt) | (0—40)% more Projectile Speed | (0—20)% more Projectile Damage after Piercing an Enemy | 60 |
| [Gas Arrow](https://poe2db.tw/us/Gas_Arrow) | Deals (0—20)% more Fire Damage | +(0—0.4) metres to impact radius | 30 |
| [Glacial Lance](https://poe2db.tw/us/Glacial_Lance) | (0—20)% chance to not remove Charges on use | active skill base area of effect radius [0,4] | 30 |
| [Hexblast](https://poe2db.tw/us/Hexblast) | (0—40)% more Critical Hit Chance | (0—10)% more Damage per 1 second of remaining duration on removed Curse | 60 |
| [Ice Nova](https://poe2db.tw/us/Ice_Nova) | (0—40)% chance to not remove an Infusion but still count as consuming them | (0—20)% more Damage with Hits against Enemies that are Chilled | 60 |
| [Ice Shot](https://poe2db.tw/us/Ice_Shot) | (0—40)% reduced Movement Speed Penalty from using Skills while moving | active skill chill effect +% final [0,30] | 60 |
| [Incinerate](https://poe2db.tw/us/Incinerate) | + (0—2) seconds of Maximum fuel | (0—20)% more Ignite duration | 3 |
| [Lightning Arrow](https://poe2db.tw/us/Lightning_Arrow) | (0—30)% chance for Lightning Damage with Hits to be Lucky | (0—40)% more chance to Shock | 45 |
| [Lightning Conduit](https://poe2db.tw/us/Lightning_Conduit) | (0—4) additional bolts if a Shocked enemy is in the target area | (0—20)% more Lightning Damage | 6 |
| [Lightning Rod](https://poe2db.tw/us/Lightning_Rod) | (0—20)% more Attack Speed | (0—20)% chance to cause an additional Burst on impact | 30 |
| [Lightning Spear](https://poe2db.tw/us/Lightning_Spear) | Benefits from consuming Charges have (0—20)% chance to be doubled | Fires +(0—2) bolts | 30 |
| [Living Bomb](https://poe2db.tw/us/Living_Bomb) | Deals (0—50)% more Fire Damage Explodes after enemy is dealt damage equal to (0—200)% of its Ailment Threshold | Inflicts (0—20)% more Flammability Magnitude | 75 |
| [Magnetic Salvo](https://poe2db.tw/us/Magnetic_Salvo) | (0—20)% more Lightning Damage | Fires up to +(0—4) missiles | 30 |
| [Molten Blast](https://poe2db.tw/us/Molten_Blast) | Fires +(0—2) Projectiles | (0—30)% chance to inflict Exposure on Hit | 3 |
| [Orb of Storms](https://poe2db.tw/us/Orb_of_Storms) | Orb expires after firing (0—6) bolts | Chains +(0—3) times | 9 |
| [Poisonburst Arrow](https://poe2db.tw/us/Poisonburst_Arrow) | Break Armour equal to (0—20)% of Poison damage | (0—10)% more Magnitude of Poison inflicted | 30 |
| [Profane Ritual](https://poe2db.tw/us/Profane_Ritual) | (0—100)% more Skill Effect Duration | (0—10)% chance to not destroy Consumed Corpse | 150 |
| [Rain of Arrows](https://poe2db.tw/us/Rain_of_Arrows) | Deals (0—20)% more damage | Arrows fall (0—20)% faster | 30 |
| [Shockchain Arrow](https://poe2db.tw/us/Shockchain_Arrow) | (0—20)% more Attack Speed | (0—20)% more Lightning Damage | 30 |
| [Snap](https://poe2db.tw/us/Snap) | (0—100)% increased Cooldown Recovery Rate | (0—10)% chance to spawn an additional Infusion Remnant | 150 |
| [Snipe](https://poe2db.tw/us/Snipe) | (0—20)% longer Perfect Timing window (0—20)% more Attack Speed | Explosion radius is (0—0.4) metres | 30 |
| [Spear of Solaris](https://poe2db.tw/us/Spear_of_Solaris) | Deals (0—20)% more Fire Damage | (0—25)% chance to retain 40% of Glory on use | 30 |
| [Spiral Volley](https://poe2db.tw/us/Spiral_Volley) | Benefits from consuming Charges have (0—30)% chance to be doubled | Fires +(0—4) Projectiles | 45 |
| [Storm Lance](https://poe2db.tw/us/Storm_Lance) | Fires +(0—2) Projectiles | base number of overcharged spears allowed [0,1] | 3 |
| [Stormcaller Arrow](https://poe2db.tw/us/Stormcaller_Arrow) | Fires +(0—2) Projectiles | (0—30)% increased Shock Duration | 3 |
| [Tornado Shot](https://poe2db.tw/us/Tornado_Shot) | + (0—2) to Limit of Tornadoes | Copied Projectiles deal +(0—15)% more damage | 3 |
| [Toxic Growth](https://poe2db.tw/us/Toxic_Growth) | (0—40)% increased Poison Duration | Fires +(0—1) Pustule Limit +(0—1) pustule | 60 |
| [Twister](https://poe2db.tw/us/Twister) | (0—20)% more Projectile Speed | (0—20)% chance for an additional twister | 30 |
| [Vine Arrow](https://poe2db.tw/us/Vine_Arrow) | (0—40)% more Skill Effect Duration | Plant deals additional Chaos Damage per second equal to (0—10)% of Poison Damage per second | 60 |
| [Whirlwind Lance](https://poe2db.tw/us/Whirlwind_Lance) | Elemental Whirlwinds Gain + (0—50)% of damage as damage of the corresponding Type | Collapse deals +(0—40)% more damage per additional stage | 75 |

## Attack Skills

_Weapon-based attacks: slams, strikes, bow and spear skills._  (21 gems)

| Gem | Quality effect (gemling) | Generic quality mod | @ 30% q |
|---|---|---|---|
| [Armour Breaker](https://poe2db.tw/us/Armour_Breaker) | Deals (0—20)% more Physical damage | Break (0—20)% increased Armour | 30 |
| [Blood Hunt](https://poe2db.tw/us/Blood_Hunt) | Enemies lose Life equal to + (0—4)% of Consumed Blood Loss | +(0—0.4) metres to explosion radius | 6 |
| [Boneshatter](https://poe2db.tw/us/Boneshatter) | Shockwave radius is (0—2) metres | (0—20)% increased Attack Speed | 3 |
| [Earthquake](https://poe2db.tw/us/Earthquake) | (0—40)% more Magnitude of Damaging Ailments inflicted | +(0—2) to Jagged Ground patch Limit | 60 |
| [Earthshatter](https://poe2db.tw/us/Earthshatter) | (0—20)% chance to cause an additional Aftershock | (0—6)% more Damage with Hits for each Spike | 30 |
| [Elemental Sundering](https://poe2db.tw/us/Elemental_Sundering) | (0—20)% more Critical Hit Chance | +(0—0.2) metres to Pulse radius | 30 |
| [Fangs of Frost](https://poe2db.tw/us/Fangs_of_Frost) | +(0—1) metres to Melee Strike Range | (0—15)% chance to not consume Parried Debuff | 1.5 |
| [Forge Hammer](https://poe2db.tw/us/Forge_Hammer) | Gain (0—20)% damage as Extra Fire Damage | (0—10)% increased Cooldown Recovery Rate | 30 |
| [Hammer of the Gods](https://poe2db.tw/us/Hammer_of_the_Gods) | (0—50)% chance to not consume Glory | +(0—0.4) metres to impact radius | 75 |
| [Perfect Strike](https://poe2db.tw/us/Perfect_Strike) | (0—40)% more Attack Speed | Inflicts (0—20)% more Flammability Magnitude | 60 |
| [Primal Strikes](https://poe2db.tw/us/Primal_Strikes) | (0—20)% more Critical Hit Chance | (0—20)% increased Attack Speed | 30 |
| [Rake](https://poe2db.tw/us/Rake) | (0—20)% chance to Aggravate Bleeding on targets you Hit with Attacks | base additional damage from distance +% final [0,30] | 30 |
| [Rapid Assault](https://poe2db.tw/us/Rapid_Assault) | (0—40)% more Magnitude of Bleeding inflicted | (0—20)% chance to leave an additional spearhead in the target | 60 |
| [Rolling Slam](https://poe2db.tw/us/Rolling_Slam) | Break Armour equal to (0—40)% of Physical damage dealt | (0—100)% increased Stun Threshold while using Skill | 60 |
| [Spearfield](https://poe2db.tw/us/Spearfield) | (0—20)% more Attack Speed | Hazards created by this Skill have (0—10)% chance to rearm after they are triggered | 30 |
| [Sunder](https://poe2db.tw/us/Sunder) | (0—20)% more Attack Speed | (0—50)% reduced Accuracy penalty based on distance | 30 |
| [Supercharged Slam](https://poe2db.tw/us/Supercharged_Slam) | (0—300)% more Stun buildup | +(0—1) maximum Stage | 450 |
| [Toxic Domain](https://poe2db.tw/us/Toxic_Domain) | Effects of Toxic Bloom Linger on you for (0—2) seconds | active skill base area of effect radius [0,3] | 3 |
| [Volcanic Fissure](https://poe2db.tw/us/Volcanic_Fissure) | Deals (0—20)% more Fire Damage | (0—20)% chance to cause an additional Aftershock | 30 |
| [Whirling Slash](https://poe2db.tw/us/Whirling_Slash) | (0—10)% more Attack Speed | Collapse deals +(0—40)% more damage per additional stage | 15 |
| [Wind Serpent's Fury](https://poe2db.tw/us/Wind_Serpents_Fury) | Gains (0—20)% of Damage as Extra Chaos Damage | (0—30)% more Knockback Distance | 30 |

## Gems with no gemling line (38)

These gems only display the generic `qualityMod` line. There is no lighter-blue `secondaryQualityMod` (gemling) on these pages — what you see is what you get.

| Gem | Generic quality mod | @ 30% q |
|---|---|---|
| [[DNT] Crushing Earth](https://poe2db.tw/us/DNT_Crushing_Earth) | — | — |
| [Bone Blast](https://poe2db.tw/us/Bone_Blast) | Ritual radius is (0—0.4) metres | 0.6 |
| [Cast on Freeze](https://poe2db.tw/us/Cast_on_Freeze) | (0—15)% increased Energy gained | 22.5 |
| [Cast on Ignite](https://poe2db.tw/us/Cast_on_Ignite) | (0—15)% increased Energy gained | 22.5 |
| [Cast on Shock](https://poe2db.tw/us/Cast_on_Shock) | (0—15)% increased Energy gained | 22.5 |
| [Chaos Bolt](https://poe2db.tw/us/Chaos_Bolt) | (0—40)% increased Projectile Speed | 60 |
| [Coiling Bolts](https://poe2db.tw/us/Coiling_Bolts) | Projectiles Split towards +(0—2) targets | 3 |
| [Dark Pact](https://poe2db.tw/us/Dark_Pact) | Sacrifices (0—2.5)% of Minion's life to deal that much Chaos damage | 3.75 |
| [Decompose](https://poe2db.tw/us/Decompose) | +(0—1) second to Cloud duration base secondary skill effect duration [0,1000] | 1.5 |
| [Discipline](https://poe2db.tw/us/Discipline) | Aura grants (0—20)% increased Energy Shield Recharge Rate | 30 |
| [Enervating Nova](https://poe2db.tw/us/Enervating_Nova) | (0—40)% more Electrocution buildup | 60 |
| [Exsanguinate](https://poe2db.tw/us/Exsanguinate) | Fires tendrils at up to +(0—1) Target | 1.5 |
| [Feast of Flesh](https://poe2db.tw/us/Feast_of_Flesh) | Consumes +(0—3) Corpses | 4.5 |
| [Firebolt](https://poe2db.tw/us/Firebolt) | Inflicts (0—20)% more Flammability Magnitude | 30 |
| [Freezing Shards](https://poe2db.tw/us/Freezing_Shards) | Fires +(0—1) Projectiles | 1.5 |
| [Fulmination](https://poe2db.tw/us/Fulmination) | Additional Hits deal (0—5)% more damage | 7.5 |
| [Galvanic Field](https://poe2db.tw/us/Galvanic_Field) | Chains +(0—2) times | 3 |
| [Heart of Ice](https://poe2db.tw/us/Heart_of_Ice) | (0—20)% more Magnitude of Chill inflicted | 30 |
| [Impurity](https://poe2db.tw/us/Impurity) | Aura grants +(0—6)% to Chaos Resistance | 9 |
| [Lightning Bolt](https://poe2db.tw/us/Lightning_Bolt) | (0—40)% more chance to Shock | 60 |
| [Malice](https://poe2db.tw/us/Malice) | Critical Weakness duration is (0—1) second | 1.5 |
| [Mana Drain](https://poe2db.tw/us/Mana_Drain) | Leeches (0—90) Mana | 135 |
| [Mirror of Refraction](https://poe2db.tw/us/Mirror_of_Refraction) | base number of projectiles [0,2] | — |
| [Overwhelming Presence](https://poe2db.tw/us/Overwhelming_Presence) | (0—15)% increased Aura Magnitudes | 22.5 |
| [Power Siphon](https://poe2db.tw/us/Power_Siphon) | (0—10)% chance to grant an additional Power Charge on Cull | 15 |
| [Purity of Fire](https://poe2db.tw/us/Purity_of_Fire) | Aura grants +(0—8)% to Fire Resistance | 12 |
| [Purity of Ice](https://poe2db.tw/us/Purity_of_Ice) | Aura grants +(0—8)% to Cold Resistance | 12 |
| [Purity of Lightning](https://poe2db.tw/us/Purity_of_Lightning) | Aura grants +(0—8)% to Lightning Resistance | 12 |
| [Reap](https://poe2db.tw/us/Reap) | Critical Weakness duration is +(0—2) seconds | 3 |
| [Sigil of Power](https://poe2db.tw/us/Sigil_of_Power) | Sigil radius is (0—0.8) metres | 1.2 |
| [Skeletal Warrior](https://poe2db.tw/us/Skeletal_Warrior) | Minions have (0—20)% more Maximum Life | 30 |
| [Solar Orb](https://poe2db.tw/us/Solar_Orb) | (0—20)% more Damage with Hits against Burning Enemies | 30 |
| [Soulrend](https://poe2db.tw/us/Soulrend) | Debuff duration is (0—0.1) seconds | 0.15 |
| [Spellslinger](https://poe2db.tw/us/Spellslinger) | (0—15)% increased Energy gained | 22.5 |
| [Spiraling Conspiracy](https://poe2db.tw/us/Spiraling_Conspiracy) | Raven Flock's Skills have (0—20)% increased Area of Effect | 30 |
| [Unleash](https://poe2db.tw/us/Unleash) | (0—10)% increased Cooldown Recovery Rate | 15 |
| [Volatile Dead](https://poe2db.tw/us/Volatile_Dead) | (0—10)% chance to not destroy Consumed Corpse | 15 |
| [Wither](https://poe2db.tw/us/Wither) | — | — |

## Errors (1)

Pages that failed to scrape. These are usually templated/placeholder URLs on the source.

| Listed name | URL | Error |
|---|---|---|
| Companion%3A %7B0%7D | <https://poe2db.tw/us/Companion%3A_%7B0%7D> | ClientResponseError: 404, message='Not Found', url='https://poe2db.tw/us/Companion:_%7B0%7D' |

---

_Data sourced from [poe2db.tw](https://poe2db.tw/us/Skill_Gems). Numbers are accurate as of the most recent scrape; gem balance changes with patches. Submit a PR or open an issue if anything's stale._
