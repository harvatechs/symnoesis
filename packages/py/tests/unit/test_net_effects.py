"""Tests for net effects, non-compensation, and parasitism suppression."""

import pytest

from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.net_effects import (
    apply_non_compensation,
)


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_non_compensation_behavior(config: SymnoesisConfig) -> None:
    # When HNE is negative and SNE is positive: SNE' is clamped to 0
    sne_prime = apply_non_compensation(-0.3, 0.8, config)
    assert sne_prime == 0.0

    # When HNE is positive: SNE is unconstrained
    sne_prime_pos = apply_non_compensation(0.3, 0.8, config)
    assert sne_prime_pos == 0.8


def test_operator_blind_parasitism_fallback(config: SymnoesisConfig) -> None:
    # Under standard conditions: HNE negative, SNE positive -> Parasitism
    cls_standard = classify_symbiosis(-0.4, 0.5, operator_blind=False, config=config)
    assert cls_standard.technical_name == "parasitism"
    assert not cls_standard.operator_blind_applied

    # Under operator_blind: true -> MUST NOT assert Parasitism; falls back to Amensalism
    cls_blind = classify_symbiosis(-0.4, 0.5, operator_blind=True, config=config)
    assert cls_blind.technical_name == "amensalism"
    assert cls_blind.public_label == "Human harmed"
    assert cls_blind.operator_blind_applied


def test_all_symbiosis_classes(config: SymnoesisConfig) -> None:
    # Test all 9 combinations
    coords = [
        (0.5, 0.5, "mutualism"),
        (0.5, 0.0, "commensalism"),
        (0.5, -0.5, "sacrificial"),
        (0.0, 0.5, "inverse_commensalism"),
        (0.0, 0.0, "neutralism"),
        (0.0, -0.5, "antagonism"),
        (-0.5, 0.5, "parasitism"),
        (-0.5, 0.0, "amensalism"),
        (-0.5, -0.5, "mutual_harm"),
    ]
    for h, s, expected in coords:
        res = classify_symbiosis(h, s, operator_blind=False, config=config)
        assert res.technical_name == expected
