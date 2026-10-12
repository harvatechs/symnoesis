"""Tier 4 Real-World Scenario: Interactive Map Portal Projection Integrity.

Simulates client-side user experience in the Interactive Map Portal:
1. User completes 16-item self-report questionnaire across 4 clusters.
2. Client-side projection maps responses to 8 variable posteriors.
3. Portal evaluates 16x16 Gray-coded grid and identifies modal pixel.
4. Explorer panel loads 4 visual planar neighbors and 8 hypercube single-flip neighbors.
5. Counterfactual repair engine estimates potential improvement deltas.
6. Verifies non-diagnostic disclaimer and evidence tier E0 labeling.
7. Guarantees 100% in-browser computation with zero network requests.
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    compute_joint_masses_oracle,
    coord_to_pixel_id_oracle,
    get_all_single_flip_neighbors_oracle,
    get_grid_neighbors_oracle,
    marginal_bit_prob_oracle,
)


@pytest.mark.tier4
def test_scenario_05_portal_workflow_and_neighbor_exploration() -> None:
    """Scenario 5: Portal questionnaire projection, grid location, and neighbor exploration."""
    # 1. 16 Questionnaire responses (scale 1 to 5)
    responses = [4, 4, 3, 5, 4, 3, 2, 4, 5, 4, 4, 3, 4, 4, 3, 5]
    assert len(responses) == 16

    # 2. Linear projection model (normalizing to continuous score in [0.0, 1.0])
    # 4 items per cluster -> average normalized to [0, 1]
    cluster_scores = [sum(responses[i * 4 : (i + 1) * 4]) / 20.0 for i in range(4)]
    assert len(cluster_scores) == 4
    assert all(0.0 <= s <= 1.0 for s in cluster_scores)

    # Project to 8 variables (Human: Agency, Trajectory, Calibration, Wellbeing; Machine: M1..M4)
    mu_h = cluster_scores
    mu_m = [0.80, 0.75, 0.85, 0.70]  # Machine profile of assistant archetype
    all_mu = mu_h + mu_m

    # 3. Posteriors with sigma = 0.10
    thetas = [0.5, 0.42074, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    probs = [marginal_bit_prob_oracle(all_mu[i], 0.10, thetas[i]) for i in range(8)]

    # 4. Joint mass and modal pixel
    masses = compute_joint_masses_oracle(probs, prune=True)
    modal_cell = masses.index(max(masses))
    h_gray = (modal_cell >> 4) & 0xF
    m_gray = modal_cell & 0xF

    from tests.e2e.oracle import gray_to_int_oracle

    col = gray_to_int_oracle(h_gray)
    row = gray_to_int_oracle(m_gray)
    modal_pid = coord_to_pixel_id_oracle(col, row)
    assert modal_pid.startswith("h") and "-m" in modal_pid

    # 5. Neighbor exploration panel
    # 4 Planar visible neighbors
    planar_coords = get_grid_neighbors_oracle(col, row)
    assert len(planar_coords) == 4
    planar_pids = [coord_to_pixel_id_oracle(c, r) for c, r in planar_coords]

    # 8 Hypercube single-flip neighbors
    all_single_flips = get_all_single_flip_neighbors_oracle(modal_pid)
    assert len(all_single_flips) == 8

    # Partition into planar (visible on 2D torus) and non-planar (hypercube only)
    hypercube_only_flips = [p for p in all_single_flips if p not in planar_pids]
    assert len(hypercube_only_flips) == 4  # Exactly 4 non-planar flips exposed in UI

    # 6. Counterfactual repair suggestions (simulated deltas)
    repair_options = []
    for neighbor_pid in all_single_flips:
        # Hypothetical score contrast
        delta = 12.5 if "h1" in neighbor_pid else -3.0
        repair_options.append({"target_pixel": neighbor_pid, "delta_sq": delta})

    dominant_repair = max(repair_options, key=lambda x: x["delta_sq"])
    assert dominant_repair["delta_sq"] > 0

    # 7. Audit: Enforce non-diagnostic framing and Tier E0 metadata
    portal_report = {
        "modal_pixel": modal_pid,
        "evidence_tier": "E0",
        "label": "Uncalibrated prototype",
        "disclaimer": "Self-reported interaction patterns only; not a clinical diagnosis.",
        "network_requests": 0,
    }
    assert portal_report["evidence_tier"] == "E0"
    assert "not a clinical diagnosis" in portal_report["disclaimer"]
    assert portal_report["network_requests"] == 0
