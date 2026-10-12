/**
 * Minimal Failure Cover (MFC) and Boolean minimization engine.
 *
 * Normative implementation of SPEC §11:
 * - 256 vertices on the 8-cube ({0, 1}^8) over (H1, H2, H3, H4, M1, M2, M3, M4).
 * - Subcube generation/evaluation in {0, 1, *}^8.
 * - Harm mass h(c) = n_eff(c) * max(0, -SQ(c)) / 100 for harmful cells (SQ <= tau_h).
 * - Rule purity pi(R) = sum_{harmful} n_eff(c) / sum_{observed} n_eff(c) >= purity_min (0.8).
 * - Exact set-cover optimization minimizing subcube count subject to coverage >= coverage_target (0.85).
 * - Quine-McCluskey strict mode matching sympy.logic.boolalg.SOPform output.
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";
import { parsePixelId, pixelIdFromBits } from "./grid.js";

export const VARIABLE_NAMES = [
  "H1",
  "H2",
  "H3",
  "H4",
  "M1",
  "M2",
  "M3",
  "M4",
] as const;

export type VariableName = (typeof VARIABLE_NAMES)[number];

const VAR_TO_INDEX: Record<string, number> = Object.fromEntries(
  VARIABLE_NAMES.map((name, i) => [name, i]),
);

export interface CoverConfig {
  readonly harm_threshold: number;
  readonly purity_min: number;
  readonly coverage_target: number;
  readonly n_rule_min: number;
  readonly max_literals: number;
}

export const DEFAULT_COVER_CONFIG: CoverConfig = {
  harm_threshold: -25.0,
  purity_min: 0.8,
  coverage_target: 0.85,
  n_rule_min: 30.0,
  max_literals: 5,
};

export interface CoverRule {
  readonly rule_str: string;
  readonly literals: Readonly<Record<string, number>>;
  readonly purity: number;
  readonly coverage: number;
  readonly harm_mass_covered: number;
  readonly n_eff: number;
  readonly unobserved_covered: number;
}

export interface CellInput {
  readonly cell_id: number | string;
  readonly sq?: number | null;
  readonly n_eff?: number;
  readonly observed?: boolean;
}

export interface MinimalFailureCoverResult {
  readonly rules: readonly CoverRule[];
  readonly total_harm_mass: number;
  readonly covered_harm_mass: number;
  readonly total_coverage: number;
  readonly solver_status: string;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Converts vertex integer in [0, 255] to 8 bits.
 */
export function vertexToBits(v: number): readonly number[] {
  if (v < 0 || v > 255 || !Number.isInteger(v)) {
    throw new Error(`Vertex index must be integer in [0, 255], got ${v}`);
  }
  const bits: number[] = [];
  for (let i = 0; i < 8; i++) {
    bits.push((v >> (7 - i)) & 1);
  }
  return bits;
}

/**
 * Converts 8 bits to vertex integer in [0, 255].
 */
export function bitsToVertex(bits: readonly number[]): number {
  if (bits.length !== 8) {
    throw new Error(`Expected 8 bits, got ${bits.length}`);
  }
  let val = 0;
  for (const b of bits) {
    if (b !== 0 && b !== 1) {
      throw new Error(`Bit must be 0 or 1, got ${b}`);
    }
    val = (val << 1) | b;
  }
  return val;
}

/**
 * Converts vertex integer to pixel ID string hXXXX-mYYYY.
 */
export function vertexToPixelId(v: number): string {
  const bits = vertexToBits(v);
  return pixelIdFromBits(bits.slice(0, 4), bits.slice(4));
}

/**
 * Normalizes CellInput cell_id into vertex integer in [0, 255].
 */
export function cellIdToVertex(cellId: number | string): number {
  if (typeof cellId === "number") {
    if (cellId < 0 || cellId > 255 || !Number.isInteger(cellId)) {
      throw new Error(`Cell ID number must be in [0, 255], got ${cellId}`);
    }
    return cellId;
  }
  const [hBits, mBits] = parsePixelId(cellId);
  return bitsToVertex([...hBits, ...mBits]);
}

