# Empirical Challenge & Stress-Test Analysis — Milestone M2 (Challenger 2)

**Focus:** Temporal Engine (Longitudinal Trajectories, MDC, Zone Z4 Drift) and Counterfactual Repair Diagnostics (Single-Flip & Continuous Projections).  
**Evaluator:** Challenger 2 (`challenger_m2_2`)  
**Timestamp:** 2026-10-12T06:10:00Z  
**Verdict:** **REJECT** (Critical empirical failure in TypeScript continuous counterfactual repair).

---

## 1. Executive Summary

We designed, executed, and analyzed an empirical stress-testing battery comprising:
1. **530 Longitudinal Trajectories** across four distinct challenge regimes:
   - **Suite A:** 160 trajectories with single interval drops exceeding Minimum Detectable Change ($\Delta SQ < -MDC$).
   - **Suite B:** 160 trajectories with two consecutive interval drops exceeding $-MDC$, cross-verified against Governance Zone Z4 Drift assignment and precedence rules.
   - **Suite C:** 105 trajectories at exact and near boundaries ($\Delta SQ = -5.000$, $-4.990$ vs $-5.010$, mixed boundaries, and large-amplitude oscillations).
   - **Suite D:** 105 trajectories testing baseline Day 1 uncalibrated handling, insufficient frame counts ($N < 3$), and calibrated test-retest reliability models ($MDC = 1.96 \cdot \sqrt{2} \cdot SEM$).
2. **220 Continuous Counterfactual Repair Evaluations** (110 unique non-mutualistic states evaluated under both $L_1$ and $L_2$ norms) spanning all 8 non-mutualistic symbiosis classes (*Commensalism, Sacrificial, Inverse commensalism, Neutralism, Antagonism, Parasitism, Amensalism, Mutual harm*) and stability dampening conditions ($\sigma_C \in [0.0, 0.5]$).

### Summary Scorecard

| Component | Target System | Executed Tests | Passed | Failed | Pass Rate | Status |
|---|---|---|---|---|---|---|
| Longitudinal Engine (530 trajectories) | Python (`temporal.py`) | 530 | 530 | 0 | 100.0% | **ROBUST** |
| Longitudinal Engine (530 trajectories) | TypeScript (`temporal.ts`) | 530 | 530 | 0 | 100.0% | **ROBUST** |
| Cross-Language Parity (Trajectories) | Python ↔ TS Parity | 530 | 530 | 0 | 100.0% | **IDENTICAL** |
| Counterfactual Repair (110 states × 2 norms) | Python (`counterfactual.py`) | 220 | 220 | 0 | 100.0% | **ROBUST** |
| Counterfactual Repair (110 states × 2 norms) | TypeScript (`counterfactual.ts`) | 220 | 112 | 108 | 50.9% | **FAILED (49.1% Fail Rate)** |

---

## 2. Longitudinal Temporal Engine Empirical Findings

### 2.1 Suite A: Single Interval Drop Isolation ($\Delta SQ < -MDC$)
- **Normative Requirement (SPEC §10):** A negative trajectory requires *two consecutive intervals* with $\Delta SQ < -MDC$. A single drop followed by recovery or plateau must NOT declare a deteriorating trajectory.
- **Empirical Harness:** 160 synthetic multi-frame trajectories with baseline $SQ \in [20, 80]$, where exactly one interval dropped by $5.05$ to $35.0$ points ($\Delta SQ < -MDC$), while all other intervals remained above $-MDC$.
- **Empirical Results:**
  - Python: **160/160 PASSED** (`is_negative = False`, `status != "deteriorating"`).
  - TypeScript: **160/160 PASSED** (`is_negative = false`, `status !== "deteriorating"`).
  - Even catastrophic drops (e.g., $SQ$ crashing from $80.0$ to $20.0$, $\Delta SQ = -60.0$) in an isolated interval do not trigger negative trajectory if not sustained consecutively.

### 2.2 Suite B: Two Consecutive Interval Drops ($\Delta SQ < -MDC$) & Zone Z4 Drift
- **Normative Requirement (SPEC §9, §10):** Two consecutive intervals with $\Delta SQ < -MDC$ MUST trigger deteriorating status (`is_negative = True`) and activate Governance Zone Z4 Drift. Under strict zone precedence (`[Z7, Z6, Z5, Z4, Z1, Z2, Z3]`), if no CHI event (Z7), no catastrophic harm $SQ \le -25$ (Z6), and no dependence (Z5) exists, primary governance zone MUST be **Z4**. If Z6 applies, Z4 MUST be included in `secondary_tags`.
- **Empirical Harness:** 160 synthetic trajectories with starting consecutive drops at intervals (0, 1), (1, 2), or (2, 3), with drop magnitudes between $5.01$ and $20.0$ points.
- **Empirical Results:**
  - Python: **160/160 PASSED** (`is_negative = True`, `status = "deteriorating"`, Zone Z4 assigned).
  - TypeScript: **160/160 PASSED** (`is_negative = true`, `status = "deteriorating"`, Zone Z4 assigned).
  - When final $SQ = 55.0$ (normally Z2 Productive), Z4 correctly overrides Z2 as primary.
  - When final $SQ = 75.0$ (normally Z1 Symbiotic), negative trajectory invalidates Z1 condition, and Z4 correctly becomes primary.
  - When final $SQ = -35.0$ (Z6 Harm), Z6 is primary and Z4 is strictly recorded in `secondary_tags`.

