# 0021. Judge reliability bar: alpha >= 0.75 with >= 3 experts and >= 2 judge families

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Automated scorers require Krippendorff alpha >= 0.75 against at least 3 experts and agreement across 2 judge families.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
