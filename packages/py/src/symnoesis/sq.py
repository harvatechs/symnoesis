"""Symnoesis Quotient (SQ) composite calculation and bootstrap CI.

Normative implementation of SPEC §6:
  SQ_raw = 100 * C * S_eff
  SQ = min(SQ_raw, 100 * G) if gate triggered else SQ_raw
  SQ = clip(SQ, -100, +100)
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from symnoesis.config import SymnoesisConfig
from symnoesis.stability import compute_effective_stability


def compute_sq(
    c: float,
    s: float,
    gate_ceiling: float | None,
    config: SymnoesisConfig,
) -> tuple[float, float, bool]:
    """Computes SQ from composite C, stability S, and optional gate ceiling G.

    Returns (sq_clipped, sq_raw, gate_triggered).
    """
    s_eff = compute_effective_stability(c, s)
    sq_raw = 100.0 * c * s_eff

    gate_triggered = gate_ceiling is not None
    if gate_ceiling is not None:
        if config.sq.gate_mode == "ceiling":
            sq_val = min(sq_raw, 100.0 * float(gate_ceiling))
        else:
            sq_val = sq_raw * float(gate_ceiling)
    else:
        sq_val = sq_raw

    sq_clipped = max(-100.0, min(100.0, sq_val))
    return sq_clipped, sq_raw, gate_triggered


def bootstrap_dyad_sq_ci(
    dyad_sq_values: Sequence[float],
    config: SymnoesisConfig,
    seed: int = 42,
) -> tuple[float, float]:
    """Computes cluster bootstrap 95% percentile confidence interval over dyads.

    Returns (ci_lower, ci_upper).
    """
    arr = np.asarray(dyad_sq_values, dtype=float)
    n = len(arr)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(arr[0]), float(arr[0])

    rng = np.random.default_rng(seed)
    reps = config.sq.bootstrap.replicates
    ci_level = config.sq.bootstrap.ci

    # Resample dyads with replacement
    indices = rng.integers(0, n, size=(reps, n))
    resampled_means = np.mean(arr[indices], axis=1)

    alpha = 1.0 - ci_level
    lower_pct = 100.0 * (alpha / 2.0)
    upper_pct = 100.0 * (1.0 - alpha / 2.0)

    ci_lower = float(np.percentile(resampled_means, lower_pct))
    ci_upper = float(np.percentile(resampled_means, upper_pct))
    return ci_lower, ci_upper
