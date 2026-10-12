"""Tier 1 Feature Tests: F12 Schema Header Repair & Integrity (Milestone M1).

Verifies the restoration of the "$schema" property across all 16 JSON Schemas in spec/schemas/.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

SCHEMA_NAMES = [
    "assessment.schema.json",
    "config.schema.json",
    "consent.schema.json",
    "cover_rule.schema.json",
    "dyad.schema.json",
    "dyad_window_record.schema.json",
    "map_frame.schema.json",
    "memory_event.schema.json",
    "pixel_record.schema.json",
    "run_manifest.schema.json",
    "session.schema.json",
    "symnoesis_card.schema.json",
    "tool_call.schema.json",
    "turn.schema.json",
    "variable_score.schema.json",
    "window.schema.json",
]


@pytest.mark.tier1
def test_tc1_12_01_config_schema_header(all_schema_paths: list[Path]) -> None:
    """TC1.12.01: config.schema.json contains valid '$schema' property."""
    config_schema = next(p for p in all_schema_paths if p.name == "config.schema.json")
    with open(config_schema, encoding="utf-8") as f:
        data = json.load(f)
    assert "$schema" in data, f"Missing '$schema' in {config_schema.name}"


@pytest.mark.tier1
def test_tc1_12_02_pixel_record_schema_header(all_schema_paths: list[Path]) -> None:
    """TC1.12.02: pixel_record.schema.json contains valid '$schema' property."""
    pixel_schema = next(p for p in all_schema_paths if p.name == "pixel_record.schema.json")
    with open(pixel_schema, encoding="utf-8") as f:
        data = json.load(f)
    assert "$schema" in data, f"Missing '$schema' in {pixel_schema.name}"


@pytest.mark.tier1
def test_tc1_12_03_run_manifest_schema_header(all_schema_paths: list[Path]) -> None:
    """TC1.12.03: run_manifest.schema.json contains valid '$schema' property."""
    manifest_schema = next(p for p in all_schema_paths if p.name == "run_manifest.schema.json")
    with open(manifest_schema, encoding="utf-8") as f:
        data = json.load(f)
    assert "$schema" in data, f"Missing '$schema' in {manifest_schema.name}"


@pytest.mark.tier1
def test_tc1_12_04_all_16_schemas_parsable(all_schema_paths: list[Path]) -> None:
    """TC1.12.04: All 16 schemas exist and parse as valid JSON."""
    found_names = {p.name for p in all_schema_paths}
    assert found_names == set(SCHEMA_NAMES), f"Missing schemas: {set(SCHEMA_NAMES) - found_names}"
    for p in all_schema_paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "type" in data or "properties" in data or "$ref" in data


@pytest.mark.tier1
def test_tc1_12_05_schema_draft_consistency(all_schema_paths: list[Path]) -> None:
    """TC1.12.05: Every schema specifies a recognized json-schema.org dialect URI."""
    for p in all_schema_paths:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        schema_uri = data.get("$schema", "")
        assert "json-schema.org" in schema_uri, (
            f"{p.name} does not reference json-schema.org dialect"
        )
