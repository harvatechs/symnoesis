# Resources: libraries and documentation bundle

## 0. Rules for using this list

1. **Versions are not pinned here on purpose.** Today is 2026-10-11 and versions move. At build time, resolve the current stable release of each tool, read its changelog, pin it in the lockfile, and record the verified version and docs URL in `docs/agent/vendor-notes/<tool>.md` (a 10-line note: version, install command, the exact API calls you rely on, one gotcha).
2. **Verify every API against the installed package or the official docs.** Do not rely on memory. Where a docs site publishes a machine-readable index (for example `llms.txt`), prefer it; confirm it exists first.
3. **Justify each dependency** (what it replaces, license, maintenance status, size). Prefer the standard library.
4. **License allow-list for dependencies:** MIT, BSD-2/3, Apache-2.0, ISC, MPL-2.0, OFL (fonts), CC0, CC BY. Anything else needs a recorded decision. Run `pip-licenses` and `license-checker` in CI.
5. Links below were assembled from memory and a limited search pass; **confirm each resolves** during M0 and log broken ones.

## 1. Python (reference implementation)

| Need | Choice | Docs | Notes |
| --- | --- | --- | --- |
| Environment and lock | `uv` | docs.astral.sh/uv | Lockfile committed; Python ≥ 3.12 |
| Lint, format | `ruff` | docs.astral.sh/ruff | Replaces flake8, isort, black |
| Types | `mypy --strict` | mypy.readthedocs.io | Zero ignores |
| Tests | `pytest`, `pytest-cov` | docs.pytest.org | Markers: `unit`, `property`, `golden`, `slow` |
| Property tests | `hypothesis` | hypothesis.readthedocs.io | Derandomize in CI with printed seeds |
| Mutation | `mutmut` | mutmut.readthedocs.io | Core modules |
| Models, validation | `pydantic` v2 | docs.pydantic.dev | Models generated from JSON Schema |
| Schema → models | `datamodel-code-generator` | github.com/koxudaxi/datamodel-code-generator | Evaluate; keep generated files in `generated/` and diff-checked |
| Numerics | `numpy`, `scipy` | numpy.org/doc, docs.scipy.org | `scipy.special.ndtr`, `scipy.optimize.milp` (HiGHS) |
| Boolean oracle | `sympy` (dev only) | docs.sympy.org | `sympy.logic.boolalg.SOPform` for strict-mode cross-checks |
| Stats helpers | `statsmodels`, `scikit-learn` | statsmodels.org, scikit-learn.org | Power simulation, calibration metrics; implement Brier and ECE yourself and cross-check |
| Krippendorff's α | `krippendorff` (PyPI), cross-checked against your own implementation | pypi.org/project/krippendorff | Validate with published worked examples |
| Tabular I/O | `pyarrow` (Parquet), stdlib `json`, `sqlite3` | arrow.apache.org/docs/python | No pandas dependency in core; allowed in analysis scripts |
| Canonical hashing | RFC 8785 JSON Canonicalization; evaluate `jcs` | rfc-editor.org/rfc/rfc8785 | For config and manifest hashes |
| Signing | `cryptography` (Ed25519) | cryptography.io | Keys never in repo |
| Differential privacy | `opendp` (evaluate) or a documented, tested Laplace/Gaussian mechanism | docs.opendp.org | Statistical tests either way |
| CLI | `typer` | typer.tiangolo.com | Stable subcommands (Architecture §4) |
| API (optional extra) | `fastapi`, `uvicorn` | fastapi.tiangolo.com | OpenAPI 3.1 export committed and diff-checked |
| Eval ecosystem interop (optional) | Inspect (UK AI Security Institute) | inspect.aisi.org.uk | ADR whether SYMN tasks should also ship as Inspect tasks |
| Providers (optional extras) | Official SDKs for hosted models; an OpenAI-compatible HTTP client for local servers (Ollama, vLLM) | each vendor's docs | Behind the `Provider` protocol; cache by request hash |
| Logging | `structlog` | structlog.org | No raw user text in logs |

## 2. TypeScript and web

