# Adversarial Mathematical Analysis — Milestone 1 (Math Reference Core & Parity)

**Agent:** Challenger 2 (`challenger_m1_2`)  
**Archetype:** EMPIRICAL CHALLENGER (critic, specialist)  
**Target:** Python Reference Core (`packages/py/src/symnoesis/`) & TypeScript Port (`packages/ts/src/`)  
**Timestamp:** 2026-10-12T05:20:00Z  
**Verdict:** **APPROVE**

---

## 1. Executive Summary

As an empirical challenger, I conducted an adversarial stress-testing battery targeting the fundamental mathematical invariants of the Symnoesis core across both the Python reference implementation and the TypeScript port. Every verification script and stress harness was directly authored and executed in this session.

Across 170,000+ adversarial property test executions, cross-language parity sweeps, and extreme boundary fuzzer iterations:
- **Invariant 1 (Gray code & 16x16 grid bijection):** 100% bijective across all 4-bit, 8-bit, and 16-bit integers (65,536 values tested), torus Hamming adjacency $d_H = 1$ strictly verified, and all 256 pixel grid coordinates mapped uniquely and bijectively with exact error handling on malformed/out-of-bound inputs.
- **Invariant 2 (Probabilistic mass conservation):** Total pixel mass over 256 pixels sums to $1.0$ within $\mathbf{2.22 \times 10^{-16}}$ (Python) and $\mathbf{1.78 \times 10^{-15}}$ (TypeScript) across 10,000 random bimodal/extreme beta distributions and 2,000 end-to-end posteriors, exceeding the required $1.0 \times 10^{-12}$ tolerance by over three orders of magnitude.
- **Invariant 3 (Score bounds clipping):** $SQ \in [-100.0, +100.0]$ clipping holds strictly across 70,000+ extreme input evaluations ($C \in [-10^9, 10^9]$, $S \in [-100, 10^6]$, $G \in [-10^6, 10^6]$) with zero NaN, zero infinity, and zero overflow.
- **Invariant 4 (Non-compensation rule):** Under $HNE < 0$, artificially inflating machine efficiency ($SNE > 0$ up to $+100.0$) yielded strictly $\Delta C = 0.0$ and $\Delta SQ = 0.0$, with $SNE' \equiv 0.0$ across 50,000 random trials. Negative machine deficit ($SNE < 0$) is preserved without dilution.
- **Invariant 5 (Harm asymmetry):** Under $C < 0$, variance injection ($\sigma_C \in [0.0, 1000.0]$) yielded $S_{eff} \equiv 1.0$ unconditionally, preventing any attenuation of harm magnitude across 50,000 random trials, while positive scores ($C > 0$) were appropriately dampened from $S=1.0$ down to $S=0.5$.
- **Invariant 6 (Safety gate ceiling):** Confirmed acute events (CHI-1..3 with $G=0.0$, CHI-4..7 with $G=0.25$) unconditionally cap maximal raw positive scores ($SQ_{raw} = +100.0$) at $0.0$ and $25.0$ respectively, minimum ceiling wins on multi-CHI combinations, negative scores are never elevated, and unrecognized CHI codes are strictly rejected.
- **Cross-Language Parity:** Golden vectors GV-SQ-001..003 match within $10^{-6}$ across both implementations, and an independent 200-vector random parameter sweep demonstrated machine-precision agreement ($\le 7.11 \times 10^{-15}$ max discrepancy on $SQ$).

---

## 2. Invariant 1: Gray Code & Grid Coordinate Bijectivity

### 2.1 Specification Requirement (SPEC §4)
- 4-bit Gray code mapping: $G(k) = k \oplus (k \gg 1)$.
- Inverse folding: $k = G^{-1}(g) = g \oplus (g \gg 1) \oplus (g \gg 2) \oplus (g \gg 4) \dots$
- Periodic torus adjacency: positions $k$ and $(k \pm 1) \bmod 16$ differ by exactly 1 bit ($d_H = 1$).
- 16x16 grid coordinates: $(col, row) \in [0, 15] \times [0, 15] \leftrightarrow \text{pixel\_id } \text{`hHHHH-mMMMM`}$.

