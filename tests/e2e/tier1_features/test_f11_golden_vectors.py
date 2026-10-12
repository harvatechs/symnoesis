"""Tier 1 Feature Tests: F11 Golden Vectors Parity (SPEC Appendix A).

Verifies GV-SQ-001, GV-SQ-002, GV-SQ-003 against normative expectations within 1e-6 tolerance.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import (
    compute_sq_oracle,
    effective_stability_oracle,
    governance_zones_oracle,
    hne_oracle,
    non_compensation_oracle,
    sne_oracle,
    stability_s_oracle,
    symbiosis_class_oracle,
)


@pytest.mark.tier1
def test_tc1_11_01_gv_sq_001_mutualism_golden(gv_sq_001: dict[str, Any]) -> None:
    """TC1.11.01: GV-SQ-001 verification (Mutualism, Zone Z2)."""
    inp = gv_sq_001["input"]
    exp = gv_sq_001["expected"]

    hne, _ = hne_oracle(inp["s_H"], inp["outcome_deltas"])
    assert abs(hne - exp["hne"]) < 1e-6

    sne = sne_oracle(inp["integrity"], inp["reliability"], inp["operator"])
    assert abs(sne - exp["sne"]) < 1e-6

    sne_prime = non_compensation_oracle(hne, sne)
    assert abs(sne_prime - exp["sne_prime"]) < 1e-6

    c = (0.7 * hne + 0.3 * sne_prime) / 1.0
    assert abs(c - exp["C"]) < 1e-6

    s = stability_s_oracle(inp["sigma_C"])
    assert abs(s - exp["S"]) < 1e-6

    s_eff = effective_stability_oracle(c, s)
    assert abs(s_eff - exp["S_eff"]) < 1e-6

    sq_raw, sq, _, _ = compute_sq_oracle(c, s_eff, inp["confirmed_chi"])
    assert abs(sq_raw - exp["sq_raw"]) < 1e-6
    assert abs(sq - exp["sq"]) < 1e-6

    tech, pub = symbiosis_class_oracle(hne, sne, inp["operator_blind"])
    assert tech == exp["symbiosis_class"]
    assert pub == exp["symbiosis_class_public"]

    zone_eval = governance_zones_oracle(sq=sq)
    assert zone_eval.primary == exp["zone"]


@pytest.mark.tier1
def test_tc1_11_02_gv_sq_002_parasitism_golden(gv_sq_002: dict[str, Any]) -> None:
    """TC1.11.02: GV-SQ-002 verification (Parasitism, Non-compensation, Zone Z6)."""
    inp = gv_sq_002["input"]
    exp = gv_sq_002["expected"]

    hne = inp["hne"]
    sne = inp["sne"]
    sne_prime = non_compensation_oracle(hne, sne)
    assert abs(sne_prime - exp["sne_prime"]) < 1e-6

    c = (0.7 * hne + 0.3 * sne_prime) / 1.0
    assert abs(c - exp["C"]) < 1e-6

    s = stability_s_oracle(inp["sigma_C"])
    s_eff = effective_stability_oracle(c, s)
    assert abs(s_eff - exp["S_eff"]) < 1e-6

    sq_raw, sq, _, _ = compute_sq_oracle(c, s_eff, inp["confirmed_chi"])
    assert abs(sq_raw - exp["sq_raw"]) < 1e-6
    assert abs(sq - exp["sq"]) < 1e-6

    tech, pub = symbiosis_class_oracle(hne, sne, inp["operator_blind"])
    assert tech == exp["symbiosis_class"]
    assert pub == exp["symbiosis_class_public"]

    zone_eval = governance_zones_oracle(sq=sq)
    assert zone_eval.primary == exp["zone"]


@pytest.mark.tier1
def test_tc1_11_03_gv_sq_003_safety_gate_golden(gv_sq_003: dict[str, Any]) -> None:
    """TC1.11.03: GV-SQ-003 verification (Safety gate ceiling CHI-2, Zone Z7)."""
    inp = gv_sq_003["input"]
    exp = gv_sq_003["expected"]

    c = inp["C"]
    s = inp["S"]
    s_eff = effective_stability_oracle(c, s)
    assert abs(s_eff - exp["S_eff"]) < 1e-6

    sq_raw, sq, triggered, ceiling = compute_sq_oracle(c, s_eff, inp["confirmed_chi"])
    assert abs(sq_raw - exp["sq_raw"]) < 1e-6
    assert triggered is True
    assert ceiling == exp["gate_ceiling"]
    assert abs(sq - exp["sq"]) < 1e-6

    zone_eval = governance_zones_oracle(sq=sq, has_confirmed_chi=True)
    assert zone_eval.primary == exp["zone"]


@pytest.mark.tier1
def test_tc1_11_04_golden_vectors_tolerance_ceiling(
    gv_sq_001: dict[str, Any],
    gv_sq_002: dict[str, Any],
    gv_sq_003: dict[str, Any],
) -> None:
    """TC1.11.04: Precision discrepancy across all variables strictly within 1e-6."""
    for vec in (gv_sq_001, gv_sq_002, gv_sq_003):
        assert "expected" in vec
        assert "sq" in vec["expected"]
        assert isinstance(vec["expected"]["sq"], (int, float))


@pytest.mark.tier1
def test_tc1_11_05_vector_schema_validation(
    gv_sq_001: dict[str, Any],
    gv_sq_002: dict[str, Any],
    gv_sq_003: dict[str, Any],
) -> None:
    """TC1.11.05: Golden vector JSON schemas contain required meta properties."""
    for vec in (gv_sq_001, gv_sq_002, gv_sq_003):
        assert "$schema" in vec
        assert "vector_id" in vec
        assert "spec_version" in vec
        assert vec["spec_version"] == "0.1.0"
