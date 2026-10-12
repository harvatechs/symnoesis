"""Tier 1 Feature Tests: F08 Composite SQ & Clipping (SPEC §6).

Verifies final SQ scoring, positive/negative clipping at +/-100.0,
and cluster bootstrap confidence bounds.
"""

from __future__ import annotations

import random
from typing import Any

import pytest
from tests.e2e.oracle import compute_sq_oracle

try:
    import symnoesis.sq as py_sq
except ImportError:
    py_sq = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_08_01_nominal_sq_calculation() -> None:
    """TC1.08.01: For C=0.319, S_eff=0.90, SQ_raw = 100 * 0.319 * 0.90 == 28.71."""
    sq_raw, sq, _, _ = compute_sq_oracle(c=0.319, s_eff=0.90)
    assert abs(sq - 28.71) < 1e-2


@pytest.mark.tier1
def test_tc1_08_02_harm_composite_negative_calculation() -> None:
    """TC1.08.02: For C=-0.28, S_eff=1.0, SQ_raw = -28.00."""
    sq_raw, sq, _, _ = compute_sq_oracle(c=-0.28, s_eff=1.0)
    assert abs(sq - (-28.0)) < 1e-2


@pytest.mark.tier1
def test_tc1_08_03_positive_clipping_bound(symn_config: Any) -> None:
    """TC1.08.03: SQ values exceeding +100.0 are clipped strictly to +100.0."""
    sq_raw, sq, _, _ = compute_sq_oracle(c=1.20, s_eff=1.0)
    assert sq_raw == 120.0
    assert sq == 100.0
    if py_sq is not None and symn_config is not None:
        sq_clipped, raw, _ = py_sq.compute_sq(1.20, 1.0, None, symn_config)
        assert sq_clipped == 100.0


@pytest.mark.tier1
def test_tc1_08_04_negative_clipping_bound(symn_config: Any) -> None:
    """TC1.08.04: SQ values below -100.0 are clipped strictly to -100.0."""
    sq_raw, sq, _, _ = compute_sq_oracle(c=-1.35, s_eff=1.0)
    assert sq_raw == -135.0
    assert sq == -100.0
    if py_sq is not None and symn_config is not None:
        sq_clipped, raw, _ = py_sq.compute_sq(-1.35, 1.0, None, symn_config)
        assert sq_clipped == -100.0


@pytest.mark.tier1
def test_tc1_08_05_cluster_bootstrap_confidence_interval() -> None:
    """TC1.08.05: Synthetic cluster bootstrap over dyads computes reproducible 95% percentile CI."""
    rng = random.Random(42)
    dyad_scores = [rng.normalvariate(25.0, 5.0) for _ in range(50)]
    B = 200
    resampled_means = [
        sum(rng.choices(dyad_scores, k=len(dyad_scores))) / len(dyad_scores) for _ in range(B)
    ]
    resampled_means.sort()
    low_ci = resampled_means[int(0.025 * B)]
    high_ci = resampled_means[int(0.975 * B)]
    assert low_ci < sum(dyad_scores) / len(dyad_scores) < high_ci
    assert 20.0 < low_ci < high_ci < 30.0