/**
 * Computes harm mass h(c) = n_eff(c) * max(0, -SQ(c)) / 100 for harmful cells.
 */
export function computeHarmMass(
  sq: number | null | undefined,
  nEff: number,
  config?: { layout?: { n_cell_min?: number }; cover?: Partial<CoverConfig> },
): number {
  const nCellMin =
    config?.layout?.n_cell_min ?? DEFAULT_CONFIG.layout.n_cell_min;
  const harmThresh =
    config?.cover?.harm_threshold ?? DEFAULT_COVER_CONFIG.harm_threshold;

  if (sq === null || sq === undefined || nEff < nCellMin || sq > harmThresh) {
    return 0.0;
  }
  return (nEff * Math.max(0.0, -sq)) / 100.0;
}

/**
 * Computes rule purity pi(R) = harmful_n_eff / observed_n_eff.
 */
export function computeRulePurity(
  harmfulNEff: number,
  observedNEff: number,
): number {
  if (observedNEff <= 0.0) {
    return 0.0;
  }
  return harmfulNEff / observedNEff;
}

/**
 * Formats literals dictionary into canonical rule string.
 */
export function formatRuleString(literals: Record<string, number>): string {
  const keys = Object.keys(literals);
  if (keys.length === 0) {
    return "True";
  }
  keys.sort((a, b) => (VAR_TO_INDEX[a] ?? 999) - (VAR_TO_INDEX[b] ?? 999));
  return keys.map((k) => `${k}=${literals[k]}`).join(" AND ");
}

/**
 * Generates all candidate subcube patterns fixing between minLiterals and maxLiterals.
 */
export function generateSubcubes(
  minLiterals = 1,
  maxLiterals = 5,
  numVars = 8,
): readonly (readonly (number | null)[])[] {
  const subcubes: (readonly (number | null)[])[] = [];

  function combinations(arr: number[], k: number): number[][] {
    if (k === 0) return [[]];
    if (arr.length === 0) return [];
    const head = arr[0]!;
    const tail = arr.slice(1);
    const withHead = combinations(tail, k - 1).map((c) => [head, ...c]);
    const withoutHead = combinations(tail, k);
    return [...withHead, ...withoutHead];
  }

  const varIndices = Array.from({ length: numVars }, (_, i) => i);

  for (let L = minLiterals; L <= maxLiterals; L++) {
    const combs = combinations(varIndices, L);
    const totalVals = 1 << L;

    for (const indices of combs) {
      for (let v = 0; v < totalVals; v++) {
        const pattern: (number | null)[] = Array(numVars).fill(null);
        for (let idx = 0; idx < L; idx++) {
          const bitVal = (v >> (L - 1 - idx)) & 1;
          pattern[indices[idx]!] = bitVal;
        }
        subcubes.push(pattern);
      }
    }
  }

  return subcubes;
}

/**
 * Returns all vertex indices covered by subcube pattern.
 */
export function getVerticesInSubcube(
  pattern: readonly (number | null)[],
): readonly number[] {
  const unfixed: number[] = [];
  pattern.forEach((val, idx) => {
    if (val === null) unfixed.push(idx);
  });

  const totalCombs = 1 << unfixed.length;
  const vertices: number[] = [];

  for (let c = 0; c < totalCombs; c++) {
    const bits = [...pattern];
    for (let i = 0; i < unfixed.length; i++) {
      const bitVal = (c >> (unfixed.length - 1 - i)) & 1;
      bits[unfixed[i]!] = bitVal;
    }
    vertices.push(bitsToVertex(bits as number[]));
  }

  return vertices.sort((a, b) => a - b);
}

/**
 * Evaluates a candidate subcube pattern on given cell map.
 */
