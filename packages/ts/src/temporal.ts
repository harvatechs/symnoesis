/**
 * Longitudinal temporal engine and trajectory diagnostics.
 *
 * Normative implementation of SPEC §9, §10:
 * - Multi-frame observation sequence: days [1, 7, 28, 84, 182].
 * - Day 1 is a baseline frame (tagged "baseline").
 * - Change score per interval k: Delta SQ_k = SQ_frame(k) - SQ_frame(k-1).
 * - Minimum Detectable Change:
 *     MDC = 1.96 * sqrt(2) * SEM approx 2.77185858 * SEM
 *     SEM = SD * sqrt(1 - r)
 *     Placeholder MDC = 5.0 SQ points until r is calibrated.
 * - Trajectory classification:
 *     - Negative trajectory (deteriorating): two consecutive intervals with Delta SQ < -MDC.
 *     - Positive trajectory (improving): two consecutive intervals with Delta SQ > +MDC.
 *     - Stable trajectory: otherwise.
 * - Sequence of fewer than 3 frames (< 2 intervals) cannot assert trajectory (returns stable).
 * - Negative trajectory triggers governance zone Z4 (Drift).
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

export type TrajectoryStatus = "improving" | "stable" | "deteriorating";
export type TrajectoryCode = "positive" | "stable" | "negative";

export interface TrajectoryResult {
  readonly status: TrajectoryStatus;
  readonly deltas: readonly number[];
  readonly is_negative: boolean;
  readonly is_improving: boolean;
  readonly is_stable: boolean;
  readonly mdc: number;
  readonly frames_days: readonly number[];
  readonly scores: readonly number[];
  readonly status_code: TrajectoryCode;
  readonly is_baseline: boolean;
}

/**
 * Computes Standard Error of Measurement: SEM = SD * sqrt(1 - r).
 */
export function computeSem(sd: number, r: number): number {
  if (sd < 0.0) {
    throw new Error(`Standard deviation must be non-negative, got ${sd}`);
  }
  if (r < 0.0 || r > 1.0) {
    throw new Error(`Reliability r must be in [0, 1], got ${r}`);
  }
  return sd * Math.sqrt(1.0 - r);
}

/**
 * Computes Minimum Detectable Change (MDC).
 *
 * MDC = 1.96 * sqrt(2) * SEM = 2.77185858 * SEM.
 */
export function computeMdc(
  sem?: number,
  sd?: number,
  r?: number,
  placeholder = 5.0,
): number {
  if (sem !== undefined && sem !== null) {
    if (sem < 0.0) {
      throw new Error(`SEM must be non-negative, got ${sem}`);
    }
    return 1.96 * Math.SQRT2 * sem;
  }

  if (sd !== undefined && sd !== null && r !== undefined && r !== null) {
    const calculatedSem = computeSem(sd, r);
    return 1.96 * Math.SQRT2 * calculatedSem;
  }

  return placeholder;
}

/**
 * Checks whether the observation day represents the baseline frame (Day 1).
 */
export function isBaselineFrame(day: number): boolean {
  return day === 1;
}

/**
 * Computes consecutive interval deltas: Delta SQ_k = SQ_k - SQ_{k-1}.
 */
export function computeIntervalDeltas(
  scores: readonly number[],
): readonly number[] {
  if (scores.length < 2) {
    return [];
  }
  const deltas: number[] = [];
  for (let i = 1; i < scores.length; i++) {
    deltas.push(scores[i]! - scores[i - 1]!);
  }
  return deltas;
}

/**
 * Evaluates multi-frame trajectory and classifies into improving, stable, or deteriorating.
 */
export function evaluateTrajectory(
  scores: readonly number[],
  frames?: readonly number[],
  mdc?: number,
  config?: SymnConfig,
): TrajectoryResult {
  const cfg = config ?? DEFAULT_CONFIG;
  const activeFrames = frames
    ? [...frames]
    : cfg.temporal.frames_days.slice(0, scores.length);
  const activeMdc =
    mdc !== undefined && mdc !== null ? mdc : cfg.temporal.mdc_placeholder;
  const scoreList = [...scores];

  const deltas = computeIntervalDeltas(scoreList);
  const isBaseline =
    scoreList.length <= 1 && activeFrames.length > 0 && activeFrames[0] === 1;

  if (scoreList.length < 3) {
    return {
      status: "stable",
      deltas,
      is_negative: false,
      is_improving: false,
      is_stable: true,
      mdc: activeMdc,
      frames_days: activeFrames,
      scores: scoreList,
      status_code: "stable",
      is_baseline: isBaseline,
    };
  }

  const consecutiveNeeded = cfg.temporal.consecutive_intervals;

  let isNegative = false;
  for (let i = 0; i <= deltas.length - consecutiveNeeded; i++) {
    let allExceed = true;
    for (let j = 0; j < consecutiveNeeded; j++) {
      if (!(deltas[i + j]! < -activeMdc)) {
        allExceed = false;
        break;
      }
    }
    if (allExceed) {
      isNegative = true;
      break;
    }
  }

  let isImproving = false;
  if (!isNegative) {
    for (let i = 0; i <= deltas.length - consecutiveNeeded; i++) {
      let allExceed = true;
      for (let j = 0; j < consecutiveNeeded; j++) {
        if (!(deltas[i + j]! > activeMdc)) {
          allExceed = false;
          break;
        }
      }
      if (allExceed) {
        isImproving = true;
        break;
      }
    }
  }

  let status: TrajectoryStatus = "stable";
  let statusCode: TrajectoryCode = "stable";
  if (isNegative) {
    status = "deteriorating";
    statusCode = "negative";
  } else if (isImproving) {
    status = "improving";
    statusCode = "positive";
  }

  return {
    status,
    deltas,
    is_negative: isNegative,
    is_improving: isImproving,
    is_stable: !isNegative && !isImproving,
    mdc: activeMdc,
    frames_days: activeFrames,
    scores: scoreList,
    status_code: statusCode,
    is_baseline: isBaseline,
  };
}

/**
 * Convenience predicate for governance zone Z4 evaluation.
 */
export function isTrajectoryNegative(
  scores: readonly number[],
  mdc?: number,
  config?: SymnConfig,
): boolean {
  return evaluateTrajectory(scores, undefined, mdc, config).is_negative;
}
