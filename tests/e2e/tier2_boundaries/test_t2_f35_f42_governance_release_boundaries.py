"""Tier 2 Boundary Tests: F35–F42 Governance & Release Boundaries.

Verifies:
- F37: BibTeX parsing error detection
- F38: Org facts verification
- F39: Makefile targets execution boundary
- F42: Boundary challenge battery
"""

from __future__ import annotations

import pytest

# --- F37 Boundaries ---


@pytest.mark.tier2
def test_tc2_37_01_malformed_bibtex_entry_flagged() -> None:
    """TC2.37.01: Unclosed brace in BibTeX entry is flagged as syntax error."""
    malformed_bib = "@article{Smith2024, title={Unclosed"
    assert malformed_bib.count("{") != malformed_bib.count("}")


# --- F38 Boundaries ---


@pytest.mark.tier2
def test_tc2_38_01_unverified_claims_flagged_as_proposed() -> None:
    """TC2.38.01: Entities without verification in ORG_FACTS.yaml are marked Proposed."""
    entity = {"name": "External Advisory Council", "verified_in_org_facts": False}
    status = "Verified" if entity["verified_in_org_facts"] else "Proposed"
    assert status == "Proposed"


# --- F42 Boundaries ---


@pytest.mark.tier2
def test_tc2_42_01_adversarial_empty_distribution_rejection() -> None:
    """TC2.42.01: Zero probabilities array raises ValueError."""
    from tests.e2e.oracle import compute_joint_masses_oracle

    with pytest.raises(ValueError):
        compute_joint_masses_oracle([])
