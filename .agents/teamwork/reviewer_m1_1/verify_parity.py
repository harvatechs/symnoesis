import json
import subprocess
from pathlib import Path
from symnoesis.config import SymnoesisConfig
from symnoesis.net_effects import compute_hne, compute_sne, compute_composite_c
from symnoesis.stability import compute_stability_factor
from symnoesis.gates import evaluate_safety_gate
from symnoesis.sq import compute_sq
from symnoesis.classes import classify_symbiosis
from symnoesis.zones import evaluate_zones

config = SymnoesisConfig.load_default()
vectors_dir = Path("E:/Symnoesis/spec/vectors")

node_script = """
import { computeHne, computeSne, computeCompositeC, computeStabilityFactor, evaluateSafetyGate, computeSq, classifySymbiosis, evaluateZones } from './packages/ts/dist/index.js';
import fs from 'fs';

const input = JSON.parse(fs.readFileSync(0, 'utf-8'));
const results = {};

// GV-001
{
  const inp = input.gv1.input;
  const [hne, outcomeAvail] = computeHne(inp.s_H, inp.outcome_deltas);
  const [sne, opBlind] = computeSne(inp.integrity, inp.reliability, inp.operator);
  const [c, snePrime] = computeCompositeC(hne, sne);
  const s = computeStabilityFactor(inp.sigma_C);
  const [gateCeiling] = evaluateSafetyGate(inp.confirmed_chi, null, 50.0);
  const [sq, sqRaw, triggered] = computeSq(c, s, gateCeiling);
  const symClass = classifySymbiosis(hne, sne, inp.operator_blind);
  const zoneRes = evaluateZones(sq, null, null, false, false);
  results.gv1 = { hne, sne, snePrime, c, s, sqRaw, sq, triggered, symClass: symClass.technical_name, zone: zoneRes.primary, secondary: zoneRes.secondary_tags };
}

// GV-002
{
  const inp = input.gv2.input;
  const [c, snePrime] = computeCompositeC(inp.hne, inp.sne);
  const s = computeStabilityFactor(inp.sigma_C);
  const [sq, sqRaw, triggered] = computeSq(c, s, null);
  const symClass = classifySymbiosis(inp.hne, inp.sne, inp.operator_blind);
  const zoneRes = evaluateZones(sq, null, null, false, false);
  results.gv2 = { snePrime, c, s, sqRaw, sq, triggered, symClass: symClass.technical_name, zone: zoneRes.primary, secondary: zoneRes.secondary_tags };
}

// GV-003
{
  const inp = input.gv3.input;
  const [gateCeiling, gateStatus] = evaluateSafetyGate([inp.confirmed_chi], null, 50.0);
  const [sq, sqRaw, triggered] = computeSq(inp.C, inp.S, gateCeiling);
  const zoneRes = evaluateZones(sq, null, null, true, false);
  results.gv3 = { gateCeiling, gateStatus, sqRaw, sq, triggered, zone: zoneRes.primary, secondary: zoneRes.secondary_tags };
}

fs.writeFileSync(1, JSON.stringify(results));
"""

gv1 = json.load(open(vectors_dir / "gv-sq-001.json"))
gv2 = json.load(open(vectors_dir / "gv-sq-002.json"))
gv3 = json.load(open(vectors_dir / "gv-sq-003.json"))

