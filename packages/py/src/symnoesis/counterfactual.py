r"""Counterfactual repair diagnostics and ridge projection engine.

Normative implementation of SPEC §10, §12:
- Single-flip repair: c \oplus v for v in {H1..H4, M1..M4} where bit_v(c) == 0.
- Delta SQ: Delta SQ_v = SQ(c \oplus v) - SQ(c).
- Sourcing:
  - If neighbor c \oplus v has n_eff >= 10, use observed SQ (source: "observed").
  - If neighbor is unobserved or sparse, estimate via ridge additive model
    with pairwise bit interactions:
      \widehat{SQ}(b) = beta_0 + sum_i beta_i b_i + sum_{i < j} gamma_ij b_i b_j.
- Dominant failure variable: v* = argmax_v Delta SQ_v.
- Associational framing invariant: strictly associational, non-causal phrasing.
- Continuous counterfactual repair: minimal L1/L2 adjustments to transition
  into Mutualism (SQ > 20, HNE > 0.2, SNE > 0.2).
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from scipy.optimize import minimize

from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.cover import VARIABLE_NAMES, CellInput, bits_to_vertex
from symnoesis.grid import parse_pixel_id, pixel_id_from_bits
from symnoesis.net_effects import (
    compute_composite_c,
    compute_hne,
    compute_sne,
)
from symnoesis.sq import compute_sq
from symnoesis.stability import compute_stability_factor

PROHIBITED_CAUSAL_TERMS: tuple[str, ...] = (
    "caused by",
    "cure",
    "causal impact",
    "fixes",
    "remedies",
)


@dataclass(frozen=True)
class FlipDiagnostic:
    """Diagnostic record for a single variable repair flip."""

    variable: str
    flipped_pixel_id: str
    delta_sq: float
    source: Literal["observed", "modeled"]
    target_sq: float


@dataclass(frozen=True)
class CounterfactualDiagnosticResult:
    """Discrete single-flip repair diagnostic result for a grid cell."""

    current_pixel_id: str
    current_sq: float
    flips: dict[str, FlipDiagnostic]
    dominant_variable: str | None
    max_delta_sq: float
    diagnostic_text: str


@dataclass(frozen=True)
class ContinuousState:
    """Continuous assessment score state for human and system variables."""

    s_h: tuple[float, float, float, float]  # [H1, H2, H3, H4] in [0, 1]
    integrity: float  # [-1, 1]
    reliability: float  # [-1, 1]
    operator: float  # [-1, 1]
    stability_std: float = 0.0


@dataclass(frozen=True)
class ContinuousRepairResult:
    """Result of continuous L1/L2 projection into Mutualism."""

    original_state: ContinuousState
    repaired_state: ContinuousState
    deltas: dict[str, float]
    norm: Literal["l1", "l2"]
    distance: float
    is_already_mutualistic: bool
    repaired_hne: float
    repaired_sne: float
    repaired_sq: float
    repaired_class: str


class RidgeBitModel:
    r"""Ridge additive model with main effects and pairwise bit interactions.

    SPEC §12:
      \widehat{SQ}(b) = beta_0 + sum_{i=1}^8 beta_i b_i + sum_{i < j} gamma_ij b_i b_j.
      Total 37 parameters: 1 intercept + 8 main effects + 28 pairwise interactions.
    """

    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = float(alpha)
        self.weights: np.ndarray[Any, np.dtype[np.float64]] = np.zeros(37, dtype=np.float64)
        self.is_fitted: bool = False
        self._interaction_pairs: list[tuple[int, int]] = list(itertools.combinations(range(8), 2))

    def _extract_features(self, bits: Sequence[int]) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Extracts 37 features from 8-bit vector."""
        if len(bits) != 8:
            raise ValueError(f"Expected 8 bits, got {len(bits)}")
        feat = np.zeros(37, dtype=np.float64)
        feat[0] = 1.0  # Intercept
        for i in range(8):
            feat[1 + i] = float(bits[i])
        for idx, (i, j) in enumerate(self._interaction_pairs):
            feat[9 + idx] = float(bits[i] * bits[j])
        return feat

    def fit(
        self,
        cells: Sequence[CellInput] | dict[int, CellInput],
        config: SymnoesisConfig | None = None,
    ) -> RidgeBitModel:
        """Fits ridge regression on observed cells."""
        cfg = config or SymnoesisConfig.load_default()
        cell_iter = cells.values() if isinstance(cells, dict) else cells

        X_rows: list[np.ndarray[Any, np.dtype[np.float64]]] = []
        y_vals: list[float] = []
        w_vals: list[float] = []

        for cell in cell_iter:
            if cell.observed and cell.n_eff >= cfg.layout.n_cell_min and cell.sq is not None:
                X_rows.append(self._extract_features(cell.bits))
                y_vals.append(float(cell.sq))
                w_vals.append(float(np.sqrt(max(1.0, cell.n_eff))))

        if not X_rows:
            self.weights = np.zeros(37, dtype=np.float64)
            self.is_fitted = True
            return self

        X = np.array(X_rows, dtype=np.float64)
        y = np.array(y_vals, dtype=np.float64)
        W = np.diag(w_vals)

        # Normal equations: (X^T W X + alpha * I) beta = X^T W y
        XtW = X.T @ W
        XtWX = XtW @ X
        reg_matrix = XtWX + self.alpha * np.eye(37)
        target_vector = XtW @ y

        self.weights = np.linalg.solve(reg_matrix, target_vector)
        self.is_fitted = True
        return self

    def predict(self, bits: Sequence[int]) -> float:
        """Predicts modeled SQ for the specified 8 bits, clipped to [-100, 100]."""
        if not self.is_fitted:
            return 0.0
        feat = self._extract_features(bits)
        pred = float(np.dot(self.weights, feat))
        return float(np.clip(pred, -100.0, 100.0))


