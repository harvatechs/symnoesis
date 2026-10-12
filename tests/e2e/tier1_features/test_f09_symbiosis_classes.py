"""Tier 1 Feature Tests: F09 Symbiosis Classification (SPEC §8).

Verifies the 9 ecological classes, 3-state sign operator, and operator-blind fallback rule.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.e2e.oracle import symbiosis_class_oracle

try:
    import symnoesis.classes as py_classes
except ImportError:
    py_classes = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_09_01_mutualism_class(symn_config: Any) -> None:
    """TC1.09.01: HNE > 0.2 (+), SNE > 0.2 (+) produces Mutualism / Mutual benefit."""
    tech, pub = symbiosis_class_oracle(hne=0.25, sne=0.48)
    assert tech == "mutualism"
    assert pub == "Mutual benefit"
    if py_classes is not None and symn_config is not None:
        c = py_classes.classify_symbiosis(0.25, 0.48, operator_blind=False, config=symn_config)
        assert c.technical_name == "mutualism"
        assert c.public_label == "Mutual benefit"


@pytest.mark.tier1
def test_tc1_09_02_commensalism_class(symn_config: Any) -> None:
    """TC1.09.02: HNE > 0.2 (+), -0.2 <= SNE <= 0.2 (0) produces Commensalism."""
    tech, pub = symbiosis_class_oracle(hne=0.35, sne=0.05)
    assert tech == "commensalism"
    assert pub == "Human benefits"
    if py_classes is not None and symn_config is not None:
        c = py_classes.classify_symbiosis(0.35, 0.05, operator_blind=False, config=symn_config)
        assert c.technical_name == "commensalism"
        assert c.public_label == "Human benefits"


@pytest.mark.tier1
def test_tc1_09_03_parasitism_class(symn_config: Any) -> None:
    """TC1.09.03: HNE < -0.2 (-), SNE > 0.2 (+) produces Parasitism when operator_blind is False."""
    tech, pub = symbiosis_class_oracle(hne=-0.40, sne=0.50, operator_blind=False)
    assert tech == "parasitism"
    assert pub == "Human harmed at system gain"
    if py_classes is not None and symn_config is not None:
        c = py_classes.classify_symbiosis(-0.40, 0.50, operator_blind=False, config=symn_config)
        assert c.technical_name == "parasitism"
        assert c.public_label == "Human harmed at system gain"


@pytest.mark.tier1
def test_tc1_09_04_amensalism_fallback_under_operator_blind(symn_config: Any) -> None:
    """TC1.09.04: Under operator_blind=True, Parasitism (-, +) falls back to Amensalism."""
    tech, pub = symbiosis_class_oracle(hne=-0.40, sne=0.50, operator_blind=True)
    assert tech == "amensalism"
    assert pub == "Human harmed"
    if py_classes is not None and symn_config is not None:
        c = py_classes.classify_symbiosis(-0.40, 0.50, operator_blind=True, config=symn_config)
        assert c.technical_name == "amensalism"
        assert c.public_label == "Human harmed"
        assert c.operator_blind_applied is True


@pytest.mark.tier1
def test_tc1_09_05_mutual_harm_class(symn_config: Any) -> None:
    """TC1.09.05: HNE < -0.2 (-), SNE < -0.2 (-) produces Mutual harm / Both harmed."""
    tech, pub = symbiosis_class_oracle(hne=-0.50, sne=-0.30)
    assert tech == "mutual_harm"
    assert pub == "Both harmed"
    if py_classes is not None and symn_config is not None:
        c = py_classes.classify_symbiosis(-0.50, -0.30, operator_blind=False, config=symn_config)
        assert c.technical_name == "mutual_harm"
        assert c.public_label == "Both harmed"
