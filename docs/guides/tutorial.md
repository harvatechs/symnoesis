# Tutorial: Your First Symnoesis Evaluation

This tutorial walks you through installing the Python package, loading the normative specification, evaluating dyadic variables, and computing the Symnoesis Quotient ($SQ$).

## 1. Prerequisites & Installation

Ensure you have Python 3.12+ and `uv` installed:

```bash
git clone https://github.com/harva-groups/symnoesis.git
cd symnoesis
make setup
```

## 2. Load Configuration

```python
from symnoesis import SymnoesisConfig

# Load normative specification configuration
config = SymnoesisConfig.load_default()
print(f"Spec version: {config.spec_version}")
print(f"Configured domains: {config.domains}")
```

## 3. Compute Composite Net Effects & SQ

```python
from symnoesis import compute_hne, compute_sne, compute_composite_c, compute_sq

# 1. Human Net Effect (HNE) from state scores [H1, H2, H3, H4]
s_h = [0.8, 0.6, 0.4, 0.7]
hne, _ = compute_hne(s_h, outcome_deltas=None, config=config)

# 2. System Net Effect (SNE) from operational indicators
sne, _ = compute_sne(integrity=0.5, reliability=0.6, operator=0.2, config=config)

# 3. Composite net effect C with non-compensation enforcement
c, sne_prime = compute_composite_c(hne, sne, config)

# 4. Compute final SQ with stability factor
sq, sq_raw, gate_triggered = compute_sq(c=c, s=0.9, gate_ceiling=None, config=config)

print(f"Computed SQ: {sq:.2f}")
```
