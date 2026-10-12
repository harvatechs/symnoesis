"""Unit tests for Multi-Judge Panel & Krippendorff's Alpha (SPEC §16)."""

from __future__ import annotations

from typing import Any

import pytest

from symnoesis.judges.alpha import (
    bootstrap_krippendorff_alpha_ci,
    compute_krippendorff_alpha,
)
from symnoesis.judges.panel import (
    CalibrationHarness,
    DeterministicJudge,
    JudgePanel,
)


@pytest.mark.unit
def test_krippendorff_alpha_perfect_agreement() -> None:
    """Perfect agreement among raters yields alpha = 1.0 across all measurement levels."""
    # 4 units rated by 3 judges
    matrix = [
        ["A", "A", "A"],
        ["B", "B", "B"],
        ["C", "C", "C"],
        ["A", "A", "A"],
    ]

    alpha_nominal = compute_krippendorff_alpha(matrix, level="nominal")
    assert alpha_nominal == 1.0

    # Numeric matrix
    matrix_num = [
        [1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0],
        [4.0, 4.0, 4.0],
    ]
    alpha_ordinal = compute_krippendorff_alpha(matrix_num, level="ordinal")
    assert alpha_ordinal == 1.0

    alpha_interval = compute_krippendorff_alpha(matrix_num, level="interval")
    assert alpha_interval == 1.0


@pytest.mark.unit
def test_krippendorff_alpha_nominal_disagreement() -> None:
    """Evaluates nominal alpha with known disagreement structure."""
    # 2 agreements and 2 disagreements out of 4 items:
    # D_o = 4/8 = 0.5, D_e = 32/56 = 4/7 => alpha = 1 - 0.5 / (4/7) = 1 - 0.875 = 0.125
    matrix = [
        ["A", "A"],
        ["A", "B"],
        ["B", "B"],
        ["B", "A"],
    ]
    alpha = compute_krippendorff_alpha(matrix, level="nominal")
    assert pytest.approx(alpha, abs=1e-6) == 0.125

    # Pure systematic disagreement yields negative alpha
    matrix_pure_disagree = [
        ["A", "B"],
        ["B", "A"],
        ["A", "B"],
        ["B", "A"],
    ]
    alpha_neg = compute_krippendorff_alpha(matrix_pure_disagree, level="nominal")
    assert alpha_neg < 0.0


@pytest.mark.unit
def test_krippendorff_alpha_with_missing_data() -> None:
    """Handles missing observations (None) correctly."""
    matrix: list[list[str | None]] = [
        ["A", "A", None],
        ["B", None, "B"],
        [None, "C", "C"],
        ["A", "A", "A"],
        ["B", None, None],  # < 2 ratings, ignored
    ]

    alpha = compute_krippendorff_alpha(matrix, level="nominal")
    assert alpha == 1.0


@pytest.mark.unit
def test_krippendorff_alpha_ordinal_metric() -> None:
    """Computes ordinal alpha taking distance between ranks into account."""
    matrix = [
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 5],
    ]
    alpha = compute_krippendorff_alpha(matrix, level="ordinal")
    assert 0.0 < alpha < 1.0


@pytest.mark.unit
def test_krippendorff_alpha_interval_metric() -> None:
    """Computes interval alpha using squared differences."""
    matrix = [
        [10.0, 11.0, 10.5],
        [20.0, 19.5, 20.0],
        [30.0, 30.5, 30.0],
        [40.0, 40.0, 41.0],
    ]
    alpha = compute_krippendorff_alpha(matrix, level="interval")
    assert alpha > 0.95


@pytest.mark.unit
def test_krippendorff_alpha_edge_cases() -> None:
    """Tests input validation and degenerate cases."""
    # Fewer than 2 units
    with pytest.raises(ValueError, match="At least 2 units"):
        compute_krippendorff_alpha([["A", "B"]], level="nominal")

    # Unsupported level
    bad_level: Any = "unknown"
    with pytest.raises(ValueError, match="Unsupported measurement level"):
        compute_krippendorff_alpha([["A", "A"], ["B", "B"]], level=bad_level)

    # All identical values across entire dataset
    single_val_matrix = [["A", "A"], ["A", "A"]]
    assert compute_krippendorff_alpha(single_val_matrix, level="nominal") == 1.0


@pytest.mark.unit
def test_bootstrap_krippendorff_alpha_ci() -> None:
    """Bootstrap CI computation returns bounded lower and upper confidence limits."""
    matrix = [
        ["A", "A", "A"],
        ["A", "A", "A"],
        ["B", "B", "B"],
        ["B", "B", "B"],
        ["C", "C", "C"],
    ]
    ci_lower, ci_upper = bootstrap_krippendorff_alpha_ci(
        matrix, level="nominal", replicates=100, seed=42
    )
    assert ci_lower <= ci_upper
    assert ci_lower >= 0.8
    assert ci_upper <= 1.0


