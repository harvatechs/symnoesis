# Architectural & Philosophical Explanation

Detailed discussions on design choices and theoretical rationale.

---

## Why Dyadic Rather than Model-Centric?

Conventional AI benchmarks isolate the machine from context. But human cognition, emotional state, and task capabilities change dynamically in response to assistive tooling. Evaluating the model alone cannot measure:
1. Whether a student is genuinely learning concepts or outsourcing problem-solving entirely.
2. Whether an advice-seeking individual is maintaining healthy human support systems or withdrawing into synthetic companionship.

The dyad ($H \times M$) is the minimum irreducible system capable of expressing these phenomena.

---

## Why Gray Code Coordinate Mapping?

In standard binary counting, transitioning from $7$ (`0111`) to $8$ (`1000`) changes all 4 bits simultaneously, creating artificial visual discontinuities. 

By contrast, the **binary-reflected Gray code** guarantees that every adjacent column or row on the 16×16 grid differs by exactly **one bit** ($d_H = 1$). A human or machine that experiences a single-variable improvement or regression moves smoothly to an adjacent cell, preserving local topology.

---

## The Rationale for the Non-Compensation Rule

In standard utilitarian utility models, high provider gains (e.g., increased engagement, subscription retention, computational throughput) can mathematically cancel out small human harms.

Symnoesis rejects this tradeoff. Human wellbeing is a non-negotiable floor: if human net effect is negative ($HNE < 0$), machine/provider benefit is mathematically clamped ($SNE' = \min(SNE, 0)$). Harm can never be purchased with system utility.
