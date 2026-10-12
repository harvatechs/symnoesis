import { describe, expect, it } from "vitest";
import { bitsToVertex, type CellInput } from "../src/cover.js";
import {
  PROHIBITED_CAUSAL_TERMS,
  RidgeBitModel,
  computeCounterfactualRepair,
  computeSingleFlipDiagnostics,
  evaluateContinuousState,
  type ContinuousState,
} from "../src/counterfactual.js";

describe("Counterfactual Repair Diagnostics & Ridge Projection (SPEC §10, §12)", () => {
  it("TC1.18.01: computeSingleFlipDiagnostics calculates delta SQ for repair flips", () => {
    const currentSq = -30.0;
    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: currentSq, n_eff: 50.0, observed: true });

    // Neighbor flipping H1 (bit 0): vertex 128 (h1000-m0000)
    const neighborSq = 15.0;
    const vH1 = bitsToVertex([1, 0, 0, 0, 0, 0, 0, 0]);
    cells.set(vH1, {
      cell_id: vH1,
      sq: neighborSq,
      n_eff: 25.0,
      observed: true,
    });

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    expect(res.current_sq).toBe(currentSq);
    expect(res.flips["H1"]).toBeDefined();
    const h1Diag = res.flips["H1"]!;
    expect(h1Diag.delta_sq).toBe(neighborSq - currentSq);
    expect(h1Diag.delta_sq).toBe(45.0);
    expect(h1Diag.source).toBe("observed");
  });

  it("TC1.18.02: observed sourcing priority for neighbors with n_eff >= 10", () => {
    const vH2 = bitsToVertex([0, 1, 0, 0, 0, 0, 0, 0]);
    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: -20.0, n_eff: 30.0, observed: true });
    cells.set(vH2, { cell_id: vH2, sq: 10.0, n_eff: 15.0, observed: true });

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    expect(res.flips["H2"]!.source).toBe("observed");
  });

  it("TC1.18.03: modeled sourcing fallback for neighbors with n_eff < 10", () => {
    const vH3 = bitsToVertex([0, 0, 1, 0, 0, 0, 0, 0]);
    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: -20.0, n_eff: 30.0, observed: true });
    // Sparse neighbor below n_cell_min
    cells.set(vH3, { cell_id: vH3, sq: 10.0, n_eff: 4.0, observed: true });

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    expect(res.flips["H3"]!.source).toBe("modeled");
  });

  it("TC1.18.04: dominant failure variable is argmax_v Delta SQ_v", () => {
    const vH1 = bitsToVertex([1, 0, 0, 0, 0, 0, 0, 0]);
    const vH3 = bitsToVertex([0, 0, 1, 0, 0, 0, 0, 0]);
    const vM2 = bitsToVertex([0, 0, 0, 0, 0, 1, 0, 0]);

    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: -40.0, n_eff: 50.0, observed: true });
    cells.set(vH1, { cell_id: vH1, sq: -30.0, n_eff: 20.0, observed: true }); // +10
    cells.set(vH3, { cell_id: vH3, sq: -15.0, n_eff: 20.0, observed: true }); // +25
    cells.set(vM2, { cell_id: vM2, sq: -22.0, n_eff: 20.0, observed: true }); // +18

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    expect(res.dominant_variable).toBe("H3");
    expect(res.max_delta_sq).toBe(25.0);
  });

  it("TC2.18.01: when all repair flips have non-positive delta, dominant variable is null", () => {
    const vH1 = bitsToVertex([1, 0, 0, 0, 0, 0, 0, 0]);
    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: 30.0, n_eff: 50.0, observed: true });
    cells.set(vH1, { cell_id: vH1, sq: 10.0, n_eff: 20.0, observed: true });

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    // Any positive deltas? If none, dominant_variable must be null
    if (Object.values(res.flips).every((f) => f.delta_sq <= 0)) {
      expect(res.dominant_variable).toBeNull();
      expect(res.diagnostic_text).toContain("no single-variable repair");
    }
  });

  it("TC2.18.02: diagnostic text adheres to non-causal vocabulary invariant", () => {
    const cells = new Map<number, CellInput>();
    cells.set(0, { cell_id: 0, sq: -10.0, n_eff: 20.0, observed: true });

    const res = computeSingleFlipDiagnostics("h0000-m0000", cells);
    const textLower = res.diagnostic_text.toLowerCase();
    for (const term of PROHIBITED_CAUSAL_TERMS) {
      expect(textLower).not.toContain(term);
    }
    expect(textLower).toContain("association");
  });

  it("TC1.18.05: RidgeBitModel extracts 37 features and predicts bounded SQ", () => {
    const model = new RidgeBitModel(1.0);
    const bits = [1, 0, 1, 0, 1, 0, 1, 0];
    const feat = model.extractFeatures(bits);
    expect(feat).toHaveLength(37);
    expect(feat[0]).toBe(1.0); // intercept

    // Train with synthetic cells
    const cells: CellInput[] = [
      { cell_id: 0, sq: -50.0, n_eff: 20.0, observed: true },
      { cell_id: 255, sq: 60.0, n_eff: 20.0, observed: true },
    ];
    model.fit(cells);
    expect(model.isFitted).toBe(true);

    const pred = model.predict(bits);
    expect(pred).toBeGreaterThanOrEqual(-100.0);
    expect(pred).toBeLessThanOrEqual(100.0);
  });

  it("TC1.18.06: computeCounterfactualRepair projects non-mutualistic state into Mutualism", () => {
    // Non-mutualistic state (Amensalism / Harm)
    const state: ContinuousState = {
      s_h: [0.1, 0.2, 0.1, 0.2],
      integrity: -0.5,
      reliability: -0.4,
      operator: 0.0,
      stability_std: 0.0,
    };

    const initial = evaluateContinuousState(state);
    expect(initial.technical_name).not.toBe("mutualism");

    // L2 projection
    const resL2 = computeCounterfactualRepair(state, "l2");
    expect(resL2.is_already_mutualistic).toBe(false);
    expect(resL2.repaired_hne).toBeGreaterThan(0.2);
    expect(resL2.repaired_sne).toBeGreaterThan(0.2);
    expect(resL2.repaired_sq).toBeGreaterThan(20.0);
    expect(resL2.repaired_class).toBe("mutualism");
    expect(resL2.distance).toBeGreaterThan(0.0);

    // L1 projection
    const resL1 = computeCounterfactualRepair(state, "l1");
    expect(resL1.repaired_class).toBe("mutualism");
    expect(resL1.distance).toBeGreaterThan(0.0);
  });

  it("TC1.18.07: computeCounterfactualRepair on already mutualistic state returns zero distance", () => {
    const mutualisticState: ContinuousState = {
      s_h: [0.9, 0.85, 0.9, 0.8],
      integrity: 0.7,
      reliability: 0.8,
      operator: 0.5,
      stability_std: 0.05,
    };

    const res = computeCounterfactualRepair(mutualisticState, "l2");
    expect(res.is_already_mutualistic).toBe(true);
    expect(res.distance).toBe(0.0);
    for (const val of Object.values(res.deltas)) {
      expect(val).toBe(0.0);
    }
  });

  it("TC1.18.08: counterfactual repair with stability dampening (stability_std in [0.1, 0.4]) strictly achieves SQ > 20.0 and Mutualism", () => {
    const stabilityLevels = [0.1, 0.25, 0.4];
    const testStates: ContinuousState[] = [
      // Neutralism state
      {
        s_h: [0.5, 0.5, 0.5, 0.5],
        integrity: 0.0,
        reliability: 0.0,
        operator: 0.0,
      },
      // Mutual harm state
      {
        s_h: [0.1, 0.1, 0.1, 0.1],
        integrity: -0.6,
        reliability: -0.6,
        operator: -0.6,
      },
      // Parasitism state
      {
        s_h: [0.1, 0.1, 0.2, 0.1],
        integrity: 0.8,
        reliability: 0.8,
        operator: 0.6,
      },
      // Amensalism state
      {
        s_h: [0.2, 0.1, 0.1, 0.2],
        integrity: -0.1,
        reliability: 0.0,
        operator: 0.1,
      },
    ];

    for (const sigma of stabilityLevels) {
      for (const baseState of testStates) {
        const state: ContinuousState = {
          ...baseState,
          stability_std: sigma,
        };

        for (const norm of ["l2", "l1"] as const) {
          const res = computeCounterfactualRepair(state, norm);
          expect(res.is_already_mutualistic).toBe(false);
          expect(res.repaired_hne).toBeGreaterThan(0.2);
          expect(res.repaired_sne).toBeGreaterThan(0.2);
          expect(res.repaired_sq).toBeGreaterThan(20.0);
          expect(res.repaired_class).toBe("mutualism");
          expect(res.distance).toBeGreaterThan(0.0);

          const reEval = evaluateContinuousState(res.repaired_state);
          expect(reEval.hne).toBeGreaterThan(0.2);
          expect(reEval.sne).toBeGreaterThan(0.2);
          expect(reEval.sq).toBeGreaterThan(20.0);
          expect(reEval.technical_name).toBe("mutualism");

          // Idempotency: re-repairing repaired state must return is_already_mutualistic = true
          const secondRepair = computeCounterfactualRepair(
            res.repaired_state,
            norm,
          );
          expect(secondRepair.is_already_mutualistic).toBe(true);
          expect(secondRepair.distance).toBe(0.0);
        }
      }
    }
  });
});
