"""Challenger Stress Test 3: Pathological Corner Cases.

Probes boundary conditions and adversarial configurations across Python and TypeScript:
1. Extremely large and small sigma values (at, below, and far below sigma_floor = 0.01, and up to inf)
2. Extreme delta values in outcome tanh scaling ([-1e15, 1e15], near 0, saturations)
3. Exact threshold values (mu == theta, H2 threshold, sign3 class boundaries, zone boundaries)
4. Pruning fallback modal allocation when all pixels have mass < prune_mass (total_surviving <= 0.0)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from symnoesis.assign import compute_dyad_window_masses, get_modal_pixel
from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.net_effects import compute_hne
from symnoesis.variables import (
    compute_h2_threshold,
    compute_marginal_probability,
)
from symnoesis.zones import evaluate_zones


def run_test() -> dict[str, object]:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    input_path = script_dir / "pathological_inputs.json"
    ts_output_path = script_dir / "pathological_outputs_ts.json"

    config = SymnoesisConfig.load_default()

    # -------------------------------------------------------------
    # 1. Sigma corner cases
    # -------------------------------------------------------------
    sigma_cases = []
    test_sigmas = [
        0.01,  # exact floor
        0.009999999,  # just below floor
        0.005,
        0.001,
        1e-6,
        1e-15,
        0.0,
        -1.0,  # negative sigma
        10.0,
        100.0,
        1e6,
        1e15,
    ]
    for idx, sig in enumerate(test_sigmas):
        theta_h1 = config.variables.thresholds["H1"]
        # Above theta, below theta, and at theta
        for dmu in [-0.1, 0.0, 0.1]:
            sigma_cases.append(
                {
                    "id": f"sigma_{idx}_{dmu}",
                    "var_id": "H1",
                    "mu": theta_h1 + dmu,
                    "sigma": sig,
                }
            )

    # -------------------------------------------------------------
    # 2. Delta outcome corner cases
    # -------------------------------------------------------------
    delta_cases = [
        {"id": "delta_huge_neg", "s_H": [0.5, 0.5, 0.5, 0.5], "outcome_deltas": [-1e15]},
        {"id": "delta_huge_pos", "s_H": [0.5, 0.5, 0.5, 0.5], "outcome_deltas": [1e15]},
        {"id": "delta_balanced_huge", "s_H": [0.5, 0.5, 0.5, 0.5], "outcome_deltas": [-1e15, 1e15]},
        {
            "id": "delta_large_array",
            "s_H": [0.8, 0.8, 0.8, 0.8],
            "outcome_deltas": [-1000.0, -500.0, 0.0, 500.0, 1000.0],
        },
        {"id": "delta_zeros", "s_H": [0.3, 0.3, 0.3, 0.3], "outcome_deltas": [0.0, -0.0]},
        {"id": "delta_subnormals", "s_H": [0.6, 0.6, 0.6, 0.6], "outcome_deltas": [-1e-15, 1e-15]},
    ]

    # -------------------------------------------------------------
    # 3. Exact threshold values
    # -------------------------------------------------------------
    # 3a. mu == theta for all 8 variables
    mu_theta_cases = []
    for v in ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"]:
        theta = config.variables.thresholds[v]
        for sig in [0.5, 0.01, 0.001]:
            mu_theta_cases.append(
                {
                    "id": f"mu_theta_{v}_{sig}",
                    "var_id": v,
                    "mu": theta,
                    "sigma": sig,
                }
            )

    # 3b. Class threshold boundaries (-0.2, +0.2)
    class_thresh_cases = []
    test_bounds = [-0.20000001, -0.2, -0.19999999, 0.19999999, 0.2, 0.20000001]
    for h in test_bounds:
        for s in test_bounds:
            for blind in [False, True]:
                class_thresh_cases.append(
                    {
                        "id": f"class_{h}_{s}_{blind}",
                        "hne": h,
                        "sne": s,
                        "operator_blind": blind,
                    }
                )

    # 3c. Zone threshold boundaries (SQ = -25.0, +25.0, +60.0)
    zone_thresh_cases = []
    sq_bounds = [
        -25.000001,
        -25.0,
        -24.999999,
        24.999999,
        25.0,
        25.000001,
        59.999999,
        60.0,
        60.000001,
    ]
    # Test combinations of Z5 dependence bits, CHI, trajectory
    z5_patterns = [
        ([0, 1, 1, 1], [1, 0, 1, 1]),  # h1=0, m2=0 -> Z5 match
        ([1, 1, 1, 0], [1, 0, 1, 1]),  # h4=0, m2=0 -> Z5 match
        ([1, 1, 1, 1], [1, 0, 1, 1]),  # h1=1, h4=1 -> NOT Z5
        ([0, 1, 1, 1], [1, 1, 1, 1]),  # m2=1 -> NOT Z5
    ]
    for sq_val in sq_bounds:
        for has_chi in [False, True]:
            for neg_traj in [False, True]:
                for h_b, m_b in z5_patterns:
                    zone_thresh_cases.append(
                        {
                            "id": f"zone_{sq_val}_{has_chi}_{neg_traj}_{h_b[0]}_{h_b[3]}_{m_b[1]}",
                            "sq": sq_val,
                            "h_bits": h_b,
                            "m_bits": m_b,
                            "has_confirmed_chi": has_chi,
                            "is_trajectory_negative": neg_traj,
                        }
                    )

    # -------------------------------------------------------------
    # 4. Pruning fallback modal allocation (all pixels < prune_mass)
    # -------------------------------------------------------------
    prune_cases = [
        # Case A: Uniform marginals p_i = 0.5. All pixels have mass 1/256 = 0.00390625.
        # Setting prune_mass = 0.005 means ALL 256 pixels are pruned!
        {
            "id": "prune_fallback_uniform",
            "prune_mass": 0.005,
            "p_vars": dict.fromkeys(["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"], 0.5),
        },
        # Case B: Slight gradient where all pixels are still < 0.005, but pixel h1111-m0000 is unique maximum
        {
            "id": "prune_fallback_gradient",
            "prune_mass": 0.005,
            "p_vars": {
                "H1": 0.504,
                "H2": 0.503,
                "H3": 0.502,
                "H4": 0.501,
                "M1": 0.499,
                "M2": 0.498,
                "M3": 0.497,
                "M4": 0.496,
            },
        },
        # Case C: High prune mass 0.99
        {
            "id": "prune_fallback_high_thresh",
            "prune_mass": 0.99,
            "p_vars": {
                "H1": 0.9,
                "H2": 0.9,
                "H3": 0.9,
                "H4": 0.9,
                "M1": 0.9,
                "M2": 0.9,
                "M3": 0.9,
                "M4": 0.9,
            },
        },
    ]

    all_test_inputs = {
        "sigma_cases": sigma_cases,
        "delta_cases": delta_cases,
        "mu_theta_cases": mu_theta_cases,
        "class_thresh_cases": class_thresh_cases,
        "zone_thresh_cases": zone_thresh_cases,
        "prune_cases": prune_cases,
    }

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(all_test_inputs, f, indent=2)

    # Run Python evaluations
    py_results = {}

    # 1. Sigma
    py_sigma = []
    for tc in sigma_cases:
        p = compute_marginal_probability(tc["mu"], tc["sigma"], tc["var_id"], config)
        py_sigma.append({"id": tc["id"], "p": p})
    py_results["sigma"] = py_sigma

    # 2. Delta
    py_delta = []
    for tc in delta_cases:
        hne, outcome_avail = compute_hne(tc["s_H"], tc["outcome_deltas"], config)
        py_delta.append({"id": tc["id"], "hne": hne, "outcomeAvail": outcome_avail})
    py_results["delta"] = py_delta

    # 3. Exact thresholds
    py_mu_theta = []
    for tc in mu_theta_cases:
        p = compute_marginal_probability(tc["mu"], tc["sigma"], tc["var_id"], config)
        py_mu_theta.append({"id": tc["id"], "p": p})
    py_results["mu_theta"] = py_mu_theta

    py_results["h2_threshold"] = compute_h2_threshold(config)

    py_class_thresh = []
    for tc in class_thresh_cases:
        res = classify_symbiosis(tc["hne"], tc["sne"], tc["operator_blind"], config)
        py_class_thresh.append(
            {
                "id": tc["id"],
                "technical_name": res.technical_name,
                "public_label": res.public_label,
                "h_sign": res.h_sign,
                "s_sign": res.s_sign,
                "operator_blind_applied": res.operator_blind_applied,
            }
        )
    py_results["class_thresh"] = py_class_thresh

    py_zone_thresh = []
    for tc in zone_thresh_cases:
        res = evaluate_zones(
            tc["sq"],
            tc["h_bits"],
            tc["m_bits"],
            tc["has_confirmed_chi"],
            tc["is_trajectory_negative"],
            config,
        )
        py_zone_thresh.append(
            {
                "id": tc["id"],
                "primary": res.primary,
                "secondary_tags": sorted(res.secondary_tags),
            }
        )
    py_results["zone_thresh"] = py_zone_thresh

    # 4. Prune fallback
    py_prune = []
    for tc in prune_cases:
        custom_assignment = config.assignment.model_copy(update={"prune_mass": tc["prune_mass"]})
        custom_cfg = config.model_copy(update={"assignment": custom_assignment})
        masses = compute_dyad_window_masses(tc["p_vars"], custom_cfg)
        modal = get_modal_pixel(masses)
        py_prune.append(
            {
                "id": tc["id"],
                "modal": modal,
                "masses": masses,
                "massCount": len(masses),
            }
        )
    py_results["prune"] = py_prune

    # Run TypeScript worker
    print("Running TypeScript worker on pathological cases...")
    node_cmd = ["node", str(script_dir / "challenger_test3_worker.js")]
    res = subprocess.run(node_cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    print("TypeScript worker output:", res.stdout.strip())

    # Load TS outputs
    with open(ts_output_path, encoding="utf-8") as f:
        ts_results = json.load(f)

    # Comparisons and verifications
    mismatches: list[dict[str, object]] = []

    # 1. Compare Sigma cases
    max_sigma_diff = 0.0
    for py, ts in zip(py_results["sigma"], ts_results["sigma"], strict=True):
        diff = abs(py["p"] - ts["p"])
        if diff > max_sigma_diff:
            max_sigma_diff = diff
        if diff > 1e-6:
            mismatches.append(
                {"section": "sigma", "id": py["id"], "diff": diff, "py": py["p"], "ts": ts["p"]}
            )

    # 2. Compare Delta cases
    max_delta_diff = 0.0
    for py, ts in zip(py_results["delta"], ts_results["delta"], strict=True):
        diff = abs(py["hne"] - ts["hne"])
        if diff > max_delta_diff:
            max_delta_diff = diff
        if diff > 1e-6 or py["outcomeAvail"] != ts["outcomeAvail"]:
            mismatches.append(
                {"section": "delta", "id": py["id"], "diff": diff, "py": py, "ts": ts}
            )

    # 3a. Compare mu == theta cases (p must be exactly 0.5!)
    for py, ts in zip(py_results["mu_theta"], ts_results["mu_theta"], strict=True):
        diff = abs(py["p"] - ts["p"])
        if diff > 1e-6:
            mismatches.append({"section": "mu_theta", "id": py["id"], "diff": diff})
        if abs(py["p"] - 0.5) > 1e-6:
            mismatches.append({"section": "mu_theta_not_half", "id": py["id"], "p": py["p"]})

    # 3b. H2 threshold parity
    h2_diff = abs(py_results["h2_threshold"] - ts_results["h2_threshold"])
    if h2_diff > 1e-6:
        mismatches.append({"section": "h2_threshold", "diff": h2_diff})

    # 3c. Class thresholds
    for py, ts in zip(py_results["class_thresh"], ts_results["class_thresh"], strict=True):
        if py != ts:
            mismatches.append({"section": "class_thresh", "id": py["id"], "py": py, "ts": ts})

    # 3d. Zone thresholds
    for py, ts in zip(py_results["zone_thresh"], ts_results["zone_thresh"], strict=True):
        if py != ts:
            mismatches.append({"section": "zone_thresh", "id": py["id"], "py": py, "ts": ts})

    # 4. Prune fallback
    for py, ts in zip(py_results["prune"], ts_results["prune"], strict=True):
        if py["modal"] != ts["modal"]:
            mismatches.append(
                {"section": "prune_modal", "id": py["id"], "py": py["modal"], "ts": ts["modal"]}
            )
        if py["massCount"] != ts["massCount"]:
            mismatches.append(
                {
                    "section": "prune_massCount",
                    "id": py["id"],
                    "py": py["massCount"],
                    "ts": ts["massCount"],
                }
            )
        # Verify fallback assigned mass exactly 1.0 to single modal pixel
        if py["masses"] != {py["modal"]: 1.0} or ts["masses"] != {ts["modal"]: 1.0}:
            mismatches.append(
                {
                    "section": "prune_fallback_mass_not_one",
                    "id": py["id"],
                    "py": py["masses"],
                    "ts": ts["masses"],
                }
            )

    # Cleanup temporary json files
    if input_path.exists():
        input_path.unlink()
    if ts_output_path.exists():
        ts_output_path.unlink()

    passed = len(mismatches) == 0

    results = {
        "passed": passed,
        "mismatches_count": len(mismatches),
        "total_corner_cases": (
            len(sigma_cases)
            + len(delta_cases)
            + len(mu_theta_cases)
            + 1
            + len(class_thresh_cases)
            + len(zone_thresh_cases)
            + len(prune_cases)
        ),
        "max_sigma_diff": max_sigma_diff,
        "max_delta_diff": max_delta_diff,
        "h2_threshold_diff": h2_diff,
        "h2_threshold_val": py_results["h2_threshold"],
        "mismatches": mismatches,
    }

    print("\n--- TEST 3 RESULTS: PATHOLOGICAL CORNER CASES ---")
    print(f"Total corner cases tested: {results['total_corner_cases']}")
    print(f"Sigma cases: {len(sigma_cases)}, Max diff: {max_sigma_diff:.4e}")
    print(f"Delta cases: {len(delta_cases)}, Max diff: {max_delta_diff:.4e}")
    print(f"mu == theta cases: {len(mu_theta_cases)}, All p == 0.5 verified")
    print(f"H2 threshold: {results['h2_threshold_val']:.15f}, Diff: {h2_diff:.4e}")
    print(
        f"Class threshold boundary cases: {len(class_thresh_cases)}, Exact matches: {len(class_thresh_cases)}"
    )
    print(
        f"Zone threshold boundary cases: {len(zone_thresh_cases)}, Exact matches: {len(zone_thresh_cases)}"
    )
    print(
        f"Prune fallback modal cases: {len(prune_cases)}, Exact modal pixel and 1.0 mass verified"
    )
    print(f"Mismatches found: {len(mismatches)}")
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    with open(script_dir / "challenger_test3_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    run_test()
