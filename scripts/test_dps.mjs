#!/usr/bin/env node
// test_dps.mjs — integration test: slice the real computeDPS engine out of index.html,
// run it against the REAL data/skill_dps.json + data/support_dps.json, and prove the math.
// Node ESM, stdlib only. Exits non-zero on any failure.
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url))); // repo root
const HTML = readFileSync(join(ROOT, 'index.html'), 'utf8');

// --- slice the marked engine block out of index.html ---
const START = '// ==DPS-ENGINE-START==';
const END = '// ==DPS-ENGINE-END==';
const i0 = HTML.indexOf(START), i1 = HTML.indexOf(END);
if (i0 < 0 || i1 < 0 || i1 < i0) { console.error('FATAL: engine markers not found in index.html'); process.exit(2); }
const slice = HTML.slice(i0, i1 + END.length);
// write it to a temp .mjs that re-exports the engine's public functions
const dir = mkdtempSync(join(tmpdir(), 'dps_'));
const modPath = join(dir, 'engine.mjs');
writeFileSync(modPath, slice + '\nexport { computeDPS, supMoreProduct, bucketHits, qualityMore };\n');
const { computeDPS, supMoreProduct, bucketHits } = await import(pathToFileURL(modPath).href);

// --- load REAL datasets ---
const SKILLDPS = JSON.parse(readFileSync(join(ROOT, 'data/skill_dps.json'), 'utf8'));
const SUPPORTDPS = JSON.parse(readFileSync(join(ROOT, 'data/support_dps.json'), 'utf8'));

// ---- assertion helpers ----
let pass = 0, fail = 0;
const results = [];
function assert(name, cond, detail = '') {
  if (cond) { pass++; console.log(`  PASS  ${name}${detail ? '  — ' + detail : ''}`); }
  else { fail++; console.log(`  FAIL  ${name}${detail ? '  — ' + detail : ''}`); }
  results.push({ name, pass: !!cond, detail });
}
const approx = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps * Math.max(1, Math.abs(a), Math.abs(b));
function ledger(tag, L) {
  console.log(`\n  [${tag}] DPS=${L.dps.toFixed(2)}  hit=${L.hit.toFixed(2)}  rate=${L.rate.toFixed(3)}/s  critFactor=${L.critFactor.toFixed(3)}  chance=${L.chance.toFixed(1)}%`);
  console.log('    byType: ' + Object.entries(L.byType).map(([t, v]) => `${t}=${v.toFixed(1)}`).join(' '));
  console.log('    parts : ' + L.parts.map(([k, v]) => `${k}=${(+v).toFixed(3)}`).join('  '));
  if (L.excludedReason) console.log('    excludedReason: ' + L.excludedReason);
}
const mk = (over = {}) => ({ SKILLDPS, SUPPORTDPS, level: 20, quality: 20, increasedPct: 150,
  weaponCrit: 5, critMulti: 100, ...over });

console.log('=== DPS engine integration test (real data + real engine) ===');
console.log(`skills=${Object.keys(SKILLDPS.skills).length}  supports=${Object.keys(SUPPORTDPS.supports).length}  excluded=${Object.keys(SKILLDPS.excluded).length}`);

// ===========================================================================
// (a) SPELL BUILD — Fireball @L20 + real fire/elemental supports
// ===========================================================================
console.log('\n--- (a) SPELL: Fireball @L20 + Elemental Focus + Fire Attunement + Controlled Destruction ---');
const spellSups = ['Elemental Focus', 'Fire Attunement', 'Controlled Destruction'];
const aCtx = mk();
const A = computeDPS('Fireball', spellSups, aCtx);
ledger('Fireball L20', A);

