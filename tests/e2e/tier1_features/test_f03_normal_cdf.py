"""Tier 1 Feature Tests: F03 Normal CDF Parity (SPEC §3).

Verifies Cody erfc calculation, standard points, symmetry, and H2 threshold derivation.
"""

from __future__ import annotations

from typing import Any

import pytest
from scipy.special import ndtr  # type: ignore[import-untyped]
from tests.e2e.oracle import normal_cdf_oracle

try:
    import symnoesis.variables as py_vars
except ImportError:
    py_vars = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_03_01_standard_normal_zero_center() -> None:
    """TC1.03.01: Phi(0.0) == 0.5 exactly."""
    assert normal_cdf_oracle(0.0) == 0.5
    if py_vars is not None:
        assert py_vars.normal_cdf(0.0) == 0.5


@pytest.mark.tier1
def test_tc1_03_02_standard_deviation_points() -> None:
    """TC1.03.02: Matches scipy.special.ndtr within 1e-9 at +/- 1, 2, 3 SD."""
    for z in (-3.0, -2.0, -1.0, 1.0, 2.0, 3.0):
        val = normal_cdf_oracle(z)
        ref = float(ndtr(z))
        assert abs(val - ref) < 1e-9
        if py_vars is not None:
            assert abs(py_vars.normal_cdf(z) - ref) < 1e-9


@pytest.mark.tier1
def test_tc1_03_03_monotonicity_across_grid() -> None:
    """TC1.03.03: Monotonicity holds strictly: z1 < z2 implies Phi(z1) < Phi(z2)."""
    grid = [-4.0 + 0.2 * i for i in range(41)]
    for i in range(len(grid) - 1):
        assert normal_cdf_oracle(grid[i]) < normal_cdf_oracle(grid[i + 1])
        if py_vars is not None:
            assert py_vars.normal_cdf(grid[i]) < py_vars.normal_cdf(grid[i + 1])


@pytest.mark.tier1
def test_tc1_03_04_symmetry_invariant() -> None:
    """TC1.03.04: Phi(z) + Phi(-z) == 1.0 across test domain within 1e-12."""
    for z in (0.1, 0.5, 1.25, 2.15, 3.75):
        s = normal_cdf_oracle(z) + normal_cdf_oracle(-z)
        assert abs(s - 1.0) < 1e-12
        if py_vars is not None:
            s_py = py_vars.normal_cdf(z) + py_vars.normal_cdf(-z)
            assert abs(s_py - 1.0) < 1e-12


@pytest.mark.tier1
def test_tc1_03_05_non_inferiority_h2_threshold(symn_config: Any) -> None:
    """TC1.03.05: H2 threshold Phi(-0.1 / 0.5) = Phi(-0.2) approx 0.42074029."""
    delta = 0.1
    tau = 0.5
    theta_h2 = normal_cdf_oracle(-delta / tau)
    assert abs(theta_h2 - 0.420740290560897) < 1e-9
    if py_vars is not None and symn_config is not None:
        assert abs(py_vars.compute_h2_threshold(symn_config) - 0.420740290560897) < 1e-9
