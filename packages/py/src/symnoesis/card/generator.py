"""Symnoesis Card and Run Manifest cryptographic generator.

Normative implementation of SPEC §14:
  - RunManifest: spec version, config hash, git SHA, dependency lock hash,
    judge models, random seeds, dataset hashes, and Ed25519 signature.
  - SymnoesisCard: system ID, domain, evidence tier, overall SQ, zone distribution,
    gate status, cryptographic run manifest.
"""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from pydantic import BaseModel, ConfigDict

from symnoesis.evidence import EvidenceTier


class RunManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest_id: str
    spec_version: str
    config_hash: str
    code_git_sha: str
    dependency_lock_hash: str
    judge_models: list[dict[str, Any]]
    random_seeds: dict[str, int]
    dataset_hashes: dict[str, str]
    signature_ed25519: str


class SymnoesisCard(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    card_id: str
    system_id: str
    domain: str
    spec_version: str
    evidence_tier: EvidenceTier
    overall_sq: float
    zone_distribution: dict[str, float]
    gate_status: str
    run_manifest: RunManifest


def compute_sha256(content: bytes) -> str:
    """Computes SHA-256 hex digest of byte content."""
    return hashlib.sha256(content).hexdigest()


def generate_ed25519_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generates an Ed25519 private/public keypair."""
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def sign_manifest_payload(payload: Mapping[str, Any], private_key: Ed25519PrivateKey) -> str:
    """Signs canonical JSON bytes of payload with Ed25519 private key."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig_bytes = private_key.sign(canonical_json)
    return base64.b64encode(sig_bytes).decode("ascii")


def verify_manifest_signature(
    payload: Mapping[str, Any],
    signature_b64: str,
    public_key: Ed25519PublicKey,
) -> bool:
    """Verifies Ed25519 signature against canonical JSON payload."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig_bytes = base64.b64decode(signature_b64.encode("ascii"))
    try:
        public_key.verify(sig_bytes, canonical_json)
        return True
    except Exception:
        return False


def build_run_manifest(
    manifest_id: str,
    spec_version: str,
    config_bytes: bytes,
    code_git_sha: str,
    lock_bytes: bytes,
    judge_models: list[dict[str, Any]],
    random_seeds: dict[str, int],
    dataset_hashes: dict[str, str],
    private_key: Ed25519PrivateKey,
) -> RunManifest:
    """Constructs a cryptographically signed RunManifest."""
    config_hash = compute_sha256(config_bytes)
    lock_hash = compute_sha256(lock_bytes)

    unsigned_payload = {
        "manifest_id": manifest_id,
        "spec_version": spec_version,
        "config_hash": config_hash,
        "code_git_sha": code_git_sha,
        "dependency_lock_hash": lock_hash,
        "judge_models": judge_models,
        "random_seeds": random_seeds,
        "dataset_hashes": dataset_hashes,
    }

    sig = sign_manifest_payload(unsigned_payload, private_key)

    return RunManifest(
        manifest_id=manifest_id,
        spec_version=spec_version,
        config_hash=config_hash,
        code_git_sha=code_git_sha,
        dependency_lock_hash=lock_hash,
        judge_models=judge_models,
        random_seeds=random_seeds,
        dataset_hashes=dataset_hashes,
        signature_ed25519=sig,
    )


def create_symnoesis_card(
    card_id: str,
    system_id: str,
    domain: str,
    overall_sq: float,
    zone_counts: Mapping[str, float],
    gate_status: str,
    manifest: RunManifest,
    evidence_tier: EvidenceTier = "E1",
) -> SymnoesisCard:
    """Constructs a validated SymnoesisCard with zone percentage distribution."""
    total_zone_mass = sum(zone_counts.values())
    if total_zone_mass <= 0.0:
        distribution = dict.fromkeys(zone_counts, 0.0)
    else:
        distribution = {k: float(v) / total_zone_mass for k, v in zone_counts.items()}

    return SymnoesisCard(
        card_id=card_id,
        system_id=system_id,
        domain=domain,
        spec_version=manifest.spec_version,
        evidence_tier=evidence_tier,
        overall_sq=round(overall_sq, 2),
        zone_distribution=distribution,
        gate_status=gate_status,
        run_manifest=manifest,
    )