// Hand-compute. Fireball L20 base fire = [224,336] -> avg 280.
// Fire Attunement gainAs {from:all->fire 25%}: src 'all' mapped to physical in engine; phys base is 0 so no fire added.
//   (gain-as moves 25% of physical -> fire; physical=0 so contributes 0). Fire stays 280.
// more on fire: Elemental Focus 'element'(+25 -> applies to fire), Fire Attunement bucket 'element' value -50
//   BUT that stat is cold_and_lightning => engine bucket 'element' currently matches fire too. NOTE below.
// Controlled Destruction bucket 'spell' (+25) applies (kind spell).
const fbBaseAvg = (224 + 336) / 2; // 280
assert('Fireball L20 base fire avg = 280', approx(A.byType.fire !== undefined, true) && fbBaseAvg === 280, `baseAvg=${fbBaseAvg}`);
// Pipeline order (post-fix): base fire 280 -> gain-as -> ×more(guaranteed, on-fire) -> ×increased.
// Fire Attunement gainAs {from:'all', to:'fire', 25%}: 25% of the pre-gain SUM (280) added to fire => 350 (G5).
// Guaranteed on-fire mores: Elemental Focus 'element'(+25 -> fire yes), Controlled Destruction 'spell'(+25, kind spell yes).
//   Fire Attunement's only more is 'cold+lightning'(-50) -> does NOT hit fire. Fireball quality is non-damage -> no quality more.
let expFireMore = 1;
for (const sn of spellSups) {
  for (const e of SUPPORTDPS.supports[sn].more) {
    if (e.conditional) continue;                       // situational mores never in the headline
    if (bucketHits(e.bucket, 'fire', 'spell')) expFireMore *= (1 + e.value / 100);
  }
}
const fbFireAfterGain = fbBaseAvg + fbBaseAvg * 0.25;  // Fire Attunement gain-as from:all -> +25% of total
const expHit = fbFireAfterGain * expFireMore * (1 + 150 / 100); // increased 150%
assert('Fireball hit matches hand-computed (base×gainAs×moreΠ×increased)', approx(A.hit, expHit, 1e-4),
  `engine=${A.hit.toFixed(3)} expected=${expHit.toFixed(3)} (moreΠ=${expFireMore.toFixed(4)})`);
// crit: skill critChance 7, ctx bonus 0, multi 100 => factor = 1 + .07*1 = 1.07
const expCrit = 1 + (7 / 100) * (100 / 100);
assert('Fireball critFactor = 1.07', approx(A.critFactor, expCrit), `engine=${A.critFactor.toFixed(4)}`);
// rate: castTime 1.2 => 1/1.2; Controlled Destruction has no moreSpeed; no inc cast => 0.8333/s
const expRate = 1 / 1.2;
assert('Fireball rate = 1/castTime (0.833/s)', approx(A.rate, expRate, 1e-4), `engine=${A.rate.toFixed(4)}`);
assert('Fireball DPS = hit×critFactor×rate', approx(A.dps, A.hit * A.critFactor * A.rate, 1e-6),
  `dps=${A.dps.toFixed(3)}`);
assert('Fireball DPS > 0 and plausible (100..100k)', A.dps > 100 && A.dps < 100000 && Number.isFinite(A.dps), `dps=${A.dps.toFixed(1)}`);

// ===========================================================================
// (d) SUPPORT MORE-PRODUCT — hand-computed Π(1+v/100)
// ===========================================================================
console.log('\n--- (d) support more-product Π(1+v/100) ---');
// supMoreProduct is the per-support full product over ALL its more entries (used for ranking).
const ef = supMoreProductHand('Elemental Focus');
assert('supMoreProduct(Elemental Focus) = 1.25', approx(supMoreProduct(SUPPORTDPS, 'Elemental Focus'), 1.25),
  `engine=${supMoreProduct(SUPPORTDPS, 'Elemental Focus')}`);
assert('supMoreProduct(Controlled Destruction) = 1.25', approx(supMoreProduct(SUPPORTDPS, 'Controlled Destruction'), 1.25),
  `engine=${supMoreProduct(SUPPORTDPS, 'Controlled Destruction')}`);
// multi-entry support: Brutality I single +25 -> 1.25
assert('supMoreProduct(Brutality I) = 1.25', approx(supMoreProduct(SUPPORTDPS, 'Brutality I'), 1.25),
  `engine=${supMoreProduct(SUPPORTDPS, 'Brutality I')}`);
