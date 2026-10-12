"""Tests for probabilistic assignment across 256 pixels."""

import pytest

from symnoesis.assign import compute_dyad_window_masses, get_modal_pixel
from symnoesis.config import SymnoesisConfig


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_assignment_masses_sum_to_one(config: SymnoesisConfig) -> None:
    # All marginal probabilities at 0.5
    p_vars = dict.fromkeys(("H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"), 0.5)
    masses = compute_dyad_window_masses(p_vars, config)

    # 1/256 ≈ 0.00390625 which is above prune_mass 1e-4, so all 256 survive
    assert len(masses) == 256
    assert sum(masses.values()) == pytest.approx(1.0, abs=1e-6)
    for m in masses.values():
        assert m == pytest.approx(1.0 / 256.0, abs=1e-6)


def test_modal_pixel_with_sharp_probabilities(config: SymnoesisConfig) -> None:
    # Sharp probabilities favoring h1111-m0000
    p_vars = {
        "H1": 0.99,
        "H2": 0.99,
        "H3": 0.99,
        "H4": 0.99,
        "M1": 0.01,
        "M2": 0.01,
        "M3": 0.01,
        "M4": 0.01,
    }
    masses = compute_dyad_window_masses(p_vars, config)
    modal = get_modal_pixel(masses)
    assert modal == "h1111-m0000"
    assert masses[modal] > 0.9
    assert sum(masses.values()) == pytest.approx(1.0, abs=1e-6)
