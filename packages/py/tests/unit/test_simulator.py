"""Unit tests for Synthetic Persona & Dyad Simulator (SPEC §13, §14)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from symnoesis.simulator.cohort import (
    export_all_domain_fixtures,
    generate_synthetic_cohort,
)
from symnoesis.simulator.dyad import (
    VALID_DOMAINS,
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


@pytest.mark.unit
def test_persona_parameter_validation_and_bounds() -> None:
    """SyntheticPersona validates that all trait dimensions are in [0.0, 1.0]."""
    # Valid persona
    persona = SyntheticPersona(
        persona_id="p-001",
        cognitive_agency=0.75,
        epistemic_calibration=0.65,
        vulnerability=0.20,
        initial_skill=0.55,
        habit_stability=0.85,
    )
    p_dict = persona.to_dict()
    assert p_dict["cognitive_agency"] == 0.75

    # Out of bounds traits
    with pytest.raises(ValueError, match="must be bounded in"):
        SyntheticPersona(
            persona_id="p-bad",
            cognitive_agency=-0.1,
            epistemic_calibration=0.5,
            vulnerability=0.5,
        )

    with pytest.raises(ValueError, match="must be bounded in"):
        SyntheticPersona(
            persona_id="p-bad",
            cognitive_agency=1.2,
            epistemic_calibration=0.5,
            vulnerability=0.5,
        )


@pytest.mark.unit
def test_generate_persona_deterministic() -> None:
    """Persona generation from identical seeds produces bit-for-bit identical traits."""
    p1 = generate_persona(seed=1337)
    p2 = generate_persona(seed=1337)
    p3 = generate_persona(seed=9999)

    assert p1 == p2
    assert p1.cognitive_agency == p2.cognitive_agency
    assert p1 != p3


@pytest.mark.unit
def test_generate_persona_cohort_uniqueness() -> None:
    """Cohort generation guarantees unique persona IDs."""
    cohort = generate_persona_cohort(size=25, seed=42)
    assert len(cohort) == 25
    ids = [p.persona_id for p in cohort]
    assert len(set(ids)) == len(ids)

    with pytest.raises(ValueError, match="Cohort size must be positive"):
        generate_persona_cohort(size=0)


@pytest.mark.unit
def test_ai_off_probe_scheduler() -> None:
    """AIOffProbeScheduler schedules probes on session 1 and multiples of interval."""
    scheduler = AIOffProbeScheduler(probe_interval_sessions=5, mode="unaided")

    assert scheduler.should_schedule_probe(0) is False
    assert scheduler.should_schedule_probe(1) is True  # Baseline frame
    assert scheduler.should_schedule_probe(2) is False
    assert scheduler.should_schedule_probe(5) is True  # Probe 1
    assert scheduler.should_schedule_probe(6) is False
    assert scheduler.should_schedule_probe(10) is True  # Probe 2

    cfg_probe = scheduler.generate_probe_config(5, "learning")
    assert cfg_probe["mode"] == "unaided"
    assert cfg_probe["is_probe_session"] is True

    cfg_aided = scheduler.generate_probe_config(3, "learning")
    assert cfg_aided["mode"] == "aided"
    assert cfg_aided["is_probe_session"] is False


@pytest.mark.unit
def test_sycophancy_twin_prompts() -> None:
    """Sycophancy twin generator produces opposing user stance prompts."""
    twins = generate_sycophancy_twin_prompts(
        topic="functional programming",
        stance_a="pure functions are essential",
        stance_b="object-oriented state is superior",
    )
    assert twins["prompt_a"] != twins["prompt_b"]
    assert "pure functions" in twins["prompt_a"]
    assert "object-oriented" in twins["prompt_b"]


@pytest.mark.unit
def test_benign_boundary_script() -> None:
    """Benign-proxy boundary erosion generator adheres to abstract token safety rule."""
    script = generate_benign_boundary_script(scenario_id="scen-test-01")
    assert script["intent"] == "boundary_erosion_test"
    assert script["benign_proxy"] is True
    assert len(script["stages"]) == 3
    # Verifies absence of harmful text
    for stage in script["stages"]:
        assert "PROBE_" in stage["token"]


@pytest.mark.unit
def test_dyad_creation_and_domain_validation() -> None:
    """SyntheticDyad validates domain membership."""
    persona = generate_persona(seed=42)

    for domain in VALID_DOMAINS:
        dyad = create_synthetic_dyad(persona=persona, domain=domain)
        d_dict = dyad.to_dict()
        assert d_dict["domain"] == domain
        assert d_dict["human_id_pseudonym"] == persona.persona_id

    with pytest.raises(ValueError, match="Domain 'invalid_domain' must be one of"):
        create_synthetic_dyad(persona=persona, domain="invalid_domain")


@pytest.mark.unit
def test_simulate_dyad_session_and_turns() -> None:
    """Simulates multi-turn session conforming to session & turn schemas without raw text."""
    persona = generate_persona(seed=101)
    dyad = create_synthetic_dyad(persona=persona, domain="learning")

    session, turns = simulate_dyad_session(dyad=dyad, session_index=1, seed=42, turn_count=5)

    assert session["dyad_id"] == dyad.dyad_id
    assert session["turn_count"] == 5
    assert len(turns) == 5

    for t in turns:
        assert t["session_id"] == session["session_id"]
        assert "turn_index" in t
        assert "features" in t
        # Ensure zero raw text
        assert "raw_prompt" not in t["features"]
        assert "raw_response" not in t["features"]
        assert "raw_text" not in t["features"]


@pytest.mark.unit
def test_simulate_dyad_window_record() -> None:
    """Simulates dyad window conforming strictly to dyad_window_record schema."""
    persona = generate_persona(seed=202)
    dyad = create_synthetic_dyad(persona=persona, domain="coding")

    window_record = simulate_dyad_window(dyad=dyad, window_id="w-day-007", seed=42)

    assert window_record["dyad_id"] == dyad.dyad_id
    assert window_record["window_id"] == "w-day-007"
    assert window_record["evidence_tier"] == "E1"
    assert isinstance(window_record["modal_pixel"], str)
    assert window_record["modal_pixel"].startswith("h")
    assert isinstance(window_record["pixel_masses"], dict)
    assert -100.0 <= window_record["sq"] <= 100.0


@pytest.mark.unit
def test_generate_synthetic_cohort_and_export() -> None:
    """Generates synthetic cohort and exports reproducible E1 fixtures across 4 domains."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        exported = export_all_domain_fixtures(output_dir=tmp_path, cohort_size=10, seed=42)

        assert len(exported) == 4
        for domain in VALID_DOMAINS:
            assert domain in exported
            fixture_file = exported[domain]
            assert fixture_file.exists()
            assert fixture_file.stat().st_size > 0


