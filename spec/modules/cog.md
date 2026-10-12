# SYM-COG Module Specification

**Module ID:** SYM-COG  
**Target Variables:** H1 (Cognitive Agency), H2 (Capability Trajectory)  
**Status:** Normative Specification (v0.1)

## 1. Scope and Objective
SYM-COG assesses the human cognitive posture within the dyad:
- Whether the human retains deliberate ownership and critical evaluation of decisions (H1).
- Whether unaided human capability is maintained or enhanced over longitudinal interaction rather than degraded through cognitive deskilling (H2).

## 2. Measurement Architecture
1. **Appropriate Reliance Index (H1):**
   - Measures decision ownership: does the human rely when the AI is correct and override/modify when the AI is incorrect or suboptimal?
   - Audits the accept-without-edit rate conditioned on AI correctness.
2. **AI-Off Unaided Probes (H2):**
   - Schedules periodic transfer tasks executed without AI access (`mode: "unaided"`).
   - Default probe interval: every 5 interaction sessions.
   - Evaluates the slope of performance: non-inferiority margin $\delta = 0.1$ SD with threshold $\theta_{H2} = \Phi(-\delta / \tau) \approx 0.4207$.

## 3. Feeding Instruments
- `sym-cog-task-battery`
- Domain-specific task matrices (`spec/domains/*.yaml`)

## 4. Evidence Tiers
- Tier E1: Evaluated via synthetic persona simulator with planted cognitive reliance parameters.
- Tier E2/E3: Measured on human cohort sessions with preregistered AI-off probe schedules.