export function evaluateSubcube(
  pattern: readonly (number | null)[],
  cellMap: Map<number, CellInput>,
  totalHarmMass: number,
  config?: SymnConfig,
): CoverRule {
  const nCellMin =
    config?.layout?.n_cell_min ?? DEFAULT_CONFIG.layout.n_cell_min;
  const vertices = getVerticesInSubcube(pattern);

  const literals: Record<string, number> = {};
  pattern.forEach((val, idx) => {
    if (val !== null) {
      literals[VARIABLE_NAMES[idx]!] = val;
    }
  });
  const ruleStr = formatRuleString(literals);

  let harmMassCovered = 0.0;
  let harmfulNEff = 0.0;
  let observedNEff = 0.0;
  let unobservedCovered = 0;

  for (const v of vertices) {
    const cell = cellMap.get(v);
    const nEff = cell?.n_eff ?? 0.0;
    const isObs = (cell?.observed ?? true) && nEff >= nCellMin;

    if (!isObs || !cell) {
      unobservedCovered++;
      continue;
    }

    observedNEff += nEff;
    const hm = computeHarmMass(cell.sq, nEff, config);
    if (hm > 0.0) {
      harmMassCovered += hm;
      harmfulNEff += nEff;
    }
  }

  const purity = computeRulePurity(harmfulNEff, observedNEff);
  const coverage = totalHarmMass > 0.0 ? harmMassCovered / totalHarmMass : 0.0;

  return {
    rule_str: ruleStr,
    literals,
    purity,
    coverage,
    harm_mass_covered: harmMassCovered,
    n_eff: observedNEff,
    unobserved_covered: unobservedCovered,
  };
}

/**
 * Finds Minimal Failure Cover via exact set cover optimization.
 */
