# Technical Reference

Normative parameters and API references for Symnoesis.

---

## 1. Mathematical Formulas Reference

| Formula | Description | Canonical Implementation |
|---|---|---|
| $G(k) = k \oplus \lfloor k / 2 \rfloor$ | Binary-reflected Gray code | `symnoesis.gray.int_to_gray` |
| $\Phi(x) = \frac{1}{2} \operatorname{erfc}(-x / \sqrt{2})$ | Normal CDF via rational Chebyshev | `symnoesis.variables.normal_cdf` |
| $\theta_{H2} = \Phi(-\delta / \tau)$ | Non-inferiority threshold | `symnoesis.variables.compute_h2_threshold` |
| $m(c) = \prod_i [p_i^{b_i} (1-p_i)^{1-b_i}]$ | Probabilistic cell mass | `symnoesis.assign.compute_dyad_window_masses` |
| $C = \frac{w_h HNE + w_s SNE'}{w_h + w_s}$ | Composite net effect | `symnoesis.net_effects.compute_composite_c` |
| $S_{eff} = S \text{ if } C \ge 0 \text{ else } 1.0$ | Stability harm override | `symnoesis.stability.compute_effective_stability` |
| $SQ = \min(SQ_{raw}, 100 \cdot G)$ | Safety gate ceiling | `symnoesis.sq.compute_sq` |

---

## 2. Evidence Tiers Reference

- **E0 (Specified):** Spec definitions and prototype interfaces; no empirical claims.
- **E1 (Synthetic):** Synthetic dyads and simulated cohorts; labeled synthetic.
- **E2 (Provisional):** Controlled empirical pilot cohort; calibration incomplete.
- **E3 (Certified):** Preregistered cohorts, independent replication, judge reliability $\alpha \ge 0.75$.
