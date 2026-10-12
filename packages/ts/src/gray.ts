/**
 * Binary-reflected Gray code operations and bijections for Symnoesis.
 *
 * Normative implementation of SPEC §4:
 *   gray(k) = k ^ (k >> 1)
 *   gray_inv(g) = fold g with shifts (1, 2, 4, 8)
 */

/**
 * Computes binary-reflected Gray code for non-negative integer k: G(k) = k ^ (k >> 1).
 */
export function intToGray(k: number): number {
  if (!Number.isInteger(k) || k < 0) {
    raiseValueError(`k must be a non-negative integer, got ${k}`);
  }
  return k ^ (k >> 1);
}

/**
 * Computes the inverse Gray code: recovers k such that intToGray(k) === g.
 */
export function grayToInt(g: number): number {
  if (!Number.isInteger(g) || g < 0) {
    raiseValueError(`g must be a non-negative integer, got ${g}`);
  }
  let n = g;
  let shift = 1;
  while (n >> shift > 0) {
    n ^= n >> shift;
    shift <<= 1;
  }
  return n;
}

/**
 * Converts an integer to a big-endian array of bits of length bitWidth.
 */
export function intToBits(val: number, bitWidth = 4): number[] {
  if (!Number.isInteger(val) || val < 0 || val >= 1 << bitWidth) {
    raiseValueError(`Value ${val} cannot fit in ${bitWidth} bits`);
  }
  const bits: number[] = new Array(bitWidth);
  for (let i = 0; i < bitWidth; i++) {
    bits[i] = (val >> (bitWidth - 1 - i)) & 1;
  }
  return bits;
}

/**
 * Converts a big-endian list of bits to an integer.
 */
export function bitsToInt(bits: readonly number[]): number {
  let val = 0;
  for (const b of bits) {
    if (b !== 0 && b !== 1) {
      raiseValueError(`Bits must be 0 or 1, got ${b}`);
    }
    val = (val << 1) | b;
  }
  return val;
}

/**
 * Computes Hamming distance (number of bit differences) between two integers.
 */
export function hammingDistance(a: number, b: number): number {
  let diff = (a ^ b) >>> 0;
  let count = 0;
  while (diff > 0) {
    diff &= diff - 1;
    count++;
  }
  return count;
}

/**
 * Returns true if index1 and index2 are neighbors on a 1D grid with periodic boundary.
 */
export function isAdjacentOnTorus(
  index1: number,
  index2: number,
  size = 16,
): boolean {
  const diff = (((index1 - index2) % size) + size) % size;
  return diff === 1 || diff === size - 1;
}

function raiseValueError(msg: string): never {
  throw new Error(msg);
}
