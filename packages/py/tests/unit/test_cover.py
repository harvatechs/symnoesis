"""Unit tests for Minimal Failure Cover (MFC) and Quine-McCluskey minimization.

Tests normative requirements of SPEC §11:
- 256 vertices on 8-cube
- Subcube generation (3488 subcubes fixing 1 to 5 literals)
- Harm mass h(c) calculation and thresholding
- Rule purity pi(R) and coverage metrics
- MILP set cover optimization with scipy.optimize.milp and HiGHS
- Quine-McCluskey exact Boolean minimization matching sympy.logic.boolalg.SOPform
"""

from __future__ import annotations

import math

import pytest
from sympy import symbols
from sympy.logic.boolalg import SOPform

from symnoesis.config import SymnoesisConfig
from symnoesis.cover import (
    VARIABLE_NAMES,
    CellInput,
    bits_to_vertex,
    compute_harm_mass,
    compute_rule_purity,
    evaluate_subcube,
    format_rule_string,
    generate_subcubes,
    get_vertices_in_subcube,
    pattern_covers_vertex,
    quine_mccluskey,
    quine_mccluskey_boolean,
    solve_mfc_milp,
    vertex_to_bits,
    vertex_to_pixel_id,
)


@pytest.fixture
def config() -> SymnoesisConfig:
    return SymnoesisConfig.load_default()


def test_vertex_to_bits_bijection() -> None:
    """Verifies all 256 vertices map bijectively to 8-bit tuples."""
    seen: set[tuple[int, ...]] = set()
    for v in range(256):
        bits = vertex_to_bits(v)
        assert len(bits) == 8
        assert bits_to_vertex(bits) == v
        seen.add(bits)
    assert len(seen) == 256

    with pytest.raises(ValueError):
        vertex_to_bits(-1)
    with pytest.raises(ValueError):
        vertex_to_bits(256)
    with pytest.raises(ValueError):
        bits_to_vertex([0, 1, 0])
    with pytest.raises(ValueError):
        bits_to_vertex([0, 1, 0, 1, 0, 1, 0, 2])


def test_vertex_to_pixel_id() -> None:
    """Verifies vertex integer converts to pixel ID string."""
    pid_0 = vertex_to_pixel_id(0)
    assert pid_0 == "h0000-m0000"
    pid_255 = vertex_to_pixel_id(255)
    assert pid_255 == "h1111-m1111"


def test_subcube_enumeration_count() -> None:
    """Verifies subcube count for 8 variables fixing 1 to 5 literals is 3488."""
    expected_count = sum(math.comb(8, L) * (2**L) for L in range(1, 6))
    assert expected_count == 3488
    subcubes = generate_subcubes(min_literals=1, max_literals=5, num_vars=8)
    assert len(subcubes) == 3488

    # Verify coverage vertex count per literal count: 2^(8 - L)
    for L in (1, 2, 3, 4, 5):
        pat = tuple([0] * L + [None] * (8 - L))
        verts = get_vertices_in_subcube(pat)
        assert len(verts) == 2 ** (8 - L)


def test_pattern_covers_vertex() -> None:
    """Verifies pattern matching logic on vertices."""
    pat = (1, 0, None, None, None, None, None, None)
    assert pattern_covers_vertex(pat, (1, 0, 1, 1, 0, 0, 0, 0))
    assert not pattern_covers_vertex(pat, (0, 0, 1, 1, 0, 0, 0, 0))


def test_format_rule_string() -> None:
    """Verifies canonical rule string formatting."""
    assert format_rule_string({}) == "True"
    rule_str = format_rule_string({"M2": 0, "H1": 1})
    assert rule_str == "H1=1 AND M2=0"


def test_harm_mass_calculation(config: SymnoesisConfig) -> None:
    """Verifies harm mass h(c) formula: n_eff * max(0, -SQ) / 100 for SQ <= -25."""
    # Active harm: SQ = -40, n_eff = 50 -> 20.0
    h1 = compute_harm_mass(sq=-40.0, n_eff=50.0, config=config)
    assert abs(h1 - 20.0) < 1e-9

    # Boundary at exactly -25.0: harmful
    h_bound = compute_harm_mass(sq=-25.0, n_eff=100.0, config=config)
    assert abs(h_bound - 25.0) < 1e-9

    # Safe cell: SQ = -24.9 -> zero harm mass
    h_safe = compute_harm_mass(sq=-24.9, n_eff=100.0, config=config)
    assert h_safe == 0.0

    # Positive SQ -> zero harm mass
    assert compute_harm_mass(sq=10.0, n_eff=100.0, config=config) == 0.0

    # Null SQ -> zero harm mass
    assert compute_harm_mass(sq=None, n_eff=100.0, config=config) == 0.0

    # Sparse cell below n_cell_min (10.0) -> zero harm mass
    assert compute_harm_mass(sq=-50.0, n_eff=9.9, config=config) == 0.0


def test_rule_purity_calculation() -> None:
    """Verifies rule purity pi(R) = harmful_n_eff / observed_n_eff."""
    purity = compute_rule_purity(harmful_n_eff=90.0, observed_n_eff=100.0)
    assert abs(purity - 0.90) < 1e-9
    assert compute_rule_purity(harmful_n_eff=0.0, observed_n_eff=0.0) == 0.0


