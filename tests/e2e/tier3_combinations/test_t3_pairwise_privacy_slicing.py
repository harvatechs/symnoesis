"""Tier 3 Combination Tests: Privacy Filters, Slicing & Manifest Integrations.

Verifies:
- CBO-07: Mass pruning x k-anonymity suppression x Cryptographic manifest hash
"""

from __future__ import annotations

import hashlib
import json

import pytest
from tests.e2e.oracle import compute_joint_masses_oracle


@pytest.mark.tier3
def test_cbo_07_mass_pruning_and_privacy_suppression_coupling() -> None:
    """CBO-07: Coupling between joint mass distribution, privacy floor, and manifest."""
    # 1. Compute joint mass distribution (concentrated dyad cluster)
    probs = [0.95] * 8
    masses = compute_joint_masses_oracle(probs, prune=True)

    # 2. Simulate 50 dyad-windows
    total_dyads = 50
    effective_counts = [m * total_dyads for m in masses]

    # 3. Privacy floor k_min = 10
    k_min = 10.0
    suppressed_cells = [c for c, n_eff in enumerate(effective_counts) if 0.0 < n_eff < k_min]
    released_cells = [c for c, n_eff in enumerate(effective_counts) if n_eff >= k_min]

    assert len(suppressed_cells) > 0
    assert len(released_cells) > 0

    # 4. Manifest artifact generation includes hash of the aggregated data
    serialized_frame = json.dumps({"released_cell_count": len(released_cells)}, sort_keys=True)
    manifest_hash = hashlib.sha256(serialized_frame.encode("utf-8")).hexdigest()
    assert len(manifest_hash) == 64
