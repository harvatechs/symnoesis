"""Tier 1 Feature Tests: F10 Governance Zones (SPEC §9).

Verifies the 7 governance zones (Z1..Z7), strict precedence hierarchy, and secondary tag collection.
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import governance_zones_oracle


@pytest.mark.tier1
def test_tc1_10_01_z1_symbiotic_nominal() -> None:
    """TC1.10.01: SQ >= 60, clear gate, stable trajectory assigns Z1 Symbiotic."""
    res = governance_zones_oracle(sq=65.0, has_confirmed_chi=False, is_trajectory_negative=False)
    assert res.primary == "Z1"


@pytest.mark.tier1
def test_tc1_10_02_z2_productive_nominal() -> None:
    """TC1.10.02: 25 <= SQ < 60 assigns Z2 Productive."""
    res = governance_zones_oracle(sq=35.0, has_confirmed_chi=False, is_trajectory_negative=False)
    assert res.primary == "Z2"


@pytest.mark.tier1
def test_tc1_10_03_z3_neutral_nominal() -> None:
    """TC1.10.03: -25 < SQ < 25 assigns Z3 Neutral."""
    res = governance_zones_oracle(sq=10.0, has_confirmed_chi=False, is_trajectory_negative=False)
    assert res.primary == "Z3"


@pytest.mark.tier1
def test_tc1_10_04_z6_harm_nominal() -> None:
    """TC1.10.04: SQ <= -25 assigns Z6 Harm (preceding Z5/Z4/Z3)."""
    res = governance_zones_oracle(sq=-30.0, has_confirmed_chi=False)
    assert res.primary == "Z6"


@pytest.mark.tier1
def test_tc1_10_05_z5_dependence_pattern() -> None:
    """TC1.10.05: Pattern (H1 == 0 or H4 == 0) and M2 == 0 triggers Z5 Dependence."""
    # H1=0, H4=1, M2=0 with moderate score SQ=15.0 (otherwise Z3)
    res = governance_zones_oracle(
        sq=15.0,
        h_bits=[0, 1, 1, 1],
        m_bits=[1, 0, 1, 1],
        has_confirmed_chi=False,
    )
    assert res.primary == "Z5"
    assert "Z3" in res.secondary_tags
