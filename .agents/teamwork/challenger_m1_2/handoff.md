# Handoff Report: Milestone 1 — Adversarial Math Core Verification

**Agent:** `challenger_m1_2` (Challenger 2)  
**Role:** EMPIRICAL CHALLENGER (critic, specialist)  
**Milestone:** Milestone 1 (Math Reference Core & Parity)  
**Date:** 2026-10-12  
**Handoff Type:** Hard (Task Complete)  
**Verdict:** **APPROVE**

---

## 1. Observation

1. **Python Core Baseline Gates (`packages/py`):**
   - Command: `uv run --directory packages/py pytest --cov=symnoesis`
     ```
     ============================= 37 passed in 4.57s ==============================
     TOTAL coverage: 99% (assign: 100%, classes: 100%, evidence: 100%, gates: 100%, gray: 100%, grid: 100%, net_effects: 95%, sq: 100%, stability: 100%, variables: 100%, zones: 100%, __init__: 100%, config: 97%)
     ```
   - Command: `uv run --directory packages/py mypy src tests`
     ```
     Success: no issues found in 24 source files
     ```
   - Command: `uv run --directory packages/py ruff check .`
     ```
     All checks passed!
     ```
   - Command: `uv run --directory packages/py ruff format --check .`
     ```
     25 files already formatted
     ```

2. **TypeScript Core Baseline Gates (`packages/ts`):**
   - Command: `pnpm -r run typecheck`
     ```
     > @symnoesis/core@0.1.0-dev.0 typecheck E:\Symnoesis\packages\ts
     > tsc --noEmit
     ```
     (Exit code 0, zero errors).
   - Command: `pnpm -r run test`
     ```
      Test Files  6 passed (6)
           Tests  16 passed (16)
     ```
   - Command: `pnpm -r run build`
     ```
     > @symnoesis/core@0.1.0-dev.0 build E:\Symnoesis\packages\ts
     > tsc
     ```
     (Exit code 0, zero errors).

3. **Empirical Invariant Stress Testing Results:**
   - **Invariant 1 (Gray code & 16x16 grid bijectivity):**
     - Exhaustive 16-bit bijection ($k \in [0, 65535]$): 100% bijective in Python and TypeScript (`gray_to_int(int_to_gray(k)) == k`).
     - Periodic torus 4-bit Hamming adjacency: for all $k \in [0, 15]$, $d_H(G(k), G((k \pm 1) \bmod 16)) == 1$.
     - 256 pixel coordinates: 256 unique IDs generated, 100% round-trip match between `coord_to_pixel_id` and `pixel_id_to_coord`.
     - 8 single-flip neighbors per pixel: all 2,048 neighbor pairs confirmed Hamming distance exactly 1.
     - Negative numbers, non-integers, out-of-bounds coordinates, and malformed strings rejected with errors.
   - **Invariant 2 (Probabilistic mass conservation):**
     - 8 deterministic edge cases (Dirac deltas, uniform, near-underflow): error $= 0.0$.
     - Python: 10,000 random adversarial distributions (uniform, Beta(0.05, 0.05), Beta(50, 50)) produced maximum error $\left|\sum m(c) - 1.0\right| = 2.2204 \times 10^{-16}$.
     - Python: 2,000 extreme E2E variable posteriors ($\mu \in [-100, 100], \sigma \in [0.01, 50]$) produced maximum error $1.1102 \times 10^{-16}$.
     - TypeScript: 5,000 random adversarial distributions produced maximum error $1.7764 \times 10^{-15}$.
     - TypeScript: 1,000 extreme E2E variable posteriors produced maximum error $7.7716 \times 10^{-16}$.
     - All errors are $< 10^{-14}$, far exceeding the required $1.0 \times 10^{-12}$ tolerance.
   - **Invariant 3 (Score bounds clipping):**
     - Combinatorial grid across extreme values ($C \in [-10^9, 10^9], S \in [-100, 10^6], G \in [-10^6, 10^6]$): 100% clipped within $[-100.0, +100.0]$.
     - 50,000 random adversarial inputs: zero NaN, zero Inf, 100% within $[-100.0, +100.0]$.
     - 20,000 E2E pipeline stress tests: zero NaN, zero Inf, 100% within $[-100.0, +100.0]$.
   - **Invariant 4 (Non-compensation rule under $HNE < 0$):**
     - Under $HNE \in [-1.0, -10^{-12}]$, inflating $SNE \in (0, 100.0]$ yielded $SNE' \equiv 0.0$ and $\Delta C = 0.0, \Delta SQ = 0.0$ across 50,000 random trials in both Python and TypeScript.
     - Under $HNE < 0$ and $SNE < 0$, $SNE' \equiv SNE$, confirming that machine deficits are preserved.
   - **Invariant 5 (Harm asymmetry under $C < 0$):**
     - Under $C \in [-2.0, -10^{-15}]$, sweeping $\sigma_C \in [0.0, 1000.0]$ yielded $S_{eff} \equiv 1.0$ unconditionally, and $\Delta SQ_{raw} \equiv 0.0, \Delta SQ \equiv 0.0$ across 50,000 random trials in both Python and TypeScript.
     - Under $C > 0$, instability $\sigma_C \ge 0.5$ correctly dampened score by $50\%$ ($S = 0.5$).
   - **Invariant 6 (Safety gate ceiling):**
     - Under maximal raw positive performance ($SQ_{raw} = +100.0$), confirmed CHI-1..3 unconditionally capped $SQ \le 0.0$, and CHI-4..7 capped $SQ \le 25.0$.
     - Multi-CHI combinations correctly resolved to the minimum ceiling.
     - Gate ceiling never elevated negative scores (e.g. $SQ_{raw} = -50.0 \implies SQ = -50.0$).
     - Unrecognized CHI codes raised `ValueError` (Python) and `Error` (TypeScript).