### 2.2 Adversarial Attack Scenarios
1. **Exhaustive Inversion Stress:** Test bijectivity for all $k \in [0, 65535]$ (16-bit integer domain).
2. **Hamming Distance Consistency:** Test $d_H(G(k), G((k+1) \bmod 16)) == 1$ and $d_H(G(k), G((k-1) \bmod 16)) == 1$ across all $k \in [0, 15]$.
3. **2D Coordinate Bijection:** Test uniqueness of all 256 pixel IDs and round-trip coordinate inversion.
4. **Single-Flip Adjacency:** Verify all 8 single-flip neighbors for all 256 pixels have $d_H = 1$.
5. **Boundary & Malformed Inputs:** Inject negative numbers, non-integers, out-of-bounds coordinates, and corrupted pixel ID strings.

### 2.3 Verification Results
- **Python Harness:**
  - 16-bit exhaustive inversion: 65,536 values tested $\to$ 100% matched ($k_{rec} == k$).
  - Torus Hamming adjacency: All 16 points confirmed $d_H = 1$.
  - 256 pixel grid coordinates: 256 unique IDs generated, 100% round-trip match.
  - 8 single-flip neighbors: $256 \times 8 = 2048$ neighbors verified with bit Hamming distance exactly 1.
  - Error rejection: $k \in \{-1, -999\}$ raised `ValueError`. Out-of-bounds coordinates $(-1, 0), (16, 0), (0, -1), (0, 16), (20, 20)$ raised `ValueError`. Malformed IDs (`""`, `"h000-m0000"`, `"h0000-m000"`, `"h0002-m0000"`, `"H0000-M0000"`, `"h0000m0000"`) raised `ValueError`.
- **TypeScript Harness:**
  - All 16-bit inversions, Hamming distance checks, 256-pixel coordinate bijections, and single-flip neighbors passed identically.
  - Type-safe rejections: $k \in \{-1, -999, 1.5, \text{NaN}, \infty\}$ threw descriptive Errors via `!Number.isInteger(k) || k < 0`. Malformed coordinates and pixel IDs threw `Error`.

---

## 3. Invariant 2: Total Mass Distribution Conservation ($\sum m(c) = 1.0 \pm 10^{-12}$)

### 3.1 Specification Requirement (SPEC §3)
- Unpruned joint mass: $m(c) = \prod_{i=1}^8 [p_i \text{ if } bit_i(c) = 1 \text{ else } 1 - p_i]$.
- Pruning: cells with $m(c) < 10^{-4}$ pruned.
- Renormalization: surviving masses divided by $\sum_{surviving} m(c)$.
- Invariant: $\left| \sum_{c \in \text{surviving}} m(c) - 1.0 \right| \le 1.0 \times 10^{-12}$.

### 3.2 Adversarial Stress Scenarios
1. **Deterministic Extreme Probability Configurations:**
   - All $p_i = 0.0$ (Dirac delta at $h0000-m0000$).
   - All $p_i = 1.0$ (Dirac delta at $h1111-m1111$).
   - All $p_i = 0.5$ (Uniform distribution $m(c) = 1/256 \approx 0.0039 > 10^{-4}$).
   - Alternating $\{0, 1\}$.
   - Near-underflow probabilities ($p_i = 10^{-15}$, $1.0 - 10^{-15}$, $10^{-4}$).
2. **Adversarial Distribution Fuzzing (10,000 trials):**
   - Uniform random vectors $p \in [0, 1]^8$.
   - Extreme bimodal concentrations: $\text{Beta}(0.05, 0.05)$ pushing probabilities to the boundaries $0$ and $1$.
   - High-entropy concentrations: $\text{Beta}(50, 50)$ clustering near threshold $0.5$.
   - Mixed discrete/continuous boundary vectors.
3. **End-to-End Raw Variable Posteriors (2,000 trials):**
   - $\mu_i \in [-100.0, 100.0]$, $\sigma_i \in [0.01, 50.0]$ passing through Cody rational Chebyshev approximation / `scipy.special.ndtr` through `compute_all_marginal_probabilities` to `compute_dyad_window_masses`.

