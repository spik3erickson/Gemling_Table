# PoE2 v0.5 Support Compatibility Validation
_Generated: 2026-06-09T12:50:54_

## Scrape Summary
- Skills in catalog: 395
- Successfully scraped: 389
- Errors (fell back to PoB): 6
- Fallback skills: 6

## Agreement: poe2db vs PoB-computed
- Total (skill,support) pairs evaluated: 67722
- Agree: 51008 (75%)
- poe2db-only (new compat found): 6156
- PoB-only (PoB had it, poe2db does not): 10558

## Top 15 Skills by Disagreement

| Skill | poe2db count | PoB count | Disagree delta |
|-------|-------------|-----------|----------------|
| Companion: {0} | 311 | 59 | 312 |
| Azmerian Wolf | 292 | 62 | 290 |
| Ancestral Spirits | 291 | 39 | 280 |
| Mist Raven | 265 | 51 | 276 |
| Wild Protector | 272 | 57 | 275 |
| Skeletal Brute | 269 | 63 | 266 |
| Wolf Pack | 251 | 57 | 254 |
| Skeletal Sniper | 258 | 66 | 254 |
| Manifest Weapon | 234 | 40 | 254 |
| Cackling Companions | 251 | 57 | 254 |
| Summon Infernal Hound | 251 | 60 | 251 |
| Skeletal Warrior | 247 | 58 | 249 |
| Skeletal Reaver | 252 | 63 | 249 |
| Skeletal Arsonist | 248 | 63 | 245 |
| Spirit Vessel | 234 | 56 | 238 |

## Spot-check: Enervating Nova
- poe2db count: 182
- PoB count: 182
- Bloodlust absent (expected): YES (correct)
- Generic spell support (Ambrosia) present: YES

## Unmatched Support Names (33 unique)
_These support names appear on poe2db but are NOT in support_gems.json._
_Likely unique-item-granted or league-mechanic supports not yet catalogued._

| Support Name | Skills referencing it |
|-------------|----------------------|
| Arbiter's Reach | Align Fate, Alchemist's Boon, Archmage, Arctic Armour, Attrition (+89 more) |
| Atziri's Call | Ancestral Spirits, Animus Exchange, Arc, Apocalypse, Ball Lightning (+95 more) |
| Breachlord's Amalgam | Arc, Ball Lightning, Electrocuting Arrow, Falling Thunder, Freezing Shards (+16 more) |
| Catha's Brilliance | Azmerian Wolf, Cackling Companions, Companion: {0}, Manifest Weapon, Mist Raven (+6 more) |
| Concussive Runes | Acidic Concoction, Ancestral Spirits, Armour Breaker, Armour Piercing Rounds, Azmerian Wolf (+170 more) |
| Dreamer's Knell | Mantra of Destruction, Tempest Bell |
| Empowered Sparks II | Combat Frenzy, Crushing Fear, Cull The Weak, Devour, Disengage (+8 more) |
| Esh's Prowess | Ancestral Spirits, Archmage, Arc, Arctic Armour, Arctic Howl (+119 more) |
| Fist Of Kalguur | Devour, Earthquake, Earthshatter, Falling Thunder, Forge Hammer (+14 more) |
| Healing Runes | Align Fate, Alchemist's Boon, Archmage, Arctic Armour, Attrition (+89 more) |
| Her Declaration | Align Fate, Alchemist's Boon, Archmage, Arctic Armour, Attrition (+89 more) |
| Medved's Felling | Ancestral Spirits, Ancestral Warrior Totem, Armour Breaker, Azmerian Wolf, Azmerian Swarms (+79 more) |
| Mórrigan's Insight | Acidic Concoction, Ancestral Spirits, Arc, Arctic Armour, Arctic Howl (+236 more) |
| Oisín's Oath | Abyssal Apparition, Acidic Concoction, Ancestral Spirits, Animus Exchange, Arc (+282 more) |
| Olroth's Conviction | Align Fate, Ancestral Cry, Arctic Howl, Barrage, Fortifying Cry (+8 more) |
| Olroth's Hubris | Acidic Concoction, Ancestral Spirits, Armour Breaker, Armour Piercing Rounds, Azmerian Wolf (+139 more) |
| Overabundance III | Artillery Ballista, Azmerian Swarms, Bloodhound's Mark, Bone Offering, Briarpatch (+51 more) |
| Prototype Seventeen | Acidic Concoction, Ancestral Spirits, Arc, Arctic Howl, Armour Breaker (+198 more) |
| Ricochet III | Acidic Concoction, Ancestral Spirits, Arc, Azmerian Wolf, Ball Lightning (+59 more) |
| Runeforged Blades | Acidic Concoction, Ancestral Spirits, Armour Breaker, Armour Piercing Rounds, Azmerian Wolf (+127 more) |
| Runic Extraction | Acidic Concoction, Ancestral Spirits, Arc, Arctic Armour, Arctic Howl (+246 more) |
| Runic Infusion | Acidic Concoction, Ancestral Spirits, Armour Breaker, Armour Piercing Rounds, Azmerian Wolf (+139 more) |
| Scouring Flame | Acidic Concoction, Ancestral Spirits, Arc, Arctic Armour, Arctic Howl (+241 more) |
| Seraph's Heart | Align Fate, Alchemist's Boon, Archmage, Arctic Armour, Attrition (+89 more) |
| Styrn's Ferocity | Raise Shield, Resonating Shield, Shield Charge, Shield Wall, Soaring Midnight |
| Styrn's Mountain | Parry, Raise Shield, Resonating Shield, Runic Reprieve, Shield Charge |
| Tangmazu's Thurible | Azmerian Wolf, Cackling Companions, Companion: {0}, Manifest Weapon, Mist Raven (+6 more) |
| Trickster's Shard | Ancestral Spirits, Animus Exchange, Arc, Apocalypse, Ball Lightning (+93 more) |
| Tul's Avalanche | Bitter Dead, Bone Blast, Bone Cage, Companion: {0}, Comet (+30 more) |
| Uhtred's Constellation | Align Fate, Animus Exchange, Arctic Armour, Arctic Howl, Barrage (+72 more) |
| Uhtred's Rite | Animus Exchange, Animus Splinters, Arctic Armour, Arctic Howl, Barrage (+73 more) |
| Vorana's Siege | Acidic Concoction, Ancestral Spirits, Arctic Howl, Armour Breaker, Azmerian Wolf (+200 more) |
| Vruun's Aftermath | Ancestral Cry, Arctic Howl, Ferocious Roar, Fortifying Cry, Infernal Cry (+4 more) |

## Errors

- **Fragments Of The Past** (`Fragments_Of_The_Past`): HTTP Error 500: Internal Server Error
- **Kelari, the Tainted Sands** (`Kelari,_the_Tainted_Sands`): no #SupportedBy element
- **Navira, the Last Mirage** (`Navira,_the_Last_Mirage`): 404 or no cache
- **Ruzhan, the Blazing Sword** (`Ruzhan,_the_Blazing_Sword`): 404 or no cache
- **Siphoning Strike** (`Siphoning_Strike`): HTTP Error 500: Internal Server Error
- **Spectre: {0}** (`Spectre:_{0}`): 404 or no cache

## Fallback Skills (using PoB data)

- Fragments Of The Past
- Kelari, the Tainted Sands
- Navira, the Last Mirage
- Ruzhan, the Blazing Sword
- Siphoning Strike
- Spectre: {0}
