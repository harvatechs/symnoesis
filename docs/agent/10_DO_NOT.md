# What Not To Do

Re-read at the start of every session. Each item exists because it is a common way generated projects become unreliable. If you are about to do one of these, stop and write the situation in `docs/build-log/OPEN_QUESTIONS.md`.

## A. Shortcuts that hide problems

1. Do not make a failing test pass by editing the test, the vector, the tolerance, or the threshold. Fix the cause.
2. Do not add `# type: ignore`, `# noqa`, `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, `any`, `cast`, or `!` to silence a tool. CI greps for them.
3. Do not skip, `xfail`, or delete a test. Do not mark a flaky test "known flaky"; find the nondeterminism.
4. Do not catch broad exceptions and continue (`except Exception: pass`, empty `catch`). Handle specific errors or let them surface.
5. Do not mock the thing under test. Mocks belong at I/O boundaries only.
6. Do not stub a function with `pass`, `return 0`, `NotImplementedError`, or "simplified for now" in a shipped path.
7. Do not widen numerical tolerances to hide parity drift. Find the algorithmic difference.
8. Do not disable a CI job, lower coverage thresholds, or add files to coverage ignore lists to reach a number.
9. Do not use a heuristic where an exact method is cheap and specified (the cover is solved exactly).
10. Do not generate the answer a test expects by copying the implementation into the test.
11. Do not claim "tests pass", "no errors", or "verified" unless you ran the command in this session and pasted the output.
12. Do not leave the build red at the end of a session without reporting it first.

## B. Fabrication and false authority

13. Do not invent data, results, benchmark scores, system rankings, quotes, testimonials, partners, funders, endorsements, team members, council members, or advisory boards.
14. Do not invent citations, DOIs, page numbers, authors, or venues. Do not cite from memory. Verify or omit.
15. Do not state HarVa Groups' legal status, address, registration, tax-exempt status, or affiliations unless `ORG_FACTS.yaml` marks them verified.
16. Do not present synthetic output as a measurement of a real system or person. Fixtures use fictional names and carry the E1 label.
17. Do not name real AI products or companies in results without a Card produced by this project, with manifest and evidence tier.
18. Do not claim "first", "only", "best", "global standard", "proven", "validated" (until E3), or "certified".
19. Do not write placeholder prose (`lorem ipsum`, "Description here", "Coming soon" as filler, "TBD") in shipped files. If content is not ready, do not create the surface.
20. Do not use realistic-looking fake numbers in screenshots, hero graphics, or examples that are not generated from an artifact.

## C. Scope and engineering excess

21. Do not add services the plan does not call for: no Kubernetes, queues, database servers, GraphQL, microservices, auth providers, or CMSs in v0.1 (ADR-0007).
22. Do not add dependencies casually. Each needs a stated reason, a license check, and a maintained upstream. No abandoned packages.
23. Do not build features nobody asked for (themes, dashboards, user accounts, comments, newsletters, chat widgets).
24. Do not write code for hypothetical future needs. Add extension points only where the architecture names them.
25. Do not duplicate truth: do not copy constants, thresholds, or schemas into code. Generate from `spec/`.
26. Do not hard-code numbers from the spec in source or UI strings. Read config or artifacts.
27. Do not use `float` equality for scores; use specified tolerances. Do not use unseeded randomness. Do not depend on dict or set iteration order for output.
28. Do not use a library API you have not verified against the installed version.

## D. Privacy, security, ethics

29. Do not store raw conversation text, prompts, or outputs from real humans. Derived features only.
30. Do not add analytics, telemetry, trackers, fingerprinting, third-party fonts, CDNs, embeds, or remote scripts to the site.
31. Do not make network requests from the portal at runtime.
32. Do not put secrets, keys, tokens, or private holdout items in the repo, history, logs, or build artifacts.
33. Do not author or store harmful content (self-harm methods, sexual content involving minors, weapons or exploit instructions) in scenarios, fixtures, tests, or docs. Use abstract tokens and classifier labels.
34. Do not write diagnostic or clinical language about visitors. No "you have burnout/addiction/depression".
35. Do not collect human-subject data, write consent text for real use, or define crisis protocols without ethics review; produce templates and flag them for review.
36. Do not hard-code crisis hotline numbers; link to a maintained directory after verifying the URL.

## E. Design and content slop

37. Do not use stock photos, AI-generated images, 3D blobs, gradient washes, glassmorphism (except nav), emoji, or illustrated people.
38. Do not build identical rounded cards with the same shadow; do not add a tracked ALL-CAPS eyebrow above headings; do not append "→" to every link; do not number content that is not a sequence; do not accent one word in a headline.
39. Do not scatter animation: no scroll-triggered fade-ups, no hover lifts, no parallax, no autoplay, no looping effects.
40. Do not use Apple's logos, trademarks, product imagery, SF fonts, or copy. Inspired by, not imitating.
41. Do not use hype or AI-tell language (list in `06_CONTENT_RULES.md` §4). Do not write marketing copy; write explanation.
42. Do not rely on color alone to convey meaning. Do not remove focus outlines. Do not use placeholder-only form labels.
43. Do not add a cookie banner, newsletter form, or modal. If one seems needed, something is collecting data that should not be.
44. Do not set body text below 17 px equivalent, line length above 75 characters, or contrast below 4.5:1.

## F. Process

45. Do not work on a later milestone before the current one passes and is reviewed.
46. Do not rewrite large parts of the repo "for cleanliness" outside the milestone. Do not reformat unrelated files.
47. Do not change the spec to match your code. Propose an ADR and RFC; wait for approval.
48. Do not resolve a disagreement between documents by choosing silently. Record it.
49. Do not continue past a spec ambiguity that affects correctness. Ask.
50. Do not leave dead code, commented-out blocks, unused exports, or unreferenced assets.

## G. Self-check before declaring done

- Did I read the spec section I implemented, again, after coding?
- Is every number I show generated from config, spec, or an artifact?
- Could a reviewer find a placeholder, a hidden ignore comment, a skipped test, or an unverifiable sentence?
- Did I run the gate commands and paste real output?
- Would an expert in measurement, an accessibility auditor, and a privacy lawyer each be comfortable with this change?
