"""Tests for 16x16 grid coordinate system and 256 pixel IDs."""

import json
from pathlib import Path

from symnoesis.grid import (
    PixelCoord,
    coord_to_pixel_id,
    get_all_single_flip_neighbors,
    get_grid_neighbors,
    parse_pixel_id,
    pixel_id_to_coord,
)


def test_256_pixels_golden_vector() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    with open(repo_root / "spec" / "vectors" / "grid-256-pixels.json", encoding="utf-8") as f:
        data = json.load(f)

    pixels = data["pixels"]
    assert len(pixels) == 256

    seen_ids: set[str] = set()
    for p in pixels:
        pid = p["pixel_id"]
        col = p["col"]
        row = p["row"]
        h_bits = p["h_bits"]
        m_bits = p["m_bits"]

        assert pid not in seen_ids
        seen_ids.add(pid)

        coord = PixelCoord(col=col, row=row)
        assert coord_to_pixel_id(coord) == pid
        assert pixel_id_to_coord(pid) == coord

        parsed_h, parsed_m = parse_pixel_id(pid)
        assert parsed_h == h_bits
        assert parsed_m == m_bits


def test_grid_neighbors_count_and_torus() -> None:
    coord = PixelCoord(col=0, row=0)
    neighbors = get_grid_neighbors(coord)
    assert len(neighbors) == 4
    # On periodic boundary 16x16: (15, 0), (1, 0), (0, 15), (0, 1)
    assert PixelCoord(col=15, row=0) in neighbors
    assert PixelCoord(col=1, row=0) in neighbors
    assert PixelCoord(col=0, row=15) in neighbors
    assert PixelCoord(col=0, row=1) in neighbors


def test_single_flip_neighbors_count() -> None:
    pid = "h0000-m0000"
    flips = get_all_single_flip_neighbors(pid)
    assert len(flips) == 8
    # 4 human flips
    assert "h1000-m0000" in flips
    assert "h0100-m0000" in flips
    assert "h0010-m0000" in flips
    assert "h0001-m0000" in flips
    # 4 machine flips
    assert "h0000-m1000" in flips
    assert "h0000-m0100" in flips
    assert "h0000-m0010" in flips
    assert "h0000-m0001" in flips
