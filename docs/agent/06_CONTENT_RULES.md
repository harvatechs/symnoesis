# Content Rules

Words are design. They exist to make the project easier to understand and use. A reader who is a scientist, a regulator, or a worried parent should trust the page within ten seconds and still find it true after an hour.

## 1. Voice

Calm, exact, modest, warm. Plain verbs. Short sentences. Say what a thing is and does; do not sell it.

| Do | Don't |
| --- | --- |
| "SYMN-01 measures a person and an AI system together, over weeks." | "A revolutionary paradigm shift in human-AI evaluation." |
| "This map uses synthetic data. It is not a measurement of any real system." | "Powerful insights at a glance." |
| "We have not yet validated these thresholds." | "Industry-leading accuracy." |
| "Your answers resemble a pattern the map calls Dependence." | "You are in the Red Zone for burnout." |

Rules:
- Sentence case for headings, buttons, and labels.
- Active voice. Name the actor. Prefer concrete nouns.
- Average sentence ≤ 20 words; none above 35 without a reason.
- Second person ("you") for the portal and how-to docs; third person for the spec and papers.
- Buttons say what happens: "Explore the Map", "Find your pixel", "Copy citation". The same action keeps the same name everywhere.
- Errors say what happened and how to fix it. They do not apologize and are never vague.
- Empty states say what is missing and what to do.
- Numbers: use real minus signs (−), thin non-breaking space before units, consistent decimals, tabular alignment.
- Spell out acronyms on first use per page. Prefer plain words in headlines; acronyms (SQ, HNE, SNE, MFC) belong in methods.

## 2. Claims policy (binding)

1. **Every empirical or factual claim has a source**: a verified reference, a spec rule, a reproducible artifact hash, or an ID in `apps/web/src/content/claims.yaml`. The site build fails if a rendered claim ID has no entry.
2. **Every number shown is generated from an artifact**, never typed by hand. Examples in prose use values from the spec's worked examples and are labeled as examples.
3. **Evidence tier is shown beside every result** (E0 Specified, E1 Synthetic, E2 Provisional, E3 Validated).
4. **Banned certainty and superlatives:** "first", "only", "best", "world-class", "state-of-the-art", "gold standard", "proven", "guarantees", "eliminates", "revolutionary", "groundbreaking", "cutting-edge", "game-changing", "transformative", "seamless", "unlock", "supercharge", "empower", "leverage" (as a verb), "robust" (unless statistical), "holistic", "next-generation", "AI-powered". "Global standard" is allowed only as "proposed open standard" with the submission status stated.
5. **No clinical or diagnostic language** about visitors: do not write "burnout", "addiction", "disorder", "depression" as a finding about the reader. Write "a pattern the map associates with reduced independence", and show uncertainty.
6. **No claims about machine welfare, consciousness, or feelings.** SNE is operational and the docs say so.
7. **No claims about named real AI products** unless backed by a published Card produced by this project, with the evidence tier and run manifest linked. Fixture systems have fictional names.
8. **Organization facts** (legal status, location, people, funders, partners, endorsements) appear only if `ORG_FACTS.yaml` marks them `verified: true`. Never invent a team, a council, an advisory board, a partner logo, a quote, or a testimonial.
9. **Limitations are part of the page**, not a footer: each result page and every Card has a "What this does not show" section.
10. **Corrections are public**: a `CHANGELOG` and a corrections note when something published was wrong.

## 3. Canonical glossary (use exactly)

| Term | Definition (one line) |
| --- | --- |
| Symnoesis | Any close, long-term cognitive or intellectual interaction between humans and synthetic systems, which may be mutually beneficial, neutral, or harmful to one or both parties. |
| SYMN-01 | The Symnoesis Map Benchmark, version 0.1.0 draft. |
| Dyad | One human paired with one system version. |
| Dyadic State | The measurable condition of a dyad over a time window. |
| Dyad-window | A dyad observed over a window; the unit of analysis. |
| Symnoesis Map | The 16 × 16 Gray-coded grid of 256 dyadic states. |
| Pixel | One state on the map: a unique combination of four human bits and four machine bits. |
| SQ (Symnoesis Quotient) | A score from −100 to +100 for a pixel, capped by the safety gate. |
| HNE / SNE | Human Net Effect / System Net Effect. SNE is operational, not a claim about machine welfare. |
| Safety gate | A ceiling on SQ triggered by a confirmed critical-harm event. |
| Minimal Failure Cover (MFC) | The shortest set of rules that explains where harm concentrates. |
| Single-flip neighbor | A pixel that differs by exactly one variable. |
| Zone (Z1–Z7) | Governance category with required actions. |
| Symnoesis Card | One-page report for a system version. |
| Symnoesis Index | Annual report presenting systems in statistically honest tiers. |
| Evidence tier (E0–E3) | How much real evidence stands behind a result. |
| Operator-blind | A result computed without operator-side data, so some classes cannot be asserted. |