def fit_ridge_additive_model(
    cells: Sequence[CellInput] | dict[int, CellInput],
    alpha: float = 1.0,
    config: SymnoesisConfig | None = None,
) -> RidgeBitModel:
    """Fits and returns a RidgeBitModel on observed cells."""
    model = RidgeBitModel(alpha=alpha)
    model.fit(cells, config=config)
    return model


def compute_single_flip_diagnostics(
    pixel_id: str,
    cells: Sequence[CellInput] | dict[int, CellInput],
    ridge_model: RidgeBitModel | None = None,
    config: SymnoesisConfig | None = None,
) -> CounterfactualDiagnosticResult:
    r"""Computes single-flip counterfactual repair diagnostics for a grid cell.

    SPEC §12:
      For pixel c and each variable v where bit_v(c) == 0:
        Flip: c \oplus v
        Delta SQ_v = SQ(c \oplus v) - SQ(c)
        Neighbor n_eff >= 10 -> source: observed
        Neighbor sparse/unobserved -> source: modeled via ridge
        Dominant failure variable: argmax_v Delta SQ_v.
    """
    cfg = config or SymnoesisConfig.load_default()
    cell_map = cells if isinstance(cells, dict) else {c.vertex_idx: c for c in cells}

    h_bits, m_bits = parse_pixel_id(pixel_id)
    current_bits = h_bits + m_bits
    current_vertex = bits_to_vertex(current_bits)

    current_cell = cell_map.get(current_vertex)
    if current_cell is not None and current_cell.sq is not None:
        current_sq = float(current_cell.sq)
    elif ridge_model is not None and ridge_model.is_fitted:
        current_sq = ridge_model.predict(current_bits)
    else:
        current_sq = 0.0

    # Ensure ridge model is available if needed for sparse neighbors
    active_ridge = ridge_model
    if active_ridge is None or not active_ridge.is_fitted:
        active_ridge = fit_ridge_additive_model(cell_map, config=cfg)

    flips: dict[str, FlipDiagnostic] = {}

    for v_idx, var_name in enumerate(VARIABLE_NAMES):
        if current_bits[v_idx] == 0:
            flipped_bits = list(current_bits)
            flipped_bits[v_idx] = 1
            flipped_vertex = bits_to_vertex(flipped_bits)
            flipped_id = pixel_id_from_bits(flipped_bits[:4], flipped_bits[4:])

            neighbor_cell = cell_map.get(flipped_vertex)
            if (
                neighbor_cell is not None
                and neighbor_cell.observed
                and neighbor_cell.n_eff >= cfg.layout.n_cell_min
                and neighbor_cell.sq is not None
            ):
                target_sq = float(neighbor_cell.sq)
                source: Literal["observed", "modeled"] = "observed"
            else:
                target_sq = active_ridge.predict(flipped_bits)
                source = "modeled"

            delta_sq = target_sq - current_sq
            flips[var_name] = FlipDiagnostic(
                variable=var_name,
                flipped_pixel_id=flipped_id,
                delta_sq=float(delta_sq),
                source=source,
                target_sq=float(target_sq),
            )

    positive_flips = {k: v for k, v in flips.items() if v.delta_sq > 0.0}
    if positive_flips:
        dominant_var = max(
            positive_flips.keys(),
            key=lambda k: (positive_flips[k].delta_sq, -VARIABLE_NAMES.index(k)),
        )
        max_delta = positive_flips[dominant_var].delta_sq
        dom_source = positive_flips[dominant_var].source
        diag_text = (
            f"{dom_source} association indicates dominant potential improvement "
            f"in {dominant_var} (+{max_delta:.1f} SQ points)"
        )
    else:
        dominant_var = None
        max_delta = max((v.delta_sq for v in flips.values()), default=0.0)
        diag_text = (
            "observed association indicates no single-variable repair yields positive improvement"
        )

    for term in PROHIBITED_CAUSAL_TERMS:
        if term in diag_text.lower():
            raise ValueError(f"Prohibited causal term '{term}' found in diagnostic text")

    return CounterfactualDiagnosticResult(
        current_pixel_id=pixel_id,
        current_sq=float(current_sq),
        flips=flips,
        dominant_variable=dominant_var,
        max_delta_sq=float(max_delta),
        diagnostic_text=diag_text,
    )


