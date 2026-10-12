"""Tier 1 Feature Tests: F01 Gray Code Bijection (SPEC §4).

Verifies forward bijection, inverse folding, bit array conversion, and Hamming adjacency.
"""

from __future__ import annotations

import pytest
from tests.e2e.oracle import (
    bits_to_int_oracle,
    gray_to_int_oracle,
    int_to_bits_oracle,
    int_to_gray_oracle,
)

try:
    import symnoesis.gray as py_gray
except ImportError:
    py_gray = None  # type: ignore[assignment]


@pytest.mark.tier1
def test_tc1_01_01_forward_bijection_exactness() -> None:
    """TC1.01.01: For all k in 0..15, gray(k) produces exact 4-bit Gray sequence."""
    expected = [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]
    for k, exp in enumerate(expected):
        assert int_to_gray_oracle(k) == exp
        if py_gray is not None:
            assert py_gray.int_to_gray(k) == exp


@pytest.mark.tier1
def test_tc1_01_02_inverse_bijection_invariance() -> None:
    """TC1.01.02: For all Gray integers g in 0..15, gray_inv(g) recovers k."""
    for k in range(16):
        g = int_to_gray_oracle(k)
        assert gray_to_int_oracle(g) == k
        if py_gray is not None:
            # Tests implementation against specification
            assert py_gray.gray_to_int(g) == k


@pytest.mark.tier1
def test_tc1_01_03_bit_representation_parsing() -> None:
    """TC1.01.03: Bit parsing and conversion exact round-trip."""
    for val in range(16):
        bits = int_to_bits_oracle(val, 4)
        assert len(bits) == 4
        assert all(b in (0, 1) for b in bits)
        assert bits_to_int_oracle(bits) == val
        if py_gray is not None:
            assert py_gray.int_to_bits(val, 4) == bits
            assert py_gray.bits_to_int(bits) == val


@pytest.mark.tier1
def test_tc1_01_04_single_bit_step_property() -> None:
    """TC1.01.04: Consecutive Gray codes on 16-cycle differ by exactly 1 bit."""
    for k in range(16):
        g1 = int_to_gray_oracle(k)
        g2 = int_to_gray_oracle((k + 1) % 16)
        hamming_dist = (g1 ^ g2).bit_count()
        assert hamming_dist == 1


@pytest.mark.tier1
def test_tc1_01_05_complete_4bit_coverage() -> None:
    """TC1.01.05: The image of gray(k) covers all integers 0..15 with no duplicates."""
    codes = [int_to_gray_oracle(k) for k in range(16)]
    assert len(codes) == 16
    assert len(set(codes)) == 16
    assert set(codes) == set(range(16))
