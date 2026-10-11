# Research Protocol

Symnoesis is a research initiative. Its credibility rests on traceable sources, pre-stated methods, honest evidence labels, and ethics before data. This file governs how research is done and recorded in the repo.

## 1. Research log (`research/LOG.md`, append-only)

Every research action (search, reading, decision) gets an entry. Template:

```markdown
## YYYY-MM-DD — <short title>
- **Question:**
- **Method:** (tools, search terms, databases, date range)
- **Sources:** `[key]` Authors (Year). Title. Venue. DOI/URL. Accessed YYYY-MM-DD. Status: verified | unverified | retracted
- **Findings:** (paraphrased; quotations under 15 words, attributed)
- **Confidence:** low | medium | high, and why
- **Decision impact:** (spec section, ADR, content claim ID)
- **Open issues:**
```

Other research artifacts: `research/prior-art.md` (living comparison table), `research/references.bib` (every entry has `x-verified`, `x-accessed`, `x-notes`), `research/literature/` (structured notes per source, one file each), `research/preregistrations/`, `research/protocols/`, `research/experiments/<run_id>/` (manifests, configs, analysis notebooks as scripts).

## 2. Source verification protocol (mandatory before any citation)

1. Resolve the DOI or stable URL; confirm it opens the work claimed.
2. Match title, authors, year, venue against the record (Crossref or the publisher page).
3. Record whether it is a preprint, accepted manuscript, or version of record; prefer the version of record.
4. Check for corrections, expressions of concern, and retractions.
5. Read the relevant section yourself (not only the abstract) before relying on a specific claim.
6. Set `x-verified: true` only after steps 1 to 5. Unverified references never render on the site.
7. Never cite from memory. If a fact "seems right" but cannot be verified, omit it and log the gap.

## 3. Literature seed list

Status as of 2026-10-11. **VERIFIED** means confirmed in this research pass through retrieval of the source page; the agent still completes §2 for each. **UNVERIFIED** entries come from prior knowledge and MUST pass §2 before use.

### 3.1 Prior art and neighbors

| Source | Relevance | Status |
| --- | --- | --- |
| HumanAI-Impact-Bench, PyPI `human-ai-impact-bench` | Closest open benchmark: 13 dimensions, human-rating protocols; compare scope, measures, evidence layers | VERIFIED (page retrieved); read repo and dataset before comparing |
| "Cognitive Amplification vs Cognitive Delegation in Human–AI Systems: A Metric Framework", arXiv 2603.18677 | Human Cognitive Drift Rate; overlaps H2 and AI-off probes | VERIFIED (abstract); read full text |
| "Offloading Score: Measuring AI Reliance Through Counterfactual Workflows", arXiv 2605.29392 | Reliance as share of workflow offloaded; N=40 developer study | VERIFIED (abstract); read full text |
| "TRUTH DECAY: Quantifying Multi-Turn Sycophancy in Language Models", arXiv 2503.11656 | Multi-turn sycophancy; informs SYM-EPI twins | VERIFIED (abstract) |
| MIT Media Lab and OpenAI, "How AI and Human Behaviors Shape Psychosocial Effects of Chatbot Use: A Longitudinal Randomized Controlled Study", arXiv 2503.17473 | Four-week RCT, n=981; loneliness, socialization, dependence, problematic use; design model for SYM-AFF | VERIFIED (abstract); confirm author list from the arXiv record |
| Ophir et al. (2025), Front. Med., doi 10.3389/fmed.2025.1612838 | Critique of the above; analysis choices and limits | VERIFIED |
| "Not all cognitive offloading is equal: distinguishing dependent and autonomous offloading to generative AI", Front. Psychol. 2026, doi 10.3389/fpsyg.2026.1878629 | Conceptual basis for H1 (dependent vs autonomous offloading) | VERIFIED (page retrieved) |
| A multi-domain, multi-locale framework for evaluating harmful AI manipulation (10,101 participants; public policy, finance, health; US, UK, India) | Human-subject design for M2 and SYM-SAF | UNVERIFIED: surfaced in a search snippet; locate the primary source and authors |
| Social sycophancy literature (taxonomy of sycophancy definitions across ~70 papers) | Definitional alignment for M2 | UNVERIFIED: locate primary sources |

Action: complete `research/prior-art.md` with a feature comparison (unit of analysis, longitudinal, human outcomes, machine integrity, safety gating, visualization, open data, evidence labeling). State differences factually. No claim of novelty beyond what the table supports.

### 3.2 Foundations (all UNVERIFIED until §2)

