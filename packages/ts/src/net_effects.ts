/**
 * Human and System Net Effect calculus (HNE, SNE) and composite net effect C.
 *
 * Normative implementation of SPEC §5 and §6:
 *   HNE_state = Sum a_i * (2*s_i - 1)
 *   HNE_outcome = mean(tanh(d_k / d0))
 *   HNE = (1 - lambda)*HNE_state + lambda*HNE_outcome
 *   SNE = 0.4*Integrity + 0.4*Reliability + 0.2*Operator
 *   SNE' = min(SNE, 0) if HNE < 0 else SNE (Non-compensation rule)
 *   C = (w_h*HNE + w_s*SNE') / (w_h + w_s)
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

/**
 * Computes HNE and outcomeAvailable flag.
 *
 * @param sH 4 scores for H1..H4 in [0, 1].
 * @param outcomeDeltas optional array of standardized outcome changes d_k.
 */
export function computeHne(
  sH: readonly number[],
  outcomeDeltas?: readonly number[] | null,
  config: SymnConfig = DEFAULT_CONFIG,
): [number, boolean] {
  if (sH.length !== 4) {
    throw new Error(`sH must contain exactly 4 scores, got ${sH.length}`);
  }

  const weights = config.net_effects.hne.state_weights;
  let hneState = 0.0;
  for (let i = 0; i < 4; i++) {
    const w = weights[i]!;
    const s = sH[i]!;
    hneState += w * (2.0 * s - 1.0);
  }

  if (!outcomeDeltas || outcomeDeltas.length === 0) {
    return [hneState, false];
  }

  const d0 = config.net_effects.hne.outcome_scale;
  let sumOutcome = 0.0;
  for (const d of outcomeDeltas) {
    sumOutcome += Math.tanh(d / d0);
  }
  const hneOutcome = sumOutcome / outcomeDeltas.length;

  const lambdaBlend = config.net_effects.hne.outcome_blend;
  const hne = (1.0 - lambdaBlend) * hneState + lambdaBlend * hneOutcome;
  return [hne, true];
}

/**
 * Computes SNE and operatorBlind flag.
 */
export function computeSne(
  integrity: number,
  reliability: number,
  operator?: number | null,
  config: SymnConfig = DEFAULT_CONFIG,
): [number, boolean] {
  let effOperator = 0.0;
  let operatorBlind = false;

  if (operator === null || operator === undefined) {
    effOperator = 0.0;
    operatorBlind = true;
  } else {
    effOperator = operator;
    operatorBlind = false;
  }

  const wInt = config.net_effects.sne.integrity;
  const wRel = config.net_effects.sne.reliability;
  const wOp = config.net_effects.sne.operator;

  const sne = wInt * integrity + wRel * reliability + wOp * effOperator;
  return [sne, operatorBlind];
}

/**
 * Applies non-compensation rule: SNE' = min(SNE, 0) if HNE < 0 else SNE.
 */
export function applyNonCompensation(
  hne: number,
  sne: number,
  config: SymnConfig = DEFAULT_CONFIG,
): number {
  if (config.sq.non_compensation && hne < 0.0) {
    return Math.min(sne, 0.0);
  }
  return sne;
}

/**
 * Computes composite effect C and effective SNE'.
 * Returns [C, snePrime].
 */
export function computeCompositeC(
  hne: number,
  sne: number,
  config: SymnConfig = DEFAULT_CONFIG,
): [number, number] {
  const snePrime = applyNonCompensation(hne, sne, config);
  const wH = config.sq.weights.human;
  const wS = config.sq.weights.system;
  const c = (wH * hne + wS * snePrime) / (wH + wS);
  return [c, snePrime];
}
