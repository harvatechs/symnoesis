/**
 * Counterfactual repair diagnostics and ridge projection engine.
 *
 * Normative implementation of SPEC §10, §12:
 * - Single-flip repair: c \oplus v for v in {H1..H4, M1..M4} where bit_v(c) == 0.
 * - Delta SQ: Delta SQ_v = SQ(c \oplus v) - SQ(c).
 * - Sourcing:
 *   - If neighbor c \oplus v has n_eff >= 10, use observed SQ (source: "observed").
 *   - If neighbor is unobserved or sparse, estimate via ridge additive model
 *     with pairwise bit interactions:
 *       \widehat{SQ}(b) = beta_0 + sum_i beta_i b_i + sum_{i < j} gamma_ij b_i b_j (source: "modeled").
 * - Dominant failure variable: v* = argmax_v Delta SQ_v.
 * - Associational framing invariant: strictly associational, non-causal phrasing.
 * - Continuous counterfactual repair: minimal L1/L2 adjustments to transition
 *   into Mutualism (SQ > 20, HNE > 0.2, SNE > 0.2).
 */

import { classifySymbiosis } from "./classes.js";
import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";
import {
  VARIABLE_NAMES,
  bitsToVertex,
  cellIdToVertex,
  type CellInput,
} from "./cover.js";
import { parsePixelId, pixelIdFromBits } from "./grid.js";
import { computeCompositeC, computeHne, computeSne } from "./net_effects.js";
import { computeSq } from "./sq.js";
import { computeStabilityFactor } from "./stability.js";

export const PROHIBITED_CAUSAL_TERMS = [
  "caused by",
  "cure",
  "causal impact",
  "fixes",
  "remedies",
] as const;

export interface FlipDiagnostic {
  readonly variable: string;
  readonly flipped_pixel_id: string;
  readonly delta_sq: number;
  readonly source: "observed" | "modeled";
  readonly target_sq: number;
}

export interface CounterfactualDiagnosticResult {
  readonly current_pixel_id: string;
  readonly current_sq: number;
  readonly flips: Readonly<Record<string, FlipDiagnostic>>;
  readonly dominant_variable: string | null;
  readonly max_delta_sq: number;
  readonly diagnostic_text: string;
}

export interface ContinuousState {
  readonly s_h: readonly [number, number, number, number];
  readonly integrity: number;
  readonly reliability: number;
  readonly operator: number;
  readonly stability_std?: number | undefined;
}

export interface ContinuousRepairResult {
  readonly original_state: ContinuousState;
  readonly repaired_state: ContinuousState;
  readonly deltas: Readonly<Record<string, number>>;
  readonly norm: "l1" | "l2";
  readonly distance: number;
  readonly is_already_mutualistic: boolean;
  readonly repaired_hne: number;
  readonly repaired_sne: number;
  readonly repaired_sq: number;
  readonly repaired_class: string;
}

function solveLinearSystem(A: number[][], b: number[]): number[] {
  const n = b.length;
  const M: number[][] = A.map((row, i) => [...row, b[i] ?? 0]);

  for (let i = 0; i < n; i++) {
    let maxRow = i;
    for (let k = i + 1; k < n; k++) {
      if (Math.abs(M[k]?.[i] ?? 0) > Math.abs(M[maxRow]?.[i] ?? 0)) {
        maxRow = k;
      }
    }
    const temp = M[i] ?? [];
    M[i] = M[maxRow] ?? [];
    M[maxRow] = temp;

    const pivot = M[i]?.[i] ?? 0;
    if (Math.abs(pivot) < 1e-12) continue;

    for (let k = i + 1; k < n; k++) {
      const rowK = M[k];
      const rowI = M[i];
      if (!rowK || !rowI) continue;
      const factor = (rowK[i] ?? 0) / pivot;
      for (let j = i; j <= n; j++) {
        rowK[j] = (rowK[j] ?? 0) - factor * (rowI[j] ?? 0);
      }
    }
  }

  const x: number[] = Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    let sum = M[i]?.[n] ?? 0;
    const rowI = M[i];
    if (rowI) {
      for (let j = i + 1; j < n; j++) {
        sum -= (rowI[j] ?? 0) * (x[j] ?? 0);
      }
    }
    const pivot = M[i]?.[i] ?? 0;
    x[i] = Math.abs(pivot) > 1e-12 ? sum / pivot : 0;
  }
  return x;
}

export class RidgeBitModel {
  readonly alpha: number;
  weights: number[];
  isFitted: boolean;
  private readonly interactionPairs: [number, number][];

