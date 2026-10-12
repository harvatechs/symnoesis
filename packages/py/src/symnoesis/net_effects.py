"""Human and System Net Effect calculus (HNE, SNE) and composite net effect C.

Normative implementation of SPEC §5 and §6:
  HNE_state = Σ a_i * (2*s_i - 1)
  HNE_outcome = mean(tanh(d_k / d0))
  HNE = (1 - λ)*HNE_state + λ*HNE_outcome
  SNE = 0.4*Integrity + 0.4*Reliability + 0.2*Operator
  SNE' = min(SNE, 0) if HNE < 0 else SNE (Non-compensation rule)
  C = (w_h*HNE + w_s*SNE') / (w_h + w_s)
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from symnoesis.config import SymnoesisConfig


def compute_hne(
    s_h: Sequence[float],
    outcome_deltas: Sequence[float] | None,
    config: SymnoesisConfig,
) -> tuple[float, bool]:
    """Computes HNE and outcome_available flag.

    s_h: 4 scores for H1..H4 in [0, 1].
    outcome_deltas: optional sequence of standardized changes d_k.
    """
    if len(s_h) != 4:
        raise ValueError(f"s_h must contain exactly 4 scores, got {len(s_h)}")

    weights = config.net_effects.hne.state_weights
    hne_state = sum(w * (2.0 * s - 1.0) for w, s in zip(weights, s_h, strict=True))

    if not outcome_deltas:
        return hne_state, False

    d0 = config.net_effects.hne.outcome_scale
    transformed_deltas = [math.tanh(d / d0) for d in outcome_deltas]
    hne_outcome = sum(transformed_deltas) / len(transformed_deltas)

    lambda_blend = config.net_effects.hne.outcome_blend
    hne = (1.0 - lambda_blend) * hne_state + lambda_blend * hne_outcome
    return hne, True


def compute_sne(
    integrity: float,
    reliability: float,
    operator: float | None,
    config: SymnoesisConfig,
) -> tuple[float, bool]:
    """Computes SNE and operator_blind flag.

    If operator proxy data is missing (operator is None), operator is set to 0.0
    and operator_blind is True.
    """
    if operator is None:
        eff_operator = 0.0
        operator_blind = True
    else:
        eff_operator = float(operator)
        operator_blind = False

    w_int = config.net_effects.sne.integrity
    w_rel = config.net_effects.sne.reliability
    w_op = config.net_effects.sne.operator

    sne = w_int * integrity + w_rel * reliability + w_op * eff_operator
    return sne, operator_blind


def apply_non_compensation(hne: float, sne: float, config: SymnoesisConfig) -> float:
    """Applies non-compensation rule: SNE' = min(SNE, 0) if HNE < 0 else SNE."""
    if config.sq.non_compensation and hne < 0.0:
        return min(sne, 0.0)
    return sne


def compute_composite_c(hne: float, sne: float, config: SymnoesisConfig) -> tuple[float, float]:
    """Computes composite effect C and effective SNE'.

    Returns (C, sne_prime).
    """
    sne_prime = apply_non_compensation(hne, sne, config)
    w_h = config.sq.weights.human
    w_s = config.sq.weights.system
    c = (w_h * hne + w_s * sne_prime) / (w_h + w_s)
    return c, sne_prime