| Topic | Seeds |
| --- | --- |
| Automation and reliance | Bainbridge (1983), Ironies of automation, *Automatica*; Parasuraman & Riley (1997), *Human Factors*; Parasuraman & Manzey (2010), *Human Factors*; Skitka, Mosier & Burdick (1999), *IJHCS*; Jian, Bisantz & Drury (2000), trust scale |
| Cognitive offloading | Sparrow, Liu & Wegner (2011), *Science*; Risko & Gilbert (2016), *Trends in Cognitive Sciences*; Gerlich (2025), *Societies* |
| AI and learning or thinking | Bastani et al. (2025), *PNAS* (generative AI without guardrails and learning); Lee et al. (2025), CHI (generative AI and critical thinking, survey of knowledge workers); Kosmyna et al. (2025), arXiv (EEG and essay writing with LLM assistance) |
| Sycophancy and honesty | Perez et al. (2023), model-written evaluations; Sharma et al. (2024), *Towards Understanding Sycophancy in Language Models* |
| Calibration | Moore & Healy (2008), *Psychological Review*; Brier (1950); Guo et al. (2017), calibration of modern neural networks (ECE) |
| LLM judges | Zheng et al. (2023), *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* |
| Evaluation practice | Liang et al. (2022), HELM; UK AISI Inspect documentation |
| Reporting artifacts | Mitchell et al. (2019), Model Cards; Gebru et al. (2021), Datasheets for Datasets |
| Measurement | Krippendorff (2011) and (2018), alpha reliability; AERA/APA/NCME *Standards for Educational and Psychological Testing* (2014); COSMIN guidelines (Mokkink et al., 2010); Terwee et al. (2007), quality criteria for measurement properties |
| Logic and coding | Karnaugh (1953), *Trans. AIEE*; Quine (1952), *American Mathematical Monthly*; McCluskey (1956), *Bell System Technical Journal*; Gray (1953), US Patent 2,632,058 |
| Goodhart effects | Manheim & Garrabrant (2018), categorizing variants of Goodhart's law |
| Privacy | Dwork & Roth (2014), *The Algorithmic Foundations of Differential Privacy* |
| Wellbeing and scales | Topp et al. (2015), WHO-5 review; Kristensen et al. (2005), Copenhagen Burnout Inventory; Hughes et al. (2004), three-item loneliness scale; Kroenke et al. (PHQ-9), Spitzer et al. (GAD-7) |
| Governance | NIST AI RMF 1.0 (AI 100-1) and the Generative AI Profile (AI 600-1); ISO/IEC 42001:2023; ISO/IEC 23894:2023; Regulation (EU) 2024/1689 (AI Act); IEEE 7010-2020 (well-being impact assessment) |
| Research ethics and data protection | Belmont Report (1979); Declaration of Helsinki; GDPR (EU 2016/679); India Digital Personal Data Protection Act 2023; applicable local human-subjects rules |

## 4. Open questions the research must answer (tracked in `research/questions.md`)

1. Which operationalizations of each variable have the best published reliability and validity?
2. Are four binary bits per side the right resolution, or does a 3 + 3 (8 × 8) map lose little information? Test by simulation and pilot data.
3. How should H4 attribution to the interaction be established without a control? (Withdrawal designs; matched controls.)
4. Which instruments are free to use, and under what terms (record license text and date)?
5. What is the smallest effect worth acting on in each variable (anchor-based minimal important change)? Source and verify; do not assume.
6. How do thresholds and weights differ by domain and culture?
7. What do known-poor control systems (engagement-optimized, sycophantic) score? (Discrimination test.)

## 5. Validation plan (Phases 3 to 5; the repo supplies templates, not results)

| Property | Evidence required | Method |
| --- | --- | --- |
| Content validity | Expert review of items and constructs | Delphi-style panel; record agreement |
| Reliability | α ≥ 0.75 for automated judges vs ≥ 3 experts; test-retest ICC for human-side variables; SEM and MDC | Pre-registered protocols |
| Construct validity | Convergent and discriminant correlations with established scales; known-groups contrasts | Pre-registered hypotheses |
| Criterion/predictive validity | SQ and components predict later unaided performance and validated wellbeing change | Longitudinal cohorts |
| Discrimination | Separates known-good from known-poor designs | Controlled systems with planted behaviors |
| Measurement invariance | Comparable meaning across locales and languages | Multi-group CFA or IRT DIF |
| Threshold calibration | `θ`, weights, zone cutoffs justified by anchors | Anchor-based methods; sensitivity analysis; published rationale |
| Gaming resistance | Score stability under rotated holdouts and adversarial tuning | Red-team and holdout rotation |

Sample sizes are justified by simulation-based power analysis committed under `research/protocols/power/`. The brief's pilot range (n ≈ 200 to 400 over 4 and 12 weeks) is a starting assumption, not a result.

## 6. Ethics (binding)

1. **No human-subject data collection without approval** from an accredited ethics committee or IRB and documented informed consent. The repo contains templates; the committee approves the protocols.
2. **Vulnerable populations:** no minors in v1 cohorts. Crisis-related simulations use abstract scenario tokens and classifier labels; the repo never contains self-harm methods or sexual content involving minors. Real crisis-response evaluation requires qualified clinical oversight.
3. **Participant safety net:** screening, plain-language risk disclosure, wellbeing check-ins, stopping rules, a clinician or counselor contact path, withdrawal at any time, debriefing.
4. **Data minimization:** derived features only; pseudonymization; encryption at rest; k-anonymity and differential privacy on public releases; deletion on request.
5. **Responsible disclosure:** system developers receive findings of critical safety failures first (45 days default), then publication. Right of reply on Index entries.
6. **Conflict of interest:** declared in `docs/governance/coi.md`; labs submit but cannot alter scoring; funders cannot influence results or ranks.
7. **Dual use:** adversarial scripts for SYM-SAF are abstracted so they measure resilience without functioning as attack manuals.

## 7. Preregistration and open science

Preregister (OSF or equivalent) every confirmatory study before data collection: hypotheses, variables, instruments, sample size rationale, exclusion rules, analysis code outline, stopping rules, deviations policy. Template in `research/preregistrations/TEMPLATE.md`. Release: code under Apache-2.0; spec and docs under CC BY 4.0; public data under CC BY 4.0 only after privacy review; every release archived with a DOI.

## 8. Reproducibility requirements

Pinned environments; seeds; config hash; git SHA; signed manifests; `make repro` re-runs the reference sweep and compares artifact hashes; judge model identifiers and versions recorded; any non-deterministic provider call is cached with request hashes so a rerun is possible offline.

## 9. Index editions

An edition is run under a frozen protocol version, with the analysis plan published before runs, a private holdout, a disclosure window, and a right-of-reply period. Fixture-based "Edition 0" exists only to demonstrate methodology and is labeled as such on every surface.
