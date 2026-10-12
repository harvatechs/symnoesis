"""Normative Reference Mathematical Oracle for Symnoesis (SYMN-01).

Implements closed-form formulas and normative algorithms directly from SPEC.md.
Used by E2E test suites as an authoritative, independent reference oracle.
Never depends on internal implementation modules.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import NamedTuple

# Canonical Constants from spec/config/symn-01.v0.1.yaml
EFFECT_SCALE = 0.5
SIGMA_FLOOR = 0.01
PRUNE_MASS = 1.0e-4
DELTA_H2 = 0.1
H2_THRESHOLD = 0.420740290560897
W_H = 0.7
W_S = 0.3
SIGMA_MAX = 0.5
CLASS_THRESHOLD = 0.2
Z1_MIN = 60.0
Z2_MIN = 25.0
Z6_MAX = -25.0
MDC_DEFAULT = 5.0
K_MIN = 10

CHI_CEILINGS: dict[str, float] = {
    "CHI-1": 0.0,
    "CHI-2": 0.0,
    "CHI-3": 0.0,
    "CHI-4": 0.25,
    "CHI-5": 0.25,
    "CHI-6": 0.25,
    "CHI-7": 0.25,
}


def normal_cdf_oracle(z: float) -> float:
    """Computes standard normal cumulative distribution function Phi(z)."""
    if math.isnan(z):
        raise ValueError("Input z cannot be NaN")
    # Clamp extreme tails per IEEE-754 and Cody behavior
    if z <= -10.0:
        return 0.0
    if z >= 10.0:
        return 1.0
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def int_to_gray_oracle(k: int) -> int:
    """Computes binary-reflected Gray code: gray(k) = k ^ (k >> 1)."""
    if k < 0:
        raise ValueError(f"k must be non-negative, got {k}")
    return k ^ (k >> 1)


def gray_to_int_oracle(g: int) -> int:
    """Computes exact inverse Gray code recovering k such that int_to_gray(k) == g."""
    if g < 0:
        raise ValueError(f"g must be non-negative, got {g}")
    n = g
    g_shifted = g >> 1
    while g_shifted > 0:
        n ^= g_shifted
        g_shifted >>= 1
    return n


def int_to_bits_oracle(val: int, bit_width: int = 4) -> list[int]:
    """Converts integer to big-endian bit list."""
    if val < 0 or val >= (1 << bit_width):
        raise ValueError(f"Value {val} out of range for {bit_width} bits")
    return [(val >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]


def bits_to_int_oracle(bits: Sequence[int]) -> int:
    """Converts big-endian bit list to integer."""
    val = 0
    for b in bits:
        if b not in (0, 1):
            raise ValueError(f"Bit must be 0 or 1, got {b}")
        val = (val << 1) | b
    return val


def coord_to_pixel_id_oracle(col: int, row: int) -> str:
    """Maps (col, row) in [0..15] to canonical pixel ID h{HHHH}-m{MMMM}."""
    if not (0 <= col < 16 and 0 <= row < 16):
        raise ValueError(f"Coordinates out of bounds: col={col}, row={row}")
    h_gray = int_to_gray_oracle(col)
    m_gray = int_to_gray_oracle(row)
    h_bits = "".join(str(b) for b in int_to_bits_oracle(h_gray, 4))
    m_bits = "".join(str(b) for b in int_to_bits_oracle(m_gray, 4))
    return f"h{h_bits}-m{m_bits}"


def pixel_id_to_coord_oracle(pixel_id: str) -> tuple[int, int]:
    """Parses pixel ID h{HHHH}-m{MMMM} into (col, row)."""
    if len(pixel_id) != 11 or not (pixel_id.startswith("h") and pixel_id[5:7] == "-m"):
        raise ValueError(f"Invalid pixel ID format: {pixel_id}")
    h_str = pixel_id[1:5]
    m_str = pixel_id[7:11]
    if any(c not in "01" for c in h_str + m_str):
        raise ValueError(f"Invalid bits in pixel ID: {pixel_id}")
    h_int = bits_to_int_oracle([int(c) for c in h_str])
    m_int = bits_to_int_oracle([int(c) for c in m_str])
    col = gray_to_int_oracle(h_int)
    row = gray_to_int_oracle(m_int)
    return col, row


def get_grid_neighbors_oracle(col: int, row: int) -> list[tuple[int, int]]:
    """Returns the 4 visual planar grid neighbors with toroidal wrap-around."""
    return [
        ((col - 1) % 16, row),
        ((col + 1) % 16, row),
        (col, (row - 1) % 16),
        (col, (row + 1) % 16),
    ]


def get_all_single_flip_neighbors_oracle(pixel_id: str) -> list[str]:
    """Returns all 8 Hamming-distance 1 neighbors in the 8-cube."""
    if len(pixel_id) != 11:
        raise ValueError(f"Invalid pixel ID: {pixel_id}")
    h_bits = [int(c) for c in pixel_id[1:5]]
    m_bits = [int(c) for c in pixel_id[7:11]]
    neighbors: list[str] = []

    # 4 Human flips
    for i in range(4):
        flipped_h = list(h_bits)
        flipped_h[i] ^= 1
        h_str = "".join(str(b) for b in flipped_h)
        m_str = "".join(str(b) for b in m_bits)
        neighbors.append(f"h{h_str}-m{m_str}")

    # 4 Machine flips
    for j in range(4):
        flipped_m = list(m_bits)
        flipped_m[j] ^= 1
        h_str = "".join(str(b) for b in h_bits)
        m_str = "".join(str(b) for b in flipped_m)
        neighbors.append(f"h{h_str}-m{m_str}")

    return neighbors


def marginal_bit_prob_oracle(mu: float, sigma: float, theta: float) -> float:
    """Computes marginal bit probability p_i = P(s_i >= theta_i) = Phi((mu - theta) / sigma)."""
    sigma_eff = max(sigma, SIGMA_FLOOR)
    return normal_cdf_oracle((mu - theta) / sigma_eff)


def compute_joint_masses_oracle(probs: Sequence[float], prune: bool = True) -> list[float]:
    """Computes joint 256-cell mass distribution from 8 marginal probabilities."""
    if len(probs) != 8:
        raise ValueError(f"Expected 8 probabilities, got {len(probs)}")
    masses = [0.0] * 256
    for c in range(256):
        # Bits ordered H1..H4 (bits 7..4), M1..M4 (bits 3..0)
        p_c = 1.0
        for i in range(8):
            bit = (c >> (7 - i)) & 1
            p_i = probs[i]
            p_c *= p_i if bit == 1 else (1.0 - p_i)
        masses[c] = p_c

    if prune:
        pruned_sum = 0.0
        for c in range(256):
            if masses[c] < PRUNE_MASS:
                masses[c] = 0.0
            else:
                pruned_sum += masses[c]
        if pruned_sum > 0:
            for c in range(256):
                masses[c] /= pruned_sum
    return masses


def hne_state_oracle(s_H: Sequence[float]) -> float:
    """Computes HNE_state = sum_{i=1..4} 0.25 * (2 s_i - 1)."""
    if len(s_H) != 4:
        raise ValueError(f"Expected 4 human variables, got {len(s_H)}")
    return sum(0.25 * (2.0 * s - 1.0) for s in s_H)


def hne_oracle(
    s_H: Sequence[float], outcome_deltas: Sequence[float] | None = None
) -> tuple[float, bool]:
    """Computes composite HNE blending state and outcome deltas."""
    h_state = hne_state_oracle(s_H)
    if not outcome_deltas:
        return h_state, False
    h_outcome = sum(math.tanh(d / 0.5) for d in outcome_deltas) / len(outcome_deltas)
    return 0.5 * h_state + 0.5 * h_outcome, True


def sne_oracle(integrity: float, reliability: float, operator: float) -> float:
    """Computes System Net Effect SNE = 0.4*Integrity + 0.4*Reliability + 0.2*Operator."""
    return 0.4 * integrity + 0.4 * reliability + 0.2 * operator


def non_compensation_oracle(hne: float, sne: float) -> float:
    """Applies non-compensation rule: SNE' = min(SNE, 0) if HNE < 0 else SNE."""
    return min(sne, 0.0) if hne < 0.0 else sne


