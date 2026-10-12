/**
 * Probabilistic pixel assignment pipeline across the 256-pixel manifold.
 *
 * Normative implementation of SPEC §3:
 *   m(c) = Prod_i [ p_i if bit_i(c) == 1 else 1 - p_i ]
 *   Prune m(c) < prune_mass (default 1e-4) and renormalize remainder.
 *   Modal pixel = argmax_c m(c).
 */

import { DEFAULT_CONFIG, type SymnConfig } from "./config.js";
import { coordToPixelId, parsePixelId } from "./grid.js";

/**
 * Computes pruned and renormalized mass distribution m(c) over 256 pixels.
 */
export function computeDyadWindowMasses(
  pVars: Record<string, number>,
  config: SymnConfig = DEFAULT_CONFIG,
): Record<string, number> {
  const orderedVars = ["H1", "H2", "H3", "H4", "M1", "M2", "M3", "M4"] as const;
  const pList: number[] = [];
  for (const v of orderedVars) {
    const p = pVars[v];
    if (p === undefined) {
      throw new Error(`Missing probability for variable ${v}`);
    }
    pList.push(p);
  }

  const rawMasses: Record<string, number> = {};
  for (let row = 0; row < 16; row++) {
    for (let col = 0; col < 16; col++) {
      const pid = coordToPixelId({ col, row });
      const [hBits, mBits] = parsePixelId(pid);
      const bits = [...hBits, ...mBits];

      let mass = 1.0;
      for (let i = 0; i < 8; i++) {
        const bit = bits[i]!;
        const p = pList[i]!;
        const factor = bit === 1 ? p : 1.0 - p;
        mass *= factor;
      }
      rawMasses[pid] = mass;
    }
  }

  const pruneThreshold = config.assignment.prune_mass;
  const filtered: Record<string, number> = {};
  let totalSurviving = 0.0;

  for (const [pid, m] of Object.entries(rawMasses)) {
    if (m >= pruneThreshold) {
      filtered[pid] = m;
      totalSurviving += m;
    }
  }

  if (totalSurviving <= 0.0) {
    let maxPid = "h0000-m0000";
    let maxM = -1.0;
    for (const [pid, m] of Object.entries(rawMasses)) {
      if (m > maxM) {
        maxM = m;
        maxPid = pid;
      }
    }
    return { [maxPid]: 1.0 };
  }

  const normalized: Record<string, number> = {};
  for (const [pid, m] of Object.entries(filtered)) {
    normalized[pid] = m / totalSurviving;
  }
  return normalized;
}

/**
 * Finds the modal pixel (argmax_c m(c)).
 */
export function getModalPixel(pixelMasses: Record<string, number>): string {
  const entries = Object.entries(pixelMasses);
  if (entries.length === 0) {
    throw new Error("Cannot find modal pixel of empty mass mapping");
  }
  let bestPid = entries[0]![0];
  let bestMass = entries[0]![1];
  for (let i = 1; i < entries.length; i++) {
    const entry = entries[i]!;
    if (entry[1] > bestMass) {
      bestMass = entry[1];
      bestPid = entry[0];
    }
  }
  return bestPid;
}
