/**
 * Empirical Adversarial Challenger: Stochastic Stability & Boundary Stress Test
 * Milestone M2 Iteration 2 (Counterfactual Repair Remediation).
 *
 * Tests:
 * 1. Random stability std dev sigma_C in [0.01, 0.49] across 500 diverse non-mutualistic states (1,000 evaluations).
 * 2. Deterministic boundary grid sweep: 110 stress states across 11 discrete sigma_C values (2,420 evaluations).
 * 3. Extreme edge-case states: all-zeros, max-human/min-system, min-human/max-system, near-boundary mutualism.
 * 4. Boundary sigma_C values: sigma_C = 0.01, 0.49, 0.4999, 0.5000.
 * 5. Idempotency verification: repairing an already-repaired state returns is_already_mutualistic = true, distance = 0.
 *
 * Success criterion:
 * 100% of repaired outputs strictly achieve:
 *   - SQ > 20.0
 *   - HNE > 0.20
 *   - SNE > 0.20
 *   - technical_name === 'mutualism'
 */

import fs from "fs";
import path from "path";
import { fileURLToPath, pathToFileURL } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..");

const moduleUrl = pathToFileURL(
  path.join(REPO_ROOT, "packages", "ts", "dist", "index.js"),
).href;
const { computeCounterfactualRepair, evaluateContinuousState, DEFAULT_CONFIG } =
  await import(moduleUrl);

