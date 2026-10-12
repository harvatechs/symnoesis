# Handoff Report — Milestone M2 Empirical Challenge (Temporal Engine & Counterfactual Repair)

**Author:** Empirical Challenger 2 (`challenger_m2_2`)  
**Timestamp:** 2026-10-12T06:12:00Z  
**Recipient:** Orchestrator (`abfd9134-810e-49b4-885c-c4bd5beb1700`)  
**Scope:** Milestone M2 Temporal Engine & Counterfactual Repair Diagnostics Empirical Validation  
**Verdict:** **REJECT**

---

## 1. Observation

Direct tool execution observations from the empirical stress test battery:

1. **Longitudinal Temporal Engine Battery (530 Trajectories):**
   - Command: `uv run --directory packages/py python ../../tests/test_challenger_m2_empirical.py`
     Output:
     ```
     --- 1. Longitudinal Temporal Engine Stress Tests (530 trajectories) ---
       suite_a_single_drop             : 160/160 passed (0 failed)
       suite_b_consecutive_drops       : 160/160 passed (0 failed)
       suite_c_boundary_oscillations   : 105/105 passed (0 failed)
       suite_d_baseline_uncalibrated   : 105/105 passed (0 failed)
     ```
   - Command: `node tests/test_challenger_m2_empirical_ts.mjs`
     Output:
     ```
     --- 1. TS Longitudinal Temporal Engine Stress Tests (530 trajectories) ---
       suite_a_single_drop             : 160/160 passed (0 failed)
       suite_b_consecutive_drops       : 160/160 passed (0 failed)
       suite_c_boundary_oscillations   : 105/105 passed (0 failed)
       suite_d_baseline_uncalibrated   : 105/105 passed (0 failed)
     ```
   Both Python and TypeScript implementations pass 530/530 trajectories across single drop recovery, two consecutive drops triggering negative trajectory and Zone Z4 Drift, exact boundaries (-5.000 vs -5.010), high-frequency oscillations, and Day 1 baseline uncalibrated handling.

2. **Counterfactual Repair Battery (110 Non-Mutualistic States × 2 Norms = 220 Evaluations):**
   - **Python Reference Implementation (`packages/py/src/symnoesis/counterfactual.py`):**
     Command: `uv run --directory packages/py python ../../tests/test_challenger_m2_empirical.py`
     Output:
     ```
     --- 2. Counterfactual Repair Stress Tests (220 evaluations across 110 states) ---
       Python Counterfactual: 220/220 passed (0 failed)
     ```
     All 220 repaired states strictly achieve Mutualism ($SQ > 20.0$, $HNE > 0.20$, $SNE > 0.20$, $\text{class} = \text{"mutualism"}$).
   - **TypeScript Implementation (`packages/ts/src/counterfactual.ts`):**
     Command: `node tests/test_challenger_m2_empirical_ts.mjs`
     Output:
     ```
     --- 2. TS Counterfactual Repair Stress Tests (220 evaluations) ---
       TypeScript Counterfactual: 112/220 passed (108 failed)

       Sample Failures in TypeScript Counterfactual Repair:
         [FAIL] tag=neutralism norm=l2 stability_std=0.4 -> SQ=19.28 (MUST BE > 20.0), HNE=0.205, SNE=0.593
         [FAIL] tag=neutralism norm=l1 stability_std=0.4 -> SQ=19.28 (MUST BE > 20.0), HNE=0.205, SNE=0.593
         [FAIL] tag=inverse_commensalism norm=l2 stability_std=0.4 -> SQ=19.21 (MUST BE > 20.0), HNE=0.205, SNE=0.589
         [FAIL] tag=inverse_commensalism norm=l1 stability_std=0.4 -> SQ=19.21 (MUST BE > 20.0), HNE=0.205, SNE=0.589
         [FAIL] tag=neutralism norm=l2 stability_std=0.15 -> SQ=17.43 (MUST BE > 20.0), HNE=0.205, SNE=0.205
         [FAIL] tag=neutralism norm=l1 stability_std=0.15 -> SQ=17.43 (MUST BE > 20.0), HNE=0.205, SNE=0.205
         [FAIL] tag=mutual_harm norm=l2 stability_std=0.25 -> SQ=16.40 (MUST BE > 20.0), HNE=0.205, SNE=0.205
     ```
     TypeScript fails 108 out of 220 evaluations (49.1% failure rate) whenever $\text{stability\_std} > 0$.

