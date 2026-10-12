# Python and TypeScript Core Architecture & Algorithm Investigation Report

**Date:** 2026-10-12  
**Author:** Python and TypeScript Core Explorer (`explorer_survey_pyts_1`)  
**Mission:** Thorough investigation of the codebase state for core math and algorithms across `packages/py`, `packages/ts`, and `spec/`, assessing exact gaps against Requirements R1 (Milestones M1, M3) and R2 (Milestones M2, M4).

---

## Executive Summary

The Symnoesis codebase contains an initial draft of the mathematical reference core in Python (`packages/py/src/symnoesis/`), but **critical implementation bugs and type errors currently break the Python test suite and type checker**. 
In TypeScript (`packages/ts/src/`), **zero mathematical or algorithmic modules are implemented** (only a 6-line version stub exists). Furthermore, none of the Minimal Failure Cover (MFC), Counterfactual Diagnostics, Temporal Engine, or Data Contract schema bindings have been authored in either language. Shared JSON schemas in `spec/schemas/` also suffer from structural malformation (corrupted `"$schema"` property keys).

### Key Metrics Snapshot
| Area | Python (`packages/py`) | TypeScript (`packages/ts`) | Shared Specs (`spec/`) |
| :--- | :--- | :--- | :--- |
| **Source Modules** | 13 files (drafted) | 1 file (stub only) | 1 config, 16 schemas, 5 vectors |
| **Test Suite** | 22 tests: 18 passed, **4 failed** | 1 test: 1 passed (sanity only) | Golden vectors pass in Py (3/3) |
| **Strict Type Checking** | **4 mypy errors** (`mypy --strict`) | Clean (only stub checked) | N/A |
| **Linting & Formatting** | **45 ruff errors**, 3 format issues | Clean | Prettier issues on 16 schemas |
| **Test Coverage** | 89% (target: >= 95%) | N/A | N/A |
| **R1 Parity Status** | Drafted with bugs in Py; **0% in TS** | **Missing** | Golden vectors present |
| **R2 MFC & Diagnostics** | **0% implemented** (`cover.py` missing) | **0% implemented** | Specification defined |

---

## 1. Directory Structure & Inventory

### 1.1 Python Package (`packages/py/`)
- **Build & Configuration:**
  - `pyproject.toml`: Configured with Hatchling backend, Python `>=3.12`. Pinned runtime dependencies: `pydantic>=2.7.0`, `pyyaml>=6.0`, `numpy>=1.26.0`, `scipy>=1.12.0`, `cryptography>=42.0.0`, `typer>=0.12.0`, `structlog>=24.1.0`. Dev dependencies: `pytest>=8.0.0`, `pytest-cov>=5.0.0`, `hypothesis>=6.100.0`, `ruff>=0.6.0`, `mypy>=1.10.0`, `types-pyyaml`, `sympy>=1.12`, `codespell>=2.3.0`.
  - `uv.lock`: Dependency lockfile committed.
  - `README.md`: Basic description.
  - Declared script entrypoint: `symnoesis = "symnoesis.cli:app"` (Target `symnoesis/cli.py` is **missing**).
- **Source Code (`packages/py/src/symnoesis/`):**
  - `__init__.py` (88 lines): Public package exports.
  - `config.py` (225 lines): Pydantic v2 configuration parser for `spec/config/symn-01.v0.1.yaml`.
  - `gray.py` (55 lines): Binary-reflected Gray code operations and bijections.
  - `grid.py` (98 lines): 16x16 Gray-coded grid coordinate transformations and pixel ID parsing.
  - `variables.py` (60 lines): Normal CDF, variable scaling, marginal probability calculation.
  - `assign.py` (63 lines): Probabilistic mass assignment across 256 pixels, pruning, modal pixel.
  - `net_effects.py` (86 lines): HNE, SNE, non-compensation rule, composite effect $C$.
  - `stability.py` (36 lines): Stability factor $S$, sample standard deviation, harm override.
  - `gates.py` (46 lines): Critical Harm Indicator (CHI) safety gate evaluation.
  - `sq.py` (74 lines): Symnoesis Quotient calculation and cluster bootstrap CI.
  - `classes.py` (87 lines): Ecological symbiosis 9-cell classification and operator-blind suppression.
  - `zones.py` (79 lines): Governance zone assignment (Z1–Z7) and precedence logic.
  - `evidence.py` (38 lines): Evidence tier hierarchy (E0–E3) and certification check.
