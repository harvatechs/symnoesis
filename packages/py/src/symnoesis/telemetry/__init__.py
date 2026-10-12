"""Telemetry and Privacy Ingestion Module (SPEC §14, §16)."""

from symnoesis.privacy import (
    PROHIBITED_TEXT_KEYS,
    add_laplace_noise,
    apply_differential_privacy,
    apply_k_anonymity,
    filter_consenting_records,
    pseudonymize_id,
    sanitize_turn_features,
    validate_no_raw_text,
)

__all__ = [
    "PROHIBITED_TEXT_KEYS",
    "add_laplace_noise",
    "apply_differential_privacy",
    "apply_k_anonymity",
    "filter_consenting_records",
    "pseudonymize_id",
    "sanitize_turn_features",
    "validate_no_raw_text",
]
