# Handoff Report — Systems Tooling, Web Portals, and Release Engineering Survey

**Agent:** Systems Tooling and Web Explorer (`explorer_survey_systems_1`)  
**Date:** 2026-10-12  
**Target Recipient:** Orchestrator (`parent`, ID: `abfd9134-810e-49b4-885c-c4bd5beb1700`)  
**Type:** Hard Handoff (Investigation Complete)  
**Detailed Report:** `E:/Symnoesis/.agents/teamwork/explorer_survey_systems_1/analysis.md`  

---

## 1. Observation

Direct observations collected from the repository across tools and files:

1. **Verification Gate Failure:**
   - Command: `make verify` (and `make lint`)
   - Verbatim Output:
     ```text
     Found 45 errors.
     [*] 37 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
     make: *** [Makefile:40: lint] Error 1
     ```
   - Linter errors cataloged:
     - `ruff check`: 45 errors in `packages/py/tests/unit/` (e.g. `test_gray.py`, `test_grid.py`, `test_net_effects.py`, `test_variables.py`, `test_worked_examples.py`).
     - `mypy --strict`: 4 errors across 3 files:
       ```text
       src\symnoesis\net_effects.py:59: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
       src\symnoesis\sq.py:33: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
       src\symnoesis\sq.py:35: error: Argument 1 to "float" has incompatible type "float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
       tests\unit\test_sanity.py:8: error: Module has no attribute "__version__"  [attr-defined]
       ```
     - `prettier --check .`: 16 files in `spec/schemas/*.schema.json` formatted inconsistently.
     - `markdownlint-cli2`: 13 errors in `.agents/teamwork/sentinel/BRIEFING.md` because `.agents/` is not in `.markdownlintignore` or `.markdownlint-cli2.jsonc`.

2. **Test Suite Failures:**
   - Command: `make test`
   - Verbatim Output:
     ```text
     FAILED tests/unit/test_gates_and_zones.py::test_zones_precedence - AssertionError: assert 'Z1' in []
     FAILED tests/unit/test_gray.py::test_gray_golden_vector - assert 9 == 8 (where 9 = gray_to_int(12))
     FAILED tests/unit/test_grid.py::test_256_pixels_golden_vector - AssertionError: assert PixelCoord(col=9, row=0) == PixelCoord(col=8, row=0)
     FAILED tests/unit/test_sanity.py::test_package_metadata - AttributeError: module 'symnoesis' has no attribute '__version__'
     ======================== 4 failed, 18 passed in 6.42s =========================
     ```
   - In `packages/py/src/symnoesis/gray.py` lines 22–27:
     ```python
     def gray_to_int(g: int) -> int:
         ...
         n = g
         shift = 1
         while (g >> shift) > 0:
             n ^= g >> shift
             shift <<= 1
         return n
     ```
     Shifts `g` rather than `n`, producing `gray_to_int(12) == 9` instead of `8`.
   - In `packages/py/src/symnoesis/zones.py` line 59:
     ```python
     if sq is not None and sq >= config.zones.z1_min and not is_trajectory_negative and not has_confirmed_chi:
         matches.append("Z1")
     ```
     Excludes Z1 from matching when `has_confirmed_chi` is True, causing `secondary_tags` to omit `"Z1"`.

3. **Web Applications (`apps/web`):**
   - File listing: `list_dir(E:\Symnoesis\apps\web)` returns `Empty directory`.
   - No `sites/` directory exists. Per `12_REPO_BLUEPRINT.md` §1 and `ADR-0014`, `apps/web` is the sole web application directory.
   - Pnpm workspace (`pnpm-workspace.yaml`) defines `packages/*` and `apps/*`, but pnpm detects only 2 packages (root and `packages/ts`) because `apps/web` lacks `package.json`.

4. **Makefile Target Stubs:**
   - In `Makefile` lines 60–117: targets `mutation`, `vectors`, `vectors-check`, `gen`, `e2e`, `a11y`, `perf`, `links`, `repro`, `docs`, `site` are echo statements that do not execute tests or builds.
   - Line 112: `verify: setup lint test build` only executes 4 targets, skipping 9 required gates from `CLAUDE.md` §3.

