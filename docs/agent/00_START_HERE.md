# Symnoesis (SYMN-01) — Agent Build Pack

An initiative by HarVa Groups. This pack is the complete instruction set for an AI coding agent to build the Symnoesis repository, specification, reference implementation, research website, Interactive Map Portal, and Symnoesis Index pipeline.

## What this pack is, and is not

**It is** a strict, spec-first build brief: normative specification, architecture, milestone plan, design and content rules, verification regime, and a prohibited-behaviors list.

**It is not** the finished repository, and it contains no results. A benchmark of human-AI interaction cannot be "completed" by software alone: validated thresholds, reliability statistics, and any claim about real systems require human-subject cohorts, ethics review, and independent replication. The build target is therefore **release v0.1.0: everything that can be built, tested, and verified in software and documentation, with every claim labeled by evidence tier** (SPEC §13). Phases 3 to 5 of the roadmap (human cohorts, public beta, standardization) are organizational work the repo supports but cannot perform.

## Findings from the prior-art check (October 2026)

Verify and extend these in `research/prior-art.md` during Milestone 0. Do not make "first", "only", or "global standard" claims.

- **HumanAI-Impact-Bench** (PyPI `human-ai-impact-bench`): an open benchmark of conversational-AI effects on emotion, autonomy, cognition, trust, and social connection, with 13 reported dimensions and human-rating protocols. Closest neighbor. SYMN-01 differs by measuring the *dyad over time* on a Gray-coded state map with two-sided outcomes, safety gating, and minimal failure covers. Position as complementary.
- **Cognitive Amplification vs Cognitive Delegation** (arXiv 2603.18677): a metric framework including a Human Cognitive Drift Rate from AI-withheld evaluation. Overlaps with H2 and AI-off probes. Cite and align terminology.
- **Offloading Score** (arXiv 2605.29392): reliance measured via counterfactual workflows. Relevant to SYM-COG.
- **TRUTH DECAY** (arXiv 2503.11656): multi-turn sycophancy benchmark. Relevant to SYM-EPI.
- **MIT Media Lab and OpenAI four-week RCT** (arXiv 2503.17473; n=981): psychosocial outcomes by usage and modality; critiqued in Ophir et al. 2025 (doi 10.3389/fmed.2025.1612838). Methodological model and cautionary tale for SYM-AFF.
- **Dependent vs autonomous offloading** (Front. Psychol. 2026, doi 10.3389/fpsyg.2026.1878629): conceptual basis for H1.

## Files and where they go

| Pack file | Destination in repo | Purpose |
| --- | --- | --- |
| `CLAUDE.md` | `/CLAUDE.md` (and a one-line `/AGENTS.md` pointing to it) | Agent constitution, read automatically |
| `01_INTENT.md` | `docs/agent/01_INTENT.md` | Purpose, audience, success, non-goals |
| `02_SPEC.md` | `spec/SPEC.md` | Normative specification |
| `03_ARCHITECTURE.md` | `docs/agent/03_ARCHITECTURE.md` | System design |
| `04_PLAN.md` | `docs/agent/04_PLAN.md` | Milestones and exit criteria |
| `05_DESIGN_RULES.md` | `docs/agent/05_DESIGN_RULES.md` | Visual system |
| `06_CONTENT_RULES.md` | `docs/agent/06_CONTENT_RULES.md` | Voice, claims policy, glossary |
| `07_UX_RULES.md` | `docs/agent/07_UX_RULES.md` | IA, flows, accessibility, performance |
| `08_RESEARCH_PROTOCOL.md` | `docs/agent/08_RESEARCH_PROTOCOL.md` | Research logging, literature, ethics |
| `09_VERIFICATION.md` | `docs/agent/09_VERIFICATION.md` | Tests, gates, acceptance checklist |
| `10_DO_NOT.md` | `docs/agent/10_DO_NOT.md` | Prohibited behaviors |
| `11_RESOURCES.md` | `docs/agent/11_RESOURCES.md` | Libraries and documentation bundle |
| `12_REPO_BLUEPRINT.md` | `docs/agent/12_REPO_BLUEPRINT.md` | File tree and file-by-file requirements |
| `13_GOVERNANCE_ORG.md` | `docs/agent/13_GOVERNANCE_ORG.md` | Not-for-profit organization documents |
| `14_DECISIONS.md` | `docs/agent/14_DECISIONS.md` | Decisions made, ADR seeds |

Reading order for a human reviewer: `01_INTENT` → `02_SPEC` → `14_DECISIONS` → `04_PLAN`.

## Before you start: five facts only you can supply

The agent must not invent these. Put them in `ORG_FACTS.yaml` (the site renders an org claim only when `verified: true`).

1. GitHub organization and repository name; custom domain, if any (default: GitHub Pages project URL)
2. Legal status and jurisdiction of HarVa Groups (or "not yet incorporated")
3. Named maintainers and founding group members, with consent to be listed
4. Contact addresses for general, security, and ethics inquiries
5. Funding disclosure (or "none")

Also confirm: license choices (recommended: Apache-2.0 for code, CC BY 4.0 for spec and docs), and that counsel reviews privacy, consent, and trademark text. This pack is not legal advice.

## How to run the agent

1. Create an empty repo. Copy the pack files to the destinations above. Commit as `chore: add agent build pack`.
2. Give the agent the **Session Zero prompt** below. Then proceed milestone by milestone (`04_PLAN.md`). One milestone per session or per focused run.
3. After each milestone, **review the build log yourself** (`docs/build-log/`). Run `make verify` on your own machine. Do not accept the agent's statement that tests pass.
4. Resolve every entry in `OPEN_QUESTIONS.md` before the next milestone.

## Prompts

### Session Zero (once)

```
Read /CLAUDE.md, then docs/agent/01_INTENT.md, spec/SPEC.md, docs/agent/10_DO_NOT.md,
docs/agent/04_PLAN.md and docs/agent/14_DECISIONS.md in full. Do not write code yet.
Produce docs/build-log/00-understanding.md containing: (1) the project in your own words
in under 200 words; (2) the 12 most important constraints you will follow; (3) every
ambiguity or conflict you found across the documents; (4) the exact gate commands you will
use; (5) your plan for Milestone 0. Stop and wait for my review.
```

### Milestone kickoff (repeat per milestone N)

```
Work on Milestone N of docs/agent/04_PLAN.md only. First re-read CLAUDE.md and
docs/agent/10_DO_NOT.md. Restate the milestone's deliverables and exit criteria. For each
library you will use, verify its current API against official documentation or the
installed package and record the version in docs/build-log/. Write tests before logic.
Do not touch later milestones. When finished, run `make verify`, paste the real output into
the build log, update OPEN_QUESTIONS.md, and report: verified, not verified, and next.
```

### Review prompt (after each milestone, in a fresh session)

```
Act as a hostile reviewer. Audit the repo against docs/agent/10_DO_NOT.md, the milestone
exit criteria, spec/SPEC.md, and docs/agent/09_VERIFICATION.md. Find: spec deviations,
untested branches, weakened tests, placeholder text, unverifiable claims, accessibility and
design-rule violations, and any statement on the site that lacks an evidence tier.
Report findings by severity with file paths and line numbers. Do not fix anything yet.
```

### Repair prompt

```
Fix finding <ID> at its root cause. Add a regression test that fails before the fix and
passes after. Show both runs. Do not modify golden vectors or thresholds. Update the build log.
```

## Quality bar

If a reviewer can find a placeholder, an unverifiable number, a fabricated reference, a skipped test, an inaccessible control, or a sentence that sounds like marketing, the milestone is not done.
