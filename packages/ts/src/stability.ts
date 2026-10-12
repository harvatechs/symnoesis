/**
 * Stability factor S calculation and harm asymmetry override.
 *
 * Normative implementation of SPEC §6 and ADR-0004:
 *   S = 0.5 + 0.5 * (1 - min(1, sigma_C / sigma_max))
 *   S_eff = S if C >= 0 else 1.0 (Harm asymmetry: instability never softens harm)
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

/**
 * Computes unbiased sample standard deviation (ddof = 1).
 */
export function computeSampleStd(values: readonly number[]): number {
  const n = values.length;
  if (n < 2) {
    return 0.0;
  }
  let sum = 0.0;
  for (const v of values) {
    sum += v;
  }
  const mean = sum / n;
  let sumSq = 0.0;
  for (const v of values) {
    const diff = v - mean;
    sumSq += diff * diff;
  }
  return Math.sqrt(sumSq / (n - 1));
}

/**
 * Computes stability factor S in [0.5, 1.0].
 */
export function computeStabilityFactor(
  sigmaC: number,
  config: SymnConfig = DEFAULT_CONFIG,
): number {
  const sigmaMax = config.sq.stability.sigma_max;
  const ratio = Math.min(1.0, Math.max(0.0, sigmaC) / sigmaMax);
  return 0.5 + 0.5 * (1.0 - ratio);
}

/**
 * Computes effective stability factor S_eff applying harm asymmetry override:
 * if C >= 0 then S else 1.0.
 */
export function computeEffectiveStability(c: number, s: number): number {
  if (c < 0.0) {
    return 1.0;
  }
  return s;
}
