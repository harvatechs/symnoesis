# Design Rules

**Direction:** Apple-inspired calm. Spacious, typographic, quiet, precise. "Inspired by", never "imitating": no Apple logos, trademarks, imagery, product shots, copy, or proprietary fonts.

**One memorable object:** the Symnoesis Map. Everything else stays quiet so the map can be the thing people remember. Spend boldness in one place.

## 1. Before building: the design plan (required, in `docs/design/plan.md`)

Produce a short plan, then critique it before writing code:

1. **Tokens:** 4–6 named base colors, type roles, spacing, radii, motion.
2. **Layout concept:** one sentence per page type plus an ASCII wireframe, with alignment stated.
3. **Principles:** what makes this site recognizably Symnoesis.
4. **Self-review:** for each part of the plan, ask "would I produce this for any research website?" If yes, revise it and write down what changed and why.

### Known defaults to avoid (the common tells of generated pages)

- Warm cream background with a high-contrast serif display and a terracotta accent.
- Near-black background with one acid-green or vermilion accent.
- Broadsheet layout with hairline rules and zero radius.
- The SaaS-card kit: content chopped into identical rounded cards, one radius everywhere, the same soft gray shadow, gradient washes.
- Template chrome: tracked-out ALL-CAPS eyebrow above every heading; meta strings joined by middle dots; "WORD — fragment" labels; a monospace face for small labels; "→" appended to every link and button; icon-in-circle feature grids; numbered 01/02/03 markers on content that is not a sequence.
- Accenting a single word in a headline with italics, bold, or color.
- Fade-and-slide-up on every section; hover lift on every card.

These are not banned individually; they are banned as unexamined defaults. Each use needs a reason recorded in the design plan.

## 2. Principles

1. **Subtract.** Before adding an element, remove one. Every border, label, or ornament must carry information.
2. **Type is the interface.** Hierarchy comes from size, weight, and space, not boxes.
3. **One idea per viewport** on the landing page.
4. **Honesty is visible.** Evidence tier, uncertainty, and unobserved cells are drawn, not hidden.
5. **Quiet motion.** Motion answers a person's action, with one orchestrated exception (§7).
6. **Same system everywhere.** Docs, portal, Cards, and PDFs share tokens.

## 3. Color

Define as CSS custom properties in `apps/web/src/styles/tokens.css` and mirror in `tokens.json` for scripts. Provide light and dark sets; follow system preference; no manual toggle in v0.1. All values below are **proposals the agent MUST validate** (contrast and color-vision-deficiency checks in `tools/check-contrast.ts`); adjust within the stated constraints and record changes.

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--paper` | `#FFFFFF` | `#0E0F11` | Page background |
| `--surface` | `#F5F6F7` | `#17181B` | Quiet panels, code blocks |
| `--line` | `#E3E5E8` | `#2A2C31` | Hairlines |
| `--ink` | `#16181B` | `#F2F3F5` | Primary text |
| `--ink-2` | `#3C4047` | `#C5C8CE` | Secondary text |
| `--ink-3` | `#6B7078` | `#9298A2` | Tertiary text (≥ 4.5:1 on its background) |
| `--accent` | `#2B4EDB` | `#8EA2FF` | Links, primary action, focus, selection |

Constraints: text ≥ 4.5:1; large text and UI components ≥ 3:1; the accent is the **only** non-data hue on the site.

### Data colors (map and charts)

Diverging SQ scale, dark at both ends, light at the center, so **lightness encodes magnitude and hue encodes sign**:

| SQ | −100 | −75 | −50 | −25 | 0 | +25 | +50 | +75 | +100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hex | `#9E3410` | `#C85A33` | `#E48D6C` | `#F0C2AE` | `#E8E9EB` | `#B3D8CE` | `#6DB5A2` | `#2E8F78` | `#006B52` |

Rules:
- Interpolate in OKLab (use `culori`), not RGB.
- **Never rely on hue alone.** Sign is also encoded by a glyph (`+` / `−`) inside cells when zoomed, by pattern in the print and high-contrast modes, and by labels in the legend.
- Run protanopia, deuteranopia, and tritanopia simulations; adjacent steps must remain distinguishable (ΔE in OKLab ≥ 0.04 between consecutive steps) and the two ends must differ in hue *and* remain distinguishable by lightness pattern.
- Zone colors Z1–Z7: use the scale endpoints plus amber `#D69E1F` (Z4), orange `#D9712B` (Z5), gray `#9AA0A8` (Z3), black with hatch (Z7). Zone identity always includes its code ("Z5") and name in text; color is never the only signal.