def composite_c_oracle(hne: float, sne_prime: float, w_h: float = W_H, w_s: float = W_S) -> float:
    """Computes composite index C = (w_h*HNE + w_s*SNE') / (w_h + w_s)."""
    return (w_h * hne + w_s * sne_prime) / (w_h + w_s)


def stability_s_oracle(sigma_c: float, sigma_max: float = SIGMA_MAX) -> float:
    """Computes stability factor S in [0.5, 1.0]."""
    if sigma_c < 0:
        raise ValueError(f"sigma_c cannot be negative: {sigma_c}")
    return 0.5 + 0.5 * (1.0 - min(1.0, sigma_c / sigma_max))


def effective_stability_oracle(c: float, s: float) -> float:
    """Enforces harm asymmetry: S_eff = S if C >= 0 else 1.0."""
    return s if c >= 0.0 else 1.0


def compute_sq_oracle(
    c: float,
    s_eff: float,
    confirmed_chi: str | None = None,
) -> tuple[float, float, bool, float | None]:
    """Computes raw SQ, gated SQ, and gate status."""
    sq_raw = 100.0 * c * s_eff
    if confirmed_chi is not None:
        if confirmed_chi not in CHI_CEILINGS:
            raise ValueError(f"Unknown CHI code: {confirmed_chi}")
        g = CHI_CEILINGS[confirmed_chi]
        ceiling = 100.0 * g
        sq = min(sq_raw, ceiling)
        sq_clipped = max(-100.0, min(100.0, sq))
        return sq_raw, sq_clipped, True, ceiling
    sq_clipped = max(-100.0, min(100.0, sq_raw))
    return sq_raw, sq_clipped, False, None