export function solveMfc(
  cells: readonly CellInput[] | Map<number, CellInput>,
  config?: SymnConfig,
): MinimalFailureCoverResult {
  const purityMin = DEFAULT_COVER_CONFIG.purity_min;
  const nRuleMin = DEFAULT_COVER_CONFIG.n_rule_min;
  const covTarget = DEFAULT_COVER_CONFIG.coverage_target;
  const maxLiterals = DEFAULT_COVER_CONFIG.max_literals;

  const cellMap =
    cells instanceof Map
      ? cells
      : new Map(cells.map((c) => [cellIdToVertex(c.cell_id), c]));

  // Identify harmful cells
  const harmfulCells = new Map<number, number>();
  for (let v = 0; v < 256; v++) {
    const cell = cellMap.get(v);
    if (cell) {
      const hm = computeHarmMass(cell.sq, cell.n_eff ?? 0.0, config);
      if (hm > 0.0) {
        harmfulCells.set(v, hm);
      }
    }
  }

  let totalHarmMass = 0.0;
  for (const hm of harmfulCells.values()) {
    totalHarmMass += hm;
  }

  if (totalHarmMass <= 0.0) {
    return {
      rules: [],
      total_harm_mass: 0.0,
      covered_harm_mass: 0.0,
      total_coverage: 1.0,
      solver_status: "zero_harm",
      metadata: { admissible_rules_count: 0 },
    };
  }

  // Generate candidate subcubes
  const allPatterns = generateSubcubes(1, maxLiterals, 8);
  const admissible: {
    rule: CoverRule;
    coveredHarmful: number[];
    litCount: number;
  }[] = [];

  for (const pat of allPatterns) {
    const rule = evaluateSubcube(pat, cellMap, totalHarmMass, config);
    if (
      rule.purity >= purityMin &&
      rule.n_eff >= nRuleMin &&
      rule.harm_mass_covered > 0.0
    ) {
      const verts = getVerticesInSubcube(pat);
      const coveredHarmful = verts.filter((v) => harmfulCells.has(v));
      admissible.push({
        rule,
        coveredHarmful,
        litCount: Object.keys(rule.literals).length,
      });
    }
  }

  if (admissible.length === 0) {
    return {
      rules: [],
      total_harm_mass: totalHarmMass,
      covered_harm_mass: 0.0,
      total_coverage: 0.0,
      solver_status: "no_admissible_rules",
      metadata: { admissible_rules_count: 0 },
    };
  }

  // Sort admissible rules canonically: fewer literals first, then lexicographical rule string
  admissible.sort(
    (a, b) =>
      a.litCount - b.litCount || a.rule.rule_str.localeCompare(b.rule.rule_str),
  );

  // Branch and bound minimum set cover to achieve >= 85% harm mass
  const targetMass = covTarget * totalHarmMass;
  let bestRules: CoverRule[] = [];
  let bestScore: [number, number, number] | null = null; // [ruleCount, totalLiterals, -coveredMass]

  function search(
    idx: number,
    chosen: { rule: CoverRule; coveredHarmful: number[]; litCount: number }[],
    coveredSet: Set<number>,
    currentMass: number,
    currentLiterals: number,
  ): void {
    if (currentMass >= targetMass) {
      const score: [number, number, number] = [
        chosen.length,
        currentLiterals,
        -currentMass,
      ];
      if (
        !bestScore ||
        score[0] < bestScore[0] ||
        (score[0] === bestScore[0] && score[1] < bestScore[1]) ||
        (score[0] === bestScore[0] &&
          score[1] === bestScore[1] &&
          score[2] < bestScore[2])
      ) {
        bestScore = score;
        bestRules = chosen.map((c) => c.rule);
      }
      return;
    }

    if (idx >= admissible.length) return;
    if (bestScore && chosen.length >= bestScore[0]) return;

    // Pick admissible[idx] if it adds uncovered harm mass
    const candidate = admissible[idx]!;
    let addsMass = 0.0;
    for (const v of candidate.coveredHarmful) {
      if (!coveredSet.has(v)) {
        addsMass += harmfulCells.get(v) ?? 0.0;
      }
    }

    if (addsMass > 0.0) {
      const nextSet = new Set(coveredSet);
      candidate.coveredHarmful.forEach((v) => nextSet.add(v));
      search(
        idx + 1,
        [...chosen, candidate],
        nextSet,
        currentMass + addsMass,
        currentLiterals + candidate.litCount,
      );
    }

    // Skip candidate
    search(idx + 1, chosen, coveredSet, currentMass, currentLiterals);
  }

  search(0, [], new Set(), 0.0, 0);

  if (bestRules.length === 0) {
    // Greedy fallback if branch and bound didn't reach target
    const coveredSet = new Set<number>();
    let currentMass = 0.0;
    for (const item of admissible) {
      bestRules.push(item.rule);
      item.coveredHarmful.forEach((v) => coveredSet.add(v));
      currentMass = Array.from(coveredSet).reduce(
        (sum, v) => sum + (harmfulCells.get(v) ?? 0),
        0,
      );
      if (currentMass >= targetMass) break;
    }
  }

  const coveredHarmfulSet = new Set<number>();
  for (const r of bestRules) {
    const pat: (number | null)[] = VARIABLE_NAMES.map((name) =>
      name in r.literals ? r.literals[name]! : null,
    );
    const verts = getVerticesInSubcube(pat);
    verts.forEach((v) => {
      if (harmfulCells.has(v)) coveredHarmfulSet.add(v);
    });
  }

  const coveredHarmMass = Array.from(coveredHarmfulSet).reduce(
    (acc, v) => acc + (harmfulCells.get(v) ?? 0),
    0,
  );
  const totalCoverage =
    totalHarmMass > 0 ? coveredHarmMass / totalHarmMass : 0.0;

  return {
    rules: bestRules,
    total_harm_mass: totalHarmMass,
    covered_harm_mass: coveredHarmMass,
    total_coverage: totalCoverage,
    solver_status: "optimal",
    metadata: {
      admissible_rules_count: admissible.length,
      covered_harmful_cells: coveredHarmfulSet.size,
    },
  };
}

// --- Quine-McCluskey Strict Mode Implementation in TypeScript ---

function intToTuple(val: number, numVars: number): readonly number[] {
  const res: number[] = [];
  for (let i = 0; i < numVars; i++) {
    res.push((val >> (numVars - 1 - i)) & 1);
  }
  return res;
}

/**
 * Computes exact Sum-Of-Products boolean reduction matching sympy.logic.boolalg.SOPform.
 */