p = subprocess.Popen(
    ["node", "--input-type=module", "-e", node_script],
    cwd="E:/Symnoesis",
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
stdout, stderr = p.communicate(input=json.dumps({"gv1": gv1, "gv2": gv2, "gv3": gv3}).encode("utf-8"))
if p.returncode != 0:
    print("Node error:", stderr.decode("utf-8"))
    exit(1)

ts_res = json.loads(stdout.decode("utf-8"))

# Python computations
# GV-1
inp1 = gv1["input"]
py_hne1, _ = compute_hne(inp1["s_H"], inp1["outcome_deltas"], config)
py_sne1, _ = compute_sne(inp1["integrity"], inp1["reliability"], inp1["operator"], config)
py_c1, py_sne_prime1 = compute_composite_c(py_hne1, py_sne1, config)
py_s1 = compute_stability_factor(inp1["sigma_C"], config)
py_gate_c1, _ = evaluate_safety_gate(inp1["confirmed_chi"], None, 50.0, config)
py_sq1, py_sq_raw1, py_trig1 = compute_sq(py_c1, py_s1, py_gate_c1, config)
py_sym1 = classify_symbiosis(py_hne1, py_sne1, inp1["operator_blind"], config)
py_zone1 = evaluate_zones(py_sq1, None, None, False, False, config)

print("--- GV-SQ-001 Comparison ---")
print(f"HNE: Py={py_hne1}, TS={ts_res['gv1']['hne']}, diff={abs(py_hne1 - ts_res['gv1']['hne']):.2e}")
print(f"SNE: Py={py_sne1}, TS={ts_res['gv1']['sne']}, diff={abs(py_sne1 - ts_res['gv1']['sne']):.2e}")
print(f"C:   Py={py_c1}, TS={ts_res['gv1']['c']}, diff={abs(py_c1 - ts_res['gv1']['c']):.2e}")
print(f"S:   Py={py_s1}, TS={ts_res['gv1']['s']}, diff={abs(py_s1 - ts_res['gv1']['s']):.2e}")
print(f"SQ:  Py={py_sq1}, TS={ts_res['gv1']['sq']}, diff={abs(py_sq1 - ts_res['gv1']['sq']):.2e}")
print(f"Class: Py={py_sym1.technical_name}, TS={ts_res['gv1']['symClass']}")
print(f"Zone: Py={py_zone1.primary}, TS={ts_res['gv1']['zone']}")

# GV-2
inp2 = gv2["input"]
py_c2, py_sne_prime2 = compute_composite_c(inp2["hne"], inp2["sne"], config)
py_s2 = compute_stability_factor(inp2["sigma_C"], config)
py_sq2, py_sq_raw2, _ = compute_sq(py_c2, py_s2, None, config)
py_sym2 = classify_symbiosis(inp2["hne"], inp2["sne"], inp2["operator_blind"], config)
py_zone2 = evaluate_zones(py_sq2, None, None, False, False, config)

print("--- GV-SQ-002 Comparison ---")
print(f"SNE prime: Py={py_sne_prime2}, TS={ts_res['gv2']['snePrime']}, diff={abs(py_sne_prime2 - ts_res['gv2']['snePrime']):.2e}")
print(f"C:         Py={py_c2}, TS={ts_res['gv2']['c']}, diff={abs(py_c2 - ts_res['gv2']['c']):.2e}")
print(f"SQ:        Py={py_sq2}, TS={ts_res['gv2']['sq']}, diff={abs(py_sq2 - ts_res['gv2']['sq']):.2e}")
print(f"Class:     Py={py_sym2.technical_name}, TS={ts_res['gv2']['symClass']}")
print(f"Zone:      Py={py_zone2.primary}, TS={ts_res['gv2']['zone']}")

# GV-3
inp3 = gv3["input"]
py_gate_c3, py_gate_st3 = evaluate_safety_gate([inp3["confirmed_chi"]], None, 50.0, config)
py_sq3, py_sq_raw3, py_trig3 = compute_sq(inp3["C"], inp3["S"], py_gate_c3, config)
py_zone3 = evaluate_zones(py_sq3, None, None, True, False, config)

print("--- GV-SQ-003 Comparison ---")
print(f"Gate ceil: Py={py_gate_c3}, TS={ts_res['gv3']['gateCeiling']}, diff={abs(py_gate_c3 - ts_res['gv3']['gateCeiling']):.2e}")
print(f"SQ raw:    Py={py_sq_raw3}, TS={ts_res['gv3']['sqRaw']}, diff={abs(py_sq_raw3 - ts_res['gv3']['sqRaw']):.2e}")
print(f"SQ:        Py={py_sq3}, TS={ts_res['gv3']['sq']}, diff={abs(py_sq3 - ts_res['gv3']['sq']):.2e}")
print(f"Zone:      Py={py_zone3.primary}, TS={ts_res['gv3']['zone']}")

# Check max parity diff across all
max_diff = max(
    abs(py_hne1 - ts_res['gv1']['hne']),
    abs(py_sne1 - ts_res['gv1']['sne']),
    abs(py_c1 - ts_res['gv1']['c']),
    abs(py_s1 - ts_res['gv1']['s']),
    abs(py_sq1 - ts_res['gv1']['sq']),
    abs(py_c2 - ts_res['gv2']['c']),
    abs(py_sq2 - ts_res['gv2']['sq']),
    abs(py_sq3 - ts_res['gv3']['sq']),
)
print(f"MAX PARITY DIFF ACROSS ALL GOLDEN VECTORS: {max_diff:.2e}")
assert max_diff < 1e-6
print("GOLDEN VECTOR PARITY VERIFICATION PASSED!")
