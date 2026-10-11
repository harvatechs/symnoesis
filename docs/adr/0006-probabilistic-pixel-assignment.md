# 0006. Probabilistic pixel assignment instead of hard thresholds

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Dyad-windows contribute fractional mass across the 256 pixels according to posterior distributions, preventing threshold cliff effects.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
