"""Tier 1 Feature Tests: F02 16x16 Grid Coordinates & Pixel ID (SPEC §4).

Verifies canonical pixel ID format, parsing, 256-coordinate mapping, and neighbor topologies.
"""

from __future__ import annotations

import re

import pytest
from tests.e2e.oracle import (
    coord_to_pixel_id_oracle,
    get_all_single_flip_neighbors_oracle,
    get_grid_neighbors_oracle,
    pixel_id_to_coord_oracle,
)

try:
    import symnoesis.grid as py_grid
except ImportError:
    py_grid = None  # type: ignore[assignment]

PIXEL_ID_RE = re.compile(r"^h([01]{4})-m([01]{4})$")


@pytest.mark.tier1
def test_tc1_02_01_canonical_pixel_id_generation() -> None:
    """TC1.02.01: Pixel IDs conform to canonical h{HHHH}-m{MMMM} format."""
    for col in (0, 7, 10, 15):
        for row in (0, 4, 11, 15):
            pid = coord_to_pixel_id_oracle(col, row)
            assert PIXEL_ID_RE.match(pid) is not None
            if py_grid is not None:
                coord = py_grid.PixelCoord(col=col, row=row)
                assert py_grid.coord_to_pixel_id(coord) == pid


@pytest.mark.tier1
def test_tc1_02_02_pixel_id_parsing() -> None:
    """TC1.02.02: Pixel ID parsing recovers exact bits and coordinates."""
    pid = "h1011-m0110"
    col, row = pixel_id_to_coord_oracle(pid)
    assert (col, row) == (13, 4)
    if py_grid is not None:
        h_bits, m_bits = py_grid.parse_pixel_id(pid)
        assert h_bits == [1, 0, 1, 1]
        assert m_bits == [0, 1, 1, 0]


@pytest.mark.tier1
def test_tc1_02_03_roundtrip_coordinate_invariance() -> None:
    """TC1.02.03: All 256 coordinates map 1-to-1 to unique pixel IDs and back."""
    seen_ids: set[str] = set()
    for col in range(16):
        for row in range(16):
            pid = coord_to_pixel_id_oracle(col, row)
            assert pid not in seen_ids
            seen_ids.add(pid)
            c_recovered, r_recovered = pixel_id_to_coord_oracle(pid)
            assert (c_recovered, r_recovered) == (col, row)
            if py_grid is not None:
                # Tests system under test against oracle
                coord = py_grid.PixelCoord(col=col, row=row)
                assert py_grid.pixel_id_to_coord(pid) == coord
    assert len(seen_ids) == 256


@pytest.mark.tier1
def test_tc1_02_04_planar_toroidal_neighbors() -> None:
    """TC1.02.04: Planar grid neighbors wrap toroidally and differ by 1 bit."""
    neighbors = get_grid_neighbors_oracle(0, 0)
    assert set(neighbors) == {(15, 0), (1, 0), (0, 15), (0, 1)}
    for nc, nr in neighbors:
        pid_orig = coord_to_pixel_id_oracle(0, 0)
        pid_neigh = coord_to_pixel_id_oracle(nc, nr)
        # Differ by exactly 1 bit
        orig_bits = [int(c) for c in pid_orig[1:5] + pid_orig[7:11]]
        neigh_bits = [int(c) for c in pid_neigh[1:5] + pid_neigh[7:11]]
        diff = sum(b1 != b2 for b1, b2 in zip(orig_bits, neigh_bits, strict=False))
        assert diff == 1


@pytest.mark.tier1
def test_tc1_02_05_eight_single_flip_hypercube_neighbors() -> None:
    """TC1.02.05: Every pixel has exactly 8 hypercube neighbors (4 H + 4 M flips)."""
    pid = "h0000-m0000"
    neighbors = get_all_single_flip_neighbors_oracle(pid)
    assert len(neighbors) == 8
    assert len(set(neighbors)) == 8
    # 4 Human bit flips
    assert "h1000-m0000" in neighbors
    assert "h0100-m0000" in neighbors
    assert "h0010-m0000" in neighbors
    assert "h0001-m0000" in neighbors
    # 4 Machine bit flips
    assert "h0000-m1000" in neighbors
    assert "h0000-m0100" in neighbors
    assert "h0000-m0010" in neighbors
    assert "h0000-m0001" in neighbors