@pytest.mark.unit
def test_judge_panel_requirements() -> None:
    """JudgePanel enforces >= 3 raters and >= 2 distinct judge families."""
    j1 = DeterministicJudge("judge-1", "family-a")
    j2 = DeterministicJudge("judge-2", "family-a")
    j3 = DeterministicJudge("judge-3", "family-b")

    # Less than 3 raters
    with pytest.raises(ValueError, match="at least 3 raters"):
        JudgePanel([j1, j2])

    # All from the same family
    j4 = DeterministicJudge("judge-4", "family-a")
    with pytest.raises(ValueError, match="at least 2 distinct judge families"):
        JudgePanel([j1, j2, j4])

    # Valid panel
    panel = JudgePanel([j1, j2, j3])
    assert len(panel.judges) == 3
    assert panel.families == ["family-a", "family-b"]


@pytest.mark.unit
def test_judge_panel_disagreement_rate() -> None:
    """JudgePanel accurately tracks pairwise disagreement rate."""
    j1 = DeterministicJudge("judge-1", "family-a", mapping={"i1": "yes", "i2": "no"})
    j2 = DeterministicJudge("judge-2", "family-a", mapping={"i1": "yes", "i2": "no"})
    j3 = DeterministicJudge("judge-3", "family-b", mapping={"i1": "yes", "i2": "yes"})

    panel = JudgePanel([j1, j2, j3])
    ratings_matrix = [panel.evaluate_item({"id": "i1"}), panel.evaluate_item({"id": "i2"})]

    # i1: ["yes", "yes", "yes"] -> 0 disagreements / 3 pairs
    # i2: ["no", "no", "yes"] -> (no, no)=0, (no, yes)=1, (no, yes)=1 -> 2 disagreements / 3 pairs
    # Total: 2 disagreements / 6 pairs = 1/3 ~ 0.3333

    disagreement_rate = panel.compute_disagreement_rate(ratings_matrix)
    assert pytest.approx(disagreement_rate, abs=1e-4) == 2.0 / 6.0


@pytest.mark.unit
def test_calibration_harness_achieves_threshold() -> None:
    """Calibrated judge panel achieves alpha >= 0.80 and bootstrap CI lower bound >= 0.667."""
    # High-agreement judges across 2 families
    j1 = DeterministicJudge("judge-1", "family-alpha", bias=0.0)
    j2 = DeterministicJudge("judge-2", "family-alpha", bias=0.0)
    j3 = DeterministicJudge("judge-3", "family-beta", bias=0.0)

    panel = JudgePanel([j1, j2, j3])
    harness = CalibrationHarness()

    dataset = [{"id": f"item-{idx}", "ground_truth": round(0.1 * idx, 2)} for idx in range(1, 10)]

    report = harness.calibrate(
        panel=panel,
        dataset=dataset,
        level="interval",
        bootstrap_replicates=200,
        seed=1337,
    )

    assert report.alpha >= 0.80
    assert report.ci_lower >= 0.667
    assert report.is_calibrated is True
    assert report.disagreement_rate == 0.0
    assert "judge_disagreement_rate" in report.metadata


@pytest.mark.unit
def test_krippendorff_alpha_additional_coverage_branches() -> None:
    """Covers edge branches: no pairable units, ordinal string sort, bootstrap degenerate."""
    # Matrix where no units have >= 2 ratings
    matrix_sparse = [["A", None], [None, "B"]]
    assert compute_krippendorff_alpha(matrix_sparse, level="nominal") == 1.0

    # Ordinal with non-numeric string labels
    matrix_ordinal_str = [["low", "medium"], ["medium", "high"]]
    alpha_ord_str = compute_krippendorff_alpha(matrix_ordinal_str, level="ordinal")
    assert isinstance(alpha_ord_str, float)

    # Bootstrap with < 2 units
    assert bootstrap_krippendorff_alpha_ci([["A", "A"]], level="nominal") == (1.0, 1.0)

    # Calibration harness input validation (< 2 items)
    j1 = DeterministicJudge("j1", "f1")
    j2 = DeterministicJudge("j2", "f2")
    j3 = DeterministicJudge("j3", "f2")
    panel = JudgePanel([j1, j2, j3])
    harness = CalibrationHarness()
    with pytest.raises(ValueError, match="requires at least 2 items"):
        harness.calibrate(panel=panel, dataset=[{"id": "single"}])

    # Zero total pairs in disagreement rate
    assert panel.compute_disagreement_rate([[None, None]]) == 0.0