def test_evaluate_subcube(config: SymnoesisConfig) -> None:
    """Verifies evaluation of a single subcube over a synthetic cell map."""
    # Pattern fixing H1=1, H2=0 (covers 64 cells)
    pat = (1, 0, None, None, None, None, None, None)
    verts = get_vertices_in_subcube(pat)

    cell_map: dict[int, CellInput] = {}
    for v in verts[:10]:
        cell_map[v] = CellInput(cell_id=v, sq=-50.0, n_eff=20.0, observed=True)

    rule = evaluate_subcube(pat, cell_map, total_harm_mass=100.0, config=config)
    assert rule.rule_str == "H1=1 AND H2=0"
    assert rule.purity == 1.0
    assert rule.n_eff == 200.0
    assert rule.unobserved_covered == 54  # 64 - 10


def test_solve_mfc_milp_zero_harm() -> None:
    """Verifies zero harm mass dataset returns empty cover rule set."""
    cells = [CellInput(cell_id=v, sq=10.0, n_eff=50.0) for v in range(256)]
    result = solve_mfc_milp(cells)
    assert len(result.rules) == 0
    assert result.total_harm_mass == 0.0
    assert result.solver_status == "zero_harm"


def test_solve_mfc_milp_single_cluster_cover(config: SymnoesisConfig) -> None:
    """Verifies MILP set cover identifies minimal subcube covering harmful cluster."""
    # Create cluster where M2=0 and H3=0 (pattern: * * 0 *  * 0 * *)
    # literals: H3=0 (idx 2), M2=0 (idx 5)
    harmful_pattern = (None, None, 0, None, None, 0, None, None)
    harmful_verts = get_vertices_in_subcube(harmful_pattern)  # 64 cells

    cell_map: dict[int, CellInput] = {}
    for v in range(256):
        if v in harmful_verts:
            cell_map[v] = CellInput(cell_id=v, sq=-40.0, n_eff=15.0, observed=True)
        else:
            cell_map[v] = CellInput(cell_id=v, sq=30.0, n_eff=20.0, observed=True)

    result = solve_mfc_milp(cell_map, config=config)
    assert result.solver_status == "optimal"
    assert len(result.rules) >= 1
    assert result.total_coverage >= 0.85

    # Check that chosen rule covers H3=0 AND M2=0
    rule_strs = [r.rule_str for r in result.rules]
    assert any("H3=0" in s and "M2=0" in s for s in rule_strs)


def test_quine_mccluskey_boolean_reduction() -> None:
    """Verifies Quine-McCluskey exact Boolean reduction against SymPy SOPform."""
    a, b, c, d = symbols("a b c d")

    # TC1.16.01: Minterms 0, 1 (0000, 0001) reduce to ~a & ~b & ~c
    qm_res = quine_mccluskey_boolean([0, 1], None, ["a", "b", "c", "d"])
    sp_res = str(SOPform([a, b, c, d], [0, 1]))
    assert qm_res == sp_res
    assert qm_res == "~a & ~b & ~c"

    # TC1.16.02: Don't-care minterms expand subcubes
    qm_dc = quine_mccluskey_boolean([0], [1], ["a", "b"])
    sp_dc = str(SOPform([a, b], [0], [1]))
    assert qm_dc == sp_dc
    assert qm_dc == "~a"

    # TC1.16.04: 4 minterms reduce to 1 literal
    qm_4 = quine_mccluskey_boolean([0, 1, 2, 3], None, ["a", "b", "c"])
    sp_4 = str(SOPform([a, b, c], [0, 1, 2, 3]))
    assert qm_4 == sp_4
    assert qm_4 == "~a"

    # TC2.16.01: Covering all minterms reduces to True
    qm_all = quine_mccluskey_boolean([0, 1, 2, 3], None, ["a", "b"])
    assert qm_all == "True"

    # Single minterm retains all literals
    qm_single = quine_mccluskey_boolean([0], None, ["a", "b", "c"])
    assert qm_single == "~a & ~b & ~c"

    # Empty minterm list returns False
    assert quine_mccluskey_boolean([], None, ["a", "b"]) == "False"


def test_quine_mccluskey_cover_rules() -> None:
    """Verifies Quine-McCluskey returns valid CoverRule schema objects."""
    rules = quine_mccluskey(minterms=[0, 1, 4, 5], dontcares=None, variables=VARIABLE_NAMES)
    assert len(rules) >= 1
    r = rules[0]
    assert r.purity == 1.0
    assert r.coverage == 1.0
    assert "H1=0" in r.rule_str
    assert isinstance(r.literals, dict)

    assert quine_mccluskey([]) == []


def test_cell_input_properties_and_errors() -> None:
    """Verifies CellInput properties for string pixel ID and boundary checks."""
    c_str = CellInput(cell_id="h0000-m0000", sq=-30.0, n_eff=20.0)
    assert c_str.vertex_idx == 0
    assert c_str.bits == (0, 0, 0, 0, 0, 0, 0, 0)

    with pytest.raises(ValueError):
        _ = CellInput(cell_id=-1).vertex_idx

    with pytest.raises(ValueError):
        _ = CellInput(cell_id=300).vertex_idx


def test_quine_mccluskey_cyclic_core() -> None:
    """Verifies Quine-McCluskey branch-and-bound optimization on cyclic core."""
    minterms = [0, 4, 5, 7, 8, 11, 12, 15]
    vars_4 = ["a", "b", "c", "d"]
    bool_str = quine_mccluskey_boolean(minterms, None, vars_4)
    assert bool_str != "False"
    assert bool_str != "True"


def test_solve_mfc_milp_no_admissible_rules(config: SymnoesisConfig) -> None:
    """Verifies MFC when harmful cells exist but no rule satisfies minimum support."""
    # Only 1 cell with n_eff = 10, but n_rule_min requires 30
    cells = [CellInput(cell_id=0, sq=-50.0, n_eff=10.0, observed=True)]
    res = solve_mfc_milp(cells, config=config)
    assert res.solver_status == "no_admissible_rules"
    assert res.total_coverage == 0.0
