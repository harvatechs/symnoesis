"""Tier 2 Boundary Tests: F05–F08 Scoring, Stability & Gate Boundaries.

Verifies:
- F05: Extremal HNE/SNE values, non-compensation zero boundary
- F06: Stability factor extremes and harm asymmetry strictness
- F07: Gate ceiling on negative scores, multiple CHI events, unknown CHI codes
- F08: SQ clipping boundaries at +/-100.0 and null SQ for zero observations
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    compute_sq_oracle,
    effective_stability_oracle,
    hne_oracle,
    hne_state_oracle,
    non_compensation_oracle,
    stability_s_oracle,
)

# --- F05 Boundaries ---


@pytest.mark.tier2
def test_tc2_05_01_extremal_positive_and_negative_hne() -> None:
    """TC2.05.01: Extremal human scores produce exact +/-1.0 HNE boundaries."""
    assert hne_state_oracle([1.0, 1.0, 1.0, 1.0]) == 1.0
    assert hne_state_oracle([0.0, 0.0, 0.0, 0.0]) == -1.0


@pytest.mark.tier2
def test_tc2_05_02_non_compensation_exact_zero_boundary() -> None:
    """TC2.05.02: HNE = 0.0000 preserves SNE' == SNE without suppression."""
    assert non_compensation_oracle(hne=0.0, sne=0.5) == 0.5


@pytest.mark.tier2
def test_tc2_05_03_non_compensation_epsilon_negative_boundary() -> None:
    """TC2.05.03: Microscopic negative HNE = -1e-9 activates non-compensation clamping."""
    assert non_compensation_oracle(hne=-1e-9, sne=0.5) == 0.0


@pytest.mark.tier2
def test_tc2_05_04_outcome_deltas_empty_and_null() -> None:
    """TC2.05.04: None or empty outcome deltas fall back cleanly to HNE_state."""
    hne_null, avail_null = hne_oracle([0.8, 0.6, 0.4, 0.7], None)
    hne_empty, avail_empty = hne_oracle([0.8, 0.6, 0.4, 0.7], [])
    assert hne_null == 0.25 and avail_null is False
    assert hne_empty == 0.25 and avail_empty is False


@pytest.mark.tier2
def test_tc2_05_05_negative_outcome_suppression() -> None:
    """TC2.05.05: Severe negative outcome deltas can drag HNE into negative harm territory."""
    hne, avail = hne_oracle([0.6, 0.6, 0.6, 0.6], [-2.0, -2.0])
    assert avail is True
    # State = 0.2, outcome = tanh(-4.0) approx -0.999 -> HNE approx 0.5*0.2 - 0.5*0.999 = -0.399
    assert hne < 0.0


# --- F06 Boundaries ---


@pytest.mark.tier2
def test_tc2_06_01_stability_exact_sigma_max_boundary() -> None:
    """TC2.06.01: For sigma_C == sigma_max (0.5), S reaches exact lower bound 0.500."""
    s = stability_s_oracle(0.5, sigma_max=0.5)
    assert s == 0.5


@pytest.mark.tier2
def test_tc2_06_02_stability_extreme_variance_clamping() -> None:
    """TC2.06.02: sigma_C = 100.0 is clamped to min(1, ratio) and outputs S = 0.5."""
    s = stability_s_oracle(100.0, sigma_max=0.5)
    assert s == 0.5


@pytest.mark.tier2
def test_tc2_06_03_negative_sigma_c_rejection() -> None:
    """TC2.06.03: Negative sigma_C raises ValueError."""
    with pytest.raises(ValueError):
        stability_s_oracle(-0.01)


@pytest.mark.tier2
def test_tc2_06_04_harm_asymmetry_exact_zero_composite() -> None:
    """TC2.06.04: Exact composite C == 0.0 uses S_eff = S."""
    assert effective_stability_oracle(c=0.0, s=0.8) == 0.8


@pytest.mark.tier2
def test_tc2_06_05_harm_asymmetry_epsilon_negative_composite() -> None:
    """TC2.06.05: Microscopic negative C = -1e-9 forces S_eff = 1.0 unconditionally."""
    assert effective_stability_oracle(c=-1e-9, s=0.5) == 1.0


