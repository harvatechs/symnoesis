# Handoff Report — Python & TypeScript Core Investigation (R1 & R2)

**Agent:** `explorer_survey_pyts_1`  
**Working Directory:** `E:/Symnoesis/.agents/teamwork/explorer_survey_pyts_1`  
**Milestone:** Survey & Gap Analysis (M1–M4)  
**Detailed Report:** `E:/Symnoesis/.agents/teamwork/explorer_survey_pyts_1/analysis.md`

---

## 1. Observation

1. **Python Source Inventory:**
   - 13 source files exist in `packages/py/src/symnoesis/`: `__init__.py`, `config.py`, `gray.py`, `grid.py`, `variables.py`, `assign.py`, `net_effects.py`, `stability.py`, `gates.py`, `sq.py`, `classes.py`, `zones.py`, `evidence.py`.
   - `packages/py/pyproject.toml` defines entrypoint `symnoesis = "symnoesis.cli:app"`, but `src/symnoesis/cli.py` does not exist.
   - Requirement R2 modules (`cover.py`, `counterfactual.py`, `temporal.py`, `privacy.py`, `signing.py`) do not exist.
2. **Python Test Failures:**
   - Ran `uv run --directory packages/py pytest`: 22 collected, 18 passed, 4 failed.
     - `tests/unit/test_sanity.py:8`: `AttributeError: module 'symnoesis' has no attribute '__version__'`.
     - `tests/unit/test_gray.py:31`: `assert 9 == 8` where `9 = gray_to_int(12)`.
     - `tests/unit/test_grid.py:36`: `AssertionError: assert PixelCoord(col=9, row=0) == PixelCoord(col=8, row=0)`.
     - `tests/unit/test_gates_and_zones.py:47`: `AssertionError: assert 'Z1' in []` where `[] = ZoneResult(primary='Z7', secondary_tags=[]).secondary_tags`.
   - Test coverage is 89% (below 95% threshold); `sq.py` is at 47%, `evidence.py` at 54%, `stability.py` at 65%.
   - `packages/py/tests/property/` is empty (0 Hypothesis tests).
3. **Python Static Analysis Failures:**
   - Ran `uv run --directory packages/py mypy src tests`: 4 errors in 3 files.
     - `src/symnoesis/net_effects.py:59`: `Argument 1 to "float" has incompatible type "float | None"`
     - `src/symnoesis/sq.py:33`: `Argument 1 to "float" has incompatible type "float | None"`
     - `src/symnoesis/sq.py:35`: `Argument 1 to "float" has incompatible type "float | None"`
     - `tests/unit/test_sanity.py:8`: `Module has no attribute "__version__"`
   - Ran `uv run --directory packages/py ruff check .`: 45 linting errors (imports, unused variables, UP015).
   - Ran `uv run --directory packages/py ruff format --check .`: 3 files need formatting (`config.py`, `zones.py`, `test_config.py`).
4. **TypeScript Source & Test Status:**
   - `packages/ts/src/index.ts` contains only `export const VERSION = "0.1.0-dev.0";`.
   - `packages/ts/tests/sanity.test.ts` contains 1 test verifying `VERSION`.
   - Core mathematical functions (Gray code, grid coordinates, normal CDF / erfc, variable probabilities, mass assignment, net effects, stability factor, safety gates, SQ, classes, zones) are 100% missing in TypeScript.
   - Ran `pnpm -r run typecheck`: clean (0 errors), but only checks the 6-line stub.
   - Ran `pnpm -r run test`: 1 passed, 0 math tests.
5. **Shared Schemas & Vectors (`spec/`):**
   - `spec/config/symn-01.v0.1.yaml` matches SPEC Appendix B.
   - All 16 JSON schema files in `spec/schemas/` have corrupt headers: `"": "https://json-schema.org/draft/2020-12/schema"` where property key `"$schema"` was erased to `""`.
   - `pnpm exec prettier --check .` flagged all 16 JSON schemas in `spec/schemas/`.
   - Golden vectors `gv-sq-001.json`, `gv-sq-002.json`, `gv-sq-003.json` pass in Python unit tests.

---

## 2. Logic Chain

1. **Gray Code & Grid Failure Chain:**
   - Observation 2 shows `gray_to_int(12)` returns 9 instead of 8 in `test_gray.py`.
   - In `gray.py` line 25: `n ^= g >> shift` inside `while (g >> shift) > 0:` uses the input integer `g` in every shift rather than the accumulated value `n`. For $g = 12 = 1100_2$, with shift 1, $n = 12 \oplus 6 = 10$; with shift 2, $n = 10 \oplus (12 \gg 2) = 10 \oplus 3 = 9$.
   - Folding $n$ iteratively via $n \oplus (n \gg 1) \oplus (n \gg 2) \oplus (n \gg 4)$ yields $12 \oplus 6 = 10$, $10 \oplus 2 = 8$, $8 \oplus 0 = 8$, which is the exact inverse.
   - `grid.py:pixel_id_to_coord` depends directly on `gray_to_int(h_code)`. For column 8 ($H=1100_2$), it computes `col = 9` instead of 8, causing `test_grid.py:36` to fail.
