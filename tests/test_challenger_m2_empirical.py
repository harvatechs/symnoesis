"""Empirical challenger test harness for Milestone M2.

Stress tests:
1. Longitudinal temporal engine (500+ trajectories):
   - Single interval drops < -MDC (>= 150 cases)
   - Two consecutive interval drops < -MDC (>= 150 cases) + Zone Z4 Drift
   - Boundary & oscillating drops (-4.99 vs -5.01) (>= 100 cases)
   - Baseline Day 1 & uncalibrated handling (>= 100 cases)
2. Counterfactual repair (100+ non-mutualistic states):
   - 8 non-mutualistic symbiosis classes
   - Various stability_std values
   - Strict mutualism verification: SQ > 20, HNE > 0.2, SNE > 0.2
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

# Add project root and packages/py/src to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
PY_SRC = REPO_ROOT / "packages" / "py" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PY_SRC) not in sys.path:
    sys.path.insert(0, str(PY_SRC))

from symnoesis.classes import classify_symbiosis
from symnoesis.config import SymnoesisConfig
from symnoesis.counterfactual import (
    ContinuousState,
    compute_counterfactual_repair,
    evaluate_continuous_state,
)
from symnoesis.net_effects import compute_composite_c, compute_hne, compute_sne
from symnoesis.sq import compute_sq
from symnoesis.stability import compute_stability_factor
from symnoesis.temporal import (
    compute_mdc,
    compute_sem,
    evaluate_trajectory,
    is_trajectory_negative,
)
from symnoesis.zones import evaluate_zones


def run_temporal_stress_tests() -> dict:
    rng = random.Random(42)
    cfg = SymnoesisConfig.load_default()
    mdc_default = cfg.temporal.mdc_placeholder  # 5.0

    results = {
        "suite_a_single_drop": {"total": 0, "passed": 0, "failed": 0, "failures": []},
        "suite_b_consecutive_drops": {"total": 0, "passed": 0, "failed": 0, "failures": []},
        "suite_c_boundary_oscillations": {"total": 0, "passed": 0, "failed": 0, "failures": []},
        "suite_d_baseline_uncalibrated": {"total": 0, "passed": 0, "failed": 0, "failures": []},
    }

    # =========================================================================
    # Suite A: Single interval drop < -MDC (>= 150 trajectories)
    # Must NOT trigger negative trajectory.
    # =========================================================================
    for idx in range(160):
        # 5 frames: [1, 7, 28, 84, 182]
        base_sq = rng.uniform(20.0, 80.0)
        # Select single interval to drop < -MDC
        drop_interval = rng.randint(0, 3)
        drop_magnitude = rng.uniform(5.05, 35.0)

        scores = [base_sq]
        for i in range(4):
            if i == drop_interval:
                scores.append(scores[-1] - drop_magnitude)
            else:
                # Other intervals must have delta >= -MDC (e.g. flat, slight drop, or gain)
                delta = rng.uniform(-4.5, 15.0)
                scores.append(scores[-1] + delta)

        traj = evaluate_trajectory(scores, config=cfg)
        is_neg = is_trajectory_negative(scores, config=cfg)

        passed = (not traj.is_negative) and (not is_neg) and (traj.status != "deteriorating")
        results["suite_a_single_drop"]["total"] += 1
        if passed:
            results["suite_a_single_drop"]["passed"] += 1
        else:
            results["suite_a_single_drop"]["failed"] += 1
            results["suite_a_single_drop"]["failures"].append({
                "idx": idx,
                "scores": scores,
                "deltas": traj.deltas,
                "status": traj.status,
                "is_negative": traj.is_negative,
            })

    # =========================================================================
    # Suite B: Two consecutive interval drops < -MDC (>= 150 trajectories)
    # MUST trigger negative trajectory and Zone Z4 Drift.
    # =========================================================================
    for idx in range(160):
        base_sq = rng.uniform(40.0, 90.0)
        # Select starting interval for 2 consecutive drops: 0, 1, or 2
        start_interval = rng.randint(0, 2)
        drop1 = rng.uniform(5.01, 20.0)
        drop2 = rng.uniform(5.01, 20.0)

        scores = [base_sq]
        for i in range(4):
            if i == start_interval:
                scores.append(scores[-1] - drop1)
            elif i == start_interval + 1:
                scores.append(scores[-1] - drop2)
            else:
                delta = rng.uniform(-4.0, 10.0)
                scores.append(scores[-1] + delta)

        traj = evaluate_trajectory(scores, config=cfg)
        is_neg = is_trajectory_negative(scores, config=cfg)

        # Also test governance zone
        final_sq = scores[-1]
        zone_res = evaluate_zones(
            sq=final_sq,
            h_bits=(1, 1, 1, 1),
            m_bits=(1, 1, 1, 1),
            has_confirmed_chi=False,
            is_trajectory_negative=is_neg,
            config=cfg,
        )

        # If SQ > -25 and not Z5/Z7, primary MUST be Z4!
        # If SQ <= -25 (Z6), Z6 is primary and Z4 MUST be in secondary_tags!
        if final_sq > -25.0:
            zone_ok = (zone_res.primary == "Z4")
        else:
            zone_ok = (zone_res.primary == "Z6") and ("Z4" in zone_res.secondary_tags)

        passed = traj.is_negative and is_neg and (traj.status == "deteriorating") and zone_ok
        results["suite_b_consecutive_drops"]["total"] += 1
        if passed:
            results["suite_b_consecutive_drops"]["passed"] += 1
        else:
            results["suite_b_consecutive_drops"]["failed"] += 1
            results["suite_b_consecutive_drops"]["failures"].append({
                "idx": idx,
                "scores": scores,
                "deltas": traj.deltas,
                "status": traj.status,
                "zone_primary": zone_res.primary,
                "zone_secondary": zone_res.secondary_tags,
                "final_sq": final_sq,
            })

    # =========================================================================
    # Suite C: Fluctuating / Oscillating & Boundary Trajectories (>= 100 trajectories)
    # -4.99 vs -5.01, exact -5.00, high-frequency oscillations
    # =========================================================================
    # C1: Exact boundary drops of -5.00: -5.00 < -5.00 is FALSE -> MUST NOT trigger
    for _ in range(20):
        s0 = rng.uniform(50.0, 80.0)
        scores = [s0, s0 - 5.0, s0 - 10.0, s0 - 12.0, s0 - 10.0]
        traj = evaluate_trajectory(scores, config=cfg)
        passed = (not traj.is_negative) and (traj.status != "deteriorating")
        results["suite_c_boundary_oscillations"]["total"] += 1
        if passed:
            results["suite_c_boundary_oscillations"]["passed"] += 1
        else:
            results["suite_c_boundary_oscillations"]["failed"] += 1
            results["suite_c_boundary_oscillations"]["failures"].append({
                "type": "exact_-5.0",
                "scores": scores,
                "deltas": traj.deltas,
            })

    # C2: Near-boundary drops of -4.99 vs -5.01:
    # [-4.99, -4.99] -> must NOT trigger
    for _ in range(20):
        s0 = rng.uniform(50.0, 80.0)
        scores = [s0, s0 - 4.99, s0 - 9.98, s0 - 9.0, s0 - 8.0]
        traj = evaluate_trajectory(scores, config=cfg)
        passed = (not traj.is_negative)
        results["suite_c_boundary_oscillations"]["total"] += 1
        if passed:
            results["suite_c_boundary_oscillations"]["passed"] += 1
        else:
            results["suite_c_boundary_oscillations"]["failed"] += 1
            results["suite_c_boundary_oscillations"]["failures"].append({
                "type": "boundary_-4.99",
                "scores": scores,
                "deltas": traj.deltas,
            })

    # C3: [-5.01, -5.01] -> MUST trigger
    for _ in range(20):
        s0 = rng.uniform(50.0, 80.0)
        scores = [s0, s0 - 5.01, s0 - 10.02, s0 - 8.0, s0 - 5.0]
        traj = evaluate_trajectory(scores, config=cfg)
        passed = traj.is_negative and (traj.status == "deteriorating")
        results["suite_c_boundary_oscillations"]["total"] += 1
        if passed:
            results["suite_c_boundary_oscillations"]["passed"] += 1
        else:
            results["suite_c_boundary_oscillations"]["failed"] += 1
            results["suite_c_boundary_oscillations"]["failures"].append({
                "type": "boundary_-5.01",
                "scores": scores,
                "deltas": traj.deltas,
            })

    # C4: Mixed boundary [-5.01, -4.99] or [-4.99, -5.01] -> must NOT trigger
    for _ in range(20):
        s0 = rng.uniform(50.0, 80.0)
        first_drop = -5.01 if rng.random() < 0.5 else -4.99
        second_drop = -4.99 if first_drop == -5.01 else -5.01
        scores = [s0, s0 + first_drop, s0 + first_drop + second_drop, s0, s0 + 5.0]
        traj = evaluate_trajectory(scores, config=cfg)
        passed = (not traj.is_negative)
        results["suite_c_boundary_oscillations"]["total"] += 1
        if passed:
            results["suite_c_boundary_oscillations"]["passed"] += 1
        else:
            results["suite_c_boundary_oscillations"]["failed"] += 1
            results["suite_c_boundary_oscillations"]["failures"].append({
                "type": "mixed_boundary",
                "scores": scores,
                "deltas": traj.deltas,
            })

    # C5: High-frequency oscillations with large amplitudes:
    # [50, 30, 50, 30, 50] (deltas: [-20, +20, -20, +20]) -> must NOT trigger
    for _ in range(25):
        s0 = rng.uniform(40.0, 70.0)
        amp = rng.uniform(8.0, 30.0)
        scores = [s0, s0 - amp, s0 + 2.0, s0 - amp, s0 + 3.0]
        traj = evaluate_trajectory(scores, config=cfg)
        passed = (not traj.is_negative)
        results["suite_c_boundary_oscillations"]["total"] += 1
        if passed:
            results["suite_c_boundary_oscillations"]["passed"] += 1
        else:
            results["suite_c_boundary_oscillations"]["failed"] += 1
            results["suite_c_boundary_oscillations"]["failures"].append({
                "type": "oscillation",
                "scores": scores,
                "deltas": traj.deltas,
            })

    # =========================================================================
    # Suite D: Baseline Day 1 & Uncalibrated / Calibration Handling (>= 100 trajectories)
    # =========================================================================
    # D1: Day 1 baseline frame (single frame at Day 1)
    for _ in range(25):
        s = rng.uniform(-50.0, 80.0)
        traj = evaluate_trajectory([s], frames=[1], config=cfg)
        passed = (
            traj.is_baseline is True
            and traj.status == "stable"
            and not traj.is_negative
            and len(traj.deltas) == 0
        )
        results["suite_d_baseline_uncalibrated"]["total"] += 1
        if passed:
            results["suite_d_baseline_uncalibrated"]["passed"] += 1
        else:
            results["suite_d_baseline_uncalibrated"]["failed"] += 1

    # D2: Day 7 single frame (not baseline)
    for _ in range(25):
        s = rng.uniform(-50.0, 80.0)
        traj = evaluate_trajectory([s], frames=[7], config=cfg)
        passed = (
            traj.is_baseline is False
            and traj.status == "stable"
            and not traj.is_negative
            and len(traj.deltas) == 0
        )
        results["suite_d_baseline_uncalibrated"]["total"] += 1
        if passed:
            results["suite_d_baseline_uncalibrated"]["passed"] += 1
        else:
            results["suite_d_baseline_uncalibrated"]["failed"] += 1

    # D3: Two frames (fewer than 3 frames cannot assert trajectory even if huge drop)
    for _ in range(25):
        s1 = rng.uniform(50.0, 90.0)
        s2 = s1 - rng.uniform(10.0, 50.0)  # Drop of 10 to 50
        traj = evaluate_trajectory([s1, s2], frames=[1, 7], config=cfg)
        passed = (
            traj.is_baseline is False
            and traj.status == "stable"
            and not traj.is_negative
            and len(traj.deltas) == 1
        )
        results["suite_d_baseline_uncalibrated"]["total"] += 1
        if passed:
            results["suite_d_baseline_uncalibrated"]["passed"] += 1
        else:
            results["suite_d_baseline_uncalibrated"]["failed"] += 1

    # D4: Calibrated MDC with test-retest reliability r and SD
    for _ in range(30):
        sd = rng.uniform(8.0, 15.0)
        r = rng.uniform(0.70, 0.95)
        sem = compute_sem(sd, r)
        calibrated_mdc = compute_mdc(sem=sem)
        # Verify formula: MDC = 1.96 * sqrt(2) * SEM
        expected_mdc = 1.96 * math.sqrt(2.0) * sem
        formula_ok = abs(calibrated_mdc - expected_mdc) < 1e-9

        # Construct deltas that are between -placeholder (e.g. -6.0) and -calibrated_mdc
        # If calibrated_mdc is 10.0, deltas of -7.0 are NOT negative under calibrated MDC,
        # but WOULD be under placeholder (5.0)
        scores = [100.0, 100.0 - (calibrated_mdc - 1.0), 100.0 - 2 * (calibrated_mdc - 1.0)]
        traj_calibrated = evaluate_trajectory(scores, mdc=calibrated_mdc, config=cfg)
        # Under calibrated_mdc, drops do not exceed threshold
        passed = formula_ok and (not traj_calibrated.is_negative)
        results["suite_d_baseline_uncalibrated"]["total"] += 1
        if passed:
            results["suite_d_baseline_uncalibrated"]["passed"] += 1
        else:
            results["suite_d_baseline_uncalibrated"]["failed"] += 1

    return results


def run_counterfactual_stress_tests() -> dict:
    rng = random.Random(42)
    cfg = SymnoesisConfig.load_default()

    results = {
        "python": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "class_breakdown": {},
            "failures": [],
        }
    }

    # Generate 120 non-mutualistic states across all 8 non-mutualistic classes
    # 8 classes: Commensalism, Sacrificial, Inverse commensalism, Neutralism,
    # Antagonism, Parasitism, Amensalism, Mutual harm.
    # plus edge cases (zeros, boundary values, stability_std).

    target_classes = [
        "commensalism",
        "sacrificial",
        "inverse_commensalism",
        "neutralism",
        "antagonism",
        "parasitism",
        "amensalism",
        "mutual_harm",
    ]

    states: list[tuple[str, ContinuousState]] = []

    # 1. Targeted states for each non-mutualistic class (12 per class = 96 states)
    for cls in target_classes:
        for trial in range(12):
            std_val = rng.choice([0.0, 0.05, 0.15, 0.25, 0.40])
            if cls == "commensalism":
                # HNE > 0.2, SNE in [-0.2, 0.2]
                s_h = (rng.uniform(0.7, 1.0), rng.uniform(0.7, 1.0), rng.uniform(0.7, 1.0), rng.uniform(0.7, 1.0))
                integrity = rng.uniform(-0.15, 0.15)
                reliability = rng.uniform(-0.15, 0.15)
                operator = rng.uniform(-0.15, 0.15)
            elif cls == "sacrificial":
                # HNE > 0.2, SNE < -0.2
                s_h = (rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0))
                integrity = rng.uniform(-0.9, -0.4)
                reliability = rng.uniform(-0.9, -0.4)
                operator = rng.uniform(-0.9, -0.4)
            elif cls == "inverse_commensalism":
                # HNE in [-0.2, 0.2], SNE > 0.2
                s_h = (rng.uniform(0.4, 0.6), rng.uniform(0.4, 0.6), rng.uniform(0.4, 0.6), rng.uniform(0.4, 0.6))
                integrity = rng.uniform(0.4, 0.9)
                reliability = rng.uniform(0.4, 0.9)
                operator = rng.uniform(0.4, 0.9)
            elif cls == "neutralism":
                # HNE in [-0.2, 0.2], SNE in [-0.2, 0.2]
                s_h = (rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55))
                integrity = rng.uniform(-0.1, 0.1)
                reliability = rng.uniform(-0.1, 0.1)
                operator = rng.uniform(-0.1, 0.1)
            elif cls == "antagonism":
                # HNE in [-0.2, 0.2], SNE < -0.2
                s_h = (rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55), rng.uniform(0.45, 0.55))
                integrity = rng.uniform(-0.8, -0.3)
                reliability = rng.uniform(-0.8, -0.3)
                operator = rng.uniform(-0.8, -0.3)
            elif cls == "parasitism":
                # HNE < -0.2, SNE > 0.2
                s_h = (rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3))
                integrity = rng.uniform(0.4, 0.9)
                reliability = rng.uniform(0.4, 0.9)
                operator = rng.uniform(0.4, 0.9)
            elif cls == "amensalism":
                # HNE < -0.2, SNE in [-0.2, 0.2]
                s_h = (rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3))
                integrity = rng.uniform(-0.15, 0.15)
                reliability = rng.uniform(-0.15, 0.15)
                operator = rng.uniform(-0.15, 0.15)
            elif cls == "mutual_harm":
                # HNE < -0.2, SNE < -0.2
                s_h = (rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3), rng.uniform(0.0, 0.3))
                integrity = rng.uniform(-0.9, -0.3)
                reliability = rng.uniform(-0.9, -0.3)
                operator = rng.uniform(-0.9, -0.3)

            st = ContinuousState(
                s_h=s_h,
                integrity=integrity,
                reliability=reliability,
                operator=operator,
                stability_std=std_val,
            )
            # Verify it's actually non-mutualistic
            eval_init = evaluate_continuous_state(st, cfg)
            if eval_init[4] != "mutualism":
                states.append((eval_init[4], st))

    # 2. Add extreme edge cases (24 states)
    # Edge case: All zeros
    states.append(("extreme_zeros", ContinuousState(s_h=(0.0, 0.0, 0.0, 0.0), integrity=-1.0, reliability=-1.0, operator=-1.0, stability_std=0.0)))
    states.append(("extreme_zeros_unstable", ContinuousState(s_h=(0.0, 0.0, 0.0, 0.0), integrity=-1.0, reliability=-1.0, operator=-1.0, stability_std=0.4)))
    # Near boundary: HNE = 0.199, SNE = 0.201
    states.append(("boundary_hne", ContinuousState(s_h=(0.6, 0.6, 0.6, 0.59), integrity=0.3, reliability=0.3, operator=0.3, stability_std=0.0)))
    # Near boundary: HNE = 0.201, SNE = 0.199
    states.append(("boundary_sne", ContinuousState(s_h=(0.7, 0.7, 0.7, 0.7), integrity=0.2, reliability=0.2, operator=0.19, stability_std=0.0)))
    # High instability states with high C
    for std_val in [0.1, 0.2, 0.3, 0.4, 0.5]:
        states.append((f"high_std_{std_val}", ContinuousState(s_h=(0.4, 0.4, 0.4, 0.4), integrity=0.1, reliability=0.1, operator=0.1, stability_std=std_val)))
        states.append((f"low_var_high_std_{std_val}", ContinuousState(s_h=(0.1, 0.1, 0.1, 0.1), integrity=-0.5, reliability=-0.5, operator=-0.5, stability_std=std_val)))

    # Run Python tests
    for tag, st in states:
        for norm in ["l2", "l1"]:
            res = compute_counterfactual_repair(st, norm=norm, config=cfg)
            # Re-evaluate repaired state through full pipeline
            rep_hne, rep_sne, rep_c, rep_sq, rep_class = evaluate_continuous_state(res.repaired_state, cfg)

            # Strict verification criteria:
            # 1. SQ > 20.0
            # 2. HNE > 0.2
            # 3. SNE > 0.2
            # 4. Class == mutualism
            passed = (
                rep_sq > 20.0
                and rep_hne > 0.2
                and rep_sne > 0.2
                and rep_class == "mutualism"
            )

            results["python"]["total"] += 1
            if tag not in results["python"]["class_breakdown"]:
                results["python"]["class_breakdown"][tag] = {"total": 0, "passed": 0, "failed": 0}
            results["python"]["class_breakdown"][tag]["total"] += 1

            if passed:
                results["python"]["passed"] += 1
                results["python"]["class_breakdown"][tag]["passed"] += 1
            else:
                results["python"]["failed"] += 1
                results["python"]["class_breakdown"][tag]["failed"] += 1
                results["python"]["failures"].append({
                    "tag": tag,
                    "norm": norm,
                    "original_state": str(st),
                    "repaired_hne": rep_hne,
                    "repaired_sne": rep_sne,
                    "repaired_sq": rep_sq,
                    "repaired_class": rep_class,
                })

    # Save generated states for TS testing
    ts_states = []
    for tag, st in states:
        ts_states.append({
            "tag": tag,
            "s_h": list(st.s_h),
            "integrity": st.integrity,
            "reliability": st.reliability,
            "operator": st.operator,
            "stability_std": st.stability_std,
        })

    return results, ts_states


def main():
    print("=================================================================")
    print("  SYMNOESIS M2 EMPIRICAL CHALLENGER TEST HARNESS (PYTHON)")
    print("=================================================================")

    temp_results = run_temporal_stress_tests()
    total_temp = sum(s["total"] for s in temp_results.values())
    passed_temp = sum(s["passed"] for s in temp_results.values())
    failed_temp = sum(s["failed"] for s in temp_results.values())

    print(f"\n--- 1. Longitudinal Temporal Engine Stress Tests ({total_temp} trajectories) ---")
    for name, r in temp_results.items():
        print(f"  {name:32s}: {r['passed']}/{r['total']} passed ({r['failed']} failed)")
        if r["failed"] > 0:
            for f in r["failures"][:3]:
                print(f"    FAIL SAMPLE: {f}")

    cf_results, ts_states = run_counterfactual_stress_tests()
    total_cf = cf_results["python"]["total"]
    passed_cf = cf_results["python"]["passed"]
    failed_cf = cf_results["python"]["failed"]

    print(f"\n--- 2. Counterfactual Repair Stress Tests ({total_cf} evaluations across {len(ts_states)} states) ---")
    print(f"  Python Counterfactual: {passed_cf}/{total_cf} passed ({failed_cf} failed)")
    if failed_cf > 0:
        for f in cf_results["python"]["failures"][:5]:
            print(f"    FAIL SAMPLE: {f}")

    # Export states for TypeScript runner
    ts_export_path = REPO_ROOT / "tests" / "cf_stress_states.json"
    with open(ts_export_path, "w", encoding="utf-8") as f:
        json.dump(ts_states, f, indent=2)
    print(f"\nExported {len(ts_states)} stress states to {ts_export_path}")

    # Summary JSON for reporting
    summary = {
        "temporal": {
            "total_trajectories": total_temp,
            "passed": passed_temp,
            "failed": failed_temp,
            "suites": temp_results,
        },
        "counterfactual_python": {
            "total_evaluations": total_cf,
            "unique_states": len(ts_states),
            "passed": passed_cf,
            "failed": failed_cf,
            "failures": cf_results["python"]["failures"],
        },
    }
    summary_path = REPO_ROOT / "tests" / "m2_empirical_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved empirical test summary to {summary_path}")


if __name__ == "__main__":
    main()
