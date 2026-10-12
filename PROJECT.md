# Project: Symnoesis (SYMN-01) v0.1.0

## Architecture
Symnoesis is an open benchmark measuring the Dyadic State (human + AI system over time).
The repository architecture consists of:
- `spec/`: Normative specification (`SPEC.md`), configuration (`config/symn-01.v0.1.yaml`), golden vectors (`vectors/`), and 16 JSON Schemas (`schemas/`).
- `packages/py/`: Python reference implementation (`src/symnoesis/`), including math core, MFC optimization, longitudinal engine, synthetic generator, cryptographic signing, card/index reporting, and CLI.
- `packages/ts/`: TypeScript port (`@symnoesis/core` in `packages/ts/src/`), implementing identical mathematical core, Gray coordinates, Cody erfc, net effects, and portal projection.
- `apps/web/`: Public research website and Interactive Map Portal built with Astro, Svelte 5, custom CSS tokens (`tokens.css`), and WCAG 2.1 AA accessibility.
- `docs/`: Architectural specifications, ADRs, Diátaxis user guides, and governance frameworks.
- `research/`: Research protocol, whitepaper, preregistration templates, and bibliography.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Gray Code Bijection | 4-bit Gray code mapping `gray(k) = k ^ (k >> 1)` and inverse folding | M1 | SPEC §5 |
| 2 | 16x16 Grid Coordinates | 8-bit pixel bit-interleaving $(H_1,S_1,H_2,S_2,H_3,S_3,H_4,S_4)$ to (col, row) | M1 | SPEC §5 |
| 3 | Normal CDF Parity | Variable scaling using Cody's erfc matching `scipy.special.ndtr` within 1e-9 | M1 | SPEC §4 |
| 4 | Probabilistic Pixel Assignment | Joint 256 mass distribution with $\sigma_{floor} = 0.01$ and $1e-4$ pruning | M1 | SPEC §4 |
| 5 | Net Effects Calculus | $HNE$ (state + outcome), $SNE$, non-compensation rule ($SNE' = \min(SNE, 0)$ if $HNE < 0$) | M1 | SPEC §6 |
| 6 | Stability & Harm Asymmetry | Asymmetric stability dampening ($S_{eff} = S$ if $C \ge 0$ else $1.0$) | M1 | SPEC §7 |
| 7 | Safety Gate Ceiling | Critical event ceiling ($G \in [0, 0.25]$) capping raw SQ | M1 | SPEC §7 |
| 8 | Composite SQ & Clipping | Final SQ calculation clipped to $[-100, +100]$ | M1 | SPEC §7 |
| 9 | Symbiosis Classification | 4 primary classes: Mutualism, Commensalism, Amensalism, Parasitism | M1 | SPEC §8 |
| 10 | Governance Zones | 7 governance zones Z1–Z7 with strict precedence and secondary tags | M1 | SPEC §9 |
| 11 | Golden Vectors Parity | Verification against GV-SQ-001..003 within 1e-6 tolerance across Py & TS | M1 | SPEC App A |
| 12 | Schema Header Repair | Restore `"$schema"` property across all 16 JSON schemas in `spec/schemas/` | M1 | Schemas |
| 13 | Py Strict Typing & Linting | Pass `mypy --strict` (0 errors) and `ruff check`/`format` across `packages/py` | M1 | CLAUDE §3 |
| 14 | TypeScript Reference Core | Full `@symnoesis/core` package with TS strict typing (`tsc --noEmit`) | M1 | ORIGINAL_REQUEST R1 |
| 15 | Minimal Failure Cover (MILP) | Exact set-cover optimization using `scipy.optimize.milp` with HiGHS | M2 | SPEC §10 |
| 16 | Quine-McCluskey Strict Mode | Boolean minimizer matching `sympy.logic.boolalg.SOPform` output | M2 | SPEC §10 |
| 17 | Subcube Harm Mass & Purity | 6561 subcube evaluation with purity $\pi(R) \ge 0.8$, coverage $\ge 0.85$ | M2 | SPEC §10 |
| 18 | Counterfactual Repair | Ridge projection identifying minimal variable deltas to restore mutualism | M2 | SPEC §10 |
| 19 | Longitudinal Temporal Engine | Multi-frame trajectory evaluation across days 1, 7, 28, 84, 182 | M2 | SPEC §9 |
| 20 | Minimum Detectable Change | MDC thresholding ($MDC = 5.0$) requiring 2 consecutive intervals | M2 | SPEC §9 |
| 21 | Domain & Instrument Specs | 4 domain configs (`spec/domains/*.yaml`), instruments, and protocol specs | M3 | SPEC §12 |
| 22 | Persona & Dyad Simulator | Synthetic session generation across learning, coding, health, companionship | M3 | SPEC §13 |
| 23 | Multi-Judge Calibration | LLM judge panel scoring with Krippendorff's $\alpha \ge 0.80$ | M3 | SPEC §12 |
| 24 | Telemetry & Privacy Engine | $k$-anonymity enforcement ($k_{min} = 10$) and differential privacy ($\varepsilon = 1.0$) | M3 | SPEC §13 |
| 25 | Synthetic Evidence Fixtures | Generation of reproducible E1 synthetic fixtures in `data/fixtures/` | M3 | ORIGINAL_REQUEST R3 |
| 26 | Cryptographic Run Manifests | Ed25519 key signing and SHA-256 hash chains for all run artifacts | M4 | SPEC §14 |
| 27 | Symnoesis Card Generator | JSON and standalone HTML Card rendering conforming to schema | M4 | SPEC §14 |
| 28 | Symnoesis Index Tooling | Bootstrapped ranking and tiering at $P(i > j) \ge 0.95$ | M4 | SPEC §14 |
| 29 | Typer CLI | Command-line interface for scoring, card, index, and verification | M4 | REPO_BLUEPRINT |
| 30 | Astro Web Application | Static research website in `apps/web` using custom CSS token system | M4 | REPO_BLUEPRINT |
| 31 | Interactive Map Portal | 16x16 Gray map visualization with adaptive resolution (16x16, 8x8, 4x4) | M4 | SPEC §14, ADR-0014 |
| 32 | Neighbor Inspection | 4 visible planar neighbors + 8 single-flip Hamming neighbors panel | M4 | SPEC §14 |
| 33 | WCAG 2.1 AA Accessibility | Keyboard navigation, high-contrast, screen-reader support, no color-only data | M4 | CLAUDE §3 |
| 34 | Claims Registry | Transparent claims index in `apps/web/src/content/claims.yaml` | M4 | DESIGN_RULES |
| 35 | Whitepaper & Research Docs | Academic preprint draft in `research/whitepaper/` and preregistration templates | M5 | RESEARCH_PROTOCOL |
| 36 | Diátaxis Documentation | Tutorials, How-To, Reference, and Explanation in `docs/guides/` | M5 | REPO_BLUEPRINT |
| 37 | Reference Bibliography | Complete citations in `research/references.bib` with zero placeholders | M5 | CLAUDE §1 |
| 38 | Governance Framework Finalization | Review and finalize all 10 policy documents in `docs/governance/` | M5 | GOVERNANCE_ORG |
| 39 | Makefile Full Automation | Real implementations of all gate targets (`make verify` clean) | M5 | CLAUDE §3 |
| 40 | Package Build & Release Artifacts | Python wheel/sdist and TypeScript `@symnoesis/core` package distribution | M5 | CLAUDE §3 |
| 41 | E2E Test Suite Tiers 1-4 | Opaque-box requirement-driven testing suite covering all features | M_E2E | Dual Track |
| 42 | Adversarial Hardening (Tier 5) | White-box stress testing and boundary challenge battery | M_FINAL | Dual Track |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Math Reference Core & Parity | Python math fixes, Schema repair, TypeScript core port, golden vectors parity | none | DONE |
| M2 | MFC & Longitudinal Diagnostics | HiGHS MILP, Quine-McCluskey strict mode, counterfactual repair, temporal engine | M1 | DONE |
| M3 | Synthetic Evidence & Privacy | 4 domains, persona simulator, judge panel ($\alpha \ge 0.80$), k-anonymity, DP | M1 | IN_PROGRESS |
| M4 | Card, Index, CLI & Web Portal | Ed25519 signing, Card/Index tooling, Typer CLI, Astro site, Interactive Map | M1, M2 | PLANNED |
| M5 | Governance & Release Eng | Whitepaper, Diátaxis docs, Makefile targets, package builds, `make verify` | M1, M2, M3, M4 | PLANNED |
| M_E2E | E2E Testing Track | Independent opaque-box test suite (Tiers 1-4), harness, `TEST_READY.md` | none | DONE |

## Interface Contracts

### Python Core ↔ TypeScript Core (`@symnoesis/core`)
- Function signatures:
  - `int_to_gray(n: int) -> int` / `intToGray(n: number): number`
  - `gray_to_int(g: int) -> int` / `grayToInt(g: number): number`
  - `pixel_coord_to_id(col: int, row: int) -> int` / `pixelCoordToId(col: number, row: number): number`
  - `pixel_id_to_coord(id: int) -> PixelCoord` / `pixelIdToCoord(id: number): PixelCoord`
  - `normal_cdf(x: float) -> float` / `normalCdf(x: number): number` (max discrepancy $< 10^{-9}$ against `ndtr`)
  - `compute_sq(variables: VariableInputs, config: SymnConfig) -> SQResult` / `computeSq(variables: VariableInputs, config: SymnConfig): SQResult`
- Tolerances: Outputs for GV-SQ-001..003 must match within $10^{-6}$ across both implementations.

### Python Core ↔ MFC Optimization
- `MinimalFailureCover`:
  - Input: Matrix of vertex masses $m(c)$ and harm $h(c) = n_{eff}(c) \cdot \max(0, -SQ(c))/100$ for $c \in \{0..255\}$.
  - Solver: HiGHS MILP (`scipy.optimize.milp`).
  - Output: List of subcubes covering $\ge 85\%$ harm mass with purity $\ge 0.8$.

### Python Core ↔ Temporal Engine
- `TrajectoryEngine`:
  - Input: Time-indexed scores $SQ(t)$ for $t \in \{1, 7, 28, 84, 182\}$.
  - Output: TrajectoryStatus (`improving`, `stable`, `deteriorating`), $\Delta SQ$, $MDC = 5.0$.

### Core ↔ Web Portal (`apps/web`)
- Bundle `@symnoesis/core` into Astro/Svelte 5 client-side bundle.
- Zero server-side API calls. Computation is 100% in-browser WebAssembly/TypeScript.
- WCAG 2.1 AA compliant SVG/Canvas rendering.

## Code Layout
- `packages/py/src/symnoesis/`:
  - `__init__.py`, `config.py`, `gray.py`, `grid.py`, `variables.py`, `assign.py`
  - `net_effects.py`, `stability.py`, `gates.py`, `sq.py`, `classes.py`, `zones.py`
  - `cover.py`, `counterfactual.py`, `temporal.py`, `signing.py`, `privacy.py`, `cli.py`
  - `simulator/`, `judges/`, `telemetry/`, `reports/`
- `packages/ts/src/`:
  - `index.ts`, `config.ts`, `gray.ts`, `grid.ts`, `math.ts`, `assign.ts`
  - `net_effects.ts`, `stability.ts`, `gates.ts`, `sq.ts`, `classes.ts`, `zones.ts`
- `apps/web/`:
  - `package.json`, `astro.config.mjs`, `src/components/`, `src/pages/`, `src/styles/tokens.css`
- `spec/`:
  - `SPEC.md`, `config/`, `vectors/`, `schemas/`, `domains/`, `instruments/`, `modules/`
