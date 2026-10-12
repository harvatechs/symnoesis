"""Tests for Gray-code bijections, Hamming metrics, and adjacency."""

import json
from pathlib import Path

import pytest

from symnoesis.gray import (
    bits_to_int,
    gray_to_int,
    hamming_distance,
    int_to_bits,
    int_to_gray,
    is_adjacent_on_torus,
)


def test_gray_golden_vector() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    vector_path = repo_root / "spec" / "vectors" / "gray-code-16.json"
    with open(vector_path, encoding="utf-8") as f:
        data = json.load(f)

    elements = data["elements"]
    assert len(elements) == 16

    for item in elements:
        idx = item["index"]
        expected_code = item["code_int"]
        expected_bits = item["bits"]

        assert int_to_gray(idx) == expected_code
        assert gray_to_int(expected_code) == idx
        assert int_to_bits(expected_code, 4) == expected_bits
        assert bits_to_int(expected_bits) == expected_code


def test_gray_adjacency_hamming_distance() -> None:
    # Adjacent indices in the 16-element sequence must have Hamming distance = 1
    for i in range(16):
        curr_gray = int_to_gray(i)
        next_gray = int_to_gray((i + 1) % 16)
        assert hamming_distance(curr_gray, next_gray) == 1
        assert is_adjacent_on_torus(i, (i + 1) % 16, 16)


def test_gray_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        int_to_gray(-1)
    with pytest.raises(ValueError):
        gray_to_int(-1)
    with pytest.raises(ValueError):
        int_to_bits(16, 4)
    with pytest.raises(ValueError):
        bits_to_int([0, 1, 2])