2. **Zone Precedence Failure Chain:**
   - In `zones.py` line 59: `if sq is not None and sq >= config.zones.z1_min and not is_trajectory_negative and not has_confirmed_chi: matches.append("Z1")`.
   - In `test_gates_and_zones.py:45`: `evaluate_zones(75.0, ..., has_confirmed_chi=True)`. Because `not has_confirmed_chi` is in the `if` guard, `"Z1"` is never appended to `matches`.
   - SPEC §9 states precedence determines the `primary` zone (here Z7), while all matching conditions must be listed in `secondary_tags`. Because Z1 was excluded from `matches`, `secondary_tags` is empty `[]`, failing line 47.
3. **Mypy Strict Failure Chain:**
   - In `net_effects.py:59`, `operator` is typed `float | None`. In `sq.py:33, 35`, `gate_ceiling` is typed `float | None`.
   - Conditionals checked boolean flags (`operator_blind`, `gate_triggered`) instead of `is not None` guards. Under `mypy --strict`, type narrowing does not cross variable boundaries, resulting in `Argument 1 to "float" has incompatible type "float | None"`.
4. **TypeScript Parity Deficit Chain:**
   - Requirement R1 requires bit-for-bit parity and $< 10^{-6}$ agreement between Python and TypeScript on golden vectors.
   - Because `packages/ts/src/index.ts` contains only a version export, TypeScript currently satisfies 0% of R1 math requirements.
5. **Requirement R2 Absence Chain:**
   - Requirement R2 mandates Minimal Failure Cover (MILP via `scipy.optimize.milp` with HiGHS and Quine-McCluskey strict mode matching `sympy.logic.boolalg.SOPform`), counterfactual diagnostics, and multi-frame temporal engine.
   - Inspection of `packages/py/src/symnoesis/` reveals none of `cover.py`, `counterfactual.py`, or `temporal.py` exist, nor do any associated tests or fixtures.

---

## 3. Caveats

- **Out of Scope:** This investigation was strictly read-only per agent constraints; no source fixes were applied.
- **R3–R5 Modules:** Evidence generator, Astro website (`apps/web`), and release engineering were outside the scope of this survey.
- **Assumptions:** We assumed the 16 schemas in `spec/schemas/` are intended to be standard JSON Schema 2020-12 drafts with `"$schema"` keys.

---

## 4. Conclusion

1. **Python Core Math (M1):** 80% implemented, but blocked by 3 clear defects (Gray inversion algorithm bug, zone secondary tag omission, missing package `__version__`), 4 mypy type narrowing errors, and 45 ruff lint errors. Test coverage is 89% (target $\ge 95\%$), and property tests are completely missing.
2. **TypeScript Core Math (M3):** 0% implemented. Needs complete porting of the math core, including Cody's rational Chebyshev `erfc` implementation, Gray/grid bijections, net effects, SQ, zones, and Vitest golden vector test suites.
3. **MFC & Diagnostics (M2, M4):** 0% implemented. `cover.py` (MILP + Quine-McCluskey), `counterfactual.py` (ridge regression), and `temporal.py` (MDC + trajectories) need to be authored from scratch in Python.
4. **Data Contracts:** All 16 schemas in `spec/schemas/` require header fix (`""` $\to$ `"$schema"`) and code-generation into Pydantic v2 (Python) and Zod (TypeScript).

---

## 5. Verification Method

To independently verify all findings in this report, execute the following commands in `E:/Symnoesis`:

1. **Verify Python test failures:**
   ```powershell
   uv run --directory packages/py pytest
   ```
   *Expected output:* 4 failures (`test_sanity`, `test_gray`, `test_grid`, `test_gates_and_zones`).
2. **Verify Python type errors:**
   ```powershell
   uv run --directory packages/py mypy src tests
   ```
   *Expected output:* 4 errors in `net_effects.py`, `sq.py`, and `test_sanity.py`.
3. **Verify Python lint errors:**
   ```powershell
   uv run --directory packages/py ruff check .
   ```
   *Expected output:* 45 errors.
4. **Verify TypeScript emptiness:**
   ```powershell
   Get-Content packages/ts/src/index.ts
   ```
   *Expected output:* 6 lines containing only `export const VERSION = "0.1.0-dev.0";`.
5. **Verify schema header defect:**
   ```powershell
   Select-String -Path spec/schemas/*.schema.json -Pattern '""'
   ```
   *Expected output:* Match on line 2 of all 16 schema files.