  constructor(alpha = 1.0) {
    this.alpha = alpha;
    this.weights = Array(37).fill(0);
    this.isFitted = false;

    this.interactionPairs = [];
    for (let i = 0; i < 8; i++) {
      for (let j = i + 1; j < 8; j++) {
        this.interactionPairs.push([i, j]);
      }
    }
  }

  extractFeatures(bits: readonly number[]): number[] {
    if (bits.length !== 8) {
      throw new Error(`Expected 8 bits, got ${bits.length}`);
    }
    const feat = Array(37).fill(0);
    feat[0] = 1.0; // intercept
    for (let i = 0; i < 8; i++) {
      feat[1 + i] = bits[i] ?? 0;
    }
    for (let idx = 0; idx < this.interactionPairs.length; idx++) {
      const [i, j] = this.interactionPairs[idx]!;
      feat[9 + idx] = (bits[i] ?? 0) * (bits[j] ?? 0);
    }
    return feat;
  }

  fit(
    cells: readonly CellInput[] | Map<number, CellInput>,
    config?: SymnConfig,
  ): RidgeBitModel {
    const nCellMin =
      config?.layout?.n_cell_min ?? DEFAULT_CONFIG.layout.n_cell_min;
    const cellList = cells instanceof Map ? Array.from(cells.values()) : cells;

    const XRows: number[][] = [];
    const yVals: number[] = [];
    const wVals: number[] = [];

    for (const cell of cellList) {
      const nEff = cell.n_eff ?? 0.0;
      const isObs =
        (cell.observed ?? true) &&
        nEff >= nCellMin &&
        cell.sq !== null &&
        cell.sq !== undefined;
      if (isObs) {
        const v = cellIdToVertex(cell.cell_id);
        const bits: number[] = [];
        for (let i = 0; i < 8; i++) bits.push((v >> (7 - i)) & 1);

        XRows.push(this.extractFeatures(bits));
        yVals.push(cell.sq!);
        wVals.push(Math.sqrt(Math.max(1.0, nEff)));
      }
    }

    if (XRows.length === 0) {
      this.weights = Array(37).fill(0);
      this.isFitted = true;
      return this;
    }

    const N = XRows.length;
    const XtWX: number[][] = Array.from({ length: 37 }, () =>
      Array(37).fill(0),
    );
    const XtWy: number[] = Array(37).fill(0);

    for (let k = 0; k < N; k++) {
      const row = XRows[k];
      const y = yVals[k] ?? 0;
      const w = wVals[k] ?? 0;
      if (!row) continue;

      for (let i = 0; i < 37; i++) {
        XtWy[i] = (XtWy[i] ?? 0) + (row[i] ?? 0) * w * y;
        const xtwxRow = XtWX[i];
        if (xtwxRow) {
          for (let j = 0; j < 37; j++) {
            xtwxRow[j] = (xtwxRow[j] ?? 0) + (row[i] ?? 0) * w * (row[j] ?? 0);
          }
        }
      }
    }

    // Add alpha * I
    for (let i = 0; i < 37; i++) {
      const row = XtWX[i];
      if (row) {
        row[i] = (row[i] ?? 0) + this.alpha;
      }
    }

    this.weights = solveLinearSystem(XtWX, XtWy);
    this.isFitted = true;
    return this;
  }

  predict(bits: readonly number[]): number {
    if (!this.isFitted) return 0.0;
    const feat = this.extractFeatures(bits);
    let pred = 0.0;
    for (let i = 0; i < 37; i++) {
      pred += (this.weights[i] ?? 0) * (feat[i] ?? 0);
    }
    return Math.max(-100.0, Math.min(100.0, pred));
  }
}

export function fitRidgeAdditiveModel(
  cells: readonly CellInput[] | Map<number, CellInput>,
  alpha = 1.0,
  config?: SymnConfig,
): RidgeBitModel {
  const model = new RidgeBitModel(alpha);
  model.fit(cells, config);
  return model;
}

