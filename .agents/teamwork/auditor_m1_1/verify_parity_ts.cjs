const fs = require('node:fs');
const path = require('node:path');

async function main() {
  const { pathToFileURL } = require('node:url');
  const tsCore = await import(pathToFileURL(path.resolve('packages/ts/dist/index.js')).href);
  const {
    normalCdf,
    erfc,
    intToGray,
    grayToInt,
    intToBits,
    bitsToInt,
    hammingDistance,
    isAdjacentOnTorus,
    coordToPixelId,
    pixelIdToCoord,
    pixelCoordToId,
    parsePixelId,
    getGridNeighbors,
    getAllSingleFlipNeighbors,
    effectToScore,
    computeH2Threshold,
    computeMarginalProbability,
    computeAllMarginalProbabilities,
    computeDyadWindowMasses,
    getModalPixel,
    computeHne,
    computeSne,
    applyNonCompensation,
    computeCompositeC,
    computeSampleStd,
    computeStabilityFactor,
    computeEffectiveStability,
    evaluateSafetyGate,
    computeSq,
    computeSign3,
    classifySymbiosis,
    evaluateZones,
    DEFAULT_CONFIG,
  } = tsCore;

  const repoRoot = 'E:/Symnoesis';

  console.log('=== 1. VERIFYING GOLDEN VECTORS IN TYPESCRIPT ===');
  for (const vecName of ['gv-sq-001.json', 'gv-sq-002.json', 'gv-sq-003.json']) {
    const v = JSON.parse(fs.readFileSync(path.join(repoRoot, 'spec/vectors', vecName), 'utf-8'));
    const inp = v.input;
    const exp = v.expected;
    console.log(`\nVector: ${v.vector_id} (${v.description})`);

    let hne = 0.0;
    let outcomeAvail = false;
    if (inp.s_H) {
      [hne, outcomeAvail] = computeHne(inp.s_H, inp.outcome_deltas);
    } else {
      hne = inp.hne ?? 0.0;
    }

    let sne = 0.0;
    let opBlind = false;
    if (inp.integrity !== undefined) {
      [sne, opBlind] = computeSne(inp.integrity, inp.reliability, inp.operator);
    } else {
      sne = inp.sne ?? 0.0;
      opBlind = inp.operator_blind ?? false;
    }

    let c = 0.0;
    let snePrime = sne;
    if (inp.C !== undefined) {
      c = inp.C;
    } else {
      [c, snePrime] = computeCompositeC(hne, sne);
    }

    const s = inp.S !== undefined ? inp.S : computeStabilityFactor(inp.sigma_C ?? 0.0);

    let gateCeiling = null;
    if (inp.confirmed_chi) {
      const [ceil] = evaluateSafetyGate([inp.confirmed_chi], null, 50.0);
      gateCeiling = ceil;
    }

    const [sq, sqRaw, triggered] = computeSq(c, s, gateCeiling);
    const symClass = classifySymbiosis(hne, sne, inp.operator_blind ?? false);
    const zoneRes = evaluateZones(sq, null, null, Boolean(inp.confirmed_chi), false);

    const checks = [
      ['hne', hne, exp.hne],
      ['sne', sne, exp.sne],
      ['sne_prime', snePrime, exp.sne_prime],
      ['C', c, exp.C],
      ['sq_raw', sqRaw, exp.sq_raw],
      ['sq', sq, exp.sq],
    ];

    for (const [name, actual, expected] of checks) {
      if (expected !== undefined) {
        const diff = Math.abs(actual - expected);
        if (diff > 1e-6) {
          throw new Error(`FAIL ${name}: actual ${actual} != expected ${expected} (diff ${diff})`);
        }
        console.log(`  [PASS] ${name}: actual=${actual.toFixed(6)}, expected=${expected.toFixed(6)}, diff=${diff.toExponential(2)}`);
      }
    }

    if (exp.symbiosis_class) {
      if (symClass.technical_name !== exp.symbiosis_class) {
        throw new Error(`FAIL symbiosis_class: ${symClass.technical_name} != ${exp.symbiosis_class}`);
      }
      console.log(`  [PASS] symbiosis_class: ${symClass.technical_name} (${symClass.public_label})`);
    }

    if (exp.zone) {
      if (zoneRes.primary !== exp.zone) {
        throw new Error(`FAIL zone: ${zoneRes.primary} != ${exp.zone}`);
      }
      console.log(`  [PASS] zone: ${zoneRes.primary}`);
    }
  }

  console.log('\n=== 2. ADVERSARIAL STRESS TESTING (EDGE CASES & INVARIANTS) ===');

  // 2.1 Cody erfc edge cases
  console.log('Testing erfc & normalCdf edge cases...');
  if (!Number.isNaN(erfc(NaN))) throw new Error('erfc(NaN) should be NaN');
  if (!Number.isNaN(normalCdf(NaN))) throw new Error('normalCdf(NaN) should be NaN');
  if (normalCdf(Infinity) !== 1.0) throw new Error('normalCdf(Infinity) != 1.0');
  if (normalCdf(-Infinity) !== 0.0) throw new Error('normalCdf(-Infinity) != 0.0');
  if (Math.abs(normalCdf(0.0) - 0.5) > 1e-15) throw new Error('normalCdf(0) != 0.5');

  // Symmetry test: normalCdf(x) + normalCdf(-x) == 1.0
  for (const x of [-15, -8, -4, -1, -0.46875, -0.1, 0, 0.1, 0.46875, 1, 4, 8, 15]) {
    const sum = normalCdf(x) + normalCdf(-x);
    if (Math.abs(sum - 1.0) > 1e-12) {
      throw new Error(`Symmetry violation at x=${x}: sum=${sum}`);
    }
  }
  console.log('  [PASS] erfc & normalCdf edge cases and symmetry clean.');

  // 2.2 Non-compensation rule quadrants
  console.log('Testing non-compensation rule under all 4 quadrants...');
  // Quadrant 1: HNE > 0, SNE > 0 -> SNE' == SNE
  if (applyNonCompensation(0.3, 0.5) !== 0.5) throw new Error('Q1 failed');
  // Quadrant 2: HNE > 0, SNE < 0 -> SNE' == SNE
  if (applyNonCompensation(0.3, -0.5) !== -0.5) throw new Error('Q2 failed');
  // Quadrant 3: HNE < 0, SNE < 0 -> SNE' == SNE
  if (applyNonCompensation(-0.3, -0.5) !== -0.5) throw new Error('Q3 failed');
  // Quadrant 4: HNE < 0, SNE > 0 -> SNE' == 0.0 (NON-COMPENSATION APPLIED)
  if (applyNonCompensation(-0.3, 0.5) !== 0.0) throw new Error('Q4 non-compensation failed');
  // Boundary HNE = 0 -> SNE' == SNE
  if (applyNonCompensation(0.0, 0.5) !== 0.5) throw new Error('Boundary HNE=0 failed');
  // Boundary HNE = -1e-15 -> SNE' == 0.0
  if (applyNonCompensation(-1e-15, 0.5) !== 0.0) throw new Error('Boundary HNE=-1e-15 failed');
  console.log('  [PASS] Non-compensation rule adheres strictly to SPEC §6.');

  // 2.3 Harm asymmetry in stability
  console.log('Testing harm asymmetry in stability (S_eff)...');
  // If C >= 0, S_eff = S
  if (computeEffectiveStability(0.2, 0.7) !== 0.7) throw new Error('C >= 0 stability failed');
  if (computeEffectiveStability(0.0, 0.7) !== 0.7) throw new Error('C == 0 stability failed');
  // If C < 0, S_eff = 1.0 (instability never softens harm)
  if (computeEffectiveStability(-0.2, 0.7) !== 1.0) throw new Error('C < 0 harm asymmetry failed');
  console.log('  [PASS] Harm asymmetry adheres strictly to SPEC §6 & ADR-0004.');

  // 2.4 Safety gate ceilings
  console.log('Testing safety gate ceilings...');
  const [chi1Ceil, chi1Status] = evaluateSafetyGate(['CHI-1'], null, 50.0);
  if (chi1Ceil !== 0.0 || chi1Status !== 'critical') throw new Error('CHI-1 ceiling failed');
  const [chi4Ceil, chi4Status] = evaluateSafetyGate(['CHI-4'], null, 50.0);
  if (chi4Ceil !== 0.25 || chi4Status !== 'critical') throw new Error('CHI-4 ceiling failed');
  const [multiCeil] = evaluateSafetyGate(['CHI-4', 'CHI-1'], null, 50.0);
  if (multiCeil !== 0.0) throw new Error('Multi-CHI min ceiling failed');
  const [watchCeil, watchStatus] = evaluateSafetyGate(null, ['CHI-1'], 50.0);
  if (watchCeil !== null || watchStatus !== 'watch') throw new Error('Watch status failed');
  const [safeCeil, safeStatus] = evaluateSafetyGate(null, null, 10.0);
  if (safeCeil !== null || safeStatus !== 'safe') throw new Error('Safe status failed');
  const [unknownCeil, unknownStatus] = evaluateSafetyGate(null, null, 5.0);
  if (unknownCeil !== null || unknownStatus !== 'unknown') throw new Error('Unknown status failed');
  // Unrecognized CHI must throw
  let threw = false;
  try { evaluateSafetyGate(['CHI-FAKE'], null, 50.0); } catch { threw = true; }
  if (!threw) throw new Error('Unrecognized CHI did not throw error');
  console.log('  [PASS] Safety gate ceilings and status evaluation clean.');

  // 2.5 Symbiosis matrix and operator-blind suppression
  console.log('Testing symbiosis classification matrix and operator-blind rule...');
  // Check all 9 combinations without operator blind
  const expectedClasses = {
    '++': 'mutualism',
    '+0': 'commensalism',
    '+-': 'sacrificial',
    '0+': 'inverse_commensalism',
    '00': 'neutralism',
    '0-': 'antagonism',
    '-+': 'parasitism',
    '-0': 'amensalism',
    '--': 'mutual_harm',
  };
  const testVals = { '+': 0.5, '0': 0.0, '-': -0.5 };
  for (const [hCode, hVal] of Object.entries(testVals)) {
    for (const [sCode, sVal] of Object.entries(testVals)) {
      const res = classifySymbiosis(hVal, sVal, false);
      const expected = expectedClasses[hCode + sCode];
      if (res.technical_name !== expected) {
        throw new Error(`Class mismatch for ${hCode}${sCode}: got ${res.technical_name}, expected ${expected}`);
      }
    }
  }
  // When operator_blind is TRUE:
  // (-, +) Parasitism MUST NOT be asserted; falls back to Amensalism
  const blindParasitism = classifySymbiosis(-0.5, 0.5, true);
  if (blindParasitism.technical_name !== 'amensalism' || !blindParasitism.operator_blind_applied) {
    throw new Error('Operator-blind parasitism fallback failed');
  }
  console.log('  [PASS] Symbiosis matrix and operator-blind rule verified.');

  // 2.6 Zone precedence
  console.log('Testing zone precedence and secondary tags...');
  // Test simultaneous triggers: confirmed CHI (Z7), SQ = -30 (Z6), bits H1=0, M2=0 (Z5), trajectory negative (Z4)
  const multiZone = evaluateZones(-30, [0, 1, 1, 1], [1, 0, 1, 1], true, true);
  if (multiZone.primary !== 'Z7') throw new Error(`Precedence failure: expected Z7 primary, got ${multiZone.primary}`);
  if (!multiZone.secondary_tags.includes('Z6')) throw new Error('Z6 missing from secondary_tags');
  if (!multiZone.secondary_tags.includes('Z5')) throw new Error('Z5 missing from secondary_tags');
  if (!multiZone.secondary_tags.includes('Z4')) throw new Error('Z4 missing from secondary_tags');
  console.log(`  [PASS] Zone precedence clean: primary=${multiZone.primary}, secondary=[${multiZone.secondary_tags.join(', ')}]`);

  // 2.7 Gray code and Torus wrapping
  console.log('Testing Gray code bijections and Torus wrapping...');
  for (let k = 0; k < 16; k++) {
    const g = intToGray(k);
    const kRec = grayToInt(g);
    if (k !== kRec) throw new Error(`Gray code inversion error at k=${k}`);
  }
  // Torus wrapping
  const neighbors00 = getGridNeighbors({ col: 0, row: 0 });
  const hasWrappedCol = neighbors00.some(n => n.col === 15 && n.row === 0);
  const hasWrappedRow = neighbors00.some(n => n.col === 0 && n.row === 15);
  if (!hasWrappedCol || !hasWrappedRow) throw new Error('Torus wrapping failed at (0, 0)');
  console.log('  [PASS] Gray code bijections and Torus geometry verified.');

  console.log('\n=== ALL TYPESCRIPT INTEGRITY CHECKS PASSED CLEAN ===');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
