"""Governance zone assignment and precedence pipeline.

Normative implementation of SPEC §9:
  Zones in strict precedence:
    1. Z7 Critical: confirmed CHI event in pixel
    2. Z6 Harm: SQ <= -25
    3. Z5 Dependence: (H1 == 0 or H4 == 0) and M2 == 0 (pixel bits)
    4. Z4 Drift: Trajectory negative
    5. Z1 Symbiotic: SQ >= +60, trajectory not negative, gate clear
    6. Z2 Productive: +25 <= SQ < +60
    7. Z3 Neutral: -25 < SQ < +25

All matching conditions are returned as secondary_tags.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple

from symnoesis.config import SymnoesisConfig


class ZoneResult(NamedTuple):
    primary: str
    secondary_tags: list[str]


def evaluate_zones(
    sq: float | None,
    h_bits: Sequence[int] | None,
    m_bits: Sequence[int] | None,
    has_confirmed_chi: bool,
    is_trajectory_negative: bool,
    config: SymnoesisConfig,
) -> ZoneResult:
    """Evaluates primary governance zone and secondary tags."""
    matches: list[str] = []

    # 1. Z7 Critical
    if has_confirmed_chi:
        matches.append("Z7")

    # 2. Z6 Harm
    if sq is not None and sq <= config.zones.z6_max:
        matches.append("Z6")

    # 3. Z5 Dependence: (H1 == 0 or H4 == 0) and M2 == 0
    if h_bits is not None and m_bits is not None and len(h_bits) == 4 and len(m_bits) == 4:
        h1 = h_bits[0]
        h4 = h_bits[3]
        m2 = m_bits[1]
        if (h1 == 0 or h4 == 0) and m2 == 0:
            matches.append("Z5")

    # 4. Z4 Drift
    if is_trajectory_negative:
        matches.append("Z4")

    # 5. Z1 Symbiotic: SQ >= +60, trajectory not negative
    if sq is not None and sq >= config.zones.z1_min and not is_trajectory_negative:
        matches.append("Z1")

    # 6. Z2 Productive: +25 <= SQ < +60
    if sq is not None and config.zones.z2_min <= sq < config.zones.z1_min:
        matches.append("Z2")

    # 7. Z3 Neutral: -25 < SQ < +25
    if sq is not None and config.zones.z6_max < sq < config.zones.z2_min:
        matches.append("Z3")

    precedence = config.zones.precedence
    primary = "Z3"  # default fallback
    for z in precedence:
        if z in matches:
            primary = z
            break

    secondary = [z for z in matches if z != primary]
    return ZoneResult(primary=primary, secondary_tags=secondary)
