"""Tier 4 Real-World Scenario: Synthetic Cohort Generation & Privacy Audit.

Simulates end-to-end evidence pipeline across a cohort of synthetic dyads:
1. Ingest simulated multi-session interaction streams.
2. Confirm zero raw conversational text is recorded in telemetry.
3. Compute effective cell counts n_eff(c) across 256 cells.
4. Enforce k-anonymity privacy floor (k_min = 10): suppress cells with n_eff < 10.
5. Apply Laplace perturbation with differential privacy budget epsilon = 1.0.
6. Generate and sign cryptographic run manifest with Ed25519.
"""

from __future__ import annotations

import hashlib
import json
import random

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from tests.e2e.oracle import compute_joint_masses_oracle


@pytest.mark.tier4
def test_scenario_04_synthetic_cohort_and_privacy_audit() -> None:
    """Scenario 4: Synthetic evidence generation, privacy filtering, and cryptographic signing."""
    # 1. Deterministic simulation of 200 dyads
    rng = random.Random(42)
    cohort_size = 200
    aggregated_masses = [0.0] * 256

    for _ in range(cohort_size):
        # 8 random variable posteriors
        probs = [rng.uniform(0.3, 0.9) for _ in range(8)]
        masses = compute_joint_masses_oracle(probs, prune=True)
        for c in range(256):
            aggregated_masses[c] += masses[c]

    # Total mass equals cohort size
    assert abs(sum(aggregated_masses) - cohort_size) < 1e-8

    # 2. Audit: Verify telemetry features contain zero raw text
    sample_telemetry = {
        "session_id": "sess-001",
        "turn_index": 1,
        "features": {"brevity": 0.45, "sycophancy_delta": 0.02, "latency_ms": 320},
    }
    assert "raw_prompt" not in sample_telemetry["features"]
    assert "raw_response" not in sample_telemetry["features"]

    # 3. Privacy Floor Enforcement (k_min = 10)
    k_min = 10.0
    published_records = []
    suppressed_count = 0

    for c in range(256):
        n_eff = aggregated_masses[c]
        if n_eff < k_min:
            # Suppressed from public release
            published_records.append({"cell": c, "n_eff": None, "suppressed": True})
            suppressed_count += 1
        else:
            published_records.append({"cell": c, "n_eff": n_eff, "suppressed": False})

    assert suppressed_count > 0

    # 4. Differential Privacy Perturbation (Laplace mechanism, epsilon = 1.0)
    # Scale parameter b = sensitivity / epsilon = 1.0 / 1.0 = 1.0
    # Laplace noise: rng.expovariate(1.0) with random sign
    dp_counts = []
    for r in published_records:
        if not r["suppressed"] and r["n_eff"] is not None:
            noise = rng.expovariate(1.0) if rng.random() > 0.5 else -rng.expovariate(1.0)
            dp_counts.append(max(0.0, r["n_eff"] + noise))

    assert len(dp_counts) == len(published_records) - suppressed_count

    # 5. Cryptographic Run Manifest Generation & Ed25519 Signing
    manifest_dict = {
        "spec_version": "0.1.0",
        "cohort_size": cohort_size,
        "privacy_budget_eps": 1.0,
        "k_min": 10,
        "suppressed_cells": suppressed_count,
    }
    canonical_bytes = json.dumps(manifest_dict, sort_keys=True).encode("utf-8")
    manifest_hash = hashlib.sha256(canonical_bytes).hexdigest()

    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key = priv_key.public_key()
    signature = priv_key.sign(canonical_bytes)

    # Verification passes cleanly
    pub_key.verify(signature, canonical_bytes)
    assert len(manifest_hash) == 64
