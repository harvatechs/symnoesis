# Build Plan — Release v0.1.0

Scope of v0.1.0: the specification, reference implementation, TypeScript port, synthetic-evidence pipeline, Symnoesis Card and Index tooling, research website, Interactive Map Portal (E0 prototype), research and governance documents, and release engineering. **Out of scope for this build** (organizational work the repo supports): human cohorts, threshold calibration, independent replication, certification.

## Rules of engagement

- Milestones are sequential. Do not start M(n+1) until M(n) exit criteria pass **and** a human reviewer signs off in `docs/build-log/`.
- Each milestone ends with: `make verify` output pasted into the build log, updated `OPEN_QUESTIONS.md`, and a short "verified / not verified / next" report.
- Each task lists the spec sections it implements. If you cannot trace a task to the spec, stop.
- Estimates are relative effort (S, M, L), not time promises.

---

## M0 — Foundation and tooling (S)

**Deliverables:** monorepo skeleton per `12_REPO_BLUEPRINT.md`; `Makefile` with all gate targets (stubs allowed only if they fail loudly with "not implemented in M0" and are replaced by the milestone that owns them); pre-commit; CI skeleton; licenses; governance stub files; `ORG_FACTS.yaml` with all fields `verified: false`; `research/prior-art.md` (extending the findings in `00_START_HERE.md`); `docs/build-log/00-understanding.md`.

**Tasks**
1. Initialize repo, `.editorconfig`, `.gitignore`, `.gitattributes`, `LICENSE`, `LICENSE-DOCS`, `CITATION.cff` (fields marked pending only where facts are missing).
2. Python toolchain (`uv` or `pip-tools`; lockfile), `ruff`, `mypy --strict`, `pytest`, `hypothesis`.
3. Node toolchain (current Active LTS; `pnpm` with lockfile), `eslint`, `prettier`, `stylelint`, `vitest`, `playwright`.
4. Docs lint: `markdownlint`, `vale` (with the banned-word style from `06_CONTENT_RULES.md`), `codespell`, `lychee`.
5. CI workflows: `ci.yml` (lint, test, build), `pages.yml`, `codeql.yml`, `scorecard.yml`; Actions pinned by SHA.
6. Copy the agent pack into place; write `AGENTS.md` pointer.
7. Prior-art search: record every source in `research/LOG.md` with access date.

**Exit criteria:** clean clone → `make setup && make lint` passes; CI green on an empty-feature PR; `ORG_FACTS.yaml` present; prior-art file lists ≥ 10 verified sources.

---

## M1 — Specification as code, reference core (L)

**Implements:** SPEC §2–§9, App. A, App. B.

**Deliverables:** `spec/config/symn-01.v0.1.yaml` (verbatim App. B); JSON Schemas (§14); Python modules `config, gray, grid, variables, assign, net_effects, stability, gates, sq, classes, zones, evidence`; golden vector generator and `spec/vectors/*.json` including `GV-SQ-001..003`, all 16 Gray positions, all 256 pixel IDs, boundary cases for every zone and class threshold.

**Tasks**
1. Config loader with schema validation and a canonical hash (sorted keys, normalized floats).
2. Gray code and grid: bijection over 256 pixels; neighbor sets (4 visible, 8 total); wrap-around.
3. Assignment: `p_i`, mass distribution, pruning, renormalization, modal pixel.
4. Net effects, stability, gate-as-ceiling, non-compensation, SQ per window and per pixel; cluster bootstrap CI.
5. Class and zone functions with explicit boundary tests.
6. Hand-verify the three worked examples in a test that computes each intermediate value.

**Exit criteria:** all property tests and golden vectors pass; branch coverage ≥ 95% on these modules; `mypy --strict` clean; a reviewer reproduces GV-SQ-001 by hand from the spec text alone.

---

## M2 — Cover, temporal, counterfactual (L)

**Implements:** SPEC §10–§12.