State encodings on the map:

| State | Encoding |
| --- | --- |
| Unobserved (`n_eff = 0`) | Paper color with a faint diagonal-dot texture; never the neutral gray |
| Suppressed (`n_eff < 10`) | Outlined empty cell with "insufficient data" in the text alternative |
| Low sample | Opacity `clamp(n_eff / 30, 0.35, 1)` |
| Evidence tier | Multiplier E0 0.35, E1 0.7, E2 0.9, E3 1.0, plus a permanent badge |
| Gate critical | 45° hatch, 1 px lines, ink color, on top of fill |
| Gate watch | Corner notch |
| MFC rule | 2 px accent outline; rules that wrap an edge are drawn as split outlines |
| Selected | 2 px ink outline; focus ring is separate (§9) |

## 4. Typography

| Role | Family | Notes |
| --- | --- | --- |
| UI, headings, body | **Inter** (variable, OFL, self-hosted via Fontsource) with the stack `-apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif` | Apple devices render the platform face; others get Inter. Same metrics policy via `size-adjust` fallback to prevent layout shift |
| Long-form reading (whitepaper, essays, spec prose) | **Source Serif 4** (variable, OFL, self-hosted) | Clearly distinct from Inter; slightly more line height |
| Code, pixel IDs | `ui-monospace` stack with **JetBrains Mono** (OFL, self-hosted) | Code blocks and pixel IDs only. Never for decorative labels |

Fluid scale (rem, `clamp()`), weights 400/500/600 only:

| Role | Size | Line height | Weight | Tracking |
| --- | --- | --- | --- | --- |
| Display | `clamp(2.75rem, 1rem + 6vw, 5rem)` | 1.04 | 600 | −0.035em |
| H1 | `clamp(2.25rem, 1rem + 4vw, 3.5rem)` | 1.08 | 600 | −0.03em |
| H2 | `clamp(1.75rem, 1rem + 2.5vw, 2.5rem)` | 1.15 | 600 | −0.02em |
| H3 | 1.375rem | 1.3 | 600 | −0.01em |
| Body (sans) | 1.0625rem | 1.6 | 400 | 0 |
| Body (serif) | 1.1875rem | 1.7 | 400 | 0 |
| Small | 0.875rem | 1.5 | 400 | 0 |
| Caption | 0.8125rem | 1.45 | 400 | 0 |

Rules: line length 62–68 characters (never above 75); sentence case everywhere; no ALL-CAPS labels; hero headline ≤ 18 characters per line; numerals tabular in tables (`font-variant-numeric: tabular-nums`); optical alignment, `text-wrap: balance` on headings and `pretty` on body; proper typographic quotes, en/em dashes only where grammatically correct, real minus sign (−) for negative numbers; `lang` attributes set.

## 5. Layout

- 4 px base unit. Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 160.
- Container max-width 1120 px; reading column 680 px; gutters 24 px (mobile) and 32 px.
- Vertical rhythm between landing sections: 160 px desktop, 96 px mobile. Docs: 64/48.
- Alignment: hero centered; every other section **left-aligned** with a generous measure; the map is centered in its viewport.
- Radii by hierarchy, not uniform: controls 10 px; panels 20 px; map cells 3 px (0 px at ≤ 12 px cell size); pills 999 px.
- Elevation: none by default. Hairlines separate. One shadow token only for popovers (`0 8px 30px rgb(0 0 0 / .12)` light; none, with a stronger line, in dark).
- Do not build identical card grids. Use whitespace, a single column, and typographic rhythm. Where a set of parallel items is real (the six modules), use a definition-style list with the module name as text.

### Wireframes

Home (desktop):

```
┌──────────────────────────────────────────────────────────────┐
│ Symnoesis                         Idea  Map  Portal  Index  ⌂│  nav, translucent, 56 px
│                                                              │
│            Measure the relationship,                         │  display, centered
│               not just the model.                            │
│    A specification for evaluating long-term human-AI use.    │  ink-2, 21 px
│            [ Explore the Map ]   Find your pixel             │  one filled button, one text link
│                                                              │
│         ┌───── Symnoesis Map (16×16, live) ─────┐            │  the memorable object
│         │                                        │           │
│         └────────────────────────────────────────┘           │
│          Synthetic demonstration data (E1). Not a real system│  evidence badge + caption
│                                                              │
│  [160 px]                                                    │
│  Benchmarks measure models.                                  │  display-sized statement, left
│  People live with them.                                      │
│  (one short paragraph, 680 px)                               │
│  …next idea, same pattern…                                   │
└──────────────────────────────────────────────────────────────┘
```

