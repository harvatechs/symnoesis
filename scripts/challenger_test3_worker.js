import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  classifySymbiosis,
  computeAllMarginalProbabilities,
  computeCompositeC,
  computeDyadWindowMasses,
  computeH2Threshold,
  computeHne,
  computeMarginalProbability,
  computeSne,
  computeSq,
  computeStabilityFactor,
  DEFAULT_CONFIG,
  evaluateSafetyGate,
  evaluateZones,
  getModalPixel,
  normalCdf,
  parsePixelId,
} from "../packages/ts/dist/index.js";

const inputPath = resolve(process.cwd(), "scripts/pathological_inputs.json");
const outputPath = resolve(process.cwd(), "scripts/pathological_outputs_ts.json");

const testCases = JSON.parse(readFileSync(inputPath, "utf-8"));
const results = {};

// 1. Sigma corner cases
const sigmaResults = [];
for (const tc of testCases.sigma_cases) {
  const p = computeMarginalProbability(tc.mu, tc.sigma, tc.var_id);
  sigmaResults.push({ id: tc.id, p });
}
results.sigma = sigmaResults;

// 2. Delta outcome corner cases
const deltaResults = [];
for (const tc of testCases.delta_cases) {
  const [hne, outcomeAvail] = computeHne(tc.s_H, tc.outcome_deltas);
  deltaResults.push({ id: tc.id, hne, outcomeAvail });
}
results.delta = deltaResults;

// 3. Exact threshold cases
// 3a. mu == theta
const muThetaResults = [];
for (const tc of testCases.mu_theta_cases) {
  const p = computeMarginalProbability(tc.mu, tc.sigma, tc.var_id);
  muThetaResults.push({ id: tc.id, p });
}
results.mu_theta = muThetaResults;

// 3b. H2 threshold
results.h2_threshold = computeH2Threshold();

// 3c. Class thresholds
const classThreshResults = [];
for (const tc of testCases.class_thresh_cases) {
  const res = classifySymbiosis(tc.hne, tc.sne, tc.operator_blind);
  classThreshResults.push({
    id: tc.id,
    technical_name: res.technical_name,
    public_label: res.public_label,
    h_sign: res.h_sign,
    s_sign: res.s_sign,
    operator_blind_applied: res.operator_blind_applied,
  });
}
results.class_thresh = classThreshResults;

// 3d. Zone thresholds
const zoneThreshResults = [];
for (const tc of testCases.zone_thresh_cases) {
  const res = evaluateZones(
    tc.sq,
    tc.h_bits,
    tc.m_bits,
    tc.has_confirmed_chi,
    tc.is_trajectory_negative
  );
  zoneThreshResults.push({
    id: tc.id,
    primary: res.primary,
    secondary_tags: [...res.secondary_tags].sort(),
  });
}
results.zone_thresh = zoneThreshResults;

// 4. Modal fallback pruning cases
const pruneResults = [];
for (const tc of testCases.prune_cases) {
  const customConfig = {
    ...DEFAULT_CONFIG,
    assignment: {
      ...DEFAULT_CONFIG.assignment,
      prune_mass: tc.prune_mass,
    },
  };
  const masses = computeDyadWindowMasses(tc.p_vars, customConfig);
  const modal = getModalPixel(masses);
  pruneResults.push({
    id: tc.id,
    modal,
    masses,
    massCount: Object.keys(masses).length,
  });
}
results.prune = pruneResults;

writeFileSync(outputPath, JSON.stringify(results, null, 2));
console.log("Pathological cases evaluated successfully in TypeScript.");
