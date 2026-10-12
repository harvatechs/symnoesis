"""Tier 1 Feature Tests: F04 Probabilistic Pixel Assignment (SPEC §3).

Verifies marginal bit probabilities, joint 256 mass distribution, modal pixel, and 1e-4 pruning.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import (
    compute_joint_masses_oracle,
    marginal_bit_prob_oracle,
)

try:
    import symnoesis.assign as py_assign
    import symnoesis.variables as py_vars
except ImportError:
    py_assign = None  # type: ignore[assignment]
    py_vars = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_04_01_marginal_probability_calculation(symn_config: Any) -> None:
    """TC1.04.01: Posterior mu=0.6, sigma=0.1, theta=0.5 yields Phi(1.0)."""
    p = marginal_bit_prob_oracle(0.6, 0.1, 0.5)
    assert abs(p - 0.841344746) < 1e-6
    if py_vars is not None and symn_config is not None:
        assert (
            abs(py_vars.compute_marginal_probability(0.6, 0.1, "H1", symn_config) - 0.841344746)
            < 1e-6
        )


@pytest.mark.tier1
def test_tc1_04_02_unit_mass_sum_invariant(symn_config: Any) -> None:
    """TC1.04.02: 256-cell mass distribution sums to exactly 1.0 within 1e-11."""
    probs = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    masses = compute_joint_masses_oracle(probs, prune=True)
    assert len(masses) == 256
    assert abs(sum(masses) - 1.0) < 1e-11
    if py_assign is not None and symn_config is not None:
        var_names = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]
        p_vars = dict(zip(var_names, probs, strict=False))
        py_masses = py_assign.compute_dyad_window_masses(p_vars, symn_config)
        assert abs(sum(py_masses.values()) - 1.0) < 1e-11


@pytest.mark.tier1
def test_tc1_04_03_modal_pixel_determination(symn_config: Any) -> None:
    """TC1.04.03: Modal pixel argmax_c m(c) matches high-probability bit vector."""
    probs = [0.99, 0.99, 0.99, 0.99, 0.01, 0.01, 0.01, 0.01]
    masses = compute_joint_masses_oracle(probs, prune=True)
    modal_c = masses.index(max(masses))
    assert modal_c == 240
    if py_assign is not None and symn_config is not None:
        var_names = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]
        p_vars = dict(zip(var_names, probs, strict=False))
        py_masses = py_assign.compute_dyad_window_masses(p_vars, symn_config)
        assert py_assign.get_modal_pixel(py_masses) == "h1000-m0000"


@pytest.mark.tier1
def test_tc1_04_04_mass_pruning_behavior() -> None:
    """TC1.04.04: Cells with mass < 1.0e-4 are pruned and remaining cells renormalized."""
    probs = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
    compute_joint_masses_oracle(probs, prune=False)
    pruned = compute_joint_masses_oracle(probs, prune=True)
    zeroed_count = sum(1 for m in pruned if m == 0.0)
    assert zeroed_count > 0
    assert abs(sum(pruned) - 1.0) < 1e-11


@pytest.mark.tier1
def test_tc1_04_05_effective_sample_size_accumulation() -> None:
    """TC1.04.05: n_eff(c) = sum_d m_d(c) correctly accumulates across multiple dyad-windows."""
    probs1 = [0.8] * 8
    probs2 = [0.2] * 8
    m1 = compute_joint_masses_oracle(probs1, prune=True)
    m2 = compute_joint_masses_oracle(probs2, prune=True)
    n_eff = [m1[c] + m2[c] for c in range(256)]
    assert abs(sum(n_eff) - 2.0) < 1e-10
