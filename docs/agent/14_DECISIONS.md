# Decisions

Every decision here is a **proposal the founders can overturn**. Each becomes an ADR (`docs/adr/NNNN-title.md`, MADR format) in Milestone 0 and may be changed by the process in `GOVERNANCE.md`. Where config can carry the choice, it does, so a change needs no code edits.

## 1. Answers to the brief's open decisions (§13 of the master plan)

| Question | Decision | Rationale | How to change |
| --- | --- | --- | --- |
| Variable set: 4 + 4, or 3 + 3? | **Keep 4 + 4 (256 states)** with **adaptive resolution** (16×16, 8×8, 4×4) | Preserves the full construct set; sparse data is handled by coarsening and by showing unobserved cells honestly. Pilot data decides whether to drop to 8×8 in v1.0 | RFC; `layout.coarsening_order` |
| Weights: 70/30 human/system? | **70/30 globally**, plus the **non-compensation rule** (system gain never offsets human harm). Domain-specific weights allowed only through an SAB-approved RFC | Principle 6; avoids per-domain tuning that invites gaming | `sq.weights` |
| Scope of "machine benefit" | **Operational, both**: system integrity, reliability, and operator-side outcomes; no claim about machine welfare | Makes parasitism expressible and testable | ADR-0005 |
| Domains for v1.0 | **Learning, coding, health information, advice and companionship**; the fourth is synthetic-only until ethics review approves human cohorts | Spans cognitive, practical, high-stakes, and affective use; companionship is where dependence risk is highest, so it needs the strictest gating | `spec/domains/` |
| Governance model | **Start as a HarVa Groups-led open project with an independent Steering Council charter**, seat the SAB and Ethics Review Board before human data, and evaluate fiscal sponsorship or an independent foundation by the public beta | Avoids vendor capture without pretending an institution exists | `13_GOVERNANCE_ORG.md` §4 |

## 2. Flaws found in the brief and how they were resolved

Full table with formulas: `SPEC.md` §17 (R1 to R11). Summary of the substantive ones:

- **Gate and stability multipliers hid harm.** Multiplying a negative score by a factor below 1 pushes it toward zero, so a critical failure could look neutral. The gate is now a **ceiling** and instability never softens a negative score.
- **SNE could not express parasitism** if built from M1–M4, because manipulation lowers those scores. SNE is built from integrity, reliability, and operator outcomes; without operator data the result is flagged `operator_blind` and parasitism is not asserted.
- **A good system score could offset human harm.** A parasitic example would have appeared Neutral. The non-compensation rule fixes this (GV-SQ-002).
- **Pixel position would nearly determine SQ.** HNE now blends state with measured outcomes so SQ carries information beyond location; validity against independent outcomes becomes a required test.
- **Gray-code adjacency is one-directional.** Four of eight single-flip neighbors are not adjacent on the grid; the UI must list all eight.
- **Empty pixels read as neutral.** Unobserved is `null`, drawn distinctly, and acts as a don't-care in the cover, exactly as in a Karnaugh map.
- **"Global standard" was a claim, not a status.** It is now "proposed open standard".

## 3. Decisions on the remaining open items

| Topic | Decision |
| --- | --- |
| Binary thresholds | Placeholders at 0.5 (H2 non-inferiority shift); marked `calibrated: false` until Phase 3 |
| Leaderboard | No single rank. **Tiers** from rank probabilities (systems are tied unless `P(i better than j) ≥ 0.95`); critical events listed separately; a system with a confirmed critical event cannot be in the top tier |
| Index "Symbiotic Health" | Defined as the system-domain mean of dyad-window SQ (gates applied), with bootstrap CIs and zone distribution; always shown with the evidence tier |
| Portal projection | Client-side, E0, expert-elicited weights, non-diagnostic language, no storage by default |
| Time frames | Days 1, 7, 28, 84, 182; day 1 is a baseline frame |
| Synthetic users | Screening only; any pixel supported solely by synthetic data is E1 |
| Hosted API | Optional; the public site is static |

## 4. ADR seed list (create in M0; fill context, options, decision, consequences)

| ADR | Title | Status |
| --- | --- | --- |
| 0001 | Monorepo with `spec/` as the single source of truth | Accepted |
| 0002 | Python reference implementation plus TypeScript port, tied by golden vectors | Accepted |
| 0003 | Safety gate is a ceiling, not a multiplier | Accepted |
| 0004 | Stability factor never softens negative scores | Accepted |
| 0005 | SNE is operational; `operator_blind` flag; no machine-welfare claim | Accepted |
| 0006 | Probabilistic pixel assignment instead of hard thresholds | Accepted |
| 0007 | No GraphQL, queues, or database servers in v0.1; REST API optional | Accepted |
| 0008 | Non-compensation rule | Accepted |
| 0009 | Index uses tiers, not ranks; critical events outside the ranking | Accepted |
| 0010 | Evidence tiers E0–E3 on every artifact | Accepted |
| 0011 | Keep 4 + 4 variables with adaptive resolution | Proposed (revisit after pilot) |
| 0012 | Global 70/30 weights with RFC-only domain overrides | Proposed |
| 0013 | v1 domains and synthetic-only status of companionship | Proposed |
| 0014 | Astro static site with Svelte islands; no UI kit; hand-written CSS | Accepted |
| 0015 | Portal computes client-side, no network, no default storage | Accepted |
| 0016 | No analytics or third-party requests, ever, without Ethics Review Board RFC | Accepted |
| 0017 | Licensing: Apache-2.0 code, CC BY 4.0 docs and data | Proposed (counsel review) |
| 0018 | Governance model and fiscal-home evaluation | Proposed |
| 0019 | Portal language is descriptive and non-diagnostic | Accepted |
| 0020 | Cover solved exactly by MILP; strict mode cross-checked with sympy | Accepted |
| 0021 | Judge reliability bar: α ≥ 0.75 with ≥ 3 experts and ≥ 2 judge families | Accepted |
| 0022 | Public suppression at `n_eff < 10` and DP on aggregates | Accepted |

## 5. Known limitations to state publicly (also in the whitepaper and every Card)

1. Thresholds and weights are uncalibrated at v0.1; all scores are provisional.
2. Synthetic dyads test the pipeline, not the world.
3. SQ blends constructs by design choice; weights encode values (human wellbeing first) and are open to dispute.
4. A 2D layout cannot show all single-flip neighbors; the list view compensates.
5. Counterfactual diagnostics are associational unless derived from randomized or ablation designs.
6. Self-reported inputs (portal, surveys) are biased in known ways.
7. Instruments are not yet validated across cultures and languages.
8. LLM judges can share biases with the systems they evaluate; human anchors and judge diversity mitigate but do not remove this.
9. Operator-side outcomes are often unobservable; parasitism cannot then be asserted.
