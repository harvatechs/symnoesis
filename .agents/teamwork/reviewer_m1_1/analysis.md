# Milestone 1 Review Analysis: Math Reference Core & Parity

**Reviewer:** `reviewer_m1_1` (Reviewer 1)  
**Roles:** Reviewer & Adversarial Critic  
**Working Directory:** `E:/Symnoesis/.agents/teamwork/reviewer_m1_1`  
**Date:** 2026-10-12  
**Target Milestone:** M1 (Math Reference Core & Parity)  
**Verdict:** **APPROVE**  

---

## 1. Executive Summary

A comprehensive, objective, and adversarial review was conducted on the Milestone 1 deliverables produced by `worker_m1_1`. The evaluation covered:
1. Complete verification of toolchain test and lint commands (`pytest`, `mypy --strict`, `ruff`, `tsc --noEmit`, `vitest`).
2. Independent re-verification of mathematical precision and cross-language parity:
   - Cody's rational Chebyshev erfc against `scipy.special.ndtr` over 65,006 points (max error: $2.22 \times 10^{-16}$, passing the $< 10^{-9}$ threshold).
   - Golden reference vector parity (GV-SQ-001, GV-SQ-002, GV-SQ-003) between Python reference and TypeScript port (discrepancy: $0.00 \times 10^{0}$, passing the $< 10^{-6}$ threshold).
   - Gray code bijection on all 16 4-bit values and all 65,536 16-bit integers.
   - 16x16 grid coordinate interleaving and inverse across all 256 pixels in `grid-256-pixels.json`.
   - Non-compensation rule ($SNE' = \min(SNE, 0)$ if $HNE < 0$) and harm asymmetry ($S_{eff} = 1.0$ if $C < 0$).
   - Governance zone precedence ($Z7 \succ Z6 \succ Z5 \succ Z4 \succ Z1 \succ Z2 \succ Z3$) and retention of secondary tags ($Z1$ retained when $Z7$ is primary).
   - Validation of all 16 JSON schemas in `spec/schemas/`.
3. Strict code quality, type safety, constant isolation, and test coverage ($\ge 95\%$, achieved $99\%$).
4. Adversarial integrity audit: zero hardcoded outputs in production code, zero facade implementations, zero shortcutting of normative requirements.

**Final Assessment:** All criteria meet or exceed normative specifications. Milestone 1 is approved for merge/handoff.

---

## 2. Independent Verification Battery

### 2.1 Toolchain Execution

| Command | Working Dir | Status | Details |
|---|---|---|---|
| `uv run --directory packages/py pytest --cov=symnoesis` | Repo root | **PASSED** | 37 tests passed in 5.07s; line coverage 99% (target $\ge 95\%$) |
| `uv run --directory packages/py mypy src tests` | Repo root | **PASSED** | 0 errors across 24 source files under strict typechecking |
| `uv run --directory packages/py ruff check .` | Repo root | **PASSED** | All lint rules passed clean |
| `uv run --directory packages/py ruff format --check .` | Repo root | **PASSED** | 25 files already formatted |
| `pnpm -r run typecheck` | Repo root | **PASSED** | `tsc --noEmit` exited 0 with 0 errors in `@symnoesis/core` |
| `pnpm -r run test` | Repo root | **PASSED** | 16 tests passed across 6 test files in Vitest |
| `cd packages/py && uv build` | `packages/py` | **PASSED** | Successfully built sdist and wheel |
| `pnpm -r run build` | Repo root | **PASSED** | Successfully built TS bundle and `.d.ts` declarations |

### 2.2 Mathematical Precision: Cody's Rational Chebyshev erfc vs. `scipy.special.ndtr`

- **Normative Requirement:** Maximum discrepancy $< 10^{-9}$ across all real inputs.
- **Verification Method:** An independent script (`verify_parity.py` / `verify_cody`) evaluated 65,006 evaluation points:
  - 50,001 points uniformly spaced in $[-10.0, 10.0]$
  - 5,000 points in $[-38.0, -9.0]$
  - 5,000 points in $[9.0, 38.0]$
  - 1,001 points sampled across Cody interval boundary at $\pm 0.46875 \cdot \sqrt{2}$
  - 1,001 points sampled across Cody interval boundary at $\pm 4.0 \cdot \sqrt{2}$
  - 1,001 points around $0.0$ ($[-10^{-5}, 10^{-5}]$)
- **Observed Result:**
  - Tested: 65,006 points
  - Maximum absolute error against `scipy.special.ndtr`: **$2.220446 \times 10^{-16}$**
  - Relative error at tails: down to floating-point machine epsilon ($\approx 1.11 \times 10^{-16}$)
  - Symmetry verification: $\Phi(z) + \Phi(-z) = 1.0000000000000000$
  - Boundary limits: $\Phi(+\infty) = 1.0$, $\Phi(-\infty) = 0.0$, $\Phi(\text{NaN}) = \text{NaN}$.
- **Verdict:** **PASS** (substantially superior to the required $< 10^{-9}$ tolerance).

### 2.3 Golden Reference Vector Parity (GV-SQ-001..003)

- **Normative Requirement:** Python reference and TypeScript port outputs match within $< 10^{-6}$.
- **Verification Method:** Direct cross-runtime execution comparing Python `symnoesis` functions against TypeScript `@symnoesis/core` functions on the exact input payloads from `spec/vectors/`.

| Vector | Metric | Python Result | TypeScript Result | Diff | Required | Status |
|---|---|---|---|---|---|---|
| **GV-SQ-001** | $HNE$ | 0.25 | 0.25 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SNE$ | 0.48 | 0.48 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SNE'$ | 0.48 | 0.48 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $C$ | 0.319 | 0.319 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $S$ | 0.90 | 0.90 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SQ_{raw}$ | 28.71 | 28.71 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SQ$ | 28.71 | 28.71 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | Class | `mutualism` | `mutualism` | exact | match | **PASS** |
| | Primary Zone | `Z2` | `Z2` | exact | match | **PASS** |
| **GV-SQ-002** | $SNE'$ | 0.00 | 0.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $C$ | -0.28 | -0.28 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $S_{eff}$ | 1.00 | 1.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SQ$ | -28.00 | -28.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | Class | `parasitism` | `parasitism` | exact | match | **PASS** |
| | Primary Zone | `Z6` | `Z6` | exact | match | **PASS** |
| **GV-SQ-003** | Gate Ceiling | 0.00 | 0.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | Gate Triggered| `true` | `true` | exact | match | **PASS** |
| | $SQ_{raw}$ | 60.00 | 60.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | $SQ$ | 0.00 | 0.00 | $0.00 \times 10^0$ | $< 10^{-6}$ | **PASS** |
| | Primary Zone | `Z7` | `Z7` | exact | match | **PASS** |

- **Verdict:** **PASS** (exact bit-for-bit parity across all computed metrics).

### 2.4 Gray Code Bijection

- **Normative Requirement:** 4-bit Gray code bijections $G(k) = k \oplus (k \gg 1)$ and $G^{-1}(g)$ invertible across all 16 values.
- **Verification Method:** Checked against `spec/vectors/gray-code-16.json` for all 16 indices, and exhaustive round-trip property test across all $k \in [0, 65535]$ in both Python and TypeScript runtimes.
- **Observed Result:**
  - $int\_to\_gray(k)$ and $gray\_to\_int(g)$ are exact mathematical inverses for all $k \in [0, 65535]$.
  - Bit representations and Hamming distance calculation verified.
- **Verdict:** **PASS**.

### 2.5 16x16 Grid Coordinate System

- **Normative Requirement:** Bijective mapping between $(col, row) \in [0, 15] \times [0, 15]$ and pixel string `hHHHH-mMMMM`.
- **Verification Method:** Verified all 256 entries in `spec/vectors/grid-256-pixels.json` in both Python and TypeScript:
  - `coord_to_pixel_id(PixelCoord(col, row)) == pixel_id`
  - `pixel_id_to_coord(pixel_id) == PixelCoord(col, row)`
  - Big-endian bit parsing: `parse_pixel_id(pixel_id)` matches golden vector `h_bits` and `m_bits`
  - Visual torus neighbors: exactly 4 planar neighbors on periodic boundary
  - Hamming single-flip neighbors: exactly 8 neighbors (4 human flips, 4 machine flips)
- **Verdict:** **PASS**.

### 2.6 Net Effects, Non-Compensation Rule & Harm Asymmetry

- **Normative Requirement:**
  - $SNE' = \min(SNE, 0)$ if $HNE < 0$ else $SNE$.
  - $S_{eff} = 1.0$ if $C < 0$ else $S$.
- **Verification Method:**
  - Tested positive $HNE = 0.5$, $SNE = 0.8 \implies SNE' = 0.8$.
  - Tested zero boundary $HNE = 0.0$, $SNE = 0.8 \implies SNE' = 0.8$.
  - Tested negative perturbation $HNE = -10^{-4}$, $SNE = 0.8 \implies SNE' = 0.0$ (positive system gains zeroed out).
  - Tested double-negative $HNE = -0.5$, $SNE = -0.3 \implies SNE' = -0.3$ (system harm preserved).
  - Harm asymmetry: $C = 0.5, S = 0.7 \implies S_{eff} = 0.7$; $C = -0.5, S = 0.7 \implies S_{eff} = 1.0$ (instability cannot soften harm).
- **Verdict:** **PASS**.

### 2.7 Governance Zones Precedence & Secondary Tags

- **Normative Requirement:** Strict precedence `[Z7, Z6, Z5, Z4, Z1, Z2, Z3]`. When a higher-priority zone matches, lower matching conditions are retained in `secondary_tags`.
- **Verification Method:**
  - Scenario 1: $SQ = 80.0$, $has\_confirmed\_chi = True$. Evaluates to Primary: `Z7`, Secondary Tags: `['Z1']`. Confirmed that `Z1` is retained in `secondary_tags`.
  - Scenario 2: $SQ = -40.0$, $has\_confirmed\_chi = True$. Evaluates to Primary: `Z7`, Secondary Tags: `['Z6']`.
  - Scenario 3: $SQ = 30.0$, $H_1=0$, $M_2=0$. Evaluates to Primary: `Z5` (Dependence), Secondary Tags: `['Z2']` (Productive).
- **Verdict:** **PASS**.

### 2.8 JSON Schema Draft 2020-12 Verification

- **Normative Requirement:** All 16 schemas in `spec/schemas/` have valid `"$schema"` header.
- **Verification Method:** `verify_schemas.py` inspected all 16 files in `spec/schemas/*.schema.json`.
- **Observed Result:**
  - Total schemas found: 16
  - Each schema possesses `"$schema": "https://json-schema.org/draft/2020-12/schema"`
  - Zero empty keys `""` found across all 16 files.
  - JSON parse succeeded for all files.
- **Verdict:** **PASS**.

---

## 3. Code Quality & Integrity Audit

### 3.1 Integrity Violation Check

As required by the adversarial critic mandate, active checks were performed for integrity shortcuts:
1. **Hardcoded test outputs:** Grepped repository source code for test-vector identifiers (`GV-SQ-001`, `GV-SQ-002`, `GV-SQ-003`). Found strictly in test suites (`tests/unit/test_worked_examples.py`, `packages/ts/tests/golden_vectors.test.ts`), with 0 occurrences in `packages/py/src/symnoesis/` or `packages/ts/src/`.
2. **Facade implementations:** Inspected mathematical functions in Python and TypeScript. All logic is algorithmic (e.g., iterative bit-shift folding for Gray inverse, rational Chebyshev polynomials for erfc, proper matrix arithmetic for pixel assignment).
3. **Delegation / bypasses:** The TypeScript port `@symnoesis/core` was built from scratch without external math libraries, using browser-compatible pure TypeScript.
4. **Self-certifying work:** Independent verification scripts (`verify_parity.py`, `verify_gray_grid.mjs`, `verify_schemas.py`) were written and executed separately from the worker's suite to validate all outputs.

### 3.2 Numeric Constants Isolation

- All domain parameters, thresholds, weights, margins, and zone boundaries are loaded from `spec/config/symn-01.v0.1.yaml` via `SymnoesisConfig` in Python.
- In TypeScript, `DEFAULT_CONFIG` is defined as a frozen configuration interface mirroring `symn-01.v0.1.yaml` to ensure zero file-system dependencies when executed in client-side web browsers.
- Constants appearing in source files are strictly standard mathematical invariants ($\sqrt{2}$, $\pi^{-1/2}$, bit widths of 4 and 8, or Gray code shift powers of 2).

### 3.3 Type Safety & Coverage

- Python: `mypy --strict src tests` passed with 0 errors across 24 files.
- TypeScript: `tsc --noEmit` passed with 0 errors, no `@ts-ignore`, no `any` types.
- Test Coverage: Core calculation line coverage is **99%** in Python, exceeding the $\ge 95\%$ target:
  - `assign.py`: 100%
  - `classes.py`: 100%
  - `evidence.py`: 100%
  - `gates.py`: 100%
  - `gray.py`: 100%
  - `grid.py`: 100%
  - `net_effects.py`: 95%
  - `sq.py`: 100%
  - `stability.py`: 100%
  - `variables.py`: 100%
  - `zones.py`: 100%
  - `config.py`: 97%

---

## 4. Adversarial Findings & Challenges

### Finding 1 [Minor / Informational]: Empty Key Artifact in `spec/vectors/grid-256-pixels.json`

- **What:** Line 2 of `spec/vectors/grid-256-pixels.json` contains `"": "https://json-schema.org/draft/2020-12/schema"` instead of `"$schema"`.
- **Where:** `spec/vectors/grid-256-pixels.json:2`
- **Why:** While all 16 JSON schema files in `spec/schemas/` were repaired, this vector fixture file still retains the legacy empty-string key.
- **Risk Assessment:** Low. `grid-256-pixels.json` is a golden vector test fixture, not a schema. Per CLAUDE.md §1 rule 5 ("Never edit a golden vector to make a test pass"), editing golden vectors without an ADR/RFC is prohibited. Tests parse the JSON object without relying on the key name.
- **Recommendation:** Do not edit now to maintain golden vector purity. Log an issue for Milestone 5 when vector generation tooling is finalized.

### Finding 2 [Informational]: TypeScript Config Synchronization

- **What:** `packages/ts/src/config.ts` defines `DEFAULT_CONFIG` as a TypeScript object literal.
- **Where:** `packages/ts/src/config.ts:94`
- **Why:** In browser runtimes (`apps/web`), reading YAML from the local disk is not possible without bundling. However, if `spec/config/symn-01.v0.1.yaml` changes in future milestones, manual edits could diverge.
- **Risk Assessment:** Low for M1 (configs are currently identical).
- **Recommendation:** For Milestone 4/5, add a build generator script (`make gen` or `pnpm run gen:config`) that parses `symn-01.v0.1.yaml` and outputs `packages/ts/src/config.ts` automatically.

### Finding 3 [Informational]: Longitudinal Dyad Bootstrap in TypeScript

- **What:** `bootstrap_dyad_sq_ci` is implemented in Python using NumPy, but is not yet in TypeScript.
- **Where:** `packages/py/src/symnoesis/sq.py:45`
- **Why:** Milestone 1 focuses on single-window calculation parity and golden vectors. Dyad clustering and multi-frame bootstrap are scoped for Milestone 2 (MFC & Longitudinal Diagnostics) and Milestone 4 (Web Portal).
- **Risk Assessment:** None for Milestone 1. Scoped appropriately.

---

## 5. Review Verdict

**Verdict:** **APPROVE**

Milestone 1 satisfies all requirements set forth in `PROJECT.md`, `CLAUDE.md`, and the prompt dispatch. The mathematical reference implementations in Python and TypeScript are robust, strictly typed, tested with high coverage, and demonstrate exact numerical parity.