3. **Code Inspection of Root Cause:**
   - In `packages/ts/src/counterfactual.ts`, lines 431–497, the repair projection only moves $s_h$ until $HNE \ge 0.205$ and moves $(int, rel, op)$ until $SNE \ge 0.205$.
   - It never calculates or constrains composite effect $C$ against stability dampening $S = \text{computeStabilityFactor}(\sigma_C)$.
   - When $\sigma_C > 0$, $S < 1.0$, producing $SQ = 100 \cdot C \cdot S \le 100 \cdot 0.205 \cdot S < 20.0$, violating the mandatory Mutualism condition $SQ > 20.0$.
   - In `packages/ts/tests/counterfactual.test.ts`, line 127, the only existing unit test hardcoded `stability_std: 0.0`, masking this failure.

---

## 2. Logic Chain

1. From **Observation 1**, the Longitudinal Temporal Engine across both Python and TypeScript conforms strictly to SPEC §9 and §10:
   - Single drops $< -MDC$ do not declare negative trajectory.
   - Two consecutive drops $< -MDC$ reliably declare deteriorating trajectory and trigger Governance Zone Z4 Drift according to precedence rules.
   - Boundary drops of $-5.000$ and mixed drops do not trigger false drift.
   - Baseline Day 1 and uncalibrated handling are functionally verified.
2. From **Observation 2 & 3**, the Counterfactual Repair engine in Python succeeds on 100% of cases by utilizing constrained optimization (`scipy.optimize.minimize(method="SLSQP")`) with explicit $SQ \ge 20.005$ constraint.
3. However, the TypeScript port in `packages/ts/src/counterfactual.ts` replaces this with an incomplete heuristic projection that omits the $SQ > 20$ constraint under stability dampening $S < 1$.
4. Whenever non-mutualistic dyads exhibit session instability ($\sigma_C > 0$), TypeScript's `computeCounterfactualRepair` produces states with $SQ \in [10.25, 19.99]$, failing the normative definition of Mutualism ($SQ > 20.0, HNE > 0.20, SNE > 0.20$).
5. Because 108 of 220 empirical evaluations (49.1%) fail this strict acceptance criterion, Milestone M2 fails cross-language parity and correctness in TypeScript.

---

## 3. Caveats

- Python's implementation is completely sound and verified across all 530 trajectories and 220 repair evaluations.
- TypeScript's failure is isolated to `computeCounterfactualRepair` in `packages/ts/src/counterfactual.ts`; its temporal engine and single-flip discrete diagnostics (`computeSingleFlipDiagnostics`) are sound.
- No modifications to implementation code were made, adhering to the Challenger constraint (`Review-only — do NOT modify implementation code`).

---

## 4. Conclusion

**Verdict: REJECT.**

Milestone M2 cannot be approved in its current state due to the critical defect in TypeScript counterfactual repair:
- `packages/ts/src/counterfactual.ts` fails to project non-mutualistic states into Mutualism ($SQ > 20$) whenever `stability_std > 0` (108 failures out of 220 evaluations, 49.1% failure rate).
- The implementation worker must address this by ensuring the projection in `computeCounterfactualRepair` accounts for stability dampening $S$ so that $C \ge \frac{20.005}{100 \cdot S}$.

---

## 5. Verification Method

To independently reproduce these findings:

```powershell
# 1. Run Python empirical challenger harness (530 trajectories, 220 counterfactual evaluations)
uv run --directory packages/py python ../../tests/test_challenger_m2_empirical.py

# 2. Run TypeScript empirical challenger harness (530 trajectories, 220 counterfactual evaluations)
node tests/test_challenger_m2_empirical_ts.mjs

# 3. View failure details in TypeScript test output
# Output shows 108/220 failures where repaired SQ < 20.0 whenever stability_std > 0
```

**Invalidation conditions:** Any test failure in Python's temporal/repair suite, or TypeScript failing to achieve $SQ > 20.0$, $HNE > 0.20$, and $SNE > 0.20$ across all non-mutualistic states.
