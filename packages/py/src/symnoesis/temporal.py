"""Longitudinal temporal engine and trajectory diagnostics.

Normative implementation of SPEC §9, §10:
- Multi-frame observation sequence: days [1, 7, 28, 84, 182].
- Day 1 is a baseline frame (tagged "baseline").
- Change score per interval k: Delta SQ_k = SQ_frame(k) - SQ_frame(k-1).
- Minimum Detectable Change:
    MDC = 1.96 * sqrt(2) * SEM approx 2.77185858 * SEM
    SEM = SD * sqrt(1 - r)
    Placeholder MDC = 5.0 SQ points until r is calibrated.
- Trajectory classification:
    - Negative trajectory (deteriorating): two consecutive intervals with Delta SQ < -MDC.
    - Positive trajectory (improving): two consecutive intervals with Delta SQ > +MDC.
    - Stable trajectory: otherwise.
- Sequence of fewer than 3 frames (< 2 intervals) cannot assert trajectory (returns stable).
- Negative trajectory triggers governance zone Z4 (Drift).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from symnoesis.config import SymnoesisConfig

TrajectoryStatus = Literal["improving", "stable", "deteriorating"]
TrajectoryCode = Literal["positive", "stable", "negative"]


@dataclass(frozen=True)
class TrajectoryResult:
    """Normative result of longitudinal trajectory evaluation."""

    status: TrajectoryStatus
    deltas: list[float]
    is_negative: bool
    is_improving: bool
    is_stable: bool
    mdc: float
    frames_days: list[int]
    scores: list[float]
    status_code: TrajectoryCode

    @property
    def is_baseline(self) -> bool:
        """True if only Day 1 baseline frame is present."""
        return len(self.scores) <= 1 and bool(self.frames_days and self.frames_days[0] == 1)


def compute_sem(sd: float, r: float) -> float:
    """Computes Standard Error of Measurement: SEM = SD * sqrt(1 - r).

    SPEC §10:
      sd: standard deviation of SQ scores.
      r: test-retest reliability coefficient in [0, 1].
    """
    if sd < 0.0:
        raise ValueError(f"Standard deviation must be non-negative, got {sd}")
    if not (0.0 <= r <= 1.0):
        raise ValueError(f"Reliability r must be in [0, 1], got {r}")
    return float(sd * math.sqrt(1.0 - r))


def compute_mdc(
    sem: float | None = None,
    sd: float | None = None,
    r: float | None = None,
    placeholder: float = 5.0,
) -> float:
    """Computes Minimum Detectable Change (MDC).

    SPEC §10:
      MDC = 1.96 * sqrt(2) * SEM = 2.77185858 * SEM.
      If sem or (sd, r) are not provided, returns placeholder (default 5.0).
    """
    if sem is not None:
        if sem < 0.0:
            raise ValueError(f"SEM must be non-negative, got {sem}")
        return float(1.96 * math.sqrt(2.0) * sem)

    if sd is not None and r is not None:
        calculated_sem = compute_sem(sd, r)
        return float(1.96 * math.sqrt(2.0) * calculated_sem)

    return float(placeholder)


def is_baseline_frame(day: int) -> bool:
    """Checks whether the observation day represents the baseline frame (Day 1)."""
    return day == 1


def compute_interval_deltas(scores: Sequence[float]) -> list[float]:
    """Computes consecutive interval deltas: Delta SQ_k = SQ_k - SQ_{k-1}."""
    if len(scores) < 2:
        return []
    return [float(scores[i] - scores[i - 1]) for i in range(1, len(scores))]


def evaluate_trajectory(
    scores: Sequence[float],
    frames: Sequence[int] | None = None,
    mdc: float | None = None,
    config: SymnoesisConfig | None = None,
) -> TrajectoryResult:
    """Evaluates multi-frame trajectory and classifies into improving, stable, or deteriorating.

    SPEC §10:
      - Negative trajectory requires exactly two consecutive intervals with Delta SQ < -MDC.
      - Positive trajectory requires two consecutive intervals with Delta SQ > +MDC.
      - Requires at least 3 frames (2 intervals); fewer than 3 frames returns stable.
    """
    cfg = config or SymnoesisConfig.load_default()
    active_frames = list(frames) if frames is not None else cfg.temporal.frames_days[: len(scores)]
    active_mdc = float(mdc) if mdc is not None else cfg.temporal.mdc_placeholder
    score_list = [float(s) for s in scores]

    deltas = compute_interval_deltas(score_list)

    # Need at least 3 frames (2 intervals) to determine trajectory slope
    if len(score_list) < 3:
        return TrajectoryResult(
            status="stable",
            deltas=deltas,
            is_negative=False,
            is_improving=False,
            is_stable=True,
            mdc=active_mdc,
            frames_days=active_frames,
            scores=score_list,
            status_code="stable",
        )

    # Check for two consecutive intervals exceeding threshold
    consecutive_needed = cfg.temporal.consecutive_intervals

    is_negative = False
    for i in range(len(deltas) - consecutive_needed + 1):
        if all(deltas[i + j] < -active_mdc for j in range(consecutive_needed)):
            is_negative = True
            break

    is_improving = False
    if not is_negative:
        for i in range(len(deltas) - consecutive_needed + 1):
            if all(deltas[i + j] > active_mdc for j in range(consecutive_needed)):
                is_improving = True
                break

    if is_negative:
        status: TrajectoryStatus = "deteriorating"
        status_code: TrajectoryCode = "negative"
    elif is_improving:
        status = "improving"
        status_code = "positive"
    else:
        status = "stable"
        status_code = "stable"

    return TrajectoryResult(
        status=status,
        deltas=deltas,
        is_negative=is_negative,
        is_improving=is_improving,
        is_stable=(not is_negative and not is_improving),
        mdc=active_mdc,
        frames_days=active_frames,
        scores=score_list,
        status_code=status_code,
    )


def is_trajectory_negative(
    scores: Sequence[float],
    mdc: float | None = None,
    config: SymnoesisConfig | None = None,
) -> bool:
    """Convenience predicate for governance zone Z4 evaluation."""
    result = evaluate_trajectory(scores, mdc=mdc, config=config)
    return result.is_negative