export function computeSingleFlipDiagnostics(
  pixelId: string,
  cells: readonly CellInput[] | Map<number, CellInput>,
  ridgeModel?: RidgeBitModel,
  config?: SymnConfig,
): CounterfactualDiagnosticResult {
  const cfg = config ?? DEFAULT_CONFIG;
  const cellMap =
    cells instanceof Map
      ? cells
      : new Map(cells.map((c) => [cellIdToVertex(c.cell_id), c]));

  const [hBits, mBits] = parsePixelId(pixelId);
  const currentBits = [...hBits, ...mBits];
  const currentVertex = bitsToVertex(currentBits);

  const currentCell = cellMap.get(currentVertex);
  let currentSq = 0.0;
  if (currentCell && currentCell.sq !== null && currentCell.sq !== undefined) {
    currentSq = currentCell.sq;
  } else if (ridgeModel && ridgeModel.isFitted) {
    currentSq = ridgeModel.predict(currentBits);
  }

  let activeRidge = ridgeModel;
  if (!activeRidge || !activeRidge.isFitted) {
    activeRidge = fitRidgeAdditiveModel(cellMap, 1.0, cfg);
  }

  const flips: Record<string, FlipDiagnostic> = {};

  for (let vIdx = 0; vIdx < VARIABLE_NAMES.length; vIdx++) {
    const varName = VARIABLE_NAMES[vIdx]!;
    if (currentBits[vIdx] === 0) {
      const flippedBits = [...currentBits];
      flippedBits[vIdx] = 1;
      const flippedVertex = bitsToVertex(flippedBits);
      const flippedId = pixelIdFromBits(
        flippedBits.slice(0, 4),
        flippedBits.slice(4),
      );

      const neighbor = cellMap.get(flippedVertex);
      let targetSq = 0.0;
      let source: "observed" | "modeled" = "modeled";

      if (
        neighbor &&
        (neighbor.observed ?? true) &&
        (neighbor.n_eff ?? 0.0) >= cfg.layout.n_cell_min &&
        neighbor.sq !== null &&
        neighbor.sq !== undefined
      ) {
        targetSq = neighbor.sq;
        source = "observed";
      } else {
        targetSq = activeRidge.predict(flippedBits);
        source = "modeled";
      }

      const deltaSq = targetSq - currentSq;
      flips[varName] = {
        variable: varName,
        flipped_pixel_id: flippedId,
        delta_sq: deltaSq,
        source,
        target_sq: targetSq,
      };
    }
  }

  const positiveFlips = Object.entries(flips).filter(
    ([, v]) => v.delta_sq > 0.0,
  );
  let dominantVar: string | null = null;
  let maxDelta = 0.0;
  let diagText = "";

  if (positiveFlips.length > 0) {
    positiveFlips.sort((a, b) => b[1].delta_sq - a[1].delta_sq);
    dominantVar = positiveFlips[0]![0];
    maxDelta = positiveFlips[0]![1].delta_sq;
    const domSource = positiveFlips[0]![1].source;
    diagText = `${domSource} association indicates dominant potential improvement in ${dominantVar} (+${maxDelta.toFixed(1)} SQ points)`;
  } else {
    dominantVar = null;
    const allDeltas = Object.values(flips).map((v) => v.delta_sq);
    maxDelta = allDeltas.length > 0 ? Math.max(...allDeltas) : 0.0;
    diagText =
      "observed association indicates no single-variable repair yields positive improvement";
  }

  for (const term of PROHIBITED_CAUSAL_TERMS) {
    if (diagText.toLowerCase().includes(term)) {
      throw new Error(
        `Prohibited causal term '${term}' found in diagnostic text`,
      );
    }
  }

  return {
    current_pixel_id: pixelId,
    current_sq: currentSq,
    flips,
    dominant_variable: dominantVar,
    max_delta_sq: maxDelta,
    diagnostic_text: diagText,
  };
}

// --- Continuous Counterfactual Repair ---

export function evaluateContinuousState(
  state: ContinuousState,
  config?: SymnConfig,
): {
  hne: number;
  sne: number;
  c: number;
  sq: number;
  technical_name: string;
} {
  const cfg = config ?? DEFAULT_CONFIG;
  const [hne] = computeHne(state.s_h, null, cfg);
  const [sneRaw, opBlind] = computeSne(
    state.integrity,
    state.reliability,
    state.operator,
    cfg,
  );
  const [c, sneEff] = computeCompositeC(hne, sneRaw, cfg);
  const s = computeStabilityFactor(state.stability_std ?? 0.0, cfg);
  const [sqVal] = computeSq(c, s, null, cfg);
  const classRes = classifySymbiosis(hne, sneEff, opBlind, cfg);

  return {
    hne,
    sne: sneEff,
    c,
    sq: sqVal,
    technical_name: classRes.technical_name,
  };
}

