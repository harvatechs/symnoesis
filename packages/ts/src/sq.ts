/**
 * Symnoesis Quotient (SQ) composite calculation and clipping.
 *
 * Normative implementation of SPEC §6:
 *   SQ_raw = 100 * C * S_eff
 *   SQ = min(SQ_raw, 100 * G) if gate triggered else SQ_raw
 *   SQ = clip(SQ, -100, +100)
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";
import { computeEffectiveStability } from "./stability.js";

export interface SqResult {
  readonly sq: number;
  readonly sqRaw: number;
  readonly gateTriggered: boolean;
}

/**
 * Computes SQ from composite C, stability S, and optional gate ceiling G.
 * Returns tuple [sqClipped, sqRaw, gateTriggered].
 */
export function computeSq(
  c: number,
  s: number,
  gateCeiling?: number | null,
  config: SymnConfig = DEFAULT_CONFIG,
): [number, number, boolean] {
  const sEff = computeEffectiveStability(c, s);
  const sqRaw = 100.0 * c * sEff;

  const gateTriggered = gateCeiling !== null && gateCeiling !== undefined;
  let sqVal = sqRaw;
  if (gateTriggered) {
    if (config.sq.gate_mode === "ceiling") {
      sqVal = Math.min(sqRaw, 100.0 * gateCeiling);
    } else {
      sqVal = sqRaw * gateCeiling;
    }
  }

  const sqClipped = Math.max(-100.0, Math.min(100.0, sqVal));
  return [sqClipped, sqRaw, gateTriggered];
}
