"""Additional unit tests ensuring >= 95% coverage on core math and edge cases."""

import pytest

from symnoesis.assign import compute_dyad_window_masses, get_modal_pixel
from symnoesis.config import SymnoesisConfig
from symnoesis.evidence import (
    is_eligible_for_certification,
    minimum_evidence_tier,
)
from symnoesis.gates import evaluate_safety_gate
from symnoesis.grid import (
    PixelCoord,
    coord_to_pixel_id,
    parse_pixel_id,
    pixel_coord_to_id,
    pixel_id_from_bits,
    pixel_id_to_coord,
)
from symnoesis.net_effects import compute_hne
from symnoesis.sq import bootstrap_dyad_sq_ci, compute_sq
from symnoesis.stability import (
    compute_effective_stability,
    compute_sample_std,
    compute_stability_factor,
)
from symnoesis.variables import (
    compute_all_marginal_probabilities,
    compute_marginal_probability,
    effect_to_score,
)


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_sq_bootstrap_ci(config: SymnoesisConfig) -> None:
    # Empty sequence
    low, high = bootstrap_dyad_sq_ci([], config, seed=42)
    assert low == 0.0 and high == 0.0

    # Single value
    low_single, high_single = bootstrap_dyad_sq_ci([25.0], config, seed=42)
    assert low_single == 25.0 and high_single == 25.0

    # Multiple values
    vals = [20.0, 25.0, 30.0, 22.0, 28.0]
    ci_l, ci_u = bootstrap_dyad_sq_ci(vals, config, seed=42)
    assert 20.0 <= ci_l <= ci_u <= 30.0


def test_sq_multiplier_mode(config: SymnoesisConfig) -> None:
    # Test multiplier gate mode
    # Create copy with gate_mode="multiplier"
    data = config.model_dump()
    data["sq"]["gate_mode"] = "multiplier"
    mult_config = SymnoesisConfig.model_validate(data)

    sq_clipped, sq_raw, triggered = compute_sq(0.5, 1.0, 0.25, mult_config)
    assert triggered
    assert sq_raw == pytest.approx(50.0)
    assert sq_clipped == pytest.approx(12.5)  # 50 * 0.25


def test_sq_clipping_bounds(config: SymnoesisConfig) -> None:
    # Extreme positive
    sq_clip_pos, _, _ = compute_sq(2.0, 1.0, None, config)
    assert sq_clip_pos == 100.0

    # Extreme negative
    sq_clip_neg, _, _ = compute_sq(-2.0, 1.0, None, config)
    assert sq_clip_neg == -100.0


def test_stability_std_and_effective(config: SymnoesisConfig) -> None:
    # Sample std empty and single
    assert compute_sample_std([]) == 0.0
    assert compute_sample_std([5.0]) == 0.0
    std = compute_sample_std([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert std == pytest.approx(2.138089935)

    # Stability factor clipping when sigma_C > sigma_max
    s_clamped = compute_stability_factor(1.0, config)
    assert s_clamped == pytest.approx(0.5)

    # Harm asymmetry: C < 0 forces S_eff = 1.0
    assert compute_effective_stability(-0.2, 0.6) == 1.0
    assert compute_effective_stability(0.2, 0.6) == 0.6


def test_hne_outcome_and_errors(config: SymnoesisConfig) -> None:
    # With outcome deltas
    hne, outcome_avail = compute_hne([0.6, 0.6, 0.6, 0.6], [0.2, -0.1], config)
    assert outcome_avail
    assert -1.0 <= hne <= 1.0

    # Invalid s_h length
    with pytest.raises(ValueError, match="s_h must contain exactly 4 scores"):
        compute_hne([0.5, 0.5], None, config)


def test_evidence_tiers_and_certification() -> None:
    assert minimum_evidence_tier(["E1", "E3"]) == "E1"
    assert minimum_evidence_tier([]) == "E0"

    # Certification requirements: E3
    assert is_eligible_for_certification("E3")
    assert not is_eligible_for_certification("E2")
    assert not is_eligible_for_certification("E1")
    assert not is_eligible_for_certification("E0")


def test_variables_edge_cases(config: SymnoesisConfig) -> None:
    assert effect_to_score(0.0, config) == pytest.approx(0.5)

    with pytest.raises(ValueError, match="Missing posterior distribution"):
        compute_all_marginal_probabilities({"H1": (0.5, 0.05)}, config)

    # Very small sigma is clamped to sigma_floor (0.01)
    p_clamped = compute_marginal_probability(0.5, 0.0001, "H1", config)
    assert p_clamped == pytest.approx(0.5)


def test_gates_edge_cases(config: SymnoesisConfig) -> None:
    # Unknown CHI code
    with pytest.raises(ValueError, match="Unrecognized CHI indicator"):
        evaluate_safety_gate(["CHI-999"], None, 20.0, config)


def test_assign_edge_cases(config: SymnoesisConfig) -> None:
    # Missing variable in p_vars
    with pytest.raises(ValueError, match="Missing probability for variable"):
        compute_dyad_window_masses({"H1": 0.5}, config)

    # Empty masses in get_modal_pixel
    with pytest.raises(ValueError, match="Cannot find modal pixel of empty"):
        get_modal_pixel({})

    # High prune threshold forcing modal fallback
    data = config.model_dump()
    data["assignment"]["prune_mass"] = 0.999
    high_prune_cfg = SymnoesisConfig.model_validate(data)
    uniform_p = dict.fromkeys(["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"], 0.5)
    res = compute_dyad_window_masses(uniform_p, high_prune_cfg)
    assert len(res) == 1
    assert list(res.values())[0] == 1.0


def test_grid_functions_and_errors() -> None:
    # pixel_coord_to_id with ints and PixelCoord
    pid1 = pixel_coord_to_id(0, 0)
    pid2 = pixel_coord_to_id(PixelCoord(col=0, row=0))
    assert pid1 == pid2 == "h0000-m0000"

    with pytest.raises(ValueError, match="row must be provided"):
        pixel_coord_to_id(0)

    with pytest.raises(ValueError, match="Coordinates out of bounds"):
        coord_to_pixel_id(PixelCoord(col=-1, row=0))

    with pytest.raises(ValueError, match="Invalid pixel ID format"):
        parse_pixel_id("invalid-format")

    with pytest.raises(ValueError, match="H and M bits must both have length 4"):
        pixel_id_from_bits([0, 1], [0, 1])

    coord = pixel_id_to_coord("h1100-m1010")
    assert 0 <= coord.col < 16 and 0 <= coord.row < 16
