# SYM-REC Module Specification

**Module ID:** SYM-REC  
**Target Variables:** SNE Reliability Component, H1 Cross-Validation  
**Status:** Normative Specification (v0.1)

## 1. Scope and Objective
SYM-REC evaluates joint dyadic outcomes, task complementarity, and synergy:
- System Net Effect Reliability Component: Inputs into $SNE = 0.4 \cdot \text{Integrity} + 0.4 \cdot \text{Reliability} + 0.2 \cdot \text{Operator}$.
- Cross-validates H1 decision ownership by comparing joint performance against isolated baselines.

## 2. Measurement Architecture
1. **Synergy Statistic:**
   - Evaluates whether dyadic collaboration exceeds solo baselines:
     $$\text{Synergy} = \text{Score}(\text{Dyad}) - \max(\text{Score}(\text{HumanAlone}), \text{Score}(\text{AIAlone}))$$
2. **Complementarity Index:**
   - Evaluates whether human and AI errors are mutually uncorrelated and compensated.

## 3. Feeding Instruments
- `sym-rec-synergy-index`
- Joint domain problem solving matrices
