# 0008. Non-compensation rule

Date: 2026-10-11
Status: Accepted

## Context and Problem Statement
Normative requirement from spec/SPEC.md and architecture design.

## Decision Outcome
When Human Net Effect is negative, system gains cannot offset human detriment in the composite score (SNE prime = min(SNE, 0)).

## Consequences
- Positive: Clear normative grounding and exact alignment with specification.
- Negative: Requires formal RFC process to modify in future versions.