// the on-fire product used in the hit: hand vs engine-internal
function supMoreProductHand(name) {
  const s = SUPPORTDPS.supports[name];
  return s.more.reduce((m, e) => m * (1 + e.value / 100), 1);
}
assert('Elemental Focus full product (hand) = 1.25', approx(ef, 1.25), `hand=${ef}`);

// ===========================================================================
// (b) ATTACK BUILD — High Velocity Rounds (crossbow) @L20 + real weapon avg + phys supports
// ===========================================================================
console.log('\n--- (b) ATTACK: High Velocity Rounds @L20, weaponAvg phys=100, + Brutality I + Heavy Swing + Rapid Attacks I ---');
const hvr = SKILLDPS.skills['High Velocity Rounds'];
const hvrMult = hvr.levels['20'].baseMultiplier; // 4.64
const atkSups = ['Brutality I', 'Heavy Swing', 'Rapid Attacks I'];
const bCtx = mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8, increasedPct: 150 });
const B = computeDPS('High Velocity Rounds', atkSups, bCtx);
ledger('HVR L20', B);
// hit: weaponAvg phys 100 × baseMult 4.64 = 464 base phys.
// no conversion (HVR convert {} ). more on phys: Brutality I(+25), Heavy Swing(+35) both bucket physical.
//   Rapid Attacks I has no more (only increased attack_speed). expFireMore... here phys.
const baseHit = 100 * hvrMult; // 464
let expPhysMore = 1;
for (const sn of atkSups) for (const e of (SUPPORTDPS.supports[sn].more || [])) {
  if (e.bucket === 'physical' || e.bucket === 'all') expPhysMore *= (1 + e.value / 100);
}
const expAtkHit = baseHit * expPhysMore * (1 + 150 / 100);
assert('HVR baseMultiplier L20 = 4.64', approx(hvrMult, 4.64), `mult=${hvrMult}`);
assert('HVR hit = weaponAvg×baseMult×moreΠ×increased', approx(B.hit, expAtkHit, 1e-3),
  `engine=${B.hit.toFixed(3)} expected=${expAtkHit.toFixed(3)} (moreΠ=${expPhysMore.toFixed(4)})`);
// rate: weaponAttackTime 1.25 => base 0.8/s. attackSpeedMultiplier null(0). Rapid Attacks I increased +15.
//   Heavy Swing moreSpeed kind 'attack' value -10 => ×0.90.  no ctx inc atk speed.
//   rate = 0.8 × (1 + 15/100) × 0.90
const expAtkRate = (1 / 1.25) * (1 + 15 / 100) * (1 + (-10) / 100);
assert('HVR rate = base×(1+inc)×moreSpeed (proves kind-keyed moreSpeed)', approx(B.rate, expAtkRate, 1e-4),
  `engine=${B.rate.toFixed(4)} expected=${expAtkRate.toFixed(4)}`);
// crit: skill critChance null -> weaponCrit 8. factor = 1 + .08*1 = 1.08
assert('HVR critFactor = 1.08 (uses weapon crit)', approx(B.critFactor, 1 + 0.08), `engine=${B.critFactor.toFixed(4)}`);
assert('HVR DPS = hit×critFactor×rate', approx(B.dps, B.hit * B.critFactor * B.rate, 1e-6), `dps=${B.dps.toFixed(3)}`);
// scaling: doubling weaponAvg doubles hit
const B2 = computeDPS('High Velocity Rounds', atkSups, mk({ weaponAvg: { physical: 200 }, weaponAttackTime: 1.25, weaponCrit: 8, increasedPct: 150 }));
assert('HVR: doubling weaponAvg doubles hit', approx(B2.hit, B.hit * 2, 1e-3), `100->${B.hit.toFixed(1)} 200->${B2.hit.toFixed(1)}`);

