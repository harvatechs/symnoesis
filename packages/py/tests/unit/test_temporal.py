"""Unit tests for Longitudinal Temporal Engine and Trajectory Diagnostics.

Tests normative requirements of SPEC §9, §10:
- Multi-frame observation sequence: [1, 7, 28, 84, 182]
- Day 1 baseline frame tagging
- Consecutive interval delta calculation Delta SQ_k
- Minimum Detectable Change (MDC) and SEM theoretical calculations
- Two consecutive intervals requirement for trajectory classification
- Status: improving, stable, deteriorating
- Insufficient history (< 3 frames) returns stable
- Integration with governance zone Z4 Drift
"""

from __future__ import annotations

import math

import pytest

from symnoesis.config import SymnoesisConfig
from symnoesis.temporal import (
    compute_interval_deltas,
    compute_mdc,
    compute_sem,
    evaluate_trajectory,
    is_baseline_frame,
    is_trajectory_negative,
)
from symnoesis.zones import evaluate_zones


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_standard_frame_sequence(config: SymnoesisConfig) -> None:
    """TC1.19.01: Standard observation windows are at days 1, 7, 28, 84, 182."""
    frames = config.temporal.frames_days
    assert frames == [1, 7, 28, 84, 182]
    assert len(frames) == 5
    assert frames[0] == 1


def test_day_1_baseline_tagging() -> None:
    """TC1.19.02: Frame 1 is tagged as baseline."""
    assert is_baseline_frame(1)
    assert not is_baseline_frame(7)
    assert not is_baseline_frame(28)


def test_interval_delta_calculation() -> None:
    """TC1.19.03: Computes consecutive interval deltas Delta SQ_k."""
    scores = [20.0, 24.0, 18.0]
    deltas = compute_interval_deltas(scores)
    assert deltas == [+4.0, -6.0]
    assert compute_interval_deltas([30.0]) == []


def test_mdc_theoretical_and_sem_formulas() -> None:
    """TC1.20.01 & TC1.20.02: MDC = 1.96 * sqrt(2) * SEM and SEM = SD * sqrt(1 - r)."""
    # SEM test
    sd = 10.0
    r = 0.84
    sem = compute_sem(sd, r)
    assert abs(sem - 4.0) < 1e-12

    with pytest.raises(ValueError):
        compute_sem(-1.0, 0.8)
    with pytest.raises(ValueError):
        compute_sem(10.0, 1.2)

    # MDC test with given sem = 2.0
    mdc = compute_mdc(sem=2.0)
    expected_mdc = 1.96 * math.sqrt(2.0) * 2.0
    assert abs(mdc - expected_mdc) < 1e-12
    assert abs(mdc - 5.5437) < 1e-3

    # MDC test with sd and r
    mdc_sdr = compute_mdc(sd=10.0, r=0.84)
    assert abs(mdc_sdr - (1.96 * math.sqrt(2.0) * 4.0)) < 1e-12

    # Default placeholder
    assert compute_mdc() == 5.0


def test_trajectory_negative_classification(config: SymnoesisConfig) -> None:
    """TC1.19.05: Two consecutive drops > MDC classifies trajectory as deteriorating / negative."""
    # Drops of -6.0 and -7.0 (> MDC 5.0) -> negative
    scores = [30.0, 24.0, 17.0]
    result = evaluate_trajectory(scores, mdc=5.0, config=config)
    assert result.status == "deteriorating"
    assert result.status_code == "negative"
    assert result.is_negative
    assert not result.is_improving
    assert not result.is_stable
    assert is_trajectory_negative(scores, mdc=5.0, config=config)


def test_trajectory_improving_classification(config: SymnoesisConfig) -> None:
    """Two consecutive gains > MDC classifies trajectory as improving / positive."""
    # Gains of +6.0 and +7.0 (> MDC 5.0) -> improving
    scores = [20.0, 26.0, 33.0]
    result = evaluate_trajectory(scores, mdc=5.0, config=config)
    assert result.status == "improving"
    assert result.status_code == "positive"
    assert result.is_improving
    assert not result.is_negative


def test_trajectory_single_drop_recovery_remains_stable(config: SymnoesisConfig) -> None:
    """TC1.20.04: Single drop > MDC followed by recovery does not trigger negative trajectory."""
    # Drop of -8.0 followed by +5.0 -> stable
    scores = [30.0, 22.0, 27.0]
    result = evaluate_trajectory(scores, mdc=5.0, config=config)
    assert result.status == "stable"
    assert result.status_code == "stable"
    assert not result.is_negative
    assert not result.is_improving
    assert result.is_stable


def test_insufficient_frames_returns_stable(config: SymnoesisConfig) -> None:
    """TC2.19.01: Sequence of only 2 frames (1 interval) returns stable."""
    scores = [30.0, 10.0]
    result = evaluate_trajectory(scores, mdc=5.0, config=config)
    assert result.status == "stable"
    assert not result.is_negative


def test_mdc_exact_drop_boundary(config: SymnoesisConfig) -> None:
    """TC2.20.01: Drop of exactly -5.000 does not exceed MDC; -5.001 does."""
    mdc = 5.0
    # Exactly -5.000 drops: 40 -> 35 -> 30
    exact_res = evaluate_trajectory([40.0, 35.0, 30.0], mdc=mdc, config=config)
    assert exact_res.status == "stable"

    # Exceeding drops: 40 -> 34.999 (-5.001) -> 29.998 (-5.001)
    exceed_res = evaluate_trajectory([40.0, 34.999, 29.998], mdc=mdc, config=config)
    assert exceed_res.status == "deteriorating"
    assert exceed_res.is_negative


def test_drift_zone_triggering(config: SymnoesisConfig) -> None:
    """TC1.20.05: Negative trajectory triggers Zone Z4 Drift."""
    # Productive SQ (45.0) would normally be Z2, but negative trajectory triggers Z4
    is_neg = is_trajectory_negative([40.0, 34.999, 29.998], mdc=5.0, config=config)
    assert is_neg

    zone_res = evaluate_zones(
        sq=45.0,
        h_bits=[1, 1, 1, 1],
        m_bits=[1, 1, 1, 1],
        has_confirmed_chi=False,
        is_trajectory_negative=is_neg,
        config=config,
    )
    assert zone_res.primary == "Z4"
    assert "Z2" in zone_res.secondary_tags


def test_trajectory_edge_cases_and_validation(config: SymnoesisConfig) -> None:
    """Verifies edge cases: baseline frame property, invalid sem/mdc inputs."""
    res_single = evaluate_trajectory([25.0], frames=[1], config=config)
    assert res_single.is_baseline
    assert res_single.status == "stable"

    with pytest.raises(ValueError):
        compute_sem(-5.0, 0.5)

    with pytest.raises(ValueError):
        compute_sem(10.0, -0.5)

    with pytest.raises(ValueError):
        compute_sem(10.0, 1.5)

    with pytest.raises(ValueError):
        compute_mdc(sem=-1.0)