Portal result (desktop): left column (5/12) text summary and zone; right column (7/12) map with the user's modal pixel and probability halo; below, single-flip neighbors as a plain list. Mobile: summary first, map second at 8×8.

## 6. Components (build only these)

Nav (sticky, translucent with `backdrop-filter`, solid fallback); Button (filled accent; text link as secondary); Link; Segmented control (domain, frame, resolution); Frame scrubber (discrete, five stops, labeled); **Map** (SVG); Legend; Pixel popover; Neighbors panel; Evidence badge; Zone chip (code + name); Callout (one style); Table (responsive, sticky header); Code block (copy button); Disclosure (`<details>`); Figure with caption; Footnote and citation; Stepper (portal questionnaire; real sequence, so numbering is justified); Result summary; Footer.

No carousels, accordions-as-decoration, tabs-as-navigation, modals (except the pixel popover, non-modal), toasts, chat widgets, cookie banners (no cookies exist), or newsletter forms.

## 7. Motion

- Durations 160 / 240 / 400 ms. Easing `cubic-bezier(0.22, 1, 0.36, 1)`.
- **Exactly one orchestrated moment:** on first load of the home page, the hero map's cells resolve from the paper color to their values in a diagonal wave, ≤ 900 ms total, once. No loop.
- Everything else is a response to input: hover and focus states (color only), popover open, frame change (cells cross-fade 240 ms), resolution change.
- `prefers-reduced-motion: reduce` removes the wave and cross-fades (state changes are instant).
- No parallax, scroll-jacking, scroll-triggered reveals, auto-playing video, or auto-advancing scrubber. The "film" plays only on an explicit Play press.

## 8. Imagery, icons, brand

- **No photography, stock imagery, 3D renders, AI-generated images, gradients (except the data scale), glassmorphism (except nav), or illustrated people.**
- Diagrams are hand-authored SVG using tokens (build-time, no runtime diagram libraries).
- Icons: a custom set of at most 12, 1.5 px stroke, 24 px grid (GitHub, external, chevron, info, close, play, pause, download, copy, print, search, menu). No emoji anywhere.
- Wordmark: "Symnoesis" in Inter 600, tracking −0.02em. Mark: a 4 × 4 grid of squares with one accent square. Favicon: the mark. No other logo. "An initiative by HarVa Groups" in the footer as plain text unless official HarVa Groups brand assets are supplied.
- Open Graph images: one template, text-only, generated at build.

## 9. Accessibility inside design

- WCAG 2.2 AA minimum; aim for AAA contrast on body text.
- Focus ring: 2 px `--accent` plus 2 px paper offset, never removed; visible on every interactive element including map cells.
- Touch targets ≥ 44 px for buttons and controls. Map cells are smaller by nature, so the map MUST also offer arrow-key navigation, a full table alternative, and the neighbors list. At viewport width < 480 px default to the 8 × 8 resolution (cells ≥ 38 px).
- Respect `prefers-contrast: more` (thicker outlines, patterns on), `forced-colors`, `prefers-reduced-motion`, and text zoom to 200% without loss.
- Color is never the only signal.

## 10. CSS architecture

`@layer reset, tokens, base, layout, components, pages;` Hand-written CSS with custom properties and logical properties (`margin-inline`, `padding-block`). No utility frameworks, no CSS-in-JS, no component libraries. Selector specificity stays flat (single class selectors; no nested descendant chains). One stylesheet per component, imported by the component. Svelte components use scoped styles that only reference tokens. Verify after each page that padding and margin between sections are not overridden by competing selectors.

## 11. Print and PDF

Every page has a print stylesheet: single column, black on white, links expanded as footnotes for the spec and whitepaper, map rendered with patterns and sign glyphs (grayscale-safe). The Card PDF follows the same tokens.

## 12. Design acceptance checks

- Squint test: at 25% zoom, the map is the dominant object on the home page.
- Remove-one-accessory test recorded in the design plan.
- Lighthouse accessibility 100; axe zero violations; CVD simulations attached to the build log.
- A screenshot review at 360, 768, 1280, and 1920 px, light and dark, without layout breakage.
