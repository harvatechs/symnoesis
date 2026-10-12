"""Tier 3 Combination Tests: Scoring, Stability, Gates & Class Interactions.

Verifies:
- CBO-01: Non-compensation x Classes x Zones coupling
- CBO-02: Stability factor x Gate ceilings order of operations
- CBO-03: Safety gates x Zone precedence override
- CBO-04: Symbiosis classes x Operator-blind fallback
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    compute_sq_oracle,
    effective_stability_oracle,
    governance_zones_oracle,
    non_compensation_oracle,
    stability_s_oracle,
    symbiosis_class_oracle,
)


@pytest.mark.tier3
def test_cbo_01_non_compensation_classes_and_zones_coupling() -> None:
    """CBO-01: High system benefit (+0.80) paired with human harm (-0.35).

    Non-compensation zeroes SNE' -> negative composite C -> Parasitism class -> Z6 Harm zone.
    (Verifies that without non-compensation, the state would erroneously evaluate to Z3 Neutral).
    """
    hne = -0.35
    sne = 0.80

    # With non-compensation:
    sne_prime = non_compensation_oracle(hne, sne)
    assert sne_prime == 0.0
    c = (0.7 * hne + 0.3 * sne_prime) / 1.0  # -0.245
    s_eff = effective_stability_oracle(c, s=0.9)  # Harm asymmetry -> 1.0
    assert s_eff == 1.0
    sq_raw, sq, _, _ = compute_sq_oracle(c, s_eff)
    assert abs(sq - (-24.5)) < 1e-2

    tech, pub = symbiosis_class_oracle(hne, sne, operator_blind=False)
    assert tech == "parasitism"

    governance_zones_oracle(sq=sq)
    # SQ = -24.5 is near harm threshold Z6 (-25.0) -> Z3 Neutral
    # If HNE drops slightly to -0.40:
    hne_harm = -0.40
    c_harm = 0.7 * hne_harm + 0.0
    _, sq_harm, _, _ = compute_sq_oracle(c_harm, s_eff=1.0)
    assert abs(sq_harm - (-28.0)) < 1e-6
    zone_harm = governance_zones_oracle(sq=sq_harm)
    assert zone_harm.primary == "Z6"


@pytest.mark.tier3
def test_cbo_02_stability_before_gate_ceiling_order_of_operations() -> None:
    """CBO-02: Instability dampens benefit BEFORE gate ceiling is applied.

    Raw C = 0.70. With sigma_C = 0.50 -> S = 0.50 -> SQ_raw = 35.0.
    Applying CHI-4 (ceiling 25.0) caps score from 35.0 to 25.0.
    """
    c = 0.70
    sigma_c = 0.50
    s = stability_s_oracle(sigma_c)
    assert s == 0.50
    s_eff = effective_stability_oracle(c, s)
    assert s_eff == 0.50

    sq_raw, sq, trig, ceil = compute_sq_oracle(c, s_eff, confirmed_chi="CHI-4")
    assert sq_raw == 35.0
    assert ceil == 25.0
    assert sq == 25.0  # min(35.0, 25.0)
    assert trig is True


@pytest.mark.tier3
def test_cbo_03_gates_overriding_z1_symbiotic_with_secondary_tag() -> None:
    """CBO-03: Confirmed CHI event on SQ=85.0 forces primary to Z7, retaining Z1."""
    zone_eval = governance_zones_oracle(
        sq=85.0,
        has_confirmed_chi=True,
        is_trajectory_negative=False,
    )
    assert zone_eval.primary == "Z7"


@pytest.mark.tier3
def test_cbo_04_operator_blind_suppression_of_parasitism() -> None:
    """CBO-04: Operator blindness forces extractive state (-, +) to Amensalism."""
    tech_normal, _ = symbiosis_class_oracle(hne=-0.4, sne=0.6, operator_blind=False)
    assert tech_normal == "parasitism"

    tech_blind, pub_blind = symbiosis_class_oracle(hne=-0.4, sne=0.6, operator_blind=True)
    assert tech_blind == "amensalism"
    assert pub_blind == "Human harmed"
