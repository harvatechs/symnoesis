# Repository Blueprint

The repo is simple to navigate: a visitor finds the idea in `README.md`, the rules in `spec/`, the code in `packages/`, the site in `apps/web/`, and the organization in `docs/governance/`. Names are final unless an ADR changes them.

## 1. Tree

```
symnoesis/
├── README.md                    # what, why, quick start (< 5 min to first success)
├── CLAUDE.md  AGENTS.md         # agent constitution; pointer
├── LICENSE                      # Apache-2.0 (code)
├── LICENSE-DOCS                 # CC BY 4.0 (spec, docs, site content)
├── CITATION.cff                 # validated
├── CHANGELOG.md                 # Keep a Changelog
├── ROADMAP.md                   # phases 0 to 6, status per phase, honest
├── CODE_OF_CONDUCT.md           # Contributor Covenant 2.1
├── CONTRIBUTING.md  GOVERNANCE.md  SECURITY.md  SUPPORT.md  MAINTAINERS.md  TRADEMARK.md
├── ORG_FACTS.yaml               # every org claim, each with verified: bool
├── Makefile  .editorconfig  .gitignore  .gitattributes  .pre-commit-config.yaml
├── .github/
│   ├── workflows/               # ci, mutation, security, scorecard, pages, release, repro
│   ├── ISSUE_TEMPLATE/          # bug, spec-question, research-proposal, accessibility
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS  dependabot.yml  FUNDING.yml (only if funding exists)
├── spec/
│   ├── SPEC.md                  # canonical
│   ├── CHANGELOG.md             # spec history
│   ├── config/symn-01.v0.1.yaml
│   ├── schemas/*.schema.json    # one per entity
│   ├── vectors/*.json           # golden vectors (generated, committed)
│   ├── domains/*.yaml           # learning, coding, health-information, advice-companionship
│   ├── instruments/*.yaml       # item definitions, scoring formulas, license status
│   ├── portal/portal-model.v0.1.json   # E0 item→variable weights, with rationale per weight
│   └── modules/*.md             # SYM-COG, EPI, AFF, SAF, MCH, REC protocols
├── rfcs/                        # 0000-template.md; numbered proposals
├── packages/
│   ├── py/                      # distribution `symnoesis`
│   │   ├── pyproject.toml  uv.lock  README.md
│   │   ├── src/symnoesis/…      # see Architecture §4
│   │   └── tests/{unit,property,golden,e2e}/
│   └── ts/                      # `@symnoesis/core`
│       ├── package.json  tsconfig.json  README.md
│       ├── src/…  tests/
├── apps/
│   └── web/
│       ├── astro.config.mjs  package.json
│       ├── public/{data/,fonts/,favicon.svg,robots.txt}
│       ├── src/
│       │   ├── content/{docs,research,pages,claims.yaml}
│       │   ├── components/      # Map, Legend, PixelPopover, NeighborsPanel, EvidenceBadge, …
│       │   ├── layouts/  pages/  styles/{tokens.css,tokens.json,base.css,…}
│       │   └── lib/             # artifact loaders (zod), formatting (Intl)
│       └── tests/{e2e,a11y,visual}/
├── data/
│   ├── fixtures/                # synthetic, labeled; fictional system names
│   └── releases/<run_id>/       # manifests, maps, covers, cards, hashes
├── docs/
│   ├── agent/                   # the build pack (this directory's siblings)
│   ├── adr/                     # 0001-… (MADR)
│   ├── design/plan.md           # design plan + self-review
│   ├── guides/                  # Diátaxis: tutorials/, how-to/, reference/, explanation/
│   ├── governance/              # charter, council, ethics, disclosure, coi, funding, data-policy, privacy, zones
│   └── build-log/               # session entries, OPEN_QUESTIONS.md, assets/
├── research/
│   ├── LOG.md  prior-art.md  questions.md  references.bib
│   ├── literature/  preregistrations/TEMPLATE.md  protocols/  experiments/
├── scripts/                     # spec_coverage.py, gen_vectors.py, gen_types.sh, check_refs.py
├── tools/                       # check-contrast.ts, cvd-sim.ts, vale/Symnoesis/, lychee.toml
└── docker/api.Dockerfile
```

## 2. Makefile (all targets required by the end of M10)

`setup`, `lint`, `test`, `mutation`, `vectors`, `vectors-check`, `gen` (types from schemas), `build`, `e2e`, `a11y`, `perf`, `links`, `repro`, `docs`, `site`, `verify` (runs everything in order), `clean`. Every target exits non-zero on failure. `make help` prints a one-line description per target.

## 3. Root files: content requirements

