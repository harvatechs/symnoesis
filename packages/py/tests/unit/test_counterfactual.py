r"""Unit tests for Counterfactual Repair Diagnostics and Ridge Projection Engine.

Tests normative requirements of SPEC §10, §12:
- Single-flip repair: c \oplus v for v in {H1..H4, M1..M4} with bit_v(c) == 0
- Sourcing rules: observed (n_eff >= 10) vs modeled (ridge fallback)
- Dominant failure variable identification: argmax_v Delta SQ_v
- Associational framing invariant (prohibition of causal vocabulary)
- Ridge additive model parameterization (37 features)
- Continuous L1/L2 repair projection to Mutualism (SQ > 20, HNE > 0.2, SNE > 0.2)
"""

from __future__ import annotations

import numpy as np
import pytest

from symnoesis.config import SymnoesisConfig
from symnoesis.counterfactual import (
    PROHIBITED_CAUSAL_TERMS,
    ContinuousState,
    RidgeBitModel,
    compute_counterfactual_repair,
    compute_single_flip_diagnostics,
    fit_ridge_additive_model,
)
from symnoesis.cover import CellInput, bits_to_vertex


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_single_flip_delta_sq_calculation(config: SymnoesisConfig) -> None:
    """TC1.18.01: Delta SQ_v = SQ(c flip v) - SQ(c) identifies potential gain."""
    # Current cell at h0000-m0000 (vertex 0)
    current_sq = -30.0
    cells: dict[int, CellInput] = {
        0: CellInput(cell_id=0, sq=current_sq, n_eff=50.0, observed=True)
    }

    # Neighbor flipping H1 (bit 0): vertex 128 (h1000-m0000)
    neighbor_sq = +15.0
    v_h1 = bits_to_vertex([1, 0, 0, 0, 0, 0, 0, 0])
    cells[v_h1] = CellInput(cell_id=v_h1, sq=neighbor_sq, n_eff=25.0, observed=True)

    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    assert result.current_sq == current_sq
    assert "H1" in result.flips
    h1_diag = result.flips["H1"]
    assert h1_diag.delta_sq == neighbor_sq - current_sq
    assert h1_diag.delta_sq == +45.0
    assert h1_diag.source == "observed"


def test_observed_sourcing_priority(config: SymnoesisConfig) -> None:
    """TC1.18.02: Neighbor with n_eff >= 10 uses observed value with source='observed'."""
    v_h2 = bits_to_vertex([0, 1, 0, 0, 0, 0, 0, 0])
    cells = {
        0: CellInput(cell_id=0, sq=-20.0, n_eff=30.0, observed=True),
        v_h2: CellInput(cell_id=v_h2, sq=10.0, n_eff=15.0, observed=True),
    }
    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    assert result.flips["H2"].source == "observed"


def test_modeled_sourcing_fallback(config: SymnoesisConfig) -> None:
    """TC1.18.03: Neighbor with n_eff < 10 falls back to ridge model with source='modeled'."""
    v_h3 = bits_to_vertex([0, 0, 1, 0, 0, 0, 0, 0])
    cells = {
        0: CellInput(cell_id=0, sq=-20.0, n_eff=30.0, observed=True),
        # Sparse neighbor below n_cell_min
        v_h3: CellInput(cell_id=v_h3, sq=10.0, n_eff=4.0, observed=True),
    }
    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    assert result.flips["H3"].source == "modeled"


def test_dominant_failure_variable_argmax(config: SymnoesisConfig) -> None:
    """TC1.18.04: Dominant failure variable is argmax_v Delta SQ_v."""
    v_h1 = bits_to_vertex([1, 0, 0, 0, 0, 0, 0, 0])
    v_h3 = bits_to_vertex([0, 0, 1, 0, 0, 0, 0, 0])
    v_m2 = bits_to_vertex([0, 0, 0, 0, 0, 1, 0, 0])

    cells = {
        0: CellInput(cell_id=0, sq=-40.0, n_eff=50.0, observed=True),
        v_h1: CellInput(cell_id=v_h1, sq=-30.0, n_eff=20.0, observed=True),  # Delta = +10
        v_h3: CellInput(cell_id=v_h3, sq=-15.0, n_eff=20.0, observed=True),  # Delta = +25
        v_m2: CellInput(cell_id=v_m2, sq=-22.0, n_eff=20.0, observed=True),  # Delta = +18
    }

    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    assert result.dominant_variable == "H3"
    assert result.max_delta_sq == 25.0