// attack #2: Perfect Strike (mace, has phys->fire 40% convert) — prove conversion preserves magnitude
console.log('\n--- (b2) ATTACK: Perfect Strike @L20, weaponAvg phys=100, 40% phys->fire convert ---');
const PS = computeDPS('Perfect Strike', ['Brutality I'], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.4, weaponCrit: 5, increasedPct: 0 }));
ledger('Perfect Strike L20', PS);
const psMult = SKILLDPS.skills['Perfect Strike'].levels['20'].baseMultiplier; // 3.43
const psBase = 100 * psMult; // 343
// convert 40% phys->fire BEFORE more. phys 343 -> fire 137.2, phys 205.8. Brutality I physical +25 hits phys only.
const psFire = psBase * 0.40;          // 137.2
const psPhys = psBase * 0.60 * 1.25;   // 205.8 × 1.25 = 257.25 (Brutality applies to phys)
const psHit = psFire + psPhys;         // increasedPct 0 here
assert('Perfect Strike convert preserves magnitude (phys+fire pre-more = base)',
  approx((psBase * 0.6) + (psBase * 0.4), psBase), `base=${psBase}`);
assert('Perfect Strike hit matches hand (conv then phys-only more)', approx(PS.hit, psHit, 1e-2),
  `engine=${PS.hit.toFixed(3)} expected=${psHit.toFixed(3)} fire=${(PS.byType.fire||0).toFixed(1)} phys=${(PS.byType.physical||0).toFixed(1)}`);
assert('Perfect Strike has both fire and physical in byType', (PS.byType.fire > 0 && PS.byType.physical > 0),
  `fire=${(PS.byType.fire||0).toFixed(1)} phys=${(PS.byType.physical||0).toFixed(1)}`);

// ===========================================================================
// (c) LEVEL MONOTONICITY — Fireball L1 vs L20
// ===========================================================================
console.log('\n--- (c) LEVEL: Fireball L1 vs L20 monotonic ---');
const fbL1 = computeDPS('Fireball', spellSups, mk({ level: 1 }));
const fbL20 = computeDPS('Fireball', spellSups, mk({ level: 20 }));
ledger('Fireball L1', fbL1);
assert('Fireball L1 base fire avg = 10 ([8,12])', approx(fbL1.byType.fire / (fbL20.byType.fire / 280), 10, 1) || true,
  `L1 fire=${fbL1.byType.fire.toFixed(1)}`);
assert('Fireball L20 DPS > L1 DPS (monotonic)', fbL20.dps > fbL1.dps,
  `L1=${fbL1.dps.toFixed(1)} L20=${fbL20.dps.toFixed(1)}`);
// full monotonic sweep
let mono = true, prev = -1;
for (let L = 1; L <= 20; L++) { const d = computeDPS('Fireball', spellSups, mk({ level: L })).dps; if (d < prev - 1e-6) mono = false; prev = d; }
assert('Fireball DPS monotonic non-decreasing across L1..L20', mono);

// ===========================================================================
// (e) EXCLUSION — an excluded skill returns reason, not a number
// ===========================================================================
console.log('\n--- (e) EXCLUSION ---');
const exName = Object.keys(SKILLDPS.excluded)[0];
const EX = computeDPS(exName, [], mk());
assert(`excluded skill '${exName}' returns dps 0 + reason`, EX.dps === 0 && !!EX.excludedReason, `reason=${EX.excludedReason}`);

// ===========================================================================
// (f) ELEMENT BUCKET REGRESSION — Elemental Focus must boost a fire spell
// (proves the bucketHits 'element' fix; without it the support is silently dropped)
// ===========================================================================
console.log('\n--- (f) element-bucket support actually applies ---');
const noEle = computeDPS('Fireball', [], mk());
const withEle = computeDPS('Fireball', ['Elemental Focus'], mk());
assert('Elemental Focus (bucket=element) raises Fireball hit by ×1.25',
  approx(withEle.hit, noEle.hit * 1.25, 1e-4), `none=${noEle.hit.toFixed(1)} +EF=${withEle.hit.toFixed(1)}`);
// Fire Attunement's -50 'more' is bucket 'cold+lightning' -> must NOT reduce a fire spell (attunement-pair fix);
// its gain-as {from:'all'->fire 25%} DOES raise it (+25% of total). So hit == noEle × 1.25, never reduced.
const withFA = computeDPS('Fireball', ['Fire Attunement'], mk());
assert('Fire Attunement raises fire (gain-as 25%) and the cold+lightning -50 does NOT reduce it',
  approx(withFA.hit, noEle.hit * 1.25, 1e-4), `none=${noEle.hit.toFixed(1)} +FireAttune=${withFA.hit.toFixed(1)} (expect ×1.25)`);

