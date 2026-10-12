"""Challenger Stress Test 1: Cody rational Chebyshev erfc / normalCdf Oracle.

Compares TypeScript Cody erfc and normalCdf against Python scipy.special.ndtr
and scipy.special.erfc across 135,000+ points including uniform random in [-10, 10],
dense clusters around Chebyshev transition thresholds, and extreme tails.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import scipy.special


def run_test() -> dict[str, object]:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    input_path = script_dir / "cody_inputs.bin"
    output_path = script_dir / "cody_outputs.bin"

    rng = np.random.default_rng(seed=1337)

    # 1. 100,000 points uniformly distributed in [-10.0, 10.0]
    p_uniform = rng.uniform(-10.0, 10.0, size=100_000)

    # 2. Boundary clusters (25,000 points total)
    p_zero = rng.uniform(-0.001, 0.001, size=5_000)
    p_thresh_pos = rng.uniform(0.46875 - 0.01, 0.46875 + 0.01, size=5_000)
    p_thresh_neg = rng.uniform(-0.46875 - 0.01, -0.46875 + 0.01, size=5_000)
    p_four_pos = rng.uniform(3.95, 4.05, size=5_000)
    p_four_neg = rng.uniform(-4.05, -3.95, size=5_000)

    # 3. Extreme tails (10,000 points)
    p_tail_neg = rng.uniform(-27.0, -10.0, size=5_000)
    p_tail_pos = rng.uniform(10.0, 27.0, size=5_000)

    # 4. Explicit discrete boundary points
    p_discrete = np.array(
        [
            -26.543,
            26.543,
            -10.0,
            10.0,
            -4.0,
            4.0,
            -0.46875,
            0.46875,
            -1.11e-16,
            1.11e-16,
            0.0,
            -0.0,
            -1.0,
            1.0,
            -2.0,
            2.0,
            -3.0,
            3.0,
            -5.0,
            5.0,
            -8.0,
            8.0,
        ],
        dtype=np.float64,
    )

    all_points = np.concatenate(
        [
            p_uniform,
            p_zero,
            p_thresh_pos,
            p_thresh_neg,
            p_four_pos,
            p_four_neg,
            p_tail_neg,
            p_tail_pos,
            p_discrete,
        ]
    ).astype(np.float64)

    total_count = len(all_points)
    print(f"Total points generated: {total_count}")

    # Write input buffer
    with open(input_path, "wb") as f:
        f.write(all_points.tobytes())

    # Run Node worker
    node_cmd = ["node", str(script_dir / "challenger_test1_worker.js")]
    res = subprocess.run(node_cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    print("Node output:", res.stdout.strip())

    # Read output buffer
    with open(output_path, "rb") as f:
        out_bytes = f.read()

    out_arr = np.frombuffer(out_bytes, dtype=np.float64)
    ts_normal_cdf = out_arr[0::2]
    ts_erfc = out_arr[1::2]

    # Python Oracles
    py_ndtr = scipy.special.ndtr(all_points)
    py_erfc = scipy.special.erfc(all_points)

    # Analysis: normalCdf vs ndtr
    cdf_abs_diff = np.abs(ts_normal_cdf - py_ndtr)
    # Mask out extreme tails where both are 0.0 or 1.0 for rel diff
    denom = np.maximum(np.abs(py_ndtr), 1e-15)
    cdf_rel_diff = cdf_abs_diff / denom

    max_cdf_abs_err = float(np.max(cdf_abs_diff))
    mean_cdf_abs_err = float(np.mean(cdf_abs_diff))
    p99_cdf_abs_err = float(np.percentile(cdf_abs_diff, 99.0))
    p999_cdf_abs_err = float(np.percentile(cdf_abs_diff, 99.9))

    # Analysis: erfc vs scipy.special.erfc
    erfc_abs_diff = np.abs(ts_erfc - py_erfc)
    max_erfc_abs_err = float(np.max(erfc_abs_diff))
    mean_erfc_abs_err = float(np.mean(erfc_abs_diff))

    # Identify worst discrepancies
    worst_indices = np.argsort(cdf_abs_diff)[-10:][::-1]
    worst_cases = []
    for idx in worst_indices:
        worst_cases.append(
            {
                "z": float(all_points[idx]),
                "ts_normal_cdf": float(ts_normal_cdf[idx]),
                "scipy_ndtr": float(py_ndtr[idx]),
                "abs_error": float(cdf_abs_diff[idx]),
                "rel_error": float(cdf_rel_diff[idx]),
            }
        )

    # Cleanup temporary bin files
    if input_path.exists():
        input_path.unlink()
    if output_path.exists():
        output_path.unlink()

    passed = max_cdf_abs_err < 1e-9

    summary = {
        "total_points": total_count,
        "max_cdf_abs_error": max_cdf_abs_err,
        "mean_cdf_abs_error": mean_cdf_abs_err,
        "p99_cdf_abs_error": p99_cdf_abs_err,
        "p999_cdf_abs_error": p999_cdf_abs_err,
        "max_erfc_abs_error": max_erfc_abs_err,
        "mean_erfc_abs_error": mean_erfc_abs_err,
        "passed": passed,
        "tolerance": 1e-9,
        "worst_cases": worst_cases,
    }

    print("\n--- TEST 1 RESULTS ---")
    print(f"Total points tested: {total_count}")
    print(f"Max normalCdf abs error: {max_cdf_abs_err:.4e} (threshold: 1.0e-9)")
    print(f"Mean normalCdf abs error: {mean_cdf_abs_err:.4e}")
    print(f"99.9th percentile error: {p999_cdf_abs_err:.4e}")
    print(f"Max erfc abs error: {max_erfc_abs_err:.4e}")
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    return summary


if __name__ == "__main__":
    result = run_test()
    # Save result to json for record
    script_dir = Path(__file__).resolve().parent
    with open(script_dir / "challenger_test1_results.json", "w") as f:
        json.dump(result, f, indent=2)
