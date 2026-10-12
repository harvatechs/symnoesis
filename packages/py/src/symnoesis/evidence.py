"""Evidence tier definitions and rules.

Normative implementation of SPEC §13:
  E0: Specified only; no data (uncalibrated prototype)
  E1: Synthetic dyads only, or human data without outcome measures
  E2: Pilot human cohort; calibration incomplete
  E3: Preregistered cohorts; reliability bars met; independently replicated
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

EvidenceTier = Literal["E0", "E1", "E2", "E3"]

TIER_ORDER: dict[EvidenceTier, int] = {
    "E0": 0,
    "E1": 1,
    "E2": 2,
    "E3": 3,
}

REVERSE_TIER_ORDER: dict[int, EvidenceTier] = {v: k for k, v in TIER_ORDER.items()}


def minimum_evidence_tier(tiers: Iterable[EvidenceTier]) -> EvidenceTier:
    """Computes minimum evidence tier across components: tier_comp = min(tiers)."""
    tier_list = list(tiers)
    if not tier_list:
        return "E0"
    min_rank = min(TIER_ORDER[t] for t in tier_list)
    return REVERSE_TIER_ORDER[min_rank]


def is_eligible_for_certification(tier: EvidenceTier) -> bool:
    """Returns True if the evidence tier meets or exceeds E3 required for certification."""
    return TIER_ORDER[tier] >= TIER_ORDER["E3"]