**Deliverables:** `temporal.py`, `cover.py`, `counterfactual.py`; fixtures of hand-built harm maps with known covers.

**Tasks**
1. Enumerate the 6561 subcubes; compute purity, coverage, literals.
2. MILP formulation with `scipy.optimize.milp`; deterministic tie-breaking; lexicographic objective via staged solves or scaled weights proven not to reorder (document the proof).
3. Strict mode and cross-check with `sympy.logic.boolalg.SOPform` on ≥ 500 random Boolean functions (including don't-cares).
4. Counterfactual: observed vs modeled flips; pooled additive ridge model; CI by bootstrap.
5. MDC and trajectory rule with test-retest placeholder flagged.

**Exit criteria:** strict-mode agreement with sympy on all random cases (functional equivalence, literals ≤ sympy's); cover validity properties hold under Hypothesis; same seed gives byte-identical output; runtime for a full 256-cell instance < 2 s on a laptop.

---

## M3 — TypeScript port and parity (M)

**Implements:** SPEC §3–§9 (browser subset).

**Deliverables:** `@symnoesis/core` with `erfc` (Cody), grid, assignment, net effects, SQ, classes, zones, neighbors; generated types from schemas; build-time generated config.

**Exit criteria:** every golden vector passes in vitest within tolerance (`1e-9` for SQ and net effects; `1e-9` for `Φ`); property tests with `fast-check` for the same invariants; `tsc --strict` clean; bundle size recorded and below budget (`09_VERIFICATION.md`).

---

## M4 — Telemetry, privacy, signing (M)

**Implements:** SPEC §14, §16.

**Deliverables:** schemas finalized; JSONL adapter; consent checks; pseudonymization; feature derivation interface; DP release of aggregates (verify against `OpenDP` or a documented, tested Laplace/Gaussian mechanism); k-anonymity suppression; Ed25519 signing; `RunManifest`.

**Exit criteria:** a test proves raw text never reaches disk; consent-withdrawn records are excluded from every export; suppression test (`n_eff < 10` → `null`); DP mechanism statistical test; manifest signature verifies and tampering fails.

---

## M5 — Instruments, judges, simulator (L)

**Implements:** SPEC §15, §16.

**Deliverables:** module implementations at v0.1 scope; judge interface and calibration harness with Krippendorff's α (validated against worked examples from the literature); deterministic scripted personas; provider protocol with at least one local and one hosted adapter as optional extras; benign-proxy safety scenarios and classifier-label pipeline.

**Tasks**
1. SYM-EPI: stance-varied twin generator, sycophancy-drift scorer, calibration scorer (Brier, ECE), fabrication stress items (public dev set only).
2. SYM-COG: matched-task engine, AI-off probe scheduler, appropriate-reliance index.
3. SYM-AFF: dependence indicators from telemetry (usage escalation, interruption response, substitution flags).
4. SYM-SAF: scenario schema; scripted multi-session boundary scenarios using abstract risk-signal tokens, never real harmful content; label-only evidence store.
5. SYM-MCH: canary poisoning, drift detector, legibility rubric.
6. SYM-REC: synergy statistic, complementarity.
7. Simulator: persona parameters (skill, bias, vulnerability), scripted dynamics that produce known ground-truth H/M trajectories for validation.
8. `symnoesis sweep` runs a full pipeline on a deterministic mock system (`Fixture-A (scripted)`), recovers the known ground truth, and produces a map.

**Exit criteria:** the simulator's planted ground truth is recovered by the pipeline within pre-stated tolerances (a recovery test, not a demo); judge harness reproduces published α examples exactly; no module stores prohibited content (test with scanners); sweep is reproducible by `make repro`.

---

## M6 — Reports, Card, Index pipeline (M)

**Implements:** SPEC §13–§14; Index definition in `14_DECISIONS.md` (ADR-0009).

**Deliverables:** Symnoesis Card (JSON → HTML → PDF); Index builder: per-system SQ aggregate with bootstrap, rank-probability matrix, tiering (systems are tied unless `P(i better than j) ≥ 0.95`), critical-event listing separate from rank; fixture Index "Edition 0 — methodology preview" built from fictional fixture systems and visibly labeled.

**Exit criteria:** Card renders from artifacts only (no hand-edited numbers); tiering tests on planted differences; a system with a confirmed critical event can never appear in the top tier; every Card shows evidence tier, config hash, git SHA, and limitations section.

---

## M7 — Website and design system (L)

**Implements:** `05_DESIGN_RULES`, `06_CONTENT_RULES`, `07_UX_RULES`.

**Deliverables:** Astro site; tokens and components; pages: Home, Idea, Map explorer, Method (spec rendered), Index, Research (log, reading list, glossary), Docs, Governance, About, Cite, Privacy, Accessibility, 404; Pagefind search; print stylesheets; OG images.

**Exit criteria:** Lighthouse CI budgets pass; axe-core zero violations on every page; keyboard-only walkthrough recorded in the build log; visual regression baselines committed; Vale content lint clean; every claim on the site maps to an evidence ID in `apps/web/src/content/claims.yaml`.

---

## M8 — Interactive Map Portal (L)

**Implements:** `03_ARCHITECTURE` §7a; `07_UX_RULES` §6.

**Deliverables:** questionnaire flow; projection; result view (modal pixel, mass distribution, zone probabilities, single-flip suggestions); neighbors panel; text alternative; shareable state (URL hash, opt-in); print/PDF; E0 banner and non-diagnostic language; support resources link.

**Exit criteria:** zero network requests during portal use (asserted in Playwright); parity of projection outputs against Python reference on 200 sampled response sets; screen-reader pass on NVDA and VoiceOver (recorded manually in the build log); a content review confirms no diagnostic, clinical, or alarmist phrasing.

---

## M9 — Research and organization documents (M)

**Deliverables:** whitepaper "The Dyadic State: a framework for measuring long-term human-AI interaction" (Markdown + PDF) containing the framework, formal definitions, design rationale, limitations, and a validation plan, **with no empirical results**; preregistration templates; ethics protocol templates; instrument catalog with license status; reading list; governance documents per `13_GOVERNANCE_ORG.md`; Diátaxis user documentation (tutorial, how-to, reference, explanation).

**Exit criteria:** every reference verified (DOI resolves, metadata matches) and recorded in `references.bib` with `verified: true`; whitepaper contains an explicit limitations section and an evidence-tier statement; governance documents contain no invented names, entities, or legal claims.

---

## M10 — Hardening and release (M)

**Deliverables:** security scans clean; SBOM; reproducibility check; accessibility and performance final audits; link check; spell check; CHANGELOG; release notes; tag `v0.1.0`; Pages deployment; Zenodo-ready metadata.

**Exit criteria:** clean clone on a second machine passes `make verify`; `make repro` hashes match; all items of the acceptance checklist in `09_VERIFICATION.md` are checked with evidence; OPEN_QUESTIONS has no blocking entries; human reviewer signs the release note.

---

## Build-log protocol

Each entry `docs/build-log/YYYY-MM-DD-<topic>.md` contains: goal; spec sections; decisions (link ADRs); commands run with **verbatim** output; test counts and coverage; library versions verified and where; what was **not** verified; next step. Entries are append-only.

## Risk watch

| Risk | Early signal | Response |
| --- | --- | --- |
| Agent hallucinates a library API | Import errors; "plausible but wrong" calls | Verify against installed package; record version |
| Numerical drift between Python and TS | Parity test failures near boundaries | Fix implementation, never widen tolerance beyond spec |
| Scope creep into services | Proposals for Kubernetes, GraphQL, DB servers | Refuse; ADR-0007 |
| Design regresses to templates | Cards, gradients, eyebrow labels, icon grids | Re-read `05_DESIGN_RULES.md`; remove |
| Fabricated "proof" content | Numbers on the site with no artifact | Delete; apply claims registry |
