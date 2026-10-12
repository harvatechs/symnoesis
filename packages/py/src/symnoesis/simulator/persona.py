"""Synthetic Persona Simulator (SPEC §13, §16).

Parameterizes cognitive agency, epistemic calibration, vulnerability,
and interaction traits for reproducible synthetic evaluation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from symnoesis.privacy import pseudonymize_id


@dataclass(frozen=True)
class SyntheticPersona:
    """Synthetic human persona with parameterized cognitive and epistemic traits."""

    persona_id: str
    cognitive_agency: float
    epistemic_calibration: float
    vulnerability: float
    initial_skill: float = 0.5
    habit_stability: float = 0.8

    def __post_init__(self) -> None:
        """Validate that all trait dimensions are bounded within [0.0, 1.0]."""
        traits = {
            "cognitive_agency": self.cognitive_agency,
            "epistemic_calibration": self.epistemic_calibration,
            "vulnerability": self.vulnerability,
            "initial_skill": self.initial_skill,
            "habit_stability": self.habit_stability,
        }
        for trait_name, value in traits.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Persona trait '{trait_name}' must be bounded in [0.0, 1.0], got {value}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Convert persona to dictionary representation."""
        return {
            "persona_id": self.persona_id,
            "cognitive_agency": self.cognitive_agency,
            "epistemic_calibration": self.epistemic_calibration,
            "vulnerability": self.vulnerability,
            "initial_skill": self.initial_skill,
            "habit_stability": self.habit_stability,
        }


def generate_persona(seed: int, persona_id: str | None = None) -> SyntheticPersona:
    """Generate a single synthetic persona deterministically from an explicit seed.

    Args:
        seed: Deterministic integer seed.
        persona_id: Optional explicit persona ID (defaults to hashed pseudonym).

    Returns:
        SyntheticPersona instance.
    """
    rng = random.Random(seed)
    pid = persona_id or pseudonymize_id(f"synth-user-{seed}", salt="symn-persona-seed")
    return SyntheticPersona(
        persona_id=pid,
        cognitive_agency=round(rng.uniform(0.1, 0.95), 4),
        epistemic_calibration=round(rng.uniform(0.1, 0.95), 4),
        vulnerability=round(rng.uniform(0.05, 0.85), 4),
        initial_skill=round(rng.uniform(0.2, 0.9), 4),
        habit_stability=round(rng.uniform(0.3, 0.95), 4),
    )


def generate_persona_cohort(
    size: int,
    seed: int = 42,
    id_prefix: str = "synth-p",
) -> list[SyntheticPersona]:
    """Generate a cohort of distinct synthetic personas with guaranteed unique IDs.

    Args:
        size: Number of personas to generate.
        seed: Base seed for cohort reproducibility.
        id_prefix: Prefix for pseudonymous identifiers.

    Returns:
        List of unique SyntheticPersona objects.

    Raises:
        ValueError: If size <= 0.
    """
    if size <= 0:
        raise ValueError(f"Cohort size must be positive, got {size}")

    cohort: list[SyntheticPersona] = []
    seen_ids: set[str] = set()

    for idx in range(size):
        sub_seed = seed * 10007 + idx
        pid = pseudonymize_id(f"{id_prefix}-{idx:04d}", salt=f"cohort-salt-{seed}")
        if pid in seen_ids:
            raise ValueError(f"Duplicate persona ID detected during cohort generation: {pid}")
        seen_ids.add(pid)
        persona = generate_persona(seed=sub_seed, persona_id=pid)
        cohort.append(persona)

    return cohort
