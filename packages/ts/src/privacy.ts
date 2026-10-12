/**
 * Privacy and Telemetry Engine (SPEC §16).
 *
 * Implements:
 * - Pseudonymous identity hashing (salted SHA-256)
 * - Raw conversational text rejection
 * - k-Anonymity cell suppression (k_min = 10 floor)
 * - Differential privacy via the Laplace mechanism (epsilon = 1.0)
 * - Informed consent revocation filtering
 */

export const PROHIBITED_TEXT_KEYS: ReadonlySet<string> = new Set([
  "raw_text",
  "message_body",
  "raw_prompt",
  "raw_response",
  "prompt",
  "response",
  "user_message",
  "assistant_message",
  "text",
  "content",
  "body",
]);

/**
 * Standard pure SHA-256 implementation for deterministic, zero-dependency hashing.
 */
function sha256(ascii: string): string {
  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]);

  const H = new Uint32Array([
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c,
    0x1f83d9ab, 0x5be0cd19,
  ]);

  const bytes: number[] = [];
  for (let i = 0; i < ascii.length; i++) {
    const code = ascii.charCodeAt(i);
    if (code < 0x80) {
      bytes.push(code);
    } else if (code < 0x800) {
      bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f));
    } else {
      bytes.push(
        0xe0 | (code >> 12),
        0x80 | ((code >> 6) & 0x3f),
        0x80 | (code & 0x3f),
      );
    }
  }

  const bitLen = bytes.length * 8;
  bytes.push(0x80);
  while ((bytes.length + 8) % 64 !== 0) {
    bytes.push(0);
  }
  for (let i = 7; i >= 0; i--) {
    bytes.push((bitLen >>> (i * 8)) & 0xff);
  }

  const W = new Uint32Array(64);
  const rotr = (x: number, n: number): number => (x >>> n) | (x << (32 - n));

  for (let chunk = 0; chunk < bytes.length; chunk += 64) {
    for (let i = 0; i < 16; i++) {
      const b0 = bytes[chunk + i * 4] ?? 0;
      const b1 = bytes[chunk + i * 4 + 1] ?? 0;
      const b2 = bytes[chunk + i * 4 + 2] ?? 0;
      const b3 = bytes[chunk + i * 4 + 3] ?? 0;
      W[i] = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3;
    }
    for (let i = 16; i < 64; i++) {
      const w15 = W[i - 15] ?? 0;
      const s0 = rotr(w15, 7) ^ rotr(w15, 18) ^ (w15 >>> 3);
      const w2 = W[i - 2] ?? 0;
      const s1 = rotr(w2, 17) ^ rotr(w2, 19) ^ (w2 >>> 10);
      W[i] = ((W[i - 16] ?? 0) + s0 + (W[i - 7] ?? 0) + s1) >>> 0;
    }

    let a = H[0] ?? 0;
    let b = H[1] ?? 0;
    let c = H[2] ?? 0;
    let d = H[3] ?? 0;
    let e = H[4] ?? 0;
    let f = H[5] ?? 0;
    let g = H[6] ?? 0;
    let h = H[7] ?? 0;

    for (let i = 0; i < 64; i++) {
      const s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + s1 + ch + (K[i] ?? 0) + (W[i] ?? 0)) >>> 0;
      const s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (s0 + maj) >>> 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    H[0] = ((H[0] ?? 0) + a) >>> 0;
    H[1] = ((H[1] ?? 0) + b) >>> 0;
    H[2] = ((H[2] ?? 0) + c) >>> 0;
    H[3] = ((H[3] ?? 0) + d) >>> 0;
    H[4] = ((H[4] ?? 0) + e) >>> 0;
    H[5] = ((H[5] ?? 0) + f) >>> 0;
    H[6] = ((H[6] ?? 0) + g) >>> 0;
    H[7] = ((H[7] ?? 0) + h) >>> 0;
  }

  let hex = "";
  for (let i = 0; i < 8; i++) {
    const v = H[i] ?? 0;
    hex += v.toString(16).padStart(8, "0");
  }
  return hex;
}

