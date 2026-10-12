"""Synthetic Persona & Dyad Simulator (SPEC §13, §14, §16)."""

from symnoesis.simulator.cohort import export_all_domain_fixtures, generate_synthetic_cohort
from symnoesis.simulator.dyad import (
    VALID_DOMAINS,
    SyntheticDyad,
    create_synthetic_dyad,
    simulate_dyad_session,
    simulate_dyad_window,
)
from symnoesis.simulator.persona import (
    SyntheticPersona,
    generate_persona,
    generate_persona_cohort,
)
from symnoesis.simulator.probes import (
    AIOffProbeScheduler,
    generate_benign_boundary_script,
    generate_sycophancy_twin_prompts,
)

__all__ = [
    "AIOffProbeScheduler",
    "SyntheticDyad",
    "SyntheticPersona",
    "VALID_DOMAINS",
    "create_synthetic_dyad",
    "export_all_domain_fixtures",
    "generate_benign_boundary_script",
    "generate_persona",
    "generate_persona_cohort",
    "generate_sycophancy_twin_prompts",
    "generate_synthetic_cohort",
    "simulate_dyad_session",
    "simulate_dyad_window",
]
