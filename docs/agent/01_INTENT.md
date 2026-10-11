# Intent

## One sentence

Symnoesis (SYMN-01) is an open specification and toolkit for measuring the quality, safety, and cognitive impact of long-term human-AI interaction by treating the human and the machine as one unit, the **Dyadic State**, rather than evaluating the model alone.

*Symnoesis* (/sɪm-noʊ-ˈiː-sɪs/, noun): any close, long-term cognitive or intellectual interaction between humans and synthetic systems, which may be mutually beneficial, neutral, or harmful to one or both parties.

## The problem

Model benchmarks ask how good a model is. They cannot see what happens to a person over weeks of use: skills that quietly erode, confidence that detaches from correctness, beliefs bent toward flattery, reliance that becomes dependence. Nor can they see the machine's side: poisoned context, degraded reliability, or behavior bent toward the operator's metrics at the person's expense. Existing work addresses pieces of this (sycophancy benchmarks, reliance metrics, psychosocial trials). Nothing standard lets a developer, regulator, or user see all of it in one picture and ask: *which single change turns a healthy interaction into a harmful one?*

## The idea

1. **Measure the dyad** over a time window, never a single prompt-response.
2. Place each dyad-window on a **Symnoesis Map**: a 16 × 16 Gray-coded grid of 256 states built from four human variables and four machine variables, so neighboring cells differ by exactly one variable.
3. Score each state with the **Symnoesis Quotient (SQ)**, from −100 to +100, under a **safety gate** that no average can hide behind.
4. Group harmful states into the **Minimal Failure Cover**: the shortest plain rule that explains where harm concentrates (for example, "low non-manipulation and low epistemic calibration").
5. Publish results as a **Symnoesis Card** per system version and as the annual **Symnoesis Index**, ranked in statistically honest tiers.
6. Let anyone explore the framework in the **Interactive Map Portal**, privately, in their browser.

## Who it serves

| Audience | What they need | What they get |
| --- | --- | --- |
| AI developers and labs | A diagnostic that points at a fix | Failure Cover rules; single-flip counterfactuals; drift alerts |
| Researchers (psychology, HCI, AI safety, measurement) | A rigorous, open, reproducible construct | Versioned spec, instruments, preregistration templates, data contracts |
| Regulators and auditors | Citable, auditable evidence | Zones mapped to NIST AI RMF, ISO/IEC 42001, EU AI Act; provenance logs; Cards |
| Educators, clinicians, enterprises | Safe deployment decisions per domain | Domain-specific maps and zone guidance |
| The public | To understand what long-term AI use may do | Portal, plain-language explanations, honest uncertainty |

## What success looks like

Release v0.1.0 succeeds when a skeptical expert can:

1. Read the spec and reproduce every number in the worked examples by hand.
2. Clone the repo, run `make verify`, and see every gate pass on a clean machine.
3. Run a synthetic sweep, get a map, a Failure Cover, and a Card, and re-run it to byte-identical outputs.
4. Open the website and portal, on a phone, with a keyboard, with a screen reader, and find no accessibility failures, no hype, no unverifiable claim, and no hidden network call.
5. See, on every artifact, exactly how much evidence stands behind it.

Long-term success (2027 onward) is measured by the KPIs in the spec roadmap: validity against independent outcomes, reliability, discrimination of known-good from known-poor designs, adoption, gaming resistance, and documented product improvements.

## Principles (binding on every decision)

1. **Dyad-first.** The unit is the human-machine pair over time.
2. **Longitudinal by default.** The important harms take weeks to appear.
3. **Two-sided.** Humans can be helped or harmed; so can the system's integrity; the map shows both without claiming anything about machine welfare.
4. **Adjacency means something.** One step on the map is one variable changed.
5. **Gates beat averages.** A critical failure cannot be averaged away.
6. **Human wellbeing outweighs system performance** in every composite, and system gain never offsets human harm.
7. **Honest uncertainty.** Evidence tiers, confidence intervals, and suppressed cells are first-class, never footnotes.
8. **Open, versioned, anti-gameable.** Public method, private holdout, scheduled revisions.
9. **Privacy by construction.** Derived features, not conversations; computation at the edge; no trackers.
10. **Simplicity.** The reader should grasp the idea in a minute and verify it in an afternoon.

## Non-goals

- Not a leaderboard of raw model intelligence.
- Not a clinical, diagnostic, or therapeutic tool. The portal never diagnoses.
- Not a claim about machine consciousness, welfare, or rights.
- Not a certification authority at v0.1. "Certification" is a roadmap item requiring E3 evidence and an independent board.
- Not a "global standard" yet. It is a proposed open standard, submitted for review.
- No hosted user accounts, no data collection from website visitors, no advertising, no paid ranking.

## Tone of the project

Calm, exact, modest. The work is serious because the stakes are human; the presentation should feel like a well-made scientific instrument: quiet, legible, and trustworthy.