| Need | Choice | Docs | Notes |
| --- | --- | --- | --- |
| Runtime | Node.js current **Active LTS** | nodejs.org | Astro 6 requires Node ≥ 22 per its docs; confirm current requirement |
| Package manager | `pnpm` | pnpm.io | Lockfile committed |
| Site framework | **Astro** (current stable major) | docs.astro.build | Static output; content collections for docs and claims; Pagefind integration |
| Interactive islands | **Svelte 5** (runes mode) | svelte.dev/docs | Verify syntax against current docs; do not write Svelte 4 patterns |
| Content | MDX via Astro; `remark-math` + `rehype-katex` | katex.org | Math rendered at build; no runtime KaTeX |
| Search | Pagefind | pagefind.app | Client-side, no external service |
| Color science | `culori` | culorijs.org | OKLab interpolation, CVD filters, contrast |
| Fonts | Fontsource: Inter, Source Serif 4, JetBrains Mono | fontsource.org | Self-hosted, subset, `woff2` |
| Validation | `zod` | zod.dev | All artifact and URL-state boundaries |
| Unit tests | `vitest` | vitest.dev | Parity tests |
| Property tests | `fast-check` | fast-check.dev | Mirror Python invariants |
| Mutation | Stryker | stryker-mutator.io | Core package |
| E2E | Playwright | playwright.dev | Network assertions, keyboard tests, screenshots |
| Accessibility | `@axe-core/playwright`; manual NVDA and VoiceOver | github.com/dequelabs/axe-core | axe is necessary, not sufficient |
| Performance | Lighthouse CI | github.com/GoogleChrome/lighthouse-ci | Budgets in UX rules |
| Lint, format | `eslint`, `typescript-eslint`, `prettier`, `stylelint` | each project's docs | `strict` configs |
| Architecture lint | `dependency-cruiser` | github.com/sverweij/dependency-cruiser | Enforces package boundaries |
| Schema → zod/types | Evaluate `json-schema-to-zod` or `quicktype` | npm / quicktype.io | Generated, diff-checked |

Do **not** add: a UI kit, Tailwind, a state-management library, a charting library (the map is bespoke SVG), an animation library, or a runtime diagram library.

## 3. Quality and process tooling

| Need | Tool | Docs |
| --- | --- | --- |
| Prose lint with custom rules | Vale | vale.sh |
| Markdown lint | markdownlint-cli2 | github.com/DavidAnson/markdownlint-cli2 |
| Spelling | codespell, cspell (domain dictionary) | github.com/codespell-project/codespell |
| Links | lychee | lychee.cli.rs |
| Secrets | gitleaks | github.com/gitleaks/gitleaks |
| Supply chain | pip-audit, npm audit, CodeQL, Dependabot, OpenSSF Scorecard, CycloneDX SBOM | scorecard.dev, cyclonedx.org |
| Licensing hygiene | REUSE spec, SPDX identifiers | reuse.software |
| Hooks | pre-commit | pre-commit.com |

## 4. Standards, specifications, accessibility

| Topic | Source |
| --- | --- |
| Web accessibility | WCAG 2.2 (w3.org/TR/WCAG22); WAI-ARIA Authoring Practices, grid pattern (w3.org/WAI/ARIA/apg/patterns/grid) |
| Color-vision-safe palettes | Okabe & Ito, "Color Universal Design" (jfly.uni-koeln.de/color) |
| AI governance crosswalk | NIST AI RMF 1.0 and Generative AI Profile (nist.gov/itl/ai-risk-management-framework); ISO/IEC 42001:2023 (iso.org); Regulation (EU) 2024/1689 (eur-lex.europa.eu); IEEE 7010-2020 on wellbeing impact assessment (standards.ieee.org) |
| Documentation | Diátaxis (diataxis.fr); Keep a Changelog (keepachangelog.com); Semantic Versioning (semver.org); Conventional Commits (conventionalcommits.org); MADR for ADRs (adr.github.io/madr) |
| Citation | Citation File Format (citation-file-format.github.io); Zenodo with GitHub (docs.github.com, "Referencing and citing content") |
| Community files | Contributor Covenant 2.1 (contributor-covenant.org); GitHub community health files |
| Hosting | GitHub Pages (docs.github.com/pages) with the official Pages deploy Action |
| Research registration | OSF Preregistration (osf.io/prereg) |
| Metadata verification | Crossref REST API (api.crossref.org) for DOI checks |
| Support directory for the portal | findahelpline.com (verify availability and wording before linking) |

## 5. Reading for the agent (before M1)

1. `spec/SPEC.md`, twice.
2. Karnaugh-map and Quine–McCluskey explanations from a standard digital-logic text, to internalize don't-cares and prime implicants.
3. The Okabe–Ito palette page and WCAG 2.2 "Use of Color" and "Target Size" criteria.
4. The prior-art sources in `08_RESEARCH_PROTOCOL.md` §3.1: read the **methods** of the MIT/OpenAI RCT and its critique, and the HumanAI-Impact-Bench repository, to understand what has already been done and where the limits are. Check each repository's license before reusing anything; reuse ideas and cite, do not copy text or data.

## 6. Documentation bundle (what to create in `docs/agent/vendor-notes/`)

One note per tool actually used, each with: verified version; docs URL; install and invocation; the exact functions used with a minimal verified example; known gotchas; license. These notes become part of the build record and prevent API hallucination in later sessions.

## 7. Template files to adopt (do not generate from imagination)

Contributor Covenant 2.1 text; Apache-2.0 license text from the canonical source; CC BY 4.0 legal code reference; GitHub issue and PR template conventions; Keep a Changelog layout; MADR template; CITATION.cff schema validated with the official validator.
