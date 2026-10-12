# Milestone M2 Review & Adversarial Analysis Report

**Reviewer:** Reviewer 2 (`reviewer_m2_2`)  
**Role:** Reviewer & Adversarial Critic  
**Date:** 2026-10-12  
**Target:** Milestone M2 — Minimal Failure Cover (MFC) & Longitudinal Diagnostics (R2)  
**Implementation Modules:**  
- Python: `packages/py/src/symnoesis/cover.py`, `counterfactual.py`, `temporal.py`  
- TypeScript: `packages/ts/src/cover.ts`, `counterfactual.ts`, `temporal.ts`  

---

## 1. Executive Summary

Milestone M2 implements normative specifications from SPEC §9, §10, §11, and §12:
- Exact Minimal Failure Cover (MFC) optimization via HiGHS MILP (`scipy.optimize.milp` and TS branch-and-bound) over 3,488 subcubes with purity $\pi(R) \ge 0.80$ and coverage $\ge 0.85$.
- Quine-McCluskey strict-mode minimization matching `sympy.logic.boolalg.SOPform`.
- Single-flip counterfactual repair diagnostics with 37-feature RidgeBitModel fallback and continuous L1/L2 projections into Mutualism ($SQ > 20, HNE > 0.2, SNE > 0.2$).
- Longitudinal temporal engine across frames $[1, 7, 28, 84, 182]$ with Minimum Detectable Change ($MDC = 5.0$, $SEM = SD \cdot \sqrt{1 - r}$) requiring two consecutive intervals to classify deteriorating trajectories and trigger governance zone Z4 Drift.

**Verdict:** **APPROVE**  
No integrity violations, no facades, no hardcoded cheats, 0 skipped tests, 0 type errors under strict typing, and $\ge 95\%$ test coverage across all modules.

---

## 2. Gate Verification & Test Battery

All normative test and quality commands were executed directly and passed without errors:

| Command | Status | Details |
|---|---|---|
| `uv run --directory packages/py pytest --cov=src --cov-report=term-missing` | **PASS** | 73 passed in 12.14s; 98% overall line coverage; $\ge 95\%$ on every module |
| `uv run --directory packages/py mypy src tests` | **PASS** | 30 source files analyzed; 0 errors under `strict = true` |
| `uv run --directory packages/py ruff check .` | **PASS** | All lint rules passed |
| `uv run --directory packages/py ruff format --check .` | **PASS** | 31 files checked, 100% formatted |
| `pnpm -r run typecheck` | **PASS** | `tsc --noEmit` exited clean, 0 type errors |
| `pnpm -r run test` | **PASS** | 9 test files, 47 tests passed in Vitest |
| `uv run --directory packages/py python ../../tests/e2e/runner.py --all` | **PASS** | 299/299 tests passed across Tiers 1–4 in 2.64s |

### Core Module Coverage Breakdown (`packages/py`)

| Module | Statements | Missing | Coverage | Threshold Met ($\ge 95\%$) |
|---|---|---|---|---|
| `symnoesis/__init__.py` | 17 | 0 | 100% | YES |
| `symnoesis/assign.py` | 32 | 0 | 100% | YES |
| `symnoesis/classes.py` | 28 | 0 | 100% | YES |
| `symnoesis/config.py` | 152 | 5 | 97% | YES |
| `symnoesis/counterfactual.py` | 199 | 5 | 97% | YES |
| `symnoesis/cover.py` | 354 | 11 | 97% | YES |
| `symnoesis/evidence.py` | 14 | 0 | 100% | YES |
| `symnoesis/gates.py` | 19 | 0 | 100% | YES |
| `symnoesis/gray.py` | 29 | 0 | 100% | YES |
| `symnoesis/grid.py` | 61 | 0 | 100% | YES |
| `symnoesis/net_effects.py` | 38 | 2 | 95% | YES |
| `symnoesis/sq.py` | 34 | 0 | 100% | YES |
| `symnoesis/stability.py` | 17 | 0 | 100% | YES |
| `symnoesis/temporal.py` | 75 | 0 | 100% | YES |
| `symnoesis/variables.py` | 27 | 0 | 100% | YES |
| `symnoesis/zones.py` | 35 | 0 | 100% | YES |
| **TOTAL** | **1131** | **23** | **98%** | **YES** |

