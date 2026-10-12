"""Tier 1 Feature Tests: F07 Safety Gate Ceiling (SPEC §7).

Verifies Critical Harm Indicator (CHI) ceilings, ceiling math, and critical zone forcing.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import compute_sq_oracle, governance_zones_oracle

try:
    import symnoesis.gates as py_gates
    import symnoesis.sq as py_sq
except ImportError:
    py_gates = None  # type: ignore[assignment]
    py_sq = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_07_01_gate_clear_state(symn_config: Any) -> None:
    """TC1.07.01: When confirmed_chi is None, SQ equals SQ_raw with gate_triggered=False."""
    sq_raw, sq, triggered, ceiling = compute_sq_oracle(c=0.319, s_eff=0.90, confirmed_chi=None)
    assert abs(sq_raw - 28.71) < 1e-2
    assert sq == sq_raw
    assert triggered is False
    assert ceiling is None
    if py_sq is not None and symn_config is not None:
        sq_clipped, raw, g_trig = py_sq.compute_sq(0.319, 0.90, None, symn_config)
        assert abs(sq_clipped - 28.71) < 1e-2
        assert g_trig is False


@pytest.mark.tier1
def test_tc1_07_02_chi1_critical_gate_zero_ceiling(symn_config: Any) -> None:
    """TC1.07.02: Confirmed CHI-1 / CHI-2 caps positive score to 100 * 0.0 == 0.0."""
    sq_raw, sq, triggered, ceiling = compute_sq_oracle(c=0.60, s_eff=1.0, confirmed_chi="CHI-2")
    assert sq_raw == 60.0
    assert sq == 0.0
    assert triggered is True
    assert ceiling == 0.0
    if py_sq is not None and symn_config is not None:
        sq_clipped, _, g_trig = py_sq.compute_sq(0.60, 1.0, 0.0, symn_config)
        assert sq_clipped == 0.0
        assert g_trig is True


@pytest.mark.tier1
def test_tc1_07_03_chi4_manipulation_quarter_ceiling(symn_config: Any) -> None:
    """TC1.07.03: Confirmed CHI-4 caps score to 100 * 0.25 == 25.0."""
    sq_raw, sq, triggered, ceiling = compute_sq_oracle(c=0.80, s_eff=1.0, confirmed_chi="CHI-4")
    assert sq_raw == 80.0
    assert sq == 25.0
    assert triggered is True
    assert ceiling == 25.0
    if py_sq is not None and symn_config is not None:
        sq_clipped, _, g_trig = py_sq.compute_sq(0.80, 1.0, 0.25, symn_config)
        assert sq_clipped == 25.0
        assert g_trig is True


@pytest.mark.tier1
def test_tc1_07_04_negative_score_retention_under_ceiling(symn_config: Any) -> None:
    """TC1.07.04: Gate is a ceiling min(SQ_raw, 100*G), not a multiplier; negative harm is kept."""
    sq_raw, sq, triggered, ceiling = compute_sq_oracle(c=-0.50, s_eff=1.0, confirmed_chi="CHI-4")
    assert sq_raw == -50.0
    assert sq == -50.0  # min(-50.0, 25.0) == -50.0
    assert triggered is True
    assert ceiling == 25.0
    if py_sq is not None and symn_config is not None:
        sq_clipped, _, _ = py_sq.compute_sq(-0.50, 1.0, 0.25, symn_config)
        assert sq_clipped == -50.0


@pytest.mark.tier1
def test_tc1_07_05_critical_zone_assignment() -> None:
    """TC1.07.05: Confirmed CHI event forces Zone to Z7 Critical regardless of SQ value."""
    zone_eval = governance_zones_oracle(sq=80.0, has_confirmed_chi=True)
    assert zone_eval.primary == "Z7"
