"""Tier 2 Boundary Tests: F09–F10 Classes & Governance Zone Boundaries.

Verifies:
- F09: Exact threshold boundaries (+/-0.2000) for the 3-state sign operator
- F10: Exact threshold boundaries for governance zones (+60, +25, -25) and precedence overrides
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import governance_zones_oracle, sign3_oracle, symbiosis_class_oracle

# --- F09 Class Boundaries ---


@pytest.mark.tier2
def test_tc2_09_01_exact_positive_sign3_threshold() -> None:
    """TC2.09.01: x == +0.200000 maps to 0 (neutral); strictly > 0.20 maps to +1."""
    assert sign3_oracle(0.200000) == 0
    assert sign3_oracle(0.200001) == 1


@pytest.mark.tier2
def test_tc2_09_02_exact_negative_sign3_threshold() -> None:
    """TC2.09.02: x == -0.200000 maps to 0 (neutral); strictly < -0.20 maps to -1."""
    assert sign3_oracle(-0.200000) == 0
    assert sign3_oracle(-0.200001) == -1


@pytest.mark.tier2
def test_tc2_09_03_neutralism_boundary_state() -> None:
    """TC2.09.03: HNE = 0.20, SNE = 0.20 are both neutral, producing Neutralism."""
    tech, pub = symbiosis_class_oracle(hne=0.20, sne=0.20)
    assert tech == "neutralism"
    assert pub == "Neutral"


@pytest.mark.tier2
def test_tc2_09_04_operator_blind_amensalism_state() -> None:
    """TC2.09.04: HNE = -0.25, SNE = 0.0 with operator_blind=True produces Amensalism."""
    tech, pub = symbiosis_class_oracle(hne=-0.25, sne=0.0, operator_blind=True)
    assert tech == "amensalism"
    assert pub == "Human harmed"


@pytest.mark.tier2
def test_tc2_09_05_all_nine_class_grid_coverage() -> None:
    """TC2.09.05: Tests all 9 sign permutations across {-1, 0, +1}^2."""
    classes_seen = set()
    for h in (-0.5, 0.0, 0.5):
        for s in (-0.5, 0.0, 0.5):
            tech, _ = symbiosis_class_oracle(h, s, operator_blind=False)
            classes_seen.add(tech)
    assert len(classes_seen) == 9


# --- F10 Zone Boundaries ---


@pytest.mark.tier2
def test_tc2_10_01_z1_symbiotic_exact_boundary() -> None:
    """TC2.10.01: SQ == +60.0000 assigns Z1; SQ == +59.9999 assigns Z2."""
    res_60 = governance_zones_oracle(sq=60.0, has_confirmed_chi=False, is_trajectory_negative=False)
    res_59 = governance_zones_oracle(
        sq=59.9999, has_confirmed_chi=False, is_trajectory_negative=False
    )
    assert res_60.primary == "Z1"
    assert res_59.primary == "Z2"


@pytest.mark.tier2
def test_tc2_10_02_z2_productive_exact_boundary() -> None:
    """TC2.10.02: SQ == +25.0000 assigns Z2; SQ == +24.9999 assigns Z3."""
    res_25 = governance_zones_oracle(sq=25.0, has_confirmed_chi=False, is_trajectory_negative=False)
    res_24 = governance_zones_oracle(
        sq=24.9999, has_confirmed_chi=False, is_trajectory_negative=False
    )
    assert res_25.primary == "Z2"
    assert res_24.primary == "Z3"


@pytest.mark.tier2
def test_tc2_10_03_z6_harm_exact_boundary() -> None:
    """TC2.10.03: SQ == -25.0000 assigns Z6; SQ == -24.9999 assigns Z3."""
    res_neg25 = governance_zones_oracle(sq=-25.0, has_confirmed_chi=False)
    res_neg24 = governance_zones_oracle(sq=-24.9999, has_confirmed_chi=False)
    assert res_neg25.primary == "Z6"
    assert res_neg24.primary == "Z3"


@pytest.mark.tier2
def test_tc2_10_04_z5_dependence_boundary_bit_patterns() -> None:
    """TC2.10.04: Tests bit boundary: H1=0 or H4=0 combined with M2=0 triggers Z5."""
    # H1=0, H4=1, M2=0 -> matches Z5
    res1 = governance_zones_oracle(sq=10.0, h_bits=[0, 1, 1, 1], m_bits=[1, 0, 1, 1])
    # H1=1, H4=0, M2=0 -> matches Z5
    res2 = governance_zones_oracle(sq=10.0, h_bits=[1, 1, 1, 0], m_bits=[1, 0, 1, 1])
    # H1=1, H4=1, M2=0 -> does NOT match Z5 (falls to Z3)
    res3 = governance_zones_oracle(sq=10.0, h_bits=[1, 1, 1, 1], m_bits=[1, 0, 1, 1])
    assert res1.primary == "Z5"
    assert res2.primary == "Z5"
    assert res3.primary == "Z3"


@pytest.mark.tier2
def test_tc2_10_05_z7_critical_overrides_high_sq() -> None:
    """TC2.10.05: High SQ (+95.0) is overridden to Z7 Critical if confirmed CHI event."""
    res = governance_zones_oracle(sq=95.0, has_confirmed_chi=True)
    assert res.primary == "Z7"
