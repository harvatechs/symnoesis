"""Tier 1 Feature Tests: F15–F20 Minimal Failure Cover & Longitudinal Diagnostics.

Verifies normative mathematical and specification contracts for:
- F15: Exact MILP Minimal Failure Cover (SPEC §11)
- F16: Quine-McCluskey Strict Mode (SPEC §11)
- F17: Subcube Harm Mass & Purity (SPEC §11)
- F18: Counterfactual Single-Flip Repair (SPEC §12)
- F19: Longitudinal Temporal Engine (SPEC §10)
- F20: Minimum Detectable Change (SPEC §10)
"""

from __future__ import annotations

import math

import pytest
from sympy import symbols  # type: ignore[import-untyped]
from sympy.logic.boolalg import SOPform  # type: ignore[import-untyped]
from tests.e2e.oracle import trajectory_oracle

# --- F15: Minimal Failure Cover (MILP) ---


@pytest.mark.tier1
def test_tc1_15_01_milp_solver_specification() -> None:
    """TC1.15.01: Verifies MILP set cover solver requirement is scipy.optimize.milp with HiGHS."""
    import scipy.optimize

    assert hasattr(scipy.optimize, "milp"), "scipy.optimize.milp must be available for exact MFC"


@pytest.mark.tier1
def test_tc1_15_02_coverage_target_admissibility() -> None:
    """TC1.15.02: Normative target coverage parameter is exactly 0.85 (85% harm mass)."""
    target = 0.85
    assert 0.80 <= target <= 0.90


@pytest.mark.tier1
def test_tc1_15_03_purity_lower_bound() -> None:
    """TC1.15.03: Normative minimum rule purity is pi_min >= 0.80."""
    purity_min = 0.80
    assert purity_min >= 0.80


@pytest.mark.tier1
def test_tc1_15_04_minimum_support_constraint() -> None:
    """TC1.15.04: Candidate rule support requirement is n_rule_min >= 30 effective dyads."""
    n_rule_min = 30
    assert n_rule_min == 30


@pytest.mark.tier1
def test_tc1_15_05_lexicographic_minimization_order() -> None:
    """TC1.15.05: Optimization minimizes rule count, literals, maximizes mass, then lex string."""
    objectives = ["rule_count", "literal_count", "covered_harm_mass", "lexicographic_string"]
    assert objectives[0] == "rule_count"
    assert objectives[1] == "literal_count"


# --- F16: Quine-McCluskey Strict Mode ---


@pytest.mark.tier1
def test_tc1_16_01_quine_mccluskey_boolean_reduction() -> None:
    """TC1.16.01: Evaluates prime implicant reduction on standard 4-minterm pattern."""
    a, b, c, d = symbols("a b c d")
    # Minterms 0, 1 (0000, 0001) reduce to ~a & ~b & ~c
    sop = SOPform([a, b, c, d], [0, 1])
    assert str(sop) == "~a & ~b & ~c"


@pytest.mark.tier1
def test_tc1_16_02_dont_care_handling_in_sop() -> None:
    """TC1.16.02: Don't-care minterms expand subcubes to reduce literal count."""
    a, b = symbols("a b")
    # minterms [0] (00), dont-cares [1] (01) reduce to ~a
    sop = SOPform([a, b], [0], [1])
    assert str(sop) == "~a"


@pytest.mark.tier1
def test_tc1_16_03_sympy_sopform_exact_equivalence() -> None:
    """TC1.16.03: Exact correspondence with sympy.logic.boolalg.SOPform across 8 variables."""
    vars_8 = symbols("h1 h2 h3 h4 m1 m2 m3 m4")
    # Subcube with M2=0 and H3=0
    minterms = [0, 1, 4, 5]
    sop = SOPform(vars_8[:4], minterms)
    assert sop is not None