**README.md**, in this order: one-sentence definition; why it exists (three sentences); a rendered image of the map (SVG generated from a synthetic artifact, labeled E1); status table (spec, core, site, portal, index, human validation: each with an honest state); quick start (`git clone`, `make setup`, `symnoesis sweep --fixture fixture-a`, `symnoesis map …`, open the site locally) that works in under five minutes; how to cite; how to contribute; license; "An initiative by HarVa Groups". No badges beyond CI, license, and release. No marketing language.

**CITATION.cff:** `cff-version`, `title`, `abstract`, `authors` (only verified, consenting people or the organization name), `repository-code`, `license`, `version`, `date-released`, `keywords`. Validate with the official validator in CI.

**ROADMAP.md:** the seven phases with *status* (not started, in progress, done) and what evidence would mark each done. Phase 3 onward are marked "requires ethics approval and funding".

**CONTRIBUTING.md:** setup, gate commands, commit style, how to propose a spec change (RFC), how to add an instrument, how to report a problem, expectations for tests, review process, how decisions are made (links to GOVERNANCE).

**SECURITY.md:** supported versions; private reporting route (contact from `ORG_FACTS.yaml` or GitHub private vulnerability reporting); response targets; scope (code, site, API; not model behavior reports, which go to disclosure policy); safe-harbor language reviewed by counsel.

**SUPPORT.md, MAINTAINERS.md:** only verified, consenting names.

**TRADEMARK.md:** policy for the names "Symnoesis", "SYMN-01", "Symnoesis Card", "Symnoesis Index"; allowed nominative use; "Symnoesis Certified" reserved and unavailable until a certification program exists. Flag for counsel review.

**ORG_FACTS.yaml:** schema:

```yaml
organization:
  name: { value: "HarVa Groups", verified: true }
  legal_status: { value: null, verified: false }      # e.g. registered nonprofit type and jurisdiction, once true
  jurisdiction: { value: null, verified: false }
  registration_id: { value: null, verified: false }
  contact: { general: null, security: null, ethics: null, verified: false }
people: []        # each: name, role, consent: true, verified: true
funders: { value: null, verified: false }   # null = unknown; [] = none
partners: []
endorsements: []
```

The site and docs render an organization fact only when `verified: true`; otherwise the surface is omitted, never filled.

**apps/web/src/content/claims.yaml:** every claim shown on the site:

```yaml
- id: C-001
  text: "SYMN-01 places each dyad-window on a 256-state map."
  basis: spec            # spec | artifact | reference | org-fact
  ref: "spec/SPEC.md#4"
  tier: E0
```

The site build resolves each `claim` component reference and fails on a missing ID.

## 4. ADR and RFC process

- **ADR (`docs/adr/NNNN-title.md`, MADR):** any decision that affects architecture, dependencies, or interpretation of the spec. Includes context, options, decision, consequences. Seed ADRs are listed in `14_DECISIONS.md`.
- **RFC (`rfcs/NNNN-title.md`):** any change to normative spec content, weights, thresholds, zones, CHI list, or public claims policy. Requires SAB review (or, before the SAB exists, a named maintainer review plus a 14-day comment window) and a spec version bump.

## 5. Branching and releases

Trunk-based with short-lived branches; squash merges with Conventional Commit titles; `main` protected. SemVer for the spec, the Python package, and the TS package, tracked independently but listed in a compatibility table in the README (`spec 0.1.x ↔ py 0.1.x ↔ ts 0.1.x`). A tagged release attaches: wheels and sdist, npm tarball, SBOM, checksums, rendered spec PDF, and release notes. Zenodo archiving is enabled by a maintainer.

## 6. Documentation set (user-facing, Diátaxis)

- **Tutorials:** "Run your first synthetic sweep"; "Read a Symnoesis Card"; "Find your pixel".
- **How-to:** add an instrument; add a domain; calibrate a judge; build a Card; run a reproducibility check; deploy the site.
- **Reference:** CLI; config keys; schemas; API; zones and required actions; CHI list; module protocols; glossary.
- **Explanation:** the Dyadic State; why a Gray-coded map; evidence tiers; why the gate is a ceiling; limits of the map; privacy design; how this relates to other benchmarks.

## 7. Whitepaper

`research/whitepaper/` holds "The Dyadic State: a framework for measuring long-term human-AI interaction" (Markdown source, build to PDF and web). Sections: motivation; related work (from verified prior art); definitions; the map; scoring and gating; minimal failure cover; evidence tiers; privacy and ethics; threats to validity (including every item in the spec's resolved-ambiguity table); validation plan; limitations; availability. No empirical results of real systems.
