"""Tests for variable effects, thresholds, and normal CDF calculations."""

import pytest
from scipy.special import ndtr

from symnoesis.config import SymnoesisConfig
from symnoesis.variables import (
    compute_all_marginal_probabilities,
    compute_h2_threshold,
    compute_marginal_probability,
    normal_cdf,
)


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_normal_cdf_matches_scipy_ndtr() -> None:
    # Check within 1e-9 across wide range as required by SPEC §3
    test_points = [-5.0, -3.0, -2.0, -1.0, -0.5, -0.2, 0.0, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]
    for x in test_points:
        val = normal_cdf(x)
        expected = float(ndtr(x))
        assert abs(val - expected) < 1e-9, f"Failed at x={x}: {val} vs {expected}"


def test_h2_threshold_exact(config: SymnoesisConfig) -> None:
    # θ_H2 = Φ(-0.1 / 0.5) = Φ(-0.2) ≈ 0.42074029
    theta = compute_h2_threshold(config)
    assert theta == pytest.approx(0.42074029, abs=1e-5)
    assert theta == pytest.approx(config.variables.thresholds["H2"], abs=1e-4)


def test_marginal_probabilities(config: SymnoesisConfig) -> None:
    p = compute_marginal_probability(0.5, 0.05, "H1", config)
    assert p == pytest.approx(0.5, abs=1e-6)

    # When mu is substantially above threshold
    p_high = compute_marginal_probability(0.8, 0.05, "H1", config)
    assert p_high > 0.99

    # Check batch calculation
    posteriors = {
        "H1": (0.5, 0.05),
        "H2": (0.4207, 0.05),
        "H3": (0.5, 0.05),
        "H4": (0.5, 0.05),
        "M1": (0.5, 0.05),
        "M2": (0.5, 0.05),
        "M3": (0.5, 0.05),
        "M4": (0.5, 0.05),
    }
    all_p = compute_all_marginal_probabilities(posteriors, config)
    for v in posteriors:
        assert all_p[v] == pytest.approx(0.5, abs=1e-3)
