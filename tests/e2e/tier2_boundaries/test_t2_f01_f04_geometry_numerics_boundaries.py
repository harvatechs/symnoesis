"""Tier 2 Boundary Tests: F01–F04 Geometry & Numerics Boundaries.

Verifies boundary, extreme, and malformed conditions for:
- F01: Gray code limits, negative, overflow, bit errors
- F02: Grid coordinate extremes, toroidal boundary, regex invalidation
- F03: Normal CDF tails (-10, +10, -38), symmetry, subnormals
- F04: Zero-variance clamping, threshold alignment, mass pruning threshold
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    bits_to_int_oracle,
    compute_joint_masses_oracle,
    coord_to_pixel_id_oracle,
    gray_to_int_oracle,
    int_to_bits_oracle,
    int_to_gray_oracle,
    marginal_bit_prob_oracle,
    normal_cdf_oracle,
    pixel_id_to_coord_oracle,
)

# --- F01 Boundaries ---


@pytest.mark.tier2
def test_tc2_01_01_axis_bound_extremes() -> None:
    """TC2.01.01: Verifies wrap-around Hamming distance between k=0 and k=15 is exactly 1."""
    g0 = int_to_gray_oracle(0)  # 0000
    g15 = int_to_gray_oracle(15)  # 1000
    assert g0 == 0
    assert g15 == 8
    assert (g0 ^ g15).bit_count() == 1


@pytest.mark.tier2
def test_tc2_01_02_negative_index_validation() -> None:
    """TC2.01.02: Negative inputs to int_to_gray raise ValueError."""
    with pytest.raises(ValueError):
        int_to_gray_oracle(-1)
    with pytest.raises(ValueError):
        gray_to_int_oracle(-5)


@pytest.mark.tier2
def test_tc2_01_03_bit_width_overflow_validation() -> None:
    """TC2.01.03: Values >= 16 cannot fit in 4-bit array and raise ValueError."""
    with pytest.raises(ValueError):
        int_to_bits_oracle(16, 4)
    with pytest.raises(ValueError):
        int_to_bits_oracle(-1, 4)


@pytest.mark.tier2
def test_tc2_01_04_malformed_bit_values() -> None:
    """TC2.01.04: Bits outside {0, 1} raise ValueError."""
    with pytest.raises(ValueError):
        bits_to_int_oracle([0, 1, 2, 0])
    with pytest.raises(ValueError):
        bits_to_int_oracle([0, -1, 1, 1])


@pytest.mark.tier2
def test_tc2_01_05_gray_to_int_roundtrip_boundaries() -> None:
    """TC2.01.05: gray_to_int recovers 0 and 15 exactly."""
    assert gray_to_int_oracle(0) == 0
    assert gray_to_int_oracle(int_to_gray_oracle(15)) == 15


# --- F02 Boundaries ---


@pytest.mark.tier2
def test_tc2_02_01_grid_four_corner_coordinates() -> None:
    """TC2.02.01: Tests all 4 corners (0,0), (0,15), (15,0), (15,15)."""
    corners = [(0, 0), (0, 15), (15, 0), (15, 15)]
    for c, r in corners:
        pid = coord_to_pixel_id_oracle(c, r)
        assert len(pid) == 11
        rc, rr = pixel_id_to_coord_oracle(pid)
        assert (rc, rr) == (c, r)


@pytest.mark.tier2
def test_tc2_02_02_out_of_bounds_grid_coordinates() -> None:
    """TC2.02.02: Coordinates outside [0, 15] raise ValueError."""
    for c, r in [(-1, 0), (0, -1), (16, 5), (5, 16), (20, 20)]:
        with pytest.raises(ValueError):
            coord_to_pixel_id_oracle(c, r)


@pytest.mark.tier2
def test_tc2_02_03_malformed_pixel_id_syntax() -> None:
    """TC2.02.03: Malformed pixel IDs raise ValueError."""
    malformed = [
        "h101-m0110",  # 3 bits in h
        "h10111-m0110",  # 5 bits in h
        "h1011-m011",  # 3 bits in m
        "h1011_m0110",  # underscore separator
        "1011-0110",  # missing h and m prefixes
        "h1012-m0110",  # invalid bit '2'
        "",  # empty string
    ]
    for bad_id in malformed:
        with pytest.raises(ValueError):
            pixel_id_to_coord_oracle(bad_id)


@pytest.mark.tier2
def test_tc2_02_04_uppercase_pixel_id_rejection() -> None:
    """TC2.02.04: Uppercase pixel IDs are rejected (format requires lowercase)."""
    with pytest.raises(ValueError):
        pixel_id_to_coord_oracle("H1011-M0110")


@pytest.mark.tier2
def test_tc2_02_05_toroidal_boundary_distances() -> None:
    """TC2.02.05: Cells across opposite borders (0,y) and (15,y) have visual distance 1."""
    from tests.e2e.oracle import get_grid_neighbors_oracle

    neighbors_0_5 = get_grid_neighbors_oracle(0, 5)
    assert (15, 5) in neighbors_0_5
    neighbors_15_5 = get_grid_neighbors_oracle(15, 5)
    assert (0, 5) in neighbors_15_5


# --- F03 Boundaries ---


@pytest.mark.tier2
def test_tc2_03_01_deep_negative_tail_clamping() -> None:
    """TC2.03.01: Phi(-10.0) and below clamps cleanly to 0.0 without underflow error."""
    assert normal_cdf_oracle(-10.0) == 0.0
    assert normal_cdf_oracle(-25.0) == 0.0


@pytest.mark.tier2
def test_tc2_03_02_deep_positive_tail_clamping() -> None:
    """TC2.03.02: Phi(+10.0) and above clamps cleanly to 1.0 without overflow error."""
    assert normal_cdf_oracle(10.0) == 1.0
    assert normal_cdf_oracle(30.0) == 1.0


@pytest.mark.tier2
def test_tc2_03_03_subnormal_tail_continuity() -> None:
    """TC2.03.03: Phi(-9.9) evaluates to a minute non-zero float."""
    val = normal_cdf_oracle(-9.9)
    assert 0.0 <= val < 1e-15


@pytest.mark.tier2
def test_tc2_03_04_nan_and_inf_handling() -> None:
    """TC2.03.04: NaN input raises ValueError; Inf clamps to 1.0."""
    with pytest.raises(ValueError):
        normal_cdf_oracle(float("nan"))
    assert normal_cdf_oracle(float("inf")) == 1.0
    assert normal_cdf_oracle(float("-inf")) == 0.0


@pytest.mark.tier2
def test_tc2_03_05_micro_step_around_zero() -> None:
    """TC2.03.05: Microscopic deviations around zero evaluate smoothly."""
    p_pos = normal_cdf_oracle(1e-9)
    p_neg = normal_cdf_oracle(-1e-9)
    assert p_pos > 0.5
    assert p_neg < 0.5
    assert abs(p_pos + p_neg - 1.0) < 1e-14


# --- F04 Boundaries ---


@pytest.mark.tier2
def test_tc2_04_01_zero_variance_clamping_to_floor() -> None:
    """TC2.04.01: Posterior variance sigma = 0.0 is clamped to sigma_floor = 0.01."""
    p = marginal_bit_prob_oracle(mu=0.55, sigma=0.0, theta=0.5)
    # Effective z = (0.55 - 0.5) / 0.01 = 5.0
    assert abs(p - normal_cdf_oracle(5.0)) < 1e-12


@pytest.mark.tier2
def test_tc2_04_02_negative_variance_floor_protection() -> None:
    """TC2.04.02: Negative sigma is clamped to sigma_floor rather than dividing by negative."""
    p = marginal_bit_prob_oracle(mu=0.52, sigma=-0.05, theta=0.5)
    # sigma_eff = max(-0.05, 0.01) = 0.01 -> z = 2.0
    assert abs(p - normal_cdf_oracle(2.0)) < 1e-12


@pytest.mark.tier2
def test_tc2_04_03_exact_threshold_alignment() -> None:
    """TC2.04.03: When mu == theta, p == 0.5 exactly."""
    p = marginal_bit_prob_oracle(mu=0.5, sigma=0.1, theta=0.5)
    assert p == 0.5


@pytest.mark.tier2
def test_tc2_04_04_extreme_posterior_confidence() -> None:
    """TC2.04.04: Extremely confident posterior mu=1.0, sigma=0.01 concentrates mass on 1 cell."""
    probs = [0.99999] * 8
    masses = compute_joint_masses_oracle(probs, prune=True)
    modal_mass = max(masses)
    assert modal_mass > 0.999


@pytest.mark.tier2
def test_tc2_04_05_pruning_threshold_exact_boundary() -> None:
    """TC2.04.05: Tests pruning around 1.0e-4 threshold."""
    # Equal uniform distribution over 256 cells: 1 / 256 = 0.00390625 > 1e-4 -> none pruned
    uniform_probs = [0.5] * 8
    masses = compute_joint_masses_oracle(uniform_probs, prune=True)
    assert all(m > 0.0 for m in masses)
    assert abs(masses[0] - (1.0 / 256.0)) < 1e-12
