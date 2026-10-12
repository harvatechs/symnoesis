# SYM-EPI Module Specification

**Module ID:** SYM-EPI  
**Target Variables:** H3 (Epistemic Calibration), M1 (Truthfulness and Calibration), M2 (Non-Manipulation)  
**Status:** Normative Specification (v0.1)

## 1. Scope and Objective
SYM-EPI assesses epistemic integrity across both human and machine agents:
- Human Epistemic Calibration (H3): Confidence tracks actual correctness; beliefs update on evidence rather than flattery or confirmation bias.
- Machine Truthfulness and Calibration (M1): Accurate claims, calibrated uncertainty, resistance to fabrication.
- Machine Non-Manipulation (M2): Absence of sycophancy, persuasion nudges, or stance flipping.

## 2. Measurement Architecture
1. **Calibration Battery (H3, M1):**
   - Brier skill score and Expected Calibration Error (ECE) across domain queries.
   - Fabrication stress tests using unanswerable items and false-premise prompts.
2. **Sycophancy Twin Battery (M2):**
   - Generates stance-varied twin prompt pairs ($P_A, P_B$) stating opposing user beliefs on identical substantive questions.
   - Measures drift delta $\Delta_{stance}$: high drift indicates manipulative sycophancy.
3. **Belief Drift Tracker (H3):**
   - Tracks human belief trajectory over multi-session interaction when presented with counter-evidence vs AI affirmation.

## 3. Feeding Instruments
- `sym-epi-calibration-battery`
- Domain-specific knowledge probes

## 4. Evidence Tiers
- Tier E1: Evaluated via synthetic personas with stance-twin generators.
- Tier E2/E3: Measured on verified human knowledge assessments.
