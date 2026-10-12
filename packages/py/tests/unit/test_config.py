"""Tests for SymnoesisConfig loader and schema enforcement."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from symnoesis.config import SymnoesisConfig


def test_load_default_config() -> None:
    cfg = SymnoesisConfig.load_default()
    assert cfg.spec_version == "0.1.0"
    assert "learning" in cfg.domains
    assert cfg.variables.thresholds["H2"] == pytest.approx(0.4207, abs=1e-4)
    assert cfg.sq.weights.human + cfg.sq.weights.system == pytest.approx(1.0, abs=1e-6)
    assert sum(cfg.net_effects.hne.state_weights) == pytest.approx(1.0, abs=1e-6)
    sne_cfg = cfg.net_effects.sne
    assert (sne_cfg.integrity + sne_cfg.reliability + sne_cfg.operator) == pytest.approx(
        1.0, abs=1e-6
    )


def test_rejects_invalid_weights(tmp_path: Path) -> None:
    invalid_yaml = """
spec_version: "0.1.0"
domains: [learning]
variables:
  effect_scale: 0.5
  sigma_floor: 0.01
  thresholds: { H1: 0.5, H2: 0.4207, H3: 0.5, H4: 0.5, M1: 0.5, M2: 0.5, M3: 0.5, M4: 0.5 }
  noninferiority_margin_h2: 0.1
  calibrated: false
assignment: { prune_mass: 1.0e-4 }
layout: { resolution_default: 16, n_cell_min: 10, coverage_80pct_rule: 0.8, coarsening_order: [H4] }
net_effects:
  hne: { state_weights: [0.5, 0.5, 0.5, 0.5], outcome_blend: 0.5, outcome_scale: 0.5 }
  sne: { integrity: 0.4, reliability: 0.4, operator: 0.2 }
sq:
  weights: { human: 0.7, system: 0.3 }
  non_compensation: true
  stability: { sigma_max: 0.5 }
  gate_mode: ceiling
  gate_ceilings: { CHI-1: 0.0 }
  bootstrap: { replicates: 2000, ci: 0.95 }
classes: { threshold: 0.2 }
zones: { z1_min: 60, z2_min: 25, z6_max: -25, precedence: [Z7, Z6, Z5, Z4, Z1, Z2, Z3] }
temporal: { frames_days: [1], consecutive_intervals: 2, mdc_placeholder: 5.0 }
cover:
  harm_threshold: -25
  purity_min: 0.8
  coverage_target: 0.85
  n_rule_min: 30
  max_literals: 5
privacy: { k_min: 10, dp_epsilon: 1.0 }
reliability: { alpha_min: 0.75, alpha_ci_lower_min: 0.667, min_raters: 3, min_judge_families: 2 }
evidence: { min_tier_for_certification: E3 }
"""
    p = tmp_path / "invalid.yaml"
    p.write_text(invalid_yaml, encoding="utf-8")
    with pytest.raises(ValidationError):
        SymnoesisConfig.from_yaml_file(p)
