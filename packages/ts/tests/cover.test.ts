import { describe, expect, it } from "vitest";
import {
  DEFAULT_COVER_CONFIG,
  VARIABLE_NAMES,
  bitsToVertex,
  computeHarmMass,
  computeRulePurity,
  evaluateSubcube,
  formatRuleString,
  generateSubcubes,
  getVerticesInSubcube,
  quineMccluskey,
  quineMccluskeyBoolean,
  solveMfc,
  vertexToBits,
  vertexToPixelId,
  type CellInput,
} from "../src/cover.js";

describe("Minimal Failure Cover & Boolean Minimization (SPEC §11)", () => {
  it("TC1.15.01: vertexToBits and bitsToVertex form an exact bijection on [0, 255]", () => {
    const seen = new Set<string>();
    for (let v = 0; v < 256; v++) {
      const bits = vertexToBits(v);
      expect(bits).toHaveLength(8);
      expect(bitsToVertex(bits)).toBe(v);
      seen.add(bits.join(""));
    }
    expect(seen.size).toBe(256);

    expect(() => vertexToBits(-1)).toThrow();
    expect(() => vertexToBits(256)).toThrow();
    expect(() => bitsToVertex([0, 1, 0])).toThrow();
    expect(() => bitsToVertex([0, 1, 0, 1, 0, 1, 0, 2])).toThrow();
  });

  it("TC1.15.02: vertexToPixelId converts vertex integer to canonical pixel ID", () => {
    expect(vertexToPixelId(0)).toBe("h0000-m0000");
    expect(vertexToPixelId(255)).toBe("h1111-m1111");
  });

  it("TC1.15.03: generateSubcubes generates exactly 3488 subcubes fixing 1 to 5 literals", () => {
    // math.comb(8, 1)*2 + comb(8, 2)*4 + comb(8, 3)*8 + comb(8, 4)*16 + comb(8, 5)*32 = 3488
    const subcubes = generateSubcubes(1, 5, 8);
    expect(subcubes).toHaveLength(3488);

    // Verify covered vertex count per literal count: 2^(8 - L)
    for (let L = 1; L <= 5; L++) {
      const pat: (number | null)[] = [
        ...Array(L).fill(0),
        ...Array(8 - L).fill(null),
      ];
      const verts = getVerticesInSubcube(pat);
      expect(verts).toHaveLength(Math.pow(2, 8 - L));
    }
  });

  it("TC1.15.04: formatRuleString generates canonical sorted rule strings", () => {
    expect(formatRuleString({})).toBe("True");
    expect(formatRuleString({ M2: 0, H1: 1 })).toBe("H1=1 AND M2=0");
  });

  it("TC1.15.05: computeHarmMass evaluates h(c) = n_eff * max(0, -SQ) / 100 for harmful cells", () => {
    // Harmful cell: SQ = -40, n_eff = 50 -> 20.0
    const h1 = computeHarmMass(-40.0, 50.0);
    expect(Math.abs(h1 - 20.0)).toBeLessThan(1e-9);

    // Boundary at -25.0
    const hBound = computeHarmMass(-25.0, 100.0);
    expect(Math.abs(hBound - 25.0)).toBeLessThan(1e-9);

    // Safe cell: SQ = -24.9 -> zero
    expect(computeHarmMass(-24.9, 100.0)).toBe(0.0);

    // Positive SQ -> zero
    expect(computeHarmMass(10.0, 100.0)).toBe(0.0);

    // Null SQ -> zero
    expect(computeHarmMass(null, 100.0)).toBe(0.0);

    // Sparse cell below n_cell_min (10.0) -> zero
    expect(computeHarmMass(-50.0, 9.9)).toBe(0.0);
  });

  it("TC1.15.06: computeRulePurity evaluates pi(R) = harmful_n_eff / observed_n_eff", () => {
    const purity = computeRulePurity(90.0, 100.0);
    expect(Math.abs(purity - 0.9)).toBeLessThan(1e-9);
    expect(computeRulePurity(0.0, 0.0)).toBe(0.0);
  });

  it("TC1.15.07: evaluateSubcube computes purity, coverage, and unobserved count", () => {
    // Pattern fixing H1=1, H2=0 (64 cells)
    const pat: (number | null)[] = [1, 0, null, null, null, null, null, null];
    const verts = getVerticesInSubcube(pat);

    const cellMap = new Map<number, CellInput>();
    for (const v of verts.slice(0, 10)) {
      cellMap.set(v, { cell_id: v, sq: -50.0, n_eff: 20.0, observed: true });
    }

    const rule = evaluateSubcube(pat, cellMap, 100.0);
    expect(rule.rule_str).toBe("H1=1 AND H2=0");
    expect(rule.purity).toBe(1.0);
    expect(rule.n_eff).toBe(200.0);
    expect(rule.unobserved_covered).toBe(54); // 64 - 10
  });

  it("TC1.15.08: solveMfc with zero harm returns empty rules with zero_harm status", () => {
    const cells: CellInput[] = Array.from({ length: 256 }, (_, v) => ({
      cell_id: v,
      sq: 10.0,
      n_eff: 50.0,
      observed: true,
    }));
    const res = solveMfc(cells);
    expect(res.rules).toHaveLength(0);
    expect(res.total_harm_mass).toBe(0.0);
    expect(res.solver_status).toBe("zero_harm");
  });

  it("TC1.15.09: solveMfc covers harmful cluster with coverage >= 0.85", () => {
    // Cluster where H3=0 and M2=0 (pattern: * * 0 *  * 0 * *)
    const harmfulPat: (number | null)[] = [
      null,
      null,
      0,
      null,
      null,
      0,
      null,
      null,
    ];
    const harmfulVerts = new Set(getVerticesInSubcube(harmfulPat));

    const cells: CellInput[] = Array.from({ length: 256 }, (_, v) => {
      if (harmfulVerts.has(v)) {
        return { cell_id: v, sq: -40.0, n_eff: 15.0, observed: true };
      }
      return { cell_id: v, sq: 30.0, n_eff: 20.0, observed: true };
    });

    const res = solveMfc(cells);
    expect(res.rules.length).toBeGreaterThanOrEqual(1);
    expect(res.total_coverage).toBeGreaterThanOrEqual(
      DEFAULT_COVER_CONFIG.coverage_target,
    );

    const ruleStrs = res.rules.map((r) => r.rule_str);
    expect(ruleStrs.some((s) => s.includes("H3=0") && s.includes("M2=0"))).toBe(
      true,
    );
  });

  it("TC1.16.01: quineMccluskeyBoolean matches exact sympy SOP reduction", () => {
    // Minterms 0, 1 on 4 vars -> ~a & ~b & ~c
    const qm = quineMccluskeyBoolean([0, 1], [], ["a", "b", "c", "d"]);
    expect(qm).toBe("~a & ~b & ~c");

    // Don't cares expansion: minterm 0, dc 1 on 2 vars -> ~a
    const qmDc = quineMccluskeyBoolean([0], [1], ["a", "b"]);
    expect(qmDc).toBe("~a");

    // 4 minterms reduce to 1 literal: [0, 1, 2, 3] on 3 vars -> ~a
    const qm4 = quineMccluskeyBoolean([0, 1, 2, 3], [], ["a", "b", "c"]);
    expect(qm4).toBe("~a");

    // All minterms reduce to True
    const qmAll = quineMccluskeyBoolean([0, 1, 2, 3], [], ["a", "b"]);
    expect(qmAll).toBe("True");

    // Empty returns False
    expect(quineMccluskeyBoolean([], [], ["a", "b"])).toBe("False");
  });

  it("TC1.16.02: quineMccluskey returns valid CoverRule schema objects", () => {
    const rules = quineMccluskey([0, 1, 4, 5], [], VARIABLE_NAMES);
    expect(rules.length).toBeGreaterThanOrEqual(1);
    const r = rules[0]!;
    expect(r.purity).toBe(1.0);
    expect(r.coverage).toBe(1.0);
    expect(r.rule_str).toContain("H1=0");
    expect(typeof r.literals).toBe("object");

    expect(quineMccluskey([])).toEqual([]);
  });

  it("TC1.16.03: solveMfc with no admissible rules returns empty with no_admissible_rules", () => {
    const cells: CellInput[] = [
      { cell_id: 0, sq: -50.0, n_eff: 10.0, observed: true },
    ];
    const res = solveMfc(cells);
    expect(res.solver_status).toBe("no_admissible_rules");
    expect(res.total_coverage).toBe(0.0);
  });
});
