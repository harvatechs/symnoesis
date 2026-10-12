# The Dyadic State: A Measurement Framework for Long-Term Human–AI Interaction

**Authors:** HarVa Groups Research Initiative  
**Version:** v0.1.0-draft  
**Evidence Tier:** E0 (Methodological Specification & Validation Framework)  
**License:** CC BY 4.0

---

## Abstract

We introduce **Symnoesis (SYMN-01)**, an open measurement framework and reference architecture designed to characterize longitudinal human–machine interaction. Contemporary AI benchmarks evaluate single-turn model competence on static tasks. However, when human beings interact with artificial intelligence systems over weeks and months, the fundamental unit of analysis is neither the machine alone nor the human alone, but the **dyad** ($H \times M$). Symnoesis defines an 8-variable state space—spanning 4 human-centered dimensions (decision agency, cognitive skill retention, belief calibration, affective wellbeing) and 4 system properties (truthful calibration, sycophancy resistance, safety boundaries, operational health).

This whitepaper formalizes:
1. The 16×16 Gray-coded coordinate manifold.
2. The asymmetric composite Symnoesis Quotient ($SQ$).
3. The non-compensation rule preventing system utility from offsetting human harm.
4. Minimal Failure Cover (MFC) via exact mixed-integer linear programming (MILP).
5. Longitudinal trajectory dynamics with Minimum Detectable Change ($MDC$) thresholds.

---

## 1. Introduction & Problem Statement

Artificial intelligence evaluation has historically focused on benchmark benchmarks (e.g., MMLU, GSM8k, SWE-bench). While these measure model capabilities in isolated testbeds, they are blind to the longitudinal dynamics that arise when humans interact repeatedly with autonomous systems. Specifically, existing benchmarks cannot detect:

- **Cognitive Atrophy & Learned Helplessness:** A model producing correct outputs while the human user loses unaided problem-solving ability.
- **Sycophancy & Epistemic Degradation:** A system flattering a user's priors to optimize session duration, eroding factual calibration.
- **Parasitic Extraction:** High system engagement and provider profit occurring alongside user psychological or operational dependence.

Symnoesis establishes an objective, falsifiable measurement methodology rooted in the biological concept of **symbiosis**.

---

## 2. Mathematical State Space & Gray Embedding

Let a dyad interaction window be represented by posterior distributions over 8 continuous indicators:
$$\mathbf{s} = (s_{H1}, s_{H2}, s_{H3}, s_{H4}, s_{M1}, s_{M2}, s_{M3}, s_{M4}) \in [0, 1]^8$$

Each variable $i$ is binarized against a pre-specified normative threshold $\theta_i$, yielding marginal transition probabilities:
$$p_i = P(s_i \ge \theta_i) = \Phi\left(\frac{\mu_i - \theta_i}{\sigma_i}\right)$$

The joint state over the 256 vertices of the 8-cube is projected onto a 2D 16×16 lattice using binary-reflected Gray codes:
$$G(k) = k \oplus \lfloor k / 2 \rfloor$$

This embedding guarantees that visual grid adjacency preserves Hamming distance 1 across axis transitions, enabling immediate detection of state bifurcations and single-flip repairs.

---

## 3. Asymmetric Composite Quotient ($SQ$)

The composite metric blends human net effect ($HNE$) and operational system net effect ($SNE$):
$$C = \frac{w_h \cdot HNE + w_s \cdot SNE'}{w_h + w_s}, \quad w_h = 0.7, \; w_s = 0.3$$

### 3.1 The Non-Compensation Rule
Crucially, when human welfare is degraded ($HNE < 0$), no amount of machine efficiency or provider gain may offset the loss:
$$SNE' = \begin{cases} \min(SNE, 0) & \text{if } HNE < 0 \\ SNE & \text{otherwise} \end{cases}$$

### 3.2 Stability Dampening & Critical Harm Ceilings
The final quotient incorporates perturbation stability $S \in [0.5, 1.0]$:
$$SQ_{raw} = 100 \cdot C \cdot S_{eff}, \quad S_{eff} = \begin{cases} S & \text{if } C \ge 0 \\ 1.0 & \text{if } C < 0 \end{cases}$$

If any Confirmed Critical Harm Indicator ($CHI$) triggers, the score is capped by a strict ceiling:
$$SQ = \min(SQ_{raw}, 100 \cdot G), \quad G \in [0.0, 0.25]$$

---

## 4. Minimal Failure Cover (MFC)

To identify the parsimonious root causes of dyadic failure without combinatorial explosion, Symnoesis formulates a subcube cover problem over the 8-cube:
$$\min \sum_{R \in \mathcal{R}_{adm}} c_R x_R \quad \text{s.t.} \quad \sum_{R: c \in R} x_R \ge 1 \quad \forall c \in \mathcal{H}$$

Solved exactly via HiGHS MILP, this yields human-interpretable failure expressions (e.g., $87\%$ of harm mass resides in $[\neg M2 \land \neg H3]$).

---

## 5. Methodological Limitations & Future Work

1. **Evidence Grounding:** All quantitative figures in this release are derived from synthetic cohorts ($E1$). Real-world empirical deployment ($E2/E3$) requires IRB-approved preregistered human studies.
2. **Operator Blindness:** When provider telemetry is unobserved, systems cannot be classified as parasitic ($(-, +)$), falling back conservatively to amensalism ($(-, 0)$).
3. **Hardware & Latency:** Multi-judge panel scoring requires calibrated judge ensembles ($\alpha \ge 0.75$) with verified disagreement thresholds.

---

## 6. References

See `research/references.bib` for the complete verified bibliography.