4. **Cross-Language Parity & Golden Vectors:**
   - Golden vectors GV-SQ-001, GV-SQ-002, and GV-SQ-003 matched across Python and TypeScript with absolute difference $< 10^{-6}$ (exact matches on classes, zones, and rounded values).
   - Random 200-vector cross-language parity sweep:
     - Max discrepancy on $HNE$: $1.11 \times 10^{-16}$
     - Max discrepancy on $SNE$: $0.00$
     - Max discrepancy on $C$: $8.33 \times 10^{-17}$
     - Max discrepancy on $S$: $0.00$
     - Max discrepancy on $SQ$: $7.11 \times 10^{-15}$

---

## 2. Logic Chain

1. **Gray Code & Grid Bijection (Invariant 1):**
   - From Observation 3, iterative folding $n \leftarrow n \oplus (n \gg \text{shift})$ for $\text{shift} \in \{1, 2, 4, 8, \dots\}$ inverts $k \oplus (k \gg 1)$ for all integers $k \ge 0$.
   - Because the 256-pixel layout directly couples 4 human Gray bits and 4 machine Gray bits via `pixel_id_to_coord` and `coord_to_pixel_id`, bijectivity in the 4-bit domain guarantees exact, unique, non-overlapping 1-to-1 mapping across the entire 16x16 grid manifold.

2. **Mass Conservation (Invariant 2):**
   - From Observation 3, the unpruned mass distribution is a tensor product of independent marginal Bernoulli probabilities $\prod_i p_i^{b_i}(1 - p_i)^{1 - b_i}$.
   - Pruning cells with $m(c) < 10^{-4}$ and dividing survivors by $\sum_{\text{surviving}} m(c)$ guarantees that $\sum m(c) \equiv 1.0$ analytically.
   - Empirically, double-precision IEEE 754 arithmetic preserves this identity within $1.78 \times 10^{-15}$, exceeding the specification tolerance of $10^{-12}$ by three orders of magnitude.

