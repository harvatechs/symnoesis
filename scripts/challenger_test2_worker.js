import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  classifySymbiosis,
  computeAllMarginalProbabilities,
  computeCompositeC,
  computeDyadWindowMasses,
  computeHne,
  computeSne,
  computeSq,
  computeStabilityFactor,
  evaluateSafetyGate,
  evaluateZones,
  getModalPixel,
  parsePixelId,
} from "../packages/ts/dist/index.js";

const inputPath = resolve(process.cwd(), "scripts/parity_inputs.json");
const outputPath = resolve(process.cwd(), "scripts/parity_outputs_ts.json");

const inputs = JSON.parse(readFileSync(inputPath, "utf-8"));
const outputs = [];

for (const testCase of inputs) {
  const {
    id,
    posteriors,
    s_H,
    outcome_deltas,
    integrity,
    reliability,
    operator,
    sigma_C,
    confirmed_chi,
    watch_chi,
    n_eff,
    is_trajectory_negative,
  } = testCase;

  // 1. Marginals
  const pVars = computeAllMarginalProbabilities(posteriors);

  // 2. Masses & Modal Pixel
  const masses = computeDyadWindowMasses(pVars);
  const modalPixel = getModalPixel(masses);
  const [hBits, mBits] = parsePixelId(modalPixel);

  // 3. Net Effects
  const [hne, outcomeAvail] = computeHne(s_H, outcome_deltas);
  const [sne, opBlind] = computeSne(integrity, reliability, operator);
  const [c, snePrime] = computeCompositeC(hne, sne);

  // 4. Stability
  const s = computeStabilityFactor(sigma_C);

  // 5. Safety Gate
  const [gateCeiling, gateStatus] = evaluateSafetyGate(confirmed_chi, watch_chi, n_eff);

  // 6. SQ
  const [sq, sqRaw, gateTriggered] = computeSq(c, s, gateCeiling);

  // 7. Symbiosis Class
  const symClass = classifySymbiosis(hne, sne, opBlind);

  // 8. Governance Zones
  const hasConfirmedChi = confirmed_chi && confirmed_chi.length > 0;
  const zoneRes = evaluateZones(
    sq,
    hBits,
    mBits,
    Boolean(hasConfirmedChi),
    is_trajectory_negative
  );

  outputs.push({
    id,
    pVars,
    modalPixel,
    massCount: Object.keys(masses).length,
    masses, // pruned masses
    hne,
    outcomeAvail,
    sne,
    snePrime,
    opBlind,
    c,
    s,
    gateCeiling,
    gateStatus,
    sq,
    sqRaw,
    gateTriggered,
    symClass: {
      technical_name: symClass.technical_name,
      public_label: symClass.public_label,
      h_sign: symClass.h_sign,
      s_sign: symClass.s_sign,
      operator_blind_applied: symClass.operator_blind_applied,
    },
    zones: {
      primary: zoneRes.primary,
      secondary_tags: [...zoneRes.secondary_tags].sort(),
    },
  });
}

writeFileSync(outputPath, JSON.stringify(outputs));
console.log(`Successfully evaluated ${outputs.length} test sets in TypeScript.`);