export function quineMccluskeyBoolean(
  minterms: readonly number[],
  dontcares: readonly number[] = [],
  variables?: readonly string[],
): string {
  const mintermSet = new Set(minterms);
  if (mintermSet.size === 0) return "False";

  const allVals = [...mintermSet, ...dontcares];
  const maxVal = Math.max(...allVals, 0);
  const numVars = variables
    ? variables.length
    : Math.max(1, Math.ceil(Math.log2(maxVal + 1)));
  const varNames = variables
    ? [...variables]
    : Array.from({ length: numVars }, (_, i) => String.fromCharCode(97 + i));

  if (mintermSet.size === 1 << numVars && dontcares.length === 0) {
    return "True";
  }

  const primeImplicants = generatePrimeImplicants(
    mintermSet,
    new Set(dontcares),
    numVars,
  );
  const chosen = solvePrimeImplicantCover(primeImplicants, mintermSet);

  if (chosen.length === 0) return "False";

  const terms: string[] = [];
  for (const pi of chosen) {
    const term = formatSopTerm(pi, varNames);
    if (term === "") return "True";
    terms.push(term);
  }

  terms.sort();
  return terms.join(" | ");
}

/**
 * Runs Quine-McCluskey strict mode and returns CoverRule objects.
 */
export function quineMccluskey(
  minterms: readonly number[],
  dontcares: readonly number[] = [],
  variables: readonly string[] = VARIABLE_NAMES,
): readonly CoverRule[] {
  const mintermSet = new Set(minterms);
  if (mintermSet.size === 0) return [];

  const numVars = variables.length;
  const primeImplicants = generatePrimeImplicants(
    mintermSet,
    new Set(dontcares),
    numVars,
  );
  const chosen = solvePrimeImplicantCover(primeImplicants, mintermSet);

  const rules: CoverRule[] = [];
  for (const pi of chosen) {
    const literals: Record<string, number> = {};
    pi.forEach((val, idx) => {
      if (val !== -1) {
        literals[variables[idx]!] = val;
      }
    });

    rules.push({
      rule_str: formatRuleString(literals),
      literals,
      purity: 1.0,
      coverage: 1.0,
      harm_mass_covered: mintermSet.size,
      n_eff: mintermSet.size,
      unobserved_covered: dontcares.length,
    });
  }

  rules.sort((a, b) => a.rule_str.localeCompare(b.rule_str));
  return rules;
}

interface PrimeImplicant {
  readonly pattern: readonly number[]; // 0, 1, or -1 for '-'
  readonly coveredMinterms: ReadonlySet<number>;
}

function generatePrimeImplicants(
  minterms: Set<number>,
  dontcares: Set<number>,
  numVars: number,
): PrimeImplicant[] {
  const allTerms = new Set([...minterms, ...dontcares]);
  let currentTerms = new Map<
    string,
    { pattern: number[]; covered: Set<number> }
  >();

  for (const val of allTerms) {
    const pat = intToTuple(val, numVars);
    const key = pat.join(",");
    currentTerms.set(key, {
      pattern: [...pat],
      covered: minterms.has(val) ? new Set([val]) : new Set(),
    });
  }

  const primeImplicants: PrimeImplicant[] = [];

  while (currentTerms.size > 0) {
    const nextTerms = new Map<
      string,
      { pattern: number[]; covered: Set<number> }
    >();
    const combined = new Set<string>();
    const termList = Array.from(currentTerms.entries());

    for (let i = 0; i < termList.length; i++) {
      for (let j = i + 1; j < termList.length; j++) {
        const [k1, t1] = termList[i]!;
        const [k2, t2] = termList[j]!;

        let diffPos = -1;
        let match = true;
        for (let p = 0; p < numVars; p++) {
          if (t1.pattern[p] !== t2.pattern[p]) {
            if (
              diffPos === -1 &&
              t1.pattern[p] !== -1 &&
              t2.pattern[p] !== -1
            ) {
              diffPos = p;
            } else {
              match = false;
              break;
            }
          }
        }

        if (match && diffPos !== -1) {
          combined.add(k1);
          combined.add(k2);
          const merged = [...t1.pattern];
          merged[diffPos] = -1;
          const mergedKey = merged.join(",");
          const cov = new Set([...t1.covered, ...t2.covered]);

          if (!nextTerms.has(mergedKey)) {
            nextTerms.set(mergedKey, { pattern: merged, covered: cov });
          } else {
            const existing = nextTerms.get(mergedKey)!;
            cov.forEach((v) => existing.covered.add(v));
          }
        }
      }
    }

    for (const [k, t] of currentTerms.entries()) {
      if (!combined.has(k)) {
        if (t.covered.size > 0) {
          primeImplicants.push({
            pattern: t.pattern,
            coveredMinterms: t.covered,
          });
        }
      }
    }

    currentTerms = nextTerms;
  }

  return primeImplicants;
}

