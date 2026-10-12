# Systems, Tooling, Web Portals, and Release Engineering Survey Report

**Author:** Systems Tooling and Web Explorer (`explorer_survey_systems_1`)  
**Date:** 2026-10-12  
**Repository:** `E:/Symnoesis`  
**Reference Specification:** `spec/SPEC.md` (SYMN-01 v0.1.0)  
**Blueprint:** `docs/agent/12_REPO_BLUEPRINT.md`  
**Parent Orchestrator:** `abfd9134-810e-49b4-885c-c4bd5beb1700`  

---

## 1. Executive Summary

A comprehensive, read-only baseline investigation of the Symnoesis repository tooling, web applications, evidence pipelines, governance documents, and verification targets was conducted.

### Core Findings
1. **Repository & Blueprint Baseline:** The repository foundation initiated in Milestone 0 is partially in place (root metadata, schemas, initial Python core files). However, major subsystems remain completely uninitialized: `apps/web` is an empty folder, `packages/ts` is a one-line version stub, and essential subdirectories (`spec/domains/`, `spec/instruments/`, `spec/modules/`, `spec/portal/`, `scripts/`, `data/fixtures/`, `data/releases/`) contain no files.
2. **Web Applications (`apps/web`):** The repository defines no `sites/` directory; per `12_REPO_BLUEPRINT.md` and `ADR-0014`, the canonical static research website and Interactive Map Portal belong in `apps/web`. Currently, `apps/web` contains zero files—no `package.json`, no Astro configuration (`astro.config.mjs`), no Svelte 5 islands, no CSS tokens (`tokens.css`), no Pagefind integration, and no claims registry (`claims.yaml`).
3. **Tooling & Cryptographic Manifests:** The schemas for `RunManifest` and `SymnoesisCard` are committed, but their runtime implementations (`symnoesis.signing` for Ed25519 signing/verification, `symnoesis.reports.card` for HTML/PDF rendering, `symnoesis.reports.index` for statistical tiering, and `symnoesis.cli` for Typer CLI commands) do not exist. `scripts/` contains no code generator or verification scripts.
4. **Synthetic Pipeline (R3 / M5):** Completely absent. There are no domain profiles, no instrument definitions, no protocol specifications, no persona simulator, no telemetry extraction or DP/k-anonymity filter, and no test fixtures.
5. **Governance Documentation (R5 / M9-M10):** Root policies and 10 policy drafts in `docs/governance/` are present and correctly marked `Proposed`. The whitepaper (`research/whitepaper/`), Diátaxis user guides (`docs/guides/`), research templates (`research/preregistrations/`), and reference verifier are missing.
6. **Verification Targets & `make verify`:** `make verify` **fails**. Specifically:
   - `make setup` passes.
   - `make lint` fails with 45 `ruff` errors, 4 `mypy` strict type errors, 16 `prettier` schema formatting issues, and `markdownlint-cli2` failures on `.agents/` markdown files. Tools like `eslint`, `stylelint`, `vale`, and `lychee` are omitted or missing installed binaries.
   - `make test` fails with 4 test failures: a mathematical bug in inverse Gray code calculation (`gray_to_int(12) == 9` instead of `8`), a secondary tags assertion failure in `test_zones_precedence`, grid coordinate mapping failures resulting from the Gray bug, and missing `__version__` in `symnoesis`.
   - `make build` partially builds wheels and TS types, but does not build the Astro website.
   - 10 gate targets in `Makefile` (`mutation`, `vectors`, `vectors-check`, `gen`, `e2e`, `a11y`, `perf`, `links`, `repro`, `docs`, `site`) are non-functional echo stubs.

---

## 2. Repository Structure & Toolchain Lockfiles vs. Blueprint

A systematic audit was performed comparing the current repository against `docs/agent/12_REPO_BLUEPRINT.md` §1:

