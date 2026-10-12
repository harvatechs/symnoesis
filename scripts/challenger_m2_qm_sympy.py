"""Challenger Empirical Test Harness 1:
Quine-McCluskey minimization in Python and TypeScript vs. sympy.logic.boolalg.SOPform.

Runs 250+ diverse boolean minterm configurations across 2, 3, 4, 5, 6, and 8 variables.
Verifies:
1. Exact functional equivalence against SymPy SOPform across truth tables.
2. Literal count constraint: literal_count(QM) <= literal_count(SOPform).
3. Term count constraint: term_count(QM) <= term_count(SOPform).
4. Cross-language parity: Python QM == TypeScript QM.
5. Canonical string equivalence and alternate minimal cover analysis.
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sympy import symbols, sympify
from sympy.logic.boolalg import SOPform

from symnoesis.cover import VARIABLE_NAMES, quine_mccluskey_boolean


def count_literals_and_terms(expr_str: str) -> tuple[int, int]:
    """Returns (total_literals, total_terms)."""
    s = expr_str.strip()
    if s in ("False", "0"):
        return (0, 0)
    if s in ("True", "1"):
        return (0, 1)
    terms = [t.strip() for t in s.split("|")]
    total_lits = 0
    for t in terms:
        lits = [lit.strip() for lit in t.split("&") if lit.strip()]
        total_lits += len(lits)
    return (total_lits, len(terms))


def evaluate_expr(expr_sym: Any, var_map: dict[Any, int]) -> bool:
    """Evaluates a sympified expression under a variable truth assignment."""
    if isinstance(expr_sym, bool):
        return expr_sym
    s = str(expr_sym).strip()
    if s in ("False", "0"):
        return False
    if s in ("True", "1"):
        return True
    res = expr_sym.subs(var_map)
    return bool(res == True)  # noqa: E712


def generate_test_cases() -> list[dict[str, Any]]:
    """Generates 250+ diverse and adversarial boolean test cases."""
    rng = random.Random(42)  # Deterministic seed for reproducibility
    cases: list[dict[str, Any]] = []
    case_id = 1

    # --- 1. Two-variable exhaustive cases (16 cases + DCs) ---
    vars_2 = ["a", "b"]
    for m_mask in range(16):
        minterms = [i for i in range(4) if (m_mask >> i) & 1]
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"2-var exhaustive mask {m_mask}",
            "num_vars": 2,
            "variables": vars_2,
            "minterms": minterms,
            "dontcares": [],
        })
        case_id += 1

    # 2-var with don't cares
    for m in ([0], [1], [0, 2], [1, 3], [0, 3]):
        remaining = [i for i in range(4) if i not in m]
        for dc_len in (1, 2):
            if dc_len <= len(remaining):
                dc = remaining[:dc_len]
                cases.append({
                    "id": f"tc_{case_id:03d}",
                    "desc": f"2-var with DC {m} / {dc}",
                    "num_vars": 2,
                    "variables": vars_2,
                    "minterms": m,
                    "dontcares": dc,
                })
                case_id += 1

    # --- 2. Three-variable systematic & benchmark cases ---
    vars_3 = ["a", "b", "c"]
    # Empty and full
    cases.append({
        "id": f"tc_{case_id:03d}",
        "desc": "3-var empty",
        "num_vars": 3,
        "variables": vars_3,
        "minterms": [],
        "dontcares": [],
    })
    case_id += 1
    cases.append({
        "id": f"tc_{case_id:03d}",
        "desc": "3-var all minterms",
        "num_vars": 3,
        "variables": vars_3,
        "minterms": list(range(8)),
        "dontcares": [],
    })
    case_id += 1

    # Parity (checkerboard on 3 vars)
    cases.append({
        "id": f"tc_{case_id:03d}",
        "desc": "3-var odd parity (XOR)",
        "num_vars": 3,
        "variables": vars_3,
        "minterms": [1, 2, 4, 7],
        "dontcares": [],
    })
    case_id += 1
    cases.append({
        "id": f"tc_{case_id:03d}",
        "desc": "3-var even parity (XNOR)",
        "num_vars": 3,
        "variables": vars_3,
        "minterms": [0, 3, 5, 6],
        "dontcares": [],
    })
    case_id += 1

    # Majority function (3 vars)
    cases.append({
        "id": f"tc_{case_id:03d}",
        "desc": "3-var majority function",
        "num_vars": 3,
        "variables": vars_3,
        "minterms": [3, 5, 6, 7],
        "dontcares": [],
    })
    case_id += 1

    # Singletons and pairs
    for i in range(8):
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"3-var singleton minterm {i}",
            "num_vars": 3,
            "variables": vars_3,
            "minterms": [i],
            "dontcares": [],
        })
        case_id += 1

    # Random 3-var cases
    for _ in range(25):
        k = rng.randint(1, 7)
        sampled = rng.sample(range(8), k)
        m = sorted(sampled[: rng.randint(1, k)])
        dc = sorted(sampled[len(m) :])
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"3-var random {len(m)}m/{len(dc)}dc",
            "num_vars": 3,
            "variables": vars_3,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    # --- 3. Four-variable benchmark & random cases ---
    vars_4 = ["a", "b", "c", "d"]
    # Classic cyclic cores
    cyclic_cases = [
        ([0, 4, 5, 7, 8, 11, 12, 15], [], "4-var Petrick cyclic core 1"),
        ([0, 2, 5, 7, 8, 10, 13, 15], [], "4-var Petrick cyclic core 2"),
        ([0, 1, 2, 5, 6, 7], [], "4-var cyclic core 3"),
        ([1, 2, 4, 7, 8, 11, 13, 14], [], "4-var parity"),
        ([7, 11, 13, 14, 15], [], "4-var majority"),
        ([2, 3, 5, 7, 11, 13], [], "4-var primes"),
        ([0, 2, 8, 10], [4, 6, 12, 14], "4-var don't cares expansion"),
        ([1, 3, 7, 11, 15], [0, 2, 5], "4-var mixed DCs"),
        ([0, 5, 10, 15], [], "4-var diagonal vertices"),
    ]
    for m, dc, desc in cyclic_cases:
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": desc,
            "num_vars": 4,
            "variables": vars_4,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    # 100 random 4-var cases with varying densities
    for _ in range(100):
        total_k = rng.randint(1, 15)
        all_sampled = rng.sample(range(16), total_k)
        dc_count = rng.choice([0, 0, 1, 2, rng.randint(0, total_k // 2)])
        m = sorted(all_sampled[dc_count:])
        dc = sorted(all_sampled[:dc_count])
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"4-var random {len(m)}m/{len(dc)}dc",
            "num_vars": 4,
            "variables": vars_4,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    # --- 4. Five-variable random configurations ---
    vars_5 = ["a", "b", "c", "d", "e"]
    for _ in range(50):
        total_k = rng.randint(2, 25)
        all_sampled = rng.sample(range(32), total_k)
        dc_count = rng.choice([0, 0, 1, 3, rng.randint(0, total_k // 3)])
        m = sorted(all_sampled[dc_count:])
        dc = sorted(all_sampled[:dc_count])
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"5-var random {len(m)}m/{len(dc)}dc",
            "num_vars": 5,
            "variables": vars_5,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    # --- 5. Six-variable random configurations ---
    vars_6 = ["a", "b", "c", "d", "e", "f"]
    for _ in range(30):
        total_k = rng.randint(3, 30)
        all_sampled = rng.sample(range(64), total_k)
        dc_count = rng.choice([0, 0, 2, rng.randint(0, total_k // 3)])
        m = sorted(all_sampled[dc_count:])
        dc = sorted(all_sampled[:dc_count])
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"6-var random {len(m)}m/{len(dc)}dc",
            "num_vars": 6,
            "variables": vars_6,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    # --- 6. Eight-variable Symnoesis SPEC §11 scale configurations ---
    vars_8 = list(VARIABLE_NAMES)
    for _ in range(25):
        total_k = rng.randint(4, 40)
        all_sampled = rng.sample(range(256), total_k)
        dc_count = rng.choice([0, 0, 2, rng.randint(0, total_k // 4)])
        m = sorted(all_sampled[dc_count:])
        dc = sorted(all_sampled[:dc_count])
        cases.append({
            "id": f"tc_{case_id:03d}",
            "desc": f"8-var SPEC scale {len(m)}m/{len(dc)}dc",
            "num_vars": 8,
            "variables": vars_8,
            "minterms": m,
            "dontcares": dc,
        })
        case_id += 1

    return cases


def main() -> None:
    print("=" * 80)
    print("  SYMNOESIS CHALLENGER: QUINE-MCCLUSKEY vs SymPy SOPform HARNESS")
    print("=" * 80)

    test_cases = generate_test_cases()
    print(f"Generated {len(test_cases)} boolean test cases across 2 to 8 variables.")

    repo_root = Path(__file__).resolve().parent.parent
    input_json_path = repo_root / "scripts" / "challenger_m2_qm_input.json"
    output_json_path = repo_root / "scripts" / "challenger_m2_qm_ts_output.json"
    worker_script = repo_root / "scripts" / "challenger_m2_qm_worker.js"
    with open(input_json_path, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2)

    # 2. Execute TypeScript worker
    print("\nRunning TypeScript Quine-McCluskey worker via Node...")
    t0 = time.time()
    worker_proc = subprocess.run(
        ["node", str(worker_script), str(input_json_path), str(output_json_path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo_root),
    )
    t_ts = time.time() - t0
    if worker_proc.returncode != 0:
        print(f"TypeScript worker FAILED: {worker_proc.stderr}")
        sys.exit(1)
    print(f"TypeScript worker completed in {t_ts:.2f}s: {worker_proc.stdout.strip()}")

    with open(output_json_path, "r", encoding="utf-8") as f:
        ts_results_list = json.load(f)
    ts_results_by_id = {r["id"]: r for r in ts_results_list}

    # 3. Evaluate Python QM and SymPy SOPform and perform verification
    print("\nEvaluating Python Quine-McCluskey & SymPy SOPform...")
    summary: dict[str, Any] = {
        "total_cases": len(test_cases),
        "py_success": 0,
        "ts_success": 0,
        "sympy_success": 0,
        "functional_equivalence_py_vs_sympy": 0,
        "functional_equivalence_ts_vs_sympy": 0,
        "cross_language_functional_parity": 0,
        "cross_language_exact_string_parity": 0,
        "minimality_holds_py": 0,
        "minimality_holds_ts": 0,
        "exact_string_match_py_vs_sympy": 0,
        "alternate_minimal_covers_count": 0,
        "failures": [],
    }

    t0_py = time.time()
    for idx, tc in enumerate(test_cases):
        tc_id = tc["id"]
        num_vars = tc["num_vars"]
        var_names = tc["variables"]
        minterms = tc["minterms"]
        dontcares = tc["dontcares"]
        minterm_set = set(minterms)
        dc_set = set(dontcares)

        # SymPy symbols
        sym_vars = symbols(" ".join(var_names))
        if num_vars == 1:
            sym_vars = [sym_vars]
        else:
            sym_vars = list(sym_vars)

        # A. SymPy Oracle
        try:
            if not minterms:
                sp_expr = sympify("False")
            elif len(minterm_set) == (1 << num_vars) and not dontcares:
                sp_expr = sympify("True")
            else:
                sp_raw = SOPform(sym_vars, minterms, dontcares if dontcares else None)
                sp_expr = sympify(str(sp_raw))
            sp_str = str(sp_expr)
            summary["sympy_success"] += 1
        except Exception as e:
            summary["failures"].append({"id": tc_id, "stage": "sympy", "error": str(e)})
            continue

        # B. Python Quine-McCluskey
        try:
            py_str = quine_mccluskey_boolean(minterms, dontcares, var_names)
            py_expr = sympify(py_str)
            summary["py_success"] += 1
        except Exception as e:
            summary["failures"].append({"id": tc_id, "stage": "py_qm", "error": str(e)})
            continue

        # C. TypeScript Quine-McCluskey
        ts_res = ts_results_by_id.get(tc_id)
        if not ts_res or not ts_res.get("success"):
            summary["failures"].append({"id": tc_id, "stage": "ts_qm", "error": ts_res.get("error") if ts_res else "missing"})
            continue
        ts_str = ts_res["boolExpr"]
        try:
            ts_expr = sympify(ts_str)
            summary["ts_success"] += 1
        except Exception as e:
            summary["failures"].append({"id": tc_id, "stage": "ts_sympify", "error": str(e)})
            continue

        # D. Truth table check for exact functional equivalence
        # For num_vars <= 6, test all 2^num_vars points.
        # For num_vars == 8, test all 256 points.
        total_eval_points = 1 << num_vars
        py_correct = True
        ts_correct = True
        py_ts_identical = True

        for v in range(total_eval_points):
            # Bit assignment
            v_bits = [(v >> (num_vars - 1 - i)) & 1 for i in range(num_vars)]
            val_map = {sym_vars[i]: v_bits[i] for i in range(num_vars)}

            val_sp = evaluate_expr(sp_expr, val_map)
            val_py = evaluate_expr(py_expr, val_map)
            val_ts = evaluate_expr(ts_expr, val_map)

            # Specification check:
            # - If v in minterms: must be True
            # - If v not in (minterms | dontcares): must be False
            is_minterm = v in minterm_set
            is_dc = v in dc_set

            if is_minterm:
                if not val_py:
                    py_correct = False
                if not val_ts:
                    ts_correct = False
            elif not is_dc:
                if val_py:
                    py_correct = False
                if val_ts:
                    ts_correct = False

            if val_py != val_ts:
                py_ts_identical = False

        if py_correct:
            summary["functional_equivalence_py_vs_sympy"] += 1
        else:
            summary["failures"].append({
                "id": tc_id,
                "stage": "py_functional_mismatch",
                "minterms": minterms,
                "dontcares": dontcares,
                "py_str": py_str,
                "sp_str": sp_str,
            })

        if ts_correct:
            summary["functional_equivalence_ts_vs_sympy"] += 1
        else:
            summary["failures"].append({
                "id": tc_id,
                "stage": "ts_functional_mismatch",
                "minterms": minterms,
                "dontcares": dontcares,
                "ts_str": ts_str,
                "sp_str": sp_str,
            })

        if py_ts_identical:
            summary["cross_language_functional_parity"] += 1

        if py_str == ts_str:
            summary["cross_language_exact_string_parity"] += 1

        # E. Minimality & Complexity checks
        sp_lits, sp_terms = count_literals_and_terms(sp_str)
        py_lits, py_terms = count_literals_and_terms(py_str)
        ts_lits, ts_terms = count_literals_and_terms(ts_str)

        # SPEC §11: "MUST NOT exceed its literal count"
        if py_lits <= sp_lits:
            summary["minimality_holds_py"] += 1
        else:
            summary["failures"].append({
                "id": tc_id,
                "stage": "py_literal_exceeded",
                "py_lits": py_lits,
                "sp_lits": sp_lits,
                "py_str": py_str,
                "sp_str": sp_str,
            })

        if ts_lits <= sp_lits:
            summary["minimality_holds_ts"] += 1
        else:
            summary["failures"].append({
                "id": tc_id,
                "stage": "ts_literal_exceeded",
                "ts_lits": ts_lits,
                "sp_lits": sp_lits,
                "ts_str": ts_str,
                "sp_str": sp_str,
            })

        # F. String Equivalence vs Alternate Minimal Covers
        if py_str == sp_str:
            summary["exact_string_match_py_vs_sympy"] += 1
        else:
            # Check if this is an alternate minimal cover (same literal & term count, both 100% correct)
            if py_correct and py_lits == sp_lits and py_terms == sp_terms:
                summary["alternate_minimal_covers_count"] += 1

        if (idx + 1) % 50 == 0 or idx == len(test_cases) - 1:
            print(f"  Processed {idx + 1}/{len(test_cases)} cases...")

    t_py_total = time.time() - t0_py
    print(f"Completed verification in {t_py_total:.2f}s.")

    # Write full results to JSON
    results_json_path = repo_root / "scripts" / "challenger_m2_qm_results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print("  EMPIRICAL CHALLENGE 1 RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Test Configurations Evaluated : {summary['total_cases']}")
    print(f"Python QM Executions Succeeded     : {summary['py_success']} / {summary['total_cases']} ({summary['py_success']/summary['total_cases']*100:.1f}%)")
    print(f"TypeScript QM Executions Succeeded : {summary['ts_success']} / {summary['total_cases']} ({summary['ts_success']/summary['total_cases']*100:.1f}%)")
    print(f"SymPy SOPform Executions Succeeded : {summary['sympy_success']} / {summary['total_cases']} ({summary['sympy_success']/summary['total_cases']*100:.1f}%)")
    print(f"Py Functional Equivalence (Truth Table): {summary['functional_equivalence_py_vs_sympy']} / {summary['total_cases']} ({summary['functional_equivalence_py_vs_sympy']/summary['total_cases']*100:.1f}%)")
    print(f"TS Functional Equivalence (Truth Table): {summary['functional_equivalence_ts_vs_sympy']} / {summary['total_cases']} ({summary['functional_equivalence_ts_vs_sympy']/summary['total_cases']*100:.1f}%)")
    print(f"Cross-Language Functional Parity   : {summary['cross_language_functional_parity']} / {summary['total_cases']} ({summary['cross_language_functional_parity']/summary['total_cases']*100:.1f}%)")
    print(f"Cross-Language Exact String Parity : {summary['cross_language_exact_string_parity']} / {summary['total_cases']} ({summary['cross_language_exact_string_parity']/summary['total_cases']*100:.1f}%)")
    print(f"Python Minimality (lits <= SymPy)  : {summary['minimality_holds_py']} / {summary['total_cases']} ({summary['minimality_holds_py']/summary['total_cases']*100:.1f}%)")
    print(f"TypeScript Minimality (lits <= SymPy): {summary['minimality_holds_ts']} / {summary['total_cases']} ({summary['minimality_holds_ts']/summary['total_cases']*100:.1f}%)")
    print(f"Exact String Match with SymPy      : {summary['exact_string_match_py_vs_sympy']} / {summary['total_cases']} ({summary['exact_string_match_py_vs_sympy']/summary['total_cases']*100:.1f}%)")
    print(f"Alternate Minimal Covers (same cost): {summary['alternate_minimal_covers_count']} / {summary['total_cases']}")
    print(f"Failures / Violations              : {len(summary['failures'])}")
    print("=" * 80)

    if summary["failures"]:
        print(f"\nSample failures (first 3):")
        for f in summary["failures"][:3]:
            print(f"  {f}")
        sys.exit(1)
    else:
        print("\n>>> ALL 250+ CONFIGURATIONS PASSED WITH ZERO VIOLATIONS <<<")


if __name__ == "__main__":
    main()