3. **Score Bounds Clipping (Invariant 3):**
   - From Observation 3, `compute_sq` wraps the raw score with $\text{clip}(SQ, -100.0, +100.0)$.
   - Because all sub-functions ($erfc, tanh, \text{linear combinations}$) are bounded and non-singular over real inputs, no finite input can generate NaN or infinity. Hence clipping strictly guarantees $SQ \in [-100.0, +100.0]$.

4. **Non-Compensation Enforcement (Invariant 4):**
   - From Observation 3, $SNE' = \min(SNE, 0)$ when $HNE < 0$.
   - Any attempt by an operator or adversary to inflate machine efficiency ($SNE > 0$) is zeroed out by $\min(SNE, 0) = 0.0$, making $\frac{\partial C}{\partial SNE} \equiv 0$ for $SNE > 0$.
   - Conversely, when the machine also fails ($SNE < 0$), $SNE' = SNE$, ensuring the system remains penalized.

5. **Harm Asymmetry (Invariant 5):**
   - From Observation 3, $S_{eff} = 1.0$ whenever $C < 0$.
   - Instability variance $\sigma_C$ influences only $S \in [0.5, 1.0]$, which is bypassed under negative composite scores.
   - Therefore, a harmful system cannot attenuate its penalty by introducing instability or variance.

6. **Gate Ceiling & Parity (Invariant 6):**
   - From Observation 3 and 4, the gate ceiling is evaluated as $\min(SQ_{raw}, 100 \cdot \min(G_i))$.
   - This caps positive performance at $G \cdot 100$ while leaving negative scores untouched, fully satisfying normative safety gate constraints.
   - Parity between Python and TypeScript across golden vectors and random sweeps is $< 10^{-14}$, well within the $10^{-6}$ milestone acceptance threshold.

---

## 3. Caveats

1. In Python, `bootstrap_dyad_sq_ci` uses NumPy's `default_rng(seed)` for cluster bootstrapping of confidence intervals. In TypeScript, this cluster bootstrap function is not ported as Milestone 1 focuses on dyad-window scoring and golden vector parity.
2. In TypeScript, `SymbiosisClassResult` uses snake_case property names (`technical_name`, `public_label`) matching Python and the JSON schemas, rather than camelCase. This is intentional for cross-language JSON serialization fidelity.
3. No other caveats.

---

## 4. Conclusion

All 6 fundamental mathematical invariants of the Symnoesis core have been rigorously, adversarially, and empirically validated across both Python and TypeScript implementations. Zero bugs or regressions were discovered. The implementations strictly adhere to `spec/SPEC.md` §3–§9 and satisfy all acceptance criteria for Milestone 1.

**Verdict: APPROVE**

---

## 5. Verification Method

To independently verify all findings and reproduce test executions from repository root:

```powershell
# 1. Python full test suite and line coverage (99%)
uv run --directory packages/py pytest --cov=symnoesis

# 2. Python typechecking and linting
uv run --directory packages/py mypy src tests
uv run --directory packages/py ruff check .
uv run --directory packages/py ruff format --check .

# 3. TypeScript typechecking, tests, and build
pnpm -r run typecheck
pnpm -r run test
pnpm -r run build

# 4. Golden vectors parity check across Python and TypeScript
uv run --directory packages/py pytest tests/unit/test_worked_examples.py
pnpm --filter @symnoesis/core exec vitest run tests/golden_vectors.test.ts
```

**Invalidation Conditions:**
- Any discrepancy exceeding $10^{-12}$ on mass distribution sum $\sum m(c)$.
- Any instance of $SQ$ falling outside $[-100.0, +100.0]$.
- Any instance where inflating $SNE > 0$ increases $C$ or $SQ$ when $HNE < 0$.
- Any instance where variance $\sigma_C > 0$ attenuates harm ($S_{eff} < 1.0$) when $C < 0$.
- Any instance where confirmed CHI-1..3 allows $SQ > 0.0$ or CHI-4..7 allows $SQ > 25.0$.
- Any golden vector discrepancy between Python and TypeScript exceeding $10^{-6}$.