def test_counterfactual_all_zero_or_negative_deltas(config: SymnoesisConfig) -> None:
    """TC2.18.01: When all repair flips have non-positive delta, no improvement is indicated."""
    # Neighbors all worse than current cell
    v_h1 = bits_to_vertex([1, 0, 0, 0, 0, 0, 0, 0])
    cells = {
        0: CellInput(cell_id=0, sq=40.0, n_eff=50.0, observed=True),
        v_h1: CellInput(cell_id=v_h1, sq=35.0, n_eff=20.0, observed=True),  # Delta = -5
    }
    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    # Flips that are <= 0 do not produce a dominant variable
    assert result.dominant_variable is None
    assert result.max_delta_sq <= 0.0


def test_associational_framing_invariant(config: SymnoesisConfig) -> None:
    """TC1.18.05: Diagnostic reports use strictly associational, non-causal phrasing."""
    v_h3 = bits_to_vertex([0, 0, 1, 0, 0, 0, 0, 0])
    cells = {
        0: CellInput(cell_id=0, sq=-30.0, n_eff=50.0, observed=True),
        v_h3: CellInput(cell_id=v_h3, sq=0.0, n_eff=20.0, observed=True),
    }
    result = compute_single_flip_diagnostics("h0000-m0000", cells, config=config)
    phrase = result.diagnostic_text
    assert "association indicates dominant potential improvement" in phrase
    for prohibited in PROHIBITED_CAUSAL_TERMS:
        assert prohibited not in phrase.lower()


def test_ridge_bit_model() -> None:
    """Verifies RidgeBitModel training, prediction, and feature extraction."""
    model = RidgeBitModel(alpha=1.0)
    # Check 37 features
    feat = model._extract_features([1, 0, 1, 0, 1, 0, 1, 0])
    assert len(feat) == 37
    assert feat[0] == 1.0  # intercept

    # Train on synthetic cells
    cells = [
        CellInput(cell_id=i, sq=float(i - 128) * 0.5, n_eff=20.0, observed=True) for i in range(50)
    ]
    model.fit(cells)
    assert model.is_fitted
    pred = model.predict([0, 0, 0, 0, 0, 0, 0, 0])
    assert -100.0 <= pred <= 100.0


def test_continuous_counterfactual_repair_mutualism(config: SymnoesisConfig) -> None:
    """Verifies continuous L1 and L2 repairs transition into Mutualism."""
    # Severely compromised state: low human agency and negative system parameters
    poor_state = ContinuousState(
        s_h=(0.1, 0.1, 0.1, 0.1),
        integrity=-0.5,
        reliability=-0.5,
        operator=-0.5,
        stability_std=0.0,
    )

    # L2 repair
    res_l2 = compute_counterfactual_repair(poor_state, norm="l2", config=config)
    assert not res_l2.is_already_mutualistic
    assert res_l2.repaired_class == "mutualism"
    assert res_l2.repaired_hne > 0.20
    assert res_l2.repaired_sne > 0.20
    assert res_l2.repaired_sq > 20.0
    assert res_l2.distance > 0.0

    # L1 repair
    res_l1 = compute_counterfactual_repair(poor_state, norm="l1", config=config)
    assert not res_l1.is_already_mutualistic
    assert res_l1.repaired_class == "mutualism"
    assert res_l1.repaired_hne > 0.20
    assert res_l1.repaired_sne > 0.20
    assert res_l1.repaired_sq > 20.0


def test_continuous_repair_already_mutualistic(config: SymnoesisConfig) -> None:
    """Verifies that an already mutualistic state produces zero adjustments."""
    good_state = ContinuousState(
        s_h=(0.9, 0.9, 0.9, 0.9),
        integrity=0.8,
        reliability=0.8,
        operator=0.8,
        stability_std=0.0,
    )
    res = compute_counterfactual_repair(good_state, norm="l2", config=config)
    assert res.is_already_mutualistic
    assert res.distance == 0.0
    assert all(d == 0.0 for d in res.deltas.values())


def test_counterfactual_edge_cases(config: SymnoesisConfig) -> None:
    """Verifies edge cases for ridge model and diagnostics."""
    unfitted = RidgeBitModel(alpha=1.0)
    assert unfitted.predict([0] * 8) == 0.0

    with pytest.raises(ValueError):
        unfitted._extract_features([0, 1])

    empty_model = RidgeBitModel(alpha=1.0)
    empty_model.fit([])
    assert empty_model.is_fitted
    assert np.all(empty_model.weights == 0.0)

    # Current cell has no observed SQ, uses modeled prediction
    cells = {
        1: CellInput(cell_id=1, sq=20.0, n_eff=15.0, observed=True),
    }
    model = fit_ridge_additive_model(cells, config=config)
    res = compute_single_flip_diagnostics("h0000-m0000", cells, ridge_model=model, config=config)
    assert res.current_sq is not None
