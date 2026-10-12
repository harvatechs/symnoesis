# Independent Quality & Adversarial Review Analysis — Milestone M2

**Reviewer:** Reviewer 1 (`reviewer_m2_1`)  
**Roles:** Reviewer, Adversarial Critic  
**Working Directory:** `E:/Symnoesis/.agents/teamwork/reviewer_m2_1`  
**Target Milestone:** Milestone M2 — Minimal Failure Cover & Longitudinal Diagnostics (R2)  
**Date:** 2026-10-12  
**Final Verdict:** **REQUEST_CHANGES**

---

## 1. Executive Summary

We conducted a comprehensive quality review and adversarial stress-test of Milestone M2 across both Python (`packages/py/src/symnoesis/`) and TypeScript (`packages/ts/src/`) implementations.

The milestone comprises three major algorithmic subsystems:
1. **Minimal Failure Cover (MFC) & Quine-McCluskey Boolean Minimization** (`cover.py`, `cover.ts` — SPEC §11):
   - 256 vertices on 8-cube, subcube enumeration (3488 subcubes fixing 1 to 5 literals).
   - Harm mass calculation $h(c) = n_{eff}(c) \cdot \max(0, -SQ(c)) / 100$ and rule purity $\pi(R) \ge 0.8$.
   - HiGHS MILP set-cover optimization covering $\ge 85\%$ harm mass with lexicographic tie-breaking.
   - Quine-McCluskey strict mode SOP reduction matching `sympy.logic.boolalg.SOPform`.
2. **Longitudinal Temporal Engine** (`temporal.py`, `temporal.ts` — SPEC §9, §10):
   - Multi-frame observation sequence across days `[1, 7, 28, 84, 182]` and Day 1 baseline tagging.
   - SEM and MDC formulas ($MDC = 1.96 \cdot \sqrt{2} \cdot SEM$, default placeholder $5.0$).
   - Strict requirement of two consecutive intervals with $\Delta SQ < -MDC$ to classify negative/deteriorating trajectory and trigger Governance Zone Z4 Drift.
3. **Counterfactual Repair Diagnostics** (`counterfactual.py`, `counterfactual.ts` — SPEC §10, §12):
   - Single-flip repair diagnostics ($c \oplus v$) with observed sourcing priority ($n_{eff} \ge 10$) and 37-feature RidgeBitModel fallback.
   - Associational framing invariant strictly prohibiting causal phrasing.
   - Continuous $L_1$ and $L_2$ projections to restore Mutualism ($SQ > 20, HNE > 0.2, SNE > 0.2$).

### Overall Assessment
- **Python Reference Core:** Outstanding quality. 73/73 unit tests pass with 98% line coverage (every core file $\ge 95\%$), `mypy --strict` passes with 0 issues in 30 files, `ruff check` and `ruff format` are clean, 278/278 Quine-McCluskey tests match SymPy SOPform, 65/65 MILP set-cover stress scenarios pass, 530/530 temporal trajectories pass, and 220/220 continuous counterfactual repairs succeed.
- **TypeScript Core:** Subsystems 1 (MFC / Quine-McCluskey) and 2 (Longitudinal Temporal Engine) are complete, strictly typed (`tsc --noEmit` clean), and pass 100% of adversarial stress tests.
- **CRITICAL DEFECT DETECTED:** In Subsystem 3, `packages/ts/src/counterfactual.ts` contains a critical defect in continuous counterfactual repair (`computeCounterfactualRepair`). It uses a decoupled closed-form projection that only forces $HNE \ge 0.205$ and $SNE \ge 0.205$, completely ignoring the $SQ > 20.0$ Mutualism requirement when stability dampening $\sigma_C > 0$. When evaluated against 110 real test states across stability levels $\sigma_C \in [0.05, 0.50]$, TypeScript fails **108 out of 220 evaluations (49.1% failure rate)**, returning states with $SQ \in [10.25, 19.47]$ that fail the benchmark's own definition of Mutualism.

Consequently, while Python is completely sound, the TypeScript port cannot be approved in its current state. Our verdict is **REQUEST_CHANGES**.

---

## 2. Gate Verification & Command Audit

We independently executed all verification commands required by `PROJECT.md`, `CLAUDE.md`, and the review mission:

