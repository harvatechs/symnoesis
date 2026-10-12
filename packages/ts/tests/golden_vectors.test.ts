import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  classifySymbiosis,
  computeCompositeC,
  computeHne,
  computeSne,
  computeSq,
  computeStabilityFactor,
  evaluateSafetyGate,
  evaluateZones,
} from "../src/index.js";

describe("Golden Vectors Parity (GV-SQ-001..003)", () => {
  it("GV-SQ-001: Mutualism & Productive Zone (Z2) within 1e-6", () => {
    const vectorPath = resolve(
      __dirname,
      "../../../spec/vectors/gv-sq-001.json",
    );
    const gv = JSON.parse(readFileSync(vectorPath, "utf-8")) as {
      input: {
        s_H: number[];
        outcome_deltas: number[] | null;
        integrity: number;
        reliability: number;
        operator: number;
        sigma_C: number;
        confirmed_chi: string[] | null;
        operator_blind: boolean;
      };
      expected: {
        hne: number;
        sne: number;
        sne_prime: number;
        C: number;
        S: number;
        sq_raw: number;
        sq: number;
        symbiosis_class: string;
        symbiosis_class_public: string;
        zone: string;
      };
    };

    const inp = gv.input;
    const exp = gv.expected;

    const [hne, outcomeAvail] = computeHne(inp.s_H, inp.outcome_deltas);
    expect(hne).toBeCloseTo(exp.hne, 6);
    expect(outcomeAvail).toBe(false);

    const [sne, opBlind] = computeSne(
      inp.integrity,
      inp.reliability,
      inp.operator,
    );
    expect(sne).toBeCloseTo(exp.sne, 6);
    expect(opBlind).toBe(false);

    const [c, snePrime] = computeCompositeC(hne, sne);
    expect(snePrime).toBeCloseTo(exp.sne_prime, 6);
    expect(c).toBeCloseTo(exp.C, 6);

    const s = computeStabilityFactor(inp.sigma_C);
    expect(s).toBeCloseTo(exp.S, 6);

    const [gateCeiling] = evaluateSafetyGate(inp.confirmed_chi, null, 50.0);
    const [sq, sqRaw, triggered] = computeSq(c, s, gateCeiling);
    expect(sqRaw).toBeCloseTo(exp.sq_raw, 6);
    expect(sq).toBeCloseTo(exp.sq, 6);
    expect(triggered).toBe(false);

    const symClass = classifySymbiosis(hne, sne, inp.operator_blind);
    expect(symClass.technical_name).toBe(exp.symbiosis_class);
    expect(symClass.public_label).toBe(exp.symbiosis_class_public);

    const zoneRes = evaluateZones(sq, null, null, false, false);
    expect(zoneRes.primary).toBe(exp.zone);
  });

  it("GV-SQ-002: Parasitism, Non-Compensation & Harm Zone (Z6) within 1e-6", () => {
    const vectorPath = resolve(
      __dirname,
      "../../../spec/vectors/gv-sq-002.json",
    );
    const gv = JSON.parse(readFileSync(vectorPath, "utf-8")) as {
      input: {
        hne: number;
        sne: number;
        sigma_C: number;
        confirmed_chi: string[] | null;
        operator_blind: boolean;
      };
      expected: {
        sne_prime: number;
        C: number;
        sq_raw: number;
        sq: number;
        symbiosis_class: string;
        symbiosis_class_public: string;
        zone: string;
      };
    };

    const inp = gv.input;
    const exp = gv.expected;

    const [c, snePrime] = computeCompositeC(inp.hne, inp.sne);
    expect(snePrime).toBeCloseTo(exp.sne_prime, 6);
    expect(c).toBeCloseTo(exp.C, 6);

    const s = computeStabilityFactor(inp.sigma_C);
    const [sq, sqRaw] = computeSq(c, s, null);
    expect(sqRaw).toBeCloseTo(exp.sq_raw, 6);
    expect(sq).toBeCloseTo(exp.sq, 6);

    const symClass = classifySymbiosis(inp.hne, inp.sne, inp.operator_blind);
    expect(symClass.technical_name).toBe(exp.symbiosis_class);
    expect(symClass.public_label).toBe(exp.symbiosis_class_public);

    const zoneRes = evaluateZones(sq, null, null, false, false);
    expect(zoneRes.primary).toBe(exp.zone);
  });

  it("GV-SQ-003: Safety Gate Ceiling & Critical Zone (Z7) within 1e-6", () => {
    const vectorPath = resolve(
      __dirname,
      "../../../spec/vectors/gv-sq-003.json",
    );
    const gv = JSON.parse(readFileSync(vectorPath, "utf-8")) as {
      input: {
        C: number;
        S: number;
        confirmed_chi: string;
        operator_blind: boolean;
      };
      expected: {
        gate_ceiling: number;
        gate_triggered: boolean;
        sq_raw: number;
        sq: number;
        zone: string;
      };
    };

    const inp = gv.input;
    const exp = gv.expected;

    const confirmed = [inp.confirmed_chi];
    const [gateCeiling, gateStatus] = evaluateSafetyGate(confirmed, null, 50.0);
    expect(gateStatus).toBe("critical");
    expect(gateCeiling).toBeCloseTo(exp.gate_ceiling, 6);

    const [sq, sqRaw, triggered] = computeSq(inp.C, inp.S, gateCeiling);
    expect(sqRaw).toBeCloseTo(exp.sq_raw, 6);
    expect(triggered).toBe(exp.gate_triggered);
    expect(sq).toBeCloseTo(exp.sq, 6);

    const zoneRes = evaluateZones(sq, null, null, true, false);
    expect(zoneRes.primary).toBe(exp.zone);
  });
});