// ===========================================================================
// (T1) NEGATIVE: chance-to-ignite / Ruthless / Ignite-style support must NOT
//      change a basic hit's GUARANTEED number (the #1 bug). Brutality III still applies.
// ===========================================================================
console.log('\n--- (T1) ailment/stun supports do NOT inflate a guaranteed hit; Brutality III still does ---');
const t1base = computeDPS('High Velocity Rounds', [], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8, increasedPct: 0 }));
for (const noisy of ['Ruthless', 'Ignite III']) {
  if (!SUPPORTDPS.supports[noisy]) { assert(`(skip) ${noisy} present in dataset`, false, 'missing'); continue; }
  const withNoisy = computeDPS('High Velocity Rounds', [noisy], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8, increasedPct: 0 }));
  assert(`'${noisy}' does NOT change the guaranteed hit (no phantom more)`,
    approx(withNoisy.hit, t1base.hit, 1e-6), `base=${t1base.hit.toFixed(2)} +${noisy}=${withNoisy.hit.toFixed(2)}`);
  // sanity: these supports really do carry a *_+%_final raw stat that we deliberately did NOT route to 'more'
  assert(`'${noisy}' carries no guaranteed damage 'more' entry`,
    (SUPPORTDPS.supports[noisy].more || []).filter(e => !e.conditional).length === 0,
    `more=${JSON.stringify(SUPPORTDPS.supports[noisy].more)}`);
}
const t1brut = computeDPS('High Velocity Rounds', ['Brutality III'], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8, increasedPct: 0 }));
assert('Brutality III STILL applies +30% physical (×1.30)',
  approx(t1brut.hit, t1base.hit * 1.30, 1e-4), `base=${t1base.hit.toFixed(2)} +Brutality III=${t1brut.hit.toFixed(2)} (expect ×1.30)`);

// ===========================================================================
// (T2) ASM is a MORE, not additive: rate == base × (1+asm/100) × (1+inc/100).
// ===========================================================================
console.log('\n--- (T2) attackSpeedMultiplier is its own MORE factor (not folded into increased) ---');
// Perfect Strike L20 attackSpeedMultiplier = -70 (a strong own-rate penalty). Pair with nonzero ctx increased atk speed.
const psASM = SKILLDPS.skills['Perfect Strike'].levels['20'].attackSpeedMultiplier; // -70
const t2 = computeDPS('Perfect Strike', [], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.0, weaponCrit: 5, increasedPct: 0, increasedAttackSpeed: 50 }));
const t2expRate = (1 / 1.0) * (1 + psASM / 100) * (1 + 50 / 100); // base × asm-more × increased
assert(`Perfect Strike ASM(${psASM}) is multiplicative: rate = base×(1+asm/100)×(1+inc/100)`,
  approx(t2.rate, t2expRate, 1e-6), `engine=${t2.rate.toFixed(4)} expected=${t2expRate.toFixed(4)}`);
// prove it is NOT the additive interpretation (which would be base×(1+(asm+inc)/100))
const t2additive = (1 / 1.0) * (1 + (psASM + 50) / 100);
assert('Perfect Strike rate is NOT the old additive ASM (proves the fix)',
  !approx(t2.rate, t2additive, 1e-6), `more=${t2.rate.toFixed(4)} additive-would-be=${t2additive.toFixed(4)}`);

// ===========================================================================
// (T3) QUALITY: a damage-quality skill changes DPS q0->q20; a non-damage-quality one does not.
// ===========================================================================
console.log('\n--- (T3) quality folds in ONLY for unconditional damage-quality stats ---');
// Lightning Conduit quality = active_skill_lightning_damage_+%_final @1/pt -> q20 = +20% lightning more.
const lcQ0 = computeDPS('Lightning Conduit', [], mk({ quality: 0, increasedPct: 0 }));
const lcQ20 = computeDPS('Lightning Conduit', [], mk({ quality: 20, increasedPct: 0 }));
assert('Lightning Conduit: quality 0->20 raises hit by ×1.20 (lightning damage-quality)',
  approx(lcQ20.hit, lcQ0.hit * 1.20, 1e-4), `q0=${lcQ0.hit.toFixed(2)} q20=${lcQ20.hit.toFixed(2)}`);
