/**
 * Variable scaling, threshold calculation, and marginal binarization probabilities.
 *
 * Normative implementation of SPEC §2.3 and §3:
 *   s = Phi(d / tau)
 *   theta_H2 = Phi(-delta / tau)
 *   p_i = Phi((mu_i - theta_i) / sigma_i) with sigma_i >= sigma_floor
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";
import { normalCdf } from "./math.js";

/**
 * Maps standardized effect size d to continuous score s in [0, 1].
 */
export function effectToScore(
  d: number,
  config: SymnConfig = DEFAULT_CONFIG,
): number {
  const tau = config.variables.effect_scale;
  return normalCdf(d / tau);
}

/**
 * Computes non-inferiority threshold for H2 (Capability Trajectory).
 */
export function computeH2Threshold(
  config: SymnConfig = DEFAULT_CONFIG,
): number {
  const delta = config.variables.noninferiority_margin_h2;
  const tau = config.variables.effect_scale;
  return normalCdf(-delta / tau);
}

/**
 * Computes marginal binarization probability p_i = P(s_i >= theta_i).
 */
export function computeMarginalProbability(
  mu: number,
  sigma: number,
  varId: string,
  config: SymnConfig = DEFAULT_CONFIG,
): number {
  const threshold = config.variables.thresholds[varId];
  if (threshold === undefined) {
    throw new Error(`Unknown variable ID: ${varId}`);
  }
  const sigmaFloor = config.variables.sigma_floor;
  const sigmaClamped = Math.max(sigmaFloor, sigma);
  const z = (mu - threshold) / sigmaClamped;
  return normalCdf(z);
}

/**
 * Computes marginal probabilities for all 8 variables given (mu, sigma) posteriors.
 */
export function computeAllMarginalProbabilities(
  posteriors: Record<string, readonly [number, number]>,
  config: SymnConfig = DEFAULT_CONFIG,
): Record<string, number> {
  const vars = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"] as const;
  const result: Record<string, number> = {};
  for (const v of vars) {
    const post = posteriors[v];
    if (!post) {
      throw new Error(`Missing posterior distribution for variable ${v}`);
    }
    result[v] = computeMarginalProbability(post[0], post[1], v, config);
  }
  return result;
}
