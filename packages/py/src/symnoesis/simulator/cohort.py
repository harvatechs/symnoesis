"""Synthetic Cohort Generation & Fixture Export (ORIGINAL_REQUEST R3, SPEC §13).

Generates reproducible synthetic cohorts across all 4 domains adhering strictly
to dyad_window_record.schema.json and exports them as E1 fixtures to data/fixtures/.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from symnoesis.simulator.dyad import (
    VALID_DOMAINS,
    create_synthetic_dyad,
    simulate_dyad_window,
)
from symnoesis.simulator.persona import generate_persona_cohort


def generate_synthetic_cohort(
    domain: str,
    system_id: str = "Fixture-A (scripted)",
    cohort_size: int = 20,
    seed: int = 42,
    window_id: str = "w-day-007",
    system_quality: float = 0.75,
) -> list[dict[str, Any]]:
    """Generate a reproducible synthetic cohort of dyad-window records for a domain.

    Args:
        domain: One of 'learning', 'coding', 'health-information', 'advice-companionship'.
        system_id: Machine identifier (fictional name with '(scripted)' label).
        cohort_size: Number of dyads in cohort.
        seed: Deterministic random seed.
        window_id: Observation window identifier.
        system_quality: System baseline quality factor.

    Returns:
        List of DyadWindowRecord dictionaries adhering to dyad_window_record.schema.json.

    Raises:
        ValueError: If domain is invalid or duplicates are detected.
    """
    if domain not in VALID_DOMAINS:
        raise ValueError(f"Invalid domain '{domain}'. Must be one of {sorted(VALID_DOMAINS)}")

    personas = generate_persona_cohort(size=cohort_size, seed=seed, id_prefix=f"user-{domain[:4]}")

    records: list[dict[str, Any]] = []
    seen_dyad_ids: set[str] = set()

    for idx, persona in enumerate(personas):
        dyad_id = f"d-{domain[:4]}-{seed:04d}-{idx:03d}"
        if dyad_id in seen_dyad_ids:
            raise ValueError(f"Duplicate dyad identifier detected in cohort: {dyad_id}")
        seen_dyad_ids.add(dyad_id)

        dyad = create_synthetic_dyad(
            persona=persona,
            system_id=system_id,
            domain=domain,
            dyad_id=dyad_id,
        )

        record = simulate_dyad_window(
            dyad=dyad,
            window_id=window_id,
            seed=seed * 100 + idx,
            system_quality=system_quality,
        )
        records.append(record)

    return records


def export_all_domain_fixtures(
    output_dir: Path,
    cohort_size: int = 25,
    seed: int = 42,
    system_id: str = "Fixture-A (scripted)",
) -> dict[str, Path]:
    """Generate and write synthetic E1 evidence fixtures for all 4 domains into data/fixtures/.

    Args:
        output_dir: Directory where fixtures will be written.
        cohort_size: Cohort size per domain.
        seed: Master random seed.
        system_id: Fictional system identifier.

    Returns:
        Mapping of domain names to created fixture file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files: dict[str, Path] = {}

    for idx, domain in enumerate(sorted(VALID_DOMAINS)):
        domain_seed = seed * 31 + idx
        records = generate_synthetic_cohort(
            domain=domain,
            system_id=system_id,
            cohort_size=cohort_size,
            seed=domain_seed,
            window_id="w-day-007",
        )

        fixture_file = output_dir / f"{domain}.json"
        payload = {
            "domain": domain,
            "system_id": system_id,
            "evidence_tier": "E1",
            "cohort_size": cohort_size,
            "seed": domain_seed,
            "records": records,
        }
        fixture_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        generated_files[domain] = fixture_file

    return generated_files