@pytest.mark.unit
def test_ground_truth_recovery() -> None:
    """High cognitive agency personas produce higher HNE than low agency personas."""
    high_agency_p = SyntheticPersona(
        persona_id="p-high",
        cognitive_agency=0.95,
        epistemic_calibration=0.90,
        vulnerability=0.10,
        initial_skill=0.90,
    )
    low_agency_p = SyntheticPersona(
        persona_id="p-low",
        cognitive_agency=0.10,
        epistemic_calibration=0.15,
        vulnerability=0.85,
        initial_skill=0.10,
    )

    dyad_high = create_synthetic_dyad(persona=high_agency_p, domain="learning")
    dyad_low = create_synthetic_dyad(persona=low_agency_p, domain="learning")

    rec_high = simulate_dyad_window(dyad=dyad_high, window_id="w-1", seed=42)
    rec_low = simulate_dyad_window(dyad=dyad_low, window_id="w-1", seed=42)

    assert rec_high["hne"] > rec_low["hne"]
    assert rec_high["sq"] > rec_low["sq"]


@pytest.mark.unit
def test_generate_synthetic_cohort_invalid_domain() -> None:
    """generate_synthetic_cohort raises ValueError on invalid domain."""
    with pytest.raises(ValueError, match="Invalid domain"):
        generate_synthetic_cohort(domain="unknown_domain")
