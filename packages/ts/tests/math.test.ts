import { describe, expect, it } from "vitest";
import { erfc, normalCdf } from "../src/index.js";

describe("Cody rational Chebyshev erfc and normalCdf", () => {
  const referencePoints = [
    { x: -5.0, expected: 2.86651571879193277e-7 },
    { x: -3.0, expected: 1.34989803163009328e-3 },
    { x: -2.0, expected: 2.27501319481791947e-2 },
    { x: -1.0, expected: 1.58655253931457074e-1 },
    { x: -0.5, expected: 3.08537538725986882e-1 },
    { x: -0.2, expected: 4.20740290560896957e-1 },
    { x: 0.0, expected: 0.5 },
    { x: 0.2, expected: 5.79259709439102988e-1 },
    { x: 0.5, expected: 6.91462461274013118e-1 },
    { x: 1.0, expected: 8.41344746068542926e-1 },
    { x: 2.0, expected: 9.77249868051820791e-1 },
    { x: 3.0, expected: 9.98650101968369897e-1 },
    { x: 5.0, expected: 9.99999713348428076e-1 },
  ];

  it("matches scipy.special.ndtr within 1e-9 across reference points", () => {
    for (const pt of referencePoints) {
      const actual = normalCdf(pt.x);
      const diff = Math.abs(actual - pt.expected);
      expect(diff).toBeLessThan(1e-9);
    }
  });

  it("satisfies symmetry: normalCdf(x) + normalCdf(-x) === 1.0", () => {
    const testValues = [0.1, 0.5, 1.25, 2.5, 4.0];
    for (const x of testValues) {
      expect(normalCdf(x) + normalCdf(-x)).toBeCloseTo(1.0, 10);
    }
  });

  it("handles edge cases: infinities, NaN", () => {
    expect(normalCdf(Number.POSITIVE_INFINITY)).toBe(1.0);
    expect(normalCdf(Number.NEGATIVE_INFINITY)).toBe(0.0);
    expect(Number.isNaN(normalCdf(Number.NaN))).toBe(true);
    expect(Number.isNaN(erfc(Number.NaN))).toBe(true);
  });
});