Do not coin synonyms ("score card", "heat grid", "AI health", "symbiosis score").

## 4. AI-writing tells to remove

Delete or rewrite: "delve", "tapestry", "landscape" (as metaphor), "in today's fast-paced world", "it's important to note", "navigate the complexities", "rapidly evolving", "ever-changing", "at the end of the day", "plays a crucial role", "a testament to", "unlock the power", "dive into", "journey" (for non-journeys), "seamless", "empowering", "foster", "ecosystem" (unless literal). Avoid reflexive triplets ("fast, flexible, and friendly"), rhetorical questions as openers, em-dash chains, and bullet lists where a sentence works. Avoid opening a paragraph by restating the heading. Vale enforces the word list (`tools/vale/Symnoesis/`).

## 5. Page copy skeletons

The agent writes final copy under these constraints. Headlines below are proposals; keep the meaning, refine the words, and record changes.

**Home**
- Headline: "Measure the relationship, not just the model."
- Sub: "SYMN-01 is an open specification for evaluating long-term human-AI interaction, one person and one system, over time."
- Primary action: "Explore the Map". Secondary: "Find your pixel".
- Map caption: "Synthetic demonstration data (E1). It is not a measurement of any real system."
- Sections (each one idea, one short paragraph, one link to depth): *Benchmarks measure models. People live with them.* / *The unit is the pair.* / *One step on the map changes one thing.* / *A critical failure cannot be averaged away.* / *Open, versioned, and hard to game.* / *Read the specification, or help test it.*

**Idea page:** problem, definition (with pronunciation and etymology: from Greek *noēsis*, "understanding"; confirm in a reputable dictionary and cite), the Dyadic State, two-sided outcomes, what the project does not claim.

**Map explorer:** how to read the map in four sentences; legend; frame scrubber; domain control; "What this does not show".

**Method:** the spec, rendered; variables; modules; worked examples; limitations; version and change history.

**Index:** "Edition 0 is a methodology preview built from fictional fixture systems." Explain tiering, critical-event listing, disclosure window, and right of reply. Real editions say: "Edition 2027 covers N systems under protocol vX; evidence tier E?".

**Research:** research log, reading list with verification status, preregistrations, glossary, FAQ, how to cite.

**About:** what Symnoesis is, who is behind it (only verified facts), license, governance, funding disclosure, contact.

## 6. Portal copy rules

The result must be **descriptive, conditional, and non-diagnostic**.

- Title: "Where your answers place you on the map".
- Lead: "Based on your answers, the most likely pixel is h1011-m0110, in Zone 2 (Productive). This is an estimate from self-reported habits, not a measurement."
- Always show: evidence tier banner ("Uncalibrated prototype (E0). Weights come from expert judgment and have not been validated against outcomes."), the probability spread (not only the mode), and "What this does not show".
- Suggestions are framed as experiments: "Teams often test one change at a time. The map suggests variable H2 (capability trajectory) is where a change would move your estimate most. One option: schedule a short unaided practice session each week."
- Support: "If you are struggling, you can talk to a professional or find a local helpline at findahelpline.com." (Verify the URL before shipping.) No hotline numbers hard-coded.
- Privacy line, always visible: "Your answers stay in your browser. Nothing is sent or stored."
- Never use second-person verdicts ("You are addicted"), alarm colors alone, countdowns, or urgency.

## 7. Citations and references

- Author–year in text; full list at the bottom; BibTeX in `research/references.bib`.
- Every reference has a resolving DOI or stable URL, an access date, and `verified: true` after a human or agent check of metadata. Unverified references do not render.
- Quotations under 15 words, attributed, with page or section; prefer paraphrase.
- Name studies by their design and size when relevant ("a four-week randomized trial, n=981"), and name known critiques.

## 8. Accessibility of language

Reading level target: grade 9–10 for public pages, technical for spec. Define terms at first use. Link text describes the destination ("Read the specification"), never "click here". Alt text states what the figure shows and why it matters. Every figure has a caption and a text alternative; the map's alternative is a generated table plus a one-paragraph summary.

## 9. Microcopy conventions

| Situation | Pattern |
| --- | --- |
| Empty pixel | "No dyads observed in this state." |
| Suppressed pixel | "Too few dyads to show this state without risking privacy or misleading precision." |
| Low confidence | "Wide uncertainty: SQ between −12 and +41." (numbers from the artifact) |
| Operator-blind | "Operator-side data were not available, so a parasitic pattern cannot be ruled in or out." |
| Synthetic | "Synthetic data (E1)." |
| Load failure | "The data file did not load. Reload the page; if it persists, report it on GitHub." |

## 10. Review checklist for any text

Is it true, sourced, and tiered? Can a sentence be cut? Is there a banned word or a tell? Would a worried reader be misled or frightened? Would an expert find it overclaimed? Is the term canonical? Does the link text say where it goes?
