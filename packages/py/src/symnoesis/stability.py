"""Stability factor calculation and perturbation resilience.

Normative implementation of SPEC §6:
  σ_C = SD of C across session-blocks
  S = 0.5 + 0.5 * (1 - min(1, σ_C / σ_max))   where S ∈ [0.5, 1.0]
  S_eff = S if C >= 0 else 1.0                (instability never softens harm)
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from symnoesis.config import SymnoesisConfig


def compute_sample_std(values: Sequence[float]) -> float:
    """Computes sample standard deviation. Returns 0.0 if fewer than 2 values."""
    n = len(values)
    if n < 2:
        return 0.0
    mean_val = sum(values) / n
    variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
    return math.sqrt(variance)


def compute_stability_factor(sigma_c: float, config: SymnoesisConfig) -> float:
    """Computes stability factor S ∈ [0.5, 1.0]."""
    sigma_max = config.sq.stability.sigma_max
    ratio = min(1.0, max(0.0, sigma_c / sigma_max))
    return 0.5 + 0.5 * (1.0 - ratio)


def compute_effective_stability(c: float, s: float) -> float:
    """Applies harm override: S_eff = S if C >= 0 else 1.0."""
    return s if c >= 0.0 else 1.0