// Seeded PRNG (Lehmer LCG)
function createRng(seed = 1337) {
  let s = seed;
  return function () {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function generateRandomNonMutualisticState(rng) {
  // Generate states across all 8 non-mutualistic regimes
  const regimes = [
    "commensalism",
    "sacrificial",
    "inverse_commensalism",
    "neutralism",
    "antagonism",
    "parasitism",
    "amensalism",
    "mutual_harm",
  ];
  const regime = regimes[Math.floor(rng() * regimes.length)];

  let s_h = [rng(), rng(), rng(), rng()];
  let integrity = -1.0 + 2.0 * rng();
  let reliability = -1.0 + 2.0 * rng();
  let operator = -1.0 + 2.0 * rng();

  if (regime === "commensalism") {
    // HNE > 0.2, SNE in [-0.2, 0.2]
    s_h = [
      0.7 + 0.3 * rng(),
      0.7 + 0.3 * rng(),
      0.7 + 0.3 * rng(),
      0.7 + 0.3 * rng(),
    ];
    integrity = -0.15 + 0.3 * rng();
    reliability = -0.15 + 0.3 * rng();
    operator = -0.15 + 0.3 * rng();
  } else if (regime === "sacrificial") {
    // HNE > 0.2, SNE < -0.2
    s_h = [
      0.75 + 0.25 * rng(),
      0.75 + 0.25 * rng(),
      0.75 + 0.25 * rng(),
      0.75 + 0.25 * rng(),
    ];
    integrity = -0.9 + 0.5 * rng();
    reliability = -0.9 + 0.5 * rng();
    operator = -0.9 + 0.5 * rng();
  } else if (regime === "inverse_commensalism") {
    // HNE in [-0.2, 0.2], SNE > 0.2
    s_h = [
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
    ];
    integrity = 0.6 + 0.4 * rng();
    reliability = 0.6 + 0.4 * rng();
    operator = 0.6 + 0.4 * rng();
  } else if (regime === "neutralism") {
    // HNE in [-0.2, 0.2], SNE in [-0.2, 0.2]
    s_h = [
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
    ];
    integrity = -0.15 + 0.3 * rng();
    reliability = -0.15 + 0.3 * rng();
    operator = -0.15 + 0.3 * rng();
  } else if (regime === "antagonism") {
    // HNE in [-0.2, 0.2], SNE < -0.2
    s_h = [
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
      0.45 + 0.15 * rng(),
    ];
    integrity = -0.9 + 0.5 * rng();
    reliability = -0.9 + 0.5 * rng();
    operator = -0.9 + 0.5 * rng();
  } else if (regime === "parasitism") {
    // HNE < -0.2, SNE > 0.2
    s_h = [0.1 * rng(), 0.15 * rng(), 0.1 * rng(), 0.15 * rng()];
    integrity = 0.6 + 0.4 * rng();
    reliability = 0.6 + 0.4 * rng();
    operator = 0.6 + 0.4 * rng();
  } else if (regime === "amensalism") {
    // HNE < -0.2, SNE in [-0.2, 0.2]
    s_h = [0.1 * rng(), 0.15 * rng(), 0.1 * rng(), 0.15 * rng()];
    integrity = -0.15 + 0.3 * rng();
    reliability = -0.15 + 0.3 * rng();
    operator = -0.15 + 0.3 * rng();
  } else if (regime === "mutual_harm") {
    // HNE < -0.2, SNE < -0.2
    s_h = [0.1 * rng(), 0.15 * rng(), 0.1 * rng(), 0.15 * rng()];
    integrity = -0.9 + 0.5 * rng();
    reliability = -0.9 + 0.5 * rng();
    operator = -0.9 + 0.5 * rng();
  }

  // Sample sigma_C uniformly in [0.01, 0.49]
  const stability_std = 0.01 + rng() * (0.49 - 0.01);

  return {
    regime,
    s_h,
    integrity,
    reliability,
    operator,
    stability_std,
  };
}

function evaluateRepair(st, norm, cfg) {
  const res = computeCounterfactualRepair(st, norm, cfg);
  const repEval = evaluateContinuousState(res.repaired_state, cfg);

  const isMutualism =
    repEval.sq > 20.0 &&
    repEval.hne > 0.2 &&
    repEval.sne > 0.2 &&
    repEval.technical_name === "mutualism";

  // Check idempotency: repairing repaired_state must return is_already_mutualistic
  const reRepair = computeCounterfactualRepair(res.repaired_state, norm, cfg);
  const isIdempotent =
    reRepair.is_already_mutualistic && reRepair.distance === 0.0;

  return {
    passed: isMutualism && isIdempotent,
    isMutualism,
    isIdempotent,
    res,
    repEval,
  };
}

async function runStochasticStabilityChallenge() {
  const cfg = DEFAULT_CONFIG;
  const rng = createRng(9999);

  console.log(
    "======================================================================",
  );
  console.log(
    "  SYMNOESIS M2 ADVERSARIAL CHALLENGE: STOCHASTIC STABILITY [0.01, 0.49]",
  );
  console.log(
    "======================================================================\n",
  );

  // -------------------------------------------------------------------------
  // Part 1: 500 Random Non-Mutualistic States with sigma_C in [0.01, 0.49]
  // -------------------------------------------------------------------------
  console.log(
    ">>> Part 1: Random States with sigma_C in [0.01, 0.49] (1,000 evaluations)...",
  );
  let p1Total = 0;
  let p1Passed = 0;
  let p1Failures = [];

  for (let i = 0; i < 500; i++) {
    const rawSt = generateRandomNonMutualisticState(rng);
    const st = {
      s_h: rawSt.s_h,
      integrity: rawSt.integrity,
      reliability: rawSt.reliability,
      operator: rawSt.operator,
      stability_std: rawSt.stability_std,
    };

    for (const norm of ["l2", "l1"]) {
      p1Total++;
      const check = evaluateRepair(st, norm, cfg);
      if (check.passed) {
        p1Passed++;
      } else {
        p1Failures.push({
          idx: i,
          regime: rawSt.regime,
          norm,
          sigma_c: rawSt.stability_std,
          sq: check.repEval.sq,
          hne: check.repEval.hne,
          sne: check.repEval.sne,
          technical_name: check.repEval.technical_name,
          isMutualism: check.isMutualism,
          isIdempotent: check.isIdempotent,
        });
      }
    }
  }
  console.log(
    `  Part 1 Result: ${p1Passed}/${p1Total} passed (${p1Failures.length} failed)`,
  );

  // -------------------------------------------------------------------------
  // Part 2: Deterministic Grid: 110 Benchmark States x 11 sigma_C values (2,420 evaluations)
  // -------------------------------------------------------------------------
  console.log(
    "\n>>> Part 2: 110 Benchmark States x 11 sigma_C values (2,420 evaluations)...",
  );
  const statesPath = path.join(REPO_ROOT, "tests", "cf_stress_states.json");
  const benchStates = JSON.parse(fs.readFileSync(statesPath, "utf8"));
  const sigmaSteps = [
    0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.49,
  ];

  let p2Total = 0;
  let p2Passed = 0;
  let p2Failures = [];

  for (const bState of benchStates) {
    for (const sigma of sigmaSteps) {
      const st = {
        s_h: bState.s_h,
        integrity: bState.integrity,
        reliability: bState.reliability,
        operator: bState.operator,
        stability_std: sigma,
      };

      for (const norm of ["l2", "l1"]) {
        p2Total++;
        const check = evaluateRepair(st, norm, cfg);
        if (check.passed) {
          p2Passed++;
        } else {
          p2Failures.push({
            tag: bState.tag,
            norm,
            sigma,
            sq: check.repEval.sq,
            hne: check.repEval.hne,
            sne: check.repEval.sne,
            technical_name: check.repEval.technical_name,
          });
        }
      }
    }
  }
  console.log(
    `  Part 2 Result: ${p2Passed}/${p2Total} passed (${p2Failures.length} failed)`,
  );

  // -------------------------------------------------------------------------
  // Part 3: Extreme Adversarial Boundary States
  // -------------------------------------------------------------------------
  console.log(
    "\n>>> Part 3: Extreme Adversarial Boundary States & Corner Cases...",
  );
  const extremeStates = [
    {
      name: "All minimum (worst case: s_h=0, sys=-1)",
      s_h: [0.0, 0.0, 0.0, 0.0],
      integrity: -1.0,
      reliability: -1.0,
      operator: -1.0,
    },
    {
      name: "Human maxed (s_h=1), System min (-1)",
      s_h: [1.0, 1.0, 1.0, 1.0],
      integrity: -1.0,
      reliability: -1.0,
      operator: -1.0,
    },
    {
      name: "Human zero (s_h=0), System max (+1)",
      s_h: [0.0, 0.0, 0.0, 0.0],
      integrity: 1.0,
      reliability: 1.0,
      operator: 1.0,
    },
    {
      name: "Boundary near-mutualism (HNE=0.199, SNE=0.199)",
      s_h: [0.5995, 0.5995, 0.5995, 0.5995],
      integrity: 0.199,
      reliability: 0.199,
      operator: 0.199,
    },
    {
      name: "High positive effect but heavy instability dampening (HNE=0.25, SNE=0.25)",
      s_h: [0.625, 0.625, 0.625, 0.625],
      integrity: 0.25,
      reliability: 0.25,
      operator: 0.25,
    },
    {
      name: "Asymmetric partial max: H1=1, H2=1, H3=0, H4=0, int=1, rel=-1, op=-1",
      s_h: [1.0, 1.0, 0.0, 0.0],
      integrity: 1.0,
      reliability: -1.0,
      operator: -1.0,
    },
    {
      name: "Near-saturation headroom: all vars = 0.99",
      s_h: [0.99, 0.99, 0.99, 0.99],
      integrity: 0.99,
      reliability: 0.99,
      operator: 0.99,
    },
  ];

  const testSigmas = [0.01, 0.15, 0.35, 0.49, 0.4999, 0.5];
  let p3Total = 0;
  let p3Passed = 0;
  let p3Failures = [];

  for (const ex of extremeStates) {
    for (const sigma of testSigmas) {
      const st = {
        s_h: ex.s_h,
        integrity: ex.integrity,
        reliability: ex.reliability,
        operator: ex.operator,
        stability_std: sigma,
      };

      for (const norm of ["l2", "l1"]) {
        p3Total++;
        const check = evaluateRepair(st, norm, cfg);
        if (check.passed) {
          p3Passed++;
        } else {
          p3Failures.push({
            name: ex.name,
            norm,
            sigma,
            sq: check.repEval.sq,
            hne: check.repEval.hne,
            sne: check.repEval.sne,
            technical_name: check.repEval.technical_name,
            isMutualism: check.isMutualism,
            isIdempotent: check.isIdempotent,
          });
        }
      }
    }
  }
  console.log(
    `  Part 3 Result: ${p3Passed}/${p3Total} passed (${p3Failures.length} failed)`,
  );

  // Summary
  const grandTotal = p1Total + p2Total + p3Total;
  const grandPassed = p1Passed + p2Passed + p3Passed;
  const grandFailed = p1Failures.length + p2Failures.length + p3Failures.length;
  const passRate = ((grandPassed / grandTotal) * 100).toFixed(2);

  console.log(
    "\n======================================================================",
  );
  console.log(
    `  GRAND TOTAL: ${grandPassed}/${grandTotal} passed (${passRate}%)`,
  );
  console.log(`  FAILURES: ${grandFailed}`);
  console.log(
    "======================================================================",
  );

  if (grandFailed > 0) {
    console.log("\nSample Failures:");
    const allFails = [...p1Failures, ...p2Failures, ...p3Failures];
    for (const f of allFails.slice(0, 10)) {
      console.log("  ", JSON.stringify(f));
    }
  }

  const resultsData = {
    summary: {
      grandTotal,
      grandPassed,
      grandFailed,
      passRate: parseFloat(passRate),
      verdict: grandFailed === 0 ? "APPROVE" : "REJECT",
    },
    part1_random_sweep: {
      total: p1Total,
      passed: p1Passed,
      failed: p1Failures.length,
    },
    part2_boundary_grid: {
      total: p2Total,
      passed: p2Passed,
      failed: p2Failures.length,
    },
    part3_extreme_states: {
      total: p3Total,
      passed: p3Passed,
      failed: p3Failures.length,
    },
    failures: [...p1Failures, ...p2Failures, ...p3Failures].slice(0, 50),
  };

  fs.writeFileSync(
    path.join(REPO_ROOT, "tests", "m2_stochastic_stability_results.json"),
    JSON.stringify(resultsData, null, 2),
  );

  return resultsData;
}

runStochasticStabilityChallenge();
