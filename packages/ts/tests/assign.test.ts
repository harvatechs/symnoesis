import { describe, expect, it } from "vitest";
import {
  computeDyadWindowMasses,
  computeMarginalProbability,
  getModalPixel,
} from "../src/index.js";

describe("Probabilistic Assignment", () => {
  it("renormalized cell masses sum to 1.0", () => {
    const posteriors = {
      H1: 0.6,
      H2: 0.45,
      H3: 0.5,
      H4: 0.7,
      M1: 0.8,
      M2: 0.3,
      M3: 0.5,
      M4: 0.65,
    };
    const masses = computeDyadWindowMasses(posteriors);
    let total = 0.0;
    for (const m of Object.values(masses)) {
      total += m;
      expect(m).toBeGreaterThanOrEqual(1e-4);
    }
    expect(total).toBeCloseTo(1.0, 9);
  });

  it("identifies modal pixel under sharp probabilities", () => {
    // Sharp probabilities near 1.0 for all bits
    const sharpPosteriors = {
      H1: 0.999,
      H2: 0.999,
      H3: 0.999,
      H4: 0.999,
      M1: 0.999,
      M2: 0.999,
      M3: 0.999,
      M4: 0.999,
    };
    const masses = computeDyadWindowMasses(sharpPosteriors);
    const modal = getModalPixel(masses);
    expect(modal).toBe("h1111-m1111");
  });

  it("clamps sigma to sigma_floor = 0.01", () => {
    const p1 = computeMarginalProbability(0.5, 0.0001, "H1");
    const p2 = computeMarginalProbability(0.5, 0.01, "H1");
    expect(p1).toBeCloseTo(p2, 9);
  });
});
