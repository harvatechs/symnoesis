"""Challenger Stress Test 2: 1,500 Random Variable Input Sets Cross-Language Parity.

Verifies bit-for-bit and mathematical equivalence (within 1e-6) between
Python symnoesis and TypeScript @symnoesis/core across:
- Marginal probabilities
- 256-pixel mass distributions and modal pixels
- HNE, outcomeAvailable flag
- SNE, SNE', operatorBlind flag
- Composite C, Stability S
- Safety gate ceiling, gateStatus, gateTriggered
- SQ (clipped), SQ_raw
- Symbiosis classification (technical_name, public_label, signs, operator_blind_applied)
- Governance zones (primary zone, secondary_tags set)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from symnoesis.assign import compute_dyad_window_masses, get_modal_pixel
from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.gates import evaluate_safety_gate
from symnoesis.grid import parse_pixel_id
from symnoesis.net_effects import compute_composite_c, compute_hne, compute_sne
from symnoesis.sq import compute_sq
from symnoesis.stability import compute_stability_factor
from symnoesis.variables import compute_all_marginal_probabilities
from symnoesis.zones import evaluate_zones


def run_test(num_cases: int = 1500) -> dict[str, object]:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    input_path = script_dir / "parity_inputs.json"
    ts_output_path = script_dir / "parity_outputs_ts.json"

    config = SymnoesisConfig.load_default()
    rng = np.random.default_rng(seed=4242)

    var_names = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]
    chi_candidates = ["CHI-1", "CHI-2", "CHI-3", "CHI-4", "CHI-5", "CHI-6", "CHI-7"]

    test_inputs = []
    py_outputs = []

    print(f"Generating and evaluating {num_cases} test cases in Python...")

    for i in range(num_cases):
        # 1. Posteriors
        posteriors: dict[str, tuple[float, float]] = {}
        for v in var_names:
            mu = float(rng.uniform(-2.0, 2.0))
            # Include values below sigma_floor (0.01)
            sigma = float(rng.uniform(0.001, 1.5))
            posteriors[v] = (mu, sigma)

        # 2. Human scores s_H
        s_h = [float(rng.uniform(0.0, 1.0)) for _ in range(4)]

        # 3. Outcome deltas
        has_outcome = rng.choice([True, False], p=[0.7, 0.3])
        if has_outcome:
            n_deltas = int(rng.integers(1, 6))
            outcome_deltas = [float(rng.uniform(-3.0, 3.0)) for _ in range(n_deltas)]
        else:
            outcome_deltas = None

        # 4. Machine/System scores
        integrity = float(rng.uniform(-1.0, 1.0))
        reliability = float(rng.uniform(-1.0, 1.0))
        has_operator = rng.choice([True, False], p=[0.6, 0.4])
        operator = float(rng.uniform(-1.0, 1.0)) if has_operator else None

        # 5. Stability & Gate parameters
        sigma_c = float(rng.uniform(0.0, 1.0))
        has_chi = int(rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
        confirmed_chi = (
            list(rng.choice(chi_candidates, size=has_chi, replace=False))
            if has_chi > 0
            else None
        )

        has_watch = rng.choice([True, False], p=[0.2, 0.8])
        watch_chi = (
            [str(rng.choice(["CHI-1", "CHI-4"]))] if (has_watch and not confirmed_chi) else None
        )

        n_eff = float(rng.uniform(0.0, 100.0))
        is_trajectory_negative = bool(rng.choice([True, False], p=[0.3, 0.7]))

        # Python evaluation
        p_vars = compute_all_marginal_probabilities(posteriors, config)
        masses = compute_dyad_window_masses(p_vars, config)
        modal_pixel = get_modal_pixel(masses)
        h_bits, m_bits = parse_pixel_id(modal_pixel)

        hne, outcome_avail = compute_hne(s_h, outcome_deltas, config)
        sne, op_blind = compute_sne(integrity, reliability, operator, config)
        c, sne_prime = compute_composite_c(hne, sne, config)

        s = compute_stability_factor(sigma_c, config)
        gate_ceiling, gate_status = evaluate_safety_gate(confirmed_chi, watch_chi, n_eff, config)
        sq, sq_raw, gate_triggered = compute_sq(c, s, gate_ceiling, config)

        sym_class = classify_symbiosis(hne, sne, op_blind, config)
        has_confirmed_bool = confirmed_chi is not None and len(confirmed_chi) > 0
        zone_res = evaluate_zones(
            sq, h_bits, m_bits, has_confirmed_bool, is_trajectory_negative, config
        )

        test_case_input = {
            "id": i,
            "posteriors": {k: [v[0], v[1]] for k, v in posteriors.items()},
            "s_H": s_h,
            "outcome_deltas": outcome_deltas,
            "integrity": integrity,
            "reliability": reliability,
            "operator": operator,
            "sigma_C": sigma_c,
            "confirmed_chi": confirmed_chi,
            "watch_chi": watch_chi,
            "n_eff": n_eff,
            "is_trajectory_negative": is_trajectory_negative,
        }
        test_inputs.append(test_case_input)

        py_outputs.append(
            {
                "id": i,
                "pVars": p_vars,
                "modalPixel": modal_pixel,
                "massCount": len(masses),
                "masses": masses,
                "hne": hne,
                "outcomeAvail": outcome_avail,
                "sne": sne,
                "snePrime": sne_prime,
                "opBlind": op_blind,
                "c": c,
                "s": s,
                "gateCeiling": gate_ceiling,
                "gateStatus": gate_status,
                "sq": sq,
                "sqRaw": sq_raw,
                "gateTriggered": gate_triggered,
                "symClass": {
                    "technical_name": sym_class.technical_name,
                    "public_label": sym_class.public_label,
                    "h_sign": sym_class.h_sign,
                    "s_sign": sym_class.s_sign,
                    "operator_blind_applied": sym_class.operator_blind_applied,
                },
                "zones": {
                    "primary": zone_res.primary,
                    "secondary_tags": sorted(zone_res.secondary_tags),
                },
            }
        )

    # Write inputs for TS worker
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(test_inputs, f)

    # Run TS worker
    print("Running TypeScript worker...")
    node_cmd = ["node", str(script_dir / "challenger_test2_worker.js")]
    res = subprocess.run(node_cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    print("TypeScript worker output:", res.stdout.strip())

    # Load TS outputs
    with open(ts_output_path, encoding="utf-8") as f:
        ts_outputs = json.load(f)

    # Compare Python vs TypeScript
    print("Verifying parity across all metrics...")
    max_diffs: dict[str, float] = {
        "pVars": 0.0,
        "masses": 0.0,
        "hne": 0.0,
        "sne": 0.0,
        "snePrime": 0.0,
        "c": 0.0,
        "s": 0.0,
        "sq": 0.0,
        "sqRaw": 0.0,
        "gateCeiling": 0.0,
    }

    mismatches: list[dict[str, object]] = []

    for idx, (py, ts) in enumerate(zip(py_outputs, ts_outputs, strict=True)):
        assert py["id"] == ts["id"]

        # Marginals
        for v in var_names:
            diff = abs(py["pVars"][v] - ts["pVars"][v])
            if diff > max_diffs["pVars"]:
                max_diffs["pVars"] = diff
            if diff > 1e-6:
                mismatches.append(
                    {
                        "case": idx,
                        "field": f"pVars.{v}",
                        "py": py["pVars"][v],
                        "ts": ts["pVars"][v],
                        "diff": diff,
                    }
                )

        # Modal pixel
        if py["modalPixel"] != ts["modalPixel"]:
            mismatches.append(
                {"case": idx, "field": "modalPixel", "py": py["modalPixel"], "ts": ts["modalPixel"]}
            )

        # Masses comparison on surviving pixels
        for pid, m_py in py["masses"].items():
            if pid in ts["masses"]:
                diff = abs(m_py - ts["masses"][pid])
                if diff > max_diffs["masses"]:
                    max_diffs["masses"] = diff
                if diff > 1e-6:
                    mismatches.append(
                        {
                            "case": idx,
                            "field": f"mass.{pid}",
                            "py": m_py,
                            "ts": ts["masses"][pid],
                            "diff": diff,
                        }
                    )
            else:
                mismatches.append({"case": idx, "field": f"missing_ts_pixel.{pid}"})

        # HNE
        diff = abs(py["hne"] - ts["hne"])
        if diff > max_diffs["hne"]:
            max_diffs["hne"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "hne", "py": py["hne"], "ts": ts["hne"], "diff": diff}
            )
        if py["outcomeAvail"] != ts["outcomeAvail"]:
            mismatches.append(
                {
                    "case": idx,
                    "field": "outcomeAvail",
                    "py": py["outcomeAvail"],
                    "ts": ts["outcomeAvail"],
                }
            )

        # SNE
        diff = abs(py["sne"] - ts["sne"])
        if diff > max_diffs["sne"]:
            max_diffs["sne"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "sne", "py": py["sne"], "ts": ts["sne"], "diff": diff}
            )

        # SNE'
        diff = abs(py["snePrime"] - ts["snePrime"])
        if diff > max_diffs["snePrime"]:
            max_diffs["snePrime"] = diff
        if diff > 1e-6:
            mismatches.append(
                {
                    "case": idx,
                    "field": "snePrime",
                    "py": py["snePrime"],
                    "ts": ts["snePrime"],
                    "diff": diff,
                }
            )

        if py["opBlind"] != ts["opBlind"]:
            mismatches.append(
                {"case": idx, "field": "opBlind", "py": py["opBlind"], "ts": ts["opBlind"]}
            )

        # C
        diff = abs(py["c"] - ts["c"])
        if diff > max_diffs["c"]:
            max_diffs["c"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "c", "py": py["c"], "ts": ts["c"], "diff": diff}
            )

        # S
        diff = abs(py["s"] - ts["s"])
        if diff > max_diffs["s"]:
            max_diffs["s"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "s", "py": py["s"], "ts": ts["s"], "diff": diff}
            )

        # Gate ceiling
        if py["gateCeiling"] is not None and ts["gateCeiling"] is not None:
            diff = abs(py["gateCeiling"] - ts["gateCeiling"])
            if diff > max_diffs["gateCeiling"]:
                max_diffs["gateCeiling"] = diff
            if diff > 1e-6:
                mismatches.append(
                    {
                        "case": idx,
                        "field": "gateCeiling",
                        "py": py["gateCeiling"],
                        "ts": ts["gateCeiling"],
                        "diff": diff,
                    }
                )
        elif py["gateCeiling"] != ts["gateCeiling"]:
            mismatches.append(
                {
                    "case": idx,
                    "field": "gateCeiling",
                    "py": py["gateCeiling"],
                    "ts": ts["gateCeiling"],
                }
            )

        if py["gateStatus"] != ts["gateStatus"]:
            mismatches.append(
                {"case": idx, "field": "gateStatus", "py": py["gateStatus"], "ts": ts["gateStatus"]}
            )

        # SQ
        diff = abs(py["sq"] - ts["sq"])
        if diff > max_diffs["sq"]:
            max_diffs["sq"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "sq", "py": py["sq"], "ts": ts["sq"], "diff": diff}
            )

        # SQ raw
        diff = abs(py["sqRaw"] - ts["sqRaw"])
        if diff > max_diffs["sqRaw"]:
            max_diffs["sqRaw"] = diff
        if diff > 1e-6:
            mismatches.append(
                {"case": idx, "field": "sqRaw", "py": py["sqRaw"], "ts": ts["sqRaw"], "diff": diff}
            )

        if py["gateTriggered"] != ts["gateTriggered"]:
            mismatches.append(
                {
                    "case": idx,
                    "field": "gateTriggered",
                    "py": py["gateTriggered"],
                    "ts": ts["gateTriggered"],
                }
            )

        # Symbiosis Class
        if py["symClass"] != ts["symClass"]:
            mismatches.append(
                {"case": idx, "field": "symClass", "py": py["symClass"], "ts": ts["symClass"]}
            )

        # Governance Zones
        if py["zones"] != ts["zones"]:
            mismatches.append({"case": idx, "field": "zones", "py": py["zones"], "ts": ts["zones"]})

    # Cleanup temporary json files
    if input_path.exists():
        input_path.unlink()
    if ts_output_path.exists():
        ts_output_path.unlink()

    passed = len(mismatches) == 0

    results = {
        "num_cases": num_cases,
        "passed": passed,
        "mismatches_count": len(mismatches),
        "max_diffs": max_diffs,
        "mismatches": mismatches[:20],
    }

    print("\n--- TEST 2 RESULTS ---")
    print(f"Total cases evaluated: {num_cases}")
    print(f"Mismatches found: {len(mismatches)}")
    print("Maximum absolute differences:")
    for metric, diff in max_diffs.items():
        print(f"  {metric:12s}: {diff:.4e} (threshold: 1.0e-6)")
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    # Write summary
    with open(script_dir / "challenger_test2_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    run_test()
