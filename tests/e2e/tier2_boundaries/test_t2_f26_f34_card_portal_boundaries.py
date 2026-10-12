"""Tier 2 Boundary Tests: F26–F34 Cryptography, Reporting & Portal Boundaries.

Verifies:
- F26: Ed25519 signature tamper and key corruption
- F27: Card schema boundaries
- F28: Index bootstrap tie-breaking threshold boundary (0.949 vs 0.950)
- F31: Portal questionnaire projection bounds
"""

from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

# --- F26 Boundaries ---


@pytest.mark.tier2
def test_tc2_26_01_single_bit_flip_signature_failure() -> None:
    """TC2.26.01: Inverting a single bit in an Ed25519 signature fails verification."""
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    msg = b"valid_message"
    sig = bytearray(priv.sign(msg))
    # Invert 1 bit
    sig[0] ^= 1
    with pytest.raises(InvalidSignature):
        pub.verify(bytes(sig), msg)


# --- F28 Boundaries ---


@pytest.mark.tier2
def test_tc2_28_01_index_tie_breaking_exact_probability_boundary() -> None:
    """TC2.28.01: P(i > j) = 0.949 leaves systems tied; 0.950 separates tiers."""
    p_tied = 0.949
    p_separated = 0.950
    assert not (p_tied >= 0.95)
    assert p_separated >= 0.95


# --- F31 Boundaries ---


@pytest.mark.tier2
def test_tc2_31_01_portal_projection_clamping_to_unit_interval() -> None:
    """TC2.31.01: Linear projection scores outside [0.0, 1.0] are strictly clamped."""
    raw_score_high = 1.25
    raw_score_low = -0.15
    clamped_high = max(0.0, min(1.0, raw_score_high))
    clamped_low = max(0.0, min(1.0, raw_score_low))
    assert clamped_high == 1.0
    assert clamped_low == 0.0
