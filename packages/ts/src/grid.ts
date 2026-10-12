/**
 * 16x16 Gray-coded Grid coordinate system and pixel ID utilities.
 *
 * Normative implementation of SPEC §4:
 *   - Columns index Human code (H1, H2, H3, H4) in Gray order.
 *   - Rows index Machine code (M1, M2, M3, M4) in Gray order.
 *   - Pixel ID format: h{HHHH}-m{MMMM}
 */

import { bitsToInt, grayToInt, intToBits, intToGray } from "./gray.js";

export const PIXEL_ID_PATTERN = /^h([01]{4})-m([01]{4})$/;

export interface PixelCoord {
  readonly col: number; // 0..15 (Human code index)
  readonly row: number; // 0..15 (Machine code index)
}

export interface PixelBits {
  readonly H: readonly number[]; // [H1, H2, H3, H4]
  readonly M: readonly number[]; // [M1, M2, M3, M4]
}

/**
 * Constructs pixel ID from bit arrays.
 */
export function pixelIdFromBits(
  hBits: readonly number[],
  mBits: readonly number[],
): string {
  if (hBits.length !== 4 || mBits.length !== 4) {
    throw new Error("H and M bits must both have length 4");
  }
  const hStr = hBits.join("");
  const mStr = mBits.join("");
  return `h${hStr}-m${mStr}`;
}

/**
 * Parses a pixel ID into [hBits, mBits].
 */
export function parsePixelId(pixelId: string): [number[], number[]] {
  const match = PIXEL_ID_PATTERN.exec(pixelId);
  if (!match || match[1] === undefined || match[2] === undefined) {
    throw new Error(
      `Invalid pixel ID format: ${pixelId}. Expected format hXXXX-mYYYY.`,
    );
  }
  const hBits = match[1].split("").map((b) => Number.parseInt(b, 10));
  const mBits = match[2].split("").map((b) => Number.parseInt(b, 10));
  return [hBits, mBits];
}

/**
 * Converts grid coordinate (col, row) to pixel ID string using Gray code.
 */
export function coordToPixelId(coord: PixelCoord): string {
  if (coord.col < 0 || coord.col >= 16 || coord.row < 0 || coord.row >= 16) {
    throw new Error(
      `Coordinates out of bounds [0, 15]: col=${coord.col}, row=${coord.row}`,
    );
  }
  const hCode = intToGray(coord.col);
  const mCode = intToGray(coord.row);
  const hBits = intToBits(hCode, 4);
  const mBits = intToBits(mCode, 4);
  return pixelIdFromBits(hBits, mBits);
}

/**
 * Converts grid coordinates to pixel ID string (supports (col, row) or PixelCoord).
 */
export function pixelCoordToId(
  colOrCoord: number | PixelCoord,
  row?: number,
): string {
  if (typeof colOrCoord === "object") {
    return coordToPixelId(colOrCoord);
  }
  if (row === undefined) {
    throw new Error("row must be provided when col is a number");
  }
  return coordToPixelId({ col: colOrCoord, row });
}

/**
 * Converts pixel ID to grid coordinate (col, row).
 */
export function pixelIdToCoord(pixelId: string): PixelCoord {
  const [hBits, mBits] = parsePixelId(pixelId);
  const hCode = bitsToInt(hBits);
  const mCode = bitsToInt(mBits);
  const col = grayToInt(hCode);
  const row = grayToInt(mCode);
  return { col, row };
}

/**
 * Returns the 4 visual grid-adjacent neighbors on periodic boundary (torus).
 */
export function getGridNeighbors(coord: PixelCoord): PixelCoord[] {
  const c = coord.col;
  const r = coord.row;
  return [
    { col: (c - 1 + 16) % 16, row: r },
    { col: (c + 1) % 16, row: r },
    { col: c, row: (r - 1 + 16) % 16 },
    { col: c, row: (r + 1) % 16 },
  ];
}

/**
 * Returns all 8 Hamming distance = 1 neighbors (4 human flips, 4 machine flips).
 */
export function getAllSingleFlipNeighbors(pixelId: string): string[] {
  const [hBits, mBits] = parsePixelId(pixelId);
  const neighbors: string[] = [];

  // 4 Human flips
  for (let i = 0; i < 4; i++) {
    const flippedH = [...hBits];
    const bit = flippedH[i];
    if (bit !== undefined) {
      flippedH[i] = bit ^ 1;
      neighbors.push(pixelIdFromBits(flippedH, mBits));
    }
  }

  // 4 Machine flips
  for (let i = 0; i < 4; i++) {
    const flippedM = [...mBits];
    const bit = flippedM[i];
    if (bit !== undefined) {
      flippedM[i] = bit ^ 1;
      neighbors.push(pixelIdFromBits(hBits, flippedM));
    }
  }

  return neighbors;
}