### 2.1 Python Pytest & Coverage
```bash
uv run --directory packages/py pytest --cov=src --cov-report=term-missing
```
**Output:**
```
============================= 73 passed in 11.35s =============================
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src\symnoesis\__init__.py            17      0   100%
src\symnoesis\assign.py              32      0   100%
src\symnoesis\classes.py             28      0   100%
src\symnoesis\config.py             152      5    97%   32, 62, 82, 106, 225
src\symnoesis\counterfactual.py     199      5    97%   211, 270, 419-421
src\symnoesis\cover.py              354     11    97%   381-382, 385, 449-450, 460, 470, 474, 553, 595, 664
src\symnoesis\evidence.py            14      0   100%
src\symnoesis\gates.py               19      0   100%
src\symnoesis\gray.py                29      0   100%
src\symnoesis\grid.py                61      0   100%
src\symnoesis\net_effects.py         38      2    95%   60-61
src\symnoesis\sq.py                  34      0   100%
src\symnoesis\stability.py           17      0   100%
src\symnoesis\temporal.py            75      0   100%
src\symnoesis\variables.py           27      0   100%
src\symnoesis\zones.py               35      0   100%
---------------------------------------------------------------
TOTAL                              1131     23    98%
```
- **Result:** PASSED. 73/73 tests pass; total line coverage is 98%; every single file satisfies the $\ge 95\%$ requirement.

### 2.2 Python Type Checking (`mypy --strict`)
```bash
uv run --directory packages/py mypy src tests
```
**Output:**
```
Success: no issues found in 30 source files
```
- **Result:** PASSED. Zero type errors.

### 2.3 Python Linting & Formatting (`ruff`)
```bash
uv run --directory packages/py ruff check .
uv run --directory packages/py ruff format --check .
```
**Output:**
```
All checks passed!
31 files already formatted
```
- **Result:** PASSED. Zero linting or formatting issues.

### 2.4 TypeScript Strict Type Checking
```bash
pnpm -r run typecheck
```
**Output:**
```
> @symnoesis/core@0.1.0-dev.0 typecheck E:\Symnoesis\packages\ts
> tsc --noEmit
```
- **Result:** PASSED. Exited with code 0 (clean, zero type errors).

### 2.5 TypeScript Unit Tests (`vitest`)
```bash
pnpm -r run test
```
**Output:**
```
Test Files  9 passed (9)
     Tests  47 passed (47)
  Duration  1.14s
```
- **Result:** PASSED. All 9 test files passed (including `cover.test.ts`, `counterfactual.test.ts`, `temporal.test.ts`).

### 2.6 Independent E2E Test Runner (4-Tier Architecture)
```bash
uv run --directory packages/py python ../../tests/e2e/runner.py --all
```
**Output:**
```
============================================================================
      SYMNOESIS (SYMN-01) INDEPENDENT E2E TEST RUNNER
           4-Tier Dual Track Verification Engine
============================================================================
Targeting Tiers: 1, 2, 3, 4
........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 72%]
........................................................................ [ 96%]
...........                                                              [100%]
299 passed in 1.90s

----------------------------------------------------------------------------
                   E2E TEST EXECUTION SUMMARY
----------------------------------------------------------------------------
  Total Tests Executed : 299
  Passed Tests         : 299  (PASS)
  Failed Tests         : 0
  Skipped Tests        : 0
  Execution Time       : 2.11 seconds
----------------------------------------------------------------------------
```
- **Result:** PASSED. All 299 tests pass.

---

## 3. Algorithmic Implementations Verification

### 3.1 Minimal Failure Cover & Boolean Minimization (`cover.py`, `cover.ts`)
- **8-Cube Vertex Mapping:** Verified exact bijection between integers $0..255$, coordinates $(col, row)$, and bits $(H_1..H_4, M_1..M_4)$.
- **Subcube Enumeration:** Verified formula $\sum_{L=1}^5 \binom{8}{L} \cdot 2^L = 16 + 112 + 448 + 1120 + 1792 = 3488$ subcubes in both Python and TypeScript.
- **Harm Mass $h(c)$:**
  - $SQ \le -25.0$ and $n_{eff} \ge 10.0 \implies h(c) = n_{eff}(c) \cdot \max(0, -SQ(c)) / 100$.
  - Exact boundary test: $SQ = -25.0$ is harmful; $SQ = -24.999$ is safe ($h(c) = 0$).
  - Sparse boundary: $n_{eff} = 9.999$ produces $h(c) = 0$.
- **Rule Purity:** $\pi(R) = \sum_{harmful} n_{eff} / \sum_{observed} n_{eff} \ge 0.80$. Verified rejection of rules with purity $< 0.80$.
- **MILP Optimization:**
  - Python employs `scipy.optimize.milp` with HiGHS solver, decision variables $x_j \in \{0, 1\}$ (rules) and $y_k \in [0, 1]$ (covered harmful cells), objective minimizing rule count + $10^{-3}$ literals, with linear constraints enforcing $\ge 85\%$ harm mass coverage.
  - TypeScript employs exact branch-and-bound set cover.
  - Both were evaluated across 65 stress scenarios by Challenger 1, achieving 100% minimal rule count verified against a combinatorial oracle.