| Blueprint Path | Current Status | Notes / Discrepancies |
|---|---|---|
| `README.md` | Present | Needs quick-start validation once CLI and fixtures exist |
| `CLAUDE.md`, `AGENTS.md` | Present | Normative agent rules in place |
| `LICENSE`, `LICENSE-DOCS` | Present | Apache-2.0 and CC BY 4.0 |
| `CITATION.cff` | Present | CFF 1.2.0 metadata; needs validation against validator |
| `CHANGELOG.md`, `ROADMAP.md` | Present | Present; roadmap honest |
| `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `SUPPORT.md`, `MAINTAINERS.md`, `TRADEMARK.md` | Present | Scaffolding complete; interim maintainers noted |
| `ORG_FACTS.yaml` | Present | All unverified fields set to `null` / `verified: false` as required |
| `Makefile` | Present | 10 targets are echo stubs; `verify` does not run all gates |
| `.editorconfig`, `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml` | Present | Configured |
| `.github/workflows/` | Partial (4 of 8) | Present: `ci.yml`, `codeql.yml`, `pages.yml`, `scorecard.yml`. **Missing**: `mutation.yml`, `security.yml`, `release.yml`, `repro.yml`. |
| `.github/ISSUE_TEMPLATE/` | Empty dir | **Missing**: bug, spec-question, research-proposal, accessibility templates |
| `.github/PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`, `dependabot.yml` | **Missing** | Not created |
| `spec/SPEC.md`, `spec/config/symn-01.v0.1.yaml` | Present | Normative spec and YAML config in place |
| `spec/CHANGELOG.md` | **Missing** | Spec revision history not created |
| `spec/schemas/*.schema.json` | Present (16 files) | All 16 entity schemas committed; need Prettier formatting |
| `spec/vectors/*.json` | Present (5 files) | `gray-code-16.json`, `grid-256-pixels.json`, `gv-sq-001..003.json` |
| `spec/domains/*.yaml` | Empty dir | **Missing**: `learning.yaml`, `coding.yaml`, `health-information.yaml`, `advice-companionship.yaml` |
| `spec/instruments/*.yaml` | Empty dir | **Missing**: instrument schemas, item definitions, license status |
| `spec/portal/portal-model.v0.1.json` | Empty dir | **Missing**: E0 item-to-variable weights model |
| `spec/modules/*.md` | Empty dir | **Missing**: SYM-COG, SYM-EPI, SYM-AFF, SYM-SAF, SYM-MCH, SYM-REC protocol docs |
| `rfcs/0000-template.md` | Present | RFC template committed |
| `packages/py/` | Present | Python 3.12, `pyproject.toml`, `uv.lock`. Missing modules (temporal, cover, counterfactual, telemetry, modules, simulator, reports, signing, cli) |
| `packages/ts/` | Present | `package.json`, `tsconfig.json`. Source has only `index.ts` stub. Missing `README.md`, core math, generated types/config |
| `apps/web/` | Empty dir | **Missing**: Astro static site, Svelte islands, components, pages, tokens, tests |
| `data/fixtures/` | Empty dir | **Missing**: synthetic fixture datasets (e.g., `Fixture-A (scripted)`) |
| `data/releases/` | Empty dir | **Missing**: run manifests, maps, covers, cards, hashes |
| `docs/agent/` | Present (15 files) | Complete build pack |
| `docs/adr/` | Present (22 files) | Seed ADRs committed |
| `docs/design/plan.md` | Empty dir | **Missing**: design plan and self-review |
| `docs/guides/` | Empty dir | **Missing**: Diátaxis tutorials/, how-to/, reference/, explanation/ |
| `docs/governance/` | Present (10 files) | 10 policy drafts marked `Proposed` |
| `docs/build-log/` | Present (3 files) | `00-understanding.md`, `01-m0-foundation.md`, `OPEN_QUESTIONS.md` |
| `research/LOG.md`, `prior-art.md`, `references.bib` | Present | References present; need DOI verification |
| `research/questions.md`, `preregistrations/TEMPLATE.md`, `protocols/` | Empty / Missing | Research templates not created |
| `research/whitepaper/` | **Missing** | Whitepaper source not created |
| `scripts/` | Empty dir | **Missing**: `spec_coverage.py`, `gen_vectors.py`, `gen_types.sh`, `check_refs.py` |
| `tools/` | Partial (2 of 4) | Present: `lychee.toml`, `tools/vale/Symnoesis/BannedWords.yml`. **Missing**: `check-contrast.ts`, `cvd-sim.ts` |
| `docker/api.Dockerfile` | Empty dir | Optional REST API container not created |

### Toolchain Lockfiles Analysis
- **Python:** Managed with `uv 0.11.33` via `packages/py/pyproject.toml` and `packages/py/uv.lock` (267 KB). Pinned runtime dependencies include `pydantic>=2.7.0`, `pyyaml>=6.0`, `numpy>=1.26.0`, `scipy>=1.12.0`, `cryptography>=42.0.0`, `typer>=0.12.0`, `structlog>=24.1.0`. Dev dependencies include `pytest`, `pytest-cov`, `hypothesis`, `ruff`, `mypy`, `sympy`, `codespell`.
- **Node.js / Monorepo:** Managed with `pnpm 9.15.9` via root `package.json`, `pnpm-workspace.yaml`, and `pnpm-lock.yaml` (57 KB).
  - Workspace currently tracks `packages/ts` and `apps/*`. Because `apps/web` has no `package.json`, pnpm recognizes only 2 workspace projects (root + `@symnoesis/core`).
  - `@symnoesis/core` (`packages/ts/package.json`) dependencies: `zod ^3.23.8`; devDependencies: `fast-check ^3.21.0`, `typescript ^5.5.4`, `vitest ^2.0.5`.

---

## 3. Web Applications & Portals

### Architectural Requirements vs. Current State
Per `03_ARCHITECTURE.md` §3 & §7, `05_DESIGN_RULES.md`, `07_UX_RULES.md`, and `ADR-0014`:
- **Repository Location:** The web application resides strictly at `apps/web/`. There is no `sites/` directory.
- **Current State:** `apps/web/` is completely empty.

### Framework & Dependency Stack Needed
1. **Astro Static Site Generator:** `astro` (^4.x / ^5.x) configured for static output (`output: 'static'`) deployable to GitHub Pages.
2. **Interactive Islands:** `@astrojs/svelte` and `svelte` (^5.x) for the interactive 16×16 Gray map, frame scrubber, and the Interactive Map Portal questionnaire.
3. **Core Math Integration:** Workspace dependency `@symnoesis/core: "workspace:*"` supplying browser-side coordinate mapping, Cody `erfc`, probabilistic assignment, SQ, classes, and zones with zero external network dependencies.
4. **Search:** `pagefind` for static, client-side, zero-telemetry search index generation.
5. **Color Science:** `culori` for OKLab diverging SQ gradient calculations and CVD simulations.
6. **Data Validation:** `zod` validating all release artifacts at site build time.
7. **Math Formatting:** Build-time `KaTeX` rendering (no client-side KaTeX scripts).
8. **Typography:** Self-hosted Fontsource packages:
   - `@fontsource-variable/inter`
   - `@fontsource-variable/source-serif-4`
   - `@fontsource/jetbrains-mono`

### Information Architecture & Required Routes
Per `07_UX_RULES.md` §1:
1. `/`: Landing page featuring display statement, the memorable 16×16 live SVG Symnoesis Map with hero diagonal wave animation (≤ 900 ms), and evidence badge.
2. `/idea/`: Conceptual explanation of the Dyadic State, etymology (*noēsis*), two-sided outcomes.
3. `/map/`: Interactive Map Explorer with domain selector, 5-stop frame scrubber (Day 1, W1, W4, W12, W26), resolution switching (16×16, 8×8, 4×4), Minimal Failure Cover overlay, cell popovers, and 8 single-flip neighbors panel.
4. `/portal/`: Interactive Map Portal 4-step questionnaire flow:
   - Step 1: Domain and frequency.
   - Step 2: 12–16 items across Agency (H1), Capability (H2), Epistemic habits (H3), Wellbeing/reliance (H4), with 5-point scales and "Prefer not to say".
   - Step 3: AI system choice (Card or archetype: `agreeable-engagement-tuned`, `candid-and-bounded`, `unknown`).
   - Step 4: Result view: modal pixel, probability distribution halo, zone probabilities, top 3 single-flip experiments, non-diagnostic microcopy, E0 banner, zero server telemetry.
5. `/index/`: Symnoesis Index methodology preview (Edition 0) with statistical tiering ($P(i > j) \ge 0.95$), critical-event counts, and fictional fixture systems.
6. `/research/`: Research log, prior-art table, reading list, whitepaper link, glossary, citation snippets.
7. `/method/` (`/spec/`): Normative specification rendered as accessible HTML.
8. `/docs/`: Diátaxis user documentation (Tutorials, How-to, Reference, Explanation).
9. `/governance/`: Charter, SAB, Ethics, Disclosure, COI, Funding, Data policy, Privacy, Zones.
10. `/about/`, `/privacy/`, `/accessibility/`, `/cite/`, `/404/`.

### Design System & CSS Rules
- Pure hand-written CSS with `@layer reset, tokens, base, layout, components, pages`.
- Tokens defined in `apps/web/src/styles/tokens.css` and mirrored in `tokens.json`:
  - `--paper`, `--surface`, `--line`, `--ink`, `--ink-2`, `--ink-3`, `--accent` (`#2B4EDB` light / `#8EA2FF` dark).
  - Diverging SQ data scale (OKLab interpolated, magnitude encoded by lightness, sign encoded by hue + glyph).
- Strict bans: No Tailwind, UnoCSS, Bootstrap, or component libraries. No marketing superlatives. No stock images, 3D renders, or AI illustrations.

### Claims Registry (`apps/web/src/content/claims.yaml`)
Per `12_REPO_BLUEPRINT.md` §3 and `06_CONTENT_RULES.md` §2, every claim displayed across the site must resolve against `claims.yaml` (mapping `id`, `text`, `basis`, `ref`, `tier`). The site build must fail if an unmapped claim ID is rendered.

---

## 4. Tooling & Cryptographic Pipelines

### 1. Symnoesis Card Generation Tooling (M6)
- **Specification:** SPEC §13–§14; schema in `spec/schemas/symnoesis_card.schema.json`.
- **Requirements:**
  - Build-time generation from verified artifacts only (no hand-edited numbers).
  - Output formats: JSON, accessible HTML, and tagged accessible PDF.
  - Required content: card ID, system ID, domain, spec version, composite evidence tier, overall SQ with 95% CI, zone distribution, gate status, linked run manifest, and explicit limitations section ("What this does not show").
  - Implementation needed in `packages/py/src/symnoesis/reports/card.py`.

### 2. Symnoesis Index Pipeline Tooling (M6)
- **Specification:** SPEC §13–§14; ADR-0009.
- **Requirements:**
  - Aggregates dyadic SQ across systems with bootstrap confidence intervals.
  - Generates rank-probability matrix.
  - Implements statistical tiering: two systems are grouped in the same tier unless $P(i \text{ is better than } j) \ge 0.95$.
  - Critical-event reporting: any system with a confirmed Critical-Harm Indicator (CHI-1..7) event is prominently flagged and excluded from the top tier.
  - Implementation needed in `packages/py/src/symnoesis/reports/index.py`.

### 3. Cryptographic Run Manifest Tooling (M4)
- **Specification:** SPEC §14 & §16; schema in `spec/schemas/run_manifest.schema.json`.
- **Integrity Chain:**
  - `manifest_id` (UUID / deterministic hash).
  - `spec_version`: Pinned normative spec version string (e.g., `"0.1.0"`).
  - `config_hash`: Canonical SHA-256 hash of `spec/config/symn-01.v0.1.yaml` (sorted keys, normalized floats).
  - `code_git_sha`: Commit SHA of code creating the artifact.
  - `dependency_lock_hash`: SHA-256 of combined `packages/py/uv.lock` and `pnpm-lock.yaml`.
  - `judge_models`: Array of pinned judge model IDs and versions.
  - `random_seeds`: Dictionary of explicit seeds for all stochastic operations.
  - `dataset_hashes`: Mapping of input feature filenames to SHA-256 hashes.
  - `signature_ed25519`: Hex-encoded Ed25519 digital signature of the canonical JSON bytes.
- **Implementation Status:** Missing. Needs implementation in `packages/py/src/symnoesis/signing.py` using `cryptography.hazmat.primitives.asymmetric.ed25519`.

### 4. Scripts Tooling (`scripts/`)
Per Blueprint §1:
- `scripts/spec_coverage.py`: Parser checking that every normative statement in `spec/SPEC.md` has at least one test tagged `# spec: §X` or `// spec: §X`.
- `scripts/gen_vectors.py`: Deterministic generator producing `spec/vectors/*.json`.
- `scripts/gen_types.sh` / `.py`: Automated generator producing Pydantic models in Python and Zod / TypeScript types in TS from `spec/schemas/*.schema.json`.
- `scripts/check_refs.py`: Automated verifier resolving DOIs/URLs and verifying metadata in `research/references.bib`.

### 5. CLI Tooling (`symnoesis.cli`)
Declared in `packages/py/pyproject.toml` lines 56-57 (`[project.scripts] symnoesis = "symnoesis.cli:app"`), but `cli.py` does not exist. Commands required:
`symnoesis validate | map | cover | card | sweep | judge-calibrate | index | spec-check | repro | vectors`.

---

## 5. Synthetic Evidence Pipeline (Requirement R3 / Milestone M5)

### Scope and Architecture
Requirement R3 mandates implementing the synthetic persona and dyad generation pipeline across the 4 domains (`learning`, `coding`, `health-information`, `advice-companionship`) producing E1 synthetic data adhering to data contracts, k-anonymity ($k_{\text{min}} = 10$), and differential privacy ($\varepsilon = 1.0$).

### Component Gap Breakdown
1. **Domain Configurations (`spec/domains/`):**
   - Must contain: `learning.yaml`, `coding.yaml`, `health-information.yaml`, `advice-companionship.yaml`.
   - Each file defines: primary task distributions, typical interaction rhythms, domain-specific noninferiority margins, and high-risk trigger boundaries. Currently empty.
2. **Instrument Specifications (`spec/instruments/`):**
   - Must contain verified scales and task definitions with license statuses:
     - SYM-COG: matched tasks, AI-off probes, decision-ownership audit.
     - SYM-EPI: sycophancy stance-varied twin battery, calibration test set.
     - SYM-AFF: dependence indicator definitions, licensed wellbeing scales (WHO-5, PHQ-9, GAD-7, CBI).
     - SYM-SAF: abstract benign-proxy risk scenario tokens.
     - SYM-MCH: canary injection strings, legibility rubrics.
     - SYM-REC: synergy and complementarity task definitions.
   - Currently empty.
3. **Module Protocol Specifications (`spec/modules/`):**
   - Must contain: `SYM-COG.md`, `SYM-EPI.md`, `SYM-AFF.md`, `SYM-SAF.md`, `SYM-MCH.md`, `SYM-REC.md`. Currently empty.
4. **Python Pipeline Engine (`packages/py/src/symnoesis/`):**
   - `modules/`: Task execution and scoring modules (`cog/`, `epi/`, `aff/`, `saf/`, `mch/`, `rec/`).
   - `judges/`: Judge interface, multi-judge calibration harness, and Krippendorff's $\alpha$ calculation (nominal, ordinal, interval with bootstrap confidence intervals, tested against published literature benchmarks).
   - `simulator/`: Deterministic synthetic persona generator (varying skill, cognitive bias, vulnerability parameters) and scripted dyad dynamics producing planted ground-truth trajectories.
   - `telemetry/`:
     - Ingestion adapters for JSONL logs.
     - Consent verification filter.
     - Pseudonymization and feature derivation.
     - Suppression filter: cell suppression where $n_{\text{eff}} < 10$ (`SQ = null`).
     - Differential privacy mechanism: calibrated Laplace/Gaussian noise on aggregate counts.
   - `providers/`: Provider protocol and adapters for local mock and OpenAI-compatible providers.
5. **Fixtures & Sweep Execution:**
   - `data/fixtures/`: Synthetic test fixture `Fixture-A (scripted)`.
   - `symnoesis sweep`: Full command executing the synthetic pipeline, recovering planted ground truth within tolerance, outputting signed run manifests and map frames.
   - `make repro`: Makefile target executing reference sweep and confirming byte-identical output hashes.

---

## 6. Governance & Research Documentation (Requirement R5 / Milestones M9–M10)

### Current Governance Status
- The 10 policy documents in `docs/governance/` are seeded: `charter.md`, `ethics.md`, `disclosure.md`, `coi.md`, `funding.md`, `data-policy.md`, `privacy.md`, `zones.md`, `certification.md`, `standards-path.md`.
- Status headers are correctly labeled `Status: Proposed`.
- `ORG_FACTS.yaml` contains no fabricated claims; all organization, people, funding, and partner attributes are unverified (`null` / `verified: false`).
- Root documents (`GOVERNANCE.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `MAINTAINERS.md`, `TRADEMARK.md`) are present.

### Missing Governance & Research Elements
1. **Whitepaper (`research/whitepaper/`):**
   - Title: "The Dyadic State: a framework for measuring long-term human-AI interaction".
   - Must contain: motivation, formal framework, related work, scoring and gating, minimal failure cover, evidence tiers, privacy/ethics, threats to validity, validation plan, limitations.
   - Strict constraint: **No empirical results of real systems**.
2. **Diátaxis Documentation Set (`docs/guides/`):**
   - `tutorials/`: "Run your first synthetic sweep", "Read a Symnoesis Card", "Find your pixel".
   - `how-to/`: add an instrument, add a domain, calibrate a judge, build a Card, run reproducibility check, deploy site.
   - `reference/`: CLI, config keys, schemas, API, zones crosswalk, CHI list, glossary.
   - `explanation/`: the Dyadic State, Gray-coded geometry, evidence tiers, safety gate ceiling, privacy by construction.
3. **Research Artifacts (`research/`):**
   - `research/questions.md`: Open research questions catalog.
   - `research/preregistrations/TEMPLATE.md`: Cohort study preregistration template.
   - `research/protocols/`: Ethics and experimental protocol templates.
   - `research/references.bib`: Reference check needed. Note: Line 116 has placeholder author `Author, Team` for `frontiers2026offloading`; requires correction to true authors or removal.

---

## 7. Makefile Targets & Verification Status

### Execution Audit of Makefile Targets

Every target in `Makefile` was tested directly in the project environment:

| Target | Command Executed | Exit Code | Current Status & Failure Diagnosis |
|---|---|:---:|---|
| `help` | `make help` | 0 | Displays available targets. |
| `setup` | `cd packages/py && uv sync --all-extras` + `pnpm install --frozen-lockfile` | 0 | **PASS.** Installs Python 3.12 dependencies and Node dependencies cleanly. |
| `lint` | `ruff check`, `ruff format --check`, `mypy src tests`, `pnpm typecheck`, `prettier --check`, `markdownlint-cli2`, `codespell` | 1 | **FAIL.**<br>1. `ruff check`: 45 errors (import ordering, unused imports, unnecessary mode argument).<br>2. `ruff format`: 3 files need formatting.<br>3. `mypy`: 4 errors (`float \| None` incompatibilities in `net_effects.py` & `sq.py`; missing `__version__`).<br>4. `prettier`: 16 schema files fail formatting.<br>5. `markdownlint-cli2`: 13 errors in `.agents/teamwork/sentinel/BRIEFING.md` because `.agents/` is not in ignore list.<br>6. Missing linters: `eslint`, `stylelint`, `vale` are not wired. |
| `test` | `pytest` + `pnpm -r run test` | 1 | **FAIL.** 4 of 22 Python tests fail:<br>1. `test_zones_precedence`: Assertion `assert 'Z1' in res7.secondary_tags` fails because `evaluate_zones` skips Z1 when CHI is present.<br>2. `test_gray_golden_vector`: `gray_to_int(12)` returns 9 instead of 8 due to variable shift bug in `gray.py`.<br>3. `test_256_pixels_golden_vector`: Coordinate mapping fails due to the inverse Gray bug.<br>4. `test_sanity.py`: `module 'symnoesis' has no attribute '__version__'`. |
| `mutation` | `echo ...` | 0 | **STUB.** Mutmut and Stryker not wired. |
| `vectors` | `echo ...` | 0 | **STUB.** Generator script not wired. |
| `vectors-check` | `echo ...` | 0 | **STUB.** Regeneration regression test not wired. |
| `gen` | `echo ...` | 0 | **STUB.** Schema typegen not wired. |
| `build` | `cd packages/py && uv build` + `pnpm -r run build` | 0 | **PARTIAL PASS.** Builds Python wheel and compiles TS `index.ts`. Does NOT build static website. |
| `e2e` | `echo ...` | 0 | **STUB.** Playwright / axe-core not wired. |
| `a11y` | `echo ...` | 0 | **STUB.** Accessibility audit not wired. |
| `perf` | `echo ...` | 0 | **STUB.** Lighthouse CI budgets not wired. |
| `links` | `echo ...` | 0 | **STUB.** Lychee link checker not wired; binary missing. |
| `repro` | `echo ...` | 0 | **STUB.** Reproducibility sweep not wired. |
| `docs` | `echo ...` | 0 | **STUB.** Documentation build not wired. |
| `site` | `echo ...` | 0 | **STUB.** Astro build not wired. |
| `verify` | `setup lint test build` | 1 | **FAIL.** Halts immediately on `lint` failure. Does not invoke the full 10-gate suite required by `CLAUDE.md`. |
| `clean` | `rm -rf dist ...` | N/A | **PORTABILITY RISK.** Uses Unix `rm -rf` syntax, failing on vanilla Windows shells. |

---

## 8. Exact Gap Analysis Matrix (Requirements R3, R4, R5)

| Requirement | Area | Exact Gap Description | Severity | Impacted Files / Modules |
|---|---|---|:---:|---|
| **R3** | Domains | Missing 4 domain configuration files | High | `spec/domains/*.yaml` |
| **R3** | Instruments | Missing instrument definitions, scoring formulas, and licenses | High | `spec/instruments/*.yaml` |
| **R3** | Modules | Missing 6 module specification protocol documents | High | `spec/modules/*.md` |
| **R3** | Implementation | Missing 6 Python measurement modules (tasks, probes, scorers) | Critical | `packages/py/src/symnoesis/modules/` |
| **R3** | Reliability | Missing multi-judge calibration harness & Krippendorff's $\alpha$ | High | `packages/py/src/symnoesis/judges/` |
| **R3** | Simulator | Missing persona generator and ground-truth recovery battery | Critical | `packages/py/src/symnoesis/simulator/` |
| **R3** | Telemetry | Missing consent, pseudonymization, k-anonymity, DP filters | Critical | `packages/py/src/symnoesis/telemetry/` |
| **R3** | Fixtures | Missing E1 synthetic dataset fixture (`Fixture-A (scripted)`) | High | `data/fixtures/` |
| **R3** | Reproducibility | `make repro` is an unverified echo stub | High | `Makefile`, `symnoesis repro` |
| **R4** | Manifest Signing | Missing Ed25519 signing and hash chain verification | Critical | `packages/py/src/symnoesis/signing.py` |
| **R4** | Symnoesis Card | Missing JSON/HTML/PDF Card reporting generator | Critical | `packages/py/src/symnoesis/reports/card.py` |
| **R4** | Index Pipeline | Missing annual Index builder, bootstrap CI, and tiering | High | `packages/py/src/symnoesis/reports/index.py` |
| **R4** | Portal Model | Missing E0 item-to-variable weights file | High | `spec/portal/portal-model.v0.1.json` |
| **R4** | TypeScript Core | `@symnoesis/core` lacks all math modules, types, and config | Critical | `packages/ts/src/*` |
| **R4** | Web Site | `apps/web` is empty; lacks Astro config, layouts, pages | Critical | `apps/web/*` |
| **R4** | Map Portal | Missing Svelte interactive 16×16 map & questionnaire flow | Critical | `apps/web/src/components/*`, `pages/portal*` |
| **R4** | Claims Registry | Missing site claims registry file | High | `apps/web/src/content/claims.yaml` |
| **R4** | Web Testing | Missing Playwright E2E and axe-core accessibility suites | High | `apps/web/tests/{e2e,a11y}` |
| **R5** | Whitepaper | Missing research whitepaper source and build | High | `research/whitepaper/` |
| **R5** | Guides | Missing Diátaxis user documentation set | High | `docs/guides/*` |
| **R5** | Citations | Reference verification script missing; invalid author in bibtex | Medium | `scripts/check_refs.py`, `research/references.bib` |
| **R5** | CI Workflows | Missing `mutation.yml`, `security.yml`, `release.yml`, `repro.yml` | High | `.github/workflows/*` |
| **R5** | GitHub Community | Missing issue/PR templates, CODEOWNERS, dependabot | Medium | `.github/*` |
| **R5** | Gate Verification | `make verify` fails; 10 targets are echo stubs | Critical | `Makefile` |

---

## 9. Architectural & Implementation Recommendations

1. **Gate Health Remediation (Immediate):**
   - Fix inverse Gray code bit-shift in `packages/py/src/symnoesis/gray.py` (`n ^= n >> shift` instead of `n ^= g >> shift`).
   - Fix Z1 condition in `packages/py/src/symnoesis/zones.py` to allow Z1 matching while letting precedence handle Z7 overriding, or align test assertion with spec rules.
   - Add `__version__ = "0.1.0.dev0"` to `packages/py/src/symnoesis/__init__.py`.
   - Resolve `float | None` type mismatches in `net_effects.py` and `sq.py`.
   - Run `ruff check --fix` and `ruff format` on `packages/py`.
   - Run `prettier --write` on `spec/schemas/`.
   - Add `.agents` to `.markdownlintignore` and `.markdownlint-cli2.jsonc`.
2. **TypeScript Core Porting:**
   - Implement `gray.ts`, `grid.ts`, `erf.ts` (Cody algorithm matching `scipy.special.erfc` within $10^{-9}$), `assign.ts`, `netEffects.ts`, `sq.ts`, `classes.ts`, `zones.ts`, `neighbors.ts`, `projection.ts`.
   - Wire schema typegen and build-time config generation.
   - Run Vitest property tests with `fast-check` to assert parity against Python golden vectors.
3. **Web Portal & Research Site Initialization (`apps/web`):**
   - Initialize Astro 4/5 + Svelte 5 in `apps/web/package.json` with workspace dependency on `@symnoesis/core`.
   - Author design tokens (`tokens.css`, `tokens.json`) strictly adhering to `05_DESIGN_RULES.md`.
   - Build accessible 16×16 SVG Map with roving tabindex and keyboard wrap-around.
   - Implement 4-step client-side portal questionnaire flow with zero external network requests.
   - Create `claims.yaml` registry and link all page claims.
4. **Synthetic Pipeline & Reporting Implementation:**
   - Author `spec/domains/*.yaml`, `spec/instruments/*.yaml`, `spec/modules/*.md`, and `spec/portal/portal-model.v0.1.json`.
   - Implement `symnoesis.signing` with Ed25519 asymmetric verification.
   - Implement synthetic persona simulator and recovery test suite.
   - Implement Card and Index report builders.
   - Connect Typer CLI commands in `symnoesis.cli`.
5. **Release Engineering & Gates Full Wiring:**
   - Wire all echo targets in `Makefile` (`vectors-check`, `gen`, `mutation`, `e2e`, `a11y`, `perf`, `links`, `repro`, `site`).
   - Ensure `make verify` runs all 10 gates in order and exits non-zero on any failure.
   - Provide portable shell handling for Windows in `clean` and shell scripts.
