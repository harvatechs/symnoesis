"""Tier 1 Feature Tests: F06 Stability & Harm Asymmetry (SPEC §6, ADR-0004).

Verifies stability factor S calculation, boundary dampening, and the harm asymmetry rule (S_eff).
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import effective_stability_oracle, stability_s_oracle

try:
    import symnoesis.stability as py_stab
except ImportError:
    py_stab = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_06_01_zero_instability_nominal(symn_config: Any) -> None:
    """TC1.06.01: For sigma_C = 0.0, stability S == 1.0."""
    s = stability_s_oracle(0.0)
    assert s == 1.0
    if py_stab is not None and symn_config is not None:
        assert py_stab.compute_stability_factor(0.0, symn_config) == 1.0


@pytest.mark.tier1
def test_tc1_06_02_partial_instability_scaling(symn_config: Any) -> None:
    """TC1.06.02: For sigma_C = 0.1, sigma_max = 0.5, S = 0.5 + 0.5*(1 - 0.2) = 0.90."""
    s = stability_s_oracle(0.1, sigma_max=0.5)
    assert abs(s - 0.90) < 1e-12
    if py_stab is not None and symn_config is not None:
        assert abs(py_stab.compute_stability_factor(0.1, symn_config) - 0.90) < 1e-12


@pytest.mark.tier1
def test_tc1_06_03_maximum_instability_floor(symn_config: Any) -> None:
    """TC1.06.03: For sigma_C >= sigma_max, S reaches lower floor of 0.50."""
    s = stability_s_oracle(0.5, sigma_max=0.5)
    assert s == 0.5
    s_extreme = stability_s_oracle(1.2, sigma_max=0.5)
    assert s_extreme == 0.5
    if py_stab is not None and symn_config is not None:
        assert py_stab.compute_stability_factor(0.5, symn_config) == 0.5
        assert py_stab.compute_stability_factor(1.2, symn_config) == 0.5


@pytest.mark.tier1
def test_tc1_06_04_harm_asymmetry_invariant() -> None:
    """TC1.06.04: For C < 0, S_eff = 1.0 unconditionally (harm never softened)."""
    s_eff = effective_stability_oracle(c=-0.28, s=0.50)
    assert s_eff == 1.0
    if py_stab is not None:
        assert py_stab.compute_effective_stability(-0.28, 0.50) == 1.0


@pytest.mark.tier1
def test_tc1_06_05_positive_benefit_stability_dampening() -> None:
    """TC1.06.05: For positive composite C >= 0, S_eff = S (dampening applies)."""
    s_eff = effective_stability_oracle(c=0.319, s=0.90)
    assert s_eff == 0.90
    if py_stab is not None:
        assert py_stab.compute_effective_stability(0.319, 0.90) == 0.90