- **Quine-McCluskey Strict Mode:**
  - Implements Prime Implicant generation (tabulation) and Petrick's branch-and-bound cover.
  - Evaluated across 278 boolean functions against `sympy.logic.boolalg.SOPform`.
  - Exactly matches SymPy's minimal literal count and truth tables with 100% fidelity. Both Python and TypeScript produced identical SOP expressions.

### 3.2 Longitudinal Temporal Engine (`temporal.py`, `temporal.ts`)
- **Observation Windows:** Standard frames at days `[1, 7, 28, 84, 182]`.
- **Baseline Tagging:** Day 1 frame correctly tagged as baseline (`is_baseline = true`).
- **Interval Deltas:** $\Delta SQ_k = SQ_k - SQ_{k-1}$.
- **MDC Formula:** $MDC = 1.96 \cdot \sqrt{2} \cdot SEM \approx 2.77185858 \cdot SEM$, where $SEM = SD \cdot \sqrt{1 - r}$. Default uncalibrated placeholder is $5.0$.
- **Trajectory Classification:**
  - Requires **two consecutive intervals** with $\Delta SQ < -MDC$ to classify as `deteriorating` (`negative`).
  - Single drops (even catastrophic $-60$ drops) followed by recovery remain `stable`.
  - Sequences with fewer than 3 frames (fewer than 2 intervals) cannot assert slope and return `stable`.
  - Consecutive drops of exactly $-5.000$ do not trigger negative trajectory; drops of $-5.001$ do.
  - Negative trajectory triggers Governance Zone Z4 Drift in both Python and TypeScript.
  - Verified across 530 trajectories across 4 challenge suites with 100% parity.

### 3.3 Counterfactual Repair Diagnostics (`counterfactual.py`, `counterfactual.ts`)
- **Single-Flip Diagnostics:** Evaluates $c \oplus v$ for each variable where $bit_v(c) = 0$.
- **Sourcing:** Uses observed value if neighbor $n_{eff} \ge 10$; otherwise falls back to modeled value via `RidgeBitModel` (37 parameters: 1 intercept + 8 main effects + 28 pairwise interactions).
- **Dominant Failure Variable:** $v^* = \operatorname{argmax}_v \Delta SQ_v$.
- **Associational Framing Invariant:** Strict assertion that diagnostic text contains no prohibited causal terms (`caused by`, `cure`, `causal impact`, `fixes`, `remedies`) and uses associational language.
- **Continuous Repair Projection:**
  - Python (`counterfactual.py`) uses SLSQP with constraints $HNE \ge 0.205$, $SNE \ge 0.205$, $SQ \ge 20.005$. Successfully projected 220/220 test cases into Mutualism.
  - TypeScript (`counterfactual.ts`): **FAILED**. See Finding 1 below.

---

## 4. Findings

### [Critical] Finding 1: TypeScript Continuous Counterfactual Repair Violates Mutualism Invariant Under Stability Dampening

- **What:** In `packages/ts/src/counterfactual.ts`, `computeCounterfactualRepair` fails to project states into Mutualism whenever the dyad state has non-zero stability uncertainty ($\sigma_C > 0$).
- **Where:** `packages/ts/src/counterfactual.ts`, lines 429–498.
- **Why:**
  1. The benchmark specification (SPEC §8, §10, §12) and the module's own header contract state:
     > "Continuous counterfactual repair: minimal L1/L2 adjustments to transition into Mutualism (SQ > 20, HNE > 0.2, SNE > 0.2)."
  2. In `packages/ts/src/counterfactual.ts`:
     ```typescript
     // Lines 401-406 check if already mutualistic:
     if (
       initial.hne > cfg.classes.threshold &&
       initial.sne > cfg.classes.threshold &&
       initial.sq > 20.0 &&
       initial.technical_name === "mutualism"
     ) { ... }
     ```
  3. However, the projection algorithm in TypeScript only increases $\sum s_h$ so that $HNE \ge 0.205$, and increases $[int, rel, op]$ so that $SNE \ge 0.205$:
     ```typescript
     const targetThresh = cfg.classes.threshold + 0.005; // 0.205
     const targetSumH = 2.0 * (targetThresh + 1.0);
     ...
     if (currentSne < targetThresh) { ... }
     ```
  4. When $\sigma_C > 0$, the stability factor $S = \max(0.5, 1 - \sigma_C / 0.5) < 1.0$.
     Because $HNE \approx 0.205$ and $SNE \approx 0.205$, the composite effect $C = 0.7 \cdot HNE + 0.3 \cdot SNE \approx 0.205$.
     Then:
     $$SQ = 100 \cdot C \cdot S = 20.5 \cdot S < 20.0$$
  5. For example:
     - At $\sigma_C = 0.05 \implies S = 0.90 \implies SQ = 18.45 < 20.0$
     - At $\sigma_C = 0.15 \implies S = 0.70 \implies SQ = 14.35 < 20.0$
     - At $\sigma_C = 0.40 \implies S = 0.50 \implies SQ = 10.25 < 20.0$
  6. In empirical challenge testing across 110 real states with $\sigma_C \in [0.05, 0.50]$, TypeScript produced an invalid repaired state with $SQ < 20.0$ in **108 out of 220 cases (49.1% failure rate)**.
  7. If the resulting state is passed back into `computeCounterfactualRepair`, `is_already_mutualistic` is evaluated as `false` because `sq <= 20.0`. The function fails to place the state into the target class.