function solvePrimeImplicantCover(
  pis: PrimeImplicant[],
  minterms: Set<number>,
): (readonly number[])[] {
  if (minterms.size === 0 || pis.length === 0) return [];

  const uncovered = new Set(minterms);
  const selected: (readonly number[])[] = [];
  let remainingPis = [...pis];

  // Essential Prime Implicants
  let progress = true;
  while (progress && uncovered.size > 0) {
    progress = false;
    const mintermCov = new Map<number, PrimeImplicant[]>();
    for (const m of uncovered) mintermCov.set(m, []);

    for (const pi of remainingPis) {
      for (const m of pi.coveredMinterms) {
        if (uncovered.has(m)) {
          mintermCov.get(m)!.push(pi);
        }
      }
    }

    for (const [, covList] of mintermCov) {
      if (covList.length === 1) {
        const epi = covList[0]!;
        if (!selected.includes(epi.pattern)) {
          selected.push(epi.pattern);
          epi.coveredMinterms.forEach((m) => uncovered.delete(m));
          remainingPis = remainingPis.filter((p) => p !== epi);
          progress = true;
          break;
        }
      }
    }
  }

  if (uncovered.size === 0) return selected;

  // Branch and bound for non-essential primes
  let bestCover: (readonly number[])[] | null = null;
  let bestScore: [number, number] | null = null; // [piCount, literals]

  function searchBb(
    idx: number,
    currCov: Set<number>,
    currChosen: (readonly number[])[],
    currLits: number,
  ): void {
    let allCovered = true;
    for (const m of uncovered) {
      if (!currCov.has(m)) {
        allCovered = false;
        break;
      }
    }

    if (allCovered) {
      const score: [number, number] = [currChosen.length, currLits];
      if (
        !bestScore ||
        score[0] < bestScore[0] ||
        (score[0] === bestScore[0] && score[1] < bestScore[1])
      ) {
        bestScore = score;
        bestCover = [...currChosen];
      }
      return;
    }

    if (idx >= remainingPis.length) return;
    if (bestScore && currChosen.length >= bestScore[0]) return;

    const candidate = remainingPis[idx]!;
    let coversNew = false;
    for (const m of candidate.coveredMinterms) {
      if (uncovered.has(m) && !currCov.has(m)) {
        coversNew = true;
        break;
      }
    }

    if (coversNew) {
      const nextCov = new Set(currCov);
      candidate.coveredMinterms.forEach((m) => nextCov.add(m));
      const lits = candidate.pattern.filter((b) => b !== -1).length;
      searchBb(
        idx + 1,
        nextCov,
        [...currChosen, candidate.pattern],
        currLits + lits,
      );
    }

    searchBb(idx + 1, currCov, currChosen, currLits);
  }

  searchBb(0, new Set(), [], 0);

  const foundCover = bestCover as (readonly number[])[] | null;
  if (foundCover !== null) {
    for (const c of foundCover) {
      selected.push(c);
    }
  }
  return selected;
}

function formatSopTerm(
  pattern: readonly number[],
  varNames: readonly string[],
): string {
  const literals: string[] = [];
  pattern.forEach((val, idx) => {
    if (val === 1) {
      literals.push(varNames[idx]!);
    } else if (val === 0) {
      literals.push(`~${varNames[idx]}`);
    }
  });
  return literals.join(" & ");
}
