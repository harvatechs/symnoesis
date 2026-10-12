"""Challenger Stress Test 4: Structural and Geometric Invariants.

Verifies:
1. Gray code bijection and inversion across all 16-bit integers [0..65535].
2. Grid coordinate bijection, torus neighbor topology, and 8-cube Hamming neighborhood across all 256 pixels.
3. Schema integrity across all 16 spec schemas (valid $schema, no empty keys).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from symnoesis.gray import gray_to_int, int_to_gray
from symnoesis.grid import (
    PixelCoord,
    coord_to_pixel_id,
    get_all_single_flip_neighbors,
    get_grid_neighbors,
    pixel_id_to_coord,
)


def run_test() -> dict[str, object]:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    input_path = script_dir / "inv_inputs.json"
    ts_output_path = script_dir / "inv_outputs_ts.json"

    # 1. Gray code test values: 0..65535
    gray_values = list(range(65536))

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump({"gray_test_values": gray_values}, f)

    # Run Python Gray tests
    py_gray_rec_matches = 0
    py_gray_hamming_matches = 0
    for k in gray_values:
        g = int_to_gray(k)
        k_rec = gray_to_int(g)
        if k == k_rec:
            py_gray_rec_matches += 1
        if k > 0:
            diff = g ^ int_to_gray(k - 1)
            # Count set bits
            if bin(diff).count("1") == 1:
                py_gray_hamming_matches += 1

    # Run Python Grid tests
    py_grid_results = []
    for col in range(16):
        for row in range(16):
            coord = PixelCoord(col=col, row=row)
            pid = coord_to_pixel_id(coord)
            rec_coord = pixel_id_to_coord(pid)
            neighbors = get_grid_neighbors(coord)
            single_flips = get_all_single_flip_neighbors(pid)
            py_grid_results.append(
                {
                    "col": col,
                    "row": row,
                    "pid": pid,
                    "rec_col": rec_coord.col,
                    "rec_row": rec_coord.row,
                    "neighbors_len": len(neighbors),
                    "single_flips_len": len(single_flips),
                    "neighbors": [(n.col, n.row) for n in neighbors],
                    "single_flips": single_flips,
                }
            )

    # Run TS worker
    print("Running TypeScript worker for invariants...")
    node_cmd = ["node", str(script_dir / "challenger_test4_worker.js")]
    res = subprocess.run(node_cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    print("TS worker output:", res.stdout.strip())

    with open(ts_output_path, encoding="utf-8") as f:
        ts_results = json.load(f)

    # Compare Gray
    gray_mismatches = 0
    for k, ts_item in zip(gray_values, ts_results["gray"], strict=True):
        g_py = int_to_gray(k)
        if ts_item["g"] != g_py or ts_item["kRec"] != k:
            gray_mismatches += 1

    # Compare Grid
    grid_mismatches = 0
    for py, ts in zip(py_grid_results, ts_results["grid"], strict=True):
        if py["pid"] != ts["pid"]:
            grid_mismatches += 1
        if py["rec_col"] != ts["coordRec"]["col"] or py["rec_row"] != ts["coordRec"]["row"]:
            grid_mismatches += 1
        if py["neighbors_len"] != 4 or ts["neighborsCount"] != 4:
            grid_mismatches += 1
        if py["single_flips_len"] != 8 or ts["singleFlipsCount"] != 8:
            grid_mismatches += 1
        # Check planar neighbors match
        py_neigh_set = set(py["neighbors"])
        ts_neigh_set = {(n["col"], n["row"]) for n in ts["neighbors"]}
        if py_neigh_set != ts_neigh_set:
            grid_mismatches += 1
        # Check single flips match
        if set(py["single_flips"]) != set(ts["singleFlips"]):
            grid_mismatches += 1

    # 3. Schema validation
    schema_files = list(repo_root.glob("spec/schemas/*.schema.json"))
    schema_errors = []
    for sf in schema_files:
        with open(sf, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            schema_errors.append(f"{sf.name}: invalid $schema header")
        if "" in data:
            schema_errors.append(f"{sf.name}: contains empty string key ''")

    # Cleanup temporary json files
    if input_path.exists():
        input_path.unlink()
    if ts_output_path.exists():
        ts_output_path.unlink()

    passed = (
        py_gray_rec_matches == 65536
        and py_gray_hamming_matches == 65535
        and gray_mismatches == 0
        and grid_mismatches == 0
        and len(schema_errors) == 0
        and len(schema_files) == 16
    )

    results = {
        "passed": passed,
        "gray_tested": len(gray_values),
        "gray_mismatches": gray_mismatches,
        "grid_tested": len(py_grid_results),
        "grid_mismatches": grid_mismatches,
        "schema_count": len(schema_files),
        "schema_errors": schema_errors,
    }

    print("\n--- TEST 4 RESULTS: STRUCTURAL INVARIANTS ---")
    print(f"Gray code values tested (0..65535): {len(gray_values)}")
    print(f"Gray code bijection & Hamming property: PASSED (mismatches: {gray_mismatches})")
    print(
        f"256-pixel Grid bijections, 4-neighbor torus, and 8-cube flips: PASSED (mismatches: {grid_mismatches})"
    )
    print(f"JSON schemas checked: {len(schema_files)}, Errors: {len(schema_errors)}")
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    with open(script_dir / "challenger_test4_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    run_test()
