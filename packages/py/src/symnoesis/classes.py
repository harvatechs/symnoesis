"""Ecological symbiosis classes and plain-language public mappings.

Normative implementation of SPEC §8:
  h = sign3(HNE), s = sign3(SNE)
  sign3(x) = '+' if x > 0.2, '-' if x < -0.2 else '0'

Class table:
  (+, +) -> Mutualism (Mutual benefit)
  (+, 0) -> Commensalism (Human benefits)
  (+, -) -> Sacrificial (Human benefits at system cost)
  (0, +) -> Inverse commensalism (System benefits)
  (0, 0) -> Neutralism (Neutral)
  (0, -) -> Antagonism (System harmed)
  (-, +) -> Parasitism (Human harmed at system gain)
  (-, 0) -> Amensalism (Human harmed)
  (-, -) -> Mutual harm (Both harmed)

If operator_blind is True, Parasitism (-, +) MUST NOT be asserted and falls back to
Amensalism (-, 0, 'Human harmed') with caveat.
"""

from __future__ import annotations

from typing import Literal, NamedTuple

from symnoesis.config import SymnoesisConfig

Sign3 = Literal["+", "0", "-"]


class SymbiosisClassResult(NamedTuple):
    technical_name: str
    public_label: str
    h_sign: Sign3
    s_sign: Sign3
    operator_blind_applied: bool


CLASS_MATRIX: dict[tuple[Sign3, Sign3], tuple[str, str]] = {
    ("+", "+"): ("mutualism", "Mutual benefit"),
    ("+", "0"): ("commensalism", "Human benefits"),
    ("+", "-"): ("sacrificial", "Human benefits at system cost"),
    ("0", "+"): ("inverse_commensalism", "System benefits"),
    ("0", "0"): ("neutralism", "Neutral"),
    ("0", "-"): ("antagonism", "System harmed"),
    ("-", "+"): ("parasitism", "Human harmed at system gain"),
    ("-", "0"): ("amensalism", "Human harmed"),
    ("-", "-"): ("mutual_harm", "Both harmed"),
}


def compute_sign3(x: float, threshold: float = 0.2) -> Sign3:
    """Computes 3-way sign with hysteresis threshold."""
    if x > threshold:
        return "+"
    if x < -threshold:
        return "-"
    return "0"


def classify_symbiosis(
    hne: float,
    sne: float,
    operator_blind: bool,
    config: SymnoesisConfig,
) -> SymbiosisClassResult:
    """Classifies dyad or pixel into 9-cell symbiosis matrix."""
    threshold = config.classes.threshold
    h_sign = compute_sign3(hne, threshold)
    s_sign = compute_sign3(sne, threshold)

    effective_s_sign = s_sign
    blind_applied = False

    # SPEC §8 / ADR-0005: Parasitism MUST NOT be asserted when operator_blind is true.
    if operator_blind and h_sign == "-" and s_sign == "+":
        effective_s_sign = "0"
        blind_applied = True

    tech_name, pub_label = CLASS_MATRIX[(h_sign, effective_s_sign)]
    return SymbiosisClassResult(
        technical_name=tech_name,
        public_label=pub_label,
        h_sign=h_sign,
        s_sign=s_sign,
        operator_blind_applied=blind_applied,
    )