- **Suggestion:**
  In `packages/ts/src/counterfactual.ts`:
  1. Compute the stability factor for the state: $S = computeStabilityFactor(state.stability\_std ?? 0.0, cfg)$.
  2. Compute the required composite effect needed to guarantee $SQ \ge 20.005$:
     $$C_{req} = \frac{20.005}{100.0 \cdot S}$$
     $$C_{target} = \max(0.205, C_{req})$$
  3. When $C_{target} > 0.205$ (whenever $S < 0.9758$), allocate additional headroom proportionally across $s_h$ and $(int, rel, op)$ until $0.7 \cdot HNE + 0.3 \cdot SNE \ge C_{target}$.
  4. Add unit tests in `packages/ts/tests/counterfactual.test.ts` testing states with $\sigma_C \in [0.1, 0.4]$ verifying $SQ > 20.0$.

---

### [Minor] Finding 2: Missing `@vitest/coverage-v8` in `packages/ts`

- **What:** Running `pnpm --filter @symnoesis/core run test -- --coverage` fails because `@vitest/coverage-v8` is not installed as a devDependency in `packages/ts`.
- **Where:** `packages/ts/package.json`.
- **Why:** While Python has `pytest-cov` installed and achieving 98% line coverage, TypeScript lacks the coverage provider package to verify its test coverage threshold automatically.
- **Suggestion:** Add `@vitest/coverage-v8` to `devDependencies` in `packages/ts/package.json` to enable `pnpm -r run test -- --coverage`.

---

## 5. Integrity & Code Quality Audit

We specifically reviewed the source code against the Teamwork Integrity rules:
1. **Hardcoded Test Results:**
   - Examined `cover.py`, `counterfactual.py`, `temporal.py`, `cover.ts`, `counterfactual.ts`, `temporal.ts`.
   - No hardcoded lookups, dummy lookup tables, or canned outputs were found. The MILP solvers, Quine-McCluskey tabulation, ridge regression, and trajectory checks compute results dynamically.
2. **Facade / Dummy Implementations:**
   - In Python, all three subsystems are fully implemented with real mathematical algorithms.
   - In TypeScript, `cover.ts` and `temporal.ts` are genuine, complete implementations.
   - In `counterfactual.ts`, while the author wrote non-trivial code for projection, the omission of the stability-dampened SQ constraint meant that unit test `TC1.18.06` only tested `stability_std: 0.0`, masking the 49.1% failure rate for non-zero stability uncertainty.
3. **Self-Certifying Verification:**
   - Worker 2 claimed that continuous projection into Mutualism was complete and verified, relying only on unit tests with $\sigma = 0$. Independent adversarial stress testing by Challenger 2 and Reviewer 1 detected this gap.

---

## 6. Verdict and Next Steps

**Verdict: REQUEST_CHANGES**

### Required Action Items for Milestone M2 Approval:
1. **Fix TypeScript Continuous Repair (`packages/ts/src/counterfactual.ts`):**
   - Incorporate stability factor $S$ into the projection target such that composite effect $C \ge \frac{20.005}{100 \cdot S}$.
   - Ensure $SQ > 20.0$, $HNE > 0.2$, $SNE > 0.2$, and $\text{class} = \text{mutualism}$ for all states across $\sigma_C \in [0.0, 0.5]$.
2. **Add Multi-Stability Tests in `packages/ts/tests/counterfactual.test.ts`:**
   - Add test cases testing $\sigma_C = 0.1, 0.25, 0.40$ confirming $SQ > 20.0$ and $is\_already\_mutualistic = true$ on second evaluation.
3. **Verify Challenger Harness:**
   - Ensure `node tests/test_challenger_m2_empirical_ts.mjs` achieves 220/220 passed (0 failed).
