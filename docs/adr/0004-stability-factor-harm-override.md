# 0004. Stability factor never softens negative scores

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Instability factor S applies only when C >= 0; when C < 0, S_eff = 1 so high variance never shrinks harm toward zero.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
