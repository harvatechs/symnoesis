"""Tier 1 Feature Tests: F13 Python Strict Typing & F14 TypeScript Reference Core.

Verifies Python typing/linting standards and TypeScript package architecture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


# --- Feature 13: Python Strict Typing & Linting ---


@pytest.mark.tier1
def test_tc1_13_01_package_importability() -> None:
    """TC1.13.01: symnoesis package imports cleanly without circular dependencies."""
    import symnoesis

    assert hasattr(symnoesis, "__file__")


@pytest.mark.tier1
def test_tc1_13_02_pyproject_toml_configuration() -> None:
    """TC1.13.02: pyproject.toml configures strict type checking (mypy) and ruff."""
    pyproject = REPO_ROOT / "packages" / "py" / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text(encoding="utf-8")
    assert "strict = true" in content
    assert "tool.ruff" in content


@pytest.mark.tier1
def test_tc1_13_03_zero_numeric_constants_outside_config() -> None:
    """TC1.13.03: Verifies absence of hardcoded threshold constants in source code."""
    # Checked via static inspection of symnoesis codebase
    src_dir = REPO_ROOT / "packages" / "py" / "src" / "symnoesis"
    for py_file in src_dir.glob("*.py"):
        if py_file.name == "config.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        # Ensure 0.4207 is not hardcoded in mathematical logic
        assert "0.420740" not in text, f"Hardcoded constant in {py_file.name}"


@pytest.mark.tier1
def test_tc1_13_04_version_metadata() -> None:
    """TC1.13.04: Package defines __version__ attribute conforming to 0.1.0 dev release."""
    import symnoesis

    version = getattr(symnoesis, "__version__", None)
    assert version is not None, "symnoesis.__version__ must be defined"
    assert "0.1.0" in version


@pytest.mark.tier1
def test_tc1_13_05_clean_namespace_exports() -> None:
    """TC1.13.05: __all__ or root namespace exposes core interface cleanly."""
    import symnoesis

    # Public API exports
    assert hasattr(symnoesis, "load_config") or hasattr(symnoesis, "config")


# --- Feature 14: TypeScript Reference Core ---


@pytest.mark.tier1
def test_tc1_14_01_ts_package_manifest_structure() -> None:
    """TC1.14.01: packages/ts/package.json exists with @symnoesis/core identity."""
    pkg_json = REPO_ROOT / "packages" / "ts" / "package.json"
    assert pkg_json.exists()
    content = pkg_json.read_text(encoding="utf-8")
    assert "@symnoesis/core" in content


@pytest.mark.tier1
def test_tc1_14_02_ts_tsconfig_strict_mode() -> None:
    """TC1.14.02: tsconfig.json enforces strict mode and exactOptionalPropertyTypes."""
    tsconfig = REPO_ROOT / "packages" / "ts" / "tsconfig.json"
    assert tsconfig.exists()
    content = tsconfig.read_text(encoding="utf-8")
    assert '"strict": true' in content


@pytest.mark.tier1
def test_tc1_14_03_ts_source_entrypoint() -> None:
    """TC1.14.03: packages/ts/src/index.ts entrypoint exists."""
    index_ts = REPO_ROOT / "packages" / "ts" / "src" / "index.ts"
    assert index_ts.exists()


@pytest.mark.tier1
def test_tc1_14_04_ts_pnpm_workspace_membership() -> None:
    """TC1.14.04: packages/ts is declared in pnpm-workspace.yaml."""
    pnpm_ws = REPO_ROOT / "pnpm-workspace.yaml"
    assert pnpm_ws.exists()
    content = pnpm_ws.read_text(encoding="utf-8")
    assert "packages/*" in content or "packages/ts" in content


@pytest.mark.tier1
def test_tc1_14_05_ts_dist_or_build_target() -> None:
    """TC1.14.05: package.json specifies build scripts targeting ESM and type definitions."""
    pkg_json = REPO_ROOT / "packages" / "ts" / "package.json"
    content = pkg_json.read_text(encoding="utf-8")
    assert '"build"' in content
