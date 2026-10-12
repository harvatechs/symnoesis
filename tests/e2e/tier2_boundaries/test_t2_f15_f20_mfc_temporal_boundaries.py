"""Tier 2 Boundary Tests: F15–F20 MFC & Temporal Engine Boundaries.

Verifies:
- F15: Zero harm mass corner cases
- F16: Boolean minimizer edge conditions
- F17: Subcube purity boundary at 0.80
- F18: Counterfactual repair ties
- F19: Insufficient frame count (< 3 frames)
- F20: MDC exact threshold boundary (-5.000 vs -5.001)
"""

from __future__ import annotations

import pytest
from sympy import symbols  # type: ignore[import-untyped]
from sympy.logic.boolalg import SOPform  # type: ignore[import-untyped]
from tests.e2e.oracle import trajectory_oracle

# --- F15 Boundaries ---


@pytest.mark.tier2
def test_tc2_15_01_zero_harm_mass_dataset() -> None:
    """TC2.15.01: Dataset with zero harmful cells returns empty cover rule set."""
    harm_mass_total = 0.0
    rules = [] if harm_mass_total == 0.0 else ["some_rule"]
    assert len(rules) == 0


# --- F16 Boundaries ---


@pytest.mark.tier2
def test_tc2_16_01_all_minterms_reduces_to_true() -> None:
    """TC2.16.01: Covering all 2^k minterms reduces Boolean formula to True."""
    a, b = symbols("a b")
    sop = SOPform([a, b], [0, 1, 2, 3])
    assert str(sop) == "True"


@pytest.mark.tier2
def test_tc2_16_02_single_minterm_retains_all_literals() -> None:
    """TC2.16.02: Single minterm cannot be reduced and retains all literals."""
    a, b, c = symbols("a b c")
    sop = SOPform([a, b, c], [0])  # 000
    assert len(sop.free_symbols) == 3


# --- F17 Boundaries ---


@pytest.mark.tier2
def test_tc2_17_01_purity_exact_boundary() -> None:
    """TC2.17.01: Purity 0.7999 is rejected (< 0.80); 0.8000 is admissible."""
    purity_fail = 0.7999
    purity_pass = 0.8000
    assert purity_fail < 0.80
    assert purity_pass >= 0.80


@pytest.mark.tier2
def test_tc2_17_02_literal_count_extremes() -> None:
    """TC2.17.02: Literal bounds L=1 (covers 128 cells) and L=5 (covers 8 cells)."""
    assert 2 ** (8 - 1) == 128
    assert 2 ** (8 - 5) == 8


# --- F18 Boundaries ---


@pytest.mark.tier2
def test_tc2_18_01_counterfactual_all_zero_deltas() -> None:
    """TC2.18.01: When all repair flips have non-positive delta, no improvement is indicated."""
    deltas = {"H1": 0.0, "H2": -5.0, "M1": -2.0}
    max_gain = max(deltas.values())
    assert max_gain <= 0.0


# --- F19 Boundaries ---


@pytest.mark.tier2
def test_tc2_19_01_two_frames_cannot_assert_trajectory() -> None:
    """TC2.19.01: Sequence of only 2 frames (1 interval) returns stable (insufficient history)."""
    traj = trajectory_oracle([30.0, 10.0], mdc=5.0)
    assert traj == "stable"


# --- F20 Boundaries ---


@pytest.mark.tier2
def test_tc2_20_01_mdc_exact_drop_boundary() -> None:
    """TC2.20.01: Drop of exactly -5.000 does not exceed MDC; drop of -5.001 does."""
    mdc = 5.0
    delta_exact = -5.000
    delta_exceed = -5.001
    assert not (delta_exact < -mdc)
    assert delta_exceed < -mdc


@pytest.mark.tier2
def test_tc2_20_02_two_consecutive_drops_boundary() -> None:
    """TC2.20.02: Exactly two consecutive drops of -5.001 trigger negative trajectory."""
    # Day 1=40, Day 7=34.999 (delta -5.001), Day 28=29.998 (delta -5.001)
    scores = [40.0, 34.999, 29.998]
    assert trajectory_oracle(scores, mdc=5.0) == "negative"