5. **Missing Subdirectories & Tooling:**
   - `spec/domains/`: Empty directory (missing 4 YAML domain files).
   - `spec/instruments/`: Empty directory (missing instrument definitions and licenses).
   - `spec/modules/`: Empty directory (missing 6 protocol markdown specs).
   - `spec/portal/`: Empty directory (missing `portal-model.v0.1.json`).
   - `scripts/`: Empty directory (missing `spec_coverage.py`, `gen_vectors.py`, `gen_types.sh`, `check_refs.py`).
   - `tools/`: Lacks `check-contrast.ts` and `cvd-sim.ts`. Neither `vale` nor `lychee` binaries exist on system PATH.
   - `data/fixtures/` and `data/releases/`: Empty directories.
   - `packages/ts/src/`: Contains only `index.ts` with `export const VERSION = "0.1.0-dev.0"`. Lacks all mathematical and projection logic.
   - `packages/py/src/symnoesis/`: Lacks `signing.py`, `cli.py`, `telemetry/`, `modules/`, `judges/`, `simulator/`, `providers/`, `reports/`.

---

## 2. Logic Chain

1. **Gate Verification Breakdown (Obs. 1, 2, 4):**
   - The user request requires that `make verify` pass clean with zero errors across all targets.
   - Observation 1 shows `make lint` fails with 45 ruff errors, 4 mypy errors, 16 prettier schema errors, and markdownlint errors on `.agents/`.
   - Observation 2 demonstrates that the test suite fails on 4 test cases due to an algebraic bug in `gray_to_int`, an over-constrained check in `zones.py`, and missing metadata in `__init__.py`.
   - Observation 4 shows `make verify` currently runs only 4 targets (`setup lint test build`) rather than the full gate suite, and 10 gate targets in `Makefile` are non-functional echo stubs.
   - Therefore, the gate runner is broken both in execution (lint and test fail) and in completeness (9 gates not implemented).

2. **Web Portal Architecture & Readiness (Obs. 3):**
   - Requirement R4 and Blueprint require an Interactive Map Portal (16×16 Gray map, adaptive resolution, single-flip neighbors, 4-step questionnaire flow, WCAG 2.1 AA) and an Astro static research website.
   - Observation 3 shows `apps/web/` is completely uninitialized with zero files.
   - Therefore, the entire web application layer—including Astro configuration, Svelte 5 interactive islands, custom CSS token system (`tokens.css`), claims registry (`claims.yaml`), Pagefind search, and E2E/a11y tests—must be created from scratch.

3. **Tooling & Cryptographic Manifests (Obs. 5):**
   - Requirement R4 requires Card generation, Index tooling, and cryptographic run manifests (Ed25519 signing and hash integrity).
   - Observation 5 confirms that while the schemas (`run_manifest.schema.json`, `symnoesis_card.schema.json`) exist, the Python implementation files (`symnoesis.signing`, `symnoesis.reports.card`, `symnoesis.reports.index`, `symnoesis.cli`) do not exist.
   - Therefore, manifest signing, card rendering (JSON/HTML/PDF), statistical index tiering ($P(i > j) \ge 0.95$), and the Typer CLI must be implemented.