---

## 3. Adversarial Analysis & Boundary Examination

### 3.1 MILP Optimization Corner Cases

1. **Empty Harm Sets ($total\_harm\_mass = 0$):**
   - *Test:* All cells set to $SQ = 50.0, n_{eff} = 100.0$.
   - *Behavior:* `solve_mfc_milp` exits immediately with `solver_status = "zero_harm"`, `rules = []`, `covered_harm_mass = 0.0`, `total_coverage = 1.0`.
   - *Result:* Correct. Does not attempt to construct a degenerate MILP problem.

2. **Single Subcube Cluster:**
   - *Test:* 32 harmful cells generated from pattern $(1, 1, 1, 1, 1, *, *, *)$ with $SQ = -60.0$.
   - *Behavior:* Solver isolates exactly that 5-literal subcube `H1=1 AND H2=1 AND H3=1 AND H4=1 AND M1=1`, achieving coverage $\ge 0.85$ and purity $1.0$.
   - *Result:* Correct.

3. **Tie-Breaking Determinism:**
   - *Test:* Two symmetric clusters ($H1=0 \land H2=0$ vs $M1=0 \land M2=0$) with identical purity, coverage, and literal counts.
   - *Behavior:* Objective includes lexicographic tie-breaking term $1e-9 \cdot (j / N)$. Rules are sorted deterministically before formulation. Multiple executions yield identical rule selections.
   - *Result:* Correct.

4. **No Admissible Rules:**
   - *Test:* Cells with $n_{eff} = 10.0$ ($< n_{rule\_min} = 30.0$).
   - *Behavior:* Returns `solver_status = "no_admissible_rules"`, `rules = []`, `total_coverage = 0.0`.
   - *Result:* Correct.

### 3.2 Quine-McCluskey Strict-Mode Equivalence

Tested 12 Boolean minimization benchmark cases against `sympy.logic.boolalg.SOPform`:
- Singleton minterms: `[0]` on 3 variables $\to$ `~a & ~b & ~c`.
- Adjacencies: `[0, 1]` on 4 variables $\to$ `~a & ~b & ~c`.
- 4-corners: `[0, 2, 8, 10]` on 4 variables $\to$ `~b & ~d`.
- Don't-cares: `[0]` with DC `[1]` on 2 variables $\to$ `~a`.
- Full minterm sets: all 16 minterms $\to$ `"True"`.
- Empty sets: $\to$ `"False"`.
- Cyclic core: `[0, 4, 5, 7, 8, 11, 12, 15]`.

*Findings:*
- Exact truth-table match across all $2^4 = 16$ input configurations for each case.
- In all 12 cases, the literal count of the Quine-McCluskey engine was $\le$ SymPy SOPform literal count.
- Deterministic canonical formatting prevents permutation instability.

### 3.3 Longitudinal Temporal Boundaries

1. **Exact Boundary: $\Delta SQ = -5.000$ vs $-5.0001$:**
   - *Condition:* $MDC = 5.0$.
   - *Trajectory $[40.0, 35.0, 30.0]$:* Drops are exactly $-5.000$. Condition `deltas < -MDC` is strict inequality (`< -5.0`). Result: `status = "stable"`.
   - *Trajectory $[40.0, 34.9999, 29.9997]$:* Drops are $-5.0001$. Condition strictly met for two consecutive intervals. Result: `status = "deteriorating"`, `is_negative = True`.
   - *Result:* Boundary strictly obeys SPEC §10.

2. **Single Drop vs. Consecutive Intervals:**
   - *Trajectory $[50.0, 35.0, 36.0]$:* Single catastrophic drop of $-15.0$ followed by $+1.0$ recovery. Classified as `stable`.
   - *Trajectory $[50.0, 40.0, 41.0, 30.0]$:* Two drops of $-10.0$ and $-11.0$ separated by $+1.0$. Classified as `stable`.
   - *Result:* Strictly enforces the "two consecutive intervals" requirement.

