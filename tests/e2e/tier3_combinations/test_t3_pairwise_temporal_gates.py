"""Tier 3 Combination Tests: Temporal Drift, Gates & Governance Precedence.

Verifies:
- CBO-06: Negative trajectory triggering Z4 Drift overriding Z1 and Z2
- CBO-09: Confirmed CHI overriding Z4 Drift into Z7 Critical
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import governance_zones_oracle, trajectory_oracle


@pytest.mark.tier3
def test_cbo_06_temporal_drift_overrides_high_sq() -> None:
    """CBO-06: High SQ (+55.0) paired with negative trajectory drops to Zone Z4 Drift."""
    # Sequence with consecutive drops: [65.0, 58.0, 51.0] (deltas -7.0, -7.0 > MDC 5.0)
    traj = trajectory_oracle([65.0, 58.0, 51.0], mdc=5.0)
    assert traj == "negative"

    zone = governance_zones_oracle(
        sq=51.0,
        has_confirmed_chi=False,
        is_trajectory_negative=True,
    )
    # Z4 Drift takes precedence over Z2 (+25 <= SQ < 60)
    assert zone.primary == "Z4"
    assert "Z2" in zone.secondary_tags


@pytest.mark.tier3
def test_cbo_09_critical_chi_overrides_temporal_drift() -> None:
    """CBO-09: Confirmed CHI overrides negative trajectory (Z4) and score to Z7 Critical."""
    zone = governance_zones_oracle(
        sq=50.0,
        has_confirmed_chi=True,
        is_trajectory_negative=True,
    )
    # Precedence: Z7 > Z6 > Z5 > Z4
    assert zone.primary == "Z7"
    assert "Z4" in zone.secondary_tags