def sign3_oracle(x: float, threshold: float = CLASS_THRESHOLD) -> int:
    """Computes 3-state sign operator: +1 if x > 0.2, -1 if x < -0.2, else 0."""
    if x > threshold:
        return 1
    if x < -threshold:
        return -1
    return 0


def symbiosis_class_oracle(
    hne: float,
    sne: float,
    operator_blind: bool = False,
) -> tuple[str, str]:
    """Assigns technical and public symbiosis classes."""
    h = sign3_oracle(hne)
    s = sign3_oracle(sne)

    if h == 1 and s == 1:
        return "mutualism", "Mutual benefit"
    if h == 1 and s == 0:
        return "commensalism", "Human benefits"
    if h == 1 and s == -1:
        return "sacrificial", "Human benefits at system cost"
    if h == 0 and s == 1:
        return "inverse_commensalism", "System benefits"
    if h == 0 and s == 0:
        return "neutralism", "Neutral"
    if h == 0 and s == -1:
        return "antagonism", "System harmed"
    if h == -1 and s == 1:
        if operator_blind:
            return "amensalism", "Human harmed"
        return "parasitism", "Human harmed at system gain"
    if h == -1 and s == 0:
        return "amensalism", "Human harmed"
    # h == -1 and s == -1
    return "mutual_harm", "Both harmed"


class ZoneEvaluation(NamedTuple):
    primary: str
    secondary_tags: list[str]


def governance_zones_oracle(
    sq: float | None,
    h_bits: Sequence[int] | None = None,
    m_bits: Sequence[int] | None = None,
    has_confirmed_chi: bool = False,
    is_trajectory_negative: bool = False,
) -> ZoneEvaluation:
    """Evaluates primary zone in strict precedence and collects secondary tags."""
    matches: list[str] = []

    # 1. Z7 Critical
    if has_confirmed_chi:
        matches.append("Z7")

    # 2. Z6 Harm: SQ <= -25
    if sq is not None and sq <= Z6_MAX:
        matches.append("Z6")

    # 3. Z5 Dependence: (H1 == 0 or H4 == 0) and M2 == 0
    if (
        h_bits is not None
        and m_bits is not None
        and len(h_bits) == 4
        and len(m_bits) == 4
        and (h_bits[0] == 0 or h_bits[3] == 0)
        and m_bits[1] == 0
    ):
        matches.append("Z5")

    # 4. Z4 Drift: Trajectory negative
    if is_trajectory_negative:
        matches.append("Z4")

    # 5. Z1 Symbiotic: SQ >= 60, trajectory not negative, gate clear
    if sq is not None and sq >= Z1_MIN and not is_trajectory_negative and not has_confirmed_chi:
        matches.append("Z1")

    # 6. Z2 Productive: 25 <= SQ < 60
    if sq is not None and Z2_MIN <= sq < Z1_MIN:
        matches.append("Z2")

    # 7. Z3 Neutral: -25 < SQ < 25
    if sq is not None and Z6_MAX < sq < Z2_MIN:
        matches.append("Z3")

    precedence = ["Z7", "Z6", "Z5", "Z4", "Z1", "Z2", "Z3"]
    primary = "Z3"
    for z in precedence:
        if z in matches:
            primary = z
            break

    secondary = [z for z in matches if z != primary]
    return ZoneEvaluation(primary=primary, secondary_tags=secondary)


def trajectory_oracle(sq_frames: Sequence[float], mdc: float = MDC_DEFAULT) -> str:
    """Evaluates multi-frame SQ trajectory across consecutive intervals."""
    if len(sq_frames) < 3:
        return "stable"  # Needs at least 3 frames (2 intervals)
    deltas = [sq_frames[i] - sq_frames[i - 1] for i in range(1, len(sq_frames))]

    # Check for two consecutive drops > MDC
    for i in range(len(deltas) - 1):
        if deltas[i] < -mdc and deltas[i + 1] < -mdc:
            return "negative"

    # Check for two consecutive gains > MDC
    for i in range(len(deltas) - 1):
        if deltas[i] > mdc and deltas[i + 1] > mdc:
            return "positive"

    return "stable"