3. **Sequence Length $< 3$:**
   - Sequence $[40.0, 20.0]$ carries only 1 interval. Returns `status = "stable"`, `is_negative = False`.
   - Day 1 single frame carries `is_baseline = True`.

4. **Theoretical SEM / MDC Formulas:**
   - Perfect reliability ($r = 1.0$) yields $SEM = 0.0$ and $MDC = 0.0$.
   - Zero reliability ($r = 0.0$) yields $SEM = SD$.
   - Verified $MDC = 1.96 \cdot \sqrt{2} \cdot SEM \approx 2.77185858 \cdot SEM$.

### 3.4 Counterfactual Projection Validity

Tested continuous L1 and L2 projections from diverse non-mutualistic starting points:
- Parasitism ($s_h = [0.1, 0.2, 0.15, 0.1], \text{system} = 0.8$)
- Amensalism ($s_h = [0.1, 0.1, 0.1, 0.1], \text{system} = 0.0$)
- Synnecrosis / Mutual Harm ($s_h = [0.05, 0.05, 0.05, 0.05], \text{system} = -0.8$)
- Sacrificial ($s_h = [0.9, 0.9, 0.9, 0.9], \text{system} = -0.9$)
- Neutralism ($s_h = [0.5, 0.5, 0.5, 0.5], \text{system} = 0.0$)

*Findings:*
- All repaired coordinates lie strictly within valid bounds ($s_h \in [0, 1]$, system variables in $[-1, 1]$).
- All repaired outcomes strictly satisfy Mutualism criteria: $HNE > 0.20$, $SNE > 0.20$, $SQ > 20.0$.
- Re-evaluation using `evaluate_continuous_state` matches the optimizer's reported values within $10^{-9}$.
- Associational framing invariant: Prohibited causal terms (`"caused by"`, `"cure"`, `"causal impact"`, `"fixes"`, `"remedies"`) are dynamically asserted and rejected.

---

## 4. Integrity and Anti-Cheating Audit

| Integrity Check | Observation | Verdict |
|---|---|---|
| Hardcoded test outputs in source code | No hardcoded outputs or lookup tables found in `cover.py`, `counterfactual.py`, or `temporal.py`. Real MILP/HiGHS solver, real Ridge normal equations, real SLSQP optimization. | **CLEAN** |
| Dummy or facade implementations | All functions contain complete mathematical logic and algorithmic execution paths. | **CLEAN** |
| Skipped or xfailed tests | Zero tests marked `@pytest.mark.skip` or `@pytest.mark.xfail`. | **CLEAN** |
| Suppressed type checks | Zero `# type: ignore` in `src/symnoesis/cover.py`, `counterfactual.py`, or `temporal.py`. Zero `@ts-ignore` in `packages/ts/src/`. | **CLEAN** |
| Non-causal language compliance | Prohibited causal terms list is checked programmatically; all generated diagnostic strings adhere to associational phrasing. | **CLEAN** |

---

## 5. Review Findings

### Positive Findings (Good Engineering Practices)
1. **Mathematical Fidelity:** Quine-McCluskey implementation in Python includes Petrick's branch-and-bound reduction for cyclic core matrices, outperforming or matching SymPy SOPform on every test case.
2. **Determinism:** The MILP formulation incorporates explicit secondary objective penalties ($1e-3 \cdot L(R)$ and $1e-9 \cdot j/N$) ensuring reproducible rule selection without relying on solver heuristics.
3. **TypeScript Parity:** TypeScript port (`@symnoesis/core`) contains identical subcube enumeration, branch-and-bound set cover, Gauss-Jordan normal equation solving for the 37-parameter RidgeBitModel, and trajectory classification.

### Gaps / Notes
- None affecting correctness or certification. All required features function as normatively specified.

---

## 6. Verdict

**APPROVE**  
Milestone M2 (Minimal Failure Cover & Longitudinal Diagnostics) meets all normative and engineering acceptance criteria.
