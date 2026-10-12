# Design Plan: Symnoesis Web & Portal (v0.1.0)

## 1. Tokens
- **Base Colors:**
  - Light mode: `--paper`: `#FFFFFF`, `--surface`: `#F5F6F7`, `--line`: `#E3E5E8`, `--ink`: `#16181B`, `--ink-2`: `#3C4047`, `--ink-3`: `#6B7078`, `--accent`: `#2B4EDB`.
  - Dark mode: `--paper`: `#0E0F11`, `--surface`: `#17181B`, `--line`: `#2A2C31`, `--ink`: `#F2F3F5`, `--ink-2`: `#C5C8CE`, `--ink-3`: `#9298A2`, `--accent`: `#8EA2FF`.
- **Diverging SQ Scale (OKLab):**
  - Negative to Positive (−100 to +100): `#9E3410`, `#C85A33`, `#E48D6C`, `#F0C2AE`, `#E8E9EB`, `#B3D8CE`, `#6DB5A2`, `#2E8F78`, `#006B52`.
  - Contrast rule: text >= 4.5:1; UI >= 3:1; non-hue indicators (glyphs, labels, patterns) accompany all color states.
- **Type Roles:**
  - Sans: `-apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif` (UI, navigation, headings, data displays).
  - Serif: `"Source Serif 4", Georgia, serif` (long-form prose, whitepaper, philosophy).
  - Monospace: `ui-monospace, "JetBrains Mono", Menlo, Consolas, monospace` (pixel IDs, math codes, CLI commands).
- **Spacing & Radii:**
  - 8-point baseline rhythm. Radii: 4px for small tags/cells, 6px for cards/panels, 0px for hair-rules.
- **Motion:**
  - Responsive only to explicit user interaction. Zero decorative scroll animations or fade-in chains. `prefers-reduced-motion` honored everywhere.

## 2. Layout Concepts & Wireframes

### Primary Navigation (Header)
```
[Symnoesis SYMN-01]       [Idea]  [Map]  [Portal]  [Index]  [Research]  [About]   [GitHub]
--------------------------------------------------------------------------------------
```

### Home Page (`/`)
- Concept: "Orient, then reveal. One idea per viewport, leading directly to the 256-state map."
```
+------------------------------------------------------------------------------------+
| Display: Measure the relationship, not just the model.                             |
| Sub: SYMN-01 is an open specification for evaluating long-term human-AI interaction.|
| [Explore the Map]   [Find your pixel]                                              |
|                                                                                    |
| [ Hero Map: 16x16 Gray Grid with State Inspector & Evidence Tier Badge ]           |
| Caption: Synthetic demonstration data (E1). Not a measurement of any real system. |
+------------------------------------------------------------------------------------+
| Section 1: The unit is the pair (dyadic state over time).                          |
| Section 2: One step changes one thing (Gray code adjacency).                       |
| Section 3: A critical failure cannot be averaged away (non-compensatory gate).     |
| Section 4: Evidence honesty (E0 to E3 tiers).                                      |
+------------------------------------------------------------------------------------+
```

### Map Explorer (`/map`)
- Concept: "A precision scientific instrument. Clean controls on top, map and inspector side-by-side, full keyboard and screen-reader parity, table toggle."
```
+------------------------------------------------------------------------------------+
| Controls: [Domain: Learning v] [Frame: Day 1 . W1 . W4 . W12 . W26] [Res: 16x16 v] |
|           [Overlay: Failure Cover [x]  Gates [x] ]  [View as table Toggle]         |
+------------------------------------------+-----------------------------------------+
| [ 16x16 Interactive Gray Grid          ] | [ State Inspector (Pinned/Hovered)    ] |
| - Cell color: OKLab SQ diverging         | - Pixel ID: h1011-m0110                 |
| - Zone patterns: Z1-Z7                   | - Coordinates: Col 11, Row 6            |
| - Roving tabindex, arrow-key navigation  | - Human variables (H1-H4)               |
| - Non-modal inspection                   | - Machine variables (M1-M4)             |
|                                          | - SQ: 28.7 [14.2, 41.9] (E1)            |
|                                          | - 8 Single-Flip Neighbors (4 grid / 4)  |
|                                          | - Dominant Failure & Gate Status        |
+------------------------------------------+-----------------------------------------+
```

### Interactive Portal (`/portal`)
- Concept: "4-step privacy-preserving self-assessment running purely in-browser, yielding descriptive, conditional non-diagnostic findings."
```
+------------------------------------------------------------------------------------+
| Step Indicator: Step 2 of 4 (Agency)                                               |
| Banner: Uncalibrated prototype (E0). Weights come from expert judgment.            |
| Questions (5-point scales + 'Prefer not to say')                                   |
| [Back]                                                                      [Next] |
| Privacy Note: Answers stay in your browser. Nothing is sent or stored.             |
+------------------------------------------------------------------------------------+
```

### Method / Spec (`/method`)
- Concept: "Authoritative academic specification with formulas, definitions, and worked examples."

### Index (`/index`)
- Concept: "Edition 0 methodology preview with honest statistical tiering and fictional fixture systems."

### Research & Governance (`/research`, `/governance`, `/about`)
- Concept: "Spacious, peer-reviewed typographic paper layout with verified citations and organizational transparency."

## 3. Principles
1. **Subtract:** No generic marketing badges, no hype cards, no decorative hero gradients.
2. **Honesty:** Every number carries an evidence tier badge (E0, E1, E2, E3).
3. **Privacy by Construction:** Zero third-party scripts, zero analytics, zero cookies.

## 4. Critique & Self-Review
- *Critique:* Did we use generic rounded SaaS cards or terracotta accents?
  *Correction:* No. We use flat quiet panels (`--surface`), standard 1px lines (`--line`), and clean typography.
- *Critique:* Does anything flash or move automatically?
  *Correction:* No autoplaying animations; all transitions are user-initiated and respect reduced-motion.
- *Removal before ship:* Removed decorative icons inside section headers to keep typography pure and quiet.
