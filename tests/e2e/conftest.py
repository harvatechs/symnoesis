"""Pytest fixtures and configuration for Symnoesis E2E test suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
py_src = REPO_ROOT / "packages" / "py" / "src"
if str(py_src) not in sys.path:
    sys.path.insert(0, str(py_src))

SPEC_DIR = REPO_ROOT / "spec"
CONFIG_FILE = SPEC_DIR / "config" / "symn-01.v0.1.yaml"
VECTORS_DIR = SPEC_DIR / "vectors"
SCHEMAS_DIR = SPEC_DIR / "schemas"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tier1: Tier 1 Feature Coverage tests")
    config.addinivalue_line("markers", "tier2: Tier 2 Boundary & Corner Case tests")
    config.addinivalue_line("markers", "tier3: Tier 3 Cross-Feature Combination tests")
    config.addinivalue_line("markers", "tier4: Tier 4 Real-World Application Scenario tests")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def spec_dir() -> Path:
    return SPEC_DIR


@pytest.fixture(scope="session")
def raw_config() -> dict[str, Any]:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def symn_config() -> Any:
    try:
        from symnoesis.config import load_config

        return load_config(CONFIG_FILE)
    except Exception:
        return None


@pytest.fixture(scope="session")
def gv_sq_001() -> dict[str, Any]:
    with open(VECTORS_DIR / "gv-sq-001.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def gv_sq_002() -> dict[str, Any]:
    with open(VECTORS_DIR / "gv-sq-002.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def gv_sq_003() -> dict[str, Any]:
    with open(VECTORS_DIR / "gv-sq-003.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def gray_code_16() -> dict[str, Any]:
    with open(VECTORS_DIR / "gray-code-16.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def grid_256_pixels() -> dict[str, Any]:
    with open(VECTORS_DIR / "grid-256-pixels.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_schema_paths() -> list[Path]:
    return sorted(SCHEMAS_DIR.glob("*.json"))
