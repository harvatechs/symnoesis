import { describe, expect, it } from "vitest";
import { DEFAULT_CONFIG } from "../src/config.js";
import {
  computeIntervalDeltas,
  computeMdc,
  computeSem,
  evaluateTrajectory,
  isBaselineFrame,
  isTrajectoryNegative,
} from "../src/temporal.js";
import { evaluateZones } from "../src/zones.js";

describe("Longitudinal Temporal Engine & Trajectory Diagnostics (SPEC §9, §10)", () => {
  it("TC1.19.01: standard observation windows are days 1, 7, 28, 84, 182", () => {
    const frames = DEFAULT_CONFIG.temporal.frames_days;
    expect(frames).toEqual([1, 7, 28, 84, 182]);
    expect(frames).toHaveLength(5);
    expect(frames[0]).toBe(1);
  });

  it("TC1.19.02: Frame 1 is tagged as baseline", () => {
    expect(isBaselineFrame(1)).toBe(true);
    expect(isBaselineFrame(7)).toBe(false);
    expect(isBaselineFrame(28)).toBe(false);
  });

  it("TC1.19.03: computeIntervalDeltas calculates consecutive differences", () => {
    const deltas = computeIntervalDeltas([20.0, 24.0, 18.0]);
    expect(deltas).toEqual([4.0, -6.0]);
    expect(computeIntervalDeltas([30.0])).toEqual([]);
  });

  it("TC1.20.01 & TC1.20.02: SEM = SD * sqrt(1 - r) and MDC = 1.96 * sqrt(2) * SEM", () => {
    // SEM
    const sd = 10.0;
    const r = 0.84;
    const sem = computeSem(sd, r);
    expect(Math.abs(sem - 4.0)).toBeLessThan(1e-12);

    expect(() => computeSem(-1.0, 0.8)).toThrow();
    expect(() => computeSem(10.0, 1.2)).toThrow();

    // MDC with given sem = 2.0
    const mdc = computeMdc(2.0);
    const expectedMdc = 1.96 * Math.SQRT2 * 2.0;
    expect(Math.abs(mdc - expectedMdc)).toBeLessThan(1e-12);
    expect(Math.abs(mdc - 5.5437)).toBeLessThan(1e-3);

    // MDC with sd and r
    const mdcSdr = computeMdc(undefined, 10.0, 0.84);
    expect(Math.abs(mdcSdr - 1.96 * Math.SQRT2 * 4.0)).toBeLessThan(1e-12);

    // Default placeholder
    expect(computeMdc()).toBe(5.0);
  });

  it("TC1.19.05: two consecutive drops > MDC classifies trajectory as deteriorating / negative", () => {
    // Drops of -6.0 and -7.0 (> MDC 5.0) -> negative
    const scores = [30.0, 24.0, 17.0];
    const res = evaluateTrajectory(scores, undefined, 5.0);
    expect(res.status).toBe("deteriorating");
    expect(res.status_code).toBe("negative");
    expect(res.is_negative).toBe(true);
    expect(res.is_improving).toBe(false);
    expect(res.is_stable).toBe(false);
    expect(isTrajectoryNegative(scores, 5.0)).toBe(true);
  });

  it("TC1.19.06: two consecutive gains > MDC classifies trajectory as improving / positive", () => {
    // Gains of +6.0 and +7.0 (> MDC 5.0) -> improving
    const scores = [20.0, 26.0, 33.0];
    const res = evaluateTrajectory(scores, undefined, 5.0);
    expect(res.status).toBe("improving");
    expect(res.status_code).toBe("positive");
    expect(res.is_improving).toBe(true);
    expect(res.is_negative).toBe(false);
  });

  it("TC1.20.04: single drop > MDC followed by recovery remains stable", () => {
    // Drop of -8.0 followed by +5.0 -> stable
    const scores = [30.0, 22.0, 27.0];
    const res = evaluateTrajectory(scores, undefined, 5.0);
    expect(res.status).toBe("stable");
    expect(res.status_code).toBe("stable");
    expect(res.is_negative).toBe(false);
    expect(res.is_improving).toBe(false);
    expect(res.is_stable).toBe(true);
  });

  it("TC2.19.01: sequence of only 2 frames returns stable", () => {
    const scores = [30.0, 10.0];
    const res = evaluateTrajectory(scores, undefined, 5.0);
    expect(res.status).toBe("stable");
    expect(res.is_negative).toBe(false);
  });

  it("TC2.20.01: drop of exactly -5.000 does not exceed MDC; -5.001 does", () => {
    const mdc = 5.0;
    // Exactly -5.000 drops: 40 -> 35 -> 30
    const exactRes = evaluateTrajectory([40.0, 35.0, 30.0], undefined, mdc);
    expect(exactRes.status).toBe("stable");

    // Exceeding drops: 40 -> 34.999 (-5.001) -> 29.998 (-5.001)
    const exceedRes = evaluateTrajectory(
      [40.0, 34.999, 29.998],
      undefined,
      mdc,
    );
    expect(exceedRes.status).toBe("deteriorating");
    expect(exceedRes.is_negative).toBe(true);
  });

  it("TC1.20.05: negative trajectory triggers governance zone Z4 Drift", () => {
    const isNeg = isTrajectoryNegative([40.0, 34.999, 29.998], 5.0);
    expect(isNeg).toBe(true);

    const zoneRes = evaluateZones(
      45.0, // normally Z2 Productive (25 <= SQ < 60)
      [1, 1, 1, 1],
      [1, 1, 1, 1],
      false,
      isNeg,
    );
    expect(zoneRes.primary).toBe("Z4");
    expect(zoneRes.secondary_tags).toContain("Z2");
  });
});