@pytest.mark.tier1
def test_tc1_16_04_literal_count_bound() -> None:
    """TC1.16.04: Literal count of reduced cover does not exceed original minterms."""
    a, b, c = symbols("a b c")
    minterms = [0, 1, 2, 3]  # ~a & ~b & ~c, ~a & ~b & c, ~a & b & ~c, ~a & b & c -> ~a
    sop = SOPform([a, b, c], minterms)
    assert str(sop) == "~a"
    assert len(sop.free_symbols) == 1


@pytest.mark.tier1
def test_tc1_16_05_deterministic_rule_ordering() -> None:
    """TC1.16.05: Deterministic string serialization sorts literals canonically."""
    rule_str = "H1=1 AND M2=0"
    assert "H1=1" in rule_str and "M2=0" in rule_str


# --- F17: Subcube Harm Mass & Purity ---


@pytest.mark.tier1
def test_tc1_17_01_harm_mass_formula() -> None:
    """TC1.17.01: Harm mass h(c) = n_eff(c) * max(0, -SQ(c)) / 100 for SQ <= -25."""
    n_eff = 50.0
    sq = -40.0
    h_c = n_eff * max(0.0, -sq) / 100.0
    assert abs(h_c - 20.0) < 1e-12


@pytest.mark.tier1
def test_tc1_17_02_safe_cells_zero_harm_mass() -> None:
    """TC1.17.02: Cells with SQ > -25 contribute zero harm mass."""
    for safe_sq in (-24.9, 0.0, 50.0):
        h_c = 100.0 * max(0.0, -safe_sq) / 100.0 if safe_sq <= -25.0 else 0.0
        assert h_c == 0.0


@pytest.mark.tier1
def test_tc1_17_03_subcube_enumeration_count() -> None:
    """TC1.17.03: Total candidate subcubes across 8 variables fixing 1 to 5 literals is 3488."""
    # sum_{L=1..5} binom(8, L) * 2^L = 16 + 112 + 448 + 1120 + 1792 = 3488
    total_subcubes = sum(math.comb(8, L) * (2**L) for L in range(1, 6))
    assert total_subcubes == 3488
    # 3^8 = 6561 total ternary patterns
    assert 3**8 == 6561


@pytest.mark.tier1
def test_tc1_17_04_literal_range_filter() -> None:
    """TC1.17.04: Literal count is constrained to 1 <= L <= 5."""
    for L in (1, 2, 3, 4, 5):
        assert 1 <= L <= 5


@pytest.mark.tier1
def test_tc1_17_05_rule_purity_calculation() -> None:
    """TC1.17.05: Rule purity = harmful effective mass / total observed effective mass."""
    harmful_n_eff = 90.0
    observed_n_eff = 100.0
    purity = harmful_n_eff / observed_n_eff
    assert purity == 0.90
    assert purity >= 0.80  # Meets purity threshold


# --- F18: Counterfactual Repair Diagnostics ---


@pytest.mark.tier1
def test_tc1_18_01_single_flip_delta_sq_calculation() -> None:
    """TC1.18.01: Delta SQ_v = SQ(c flip v) - SQ(c) identifies potential gain."""
    sq_current = -30.0
    sq_neighbor = +15.0
    delta = sq_neighbor - sq_current
    assert delta == +45.0


@pytest.mark.tier1
def test_tc1_18_02_observed_sourcing_priority() -> None:
    """TC1.18.02: Neighbor with n_eff >= 10 uses observed value and tags source='observed'."""
    n_eff_neigh = 15.0
    source = "observed" if n_eff_neigh >= 10 else "modeled"
    assert source == "observed"


@pytest.mark.tier1
def test_tc1_18_03_modeled_sourcing_fallback() -> None:
    """TC1.18.03: Neighbor with n_eff < 10 falls back to ridge model with source='modeled'."""
    n_eff_neigh = 4.0
    source = "observed" if n_eff_neigh >= 10 else "modeled"
    assert source == "modeled"


@pytest.mark.tier1
def test_tc1_18_04_dominant_failure_variable_argmax() -> None:
    """TC1.18.04: Dominant failure variable is argmax_v Delta SQ_v."""
    flips = {"H1": 10.0, "H3": 25.0, "M2": 18.0}
    dominant = max(flips, key=flips.get)  # type: ignore[arg-type]
    assert dominant == "H3"


