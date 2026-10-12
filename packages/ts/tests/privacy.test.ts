import { describe, expect, it } from "vitest";
import {
  addLaplaceNoise,
  applyDifferentialPrivacy,
  applyKAnonymity,
  filterConsentingRecords,
  pseudonymizeId,
  sanitizeTurnFeatures,
  validateNoRawText,
} from "../src/privacy.js";

describe("Privacy and Telemetry Protection (TypeScript)", () => {
  it("generates deterministic pseudonyms matching expected SHA-256 structure", () => {
    const p1 = pseudonymizeId("user_12345");
    const p2 = pseudonymizeId("user_12345");
    const p3 = pseudonymizeId("user_99999");
    expect(p1).toBe(p2);
    expect(p1.startsWith("anon_")).toBe(true);
    expect(p1).not.toBe(p3);
    expect(p1.length).toBe(21); // "anon_" (5) + 16 chars = 21
  });

  it("rejects prohibited raw text keys in telemetry payloads", () => {
    expect(() => validateNoRawText({ raw_text: "hello world" })).toThrow(
      /Prohibited raw text key/,
    );
    expect(() => validateNoRawText({ message_body: "hello" })).toThrow(
      /Prohibited raw text key/,
    );
    expect(() =>
      validateNoRawText({ nested: { prompt: "user query" } }),
    ).toThrow(/Prohibited raw text key/);

    // Clean payload does not throw
    expect(() =>
      validateNoRawText({
        turn_index: 1,
        features: { latency_ms: 250, brevity: 0.8 },
      }),
    ).not.toThrow();
  });

  it("sanitizes turn features retaining only numerical and boolean values", () => {
    const raw = {
      latency_ms: 120,
      brevity: 0.65,
      is_unaided: true,
      metadata: "some non-prohibited string",
    };
    const sanitized = sanitizeTurnFeatures(raw);
    expect(sanitized).toEqual({
      latency_ms: 120,
      brevity: 0.65,
      is_unaided: true,
    });
  });

  it("enforces k-anonymity suppression floor at k_min = 10", () => {
    const records = [
      { cell: 1, n_eff: 9.999, sq: 42.0 },
      { cell: 2, n_eff: 10.0, sq: 55.0 },
      { cell: 3, n_eff: 15.2, sq: 18.5 },
    ];
    const anonymized = applyKAnonymity(records, 10.0);

    expect(anonymized[0]?.suppressed).toBe(true);
    expect(anonymized[0]?.sq).toBeNull();

    expect(anonymized[1]?.suppressed).toBe(false);
    expect(anonymized[1]?.sq).toBe(55.0);

    expect(anonymized[2]?.suppressed).toBe(false);
    expect(anonymized[2]?.sq).toBe(18.5);
  });

  it("raises error for non-positive differential privacy budget", () => {
    expect(() => addLaplaceNoise(10.0, 0.0)).toThrow(/strictly positive/);
    expect(() => addLaplaceNoise(10.0, -1.0)).toThrow(/strictly positive/);
    expect(() => applyDifferentialPrivacy([10.0], 0.0)).toThrow(
      /strictly positive/,
    );
  });

  it("perturbs counts under differential privacy with non-negative clamp", () => {
    const counts = [10.0, 20.0, 30.0];
    const perturbed = applyDifferentialPrivacy(
      counts,
      1.0,
      1.0,
      Math.random,
      0.0,
    );
    expect(perturbed.length).toBe(3);
    for (const val of perturbed) {
      expect(val).toBeGreaterThanOrEqual(0.0);
    }
  });

  it("filters records to exclude revoked or absent consent", () => {
    const records = [
      { human_id_pseudonym: "anon_user_1", metric: 1.0 },
      { human_id_pseudonym: "anon_user_2", metric: 2.0 },
      { human_id_pseudonym: "anon_user_3", metric: 3.0 },
    ];
    const consents = {
      anon_user_1: true,
      anon_user_2: false, // revoked
    };
    const filtered = filterConsentingRecords(records, consents);
    expect(filtered.length).toBe(1);
    expect(filtered[0]?.human_id_pseudonym).toBe("anon_user_1");
  });
});
