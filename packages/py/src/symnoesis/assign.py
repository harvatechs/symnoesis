"""Probabilistic pixel assignment pipeline across the 256-pixel manifold.

Normative implementation of SPEC §3:
  m(c) = Π_i [ p_i if bit_i(c) == 1 else 1 - p_i ]
  Prune m(c) < prune_mass (default 1e-4) and renormalize remainder.
  Modal pixel = argmax_c m(c).
"""

from __future__ import annotations

from collections.abc import Mapping

from symnoesis.config import SymnoesisConfig
from symnoesis.grid import PixelCoord, coord_to_pixel_id, parse_pixel_id


def compute_dyad_window_masses(
    p_vars: Mapping[str, float],
    config: SymnoesisConfig,
) -> dict[str, float]:
    """Computes pruned and renormalized mass distribution m(c) over 256 pixels.

    p_vars must supply marginal probabilities for H1..H4 and M1..M4.
    """
    ordered_vars = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]
    for v in ordered_vars:
        if v not in p_vars:
            raise ValueError(f"Missing probability for variable {v}")

    p_list = [p_vars[v] for v in ordered_vars]

    # Compute unpruned masses for all 256 pixels
    raw_masses: dict[str, float] = {}
    for row in range(16):
        for col in range(16):
            pid = coord_to_pixel_id(PixelCoord(col=col, row=row))
            h_bits, m_bits = parse_pixel_id(pid)
            bits = h_bits + m_bits

            mass = 1.0
            for bit, p in zip(bits, p_list, strict=True):
                factor = p if bit == 1 else (1.0 - p)
                mass *= factor
            raw_masses[pid] = mass

    prune_threshold = config.assignment.prune_mass
    filtered = {pid: m for pid, m in raw_masses.items() if m >= prune_threshold}

    total_surviving = sum(filtered.values())
    if total_surviving <= 0.0:
        # Fallback to modal if extreme edge case
        modal_pid = max(raw_masses.keys(), key=lambda k: raw_masses[k])
        return {modal_pid: 1.0}

    # Renormalize
    return {pid: m / total_surviving for pid, m in filtered.items()}


def get_modal_pixel(pixel_masses: Mapping[str, float]) -> str:
    """Finds the modal pixel (argmax_c m(c))."""
    if not pixel_masses:
        raise ValueError("Cannot find modal pixel of empty mass mapping")
    return max(pixel_masses.keys(), key=lambda k: pixel_masses[k])