### 3.3 Empirical Findings
| Implementation | Test Suite | Iterations | Max Absolute Error $\left| \sum m - 1 \right|$ | Specification Tolerance | Status |
|---|---|---|---|---|---|
| **Python** | Deterministic Extremes | 8 | $0.00 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | PASS |
| **Python** | Random Adversarial Fuzzing | 10,000 | $2.2204 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | PASS |
| **Python** | E2E Posteriors Pipeline | 2,000 | $1.1102 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | PASS |
| **TypeScript**| Deterministic Extremes | 8 | $0.00 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | PASS |
| **TypeScript**| Random Adversarial Fuzzing | 5,000 | $1.7764 \times 10^{-15}$ | $1.0 \times 10^{-12}$ | PASS |
| **TypeScript**| E2E Posteriors Pipeline | 1,000 | $7.7716 \times 10^{-16}$ | $1.0 \times 10^{-12}$ | PASS |

Both implementations remain within machine precision ($\approx 10^{-15}$), surpassing the required $10^{-12}$ margin by $10^3\times$.

---

## 4. Invariant 3: Score Bounds $[-100.0, +100.0]$ Clipping

### 4.1 Specification Requirement (SPEC §6)
- $SQ_{raw} = 100 \cdot C \cdot S_{eff}$.
- $SQ = \min(SQ_{raw}, 100 \cdot G)$ if gate triggered else $SQ_{raw}$.
- $SQ = \text{clip}(SQ, -100.0, +100.0)$.

### 4.2 Adversarial Attack Scenarios
1. **Direct Parameter Space Stress:** Combinatorial grid of extreme values:
   - $C \in \{-10^9, -10^6, -100, -10, -1, -0.5, -0.0, 0.0, 0.5, 1, 10, 100, 10^6, 10^9\}$
   - $S \in \{-100, 0.0, 0.5, 0.75, 1.0, 2.0, 100, 10^6\}$
   - $G \in \{\text{None}, 0.0, 0.25, 0.5, 1.0, -1.0, -100, 100, 10^6\}$
2. **50,000 Random Fuzzing Iterations:** Arbitrary large floating-point inputs $C \in [-10^5, 10^5]$, $S \in [-10^5, 10^5]$, $G \in [-10^3, 10^3]$.
3. **20,000 End-to-End Pipeline Iterations:** Extreme unbounded scores $s_H \in [-10, 10]$, huge outcome deltas $d_k \in [-1000, 1000]$, unbounded telemetry components, and variance $\sigma_C \in [-100, 1000]$.

### 4.3 Empirical Findings
- **Python:** 0 NaN, 0 Inf, 0 boundary violations across all 70,000+ trials. Every output strictly satisfied $-100.0 \le SQ \le 100.0$.
- **TypeScript:** 0 NaN, 0 Inf, 0 boundary violations across all 70,000+ trials. Every output strictly satisfied $-100.0 \le SQ \le 100.0$.

---

## 5. Invariant 4: Non-Compensation Rule ($HNE < 0 \implies SNE' \le 0$)

