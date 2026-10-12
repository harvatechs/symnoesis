"""Variable scaling and probability calculation for Symnoesis.

Normative implementation of SPEC §2.3 and §3:
  s = Φ(d / τ)
  p_i = P(s_i ≥ θ_i) = Φ((μ_i - θ_i) / σ_i)
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from symnoesis.config import SymnoesisConfig


def normal_cdf(x: float) -> float:
    """Computes standard normal cumulative distribution function Φ(x) = 0.5 * erfc(-x / sqrt(2))."""
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def effect_to_score(d: float, config: SymnoesisConfig) -> float:
    """Maps standardized effect d to score s in [0, 1] using s = Φ(d / τ)."""
    tau = config.variables.effect_scale
    return normal_cdf(d / tau)


def compute_h2_threshold(config: SymnoesisConfig) -> float:
    """Computes θ_H2 = Φ(-δ / τ) where δ is non-inferiority margin and τ is effect scale."""
    delta = config.variables.noninferiority_margin_h2
    tau = config.variables.effect_scale
    return normal_cdf(-delta / tau)


def compute_marginal_probability(
    mu: float,
    sigma: float,
    var_id: str,
    config: SymnoesisConfig,
) -> float:
    """Computes p_i = P(s_i ≥ θ_i) = Φ((μ_i - θ_i) / σ_i) enforcing sigma_floor."""
    sigma_floor = config.variables.sigma_floor
    eff_sigma = max(sigma, sigma_floor)

    theta = config.variables.thresholds[var_id]
    z = (mu - theta) / eff_sigma
    return normal_cdf(z)


def compute_all_marginal_probabilities(
    posteriors: Mapping[str, tuple[float, float]],
    config: SymnoesisConfig,
) -> dict[str, float]:
    """Computes marginal probability p_i for each of the 8 variables given posteriors."""
    probs: dict[str, float] = {}
    for var_id in ("H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"):
        if var_id not in posteriors:
            raise ValueError(f"Missing posterior distribution for variable {var_id}")
        mu, sigma = posteriors[var_id]
        probs[var_id] = compute_marginal_probability(mu, sigma, var_id, config)
    return probs