/**
 * Generate a pseudonymous ID using salted SHA-256.
 */
export function pseudonymizeId(
  rawId: string,
  salt = "symnoesis-v0.1-salt",
): string {
  const digest = sha256(salt + rawId);
  return `anon_${digest.slice(0, 16)}`;
}

/**
 * Reject payloads containing prohibited raw text keys.
 */
export function validateNoRawText(payload: Record<string, unknown>): void {
  for (const [key, value] of Object.entries(payload)) {
    if (PROHIBITED_TEXT_KEYS.has(key)) {
      throw new Error(
        `Prohibited raw text key '${key}' detected. Raw text persistence is forbidden.`,
      );
    }
    if (value && typeof value === "object" && !Array.isArray(value)) {
      validateNoRawText(value as Record<string, unknown>);
    } else if (Array.isArray(value)) {
      for (const item of value) {
        if (item && typeof item === "object") {
          validateNoRawText(item as Record<string, unknown>);
        }
      }
    }
  }
}

/**
 * Sanitize turn features, ensuring only numeric or boolean values remain.
 */
export function sanitizeTurnFeatures(
  rawFeatures: Record<string, unknown>,
): Record<string, number | boolean> {
  validateNoRawText(rawFeatures);
  const result: Record<string, number | boolean> = {};
  for (const [k, v] of Object.entries(rawFeatures)) {
    if (typeof v === "number" || typeof v === "boolean") {
      result[k] = v;
    }
  }
  return result;
}

/**
 * Enforce k-anonymity privacy floor via cell suppression.
 */
export function applyKAnonymity<T extends Record<string, unknown>>(
  records: T[],
  kMin = 10.0,
  countKey = "n_eff",
  valueKey = "sq",
): T[] {
  return records.map((rec) => {
    const copy = { ...rec };
    const count = copy[countKey] as number | undefined;
    if (count === undefined || count === null || count < kMin) {
      (copy as Record<string, unknown>)[valueKey] = null;
      (copy as Record<string, unknown>)["suppressed"] = true;
    } else {
      (copy as Record<string, unknown>)["suppressed"] = false;
    }
    return copy;
  });
}

/**
 * Perturb a scalar count with Laplace noise.
 */
export function addLaplaceNoise(
  value: number,
  epsilon = 1.0,
  sensitivity = 1.0,
  rng: () => number = Math.random,
  minVal: number | null = 0.0,
): number {
  if (epsilon <= 0.0) {
    throw new Error(
      `Privacy budget epsilon must be strictly positive, got ${epsilon}`,
    );
  }
  if (sensitivity <= 0.0) {
    throw new Error(
      `Sensitivity must be strictly positive, got ${sensitivity}`,
    );
  }

  const scaleB = sensitivity / epsilon;
  const u = rng();
  const sign = u >= 0.5 ? 1.0 : -1.0;
  // Expovariate: -ln(1 - U) * scaleB
  const uniform = Math.max(1e-12, rng());
  const expSample = -Math.log(uniform) * scaleB;
  const noise = sign * expSample;

  let perturbed = value + noise;
  if (minVal !== null) {
    perturbed = Math.max(minVal, perturbed);
  }
  return perturbed;
}

/**
 * Perturb an array of counts with Laplace differential privacy.
 */
export function applyDifferentialPrivacy(
  counts: number[],
  epsilon = 1.0,
  sensitivity = 1.0,
  rng: () => number = Math.random,
  minVal: number | null = 0.0,
): number[] {
  if (epsilon <= 0.0) {
    throw new Error(
      `Privacy budget epsilon must be strictly positive, got ${epsilon}`,
    );
  }
  return counts.map((c) =>
    addLaplaceNoise(c, epsilon, sensitivity, rng, minVal),
  );
}

/**
 * Filter records to only retain subjects with granted consent.
 */
export function filterConsentingRecords<T extends Record<string, unknown>>(
  records: T[],
  consents: Record<string, boolean>,
  idKey = "human_id_pseudonym",
): T[] {
  return records.filter((rec) => consents[String(rec[idKey])] === true);
}
