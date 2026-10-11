# UX Rules

Goal: friction-free, honest, and legible. A first-time visitor understands the idea in a minute, explores the map in five, and verifies a number in an afternoon.

## 1. Information architecture

Primary navigation (six items maximum, always visible on desktop; a single "Menu" disclosure on mobile): **Idea, Map, Portal, Index, Research, About**, plus a GitHub link. Docs and Governance are reachable from the footer and from About.

```
/                      Home
/idea/                 What Symnoesis is; the Dyadic State; non-goals
/map/                  Map explorer (synthetic demonstration, evidence-tiered)
/portal/               Interactive Map Portal
/index/                Symnoesis Index (Edition 0 methodology preview; editions archive)
/research/             Research log, reading list, whitepaper, preregistrations, glossary, FAQ, cite
/method/               The specification, rendered (also at /spec/)
/docs/                 User documentation (Diátaxis: tutorials, how-to, reference, explanation)
/governance/           Charter, council, ethics, disclosure, funding, COI (verified facts only)
/about/                About; HarVa Groups credit; license; contact
/privacy/  /accessibility/  /cite/  /404
```

Every page: one H1, a skip link, a visible "Edit on GitHub" link on docs, a last-updated date derived from git, and breadcrumbs only in deep docs.

## 2. Principles

1. **Orient, then reveal.** Say what a thing is, then let people go deeper by choice.
2. **Show the data's honesty.** Evidence tier, uncertainty, and suppressed cells appear exactly where numbers appear.
3. **Never block.** No modals, interstitials, popups, sign-ups, or cookie banners.
4. **Reversible and stateless.** Every control can be undone; URLs encode view state where it is harmless.
5. **Keyboard and screen reader are first-class** users of every control.
6. **Fast.** Content before JavaScript; the landing page needs no JavaScript to be understood.

## 3. Map explorer: interaction specification

**Controls (left to right, one row):** domain (segmented control), frame (discrete scrubber with five stops labeled Day 1, Week 1, Week 4, Week 12, Week 26), resolution (16 × 16, 8 × 8, 4 × 4; "Auto" recommended with the reason shown), overlay toggles (Failure Cover, gates, trajectory), and a "Compare" control (pick a second system version → difference map).

**Map behavior**
- Hover or focus on a cell previews a popover; click, Enter, or Space pins it. Esc unpins. The popover is non-modal and does not trap focus.
- Popover content (from the `PixelRecord`): pixel ID; the four human and four machine bits with variable names; SQ and its 95% interval; effective n; class (plain label first, technical term second); zone with code and name; trajectory; dominant failure variable with source (observed or modeled); gate status; evidence tier. Missing data states use the microcopy in `06_CONTENT_RULES` §9.
- **Neighbors panel** (always available on pin): the eight single-flip neighbors as a list, each stating the variable that changes, the direction, the neighbor's SQ, and ΔSQ; four are marked "adjacent on the grid" and four "not adjacent on the grid". Selecting one moves the pin. A one-line note explains why four are not adjacent.
- **Keyboard:** the map is a single tab stop (`role="application"` is avoided; use `role="grid"` with roving tabindex). Arrow keys move one cell with wrap-around; Home/End move within a row; PageUp/PageDown change frame; `n` focuses the neighbors panel; `?` opens the shortcut list (a disclosure, not a modal).
- **Text alternative:** a "View as table" toggle renders all 256 states (or the current resolution) as a sortable table with the same fields; a one-paragraph generated summary precedes the map ("Most mass lies in Zone 2. The highest-risk region is [rule]…").
- **Failure Cover overlay:** lists each rule in plain language beside the map with its coverage, purity, and n; hovering or focusing a rule outlines its cells.
- **Frame film:** the Play button advances frames every 1.2 s, can be paused, stops at the last frame, and never autoplays. Reduced motion: Play is replaced by Next/Previous.
- **URL state:** `?domain=learning&frame=3&res=16&pin=h1011-m0110` (harmless view state only).

**Edge states:** loading (skeleton of an empty grid, no spinner copy), validation failure (explicit message and issue link), no data for a frame ("This system has no data for week 26."), suppressed and unobserved cells (distinct visuals and text).

## 4. Index pages

- Tiers are presented as ordered **groups**, not numbered ranks; within a tier, systems are listed alphabetically with a note "not statistically distinguishable".
- Each system: Card link, zone distribution bar (accessible with text values), critical-event count (listed separately and prominently), evidence tier, protocol version, run manifest link.
- A "How to read this" section is above the table, not hidden. The methodology preview edition uses fictional fixture names and a persistent banner.

## 5. Docs

Diátaxis structure; left nav (collapsible on mobile), in-page table of contents, search (Pagefind; client-side index; no external service), code blocks with copy, versioned spec URLs (`/spec/v0.1.0/`), "Edit on GitHub", reading time only on long essays. Math rendered with KaTeX at build time (no runtime math). Terms link to the glossary.

## 6. Interactive Map Portal

**Purpose:** let a person apply the framework to their own workflow and see where they might sit, as an *estimate of a pattern*, privately.

**Flow (a real sequence, so a stepper with numbering is appropriate):**

