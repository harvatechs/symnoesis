"""Tier 4 Real-World Scenario: Longitudinal Trajectory & Drift Detection.

Simulates multi-frame longitudinal tracking across days 1, 7, 28, 84, 182:
1. Frame 1 (Day 1) serves as baseline with state metrics only (E1 tier).
2. Frames 2 & 3 show stable engagement.
3. Frames 4 & 5 exhibit consecutive performance drops exceeding MDC (5.0 SQ points).
4. Trajectory engine transitions status from stable to negative.
5. Governance zone updates from Z2 Productive to Z4 Drift.
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import governance_zones_oracle, trajectory_oracle


@pytest.mark.tier4
def test_scenario_02_longitudinal_drift_workflow() -> None:
    """Scenario 2: Longitudinal tracking and drift detection across standard temporal frames."""
    # Frames at Days [1, 7, 28, 84, 182]
    # Frame 1: Day 1 (Baseline)
    frame_1_sq = 45.0
    frame_1_meta = {"day": 1, "label": "baseline", "evidence_tier": "E1"}
    assert frame_1_meta["label"] == "baseline"

    # Frame 2: Day 7 (Early adoption)
    frame_2_sq = 47.0  # +2.0 gain
    # Frame 3: Day 28 (Habituation)
    frame_3_sq = 46.0  # -1.0 change

    # Status across first 3 frames is stable
    early_traj = trajectory_oracle([frame_1_sq, frame_2_sq, frame_3_sq], mdc=5.0)
    assert early_traj == "stable"

    # Frame 4: Day 84 (Erosion begins)
    frame_4_sq = 40.0  # -6.0 drop (> MDC 5.0)
    mid_traj = trajectory_oracle([frame_1_sq, frame_2_sq, frame_3_sq, frame_4_sq], mdc=5.0)
    # Single drop does NOT trigger negative trajectory
    assert mid_traj == "stable"

    # Frame 5: Day 182 (Chronic dependence / degradation)
    frame_5_sq = 33.5  # -6.5 drop (> MDC 5.0)
    full_series = [frame_1_sq, frame_2_sq, frame_3_sq, frame_4_sq, frame_5_sq]
    final_traj = trajectory_oracle(full_series, mdc=5.0)
    # Two consecutive intervals with drop > MDC triggers negative trajectory
    assert final_traj == "negative"

    # Zone evaluation before drift was Z2 Productive
    early_zone = governance_zones_oracle(sq=frame_3_sq, is_trajectory_negative=False)
    assert early_zone.primary == "Z2"

    # Zone evaluation after drift shifts to Z4 Drift despite SQ still being > 25 (33.5)
    drift_zone = governance_zones_oracle(sq=frame_5_sq, is_trajectory_negative=True)
    assert drift_zone.primary == "Z4"
    assert "Z2" in drift_zone.secondary_tags
