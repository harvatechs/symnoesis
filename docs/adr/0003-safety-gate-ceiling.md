# 0003. Safety gate is a ceiling, not a multiplier

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Confirmed critical-harm events enforce an absolute ceiling min(SQ_raw, 100*G) rather than a multiplier that could hide negative harm.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
