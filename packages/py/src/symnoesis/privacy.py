"""Privacy and Telemetry Protection Engine (SPEC §16).

Implements:
- Pseudonymous identity hashing (salted SHA-256)
- Raw conversational text rejection & telemetry feature validation
- k-Anonymity cell suppression (k_min = 10 floor)
- Differential privacy via the Laplace mechanism (epsilon = 1.0)
- Informed consent revocation filtering
"""

from __future__ import annotations

import hashlib
import random
from typing import Any

PROHIBITED_TEXT_KEYS: frozenset[str] = frozenset(
    {
        "raw_text",
        "message_body",
        "raw_prompt",
        "raw_response",
        "prompt",
        "response",
        "user_message",
        "assistant_message",
        "text",
        "content",
        "body",
    }
)


def pseudonymize_id(raw_id: str, salt: str = "symnoesis-v0.1-salt") -> str:
    """Generate a deterministic pseudonymous identifier via salted SHA-256.

    Args:
        raw_id: The original subject or system identifier.
        salt: Salt string to prevent rainbow table attacks.

    Returns:
        Pseudonymous string in the format `anon_<hash[:16]>`.
    """
    hasher = hashlib.sha256()
    hasher.update(salt.encode("utf-8"))
    hasher.update(raw_id.encode("utf-8"))
    digest = hasher.hexdigest()
    return f"anon_{digest[:16]}"


def validate_no_raw_text(payload: dict[str, Any]) -> None:
    """Verify that a dictionary contains zero raw conversational text keys.

    Recursively inspects keys and nested structures.

    Raises:
        ValueError: If any prohibited raw text key is detected.
    """
    for key, value in payload.items():
        if key in PROHIBITED_TEXT_KEYS:
            raise ValueError(
                f"Prohibited raw text key '{key}' detected. Raw text persistence is forbidden."
            )
        if isinstance(value, dict):
            validate_no_raw_text(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    validate_no_raw_text(item)


def sanitize_turn_features(raw_features: dict[str, Any]) -> dict[str, float | int | bool]:
    """Sanitize turn features, ensuring only derived numerical metrics are retained.

    Args:
        raw_features: Input features dictionary.

    Returns:
        Sanitized dictionary with only allowed numerical/boolean metric keys.

    Raises:
        ValueError: If prohibited raw text keys are present.
    """
    validate_no_raw_text(raw_features)
    sanitized: dict[str, float | int | bool] = {}
    for k, v in raw_features.items():
        if isinstance(v, (int, float, bool)) and not isinstance(v, str):
            sanitized[k] = v
    return sanitized


def apply_k_anonymity(
    records: list[dict[str, Any]],
    k_min: float = 10.0,
    count_key: str = "n_eff",
    value_key: str = "sq",
) -> list[dict[str, Any]]:
    """Enforce k-anonymity privacy floor via cell suppression.

    Cells with count < k_min are suppressed (value set to None, suppressed = True).
    Cells with count >= k_min are released (suppressed = False).

    Args:
        records: List of cell or aggregate dictionaries.
        k_min: Minimum effective sample size floor (default 10.0).
        count_key: Key corresponding to effective count (e.g. 'n_eff').
        value_key: Key corresponding to sensitive value (e.g. 'sq').

    Returns:
        Updated list of record dictionaries with suppression flags applied.
    """
    processed: list[dict[str, Any]] = []
    for rec in records:
        out = dict(rec)
        count = out.get(count_key)
        if count is None or count < k_min:
            out[value_key] = None
            out["suppressed"] = True
        else:
            out["suppressed"] = False
        processed.append(out)
    return processed


def add_laplace_noise(
    value: float,
    epsilon: float = 1.0,
    sensitivity: float = 1.0,
    seed: int | None = None,
    rng: random.Random | None = None,
    min_val: float | None = 0.0,
) -> float:
    """Perturb a scalar count using the differential privacy Laplace mechanism.

    Scale parameter b = sensitivity / epsilon.

    Args:
        value: The true aggregate value.
        epsilon: Differential privacy budget (must be strictly > 0).
        sensitivity: L1 sensitivity of the query (default 1.0).
        seed: Optional deterministic random seed.
        rng: Optional random.Random instance.
        min_val: Optional lower bound clamp (e.g. 0.0 for non-negative counts).

    Returns:
        Perturbed value.

    Raises:
        ValueError: If epsilon <= 0 or sensitivity <= 0.
    """
    if epsilon <= 0.0:
        raise ValueError(f"Privacy budget epsilon must be strictly positive, got {epsilon}")
    if sensitivity <= 0.0:
        raise ValueError(f"Sensitivity must be strictly positive, got {sensitivity}")

    if rng is None:
        rng = random.Random(seed)

    scale_b = sensitivity / epsilon
    # Draw Laplace(0, b) noise using exponential distribution with random sign
    u = rng.random()
    sign = 1.0 if u >= 0.5 else -1.0
    exp_sample = rng.expovariate(1.0 / scale_b)
    noise = sign * exp_sample

    perturbed = value + noise
    if min_val is not None:
        perturbed = max(min_val, perturbed)
    return perturbed


def apply_differential_privacy(
    counts: list[float],
    epsilon: float = 1.0,
    sensitivity: float = 1.0,
    seed: int | None = None,
    min_val: float | None = 0.0,
) -> list[float]:
    """Perturb a list of aggregate counts using the Laplace mechanism.

    Args:
        counts: Unperturbed counts.
        epsilon: Differential privacy budget (must be > 0).
        sensitivity: Query sensitivity (default 1.0).
        seed: Random seed for reproducibility.
        min_val: Optional clipping floor.

    Returns:
        List of perturbed counts.
    """
    if epsilon <= 0.0:
        raise ValueError(f"Privacy budget epsilon must be strictly positive, got {epsilon}")
    rng = random.Random(seed)
    return [
        add_laplace_noise(c, epsilon=epsilon, sensitivity=sensitivity, rng=rng, min_val=min_val)
        for c in counts
    ]


def filter_consenting_records(
    records: list[dict[str, Any]],
    consents: dict[str, bool],
    id_key: str = "human_id_pseudonym",
) -> list[dict[str, Any]]:
    """Filter records to strictly retain subjects with active, unrevoked consent.

    Args:
        records: List of dyad, session, or assessment records.
        consents: Mapping of pseudonymous IDs to boolean consent status.
        id_key: Key containing the subject identifier.

    Returns:
        Filtered list containing only records with granted=True consent.
    """
    return [rec for rec in records if consents.get(str(rec.get(id_key, "")), False) is True]
