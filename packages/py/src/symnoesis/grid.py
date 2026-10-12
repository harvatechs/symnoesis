"""16x16 Gray-coded Grid coordinate system and pixel ID utilities.

Normative implementation of SPEC §4:
  - Columns index Human code (H1, H2, H3, H4) in Gray order.
  - Rows index Machine code (M1, M2, M3, M4) in Gray order.
  - Pixel ID format: h{HHHH}-m{MMMM}
"""

from __future__ import annotations

import re
from typing import NamedTuple

from symnoesis.gray import bits_to_int, gray_to_int, int_to_bits, int_to_gray

PIXEL_ID_PATTERN = re.compile(r"^h([01]{4})-m([01]{4})$")


class PixelCoord(NamedTuple):
    col: int  # 0..15 (Human code index)
    row: int  # 0..15 (Machine code index)


class PixelBits(NamedTuple):
    H: list[int]  # [H1, H2, H3, H4]
    M: list[int]  # [M1, M2, M3, M4]


def pixel_id_from_bits(h_bits: list[int], m_bits: list[int]) -> str:
    """Constructs pixel ID from bit lists."""
    if len(h_bits) != 4 or len(m_bits) != 4:
        raise ValueError("H and M bits must both have length 4")
    h_str = "".join(str(b) for b in h_bits)
    m_str = "".join(str(b) for b in m_bits)
    return f"h{h_str}-m{m_str}"


def parse_pixel_id(pixel_id: str) -> tuple[list[int], list[int]]:
    """Parses a pixel ID into (h_bits, m_bits)."""
    match = PIXEL_ID_PATTERN.match(pixel_id)
    if not match:
        raise ValueError(f"Invalid pixel ID format: {pixel_id}. Expected format hXXXX-mYYYY.")
    h_str, m_str = match.groups()
    h_bits = [int(b) for b in h_str]
    m_bits = [int(b) for b in m_str]
    return h_bits, m_bits


def coord_to_pixel_id(coord: PixelCoord) -> str:
    """Converts grid coordinate (col, row) to pixel ID using Gray code."""
    if not (0 <= coord.col < 16 and 0 <= coord.row < 16):
        raise ValueError(f"Coordinates out of bounds [0, 15]: col={coord.col}, row={coord.row}")
    h_code = int_to_gray(coord.col)
    m_code = int_to_gray(coord.row)
    h_bits = int_to_bits(h_code, 4)
    m_bits = int_to_bits(m_code, 4)
    return pixel_id_from_bits(h_bits, m_bits)


def pixel_coord_to_id(col_or_coord: int | PixelCoord, row: int | None = None) -> str:
    """Converts grid coordinate (col, row) or PixelCoord to pixel ID using Gray code."""
    if isinstance(col_or_coord, PixelCoord):
        return coord_to_pixel_id(col_or_coord)
    if row is None:
        raise ValueError("row must be provided when col is an int")
    return coord_to_pixel_id(PixelCoord(col=col_or_coord, row=row))


def pixel_id_to_coord(pixel_id: str) -> PixelCoord:
    """Converts pixel ID to grid coordinate (col, row)."""
    h_bits, m_bits = parse_pixel_id(pixel_id)
    h_code = bits_to_int(h_bits)
    m_code = bits_to_int(m_bits)
    col = gray_to_int(h_code)
    row = gray_to_int(m_code)
    return PixelCoord(col=col, row=row)


def get_grid_neighbors(coord: PixelCoord) -> list[PixelCoord]:
    """Returns the 4 visual grid-adjacent neighbors (torus/periodic boundary)."""
    c, r = coord.col, coord.row
    return [
        PixelCoord(col=(c - 1) % 16, row=r),
        PixelCoord(col=(c + 1) % 16, row=r),
        PixelCoord(col=c, row=(r - 1) % 16),
        PixelCoord(col=c, row=(r + 1) % 16),
    ]


def get_all_single_flip_neighbors(pixel_id: str) -> list[str]:
    """Returns all 8 Hamming distance = 1 neighbors (4 human flips, 4 machine flips)."""
    h_bits, m_bits = parse_pixel_id(pixel_id)
    neighbors: list[str] = []

    # 4 Human flips
    for i in range(4):
        flipped_h = list(h_bits)
        flipped_h[i] ^= 1
        neighbors.append(pixel_id_from_bits(flipped_h, m_bits))

    # 4 Machine flips
    for i in range(4):
        flipped_m = list(m_bits)
        flipped_m[i] ^= 1
        neighbors.append(pixel_id_from_bits(h_bits, flipped_m))

    return neighbors
