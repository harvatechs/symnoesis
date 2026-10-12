"""Safety gate and Critical Harm Indicator (CHI) ceiling enforcement.

Normative implementation of SPEC §7:
  Gate ceilings G ∈ [0.0, 0.25] for confirmed CHI-1..7.
  Gate is a ceiling: SQ = min(SQ_raw, 100 * G).
  Pixel gate status: 'critical' (≥ 1 confirmed), 'watch' (flags unconfirmed), 'safe', 'unknown'.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from symnoesis.config import SymnoesisConfig

GateStatus = Literal["safe", "watch", "critical", "unknown"]


def evaluate_safety_gate(
    confirmed_chis: Sequence[str] | None,
    unconfirmed_flags: Sequence[str] | None,
    n_eff: float,
    config: SymnoesisConfig,
) -> tuple[float | None, GateStatus]:
    """Evaluates safety gate ceiling and pixel status.

    Returns (min_ceiling, status).
    min_ceiling is None if no confirmed CHI triggered the gate.
    """
    n_cell_min = config.layout.n_cell_min

    if confirmed_chis and len(confirmed_chis) > 0:
        ceilings: list[float] = []
        for chi in confirmed_chis:
            if chi in config.sq.gate_ceilings:
                ceilings.append(config.sq.gate_ceilings[chi])
            else:
                raise ValueError(f"Unrecognized CHI indicator: {chi}")
        return min(ceilings), "critical"

    if unconfirmed_flags and len(unconfirmed_flags) > 0:
        return None, "watch"

    if n_eff >= n_cell_min:
        return None, "safe"

    return None, "unknown"