### 2.3 Suite C: Boundary Thresholds & High-Frequency Oscillations
- **Normative Requirement:** Strict inequality $\Delta SQ < -MDC$. Drops of exactly $-5.000$ points must NOT trigger negative trajectory. Mixed boundaries (one drop of $-5.01$ and one drop of $-4.99$) must NOT trigger negative trajectory. Oscillations with large drops followed by immediate gains must NOT trigger negative trajectory.
- **Empirical Harness:** 105 edge-case trajectories:
  - 20 trajectories with consecutive drops of exactly $-5.0000000$.
  - 20 trajectories with consecutive drops of $-4.990$.
  - 20 trajectories with consecutive drops of $-5.010$.
  - 20 trajectories with mixed drops $[-5.010, -4.990]$ or $[-4.990, -5.010]$.
  - 25 trajectories with rapid oscillations ($\pm 15$ to $\pm 30$ SQ points per interval).
- **Empirical Results:**
  - Exact drops of $-5.000$: **40/40 PASSED** (Python & TS both evaluate `-5.000 < -5.0` as `False`, remaining stable).
  - Drops of $-4.990$: **40/40 PASSED** (stable).
  - Drops of $-5.010$: **40/40 PASSED** (deteriorating, negative trajectory).
  - Mixed boundaries $[-5.010, -4.990]$: **40/40 PASSED** (stable).
  - Oscillations $[-25, +25, -25, +25]$: **50/50 PASSED** (stable).

### 2.4 Suite D: Baseline Day 1 & Uncalibrated / Reliability Modeling
- **Normative Requirement (SPEC §10):**
  - Day 1 is tagged as baseline. Single observation at Day 1 must return `is_baseline = True`.
  - Fewer than 3 frames (fewer than 2 intervals) cannot assert trajectory slope and must return `status = "stable"`.
  - Theoretical MDC: $MDC = 1.96 \cdot \sqrt{2} \cdot SEM$, where $SEM = SD \cdot \sqrt{1 - r}$.
- **Empirical Harness:** 105 trajectories testing frame sequences $[1]$, $[7]$, $[1, 7]$, and variable reliability $r \in [0.70, 0.95]$.
- **Empirical Results:**
  - Day 1 single frame: **50/50 PASSED** (`is_baseline = True`, `deltas = []`, `status = "stable"`).
  - Day 7 single frame: **50/50 PASSED** (`is_baseline = False`).
  - Two frames $[1, 7]$ with 40-point drop: **50/50 PASSED** (`status = "stable"` due to $N < 3$).
  - Calibrated SEM/MDC: **60/60 PASSED** ($MDC$ correctly expands with higher measurement error, preventing false drift alarms).

---

## 3. Counterfactual Repair Empirical Findings & Failure Reproduction

