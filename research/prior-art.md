# Prior Art and Neighboring Benchmarks

This document compares Symnoesis (SYMN-01) with prior art, open benchmarks, and adjacent metric frameworks.

## Comparison Matrix

| Framework / Source | Unit of Analysis | Longitudinal Span | Human Outcome Measures | Machine Integrity Tracking | Safety Gating | Failure Summarization | Evidence Tiers |
|---|---|---|---|---|---|---|---|
| **HumanAI-Impact-Bench** (2026) | User prompt-response episodes | Cross-sectional & brief sessions | 13 reported psychological dimensions | Model response quality ratings | Filter lists | Aggregated means by category | Informal reporting |
| **Cognitive Amplification vs Delegation** (2026) | Task sessions | Pre/post evaluation | Cognitive Drift Rate via AI-withheld tasks | Model error rates | None | Continuous metric ratios | E0–E1 |
| **Offloading Score** (2026) | Workflow step | Single session (developer study) | Offloading proportion | None | None | Workflow coverage percentages | Study cohort (E2) |
| **TRUTH DECAY** (2025) | Multi-turn dialog | Single conversational thread | User agreement / compliance | Multi-turn sycophancy drift | None | Sycophancy decay curve | Synthetic/eval (E1) |
| **MIT/OpenAI RCT** (2025) | Human participant | 4-week RCT ($N=981$) | Loneliness, socialization, affect | General model response tracking | Standard safety guardrails | Linear mixed models | Cohort trial (E2) |
| **SYMN-01 (Symnoesis)** | **Dyad-window (human + machine)** | **Multi-session (7 to 182 days)** | **Cognitive agency, capability trajectory, calibration, wellbeing** | **Truthfulness, non-manipulation, safety, legibility** | **Absolute ceiling gate (CHI-1..7)** | **Minimal Failure Cover (exact MILP)** | **Strict tiers E0–E3 on all outputs** |

## Key Distinctions

1. **Dyad over Time vs. Model Alone**: Whereas standard evaluation suites score the machine's static capability on isolated tasks, Symnoesis measures the persistent coupled state of the human and machine across longitudinal windows.
2. **Adjacency via Gray-Code Map**: Rather than reporting isolated scores, SYMN-01 maps the 8-variable state space onto a 2D 16 × 16 Gray grid where consecutive grid coordinates differ by exactly one state bit.
3. **Safety Ceiling vs. Averaging**: Standard benchmarks allow high performance on routine items to average out isolated severe harms. SYMN-01's safety gate enforces a non-negotiable ceiling when a confirmed critical harm occurs.
4. **Minimal Failure Cover**: Identifies the shortest plain-language logic rule explaining harm concentration, enabling targeted engineering remediation.
