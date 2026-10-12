/**
 * Empirical challenger test harness for Milestone M2 in TypeScript.
 *
 * Evaluates:
 * 1. Longitudinal temporal engine (530 trajectories matching Python test conditions)
 * 2. Counterfactual repair across 110 stress states (220 evaluations for L1 and L2)
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { pathToFileURL } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..");

// Import from packages/ts/dist/index.js
const moduleUrl = pathToFileURL(
  path.join(REPO_ROOT, "packages", "ts", "dist", "index.js"),
).href;
const {
  evaluateTrajectory,
  isTrajectoryNegative,
  computeSem,
  computeMdc,
  evaluateZones,
  computeCounterfactualRepair,
  evaluateContinuousState,
  DEFAULT_CONFIG,
} = await import(moduleUrl);

// Simple seeded PRNG for reproducible test sequences
function createRng(seed = 42) {
  let s = seed;
  return function () {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function runTemporalStressTestsTS() {
  const rng = createRng(42);
  const cfg = DEFAULT_CONFIG;

  const results = {
    suite_a_single_drop: { total: 0, passed: 0, failed: 0, failures: [] },
    suite_b_consecutive_drops: { total: 0, passed: 0, failed: 0, failures: [] },
    suite_c_boundary_oscillations: {
      total: 0,
      passed: 0,
      failed: 0,
      failures: [],
    },
    suite_d_baseline_uncalibrated: {
      total: 0,
      passed: 0,
      failed: 0,
      failures: [],
    },
  };

  // Suite A: Single interval drop < -MDC (160 trajectories)
  for (let idx = 0; idx < 160; idx++) {
    const baseSq = 20.0 + rng() * 60.0;
    const dropInterval = Math.floor(rng() * 4);
    const dropMagnitude = 5.05 + rng() * 30.0;

    const scores = [baseSq];
    for (let i = 0; i < 4; i++) {
      if (i === dropInterval) {
        scores.push(scores[scores.length - 1] - dropMagnitude);
      } else {
        const delta = -4.5 + rng() * 19.5;
        scores.push(scores[scores.length - 1] + delta);
      }
    }

    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const isNeg = isTrajectoryNegative(scores, undefined, cfg);

    const passed =
      !traj.is_negative && !isNeg && traj.status !== "deteriorating";
    results.suite_a_single_drop.total++;
    if (passed) {
      results.suite_a_single_drop.passed++;
    } else {
      results.suite_a_single_drop.failed++;
      results.suite_a_single_drop.failures.push({ idx, scores, traj });
    }
  }

  // Suite B: Two consecutive drops < -MDC (160 trajectories)
  for (let idx = 0; idx < 160; idx++) {
    const baseSq = 40.0 + rng() * 50.0;
    const startInterval = Math.floor(rng() * 3);
    const drop1 = 5.01 + rng() * 15.0;
    const drop2 = 5.01 + rng() * 15.0;

    const scores = [baseSq];
    for (let i = 0; i < 4; i++) {
      if (i === startInterval) {
        scores.push(scores[scores.length - 1] - drop1);
      } else if (i === startInterval + 1) {
        scores.push(scores[scores.length - 1] - drop2);
      } else {
        const delta = -4.0 + rng() * 14.0;
        scores.push(scores[scores.length - 1] + delta);
      }
    }

    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const isNeg = isTrajectoryNegative(scores, undefined, cfg);

    const finalSq = scores[scores.length - 1];
    const zoneRes = evaluateZones(
      finalSq,
      [1, 1, 1, 1],
      [1, 1, 1, 1],
      false,
      isNeg,
      cfg,
    );

    let zoneOk = false;
    if (finalSq > -25.0) {
      zoneOk = zoneRes.primary === "Z4";
    } else {
      zoneOk =
        zoneRes.primary === "Z6" && zoneRes.secondary_tags.includes("Z4");
    }

    const passed =
      traj.is_negative && isNeg && traj.status === "deteriorating" && zoneOk;
    results.suite_b_consecutive_drops.total++;
    if (passed) {
      results.suite_b_consecutive_drops.passed++;
    } else {
      results.suite_b_consecutive_drops.failed++;
      results.suite_b_consecutive_drops.failures.push({
        idx,
        scores,
        traj,
        zoneRes,
      });
    }
  }

  // Suite C: Boundary & oscillations (105 trajectories)
  // C1: Exact boundary drops of -5.00
  for (let i = 0; i < 20; i++) {
    const s0 = 50.0 + rng() * 30.0;
    const scores = [s0, s0 - 5.0, s0 - 10.0, s0 - 12.0, s0 - 10.0];
    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const passed = !traj.is_negative && traj.status !== "deteriorating";
    results.suite_c_boundary_oscillations.total++;
    if (passed) results.suite_c_boundary_oscillations.passed++;
    else results.suite_c_boundary_oscillations.failed++;
  }

  // C2: Near boundary [-4.99, -4.99]
  for (let i = 0; i < 20; i++) {
    const s0 = 50.0 + rng() * 30.0;
    const scores = [s0, s0 - 4.99, s0 - 9.98, s0 - 9.0, s0 - 8.0];
    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const passed = !traj.is_negative;
    results.suite_c_boundary_oscillations.total++;
    if (passed) results.suite_c_boundary_oscillations.passed++;
    else results.suite_c_boundary_oscillations.failed++;
  }

  // C3: Near boundary [-5.01, -5.01]
  for (let i = 0; i < 20; i++) {
    const s0 = 50.0 + rng() * 30.0;
    const scores = [s0, s0 - 5.01, s0 - 10.02, s0 - 8.0, s0 - 5.0];
    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const passed = traj.is_negative && traj.status === "deteriorating";
    results.suite_c_boundary_oscillations.total++;
    if (passed) results.suite_c_boundary_oscillations.passed++;
    else results.suite_c_boundary_oscillations.failed++;
  }

  // C4: Mixed boundary [-5.01, -4.99]
  for (let i = 0; i < 20; i++) {
    const s0 = 50.0 + rng() * 30.0;
    const firstDrop = rng() < 0.5 ? -5.01 : -4.99;
    const secondDrop = firstDrop === -5.01 ? -4.99 : -5.01;
    const scores = [
      s0,
      s0 + firstDrop,
      s0 + firstDrop + secondDrop,
      s0,
      s0 + 5.0,
    ];
    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const passed = !traj.is_negative;
    results.suite_c_boundary_oscillations.total++;
    if (passed) results.suite_c_boundary_oscillations.passed++;
    else results.suite_c_boundary_oscillations.failed++;
  }

  // C5: Oscillations
  for (let i = 0; i < 25; i++) {
    const s0 = 40.0 + rng() * 30.0;
    const amp = 8.0 + rng() * 20.0;
    const scores = [s0, s0 - amp, s0 + 2.0, s0 - amp, s0 + 3.0];
    const traj = evaluateTrajectory(scores, undefined, undefined, cfg);
    const passed = !traj.is_negative;
    results.suite_c_boundary_oscillations.total++;
    if (passed) results.suite_c_boundary_oscillations.passed++;
    else results.suite_c_boundary_oscillations.failed++;
  }

  // Suite D: Baseline Day 1 & Uncalibrated (105 trajectories)
  // D1: Single frame at Day 1
  for (let i = 0; i < 25; i++) {
    const s = -50.0 + rng() * 130.0;
    const traj = evaluateTrajectory([s], [1], undefined, cfg);
    const passed =
      traj.is_baseline === true &&
      traj.status === "stable" &&
      !traj.is_negative &&
      traj.deltas.length === 0;
    results.suite_d_baseline_uncalibrated.total++;
    if (passed) results.suite_d_baseline_uncalibrated.passed++;
    else results.suite_d_baseline_uncalibrated.failed++;
  }

  // D2: Single frame at Day 7
  for (let i = 0; i < 25; i++) {
    const s = -50.0 + rng() * 130.0;
    const traj = evaluateTrajectory([s], [7], undefined, cfg);
    const passed =
      traj.is_baseline === false &&
      traj.status === "stable" &&
      !traj.is_negative &&
      traj.deltas.length === 0;
    results.suite_d_baseline_uncalibrated.total++;
    if (passed) results.suite_d_baseline_uncalibrated.passed++;
    else results.suite_d_baseline_uncalibrated.failed++;
  }

  // D3: Two frames
  for (let i = 0; i < 25; i++) {
    const s1 = 50.0 + rng() * 40.0;
    const s2 = s1 - (10.0 + rng() * 40.0);
    const traj = evaluateTrajectory([s1, s2], [1, 7], undefined, cfg);
    const passed =
      traj.is_baseline === false &&
      traj.status === "stable" &&
      !traj.is_negative &&
      traj.deltas.length === 1;
    results.suite_d_baseline_uncalibrated.total++;
    if (passed) results.suite_d_baseline_uncalibrated.passed++;
    else results.suite_d_baseline_uncalibrated.failed++;
  }

  // D4: Calibrated MDC
  for (let i = 0; i < 30; i++) {
    const sd = 8.0 + rng() * 7.0;
    const r = 0.7 + rng() * 0.25;
    const sem = computeSem(sd, r);
    const calibratedMdc = computeMdc(sem);
    const expectedMdc = 1.96 * Math.SQRT2 * sem;
    const formulaOk = Math.abs(calibratedMdc - expectedMdc) < 1e-9;

    const scores = [
      100.0,
      100.0 - (calibratedMdc - 1.0),
      100.0 - 2 * (calibratedMdc - 1.0),
    ];
    const trajCalibrated = evaluateTrajectory(
      scores,
      undefined,
      calibratedMdc,
      cfg,
    );
    const passed = formulaOk && !trajCalibrated.is_negative;
    results.suite_d_baseline_uncalibrated.total++;
    if (passed) results.suite_d_baseline_uncalibrated.passed++;
    else results.suite_d_baseline_uncalibrated.failed++;
  }

  return results;
}

function runCounterfactualStressTestsTS() {
  const cfg = DEFAULT_CONFIG;
  const statesPath = path.join(REPO_ROOT, "tests", "cf_stress_states.json");
  const states = JSON.parse(fs.readFileSync(statesPath, "utf8"));

  const results = {
    total: 0,
    passed: 0,
    failed: 0,
    failures: [],
  };

  for (const item of states) {
    const st = {
      s_h: item.s_h,
      integrity: item.integrity,
      reliability: item.reliability,
      operator: item.operator,
      stability_std: item.stability_std,
    };

    for (const norm of ["l2", "l1"]) {
      const res = computeCounterfactualRepair(st, norm, cfg);
      const repEval = evaluateContinuousState(res.repaired_state, cfg);

      // Strict Mutualism verification criteria:
      // SQ > 20.0, HNE > 0.2, SNE > 0.2, class == "mutualism"
      const passed =
        repEval.sq > 20.0 &&
        repEval.hne > 0.2 &&
        repEval.sne > 0.2 &&
        repEval.technical_name === "mutualism";

      results.total++;
      if (passed) {
        results.passed++;
      } else {
        results.failed++;
        results.failures.push({
          tag: item.tag,
          norm,
          stability_std: item.stability_std,
          repaired_hne: repEval.hne,
          repaired_sne: repEval.sne,
          repaired_sq: repEval.sq,
          repaired_class: repEval.technical_name,
        });
      }
    }
  }

  return results;
}

function main() {
  console.log(
    "=================================================================",
  );
  console.log("  SYMNOESIS M2 EMPIRICAL CHALLENGER TEST HARNESS (TYPESCRIPT)");
  console.log(
    "=================================================================",
  );

  const tempResults = runTemporalStressTestsTS();
  const totalTemp = Object.values(tempResults).reduce(
    (acc, s) => acc + s.total,
    0,
  );
  const passedTemp = Object.values(tempResults).reduce(
    (acc, s) => acc + s.passed,
    0,
  );
  const failedTemp = Object.values(tempResults).reduce(
    (acc, s) => acc + s.failed,
    0,
  );

  console.log(
    `\n--- 1. TS Longitudinal Temporal Engine Stress Tests (${totalTemp} trajectories) ---`,
  );
  for (const [name, r] of Object.entries(tempResults)) {
    console.log(
      `  ${name.padEnd(32)}: ${r.passed}/${r.total} passed (${r.failed} failed)`,
    );
    if (r.failed > 0) {
      for (const f of r.failures.slice(0, 3)) {
        console.log(`    FAIL SAMPLE:`, JSON.stringify(f));
      }
    }
  }

  const cfResults = runCounterfactualStressTestsTS();
  console.log(
    `\n--- 2. TS Counterfactual Repair Stress Tests (${cfResults.total} evaluations) ---`,
  );
  console.log(
    `  TypeScript Counterfactual: ${cfResults.passed}/${cfResults.total} passed (${cfResults.failed} failed)`,
  );
  if (cfResults.failed > 0) {
    console.log(`\n  Sample Failures in TypeScript Counterfactual Repair:`);
    for (const f of cfResults.failures.slice(0, 10)) {
      console.log(
        `    [FAIL] tag=${f.tag} norm=${f.norm} stability_std=${f.stability_std} -> SQ=${f.repaired_sq.toFixed(2)} (MUST BE > 20.0), HNE=${f.repaired_hne.toFixed(3)}, SNE=${f.repaired_sne.toFixed(3)}`,
      );
    }
  }

  const report = {
    temporal: {
      total: totalTemp,
      passed: passedTemp,
      failed: failedTemp,
      suites: tempResults,
    },
    counterfactual_ts: cfResults,
  };
  fs.writeFileSync(
    path.join(REPO_ROOT, "tests", "m2_empirical_summary_ts.json"),
    JSON.stringify(report, null, 2),
  );
}

main();