export function computeCounterfactualRepair(
  state: ContinuousState,
  norm: "l1" | "l2" = "l2",
  config?: SymnConfig,
): ContinuousRepairResult {
  const cfg = config ?? DEFAULT_CONFIG;
  const initial = evaluateContinuousState(state, cfg);

  if (
    initial.hne > cfg.classes.threshold &&
    initial.sne > cfg.classes.threshold &&
    initial.sq > 20.0 &&
    initial.technical_name === "mutualism"
  ) {
    return {
      original_state: state,
      repaired_state: state,
      deltas: {
        H1: 0.0,
        H2: 0.0,
        H3: 0.0,
        H4: 0.0,
        Integrity: 0.0,
        Reliability: 0.0,
        Operator: 0.0,
      },
      norm,
      distance: 0.0,
      is_already_mutualistic: true,
      repaired_hne: initial.hne,
      repaired_sne: initial.sne,
      repaired_sq: initial.sq,
      repaired_class: initial.technical_name,
    };
  }

  const targetThresh = cfg.classes.threshold + 0.005;

  // Project H: sum(s_h) must be >= 2 * targetThresh + 2.0 = 2.41
  const targetSumH = 2.0 * (targetThresh + 1.0);
  const currentSumH = state.s_h.reduce((acc, v) => acc + v, 0);
  const repH: [number, number, number, number] = [...state.s_h];

  if (currentSumH < targetSumH) {
    let shortfall = targetSumH - currentSumH;
    if (norm === "l2") {
      for (let iter = 0; iter < 10 && shortfall > 1e-6; iter++) {
        const unfixed = repH
          .map((v, i) => (v < 1.0 ? i : -1))
          .filter((i) => i >= 0);
        if (unfixed.length === 0) break;
        const add = shortfall / unfixed.length;
        let addedThisRound = 0.0;
        for (const idx of unfixed) {
          const currentVal = repH[idx] ?? 0;
          const headroom = 1.0 - currentVal;
          const alloc = Math.min(headroom, add);
          repH[idx] = currentVal + alloc;
          addedThisRound += alloc;
        }
        shortfall -= addedThisRound;
      }
    } else {
      for (let i = 0; i < 4 && shortfall > 1e-6; i++) {
        const currentVal = repH[i] ?? 0;
        const headroom = 1.0 - currentVal;
        const alloc = Math.min(headroom, shortfall);
        repH[i] = currentVal + alloc;
        shortfall -= alloc;
      }
    }
  }

  let repInt = state.integrity;
  let repRel = state.reliability;
  let repOp = state.operator;

  const currentSne = 0.4 * repInt + 0.4 * repRel + 0.2 * repOp;
  if (currentSne < targetThresh) {
    let sneShortfall = targetThresh - currentSne;
    if (norm === "l2") {
      const lambda = sneShortfall / 0.36;
      repInt = Math.min(1.0, Math.max(-1.0, repInt + 0.4 * lambda));
      repRel = Math.min(1.0, Math.max(-1.0, repRel + 0.4 * lambda));
      repOp = Math.min(1.0, Math.max(-1.0, repOp + 0.2 * lambda));
    } else {
      const headroomInt = 1.0 - repInt;
      const allocInt = Math.min(headroomInt, sneShortfall / 0.4);
      repInt += allocInt;
      sneShortfall -= 0.4 * allocInt;

      if (sneShortfall > 1e-6) {
        const headroomRel = 1.0 - repRel;
        const allocRel = Math.min(headroomRel, sneShortfall / 0.4);
        repRel += allocRel;
        sneShortfall -= 0.4 * allocRel;
      }

      if (sneShortfall > 1e-6) {
        const headroomOp = 1.0 - repOp;
        const allocOp = Math.min(headroomOp, sneShortfall / 0.2);
        repOp += allocOp;
      }
    }
  }

  const repairedState: ContinuousState = {
    s_h: repH,
    integrity: repInt,
    reliability: repRel,
    operator: repOp,
    stability_std: state.stability_std,
  };

  const repEval = evaluateContinuousState(repairedState, cfg);

  const deltas = {
    H1: (repH[0] ?? 0) - state.s_h[0],
    H2: (repH[1] ?? 0) - state.s_h[1],
    H3: (repH[2] ?? 0) - state.s_h[2],
    H4: (repH[3] ?? 0) - state.s_h[3],
    Integrity: repInt - state.integrity,
    Reliability: repRel - state.reliability,
    Operator: repOp - state.operator,
  };

  const deltaArr = Object.values(deltas);
  const distance =
    norm === "l2"
      ? Math.sqrt(deltaArr.reduce((acc, v) => acc + v * v, 0))
      : deltaArr.reduce((acc, v) => acc + Math.abs(v), 0);

  return {
    original_state: state,
    repaired_state: repairedState,
    deltas,
    norm,
    distance,
    is_already_mutualistic: false,
    repaired_hne: repEval.hne,
    repaired_sne: repEval.sne,
    repaired_sq: repEval.sq,
    repaired_class: repEval.technical_name,
  };
}
