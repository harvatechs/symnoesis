"""Multi-Judge Panel & Calibration Harness (SPEC §16).

Implements:
- Multi-judge panel evaluation
- Inter-judge disagreement rate tracking
- Multi-family requirements (>= 2 distinct judge families)
- Automated calibration harness checking alpha >= 0.75 (calibrated >= 0.80)
  and bootstrap CI lower bound >= 0.667.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from symnoesis.judges.alpha import (
    MeasurementLevel,
    bootstrap_krippendorff_alpha_ci,
    compute_krippendorff_alpha,
)


class Judge(Protocol):
    """Protocol representing an automated or expert rater."""

    @property
    def judge_id(self) -> str: ...

    @property
    def family(self) -> str: ...

    def evaluate(self, item: dict[str, Any]) -> float | int | str: ...


@dataclass(frozen=True)
class DeterministicJudge:
    """Deterministic judge for repeatable evaluation and calibration batteries."""

    judge_id: str
    family: str
    bias: float = 0.0
    mapping: dict[str, float | int | str] = field(default_factory=dict)

    def evaluate(self, item: dict[str, Any]) -> float | int | str:
        item_id = str(item.get("id", ""))
        if item_id in self.mapping:
            return self.mapping[item_id]

        ground_truth = float(item.get("ground_truth", 0.5))
        # Continuous or bucketed rating
        score = max(0.0, min(1.0, ground_truth + self.bias))
        return score


@dataclass(frozen=True)
class CalibrationReport:
    """Structured report produced by the Multi-Judge Calibration Harness."""

    alpha: float
    ci_lower: float
    ci_upper: float
    is_calibrated: bool
    disagreement_rate: float
    level_of_measurement: MeasurementLevel
    n_units: int
    n_raters: int
    judge_families: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class JudgePanel:
    """Multi-judge panel managing multiple raters across distinct families."""

    def __init__(self, judges: list[Judge]) -> None:
        if len(judges) < 3:
            raise ValueError(f"Judge panel requires at least 3 raters, got {len(judges)}")

        distinct_families = {j.family for j in judges}
        if len(distinct_families) < 2:
            raise ValueError(
                f"Judge panel requires at least 2 distinct judge families, got {distinct_families}"
            )

        self.judges = judges
        self.families = sorted(distinct_families)

    def evaluate_item(self, item: dict[str, Any]) -> list[float | int | str]:
        """Collect ratings for a single item across all judges in the panel."""
        return [judge.evaluate(item) for judge in self.judges]

    def compute_disagreement_rate(
        self, ratings_matrix: Sequence[Sequence[float | int | str | None]]
    ) -> float:
        """Compute the pairwise disagreement rate across all evaluated units."""
        disagreements = 0
        total_pairs = 0

        for row in ratings_matrix:
            valid = [r for r in row if r is not None]
            n_valid = len(valid)
            for i in range(n_valid):
                for j in range(i + 1, n_valid):
                    total_pairs += 1
                    if valid[i] != valid[j]:
                        disagreements += 1

        if total_pairs == 0:
            return 0.0
        return float(disagreements) / float(total_pairs)


class CalibrationHarness:
    """Harness to calibrate and certify judge panels against held-out datasets."""

    def __init__(
        self,
        alpha_min: float = 0.75,
        alpha_ci_lower_min: float = 0.667,
        alpha_calibrated_target: float = 0.80,
    ) -> None:
        self.alpha_min = alpha_min
        self.alpha_ci_lower_min = alpha_ci_lower_min
        self.alpha_calibrated_target = alpha_calibrated_target

    def calibrate(
        self,
        panel: JudgePanel,
        dataset: list[dict[str, Any]],
        level: MeasurementLevel = "nominal",
        bootstrap_replicates: int = 1000,
        seed: int | None = 42,
    ) -> CalibrationReport:
        """Run calibration over a dataset and evaluate Krippendorff's alpha and bootstrap CI.

        Args:
            panel: JudgePanel under test.
            dataset: List of items to evaluate.
            level: Level of measurement ('nominal', 'ordinal', 'interval').
            bootstrap_replicates: Bootstrap iterations for CI.
            seed: Random seed for reproducibility.

        Returns:
            CalibrationReport with alpha, CI bounds, and pass/fail certification.
        """
        if len(dataset) < 2:
            raise ValueError(f"Calibration dataset requires at least 2 items, got {len(dataset)}")

        # Collect ratings matrix (units x judges)
        ratings_matrix: list[list[float | int | str | None]] = []
        for item in dataset:
            row: list[float | int | str | None] = []
            for judge in panel.judges:
                rating = judge.evaluate(item)
                row.append(rating)
            ratings_matrix.append(row)

        alpha = compute_krippendorff_alpha(ratings_matrix, level=level)
        ci_lower, ci_upper = bootstrap_krippendorff_alpha_ci(
            ratings_matrix,
            level=level,
            replicates=bootstrap_replicates,
            confidence=0.95,
            seed=seed,
        )

        disagreement_rate = panel.compute_disagreement_rate(ratings_matrix)

        # Normative criteria: alpha >= alpha_min and ci_lower >= alpha_ci_lower_min
        # Calibrated panel criteria: alpha >= alpha_calibrated_target (0.80)
        is_calibrated = (
            alpha >= self.alpha_calibrated_target and ci_lower >= self.alpha_ci_lower_min
        )

        return CalibrationReport(
            alpha=alpha,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            is_calibrated=is_calibrated,
            disagreement_rate=disagreement_rate,
            level_of_measurement=level,
            n_units=len(dataset),
            n_raters=len(panel.judges),
            judge_families=panel.families,
            metadata={"judge_disagreement_rate": disagreement_rate},
        )
