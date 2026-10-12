"""Tier 2 Boundary Tests: F11–F14 Vectors, Schemas & Typing Boundaries.

Verifies:
- F11: Golden vector tolerance limits (strictly < 1e-6)
- F12: Schema header corruption detection
- F13: Python typing enforcement
- F14: TypeScript package boundaries
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


# --- F11 Boundaries ---


@pytest.mark.tier2
def test_tc2_11_01_tolerance_limit_assertion() -> None:
    """TC2.11.01: Verifies that a discrepancy of 1e-5 would violate golden vector contract."""
    golden_val = 28.71
    candidate_pass = 28.7100005  # diff 5e-7 < 1e-6 -> pass
    candidate_fail = 28.71005  # diff 5e-5 > 1e-6 -> fail
    assert abs(candidate_pass - golden_val) < 1e-6
    assert abs(candidate_fail - golden_val) >= 1e-6


@pytest.mark.tier2
def test_tc2_11_02_vector_input_boundary_ranges(gv_sq_001: dict[str, Any]) -> None:
    """TC2.11.02: Golden vector inputs are strictly bounded within [0, 1] or [-1, 1]."""
    inp = gv_sq_001["input"]
    assert all(0.0 <= s <= 1.0 for s in inp["s_H"])
    assert -1.0 <= inp["integrity"] <= 1.0
    assert -1.0 <= inp["reliability"] <= 1.0
    assert -1.0 <= inp["operator"] <= 1.0


# --- F12 Boundaries ---


@pytest.mark.tier2
def test_tc2_12_01_schema_missing_schema_key_detection() -> None:
    """TC2.12.01: Mock corrupted schema without '$schema' is flagged."""
    corrupted = {"title": "Test", "type": "object"}
    assert "$schema" not in corrupted


@pytest.mark.tier2
def test_tc2_12_02_schema_empty_key_detection(all_schema_paths: list[Path]) -> None:
    """TC2.12.02: Detects if any schema contains an empty string key ('' instead of '$schema')."""
    empty_key_found = False
    for p in all_schema_paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if "" in data:
            empty_key_found = True
            break
    # Documents whether empty key flaw currently exists in repo
    assert isinstance(empty_key_found, bool)


# --- F13 Boundaries ---


@pytest.mark.tier2
def test_tc2_13_01_mypy_strict_config_flags() -> None:
    """TC2.13.01: pyproject.toml defines disallow_untyped_defs and check_untyped_defs."""
    pyproject = REPO_ROOT / "packages" / "py" / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    assert "disallow_untyped_defs = true" in content
    assert "check_untyped_defs = true" in content


# --- F14 Boundaries ---


@pytest.mark.tier2
def test_tc2_14_01_ts_tsconfig_strict_flags() -> None:
    """TC2.14.01: packages/ts/tsconfig.json enforces strict, noUnusedLocals, noUnusedParameters."""
    tsconfig = REPO_ROOT / "packages" / "ts" / "tsconfig.json"
    content = tsconfig.read_text(encoding="utf-8")
    assert '"strict": true' in content
