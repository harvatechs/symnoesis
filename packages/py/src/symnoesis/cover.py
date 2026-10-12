"""Minimal Failure Cover (MFC) and Boolean minimization engine.

Normative implementation of SPEC §11:
- 256 vertices on the 8-cube ({0, 1}^8) over (H1, H2, H3, H4, M1, M2, M3, M4).
- Subcube generation/evaluation in {0, 1, *}^8.
- Harm mass h(c) = n_eff(c) * max(0, -SQ(c)) / 100 for harmful cells (SQ <= tau_h).
- Rule purity pi(R) = sum_{harmful} n_eff(c) / sum_{observed} n_eff(c) >= purity_min (0.8).
- Exact set-cover MILP optimization via scipy.optimize.milp with HiGHS solver
  minimizing subcube count subject to coverage >= coverage_target (0.85).
- Quine-McCluskey strict mode matching sympy.logic.boolalg.SOPform output.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, NamedTuple

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from symnoesis.config import SymnoesisConfig
from symnoesis.grid import parse_pixel_id, pixel_id_from_bits

VARIABLE_NAMES: tuple[str, ...] = ("H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4")
VAR_TO_INDEX: dict[str, int] = {name: i for i, name in enumerate(VARIABLE_NAMES)}


class CoverRule(NamedTuple):
    """Normative Cover Rule conforming to spec/schemas/cover_rule.schema.json."""

    rule_str: str
    literals: dict[str, int]
    purity: float
    coverage: float
    harm_mass_covered: float
    n_eff: float
    unobserved_covered: int


@dataclass(frozen=True)
class CellInput:
    """Cell observation input for Minimal Failure Cover evaluation."""

    cell_id: int | str
    sq: float | None = None
    n_eff: float = 0.0
    observed: bool = True

    @property
    def vertex_idx(self) -> int:
        """Integer vertex index in 0..255."""
        if isinstance(self.cell_id, int):
            if not (0 <= self.cell_id < 256):
                raise ValueError(f"cell_id integer must be in [0, 255], got {self.cell_id}")
            return self.cell_id
        # Parse pixel ID string format hXXXX-mYYYY
        h_bits, m_bits = parse_pixel_id(self.cell_id)
        val = 0
        for b in h_bits + m_bits:
            val = (val << 1) | b
        return val

    @property
    def bits(self) -> tuple[int, ...]:
        """8-bit representation (H1, H2, H3, H4, M1, M2, M3, M4)."""
        v = self.vertex_idx
        return tuple((v >> (7 - i)) & 1 for i in range(8))


@dataclass(frozen=True)
class MinimalFailureCoverResult:
    """Complete result of Minimal Failure Cover optimization."""

    rules: list[CoverRule]
    total_harm_mass: float
    covered_harm_mass: float
    total_coverage: float
    solver_status: str
    metadata: dict[str, Any] = field(default_factory=dict)


def vertex_to_bits(v: int) -> tuple[int, ...]:
    """Converts vertex index in [0, 255] to 8 bits."""
    if not (0 <= v < 256):
        raise ValueError(f"Vertex index must be in [0, 255], got {v}")
    return tuple((v >> (7 - i)) & 1 for i in range(8))


def bits_to_vertex(bits: Sequence[int]) -> int:
    """Converts 8 bits to vertex index in [0, 255]."""
    if len(bits) != 8:
        raise ValueError(f"Expected 8 bits, got {len(bits)}")
    val = 0
    for b in bits:
        if b not in (0, 1):
            raise ValueError(f"Bit must be 0 or 1, got {b}")
        val = (val << 1) | b
    return val


def vertex_to_pixel_id(v: int) -> str:
    """Converts vertex index in [0, 255] to pixel ID string hXXXX-mYYYY."""
    bits = vertex_to_bits(v)
    return pixel_id_from_bits(list(bits[:4]), list(bits[4:]))


def compute_harm_mass(
    sq: float | None,
    n_eff: float,
    config: SymnoesisConfig | None = None,
) -> float:
    """Computes harm mass h(c) = n_eff(c) * max(0, -SQ(c)) / 100 for harmful cells.

    SPEC §11:
      Harmful cell: observed (n_eff >= n_cell_min) and SQ <= tau_h (-25.0).
    """
    cfg = config or SymnoesisConfig.load_default()
    if sq is None:
        return 0.0
    if n_eff < cfg.layout.n_cell_min:
        return 0.0
    if sq > cfg.cover.harm_threshold:
        return 0.0
    return float(n_eff * max(0.0, -sq) / 100.0)


def compute_rule_purity(
    harmful_n_eff: float,
    observed_n_eff: float,
) -> float:
    """Computes rule purity pi(R) = sum_{harmful} n_eff(c) / sum_{observed} n_eff(c)."""
    if observed_n_eff <= 0.0:
        return 0.0
    return float(harmful_n_eff / observed_n_eff)


def format_rule_string(literals: dict[str, int]) -> str:
    """Formats literal assignment into canonical rule string.

    Example: {"H1": 1, "M2": 0} -> "H1=1 AND M2=0".
    """
    if not literals:
        return "True"
    # Sort deterministically by canonical variable ordering
    sorted_items = sorted(literals.items(), key=lambda item: VAR_TO_INDEX.get(item[0], 999))
    return " AND ".join(f"{k}={v}" for k, v in sorted_items)


def generate_subcubes(
    min_literals: int = 1,
    max_literals: int = 5,
    num_vars: int = 8,
) -> list[tuple[int | None, ...]]:
    """Generates all subcubes fixing between min_literals and max_literals variables.

    For 8 variables fixing 1 to 5 literals, total is 3488 candidate subcubes.
    """
    subcubes: list[tuple[int | None, ...]] = []
    for L in range(min_literals, max_literals + 1):
        for indices in itertools.combinations(range(num_vars), L):
            for values in itertools.product((0, 1), repeat=L):
                pattern: list[int | None] = [None] * num_vars
                for idx, val in zip(indices, values, strict=True):
                    pattern[idx] = val
                subcubes.append(tuple(pattern))
    return subcubes


def pattern_to_literals(
    pattern: tuple[int | None, ...],
    variables: Sequence[str] = VARIABLE_NAMES,
) -> dict[str, int]:
    """Converts a pattern tuple into a dictionary of literal assignments."""
    return {variables[i]: val for i, val in enumerate(pattern) if val is not None}


def pattern_covers_vertex(
    pattern: tuple[int | None, ...],
    vertex_bits: Sequence[int],
) -> bool:
    """Checks whether a subcube pattern covers the specified vertex bits."""
    return all(p is None or p == b for p, b in zip(pattern, vertex_bits, strict=True))


def get_vertices_in_subcube(pattern: tuple[int | None, ...]) -> list[int]:
    """Returns the list of all 2^(8-L) vertex indices covered by the subcube pattern."""
    unfixed_indices = [i for i, p in enumerate(pattern) if p is None]
    num_unfixed = len(unfixed_indices)
    vertices: list[int] = []

    for comb in itertools.product((0, 1), repeat=num_unfixed):
        bits = list(pattern)
        for idx, val in zip(unfixed_indices, comb, strict=True):
            bits[idx] = val
        vertices.append(bits_to_vertex([int(b) for b in bits]))  # type: ignore[arg-type]

    return sorted(vertices)


def evaluate_subcube(
    pattern: tuple[int | None, ...],
    cell_map: dict[int, CellInput],
    total_harm_mass: float,
    config: SymnoesisConfig | None = None,
) -> CoverRule:
    """Evaluates a candidate subcube pattern on the given cell map."""
    cfg = config or SymnoesisConfig.load_default()
    vertices = get_vertices_in_subcube(pattern)
    literals = pattern_to_literals(pattern)
    rule_str = format_rule_string(literals)

    harm_mass_covered = 0.0
    harmful_n_eff = 0.0
    observed_n_eff = 0.0
    unobserved_count = 0

    for v in vertices:
        cell = cell_map.get(v)
        if cell is None or not cell.observed or cell.n_eff < cfg.layout.n_cell_min:
            unobserved_count += 1
            continue

        observed_n_eff += cell.n_eff
        hm = compute_harm_mass(cell.sq, cell.n_eff, cfg)
        if hm > 0.0:
            harm_mass_covered += hm
            harmful_n_eff += cell.n_eff

    purity = compute_rule_purity(harmful_n_eff, observed_n_eff)
    coverage = (harm_mass_covered / total_harm_mass) if total_harm_mass > 0.0 else 0.0

    return CoverRule(
        rule_str=rule_str,
        literals=literals,
        purity=float(purity),
        coverage=float(coverage),
        harm_mass_covered=float(harm_mass_covered),
        n_eff=float(observed_n_eff),
        unobserved_covered=unobserved_count,
    )


def solve_mfc_milp(
    cells: Sequence[CellInput] | dict[int, CellInput],
    config: SymnoesisConfig | None = None,
) -> MinimalFailureCoverResult:
    """Finds the Minimal Failure Cover via HiGHS MILP optimization.

    SPEC §11:
      1. Cover at least coverage_target (0.85) of total harm mass.
      2. Lexicographically minimize:
         (a) number of rules
         (b) total literals
         (c) maximize covered mass
         (d) lexicographic rule string for determinism.
    """
    cfg = config or SymnoesisConfig.load_default()

    # Index cells by vertex integer [0..255]
    cell_map = cells if isinstance(cells, dict) else {c.vertex_idx: c for c in cells}

    # Identify harmful cells and compute total harm mass
    harmful_cells: dict[int, float] = {}
    for v in range(256):
        cell = cell_map.get(v)
        if cell is not None:
            hm = compute_harm_mass(cell.sq, cell.n_eff, cfg)
            if hm > 0.0:
                harmful_cells[v] = hm

    total_harm_mass = sum(harmful_cells.values())
    if total_harm_mass <= 0.0:
        return MinimalFailureCoverResult(
            rules=[],
            total_harm_mass=0.0,
            covered_harm_mass=0.0,
            total_coverage=1.0,
            solver_status="zero_harm",
            metadata={"admissible_rules_count": 0},
        )

    # Generate all candidate subcubes with 1 <= L <= max_literals
    all_patterns = generate_subcubes(
        min_literals=1,
        max_literals=cfg.cover.max_literals,
        num_vars=8,
    )

    # Filter admissible rules:
    # purity >= purity_min (0.8), observed n_eff >= n_rule_min (30), covers some harm mass
    admissible_rules: list[tuple[CoverRule, list[int], int]] = []
    for pattern in all_patterns:
        rule = evaluate_subcube(pattern, cell_map, total_harm_mass, cfg)
        if (
            rule.purity >= cfg.cover.purity_min
            and rule.n_eff >= cfg.cover.n_rule_min
            and rule.harm_mass_covered > 0.0
        ):
            verts = get_vertices_in_subcube(pattern)
            covered_harmful = [v for v in verts if v in harmful_cells]
            admissible_rules.append((rule, covered_harmful, len(rule.literals)))

    if not admissible_rules:
        return MinimalFailureCoverResult(
            rules=[],
            total_harm_mass=total_harm_mass,
            covered_harm_mass=0.0,
            total_coverage=0.0,
            solver_status="no_admissible_rules",
            metadata={"admissible_rules_count": 0},
        )

    # Sort admissible rules canonically for determinism
    admissible_rules.sort(key=lambda item: (item[2], item[0].rule_str))

    num_rules = len(admissible_rules)
    harmful_list = sorted(harmful_cells.keys())
    num_harmful = len(harmful_list)

    # Decision variables:
    # x_j in {0, 1} for j in 0..num_rules - 1 (selected rule)
    # y_k in [0, 1] for k in 0..num_harmful - 1 (harmful cell covered)
    num_vars = num_rules + num_harmful

    # Objective weights:
    # 1.0 * x_j (minimize rule count)
    # + 1e-3 * L(R_j) * x_j (minimize literal count)
    # + 1e-9 * (j / num_rules) * x_j (deterministic tie-breaking)
    # - 1e-6 * (h(c_k) / total_harm_mass) * y_k (maximize covered harm mass)
    c_obj = np.zeros(num_vars)
    for j, (_rule, _, lit_count) in enumerate(admissible_rules):
        c_obj[j] = 1.0 + 1e-3 * lit_count + 1e-9 * (j / max(1, num_rules))

    for k, v in enumerate(harmful_list):
        h_k = harmful_cells[v]
        c_obj[num_rules + k] = -1e-6 * (h_k / total_harm_mass)

    # Integrality: x_j are binary integers (1), y_k are continuous (0)
    integrality = np.zeros(num_vars, dtype=int)
    integrality[:num_rules] = 1

    # Variable bounds: x_j in [0, 1], y_k in [0, 1]
    lb = np.zeros(num_vars)
    ub = np.ones(num_vars)
    bounds = Bounds(lb=lb, ub=ub)

    # Constraints:
    # 1. Coverage linking: for each harmful cell k: y_k - sum_{j: c_k in R_j} x_j <= 0
    # 2. Target coverage: sum_{k} h(c_k) * y_k >= coverage_target * total_harm_mass
    num_constraints = num_harmful + 1
    A = np.zeros((num_constraints, num_vars))
    lhs = np.full(num_constraints, -np.inf)
    rhs = np.zeros(num_constraints)

    for k, v in enumerate(harmful_list):
        row = k
        A[row, num_rules + k] = 1.0  # + y_k
        for j, (_, covered_verts, _) in enumerate(admissible_rules):
            if v in covered_verts:
                A[row, j] = -1.0  # - x_j
        rhs[row] = 0.0

    # Target coverage constraint row
    target_row = num_harmful
    for k, v in enumerate(harmful_list):
        A[target_row, num_rules + k] = harmful_cells[v]
    target_mass = cfg.cover.coverage_target * total_harm_mass
    lhs[target_row] = target_mass
    rhs[target_row] = np.inf

    constraints = LinearConstraint(A=A, lb=lhs, ub=rhs)

    # Solve MILP with HiGHS
    res = milp(c=c_obj, integrality=integrality, bounds=bounds, constraints=constraints)

    if not res.success or res.x is None:
        # Fallback: if target coverage (0.85) was infeasible with admissible rules,
        # solve with maximal possible coverage relaxation
        lhs[target_row] = 0.0  # relax target constraint to find maximal possible cover
        res = milp(c=c_obj, integrality=integrality, bounds=bounds, constraints=constraints)

    if res.x is None:
        return MinimalFailureCoverResult(
            rules=[],
            total_harm_mass=total_harm_mass,
            covered_harm_mass=0.0,
            total_coverage=0.0,
            solver_status=f"infeasible ({res.status})",
            metadata={"admissible_rules_count": num_rules},
        )

    # Extract chosen rules
    chosen_rules: list[CoverRule] = []
    covered_harmful_set: set[int] = set()

    for j, (rule, covered_verts, _) in enumerate(admissible_rules):
        if res.x[j] > 0.5:
            chosen_rules.append(rule)
            covered_harmful_set.update(covered_verts)

    covered_harm_mass = sum(harmful_cells[v] for v in covered_harmful_set)
    total_coverage = (covered_harm_mass / total_harm_mass) if total_harm_mass > 0.0 else 0.0

    return MinimalFailureCoverResult(
        rules=chosen_rules,
        total_harm_mass=float(total_harm_mass),
        covered_harm_mass=float(covered_harm_mass),
        total_coverage=float(total_coverage),
        solver_status="optimal" if res.success else f"suboptimal ({res.status})",
        metadata={
            "admissible_rules_count": num_rules,
            "covered_harmful_cells": len(covered_harmful_set),
        },
    )


# --- Quine-McCluskey Strict Mode Implementation ---


def quine_mccluskey_boolean(
    minterms: Sequence[int],
    dontcares: Sequence[int] | None = None,
    variables: Sequence[str] | None = None,
) -> str:
    """Computes exact Sum-Of-Products boolean reduction matching sympy.logic.boolalg.SOPform.

    SPEC §11:
      Strict mode (purity_min = 1.0, coverage_target = 1.0, unobserved = don't-care,
      Boolean harm function): reduces to classical Quine-McCluskey minimization.
      It MUST agree functionally with sympy.logic.boolalg.SOPform and MUST NOT
      exceed its literal count.
    """
    minterm_set = set(minterms)
    dc_set = set(dontcares) if dontcares else set()

    if not minterm_set:
        return "False"

    # Determine variable count
    all_vals = minterm_set | dc_set
    max_val = max(all_vals) if all_vals else 0
    if variables is not None:
        num_vars = len(variables)
        var_names = list(variables)
    else:
        # Determine bit width from max minterm
        num_vars = max(1, max_val.bit_length())
        var_names = [chr(ord("a") + i) for i in range(num_vars)]

    if len(minterm_set) == (1 << num_vars) and not dc_set:
        return "True"

    # Run Quine-McCluskey prime implicant generation and reduction
    prime_implicants = _generate_prime_implicants(minterm_set, dc_set, num_vars)
    chosen_pis = _solve_prime_implicant_cover(prime_implicants, minterm_set)

    if not chosen_pis:
        return "False"

    # Format into boolean expression matching SymPy SOPform notation
    terms: list[str] = []
    # Sort chosen PIs deterministically
    sorted_pis = sorted(chosen_pis, key=lambda pi: _format_sop_term(pi, var_names))

    for pi in sorted_pis:
        term_str = _format_sop_term(pi, var_names)
        if term_str == "":
            return "True"
        terms.append(term_str)

    if not terms:
        return "False"
    return " | ".join(terms)


def quine_mccluskey(
    minterms: Sequence[int],
    dontcares: Sequence[int] | None = None,
    variables: Sequence[str] = VARIABLE_NAMES,
) -> list[CoverRule]:
    """Runs Quine-McCluskey strict mode and returns CoverRule objects conforming to schema."""
    minterm_set = set(minterms)
    dc_set = set(dontcares) if dontcares else set()
    num_vars = len(variables)

    if not minterm_set:
        return []

    prime_implicants = _generate_prime_implicants(minterm_set, dc_set, num_vars)
    chosen_pis = _solve_prime_implicant_cover(prime_implicants, minterm_set)

    rules: list[CoverRule] = []
    for pi in sorted(chosen_pis, key=lambda t: _format_rule_term(t, variables)):
        literals: dict[str, int] = {}
        for i, val in enumerate(pi):
            if val != -1:
                literals[variables[i]] = val

        rule_str = format_rule_string(literals)
        rules.append(
            CoverRule(
                rule_str=rule_str,
                literals=literals,
                purity=1.0,
                coverage=1.0,
                harm_mass_covered=float(len(minterm_set)),
                n_eff=float(len(minterm_set)),
                unobserved_covered=len(dc_set),
            )
        )
    return rules


def _int_to_tuple(val: int, num_vars: int) -> tuple[int, ...]:
    return tuple((val >> (num_vars - 1 - i)) & 1 for i in range(num_vars))


def _generate_prime_implicants(
    minterms: set[int],
    dontcares: set[int],
    num_vars: int,
) -> set[tuple[tuple[int, ...], frozenset[int]]]:
    """Generates all prime implicants using Tabulation (Quine-McCluskey step 1).

    Each implicant is represented as a tuple of ints in {0, 1, -1} where -1 is '-'.
    """
    all_terms = minterms | dontcares
    # Map term pattern -> set of covered minterms (only tracking true minterms)
    current_terms: dict[tuple[int, ...], set[int]] = {
        _int_to_tuple(x, num_vars): ({x} if x in minterms else set()) for x in all_terms
    }

    prime_implicants: set[tuple[tuple[int, ...], frozenset[int]]] = set()

    while current_terms:
        next_terms: dict[tuple[int, ...], set[int]] = {}
        combined: set[tuple[int, ...]] = set()
        term_list = list(current_terms.keys())

        # Group terms by count of 1s for efficiency
        groups: dict[int, list[tuple[int, ...]]] = {}
        for t in term_list:
            ones = sum(1 for b in t if b == 1)
            groups.setdefault(ones, []).append(t)

        sorted_groups = sorted(groups.keys())
        for idx in range(len(sorted_groups) - 1):
            g1 = sorted_groups[idx]
            g2 = sorted_groups[idx + 1]
            if g2 != g1 + 1:
                continue
            for t1 in groups[g1]:
                for t2 in groups[g2]:
                    # Check if t1 and t2 differ in exactly one position
                    diff_pos = -1
                    match = True
                    for p in range(num_vars):
                        if t1[p] != t2[p]:
                            if diff_pos == -1 and t1[p] != -1 and t2[p] != -1:
                                diff_pos = p
                            else:
                                match = False
                                break
                    if match and diff_pos != -1:
                        combined.add(t1)
                        combined.add(t2)
                        merged = list(t1)
                        merged[diff_pos] = -1
                        merged_tup = tuple(merged)
                        cov = current_terms[t1] | current_terms[t2]
                        if merged_tup not in next_terms:
                            next_terms[merged_tup] = set()
                        next_terms[merged_tup].update(cov)

        for t, cov in current_terms.items():
            if t not in combined:
                # Only keep prime implicants that cover at least one minterm
                covered_minterms = cov & minterms
                if covered_minterms:
                    prime_implicants.add((t, frozenset(covered_minterms)))

        current_terms = next_terms

    return prime_implicants


def _solve_prime_implicant_cover(
    prime_implicants: set[tuple[tuple[int, ...], frozenset[int]]],
    minterms: set[int],
) -> list[tuple[int, ...]]:
    """Finds the minimum set of prime implicants covering all minterms (Petrick's / Set Cover)."""
    if not minterms or not prime_implicants:
        return []

    uncovered = set(minterms)
    selected_pis: list[tuple[int, ...]] = []
    remaining_pis = list(prime_implicants)

    # Step 1: Identify Essential Prime Implicants (EPIs)
    # A minterm covered by only one PI makes that PI essential
    progress = True
    while progress and uncovered:
        progress = False
        minterm_cov: dict[int, list[tuple[tuple[int, ...], frozenset[int]]]] = {
            m: [] for m in uncovered
        }
        for pi_tup in remaining_pis:
            for m in pi_tup[1]:
                if m in uncovered:
                    minterm_cov[m].append(pi_tup)

        for _m, cov_list in minterm_cov.items():
            if len(cov_list) == 1:
                epi = cov_list[0]
                if epi[0] not in selected_pis:
                    selected_pis.append(epi[0])
                    uncovered.difference_update(epi[1])
                    if epi in remaining_pis:
                        remaining_pis.remove(epi)
                    progress = True
                    break

    if not uncovered:
        return selected_pis

    # Step 2: Branch-and-bound / minimum set-cover for remaining uncovered minterms
    best_cover = _branch_and_bound_cover(remaining_pis, uncovered)
    if best_cover is not None:
        selected_pis.extend(best_cover)

    return selected_pis


def _branch_and_bound_cover(
    pis: list[tuple[tuple[int, ...], frozenset[int]]],
    uncovered: set[int],
) -> list[tuple[int, ...]] | None:
    """Exact branch-and-bound minimum set-cover minimizing PI count, then literals."""
    best_sol: list[tuple[int, ...]] | None = None
    best_score: tuple[int, int] | None = None  # (num_pis, literal_count)

    def search(
        pi_idx: int,
        curr_cov: set[int],
        curr_selected: list[tuple[int, ...]],
        curr_literals: int,
    ) -> None:
        nonlocal best_sol, best_score

        if uncovered.issubset(curr_cov):
            score = (len(curr_selected), curr_literals)
            if best_score is None or score < best_score:
                best_score = score
                best_sol = list(curr_selected)
            return

        if pi_idx >= len(pis):
            return

        # Prune if already worse than best
        if best_score is not None and len(curr_selected) >= best_score[0]:
            return

        # Option A: pick pis[pi_idx]
        pi_pattern, pi_minterms = pis[pi_idx]
        # Only pick if it covers new minterms
        if not (pi_minterms & uncovered).issubset(curr_cov):
            lit_count = sum(1 for b in pi_pattern if b != -1)
            search(
                pi_idx + 1,
                curr_cov | pi_minterms,
                curr_selected + [pi_pattern],
                curr_literals + lit_count,
            )

        # Option B: don't pick pis[pi_idx]
        search(pi_idx + 1, curr_cov, curr_selected, curr_literals)

    search(0, set(), [], 0)
    return best_sol


def _format_sop_term(pattern: tuple[int, ...], var_names: list[str]) -> str:
    """Formats pattern into SymPy-style SOP term (e.g. ~a & ~b & ~c)."""
    literals: list[str] = []
    for i, val in enumerate(pattern):
        if val == 1:
            literals.append(var_names[i])
        elif val == 0:
            literals.append(f"~{var_names[i]}")
    return " & ".join(literals)


def _format_rule_term(pattern: tuple[int, ...], var_names: Sequence[str]) -> str:
    """Formats pattern into Symnoesis rule string (e.g. H1=1 AND M2=0)."""
    literals = {var_names[i]: val for i, val in enumerate(pattern) if val != -1}
    return format_rule_string(literals)