# --- Continuous Counterfactual Repair ---


def evaluate_continuous_state(
    state: ContinuousState,
    config: SymnoesisConfig,
) -> tuple[float, float, float, float, str]:
    """Evaluates continuous state and returns (hne, sne_effective, c, sq, technical_name)."""
    hne, _ = compute_hne(state.s_h, None, config)
    sne_raw, op_blind = compute_sne(state.integrity, state.reliability, state.operator, config)
    c, sne_eff = compute_composite_c(hne, sne_raw, config)
    s = compute_stability_factor(state.stability_std, config)
    sq_val, _, _ = compute_sq(c, s, None, config)
    class_res = classify_symbiosis(hne, sne_eff, op_blind, config)
    return hne, sne_eff, c, sq_val, class_res.technical_name


def compute_counterfactual_repair(
    state: ContinuousState,
    norm: Literal["l1", "l2"] = "l2",
    config: SymnoesisConfig | None = None,
) -> ContinuousRepairResult:
    """Computes minimal L1 or L2 variable adjustments to transition into Mutualism.

    Mutualism requirement:
      HNE > 0.2 (sign3(HNE) == +)
      SNE > 0.2 (sign3(SNE) == +)
      SQ > 20.0
    """
    cfg = config or SymnoesisConfig.load_default()

    hne_init, sne_init, _, sq_init, tech_class_init = evaluate_continuous_state(state, cfg)

    # Check if already mutualistic
    if (
        hne_init > cfg.classes.threshold
        and sne_init > cfg.classes.threshold
        and sq_init > 20.0
        and tech_class_init == "mutualism"
    ):
        return ContinuousRepairResult(
            original_state=state,
            repaired_state=state,
            deltas={
                "H1": 0.0,
                "H2": 0.0,
                "H3": 0.0,
                "H4": 0.0,
                "Integrity": 0.0,
                "Reliability": 0.0,
                "Operator": 0.0,
            },
            norm=norm,
            distance=0.0,
            is_already_mutualistic=True,
            repaired_hne=float(hne_init),
            repaired_sne=float(sne_init),
            repaired_sq=float(sq_init),
            repaired_class=tech_class_init,
        )

    # Variables x = [h1, h2, h3, h4, integrity, reliability, operator]
    x0 = np.array(
        [
            state.s_h[0],
            state.s_h[1],
            state.s_h[2],
            state.s_h[3],
            state.integrity,
            state.reliability,
            state.operator,
        ],
        dtype=np.float64,
    )

    bounds = [
        (0.0, 1.0),
        (0.0, 1.0),
        (0.0, 1.0),
        (0.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
    ]

    target_thresh = cfg.classes.threshold + 0.005

    if norm == "l2":

        def objective(x: np.ndarray[Any, np.dtype[np.float64]]) -> float:
            return float(np.sum((x - x0) ** 2))

    else:

        def objective(x: np.ndarray[Any, np.dtype[np.float64]]) -> float:
            return float(np.sum(np.abs(x - x0)))

    def hne_constraint(x: np.ndarray[Any, np.dtype[np.float64]]) -> float:
        h_vals = (float(x[0]), float(x[1]), float(x[2]), float(x[3]))
        h_score, _ = compute_hne(h_vals, None, cfg)
        return float(h_score - target_thresh)

    def sne_constraint(x: np.ndarray[Any, np.dtype[np.float64]]) -> float:
        s_score, _ = compute_sne(float(x[4]), float(x[5]), float(x[6]), cfg)
        return float(s_score - target_thresh)

    def sq_constraint(x: np.ndarray[Any, np.dtype[np.float64]]) -> float:
        h_vals = (float(x[0]), float(x[1]), float(x[2]), float(x[3]))
        h_score, _ = compute_hne(h_vals, None, cfg)
        s_score, _ = compute_sne(float(x[4]), float(x[5]), float(x[6]), cfg)
        c, _ = compute_composite_c(h_score, s_score, cfg)
        s = compute_stability_factor(state.stability_std, cfg)
        sq_score, _, _ = compute_sq(c, s, None, cfg)
        return float(sq_score - 20.005)

    constraints = [
        {"type": "ineq", "fun": hne_constraint},
        {"type": "ineq", "fun": sne_constraint},
        {"type": "ineq", "fun": sq_constraint},
    ]

    x_init = np.copy(x0)
    if hne_init < target_thresh:
        x_init[:4] = np.maximum(x_init[:4], 0.7)
    if sne_init < target_thresh:
        x_init[4:7] = np.maximum(x_init[4:7], 0.5)

    res = minimize(
        objective,
        x_init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-9, "maxiter": 200},
    )

    if not res.success:
        x_init[:4] = 0.8
        x_init[4:7] = 0.6
        res = minimize(
            objective,
            x_init,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"ftol": 1e-9, "maxiter": 500},
        )

    x_rep = res.x
    repaired_h = (float(x_rep[0]), float(x_rep[1]), float(x_rep[2]), float(x_rep[3]))
    repaired_state = ContinuousState(
        s_h=repaired_h,
        integrity=float(x_rep[4]),
        reliability=float(x_rep[5]),
        operator=float(x_rep[6]),
        stability_std=state.stability_std,
    )

    rep_hne, rep_sne, _, rep_sq, rep_class = evaluate_continuous_state(repaired_state, cfg)

    deltas = {
        "H1": float(repaired_h[0] - state.s_h[0]),
        "H2": float(repaired_h[1] - state.s_h[1]),
        "H3": float(repaired_h[2] - state.s_h[2]),
        "H4": float(repaired_h[3] - state.s_h[3]),
        "Integrity": float(repaired_state.integrity - state.integrity),
        "Reliability": float(repaired_state.reliability - state.reliability),
        "Operator": float(repaired_state.operator - state.operator),
    }

    if norm == "l2":
        dist = float(np.sqrt(np.sum((x_rep - x0) ** 2)))
    else:
        dist = float(np.sum(np.abs(x_rep - x0)))

    return ContinuousRepairResult(
        original_state=state,
        repaired_state=repaired_state,
        deltas=deltas,
        norm=norm,
        distance=dist,
        is_already_mutualistic=False,
        repaired_hne=float(rep_hne),
        repaired_sne=float(rep_sne),
        repaired_sq=float(rep_sq),
        repaired_class=rep_class,
    )
