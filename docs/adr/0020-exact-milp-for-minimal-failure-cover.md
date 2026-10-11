# 0020. Cover solved exactly by MILP; strict mode cross-checked with sympy

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
Solve Minimal Failure Cover via exact MILP over 6561 subcubes using scipy.optimize.milp, with strict mode validated against sympy SOPform.

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