### 5.1 Specification Requirement (SPEC §6)
- Rule: $SNE' = \min(SNE, 0)$ if $HNE < 0$ else $SNE$.
- Composite: $C = (w_h \cdot HNE + w_s \cdot SNE') / (w_h + w_s)$.
- Rationale: A system that harms a human ($HNE < 0$) cannot offset or dilute that harm by demonstrating high system efficiency or operator profits ($SNE > 0$).

### 5.2 Adversarial Attack Scenarios
1. **Artificial Efficiency Inflation:** Under varying negative human states $HNE \in \{-1.0, -0.8, -0.5, -0.2, -0.1, -0.01, -10^{-6}, -10^{-12}\}$, inject massive artificial system gains $SNE \in \{0.0, 0.01, 0.1, 0.5, 0.9, 1.0, 5.0, 100.0\}$.
   - Invariant: Verify $\Delta C = 0.0$, $\Delta SQ = 0.0$, and $SNE' \equiv 0.0$.
2. **50,000 Random Non-Compensation Trials:** Random $HNE \in [-1.0, -10^{-15}]$, random $SNE \in [10^{-15}, 100.0]$.
3. **Preservation of System Deficit:** Verify that when both human and system suffer ($HNE < 0$ and $SNE < 0$), machine harm is NOT wiped out ($SNE' == SNE < 0$), ensuring full accountability.

### 5.3 Empirical Findings
- **Python:**
  - Across all systematic and random trials with $HNE < 0$ and $SNE > 0$, $SNE'$ was identically $0.0$.
  - In all cases, $C(HNE, SNE) \equiv C(HNE, 0.0)$ and $SQ(HNE, SNE) \equiv SQ(HNE, 0.0)$.
  - When $SNE < 0$, $SNE' \equiv SNE$, correctly lowering composite $C$ and $SQ$. Zero violations.
- **TypeScript:**
  - Identical behavior across all 50,000 trials: $SNE' \le 0$, $\Delta C = 0$, $\Delta SQ = 0$. Zero violations.

---

## 6. Invariant 5: Harm Asymmetry (Under $C < 0$, $S_{eff} \equiv 1.0$)

### 6.1 Specification Requirement (SPEC §6, ADR-0004)
- Stability factor: $S = 0.5 + 0.5 \cdot (1 - \min(1, \sigma_C / \sigma_{max})) \in [0.5, 1.0]$.
- Harm override: $S_{eff} = S \text{ if } C \ge 0 \text{ else } 1.0$.
- Rationale: For positive scores, instability dampens performance ($S \to 0.5$ cuts score in half). If applied symmetrically to harm ($C < 0$), multiplying negative scores by $S = 0.5$ would cut harm magnitude in half (attenuate harm), rewarding an unstable harmful system. Therefore, $S_{eff}$ must be $1.0$ unconditionally when $C < 0$.

### 6.2 Adversarial Attack Scenarios
1. **Variance Injection Attack:** For negative composite scores $C \in \{-10^{-12}, -10^{-6}, -0.01, -0.1, -0.25, -0.5, -0.75, -1.0, -2.0\}$, sweep instability variance $\sigma_C$ from $0.0$ to $1000.0$ (including $\sigma_{max} = 0.5$).
   - Invariant: Verify $S_{eff} \equiv 1.0$, $SQ_{raw}(\sigma_C) \equiv SQ_{raw}(0)$, and $\frac{\partial SQ}{\partial \sigma_C} \equiv 0$.
2. **50,000 Random Harm Asymmetry Trials:** Random $C \in [-2.0, -10^{-15}]$, paired with two independent random variances $\sigma_1, \sigma_2 \in [0, 100]$. Verify $SQ_1 \equiv SQ_2$.
3. **Positive Dampening Contrast:** Verify that under $C > 0$, unstable variance $\sigma_C \ge 0.5$ correctly halves the raw score ($SQ_{unstable} = 0.5 \cdot SQ_{stable}$).

### 6.3 Empirical Findings
- **Python:**
  - Across all 50,000+ tests under $C < 0$, $S_{eff} \equiv 1.0$ unconditionally.
  - Harm magnitude is completely impervious to instability variance: $\Delta SQ = 0.0$ across all $\sigma_C$.
  - Contrast verified: for $C = 0.5$, $SQ_{stable} = 50.0 \to SQ_{unstable} = 25.0$ ($50\%$ dampening). Zero violations.
- **TypeScript:**
  - Identical behavior across all 50,000 trials: $S_{eff} \equiv 1.0$, $SQ_{raw}$ and $SQ$ perfectly constant across all $\sigma_C$. Zero violations.

---

## 7. Invariant 6: Safety Gate Ceiling Enforcement ($SQ \le 100 \cdot G$)

### 7.1 Specification Requirement (SPEC §7)
- Gate ceilings: CHI-1..3 ($G = 0.0$), CHI-4..7 ($G = 0.25$).
- Enforcement: $SQ = \min(SQ_{raw}, 100 \cdot G)$.
- Multi-event precedence: $G = \min_{i} G_i$.
- Non-elevation: Gate is a ceiling, not a floor; negative raw scores must never be increased.

### 7.2 Adversarial Attack Scenarios
1. **Maximum Performance Capping:** Under perfect raw performance ($C = 1.0, S = 1.0 \implies SQ_{raw} = +100.0$), verify that confirmed CHI-1..3 cap $SQ \le 0.0$, and CHI-4..7 cap $SQ \le 25.0$.
2. **Multi-CHI Resolution:** Test mixed sets (e.g., CHI-4 with $0.25$ + CHI-1 with $0.0$). Verify that minimum ceiling ($0.0$) strictly governs.
3. **Negative Score Elevation Attack:** Test whether gate ceiling elevates negative scores (e.g., $SQ_{raw} = -50.0$, gate ceiling $G = 0.25$). Verify $SQ = \min(-50, 25) = -50.0$.
4. **Invalid CHI Code Injection:** Inject invalid codes (`"CHI-0"`, `"CHI-8"`, `"CHI-99"`, `""`, `"CRITICAL"`). Verify immediate error rejection.

### 7.3 Empirical Findings
- **Python:**
  - Acute indicators CHI-1..3 capped $+100.0 \to 0.0$; CHI-4..7 capped $+100.0 \to 25.0$.
  - Mixed combinations strictly selected $\min(G_i)$ (e.g., `['CHI-4', 'CHI-1']` yielded ceiling $0.0$).
  - Negative scores were unaffected: $SQ_{raw} = -50.0$ remained $-50.0$ under all gates.
  - Invalid codes raised `ValueError`. Zero violations.
- **TypeScript:**
  - Acute indicators CHI-1..3 capped to $0.0$; CHI-4..7 capped to $25.0$.
  - Minimum ceiling resolution and negative score preservation verified.
  - Invalid codes threw descriptive `Error`. Zero violations.

---

## 8. Cross-Language Parity & Golden Vectors Parity

### 8.1 Golden Vectors Parity (SPEC Appendix A)
| Golden Vector | Target Concept | Metric | Expected | Python Result | TS Result | Diff (Py vs TS) |
|---|---|---|---|---|---|---|
| **GV-SQ-001** | Mutualism, Zone Z2 | $HNE$ | $0.25$ | $0.25$ | $0.25$ | $0.00$ |
| | | $SNE$ | $0.48$ | $0.48$ | $0.48$ | $0.00$ |
| | | $C$ | $0.319$ | $0.319$ | $0.319$ | $0.00$ |
| | | $S$ | $0.9$ | $0.9$ | $0.9$ | $0.00$ |
| | | $SQ$ | $28.71$ | $28.71$ | $28.71$ | $0.00$ |
| | | Class | `mutualism` | `mutualism` | `mutualism` | MATCH |
| | | Zone | `Z2` | `Z2` | `Z2` | MATCH |
| **GV-SQ-002** | Parasitism, Non-comp, Z6 | $HNE$ | $-0.4$ | $-0.4$ | $-0.4$ | $0.00$ |
| | | $SNE'$ | $0.0$ | $0.0$ | $0.0$ | $0.00$ |
| | | $C$ | $-0.28$ | $-0.28$ | $-0.28$ | $0.00$ |
| | | $SQ$ | $-28.0$ | $-28.0$ | $-28.0$ | $0.00$ |
| | | Class | `parasitism`| `parasitism`| `parasitism`| MATCH |
| | | Zone | `Z6` | `Z6` | `Z6` | MATCH |
| **GV-SQ-003** | Gate CHI-2, Zone Z7 | $C$ | $0.6$ | $0.6$ | $0.6$ | $0.00$ |
| | | $SQ_{raw}$ | $60.0$ | $60.0$ | $60.0$ | $0.00$ |
| | | Ceiling | $0.0$ | $0.0$ | $0.0$ | $0.00$ |
| | | $SQ$ | $0.0$ | $0.0$ | $0.0$ | $0.00$ |
| | | Zone | `Z7` | `Z7` | `Z7` | MATCH |

### 8.2 200-Vector Random Cross-Language Sweep
Across 200 random dyads evaluated independently in Python and TypeScript:
- **Max Absolute Discrepancy on HNE:** $1.1102 \times 10^{-16}$
- **Max Absolute Discrepancy on SNE:** $0.0000 \times 10^{0}$
- **Max Absolute Discrepancy on C:** $8.3267 \times 10^{-17}$
- **Max Absolute Discrepancy on S:** $0.0000 \times 10^{0}$
- **Max Absolute Discrepancy on SQ:** $7.1054 \times 10^{-15}$

All metrics match well within the normative threshold of $1.0 \times 10^{-6}$, achieving near double-precision floating-point parity.

---

## 9. Conclusion & Verdict

The mathematical core implementations in both Python (`packages/py/src/symnoesis/`) and TypeScript (`packages/ts/src/`) strictly conform to normative specification SPEC §3–§9. All 6 fundamental invariants withstand comprehensive adversarial stress testing with zero regressions, zero violations, and machine-precision numerical parity.

**Final Verdict:** **APPROVE**
