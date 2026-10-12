"""Tier 3 Combination Tests: Geometry, Pixel Assignment & Zone Patterns.

Verifies:
- CBO-05: Grid mapping x Probabilistic assignment x Mass conservation
- CBO-08: Pixel 8-bit patterns x Governance Zone Z5 Dependence
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    compute_joint_masses_oracle,
    coord_to_pixel_id_oracle,
    governance_zones_oracle,
    pixel_id_to_coord_oracle,
)


@pytest.mark.tier3
def test_cbo_05_grid_mapping_mass_conservation_across_coordinates() -> None:
    """CBO-05: Mapping probabilities to 256 coordinates preserves exact total mass of 1.0."""
    probs = [0.85, 0.65, 0.45, 0.35, 0.75, 0.55, 0.25, 0.15]
    masses = compute_joint_masses_oracle(probs, prune=True)
    assert len(masses) == 256
    assert abs(sum(masses) - 1.0) < 1e-11

    # Verify that each cell index maps cleanly to a valid coordinate
    for c in range(256):
        if masses[c] > 0.0:
            h_code = (c >> 4) & 0xF
            m_code = c & 0xF
            from tests.e2e.oracle import gray_to_int_oracle

            col = gray_to_int_oracle(h_code)
            row = gray_to_int_oracle(m_code)
            assert 0 <= col < 16 and 0 <= row < 16
            pid = coord_to_pixel_id_oracle(col, row)
            rec_col, rec_row = pixel_id_to_coord_oracle(pid)
            assert (rec_col, rec_row) == (col, row)


@pytest.mark.tier3
def test_cbo_08_z5_dependence_interaction_with_modal_pixel_bits() -> None:
    """CBO-08: Pattern (H1 == 0 or H4 == 0) and M2 == 0 on modal pixel forces Zone Z5."""
    # Pixel with H = [0, 1, 1, 1] and M = [1, 0, 1, 1]
    # Modal pixel has H1 = 0 and M2 = 0
    h_bits = [0, 1, 1, 1]
    m_bits = [1, 0, 1, 1]
    # Even if score is productive (e.g. SQ = +35.0), Z5 takes precedence over Z2 and Z3!
    zone_eval = governance_zones_oracle(
        sq=35.0,
        h_bits=h_bits,
        m_bits=m_bits,
        has_confirmed_chi=False,
        is_trajectory_negative=False,
    )
    assert zone_eval.primary == "Z5"
    assert "Z2" in zone_eval.secondary_tags
