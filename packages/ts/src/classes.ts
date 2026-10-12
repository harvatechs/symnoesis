/**
 * Ecological symbiosis classes and plain-language public mappings.
 *
 * Normative implementation of SPEC §8:
 *   h = sign3(HNE), s = sign3(SNE)
 *   sign3(x) = '+' if x > 0.2, '-' if x < -0.2 else '0'
 *
 * If operator_blind is true, Parasitism (-, +) falls back to Amensalism (-, 0) with caveat.
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

export type Sign3 = "+" | "0" | "-";

export interface SymbiosisClassResult {
  readonly technical_name: string;
  readonly public_label: string;
  readonly h_sign: Sign3;
  readonly s_sign: Sign3;
  readonly operator_blind_applied: boolean;
}

const CLASS_MATRIX: Record<string, readonly [string, string]> = {
  "++": ["mutualism", "Mutual benefit"],
  "+0": ["commensalism", "Human benefits"],
  "+-": ["sacrificial", "Human benefits at system cost"],
  "0+": ["inverse_commensalism", "System benefits"],
  "00": ["neutralism", "Neutral"],
  "0-": ["antagonism", "System harmed"],
  "-+": ["parasitism", "Human harmed at system gain"],
  "-0": ["amensalism", "Human harmed"],
  "--": ["mutual_harm", "Both harmed"],
};

/**
 * Computes 3-way sign with hysteresis threshold.
 */
export function computeSign3(x: number, threshold = 0.2): Sign3 {
  if (x > threshold) {
    return "+";
  }
  if (x < -threshold) {
    return "-";
  }
  return "0";
}

/**
 * Classifies dyad or pixel into 9-cell symbiosis matrix.
 */
export function classifySymbiosis(
  hne: number,
  sne: number,
  operatorBlind = false,
  config: SymnConfig = DEFAULT_CONFIG,
): SymbiosisClassResult {
  const threshold = config.classes.threshold;
  const hSign = computeSign3(hne, threshold);
  const sSign = computeSign3(sne, threshold);

  let effectiveSSign = sSign;
  let blindApplied = false;

  // SPEC §8 / ADR-0005: Parasitism MUST NOT be asserted when operatorBlind is true.
  if (operatorBlind && hSign === "-" && sSign === "+") {
    effectiveSSign = "0";
    blindApplied = true;
  }

  const key = `${hSign}${effectiveSSign}`;
  const match = CLASS_MATRIX[key];
  if (!match) {
    throw new Error(`Unexpected sign combination: ${key}`);
  }

  return {
    technical_name: match[0],
    public_label: match[1],
    h_sign: hSign,
    s_sign: sSign,
    operator_blind_applied: blindApplied,
  };
}
