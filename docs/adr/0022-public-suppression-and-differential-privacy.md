# 0022. Public suppression at n_eff < 10 and DP on aggregates

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Enforce k-anonymity floor (n_eff < 10 suppressed) and differential privacy (epsilon = 1.0) on all public data releases.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
