"""Synthetic Dyad Simulation Engine (SPEC §1, §13, §14).

Simulates dyadic interactions between a SyntheticPersona and a machine system.
Produces structured sessions and dyad-window analysis records adhering strictly
to schemas in spec/schemas/ (dyad, session, turn, dyad_window_record).
"""

from __future__ import annotations

import datetime
import random
from dataclasses import dataclass
from typing import Any

from symnoesis.assign import compute_dyad_window_masses, get_modal_pixel
from symnoesis.config import SymnoesisConfig
from symnoesis.net_effects import compute_composite_c, compute_hne, compute_sne
from symnoesis.privacy import sanitize_turn_features
from symnoesis.simulator.persona import SyntheticPersona
from symnoesis.sq import compute_sq
from symnoesis.variables import compute_all_marginal_probabilities

VALID_DOMAINS: frozenset[str] = frozenset(
    {"learning", "coding", "health-information", "advice-companionship"}
)


@dataclass(frozen=True)
class SyntheticDyad:
    """Represents a human-AI pairing (dyad) in a target domain."""

    dyad_id: str
    human_id_pseudonym: str
    system_id: str
    domain: str
    created_at: str
    persona: SyntheticPersona

    def __post_init__(self) -> None:
        if self.domain not in VALID_DOMAINS:
            valid_list = sorted(VALID_DOMAINS)
            raise ValueError(f"Invalid domain '{self.domain}'. Must be one of {valid_list}")

    def to_dict(self) -> dict[str, str]:
        """Convert to dict conforming strictly to dyad.schema.json."""
        return {
            "dyad_id": self.dyad_id,
            "human_id_pseudonym": self.human_id_pseudonym,
            "system_id": self.system_id,
            "domain": self.domain,
            "created_at": self.created_at,
        }


def create_synthetic_dyad(
    persona: SyntheticPersona,
    system_id: str = "Fixture-A (scripted)",
    domain: str = "learning",
    dyad_id: str | None = None,
    created_at: str | None = None,
) -> SyntheticDyad:
    """Create a SyntheticDyad instance with validated fields."""
    if domain not in VALID_DOMAINS:
        raise ValueError(f"Domain '{domain}' must be one of {sorted(VALID_DOMAINS)}")

    did = dyad_id or f"d-{persona.persona_id[:8]}-{domain[:4]}"
    timestamp = created_at or datetime.datetime.now(datetime.UTC).isoformat()

    return SyntheticDyad(
        dyad_id=did,
        human_id_pseudonym=persona.persona_id,
        system_id=system_id,
        domain=domain,
        created_at=timestamp,
        persona=persona,
    )