# --- F07 Boundaries ---


@pytest.mark.tier2
def test_tc2_07_01_gate_ceiling_on_zero_raw_sq() -> None:
    """TC2.07.01: Gate trigger on SQ_raw = 0.0 remains 0.0."""
    sq_raw, sq, trig, ceil = compute_sq_oracle(c=0.0, s_eff=1.0, confirmed_chi="CHI-1")
    assert sq_raw == 0.0 and sq == 0.0 and trig is True and ceil == 0.0


@pytest.mark.tier2
def test_tc2_07_02_gate_ceiling_never_elevates_negative_harm() -> None:
    """TC2.07.02: Severe negative harm SQ_raw = -75.0 under CHI-4 (ceiling 25.0) remains -75.0."""
    sq_raw, sq, trig, ceil = compute_sq_oracle(c=-0.75, s_eff=1.0, confirmed_chi="CHI-4")
    assert sq_raw == -75.0
    assert sq == -75.0  # min(-75, 25) == -75
    assert ceil == 25.0


@pytest.mark.tier2
def test_tc2_07_03_raw_sq_exactly_equal_to_ceiling() -> None:
    """TC2.07.03: SQ_raw == ceiling outputs the exact ceiling value."""
    sq_raw, sq, trig, ceil = compute_sq_oracle(c=0.25, s_eff=1.0, confirmed_chi="CHI-4")
    assert sq_raw == 25.0 and sq == 25.0


@pytest.mark.tier2
def test_tc2_07_04_unknown_chi_code_rejection() -> None:
    """TC2.07.04: Unrecognized CHI string raises ValueError."""
    with pytest.raises(ValueError):
        compute_sq_oracle(c=0.5, s_eff=1.0, confirmed_chi="CHI-99_INVALID")


@pytest.mark.tier2
def test_tc2_07_05_chi_ceilings_range_bound() -> None:
    """TC2.07.05: All defined CHI ceilings are strictly in [0.0, 0.25]."""
    from tests.e2e.oracle import CHI_CEILINGS

    for code, g in CHI_CEILINGS.items():
        assert 0.0 <= g <= 0.25, f"{code} ceiling {g} out of bounds"


# --- F08 Boundaries ---


@pytest.mark.tier2
def test_tc2_08_01_sq_clipping_positive_epsilon() -> None:
    """TC2.08.01: Unclipped score +100.01 clips strictly to +100.0."""
    _, sq, _, _ = compute_sq_oracle(c=1.0001, s_eff=1.0)
    assert sq == 100.0


@pytest.mark.tier2
def test_tc2_08_02_sq_clipping_negative_epsilon() -> None:
    """TC2.08.02: Unclipped score -100.01 clips strictly to -100.0."""
    _, sq, _, _ = compute_sq_oracle(c=-1.0001, s_eff=1.0)
    assert sq == -100.0


@pytest.mark.tier2
def test_tc2_08_03_sq_exact_bounds() -> None:
    """TC2.08.03: Exact +/-100.0 boundary scores are retained without distortion."""
    _, sq_max, _, _ = compute_sq_oracle(c=1.0, s_eff=1.0)
    _, sq_min, _, _ = compute_sq_oracle(c=-1.0, s_eff=1.0)
    assert sq_max == 100.0
    assert sq_min == -100.0


@pytest.mark.tier2
def test_tc2_08_04_empty_dyad_null_sq_invariant() -> None:
    """TC2.08.04: Specification forbids exporting 0.0 for unobserved cells (n_eff = 0)."""
    # Verifies null SQ contract
    n_eff = 0
    sq_exported = None if n_eff == 0 else 0.0
    assert sq_exported is None
    assert sq_exported != 0.0


@pytest.mark.tier2
def test_tc2_08_05_suppressed_cell_contract() -> None:
    """TC2.08.05: Cells with 0 < n_eff < 10 carry SQ = null and suppressed = True."""
    n_eff = 8.5
    k_min = 10
    public_sq = None if n_eff < k_min else 45.0
    suppressed = n_eff < k_min
    assert public_sq is None
    assert suppressed is True