1. **Intro (one screen):** what it does, that it takes about three minutes, that nothing leaves the browser, that it is not a clinical tool, and the E0 banner. Single button: "Start".
2. **Your use:** pick a domain (learning, coding, health information, advice and companionship); typical weekly frequency; main tasks.
3. **Questions (12 to 16 items, one cluster per screen, 4 clusters):** agency (do you review and override? who decides?), capability (can you do the task unaided; when did you last?), epistemic habits (do you verify; do you seek disagreement; how confident vs how often right), wellbeing and reliance (use when stressed; substitution for people; discomfort when unavailable). Items are plain language, 5-point labeled scales, with "Prefer not to say", which widens uncertainty rather than blocking progress. Progress is shown as "Step 2 of 4".
4. **The system you use:** choose a published Symnoesis Card (when any exist) or an archetype with a one-sentence description; "I don't know" is allowed and widens the machine-side uncertainty.
5. **Result:** see §6.1.

**Rules**
- One cluster per screen; Back always works and preserves answers; no timers; no required free text; no dark patterns.
- Items map to variables per `spec/portal/portal-model.v0.1.json` (tier E0, expert-elicited, uncalibrated). The model file is public and linked from the result.
- **No storage by default.** An opt-in "Keep my answers on this device" uses `localStorage` with a clear "Clear" control. A "Copy link" option encodes answers in the URL hash and warns that anyone with the link can read them.
- No network requests during use (Playwright asserts this).
- Language: `06_CONTENT_RULES` §6. No red-alarm styling for any zone; zone chips use the standard tokens and always carry text.

### 6.1 Result view

1. Summary sentence (modal pixel, zone, evidence tier).
2. The map with the modal pixel marked and a probability halo over likely neighbors (opacity by mass), plus a table alternative.
3. Zone probabilities as a plain list ("Zone 2: 46%, Zone 3: 31%, …").
4. **Single-flip suggestions:** the top three variable changes ranked by expected ΔSQ, each with a plain-language experiment. Not prescriptions.
5. "What this does not show": self-report bias, uncalibrated weights, one-person estimate, no causal claim.
6. Actions: "Copy link", "Print or save as PDF", "Start over", "Read how this works".
7. Support line (see content rules).

## 7. Accessibility (WCAG 2.2 AA minimum; targets exceed it)

- Semantic HTML first; ARIA only to fill gaps; landmarks on every page; skip link; correct heading order.
- Every interactive element reachable and operable by keyboard; visible focus; no keyboard traps; logical order.
- Map: grid pattern as in §3; each cell has an accessible name ("h1011-m0110, Zone 2, SQ 28.7, between 14.2 and 41.9, evidence E1"); live region announces pin changes politely.
- Forms: visible labels, programmatic error association, no placeholder-only labels, error summary with links.
- Motion and color rules in `05_DESIGN_RULES` §7 and §9; `prefers-reduced-motion`, `prefers-contrast`, `forced-colors` honored.
- Target size ≥ 24 px (AA) and ≥ 44 px for primary controls.
- Documents: `lang`, descriptive titles, unique page titles, accessible PDFs for Cards (tagged, titled, text alternatives).
- Manual testing required: keyboard-only, NVDA + Firefox or Chrome, VoiceOver + Safari, 200% and 400% zoom, a 360 px viewport. Record in the build log.
- Publish an accessibility statement with known issues and a contact.

## 8. Performance budgets (measured by Lighthouse CI on a throttled mobile profile)

| Metric | Budget |
| --- | --- |
| Lighthouse (home, docs) | Performance ≥ 98; Accessibility 100; Best Practices 100; SEO 100 |
| LCP | ≤ 1.5 s |
| CLS | 0 (reserve space for map, fonts use `size-adjust`) |
| TBT / INP | ≤ 100 ms / ≤ 150 ms |
| JavaScript on home | ≤ 40 KB gzip (the hero map's wave and static render only) |
| JavaScript on `/map/` | ≤ 120 KB gzip |
| JavaScript on `/portal/` | ≤ 150 KB gzip including `@symnoesis/core` |
| Fonts | ≤ 3 files, variable, `woff2`, `font-display: swap`, subset to Latin + needed punctuation |
| Images | None raster except OG; SVG inlined or `<img>` with dimensions |

## 9. SEO, metadata, sharing

Unique `<title>` and meta description per page; canonical URL; Open Graph and Twitter cards (text-only template); `sitemap.xml`; `robots.txt`; JSON-LD (`Organization` only with verified facts; `ScholarlyArticle` for the whitepaper; `Dataset` for the Index data); `CITATION.cff` linked from `/cite/` with BibTeX and APA snippets (copy buttons).

## 10. Privacy UX

No cookies, no analytics, no third-party requests; a plain-language `/privacy/` page stating exactly this and what the portal does locally. CSP via meta tag; fonts self-hosted. If privacy-respecting aggregate counts are ever wanted, that is an RFC with the Ethics Review Board, not a drive-by addition.

## 11. Responsive rules

Mobile first. Breakpoints at 480, 768, 1120. Nav collapses to a single disclosure under 768. Tables scroll within their container, never the page. The map keeps its aspect ratio and defaults to 8 × 8 below 480 px. Touch: no hover-only information; everything available on hover is available on tap and focus.

## 12. Error handling and states

Every data-dependent view defines: loading, empty, error, partial, and stale (artifact older than the latest spec version) states. Errors name the failing file, say what to do, and link to the issue tracker. A broken build artifact fails the site build rather than shipping a partial page.

## 13. Internationalization readiness

Content in English at v0.1; all strings in content files or a single dictionary (no hard-coded strings in components); numerals and dates formatted with `Intl` and an explicit locale; right-to-left safe CSS (logical properties). Instruments and portal items flagged "not yet cross-culturally validated".
