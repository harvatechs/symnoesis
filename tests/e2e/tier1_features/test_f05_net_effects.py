"""Tier 1 Feature Tests: F05 Net Effects Calculus (SPEC §5).

Verifies HNE state, HNE outcome blending, SNE components, and the non-compensation rule.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import (
    hne_oracle,
    hne_state_oracle,
    non_compensation_oracle,
    sne_oracle,
)

try:
    import symnoesis.net_effects as py_ne
except ImportError:
    py_ne = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_05_01_human_net_effect_state(symn_config: Any) -> None:
    """TC1.05.01: HNE_state = sum a_i * (2 s_i - 1) with equal weights a_i = 0.25."""
    s_H = [0.8, 0.6, 0.4, 0.7]
    hne = hne_state_oracle(s_H)
    assert abs(hne - 0.25) < 1e-12
    if py_ne is not None and symn_config is not None:
        val, _ = py_ne.compute_hne(s_H, None, symn_config)
        assert abs(val - 0.25) < 1e-12


@pytest.mark.tier1
def test_tc1_05_02_human_net_effect_outcome_blend(symn_config: Any) -> None:
    """TC1.05.02: HNE blends state with outcome deltas: (1 - lambda)*state + lambda*outcome."""
    s_H = [0.8, 0.6, 0.4, 0.7]
    deltas = [0.5, 0.25]
    hne, outcome_avail = hne_oracle(s_H, deltas)
    assert outcome_avail is True
    assert hne > 0.25
    if py_ne is not None and symn_config is not None:
        py_val, py_avail = py_ne.compute_hne(s_H, deltas, symn_config)
        assert py_avail is True
        assert abs(py_val - hne) < 1e-12


@pytest.mark.tier1
def test_tc1_05_03_system_net_effect_linear_combination(symn_config: Any) -> None:
    """TC1.05.03: SNE = 0.4*Integrity + 0.4*Reliability + 0.2*Operator."""
    sne = sne_oracle(0.5, 0.6, 0.2)
    assert abs(sne - 0.48) < 1e-12
    if py_ne is not None and symn_config is not None:
        val, blind = py_ne.compute_sne(0.5, 0.6, 0.2, symn_config)
        assert abs(val - 0.48) < 1e-12
        assert blind is False


@pytest.mark.tier1
def test_tc1_05_04_non_compensation_positive_invariance(symn_config: Any) -> None:
    """TC1.05.04: When HNE >= 0, system gains are preserved: SNE' == SNE."""
    sne_prime = non_compensation_oracle(hne=0.25, sne=0.48)
    assert sne_prime == 0.48
    if py_ne is not None and symn_config is not None:
        assert py_ne.apply_non_compensation(0.25, 0.48, symn_config) == 0.48


@pytest.mark.tier1
def test_tc1_05_05_non_compensation_clamping(symn_config: Any) -> None:
    """TC1.05.05: When HNE < 0, system gains cannot compensate: SNE' = min(SNE, 0)."""
    sne_prime = non_compensation_oracle(hne=-0.4, sne=0.5)
    assert sne_prime == 0.0
    sne_loss = non_compensation_oracle(hne=-0.4, sne=-0.3)
    assert sne_loss == -0.3
    if py_ne is not None and symn_config is not None:
        assert py_ne.apply_non_compensation(-0.4, 0.5, symn_config) == 0.0
        assert py_ne.apply_non_compensation(-0.4, -0.3, symn_config) == -0.3
