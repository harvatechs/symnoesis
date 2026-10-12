# How-To Guides

Actionable guides for common tasks with Symnoesis.

---

## How to Run Full Gate Verification

To verify all linters, formatting, typecheckers, unit tests, and E2E batteries:

```bash
make verify
```

---

## How to Run Minimal Failure Cover (MFC)

To solve exact set cover via MILP on a harm distribution:

```python
from symnoesis.cover import solve_mfc_milp, CellInput

# Prepare cells with observed effective sample sizes and SQ scores
cells = [
    CellInput(vertex=0, n_eff=25.0, sq=-40.0),
    CellInput(vertex=1, n_eff=15.0, sq=-30.0),
]

solution = solve_mfc_milp(cells)
for rule in solution.selected_rules:
    print(f"Cover Rule: {rule.rule_str} (Purity: {rule.purity:.2f}, Coverage: {rule.coverage:.2f})")
```

---

## How to Generate and Verify a Cryptographic Manifest

```python
from symnoesis.card.generator import (
    generate_ed25519_keypair,
    build_run_manifest,
    verify_manifest_signature,
)

priv_key, pub_key = generate_ed25519_keypair()

manifest = build_run_manifest(
    manifest_id="MAN-001",
    spec_version="0.1.0",
    config_bytes=b"config...",
    code_git_sha="abcd123",
    lock_bytes=b"lock...",
    judge_models=[{"id": "j1"}],
    random_seeds={"sim": 42},
    dataset_hashes={"data/test.json": "hash..."},
    private_key=priv_key,
)

# Verify signature
payload = {
    "manifest_id": manifest.manifest_id,
    "spec_version": manifest.spec_version,
    "config_hash": manifest.config_hash,
    "code_git_sha": manifest.code_git_sha,
    "dependency_lock_hash": manifest.dependency_lock_hash,
    "judge_models": manifest.judge_models,
    "random_seeds": manifest.random_seeds,
    "dataset_hashes": manifest.dataset_hashes,
}
is_valid = verify_manifest_signature(payload, manifest.signature_ed25519, pub_key)
print(f"Manifest Verified: {is_valid}")
```