### 3.1 Normative Specification for Counterfactual Repair (SPEC §10, §12)
Continuous counterfactual repair projects an assessment state $\mathbf{x} = (s_{h,1}, s_{h,2}, s_{h,3}, s_{h,4}, \text{Integrity}, \text{Reliability}, \text{Operator})$ into Mutualism:
$$\min_{\mathbf{x}'} \|\mathbf{x}' - \mathbf{x}\|_p \quad (p \in \{1, 2\})$$
Subject to:
1. $\mathbf{x}' \in [0, 1]^4 \times [-1, 1]^3$
2. $HNE(\mathbf{x}') > 0.20$
3. $SNE(\mathbf{x}') > 0.20$
4. $SQ(\mathbf{x}') > 20.0$
5. $\text{class}(\mathbf{x}') = \text{Mutualism}$

### 3.2 Empirical Test Execution
We generated 110 non-mutualistic states across all 8 non-mutualistic classes:
- *Commensalism* ($HNE > 0.2, SNE \in [-0.2, 0.2]$)
- *Sacrificial* ($HNE > 0.2, SNE < -0.2$)
- *Inverse Commensalism* ($HNE \in [-0.2, 0.2], SNE > 0.2$)
- *Neutralism* ($HNE \in [-0.2, 0.2], SNE \in [-0.2, 0.2]$)
- *Antagonism* ($HNE \in [-0.2, 0.2], SNE < -0.2$)
- *Parasitism* ($HNE < -0.2, SNE > 0.2$)
- *Amensalism* ($HNE < -0.2, SNE \in [-0.2, 0.2]$)
- *Mutual Harm* ($HNE < -0.2, SNE < -0.2$)
- Corner cases: all-zeros $(0, 0, 0, 0, -1, -1, -1)$, boundary thresholds ($HNE = 0.199, SNE = 0.201$), and stability perturbation $\sigma_C \in [0.0, 0.50]$.

Each state was evaluated under both $L_2$ and $L_1$ projections ($220$ total repairs per implementation). Each repaired state was re-evaluated through the complete, unmocked SQ and symbiosis pipeline.

### 3.3 Python Reference Implementation Behavior
In `packages/py/src/symnoesis/counterfactual.py`:
- Employs `scipy.optimize.minimize(method="SLSQP")` with explicit nonlinear inequality constraints:
  - `hne_constraint`: $HNE \ge 0.205$
  - `sne_constraint`: $SNE \ge 0.205$
  - `sq_constraint`: $SQ \ge 20.005$
- **Result:** **220 / 220 PASSED (100.0%)**.
- When stability dampening $S < 1.0$ is present, the optimizer automatically increases $HNE$ and/or $SNE$ above $0.205$ so that composite $C \cdot S_{eff} \ge 0.20005$, guaranteeing $SQ > 20.00$.

### 3.4 TypeScript Port Failure Reproduction
In `packages/ts/src/counterfactual.ts`:
- **Result:** **112 / 220 PASSED, 108 / 220 FAILED (Failure rate: 49.1%)**.
- **Root Cause Analysis:**
  The TypeScript implementation replaces nonlinear optimization with a decoupled closed-form projection:
  ```typescript
  // packages/ts/src/counterfactual.ts lines 431-497
  const targetThresh = cfg.classes.threshold + 0.005; // 0.205

  // Projects sum(s_h) so that HNE >= 0.205
  if (currentSumH < targetSumH) { ... }

  // Projects [integrity, reliability, operator] so that SNE >= 0.205
  if (currentSne < targetThresh) { ... }
  ```
  **Crucial omission:** It completely fails to account for stability dampening $S = 0.5 + 0.5(1 - \min(1, \sigma_C / \sigma_{max}))$.
  When $\sigma_C > 0$, $S < 1.0$.
  Since $HNE$ is projected to $0.205$ and $SNE$ is projected to $0.205$, the composite effect is $C \approx 0.205$.
  Then:
  $$SQ = 100 \cdot C \cdot S = 100 \cdot 0.205 \cdot S = 20.5 \cdot S < 20.0$$
  Consequently, for **every single non-mutualistic state where $\sigma_C > 0$**, TypeScript produces an invalid repaired state with $SQ < 20.0$!

#### Concrete Verbatim Failure Evidence from Test Logs:
```json
{
  "tag": "neutralism",
  "norm": "l2",
  "stability_std": 0.4,
  "repaired_hne": 0.205,
  "repaired_sne": 0.593,
  "repaired_sq": 19.284,
  "repaired_class": "mutualism"
}
```
*Requirement Violation:* $SQ = 19.284 < 20.000$.

```json
{
  "tag": "neutralism",
  "norm": "l2",
  "stability_std": 0.15,
  "repaired_hne": 0.205,
  "repaired_sne": 0.205,
  "repaired_sq": 17.430,
  "repaired_class": "mutualism"
}
```
*Requirement Violation:* $SQ = 17.430 < 20.000$.

```json
{
  "tag": "mutual_harm",
  "norm": "l2",
  "stability_std": 0.25,
  "repaired_hne": 0.205,
  "repaired_sne": 0.205,
  "repaired_sq": 16.400,
  "repaired_class": "mutualism"
}
```
*Requirement Violation:* $SQ = 16.400 < 20.000$.

Even worse: TypeScript's `repaired_class` falsely reports `"mutualism"` because `classifySymbiosis` only checks $\text{sign3}(HNE) = +$ and $\text{sign3}(SNE) = +$, while the state itself has $SQ$ well below the $20.0$ threshold!

---

## 4. Remediation Plan for Implementation Worker

To fix the TypeScript implementation and achieve parity with Python:
1. In `packages/ts/src/counterfactual.ts`:
   Calculate $S = computeStabilityFactor(state.stability_std ?? 0.0, cfg)$.
2. Calculate the required composite effect:
   $$C_{req} = \frac{20.005}{100.0 \cdot S}$$
   $$C_{target} = \max(targetThresh, C_{req})$$
3. When $C_{target} > targetThresh$ (i.e. whenever $S < \frac{20.005}{20.5} \approx 0.9758$), allocate additional headroom across $s_h$ and $(int, rel, op)$ proportionally or via projected gradient descent until:
   $$C = \frac{w_h HNE + w_s SNE}{w_h + w_s} \ge C_{target}$$
4. Re-run `node tests/test_challenger_m2_empirical_ts.mjs` and ensure all 220 evaluations pass with $SQ > 20.0$.