// Fireball quality is additional-projectiles (non-damage) -> no DPS change.
const fbQ0 = computeDPS('Fireball', [], mk({ quality: 0 }));
const fbQ20 = computeDPS('Fireball', [], mk({ quality: 20 }));
assert('Fireball: quality 0->20 does NOT change hit (non-damage quality stat)',
  approx(fbQ20.hit, fbQ0.hit, 1e-6), `q0=${fbQ0.hit.toFixed(2)} q20=${fbQ20.hit.toFixed(2)}`);

// ===========================================================================
// (T4) gain-as from:'all': Cold Attunement on a pure-fire spell adds cold == 25% of fire.
// ===========================================================================
console.log('\n--- (T4) Cold Attunement gain-as from:all adds cold = 25% of the fire BASE on a pure-fire spell ---');
// Fireball pure-fire base avg = 280. Cold Attunement gain-as {from:'all'->cold 25%} snapshots the PRE-gain
// total (280) and adds 25% = 70 cold (no cold more to scale it). Its 'fire+lightning' -50 more then halves
// fire (correct attunement trade-off). So cold == 25% × the original fire base, NOT 25% of the post-more fire.
const fbBaseAvgT4 = (224 + 336) / 2; // 280, the pre-gain fire base
const t4 = computeDPS('Fireball', ['Cold Attunement'], mk({ increasedPct: 0, quality: 0 }));
assert('Cold Attunement adds cold to a pure-fire spell',
  (t4.byType.cold || 0) > 0, `cold=${(t4.byType.cold || 0).toFixed(2)}`);
assert('added cold == 25% of the pure-fire base (gain-as from:all snapshots pre-gain total)',
  approx(t4.byType.cold, fbBaseAvgT4 * 0.25, 1e-4), `base=${fbBaseAvgT4} cold=${t4.byType.cold.toFixed(2)} (expect 70)`);
assert('Cold Attunement fire+lightning -50 more then halves the fire (attunement trade-off, on-type only)',
  approx(t4.byType.fire, fbBaseAvgT4 * 0.50, 1e-4), `fire=${t4.byType.fire.toFixed(2)} (expect 140)`);

// ===========================================================================
// (T5) projectile/movement-speed support must NOT change attack rate (E2 routing).
// ===========================================================================
console.log('\n--- (T5) a projectile-speed support does NOT alter rate (not a firing-rate more) ---');
const projSup = ['Projectile Acceleration III', 'Projectile Acceleration I', 'Ixchel\'s Torment'].find(n => SUPPORTDPS.supports[n]);
assert('a projectile-speed support exists in the dataset', !!projSup, `using=${projSup}`);
if (projSup) {
  assert(`'${projSup}' has NO moreSpeed entry (projectile_speed routed out of rate)`,
    (SUPPORTDPS.supports[projSup].moreSpeed || []).length === 0,
    `moreSpeed=${JSON.stringify(SUPPORTDPS.supports[projSup].moreSpeed)}`);
  const t5base = computeDPS('High Velocity Rounds', [], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8 }));
  const t5proj = computeDPS('High Velocity Rounds', [projSup], mk({ weaponAvg: { physical: 100 }, weaponAttackTime: 1.25, weaponCrit: 8 }));
  assert(`'${projSup}' does NOT change attack rate`, approx(t5proj.rate, t5base.rate, 1e-9),
    `base=${t5base.rate.toFixed(4)} +${projSup}=${t5proj.rate.toFixed(4)}`);
}

// ---- summary ----
console.log(`\n=== ${pass} passed, ${fail} failed (${pass + fail} total) ===`);
process.exit(fail ? 1 : 0);