4. **Synthetic Pipeline Gaps (Obs. 5):**
   - Requirement R3 mandates synthetic persona and dyad generation across 4 domains (`learning`, `coding`, `health-information`, `advice-companionship`) adhering to k-anonymity ($k_{\text{min}} = 10$) and differential privacy ($\varepsilon = 1.0$).
   - Observation 5 reveals that `spec/domains/`, `spec/instruments/`, `spec/modules/`, `data/fixtures/`, and `packages/py/src/symnoesis/modules/`, `judges/`, `simulator/`, `telemetry/` are entirely empty or missing.
   - Therefore, the entire synthetic evidence generation pipeline, judge calibration harness (Krippendorff's $\alpha$), telemetry extraction, and privacy filters must be developed.

5. **Governance & Documentation Status (Obs. 5):**
   - Requirement R5 mandates governance documentation, verified citations, and release engineering.
   - Observation 5 confirms that the 10 core governance policies in `docs/governance/` exist and are appropriately labeled `Proposed`.
   - However, the whitepaper (`research/whitepaper/`), Diátaxis user guides (`docs/guides/`), research templates (`research/preregistrations/TEMPLATE.md`), and automated reference verification scripts (`scripts/check_refs.py`) are absent, and `research/references.bib` contains placeholder author strings that must be resolved.

---

## 3. Caveats

1. **Read-Only Constraint:** In accordance with explorer agent constraints, no code modifications were applied to fix the identified bugs in `gray.py`, `zones.py`, or tests. Concrete patch snippets are provided in the recommendations.
2. **Missing External Binaries:** `vale` and `lychee` are specified in gate commands but are not currently installed on the host Windows machine. In CI (Linux), they can be installed via package managers or GitHub Actions. Locally, fallback scripts or conditional execution will be required.
3. **Windows Shell Portability:** The Makefile's `clean` target relies on Unix `rm -rf`. While GNU Make 4.4.1 is installed and running, commands invoking Unix shell utilities will fail under native PowerShell unless wrapped or using Windows-compatible commands.

---

## 4. Conclusion

The Symnoesis repository has a solid theoretical and architectural foundation (`spec/SPEC.md`, JSON schemas, golden vectors, ADRs, governance scaffolds). However, **Requirements R3, R4, and R5 are currently 0% implemented**, and the active test/lint gates in Milestone 0 are currently broken due to 4 specific code/test defects and formatting issues.

### Priority Action Items for Implementation:
1. **Fix Active Gate Defects:**
   - Correct Gray code inversion loop in `packages/py/src/symnoesis/gray.py`: change `n ^= g >> shift` to `n ^= n >> shift`.
   - Resolve Z1 matching logic in `packages/py/src/symnoesis/zones.py`.
   - Add `__version__ = "0.1.0.dev0"` to `packages/py/src/symnoesis/__init__.py`.
   - Resolve `float | None` type incompatibilities in `net_effects.py` and `sq.py`.
   - Auto-fix Ruff and Prettier formatting; add `.agents` to Markdownlint ignore lists.
2. **Initialize Web Monorepo Package (`apps/web`):**
   - Create `apps/web/package.json` with Astro, Svelte 5, and workspace dependency `@symnoesis/core`.
   - Implement design tokens in `tokens.css` and `tokens.json`.
   - Author 16×16 Gray Map component, Neighbors panel, and 4-step client-side portal flow.
   - Create `apps/web/src/content/claims.yaml` registry.
3. **Port `@symnoesis/core` to TypeScript:**
   - Implement core math, Cody `erfc`, grid coordinates, assignment, and portal projection.
   - Verify parity against Python golden vectors within $10^{-9}$ tolerance.
4. **Implement Synthetic Evidence Pipeline (R3) & Tooling (R4):**
   - Implement `spec/domains/*.yaml`, `spec/instruments/*.yaml`, `spec/modules/*.md`.
   - Build `symnoesis.signing` (Ed25519), `simulator`, `judges` (Krippendorff $\alpha$), `telemetry` (k-anonymity & DP), and reports (`card.py`, `index.py`).
   - Wire Typer CLI commands in `symnoesis.cli`.
5. **Finalize Governance & Release Engineering (R5):**
   - Author whitepaper draft in `research/whitepaper/`.
   - Author Diátaxis documentation in `docs/guides/`.
   - Wire all 10 gate targets in `Makefile` and configure remaining GitHub Actions workflows.

---

## 5. Verification Method

To independently reproduce all observations and verify findings:

1. **Verify Setup:**
   ```powershell
   make setup
   ```
   (Should succeed with exit code 0).

2. **Verify Lint Failures:**
   ```powershell
   cd E:\Symnoesis
   uv run --directory packages/py ruff check .
   uv run --directory packages/py mypy src tests
   pnpm exec prettier --check .
   pnpm exec markdownlint-cli2
   ```
   (Observe 45 ruff errors, 4 mypy errors, 16 prettier schema warnings, and 13 markdownlint errors).

3. **Verify Test Failures & Gray Bug:**
   ```powershell
   uv run --directory packages/py pytest tests/unit/test_gray.py -k test_gray_golden_vector
   ```
   (Fails with `assert 9 == 8` where `9 = gray_to_int(12)`).

4. **Verify Web App Directory:**
   ```powershell
   Get-ChildItem -Path E:\Symnoesis\apps\web
   ```
   (Observe zero files returned).

5. **Verify Gate Incompleteness:**
   Inspect `E:/Symnoesis/Makefile` lines 60–117 to observe echo stubs for `mutation`, `vectors-check`, `e2e`, `a11y`, `perf`, `links`, `repro`, `site`, and `verify`.
