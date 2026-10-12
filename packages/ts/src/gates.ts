/**
 * Critical Harm Indicator (CHI) safety gate evaluation and ceiling extraction.
 *
 * Normative implementation of SPEC §7:
 *   G in [0.0, 0.25] caps SQ_raw: SQ = min(SQ_raw, 100 * G).
 *   Status: critical (>= 1 confirmed), watch (>= 1 unconfirmed),
 *           safe (none with n_eff >= n_cell_min), unknown (insufficient data).
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";

export type GateStatus = "critical" | "watch" | "safe" | "unknown";

/**
 * Evaluates safety gate status and ceiling G.
 * Returns [gateCeiling, gateStatus].
 */
export function evaluateSafetyGate(
  confirmedChis?: readonly string[] | null,
  watchChis?: readonly string[] | null,
  nEff = 0.0,
  config: SymnConfig = DEFAULT_CONFIG,
): [number | null, GateStatus] {
  const ceilings = config.sq.gate_ceilings;

  if (confirmedChis && confirmedChis.length > 0) {
    let minCeiling = 1.0;
    for (const chi of confirmedChis) {
      const c = ceilings[chi];
      if (c === undefined) {
        throw new Error(`Unrecognized CHI indicator: ${chi}`);
      }
      if (c < minCeiling) {
        minCeiling = c;
      }
    }
    return [minCeiling, "critical"];
  }

  if (watchChis && watchChis.length > 0) {
    return [null, "watch"];
  }

  if (nEff >= config.layout.n_cell_min) {
    return [null, "safe"];
  }

  return [null, "unknown"];
}
