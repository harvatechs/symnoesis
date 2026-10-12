import json
import math
from pathlib import Path
from symnoesis import (
    compute_hne,
    compute_sne,
    compute_composite_c,
    compute_stability_factor,
    compute_sq,
    classify_symbiosis,
    evaluate_zones,
    evaluate_safety_gate,
    normal_cdf,
    int_to_gray,
    gray_to_int,
    SymnoesisConfig,
)
from scipy.special import ndtr

cfg = SymnoesisConfig.load_default()
repo_root = Path("E:/Symnoesis")

print("=== 1. VERIFYING GOLDEN VECTORS IN PYTHON ===")
for vec_name in ["gv-sq-001.json", "gv-sq-002.json", "gv-sq-003.json"]:
    with open(repo_root / "spec" / "vectors" / vec_name, encoding="utf-8") as f:
        v = json.load(f)
    inp = v["input"]
    exp = v["expected"]
    print(f"\nVector: {v['vector_id']} ({v['description']})")

    if "s_H" in inp:
        hne, _ = compute_hne(inp["s_H"], inp.get("outcome_deltas"), cfg)
    else:
        hne = inp.get("hne", 0.0)

    if "integrity" in inp:
        sne, op_blind = compute_sne(inp["integrity"], inp["reliability"], inp.get("operator"), cfg)
    else:
        sne = inp.get("sne", 0.0)
        op_blind = inp.get("operator_blind", False)

    if "C" in inp:
        c = inp["C"]
        sne_prime = sne
    else:
        c, sne_prime = compute_composite_c(hne, sne, cfg)

    s = inp.get("S", compute_stability_factor(inp.get("sigma_C", 0.0), cfg))
    gate_ceiling = None
    if inp.get("confirmed_chi"):
        gate_ceiling, _ = evaluate_safety_gate([inp["confirmed_chi"]], None, 50.0, cfg)

    sq, sq_raw, triggered = compute_sq(c, s, gate_ceiling, cfg)
    sym_class = classify_symbiosis(hne, sne, inp.get("operator_blind", False), cfg)
    zone_res = evaluate_zones(sq, None, None, bool(inp.get("confirmed_chi")), False, cfg)

    checks = [
        ("hne", hne, exp.get("hne")),
        ("sne", sne, exp.get("sne")),
        ("sne_prime", sne_prime, exp.get("sne_prime")),
        ("C", c, exp.get("C")),
        ("sq_raw", sq_raw, exp.get("sq_raw")),
        ("sq", sq, exp.get("sq")),
    ]
    for name, actual, expected in checks:
        if expected is not None:
            diff = abs(actual - expected)
            assert diff <= 1e-6, f"FAIL {name}: actual {actual} != expected {expected} (diff {diff})"
            print(f"  [PASS] {name}: actual={actual:.6f}, expected={expected:.6f}, diff={diff:.2e}")

    if "symbiosis_class" in exp:
        assert sym_class.technical_name == exp["symbiosis_class"]
        assert sym_class.public_label == exp["symbiosis_class_public"]
        print(f"  [PASS] symbiosis_class: {sym_class.technical_name} ({sym_class.public_label})")

    if "zone" in exp:
        assert zone_res.primary == exp["zone"]
        print(f"  [PASS] zone: {zone_res.primary}")

print("\n=== 2. VERIFYING DENSE NORMAL_CDF AGAINST SCIPY.SPECIAL.NDTR ===")
max_diff = 0.0
# Test 200,001 points between -10 and 10
step = 0.0001
for i in range(200001):
    x = -10.0 + i * step
    val = normal_cdf(x)
    ref = float(ndtr(x))
    d = abs(val - ref)
    if d > max_diff:
        max_diff = d
print(f"Max difference across 200,001 points in [-10, 10]: {max_diff:.3e}")
assert max_diff < 1e-9, f"Max difference {max_diff} exceeded 1e-9 threshold!"

print("\n=== 3. VERIFYING GRAY CODE BIJECTIONS FOR ALL 16 VALUES ===")
for k in range(16):
    g = int_to_gray(k)
    k_rec = gray_to_int(g)
    assert k == k_rec, f"Gray code bijection failed for k={k}, g={g}, k_rec={k_rec}"
print("All 16 Gray code bijections verified.")

print("\n=== ALL PYTHON INTEGRITY CHECKS PASSED CLEAN ===")