def simulate_dyad_session(
    dyad: SyntheticDyad,
    session_index: int,
    seed: int = 42,
    turn_count: int = 6,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Simulate a single interaction episode (session) and its derived turns.

    Conforms to session.schema.json and turn.schema.json.

    Args:
        dyad: The SyntheticDyad under observation.
        session_index: 1-indexed session number.
        seed: Deterministic random seed.
        turn_count: Number of conversational turns in the session.

    Returns:
        Tuple of (session_record, list_of_turn_records).
    """
    rng = random.Random(seed * 1009 + session_index)
    session_id = f"sess-{dyad.dyad_id}-{session_index:03d}"

    start_dt = datetime.datetime(2026, 1, 1, 10, 0, 0, tzinfo=datetime.UTC)
    session_start = (start_dt + datetime.timedelta(days=session_index * 2)).isoformat()
    session_end = (start_dt + datetime.timedelta(days=session_index * 2, minutes=25)).isoformat()

    session_record: dict[str, Any] = {
        "session_id": session_id,
        "dyad_id": dyad.dyad_id,
        "start_time": session_start,
        "end_time": session_end,
        "turn_count": turn_count,
    }

    turn_records: list[dict[str, Any]] = []
    for t_idx in range(1, turn_count + 1):
        turn_id = f"turn-{session_id}-{t_idx:02d}"

        # Derived numerical features only (zero raw text)
        raw_features = {
            "turn_latency_ms": round(rng.uniform(150.0, 950.0), 1),
            "brevity": round(rng.uniform(0.2, 0.9), 3),
            "cognitive_reliance_ratio": round(rng.uniform(0.1, 0.9), 3),
            "epistemic_drift_delta": round(rng.uniform(-0.1, 0.1), 3),
            "is_unaided_probe": (session_index % 5 == 0),
        }
        sanitized_features = sanitize_turn_features(raw_features)

        turn_records.append(
            {
                "turn_id": turn_id,
                "session_id": session_id,
                "turn_index": t_idx,
                "features": sanitized_features,
            }
        )

    return session_record, turn_records


def simulate_dyad_window(
    dyad: SyntheticDyad,
    window_id: str,
    seed: int = 42,
    outcome_deltas: list[float] | None = None,
    config: SymnoesisConfig | None = None,
    system_quality: float = 0.75,
) -> dict[str, Any]:
    """Simulate a complete dyad-window unit of analysis.

    Conforms strictly to spec/schemas/dyad_window_record.schema.json.

    Args:
        dyad: The SyntheticDyad under observation.
        window_id: Temporal window identifier (e.g. 'w-day-007').
        seed: Random seed for simulation variance.
        outcome_deltas: Optional list of standardized outcome changes.
        config: Optional SymnoesisConfig (defaults to default config).
        system_quality: Base machine system quality factor in [0.0, 1.0].

    Returns:
        DyadWindowRecord dictionary.
    """
    cfg = config or SymnoesisConfig.load_default()
    rng = random.Random(seed * 2003 + 7)

    # Derive variable posteriors from persona traits and system quality
    # Human variables H1-H4
    p = dyad.persona
    h1_mu = max(0.01, min(0.99, p.cognitive_agency + rng.gauss(0.0, 0.05)))
    h2_mu = max(0.01, min(0.99, p.initial_skill + rng.gauss(0.0, 0.05)))
    h3_mu = max(0.01, min(0.99, p.epistemic_calibration + rng.gauss(0.0, 0.05)))
    h4_mu = max(0.01, min(0.99, (1.0 - p.vulnerability * 0.5) + rng.gauss(0.0, 0.05)))

    # Machine variables M1-M4
    m1_mu = max(0.01, min(0.99, system_quality + rng.gauss(0.0, 0.04)))
    m2_mu = max(0.01, min(0.99, system_quality + rng.gauss(0.0, 0.04)))
    m3_mu = max(0.01, min(0.99, system_quality + rng.gauss(0.0, 0.04)))
    m4_mu = max(0.01, min(0.99, system_quality + rng.gauss(0.0, 0.04)))

    posteriors = {
        "H1": (h1_mu, 0.08),
        "H2": (h2_mu, 0.08),
        "H3": (h3_mu, 0.08),
        "H4": (h4_mu, 0.08),
        "M1": (m1_mu, 0.08),
        "M2": (m2_mu, 0.08),
        "M3": (m3_mu, 0.08),
        "M4": (m4_mu, 0.08),
    }

    # Compute marginal probabilities & joint masses
    probs = compute_all_marginal_probabilities(posteriors, cfg)
    masses = compute_dyad_window_masses(probs, cfg)
    modal_pixel = get_modal_pixel(masses)

    # Net effects calculation
    s_h = [h1_mu, h2_mu, h3_mu, h4_mu]
    hne, _ = compute_hne(s_h, outcome_deltas=outcome_deltas, config=cfg)

    integrity = 2.0 * m4_mu - 1.0
    reliability = 2.0 * system_quality - 1.0
    sne, _ = compute_sne(integrity=integrity, reliability=reliability, operator=0.0, config=cfg)

    c, _ = compute_composite_c(hne, sne, cfg)
    # Window stability
    stability = round(0.5 + 0.5 * p.habit_stability, 3)
    sq_clipped, _, _ = compute_sq(c=c, s=stability, gate_ceiling=None, config=cfg)

    return {
        "dyad_id": dyad.dyad_id,
        "window_id": window_id,
        "modal_pixel": modal_pixel,
        "pixel_masses": masses,
        "sq": round(sq_clipped, 2),
        "hne": round(hne, 4),
        "sne": round(sne, 4),
        "evidence_tier": "E1",
    }
