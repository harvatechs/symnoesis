"""Tests for golden reference vectors GV-SQ-001, GV-SQ-002, GV-SQ-003.

Checks bit-for-bit and mathematical precision against SPEC Appendix A.
"""

import json
from pathlib import Path

import pytest

from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.gates import evaluate_safety_gate
from symnoesis.net_effects import compute_composite_c, compute_hne, compute_sne
from symnoesis.sq import compute_sq
from symnoesis.stability import compute_stability_factor
from symnoesis.zones import evaluate_zones


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_gv_sq_001_mutualism(config: SymnoesisConfig) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    with open(repo_root / "spec" / "vectors" / "gv-sq-001.json", encoding="utf-8") as f:
        gv = json.load(f)

    inp = gv["input"]
    exp = gv["expected"]

    hne, outcome_avail = compute_hne(inp["s_H"], inp["outcome_deltas"], config)
    assert hne == pytest.approx(exp["hne"], abs=1e-6)
    assert not outcome_avail

    sne, op_blind = compute_sne(inp["integrity"], inp["reliability"], inp["operator"], config)
    assert sne == pytest.approx(exp["sne"], abs=1e-6)
    assert not op_blind

    c, sne_prime = compute_composite_c(hne, sne, config)
    assert sne_prime == pytest.approx(exp["sne_prime"], abs=1e-6)
    assert c == pytest.approx(exp["C"], abs=1e-6)

    s = compute_stability_factor(inp["sigma_C"], config)
    assert s == pytest.approx(exp["S"], abs=1e-6)

    gate_ceiling, _ = evaluate_safety_gate(inp["confirmed_chi"], None, 50.0, config)
    sq, sq_raw, triggered = compute_sq(c, s, gate_ceiling, config)
    assert sq_raw == pytest.approx(exp["sq_raw"], abs=1e-6)
    assert sq == pytest.approx(exp["sq"], abs=1e-6)
    assert not triggered

    sym_class = classify_symbiosis(hne, sne, inp["operator_blind"], config)
    assert sym_class.technical_name == exp["symbiosis_class"]
    assert sym_class.public_label == exp["symbiosis_class_public"]

    zone_res = evaluate_zones(sq, None, None, False, False, config)
    assert zone_res.primary == exp["zone"]


def test_gv_sq_002_parasitism_non_compensation(config: SymnoesisConfig) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    with open(repo_root / "spec" / "vectors" / "gv-sq-002.json", encoding="utf-8") as f:
        gv = json.load(f)

    inp = gv["input"]
    exp = gv["expected"]

    hne = inp["hne"]
    sne = inp["sne"]

    c, sne_prime = compute_composite_c(hne, sne, config)
    assert sne_prime == pytest.approx(exp["sne_prime"], abs=1e-6)
    assert c == pytest.approx(exp["C"], abs=1e-6)

    s = compute_stability_factor(inp["sigma_C"], config)
    sq, sq_raw, _ = compute_sq(c, s, None, config)
    assert sq_raw == pytest.approx(exp["sq_raw"], abs=1e-6)
    assert sq == pytest.approx(exp["sq"], abs=1e-6)

    sym_class = classify_symbiosis(hne, sne, inp["operator_blind"], config)
    assert sym_class.technical_name == exp["symbiosis_class"]
    assert sym_class.public_label == exp["symbiosis_class_public"]

    zone_res = evaluate_zones(sq, None, None, False, False, config)
    assert zone_res.primary == exp["zone"]


def test_gv_sq_003_safety_gate_ceiling(config: SymnoesisConfig) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    with open(repo_root / "spec" / "vectors" / "gv-sq-003.json", encoding="utf-8") as f:
        gv = json.load(f)

    inp = gv["input"]
    exp = gv["expected"]

    c = inp["C"]
    s = inp["S"]
    confirmed = [inp["confirmed_chi"]]

    gate_ceiling, gate_status = evaluate_safety_gate(confirmed, None, 50.0, config)
    assert gate_status == "critical"
    assert gate_ceiling == pytest.approx(exp["gate_ceiling"], abs=1e-6)

    sq, sq_raw, triggered = compute_sq(c, s, gate_ceiling, config)
    assert sq_raw == pytest.approx(exp["sq_raw"], abs=1e-6)
    assert triggered == exp["gate_triggered"]
    assert sq == pytest.approx(exp["sq"], abs=1e-6)

    zone_res = evaluate_zones(sq, None, None, True, False, config)
    assert zone_res.primary == exp["zone"]
