"""Binary-reflected Gray code operations and bijections for Symnoesis.

Normative implementation of SPEC §4:
  gray(k) = k ^ (k >> 1)
  gray_inv(g) = fold g with shifts (1, 2, 4, 8)
"""

from __future__ import annotations


def int_to_gray(k: int) -> int:
    """Computes the binary-reflected Gray code for integer k: G(k) = k ^ (k >> 1)."""
    if k < 0:
        raise ValueError(f"k must be non-negative, got {k}")
    return k ^ (k >> 1)


def gray_to_int(g: int) -> int:
    """Computes the inverse Gray code: recovers k such that int_to_gray(k) == g."""
    if g < 0:
        raise ValueError(f"g must be non-negative, got {g}")
    n = g
    shift = 1
    while (n >> shift) > 0:
        n ^= n >> shift
        shift <<= 1
    return n


def int_to_bits(val: int, bit_width: int = 4) -> list[int]:
    """Converts an integer to a big-endian list of bits of length bit_width."""
    if val < 0 or val >= (1 << bit_width):
        raise ValueError(f"Value {val} cannot fit in {bit_width} bits")
    return [(val >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]


def bits_to_int(bits: list[int]) -> int:
    """Converts a big-endian list of bits to an integer."""
    val = 0
    for b in bits:
        if b not in (0, 1):
            raise ValueError(f"Bits must be 0 or 1, got {b}")
        val = (val << 1) | b
    return val


def hamming_distance(a: int, b: int) -> int:
    """Computes the Hamming distance (number of bit differences) between two integers."""
    return (a ^ b).bit_count()


def is_adjacent_on_torus(index1: int, index2: int, size: int = 16) -> bool:
    """Returns True if index1 and index2 are neighbors on periodic 1D grid."""
    return (index1 - index2) % size in (1, size - 1)
