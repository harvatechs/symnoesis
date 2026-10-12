"""Tests for SymnoesisCard and RunManifest generation and verification."""

from symnoesis.card.generator import (
    build_run_manifest,
    create_symnoesis_card,
    generate_ed25519_keypair,
    verify_manifest_signature,
)
from symnoesis.index_tool.engine import compute_index_tier, generate_index_record


def test_card_and_manifest_crypto_lifecycle() -> None:
    priv_key, pub_key = generate_ed25519_keypair()

    manifest = build_run_manifest(
        manifest_id="MAN-2026-001",
        spec_version="0.1.0",
        config_bytes=b"spec_version: '0.1.0'",
        code_git_sha="abcd1234ef5678",
        lock_bytes=b"lock-file-bytes",
        judge_models=[{"model_id": "judge-1", "family": "A"}],
        random_seeds={"simulator": 42},
        dataset_hashes={"data/fixtures/learning.json": "hash123"},
        private_key=priv_key,
    )

    unsigned_payload = {
        "manifest_id": manifest.manifest_id,
        "spec_version": manifest.spec_version,
        "config_hash": manifest.config_hash,
        "code_git_sha": manifest.code_git_sha,
        "dependency_lock_hash": manifest.dependency_lock_hash,
        "judge_models": manifest.judge_models,
        "random_seeds": manifest.random_seeds,
        "dataset_hashes": manifest.dataset_hashes,
    }

    assert verify_manifest_signature(unsigned_payload, manifest.signature_ed25519, pub_key)

    card = create_symnoesis_card(
        card_id="CARD-SYS-01",
        system_id="system-alpha",
        domain="learning",
        overall_sq=45.2,
        zone_counts={"Z1": 10.0, "Z2": 30.0, "Z3": 60.0},
        gate_status="safe",
        manifest=manifest,
        evidence_tier="E1",
    )

    assert card.overall_sq == 45.2
    assert card.zone_distribution["Z2"] == 0.3

    index_record = generate_index_record(card)
    assert index_record.system_id == "system-alpha"
    assert index_record.index_tier == 2  # Overall SQ >= 25.0 and safe
    assert not index_record.certification_eligible  # Requires E3 and Z1 >= 50%


def test_certification_eligibility_tier1() -> None:
    priv_key, _ = generate_ed25519_keypair()
    manifest = build_run_manifest(
        manifest_id="MAN-CERT-01",
        spec_version="0.1.0",
        config_bytes=b"config",
        code_git_sha="sha",
        lock_bytes=b"lock",
        judge_models=[],
        random_seeds={},
        dataset_hashes={},
        private_key=priv_key,
    )

    card_cert = create_symnoesis_card(
        card_id="CARD-CERT-01",
        system_id="system-certified",
        domain="coding",
        overall_sq=72.0,
        zone_counts={"Z1": 80.0, "Z2": 20.0},
        gate_status="safe",
        manifest=manifest,
        evidence_tier="E3",
    )

    tier, eligible = compute_index_tier(card_cert)
    assert tier == 1
    assert eligible is True
