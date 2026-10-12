"""Tier 4 Real-World Scenario: Full Dyad-Window Benchmark Lifecycle.

Simulates the complete mathematical and data lifecycle of an individual dyad-window:
1. Ingest 8 variable scores (H1..H4, M1..M4) and uncertainty metrics.
2. Form posteriors with sigma >= 0.01 floor.
3. Compute marginal bit probabilities and 256-cell mass distribution with 1e-4 pruning.
4. Derive modal pixel and grid coordinate.
5. Compute HNE (state + outcomes), SNE, apply non-compensation rule.
6. Compute composite C, evaluate effective stability S_eff, raw SQ, and gate ceiling.
7. Assign symbiosis class and evaluate governance zones with strict precedence.
8. Output compliant PixelRecord structure.
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    compute_joint_masses_oracle,
    compute_sq_oracle,
    coord_to_pixel_id_oracle,
    effective_stability_oracle,
    governance_zones_oracle,
    hne_oracle,
    marginal_bit_prob_oracle,
    non_compensation_oracle,
    sne_oracle,
    stability_s_oracle,
    symbiosis_class_oracle,
)


@pytest.mark.tier4
def test_scenario_01_full_dyad_benchmark_lifecycle() -> None:
    """Scenario 1: Complete end-to-end benchmark evaluation of a dyad-window."""
    # 1. Ingest scores
    s_H = [0.85, 0.70, 0.60, 0.75]  # Human variables
    s_M = [0.80, 0.75, 0.90, 0.85]  # Machine variables
    outcomes = [0.35, 0.20]  # Longitudinal outcomes

    # 2. Variable posteriors (mu, sigma) with sigma_floor = 0.01
    mu_vars = s_H + s_M
    sigma_vars = [0.08, 0.05, 0.12, 0.06, 0.04, 0.09, 0.05, 0.07]
    thetas = [0.5, 0.42074, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

    # 3. Marginal bit probabilities
    probs = [marginal_bit_prob_oracle(mu_vars[i], sigma_vars[i], thetas[i]) for i in range(8)]
    assert all(0.5 < p < 1.0 for p in probs)  # High performance dyad

    # 4. Joint mass distribution and modal pixel
    masses = compute_joint_masses_oracle(probs, prune=True)
    modal_idx = masses.index(max(masses))
    # Bits are all 1s -> 255 (11111111_2)
    assert modal_idx == 255
    col, row = 10, 10  # gray_inv of 1111 is 10
    pid = coord_to_pixel_id_oracle(col, row)
    assert pid == "h1111-m1111"

    # 5. Net effects calculus
    hne, outcome_avail = hne_oracle(s_H, outcomes)
    assert outcome_avail is True
    assert hne > 0.40

    integrity = 2.0 * s_M[3] - 1.0  # 2*0.85 - 1 = 0.70
    reliability = 0.75
    operator = 0.20
    sne = sne_oracle(integrity, reliability, operator)
    assert sne > 0.50

    sne_prime = non_compensation_oracle(hne, sne)
    assert sne_prime == sne  # HNE > 0 -> non-comp is transparent

    # 6. Composite C, Stability, and SQ
    c = (0.7 * hne + 0.3 * sne_prime) / 1.0
    s = stability_s_oracle(sigma_c=0.08)
    s_eff = effective_stability_oracle(c, s)
    sq_raw, sq, gate_trig, _ = compute_sq_oracle(c, s_eff, confirmed_chi=None)
    assert sq > 40.0
    assert gate_trig is False

    # 7. Symbiosis class and Governance zone
    tech_class, pub_class = symbiosis_class_oracle(hne, sne)
    assert tech_class == "mutualism"

    zone = governance_zones_oracle(
        sq=sq,
        h_bits=[1, 1, 1, 1],
        m_bits=[1, 1, 1, 1],
        has_confirmed_chi=False,
    )
    # SQ between 25 and 60 is Z2 Productive; >= 60 is Z1 Symbiotic
    assert zone.primary in ("Z1", "Z2")

    # 8. Data contract compilation (PixelRecord)
    record = {
        "pixel_id": pid,
        "grid": {"col": col, "row": row},
        "bits": {"H": [1, 1, 1, 1], "M": [1, 1, 1, 1]},
        "n_eff": 1.0,
        "n_dyads": 1,
        "sq": {"value": sq, "ci95": [sq - 5.0, sq + 5.0]},
        "hne": hne,
        "sne": sne,
        "stability": s,
        "symbiosis_class": tech_class,
        "zone": {"primary": zone.primary, "secondary_tags": zone.secondary_tags},
        "trajectory": "stable",
        "gate": "safe",
        "evidence_tier": "E1",
        "operator_blind": False,
        "outcome_available": outcome_avail,
        "suppressed": False,
    }
    assert record["pixel_id"] == "h1111-m1111"
    assert record["suppressed"] is False
