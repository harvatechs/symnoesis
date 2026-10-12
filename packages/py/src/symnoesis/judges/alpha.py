"""Krippendorff's Alpha Reliability Metric (SPEC §16).

Implements exact calculation of Krippendorff's alpha for:
- Nominal metric
- Ordinal metric
- Interval metric

Handles arbitrary number of raters, missing observations, and bootstrap CI estimation.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Literal

MeasurementLevel = Literal["nominal", "ordinal", "interval"]


def compute_krippendorff_alpha(
    matrix: Sequence[Sequence[float | int | str | None]],
    level: MeasurementLevel = "nominal",
) -> float:
    """Compute exact Krippendorff's alpha reliability coefficient.

    Args:
        matrix: Reliability matrix where rows represent units (items)
            and columns represent raters (coders). Missing entries are None.
        level: Level of measurement ('nominal', 'ordinal', 'interval').

    Returns:
        Alpha coefficient in [-inf, 1.0], where 1.0 indicates perfect agreement.

    Raises:
        ValueError: If fewer than 2 units exist or level is unsupported.
    """
    if len(matrix) < 2:
        raise ValueError(f"At least 2 units are required to compute alpha, got {len(matrix)}")

    # 1. Filter units with at least 2 non-None ratings
    pairable_units: list[list[float | int | str]] = []
    for row in matrix:
        valid_ratings = [val for val in row if val is not None]
        if len(valid_ratings) >= 2:
            pairable_units.append(valid_ratings)

    if not pairable_units:
        # No units have >= 2 ratings
        return 1.0

    # 2. Extract unique categories/values across all pairable units
    unique_vals: list[float | int | str] = []
    seen: set[float | int | str] = set()
    for row in pairable_units:
        for val in row:
            if val not in seen:
                seen.add(val)
                unique_vals.append(val)

    # For ordinal and interval metrics, sort categories
    if level in ("ordinal", "interval"):
        try:
            # Ensure sorting numerically
            unique_vals.sort(key=lambda x: float(x))
        except (ValueError, TypeError):
            unique_vals.sort(key=str)

    # If only 1 unique value across the entire matrix, perfect agreement
    if len(unique_vals) <= 1:
        return 1.0

    val_to_idx = {val: idx for idx, val in enumerate(unique_vals)}
    num_vals = len(unique_vals)

    # 3. Calculate total pairable ratings n and marginal counts n_c
    # n_c: total count of value c across all pairable units
    marginal_counts = [0] * num_vals
    total_ratings_n = 0

    for row in pairable_units:
        for val in row:
            idx = val_to_idx[val]
            marginal_counts[idx] += 1
            total_ratings_n += 1

    if total_ratings_n < 2:
        return 1.0

    # 4. Construct coincidence matrix O where O[c][k] is observed coincidence
    coincidence = [[0.0] * num_vals for _ in range(num_vals)]

    for row in pairable_units:
        m_u = len(row)
        # Unit value frequency distribution
        unit_counts = [0] * num_vals
        for val in row:
            unit_counts[val_to_idx[val]] += 1

        denom = float(m_u - 1)
        for c in range(num_vals):
            n_uc = unit_counts[c]
            if n_uc == 0:
                continue
            for k in range(num_vals):
                n_uk = unit_counts[k]
                if n_uk == 0:
                    continue
                if c == k:
                    coincidence[c][k] += (n_uc * (n_uc - 1)) / denom
                else:
                    coincidence[c][k] += (n_uc * n_uk) / denom

    # 5. Define distance function delta(c, k)^2
    def metric_diff_sq(c_idx: int, k_idx: int) -> float:
        if c_idx == k_idx:
            return 0.0

        if level == "nominal":
            return 1.0

        elif level == "interval":
            c_val = float(unique_vals[c_idx])
            k_val = float(unique_vals[k_idx])
            return (c_val - k_val) ** 2

        elif level == "ordinal":
            # Krippendorff ordinal distance formula:
            # delta(c, k)^2 = ( sum_{g=min(c,k)}^{max(c,k)} n_g - (n_c + n_k)/2 )^2
            low, high = min(c_idx, k_idx), max(c_idx, k_idx)
            sub_sum = sum(marginal_counts[g] for g in range(low, high + 1))
            diff = sub_sum - (marginal_counts[low] + marginal_counts[high]) / 2.0
            return diff**2

        else:
            raise ValueError(f"Unsupported measurement level: {level}")

    # 6. Compute observed disagreement D_o and expected disagreement D_e
    d_observed_sum = 0.0
    d_expected_sum = 0.0

    for c in range(num_vals):
        for k in range(num_vals):
            delta_sq = metric_diff_sq(c, k)
            if delta_sq == 0.0:
                continue
            d_observed_sum += coincidence[c][k] * delta_sq
            d_expected_sum += (marginal_counts[c] * marginal_counts[k]) * delta_sq

    d_observed = d_observed_sum / float(total_ratings_n)
    d_expected = d_expected_sum / float(total_ratings_n * (total_ratings_n - 1))

    if d_expected == 0.0:
        return 1.0

    alpha = 1.0 - (d_observed / d_expected)
    return alpha


def bootstrap_krippendorff_alpha_ci(
    matrix: Sequence[Sequence[float | int | str | None]],
    level: MeasurementLevel = "nominal",
    replicates: int = 1000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> tuple[float, float]:
    """Compute percentile bootstrap confidence interval for Krippendorff's alpha.

    Resamples units (rows) with replacement.

    Args:
        matrix: Reliability matrix (units x raters).
        level: Level of measurement.
        replicates: Number of bootstrap iterations (default 1000).
        confidence: Confidence level (default 0.95).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (ci_lower, ci_upper).
    """
    n_units = len(matrix)
    if n_units < 2:
        return (1.0, 1.0)

    rng = random.Random(seed)
    alphas: list[float] = []

    for _ in range(replicates):
        resampled_matrix = [matrix[rng.randrange(n_units)] for _ in range(n_units)]
        alpha_val = compute_krippendorff_alpha(resampled_matrix, level=level)
        if not math.isnan(alpha_val):
            alphas.append(alpha_val)

    if not alphas:
        return (0.0, 1.0)

    alphas.sort()
    alpha_count = len(alphas)
    half_alpha = (1.0 - confidence) / 2.0
    lower_idx = max(0, int(math.floor(half_alpha * alpha_count)))
    upper_idx = min(alpha_count - 1, int(math.ceil((1.0 - half_alpha) * alpha_count) - 1))

    return (alphas[lower_idx], alphas[upper_idx])