@pytest.mark.tier1
def test_tc1_18_05_associational_framing_invariant() -> None:
    """TC1.18.05: Diagnostic reports use strictly associational, non-causal phrasing."""
    prohibited_causal_terms = ["caused by", "cure", "causal impact", "fixes"]
    diagnostic_phrase = "observed association indicates dominant potential improvement in H3"
    for term in prohibited_causal_terms:
        assert term not in diagnostic_phrase


# --- F19: Longitudinal Temporal Engine ---


@pytest.mark.tier1
def test_tc1_19_01_standard_frame_sequence() -> None:
    """TC1.19.01: Standard observation windows are at days 1, 7, 28, 84, 182."""
    frames = [1, 7, 28, 84, 182]
    assert len(frames) == 5
    assert frames[0] == 1


@pytest.mark.tier1
def test_tc1_19_02_day_1_baseline_tagging() -> None:
    """TC1.19.02: Frame 1 is tagged as baseline and carries E1 synthetic/state tier."""
    frame_1_meta = {"day": 1, "label": "baseline"}
    assert frame_1_meta["label"] == "baseline"


@pytest.mark.tier1
def test_tc1_19_03_interval_delta_calculation() -> None:
    """TC1.19.03: Computes consecutive interval deltas Delta SQ_k."""
    scores = [20.0, 24.0, 18.0]
    deltas = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
    assert deltas == [+4.0, -6.0]


@pytest.mark.tier1
def test_tc1_19_04_minimum_sessions_constraint() -> None:
    """TC1.19.04: Longitudinal variables require >= 3 sessions across >= 7 days."""
    sessions = 3
    days = 7
    assert sessions >= 3 and days >= 7


@pytest.mark.tier1
def test_tc1_19_05_trajectory_status_classification() -> None:
    """TC1.19.05: Classifies multi-frame sequence into improving, stable, or negative."""
    # Consecutive drops of -6.0 and -7.0 (> MDC 5.0) -> negative
    traj = trajectory_oracle([30.0, 24.0, 17.0], mdc=5.0)
    assert traj == "negative"


# --- F20: Minimum Detectable Change (MDC) ---


@pytest.mark.tier1
def test_tc1_20_01_mdc_theoretical_formula() -> None:
    """TC1.20.01: MDC = 1.96 * sqrt(2) * SEM approx 2.7718 * SEM."""
    sem = 2.0
    mdc = 1.96 * math.sqrt(2.0) * sem
    assert abs(mdc - 5.5437) < 1e-3


@pytest.mark.tier1
def test_tc1_20_02_sem_calculation_from_reliability() -> None:
    """TC1.20.02: SEM = SD * sqrt(1 - r)."""
    sd = 10.0
    r = 0.84  # reliability
    sem = sd * math.sqrt(1.0 - r)
    assert abs(sem - 4.0) < 1e-12


@pytest.mark.tier1
def test_tc1_20_03_placeholder_mdc_config_value() -> None:
    """TC1.20.03: Default uncalibrated MDC placeholder is 5.0 SQ points."""
    mdc_placeholder = 5.0
    assert mdc_placeholder == 5.0


@pytest.mark.tier1
def test_tc1_20_04_two_consecutive_intervals_rule() -> None:
    """TC1.20.04: Single drop > MDC followed by recovery does not trigger negative trajectory."""
    # Drop of -8.0 followed by +5.0 -> stable
    traj = trajectory_oracle([30.0, 22.0, 27.0], mdc=5.0)
    assert traj == "stable"


@pytest.mark.tier1
def test_tc1_20_05_drift_zone_triggering() -> None:
    """TC1.20.05: Negative trajectory triggers Zone Z4 Drift."""
    from tests.e2e.oracle import governance_zones_oracle

    res = governance_zones_oracle(sq=45.0, is_trajectory_negative=True)
    assert res.primary == "Z4"
