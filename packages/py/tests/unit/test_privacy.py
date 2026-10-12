"""Unit tests for Privacy & Telemetry Protection Engine (SPEC §16)."""

from __future__ import annotations

from typing import Any

import pytest

from symnoesis.privacy import (
    add_laplace_noise,
    apply_differential_privacy,
    apply_k_anonymity,
    filter_consenting_records,
    pseudonymize_id,
    sanitize_turn_features,
    validate_no_raw_text,
)


@pytest.mark.unit
def test_pseudonymize_id_determinism_and_format() -> None:
    """Pseudonymization produces deterministic salted SHA-256 strings."""
    p1 = pseudonymize_id("user_alpha", salt="salt1")
    p2 = pseudonymize_id("user_alpha", salt="salt1")
    p3 = pseudonymize_id("user_alpha", salt="salt2")
    p4 = pseudonymize_id("user_beta", salt="salt1")

    assert p1 == p2
    assert p1 != p3
    assert p1 != p4
    assert p1.startswith("anon_")
    assert len(p1) == 21  # "anon_" (5) + 16 chars = 21


@pytest.mark.unit
def test_validate_no_raw_text_detects_prohibited_keys() -> None:
    """validate_no_raw_text raises ValueError on prohibited raw conversational text."""
    # Top-level prohibited keys
    for key in ("raw_text", "message_body", "raw_prompt", "raw_response", "prompt", "response"):
        with pytest.raises(ValueError, match="Prohibited raw text key"):
            validate_no_raw_text({key: "sample content"})

    # Nested prohibited keys
    with pytest.raises(ValueError, match="Prohibited raw text key"):
        validate_no_raw_text({"metadata": {"nested": {"text": "hello"}}})

    # Prohibited key inside a list of dicts
    with pytest.raises(ValueError, match="Prohibited raw text key"):
        validate_no_raw_text({"events": [{"turn": 1}, {"content": "bad"}]})

    # Valid telemetry payload does not raise
    clean_payload = {
        "session_id": "sess-001",
        "turn_index": 2,
        "features": {
            "brevity": 0.55,
            "latency_ms": 320,
            "is_unaided": True,
        },
    }
    validate_no_raw_text(clean_payload)


@pytest.mark.unit
def test_sanitize_turn_features() -> None:
    """sanitize_turn_features retains only numerical and boolean metrics."""
    raw = {
        "latency_ms": 240.5,
        "token_count": 42,
        "is_probe": True,
        "ignored_string_metadata": "some_tag",
    }
    sanitized = sanitize_turn_features(raw)
    assert sanitized == {
        "latency_ms": 240.5,
        "token_count": 42,
        "is_probe": True,
    }


@pytest.mark.unit
def test_apply_k_anonymity_floor_and_boundary() -> None:
    """Enforces cell suppression at k_min = 10.0 floor."""
    records: list[dict[str, Any]] = [
        {"cell": 1, "n_eff": 9.999, "sq": 35.0},
        {"cell": 2, "n_eff": 10.000, "sq": 45.0},
        {"cell": 3, "n_eff": 25.4, "sq": -12.0},
        {"cell": 4, "n_eff": None, "sq": 10.0},
    ]

    anonymized = apply_k_anonymity(records, k_min=10.0)

    # Cell 1: 9.999 < 10.0 -> Suppressed
    assert anonymized[0]["suppressed"] is True
    assert anonymized[0]["sq"] is None

    # Cell 2: 10.000 >= 10.0 -> Released
    assert anonymized[1]["suppressed"] is False
    assert anonymized[1]["sq"] == 45.0

    # Cell 3: 25.4 >= 10.0 -> Released
    assert anonymized[2]["suppressed"] is False
    assert anonymized[2]["sq"] == -12.0

    # Cell 4: None -> Suppressed
    assert anonymized[3]["suppressed"] is True
    assert anonymized[3]["sq"] is None


@pytest.mark.unit
def test_differential_privacy_laplace_budget_validation() -> None:
    """add_laplace_noise rejects non-positive epsilon and sensitivity."""
    for bad_eps in (0.0, -0.5, -10.0):
        with pytest.raises(ValueError, match="strictly positive"):
            add_laplace_noise(10.0, epsilon=bad_eps)

    with pytest.raises(ValueError, match="Sensitivity must be strictly positive"):
        add_laplace_noise(10.0, epsilon=1.0, sensitivity=0.0)

    with pytest.raises(ValueError, match="strictly positive"):
        apply_differential_privacy([10.0], epsilon=-1.0)


@pytest.mark.unit
def test_differential_privacy_laplace_noise_properties() -> None:
    """Differential privacy produces perturbed values respecting seed and clamping."""
    val = 50.0
    # Seed reproducibility
    res1 = add_laplace_noise(val, epsilon=1.0, sensitivity=1.0, seed=12345)
    res2 = add_laplace_noise(val, epsilon=1.0, sensitivity=1.0, seed=12345)
    assert res1 == res2
    assert res1 != val

    # Non-negative clamp
    clamped = add_laplace_noise(0.0, epsilon=1.0, seed=42, min_val=0.0)
    assert clamped >= 0.0

    # Vectorized perturbation
    counts = [10.0, 20.0, 30.0, 40.0]
    dp_counts = apply_differential_privacy(counts, epsilon=1.0, seed=999, min_val=0.0)
    assert len(dp_counts) == len(counts)
    assert all(c >= 0.0 for c in dp_counts)
    assert dp_counts != counts


@pytest.mark.unit
def test_filter_consenting_records() -> None:
    """Excludes records from subjects with revoked or missing consent."""
    records = [
        {"human_id_pseudonym": "anon_001", "metric": 10},
        {"human_id_pseudonym": "anon_002", "metric": 20},
        {"human_id_pseudonym": "anon_003", "metric": 30},
    ]
    consents = {
        "anon_001": True,
        "anon_002": False,  # Revoked
        # anon_003: missing from mapping
    }

    filtered = filter_consenting_records(records, consents)
    assert len(filtered) == 1
    assert filtered[0]["human_id_pseudonym"] == "anon_001"


@pytest.mark.unit
def test_telemetry_module_re_exports() -> None:
    """Telemetry module properly re-exports privacy protection primitives."""
    import symnoesis.telemetry as tel

    assert hasattr(tel, "pseudonymize_id")
    assert hasattr(tel, "apply_k_anonymity")
    assert hasattr(tel, "add_laplace_noise")
    assert hasattr(tel, "apply_differential_privacy")
    assert hasattr(tel, "filter_consenting_records")
    assert hasattr(tel, "sanitize_turn_features")
    assert hasattr(tel, "validate_no_raw_text")
