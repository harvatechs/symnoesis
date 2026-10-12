/**
 * Governance zone assignment and precedence pipeline.
 *
 * Normative implementation of SPEC §9:
 *   Zones in strict precedence:
 *     1. Z7 Critical: confirmed CHI event in pixel
 *     2. Z6 Harm: SQ <= -25
 *     3. Z5 Dependence: (H1 == 0 or H4 == 0) and M2 == 0 (pixel bits)
 *     4. Z4 Drift: Trajectory negative
 *     5. Z1 Symbiotic: SQ >= +60, trajectory not negative
 *     6. Z2 Productive: +25 <= SQ < +60
 *     7. Z3 Neutral: -25 < SQ < +25
 *
 * All matching conditions are returned as secondary_tags.
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

export interface ZoneResult {
  readonly primary: string;
  readonly secondary_tags: readonly string[];
}

/**
 * Evaluates primary governance zone and secondary tags.
 */
export function evaluateZones(
  sq: number | null,
  hBits?: readonly number[] | null,
  mBits?: readonly number[] | null,
  hasConfirmedChi = false,
  isTrajectoryNegative = false,
  config: SymnConfig = DEFAULT_CONFIG,
): ZoneResult {
  const matches: string[] = [];

  // 1. Z7 Critical
  if (hasConfirmedChi) {
    matches.push("Z7");
  }

  // 2. Z6 Harm
  if (sq !== null && sq <= config.zones.z6_max) {
    matches.push("Z6");
  }

  // 3. Z5 Dependence: (H1 == 0 or H4 == 0) and M2 == 0
  if (hBits && mBits && hBits.length === 4 && mBits.length === 4) {
    const h1 = hBits[0]!;
    const h4 = hBits[3]!;
    const m2 = mBits[1]!;
    if ((h1 === 0 || h4 === 0) && m2 === 0) {
      matches.push("Z5");
    }
  }

  // 4. Z4 Drift
  if (isTrajectoryNegative) {
    matches.push("Z4");
  }

  // 5. Z1 Symbiotic: SQ >= +60, trajectory not negative
  if (sq !== null && sq >= config.zones.z1_min && !isTrajectoryNegative) {
    matches.push("Z1");
  }

  // 6. Z2 Productive: +25 <= SQ < +60
  if (sq !== null && sq >= config.zones.z2_min && sq < config.zones.z1_min) {
    matches.push("Z2");
  }

  // 7. Z3 Neutral: -25 < SQ < +25
  if (sq !== null && sq > config.zones.z6_max && sq < config.zones.z2_min) {
    matches.push("Z3");
  }

  const precedence = config.zones.precedence;
  let primary = "Z3";
  for (const z of precedence) {
    if (matches.includes(z)) {
      primary = z;
      break;
    }
  }

  const secondary = matches.filter((z) => z !== primary);
  return {
    primary,
    secondary_tags: secondary,
  };
}
