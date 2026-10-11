# CLAUDE.md — Symnoesis (SYMN-01)

You are building **Symnoesis**, an open, not-for-profit research initiative of HarVa Groups: a benchmark that measures the **Dyadic State** (a human and an AI system as one unit, over time), plus its specification, reference implementation, public portal, annual Index, and research website. This repo is read by researchers, auditors, and regulators. Treat every file as something a skeptical expert will check.

## 0. Read first, in this order

1. `docs/agent/01_INTENT.md` — why this exists, what success is, what it is not
2. `spec/SPEC.md` — normative. **The spec wins over every other document and over your own judgment.**
3. `docs/agent/10_DO_NOT.md` — prohibited behaviors. Re-read at the start of every session
4. `docs/agent/04_PLAN.md` — milestones and exit criteria. Work only on the current milestone
5. The topical file for your task: `03_ARCHITECTURE`, `05_DESIGN_RULES`, `06_CONTENT_RULES`, `07_UX_RULES`, `08_RESEARCH_PROTOCOL`, `09_VERIFICATION`, `11_RESOURCES`, `12_REPO_BLUEPRINT`, `13_GOVERNANCE_ORG`, `14_DECISIONS`

## 1. Non-negotiables

1. **No shortcuts.** Fix root causes. Do not bypass an error, weaken a test, loosen a threshold, add `# type: ignore` / `@ts-ignore` / `any`, skip or `xfail` a test, silence a linter, swallow an exception, or stub a function to get green. If something cannot be fixed properly, stop and record it in `docs/build-log/OPEN_QUESTIONS.md`.
2. **No fabrication.** Never invent data, results, scores, citations, DOIs, quotes, partners, funders, council members, testimonials, statistics, benchmarks, or org facts (legal status, address, people). Everything on the site traces to a spec rule, a reproducible artifact hash, a verified reference, or `ORG_FACTS.yaml`.
3. **No pseudocode, no placeholders in shipped files.** No `TODO`, `FIXME`, `lorem ipsum`, `foo/bar`, `example.com` stand-ins presented as real, or `pass` bodies. Fixtures must be labeled synthetic and use fictional names (`Fixture-A (scripted)`).
4. **Verify, never assume.** Before using any library API, read the installed version's docs or source (`python -c "help(...)"`, `npm view`, official docs via fetch). Your memory of APIs and versions is likely stale. Record the version you verified.
5. **Spec first.** If code and spec disagree, the spec is right unless an ADR in `docs/adr/` changes it via the RFC process. Never edit a golden vector to make a test pass.
6. **Evidence honesty.** Every score, map, and claim carries an evidence tier (E0–E3, SPEC §13). Synthetic results are never presented as measurements of real systems or real people.
7. **Human wellbeing and privacy first.** No raw conversation retention, no third-party trackers, no analytics, no diagnosis, no clinical claims. The portal computes in the browser and sends nothing.
8. **Quality over speed.** Do fewer things completely. A milestone is done only when its exit criteria pass and the output is pasted into the build log.

## 2. Workflow for every task

1. **State** the task and the spec section(s) it implements.
2. **Plan** in 3–8 lines. Name the tests you will write first.
3. **Write tests first** where logic is involved (property tests for invariants, golden vectors for numerics).
4. **Implement** in small commits. Conventional Commits: `feat(core): …`, `fix(web): …`, `docs(spec): …`.
5. **Verify** by running the gate commands (Section 3). Paste real output into `docs/build-log/YYYY-MM-DD-<topic>.md`.
6. **Log research** decisions in `research/LOG.md` (template in `08_RESEARCH_PROTOCOL.md`).
7. **Self-review** against `10_DO_NOT.md` and the milestone's checklist before declaring done.

If a requirement is ambiguous: choose the most conservative reading, document it in `docs/adr/`, and continue. If it blocks correctness, stop and ask.

## 3. Gate commands (must be green before any commit to `main`)

```
make setup        # install pinned toolchains from lockfiles
make lint         # ruff, mypy --strict, eslint, tsc --noEmit, stylelint, markdownlint, vale, codespell
make test         # pytest (unit, property, golden), vitest, parity tests
make mutation     # mutmut on packages/py core, Stryker on packages/ts (thresholds in 09_VERIFICATION)
make vectors-check# regenerate golden vectors; fail on any diff
make build        # python wheel + sdist, ts package, astro static site
make e2e          # playwright incl. axe-core accessibility
make perf         # lighthouse-ci budgets
make links        # lychee link check
make repro        # re-run reference sweep; artifact hashes must match
make verify       # all of the above, in order
```

If a target does not yet exist for the current milestone, create it as part of that milestone. Do not claim "tests pass" without having run them in this session.

## 4. Engineering conventions

- **Python ≥ 3.12**, `src/` layout, `pydantic` v2 models, full type hints, `mypy --strict`, `ruff` (lint + format). Pure functions for all scoring math. No global mutable state. No numerical constants in source: read from `spec/config/symn-01.v0.1.yaml`. All randomness takes an explicit seed.
- **TypeScript strict**, ES modules, no `any`, no non-null `!` assertions without a comment-justified invariant, zod at every I/O boundary.
- **CSS**: hand-written, custom properties as tokens, cascade layers, logical properties. No utility-class frameworks, no UI kits.
- **Markdown**: sentence-case headings, one H1 per file, line length unconstrained, tables for reference data, no emoji.
- **Naming**: `symnoesis` (package), `SYMN-01` (benchmark), `Symnoesis Map`, `Symnoesis Card`, `Symnoesis Index`, `Dyadic State`, `SQ`, `HNE`, `SNE`, `MFC`. Use the glossary in `06_CONTENT_RULES.md` exactly.
- **Determinism**: same inputs, config, and seed produce byte-identical outputs. Artifacts embed a config hash and git SHA.
- **Dependencies**: justify each in the PR description. Prefer the standard library and existing deps. Pin via lockfiles. GitHub Actions pinned by commit SHA.
- **Security**: no secrets in the repo (`gitleaks` runs in CI). No network calls from the portal at runtime. Strict CSP meta tag.

## 5. Design and content in one paragraph

Apple-inspired, not Apple-imitating: calm, spacious, typographic, monochrome with one restrained accent, one memorable object (the Symnoesis Map). Plain, precise, unhyped language. Read `05_DESIGN_RULES.md`, `06_CONTENT_RULES.md`, and `07_UX_RULES.md` before touching any page. Never use Apple trademarks, logos, imagery, or copy.

## 6. Session protocol

**Start:** read this file, `10_DO_NOT.md`, the latest build-log entry, and `OPEN_QUESTIONS.md`. Run `git status` and `make verify` (or the subset that exists) to learn the true baseline.
**End:** commit; update `docs/build-log/`; update `OPEN_QUESTIONS.md`; list what is verified, what is not, and what is next. Never end a session with a failing gate you did not report.

## 7. When to stop and ask

Stop (do not guess) if: a legal or ethical decision is needed (licenses, consent text, human-subject protocols, legal status of HarVa Groups); you need credentials or paid API access; a spec change seems necessary; two documents conflict and the spec does not resolve it; a verification cannot be completed. Write the question in `OPEN_QUESTIONS.md` with options and your recommendation.

## 8. Definition of done (any task)

Spec section implemented as written; tests written and passing; types and lint clean; docs updated; evidence tier labeled; no placeholder text; build log entry with pasted command output; self-review against `10_DO_NOT.md` completed.
