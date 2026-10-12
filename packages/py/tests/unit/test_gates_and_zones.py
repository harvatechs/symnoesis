"""Tests for safety gates and governance zones."""

import pytest

from symnoesis.config import SymnoesisConfig
from symnoesis.gates import evaluate_safety_gate
from symnoesis.zones import evaluate_zones


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_safety_gate_ceilings(config: SymnoesisConfig) -> None:
    # CHI-1 has ceiling 0.0
    c1, status1 = evaluate_safety_gate(["CHI-1"], None, 20.0, config)
    assert status1 == "critical"
    assert c1 == 0.0

    # CHI-4 has ceiling 0.25
    c4, status4 = evaluate_safety_gate(["CHI-4"], None, 20.0, config)
    assert status4 == "critical"
    assert c4 == 0.25

    # Multiple CHIs choose minimum ceiling
    c_multi, status_multi = evaluate_safety_gate(["CHI-4", "CHI-2"], None, 20.0, config)
    assert status_multi == "critical"
    assert c_multi == 0.0

    # Watch status for unconfirmed
    _, status_watch = evaluate_safety_gate(None, ["CHI-1"], 20.0, config)
    assert status_watch == "watch"

    # Safe status
    _, status_safe = evaluate_safety_gate(None, None, 20.0, config)
    assert status_safe == "safe"

    # Unknown status when n_eff < n_cell_min (10.0)
    _, status_unk = evaluate_safety_gate(None, None, 5.0, config)
    assert status_unk == "unknown"


def test_zones_precedence(config: SymnoesisConfig) -> None:
    # Z7 Critical overrides high SQ
    res7 = evaluate_zones(75.0, [1, 1, 1, 1], [1, 1, 1, 1], True, False, config)
    assert res7.primary == "Z7"
    assert "Z1" in res7.secondary_tags

    # Z6 Harm (SQ <= -25)
    res6 = evaluate_zones(-26.0, [1, 1, 1, 1], [1, 1, 1, 1], False, False, config)
    assert res6.primary == "Z6"

    # Z5 Dependence: (H1=0 or H4=0) and M2=0
    res5 = evaluate_zones(10.0, [0, 1, 1, 1], [1, 0, 1, 1], False, False, config)
    assert res5.primary == "Z5"
    assert "Z3" in res5.secondary_tags

    # Z4 Drift (negative trajectory)
    res4 = evaluate_zones(65.0, [1, 1, 1, 1], [1, 1, 1, 1], False, True, config)
    assert res4.primary == "Z4"
    # Z1 requires trajectory not negative, so Z1 is not secondary

    # Z1 Symbiotic (SQ >= 60)
    res1 = evaluate_zones(65.0, [1, 1, 1, 1], [1, 1, 1, 1], False, False, config)
    assert res1.primary == "Z1"

    # Z2 Productive (25 <= SQ < 60)
    res2 = evaluate_zones(30.0, [1, 1, 1, 1], [1, 1, 1, 1], False, False, config)
    assert res2.primary == "Z2"

    # Z3 Neutral (-25 < SQ < 25)
    res3 = evaluate_zones(5.0, [1, 1, 1, 1], [1, 1, 1, 1], False, False, config)
    assert res3.primary == "Z3"