- **Test Suite (`packages/py/tests/`):**
  - `tests/unit/test_sanity.py`: Package metadata test.
  - `tests/unit/test_config.py`: Configuration parsing and validation tests.
  - `tests/unit/test_gray.py`: Gray code bijection and Hamming distance tests.
  - `tests/unit/test_grid.py`: 256-pixel coordinate mapping and neighbor tests.
  - `tests/unit/test_variables.py`: Normal CDF precision vs `scipy.special.ndtr`, H2 threshold.
  - `tests/unit/test_assign.py`: Probabilistic assignment mass normalization.
  - `tests/unit/test_net_effects.py`: Non-compensation, operator-blind fallback, symbiosis classes.
  - `tests/unit/test_gates_and_zones.py`: Safety gate ceilings and governance zones.
  - `tests/unit/test_worked_examples.py`: Golden vectors GV-SQ-001, GV-SQ-002, GV-SQ-003.
  - `tests/property/`: **Empty directory**. No Hypothesis property tests exist.

### 1.2 TypeScript Package (`packages/ts/`)
- **Build & Configuration:**
  - `package.json`: Package `@symnoesis/core` (v0.1.0-dev.0). Module type: `module`. Dependencies: `zod: ^3.23.8`. DevDependencies: `fast-check: ^3.21.0`, `typescript: ^5.5.4`, `vitest: ^2.0.5`.
  - `tsconfig.json`: Target `ES2022`, Module `NodeNext`, ModuleResolution `NodeNext`, strict mode fully enabled (`noImplicitAny`, `strictNullChecks`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`).
- **Source Code (`packages/ts/src/`):**
  - `index.ts` (6 lines): Contains only `export const VERSION = "0.1.0-dev.0";`.
- **Test Suite (`packages/ts/tests/`):**
  - `tests/sanity.test.ts`: 1 test verifying `VERSION`.

### 1.3 Shared Schemas & Vectors (`spec/`)
- `spec/config/symn-01.v0.1.yaml`: Canonical normative configuration file matching SPEC Appendix B.
- `spec/schemas/`: 16 JSON Schemas:
  `assessment.schema.json`, `config.schema.json`, `consent.schema.json`, `cover_rule.schema.json`, `dyad.schema.json`, `dyad_window_record.schema.json`, `map_frame.schema.json`, `memory_event.schema.json`, `pixel_record.schema.json`, `run_manifest.schema.json`, `session.schema.json`, `symnoesis_card.schema.json`, `tool_call.schema.json`, `turn.schema.json`, `variable_score.schema.json`, `window.schema.json`.
  *(Defect: All 16 schemas have `"": "https://json-schema.org/draft/2020-12/schema"` instead of `"$schema": "..."`)*.
- `spec/vectors/`:
  - `gray-code-16.json`: 16 Gray code elements.
  - `grid-256-pixels.json`: Complete 256 pixel coordinates, bit patterns, and Z5 conditions.
  - `gv-sq-001.json`: Golden vector 1 (Mutualism, Zone Z2).
  - `gv-sq-002.json`: Golden vector 2 (Parasitism, Non-compensation, Zone Z6).
  - `gv-sq-003.json`: Golden vector 3 (Safety gate ceiling, Zone Z7).

---

## 2. Implementation Analysis: Implemented vs Missing vs Broken

### 2.1 Python Reference Core (`packages/py`)

#### Implemented Components
1. **Configuration Loader (`config.py`):**
   - Implements full Pydantic v2 frozen schema matching SPEC Appendix B.
   - Validates weights summation ($\sum w = 1.0$), threshold completeness, bounds.
   - Provides `SymnoesisConfig.load_default()` searching parent hierarchy.
2. **Normal CDF & Probability (`variables.py`):**
   - `normal_cdf(x) = 0.5 * erfc(-x / sqrt(2))` implemented using Python `math.erfc`.
   - Verified in `test_variables.py` to match `scipy.special.ndtr` within machine precision ($< 10^{-15}$).
   - `effect_to_score`, `compute_h2_threshold`, `compute_marginal_probability`, `compute_all_marginal_probabilities` implemented.
3. **Mass Assignment (`assign.py`):**
   - Computes unpruned masses for all 256 pixels: $\prod_i [p_i \text{ if } b_i=1 \text{ else } 1-p_i]$.
   - Pruning below `config.assignment.prune_mass` ($10^{-4}$) and renormalization implemented.
   - `get_modal_pixel` returns $\text{argmax}_c m(c)$.
4. **Net Effects Calculus (`net_effects.py`):**
   - `compute_hne`: $\text{HNE}_{\text{state}} = \sum a_i (2s_i - 1)$, tanh-transformed outcomes, blend $\lambda$.
   - `compute_sne`: $0.4 \cdot \text{Integrity} + 0.4 \cdot \text{Reliability} + 0.2 \cdot \text{Operator}$. Missing operator sets `operator_blind = True` and defaults to 0.0.
   - `apply_non_compensation`: $\text{SNE}' = \min(\text{SNE}, 0)$ if $\text{HNE} < 0$.
   - `compute_composite_c`: $C = (w_h \cdot \text{HNE} + w_s \cdot \text{SNE}') / (w_h + w_s)$.
5. **Stability & SQ Composite (`stability.py`, `sq.py`):**
   - `compute_stability_factor`: $S = 0.5 + 0.5 \cdot (1 - \min(1, \sigma_C / \sigma_{\max}))$.
   - `compute_effective_stability`: Harm override $S_{\text{eff}} = S \text{ if } C \ge 0 \text{ else } 1.0$.
   - `compute_sq`: $\text{SQ}_{\text{raw}} = 100 \cdot C \cdot S_{\text{eff}}$, gate ceiling $\min(\text{SQ}_{\text{raw}}, 100 \cdot G)$, clipping $[-100, +100]$.
   - `bootstrap_dyad_sq_ci`: Cluster bootstrap percentile CI over dyads using `numpy.random.default_rng`.
6. **Safety Gate & Symbiosis Classes (`gates.py`, `classes.py`):**
   - `evaluate_safety_gate`: Minimum ceiling among confirmed CHIs; status mapping (`critical`, `watch`, `safe`, `unknown`).
   - `classify_symbiosis`: 3-way sign with hysteresis ($\pm 0.2$); 9-cell matrix mapping; operator-blind suppression (parasitism $\to$ amensalism with caveat).
7. **Golden Vector Verification (`test_worked_examples.py`):**
   - GV-SQ-001 (Mutualism, Z2), GV-SQ-002 (Parasitism, Z6), GV-SQ-003 (Gate ceiling, Z7) all pass within $10^{-6}$.

#### Broken & Defective Components in Python
1. **Gray Code Inversion Flaw (`gray.py:25`):**
   - **Flaw:** `gray_to_int(g)` uses `n ^= g >> shift` inside `while (g >> shift) > 0:` with `shift <<= 1`. Because it XORs against shifts of the original input `g` rather than the accumulating value `n`, `gray_to_int(12)` yields `9` instead of `8`.
   - **Correct algorithm (SPEC §4):** Fold `n` via `n ^= (n >> shift)` or `g ^= g >> 1; g ^= g >> 2; g ^= g >> 4; g ^= g >> 8`.
   - **Impact:** Fails `test_gray_golden_vector` and cascades to `grid.py:pixel_id_to_coord`, breaking `test_256_pixels_golden_vector`.
2. **Governance Zone Logic Defect (`zones.py:59`):**
   - **Flaw:** Line 59 checks `if sq is not None and sq >= config.zones.z1_min and not is_trajectory_negative and not has_confirmed_chi: matches.append("Z1")`.
   - **Impact:** When a pixel has confirmed CHI (`has_confirmed_chi = True`) and SQ $\ge 60$, Z7 is primary, but Z1 is completely excluded from `matches`, so `assert "Z1" in res7.secondary_tags` fails in `test_gates_and_zones.py`. Precedence rule (SPEC §9) states all matching conditions must be reported as secondary tags.
3. **Missing Package Metadata (`__init__.py`):**
   - `__version__ = "0.1.0.dev0"` was accidentally omitted from `symnoesis/__init__.py`.
   - Fails `test_sanity.py` (`AttributeError: module 'symnoesis' has no attribute '__version__'`).
4. **Mypy Type Narrowing Errors (`net_effects.py:59`, `sq.py:33, 35`):**
   - In `net_effects.py:59`, `eff_operator = 0.0 if operator_blind else float(operator)` fails strict mypy because `operator` has type `float | None` and mypy does not narrow through boolean flag `operator_blind`.
   - In `sq.py:33, 35`, `float(gate_ceiling)` fails strict mypy because `gate_ceiling` is `float | None` and condition checked boolean flag `gate_triggered`.

#### Missing Components in Python (R1 & R2)
1. **Minimal Failure Cover (MFC) Optimization (`cover.py` - MISSING):**
   - SPEC §11 requires exact MFC optimization via MILP (`scipy.optimize.milp` with HiGHS) across 6561 candidate subcubes of the 8-cube.
   - Missing subcube enumeration, purity $\pi(R)$, coverage $\text{cov}(R)$, harm mass $h(c)$.
   - Missing MILP objective formulation (lexicographically minimize rule count, total literals, maximize covered mass, deterministic tie-breaking).
   - Missing strict mode Quine-McCluskey solver and cross-check against `sympy.logic.boolalg.SOPform`.
   - Missing human-readable explanation formatting.
2. **Counterfactual Repair Diagnostics (`counterfactual.py` - MISSING):**
   - SPEC §12 requires evaluating repair flips $c \oplus v$ for all $v$ with $b_v(c) = 0$.
   - Missing observed vs modeled decision logic (`n_eff >= n_cell_min`).
   - Missing pooled additive ridge regression model for unobserved states.
   - Missing dominant failure variable identification ($\text{argmax}_v \Delta\text{SQ}_v$).
3. **Temporal Engine (`temporal.py` - MISSING):**
   - SPEC §10 requires trajectory tracking across frames `[1, 7, 28, 84, 182]`.
   - Missing Minimum Detectable Change calculation ($\text{MDC} = 1.96 \cdot \sqrt{2} \cdot \text{SEM}$).
   - Missing consecutive negative trajectory evaluator (2 consecutive intervals $\Delta\text{SQ} < -\text{MDC}$).
4. **Data Contract Schema Bindings (MISSING):**
   - SPEC §14 requires Pydantic v2 models for all 16 JSON schema entities (`Dyad`, `Window`, `Session`, `Turn`, `ToolCall`, `MemoryEvent`, `Consent`, `Assessment`, `VariableScore`, `DyadWindowRecord`, `PixelRecord`, `MapFrame`, `CoverRule`, `SymnoesisCard`, `RunManifest`).
5. **Cryptographic Signing & Privacy (`signing.py`, `privacy.py` - MISSING):**
   - SPEC §14, §16 requires Ed25519 signing of `RunManifest`, differential privacy Laplace/Gaussian mechanism, and $k$-anonymity suppression ($k_{\min} = 10$).
6. **CLI Entrypoint (`cli.py` - MISSING):**
   - `pyproject.toml` references `symnoesis.cli:app`, but `cli.py` does not exist.

---

### 2.2 TypeScript Reference Core (`packages/ts`)

#### Current Status
- **Files present:** Only `src/index.ts` (exporting `VERSION`) and `tests/sanity.test.ts`.
- **Implementation completeness:** **0%** of core math and algorithms.

#### Missing Components in TypeScript (R1 Parity)
1. **Normative Configuration Loader & Schema:**
   - Typed configuration model and bundled/loaded normative defaults matching `symn-01.v0.1.yaml`.
2. **Normal CDF & Cody's `erfc` Algorithm:**
   - SPEC §3 requires $\Phi(x)$ computed via `erfc` with documented algorithm (e.g., Cody's rational Chebyshev approximation) matching `scipy.special.ndtr` within $10^{-9}$.
3. **Gray Code & Grid Coordinates:**
   - `intToGray`, `grayToInt`, `intToBits`, `bitsToInt`, `hammingDistance`, `isAdjacentOnTorus`.
   - `PixelCoord`, `coordToPixelId`, `pixelIdToCoord`, `getGridNeighbors`, `getAllSingleFlipNeighbors`.
4. **Variable Scaling & Mass Assignment:**
   - `effectToScore`, `computeH2Threshold`, `computeMarginalProbability`, `computeDyadWindowMasses`, `getModalPixel`.
5. **Net Effects & SQ Composite:**
   - `computeHne`, `computeSne`, `applyNonCompensation`, `computeCompositeC`, `computeStabilityFactor`, `computeEffectiveStability`, `evaluateSafetyGate`, `computeSq`.
6. **Classification & Governance Zones:**
   - `computeSign3`, `classifySymbiosis`, `evaluateZones`.
7. **Data Contracts & Zod Schemas:**
   - Zod runtime validation schemas and TypeScript types for all 16 data entities.
8. **Parity Tests & Golden Vectors:**
   - Vitest test suite executing GV-SQ-001, GV-SQ-002, GV-SQ-003, Gray-16, and Grid-256 with parity verification within $10^{-6}$ against Python.
   - Property tests using `fast-check` mirroring Python Hypothesis tests.

---

## 3. Verification & Diagnostic Commands Executed

### 3.1 Python Test Suite (`pytest`)
**Command:** `uv run --directory packages/py pytest`  
**Result:** **4 FAILED, 18 PASSED** (Exit code 1).
```
FAILED tests/unit/test_sanity.py::test_package_metadata - AttributeError: module 'symnoesis' has no attribute '__version__'
FAILED tests/unit/test_gray.py::test_gray_golden_vector - assert 9 == 8 (gray_to_int(12) returned 9)
FAILED tests/unit/test_grid.py::test_256_pixels_golden_vector - AssertionError: assert PixelCoord(col=9, row=0) == PixelCoord(col=8, row=0)
FAILED tests/unit/test_gates_and_zones.py::test_zones_precedence - AssertionError: assert 'Z1' in [] (res7.secondary_tags was empty)
```

### 3.2 Python Test Coverage (`pytest --cov=symnoesis`)
**Command:** `uv run --directory packages/py pytest --cov=symnoesis`  
**Result:** Overall line coverage is **89%** (Target: $\ge 95\%$).
```
Name                           Stmts   Miss  Cover
--------------------------------------------------
src\symnoesis\__init__.py         13      0   100%
src\symnoesis\assign.py           32      4    88%
src\symnoesis\classes.py          28      0   100%
src\symnoesis\config.py          152      5    97%
src\symnoesis\evidence.py         13      6    54%
src\symnoesis\gates.py            18      1    94%
src\symnoesis\gray.py             29      0   100%
src\symnoesis\grid.py             55      3    95%
src\symnoesis\net_effects.py      35      7    80%
src\symnoesis\sq.py               34     18    47%
src\symnoesis\stability.py        17      6    65%
src\symnoesis\variables.py        27      3    89%
src\symnoesis\zones.py            34      3    91%
--------------------------------------------------
TOTAL                            487     56    89%
```
*Note:* Modules with low coverage include `sq.py` (47% - bootstrap CI untested), `evidence.py` (54%), `stability.py` (65%), and `net_effects.py` (80%).

### 3.3 Python Type Checking (`mypy --strict`)
**Command:** `uv run --directory packages/py mypy src tests`  
**Result:** **4 errors in 3 files** (Exit code 1).
```
src\symnoesis\net_effects.py:59: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
src\symnoesis\sq.py:33: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
src\symnoesis\sq.py:35: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
tests\unit\test_sanity.py:8: error: Module has no attribute "__version__"  [attr-defined]
```

### 3.4 Python Linting (`ruff check`)
**Command:** `uv run --directory packages/py ruff check .`  
**Result:** **45 errors** found across test and source files (Exit code 1).
- Unsorted/unformatted import blocks (`I001`).
- Unused imports in tests (`F401`).
- Redundant mode arguments in `open()` (`UP015`).

### 3.5 Python Code Formatting (`ruff format --check`)
**Command:** `uv run --directory packages/py ruff format --check .`  
**Result:** **3 files unformatted** (`src/symnoesis/config.py`, `src/symnoesis/zones.py`, `tests/unit/test_config.py`).

### 3.6 TypeScript Type Checking (`tsc --noEmit`)
**Command:** `pnpm -r run typecheck`  
**Result:** Exit code 0 (clean, but only checking 6-line stub `src/index.ts`).

### 3.7 TypeScript Tests (`vitest run`)
**Command:** `pnpm -r run test`  
**Result:** Exit code 0 (1 passed test, verifying version string).

### 3.8 Prettier Check (`prettier --check .`)
**Command:** `pnpm exec prettier --check .`  
**Result:** Code style issues found in 16 JSON schema files in `spec/schemas/`.

---

## 4. Gap Analysis Against Requirements R1 & R2

### 4.1 Requirement R1: Specification & Mathematical Reference Core (M1 & M3)

| Requirement Feature | Spec Section | Python Status | TypeScript Status | Gap Details |
| :--- | :--- | :--- | :--- | :--- |
| **Config Loader** | App. B | Implemented | Missing | TS lacks YAML/JSON config loader and type definitions |
| **Gray Code Bijections** | §4 | Bug in `gray_to_int` | Missing | Python has bit-fold bug (`gray_to_int(12) != 8`). TS missing entirely |
| **16x16 Grid & Coordinates** | §4 | Bug in `pixel_id_to_coord` | Missing | Python coordinate conversion fails due to Gray bug. TS missing entirely |
| **Normal CDF via erfc** | §2.3, §3 | Implemented | Missing | TS requires Cody's rational Chebyshev approximation ($< 10^{-9}$ of `ndtr`) |
| **Variable Scaling & Probs** | §2.3, §3 | Implemented | Missing | TS missing $p_i = \Phi((\mu_i - \theta_i) / \sigma_i)$ |
| **Mass Assignment** | §3 | Implemented | Missing | TS missing 256-cell mass distribution, pruning, modal pixel |
| **Net Effects (HNE, SNE)** | §5 | Implemented (mypy flaw) | Missing | TS missing HNE, SNE, operator-blind parasitism suppression |
| **Non-compensation Rule** | §6 | Implemented | Missing | TS missing $\text{SNE}' = \min(\text{SNE}, 0)$ when $\text{HNE} < 0$ |
| **Stability Factor & Override**| §6 | Implemented | Missing | TS missing $S$ calculation and $S_{\text{eff}}$ harm override |
| **Safety Gate Ceilings** | §7 | Implemented | Missing | TS missing CHI-1..7 evaluation and gate ceiling application |
| **Composite SQ** | §6 | Implemented (mypy flaw) | Missing | TS missing SQ calculation and clipping $[-100, 100]$ |
| **Symbiosis Classes** | §8 | Implemented | Missing | TS missing 9-cell matrix and operator-blind fallback |
| **Governance Zones** | §9 | Bug in `evaluate_zones` | Missing | Python has Z1 secondary tag bug. TS missing precedence & tags |
| **Golden Vectors** | App. A | 3/3 passing | 0/3 present | TS has no golden vector tests |
| **Data Contract Schemas** | §14 | Schemas drafted | Missing | Missing Pydantic models in Py; missing Zod models in TS; corrupted `"$schema"` keys |
| **Property Tests** | Blueprint | 0 tests | 0 tests | Hypothesis and `fast-check` suites both missing |

### 4.2 Requirement R2: Minimal Failure Cover & Longitudinal Diagnostics (M2 & M4)

| Requirement Feature | Spec Section | Python Status | TypeScript Status | Gap Details |
| :--- | :--- | :--- | :--- | :--- |
| **6561 Subcube Generation** | §11 | Missing | Missing | Candidate subcube enumeration of the 8-cube not implemented |
| **Purity & Coverage Metrics** | §11 | Missing | Missing | Purity $\pi(R)$, coverage $\text{cov}(R)$, harm mass $h(c)$ not implemented |
| **Exact MILP Optimization** | §11 | Missing | Missing | `scipy.optimize.milp` with HiGHS formulation not implemented |
| **Quine-McCluskey Strict Mode**| §11 | Missing | Missing | Boolean reduction matching `sympy.logic.boolalg.SOPform` not implemented |
| **Human-readable Rule Output**| §11 | Missing | Missing | Rule formatting not implemented |
| **Counterfactual Diagnostics** | §12 | Missing | Missing | Single-flip evaluation ($c \oplus v$) not implemented |
| **Pooled Ridge Model** | §12 | Missing | Missing | Ridge regression for unobserved neighbor states not implemented |
| **Dominant Failure Variable** | §12 | Missing | Missing | $\text{argmax}_v \Delta\text{SQ}_v$ identification not implemented |
| **Temporal Multi-Frame Engine**| §10 | Missing | Missing | Frames [1, 7, 28, 84, 182] trajectory engine not implemented |
| **MDC Thresholds & Drift Rule**| §10 | Missing | Missing | $\text{MDC} = 1.96 \cdot \sqrt{2} \cdot \text{SEM}$ and 2-interval drift rule not implemented |
| **K-Anonymity & DP Release** | §16 | Missing | Missing | $k_{\min} = 10$ suppression and DP Laplace/Gaussian engine not implemented |
| **Cryptographic RunManifest** | §14, §16 | Missing | Missing | Ed25519 signing and verification not implemented |

---

## 5. Architectural Recommendations for Implementation Agents

1. **Python Core Remediation (Immediate Priority):**
   - In `gray.py`: Fix `gray_to_int` to fold `n` iteratively:
     ```python
     def gray_to_int(g: int) -> int:
         if g < 0: raise ValueError(...)
         n = g
         shift = 1
         while shift < 32:
             n ^= (n >> shift)
             shift <<= 1
         return n
     ```
   - In `zones.py`: Allow Z1 to match regardless of `has_confirmed_chi` so that precedence puts Z7 as `primary` and Z1 into `secondary_tags`.
   - In `__init__.py`: Restore `__version__ = "0.1.0.dev0"`.
   - In `net_effects.py` and `sq.py`: Use direct `is not None` guard checks for `operator` and `gate_ceiling` to satisfy strict `mypy`.
   - Run `ruff check --fix` and `ruff format`.
2. **TypeScript Core Port (`@symnoesis/core`):**
   - Create modular source structure matching Python:
     `src/math/erfc.ts`, `src/config.ts`, `src/gray.ts`, `src/grid.ts`, `src/variables.ts`, `src/assign.ts`, `src/net_effects.ts`, `src/stability.ts`, `src/gates.ts`, `src/sq.ts`, `src/classes.ts`, `src/zones.ts`.
   - Implement Cody's rational Chebyshev approximation in `src/math/erfc.ts` to guarantee $< 10^{-9}$ error against `scipy.special.ndtr`.
   - Mirror all unit tests and golden vectors (`gv-sq-001`, `gv-sq-002`, `gv-sq-003`, `gray-code-16`, `grid-256-pixels`) into `packages/ts/tests/`.
3. **Requirement R2 Modules:**
   - Implement `packages/py/src/symnoesis/cover.py` using `scipy.optimize.milp` with HiGHS for exact MILP solving, verified against `sympy.logic.boolalg.SOPform`.
   - Implement `packages/py/src/symnoesis/counterfactual.py` and `packages/py/src/symnoesis/temporal.py`.
4. **Data Contracts & Shared Schemas:**
   - Fix corrupted `"": "https://json-schema.org/..."` to `"$schema": "https://json-schema.org/..."` across all 16 files in `spec/schemas/` and run `prettier --write`.
   - Generate Pydantic v2 models in Python and Zod schemas in TypeScript.
