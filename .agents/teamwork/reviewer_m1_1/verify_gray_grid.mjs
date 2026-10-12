import fs from "fs";
import { intToGray, grayToInt, intToBits, bitsToInt } from "../../../packages/ts/dist/gray.js";
import {
  coordToPixelId,
  pixelCoordToId,
  pixelIdToCoord,
  getGridNeighbors,
  getAllSingleFlipNeighbors,
  parsePixelId,
  pixelIdFromBits,
} from "../../../packages/ts/dist/grid.js";

// 1. Verify Gray Code Golden Vector
const grayData = JSON.parse(fs.readFileSync("E:/Symnoesis/spec/vectors/gray-code-16.json", "utf-8"));
for (const elem of grayData.elements) {
  const idx = elem.index;
  const code = elem.code_int;
  const bits = elem.bits;
  if (intToGray(idx) !== code) throw new Error(`TS: intToGray(${idx}) !== ${code}`);
  if (grayToInt(code) !== idx) throw new Error(`TS: grayToInt(${code}) !== ${idx}`);
  const b = intToBits(code, 4);
  if (JSON.stringify(b) !== JSON.stringify(bits)) throw new Error(`TS: bits mismatch for ${code}`);
  if (bitsToInt(bits) !== code) throw new Error(`TS: bitsToInt mismatch for ${bits}`);
}

// Check bijection on full 16-bit range
for (let k = 0; k < 65536; k++) {
  const g = intToGray(k);
  const kRec = grayToInt(g);
  if (k !== kRec) throw new Error(`TS: Failed Gray bijection for ${k}`);
}
console.log("TypeScript Gray code bijection: PASS (all 16 golden elements + 0..65535)");

// 2. Verify 16x16 Grid Coordinates against grid-256-pixels.json
const gridData = JSON.parse(fs.readFileSync("E:/Symnoesis/spec/vectors/grid-256-pixels.json", "utf-8"));
if (gridData.pixels.length !== 256) throw new Error("Expected 256 pixels");

for (const p of gridData.pixels) {
  const pid = p.pixel_id;
  const col = p.col;
  const row = p.row;

  // coord -> pixel_id
  const computedId1 = coordToPixelId({ col, row });
  if (computedId1 !== pid) throw new Error(`coordToPixelId mismatch: ${computedId1} !== ${pid}`);

  const computedId2 = pixelCoordToId(col, row);
  if (computedId2 !== pid) throw new Error(`pixelCoordToId mismatch: ${computedId2} !== ${pid}`);

  // pixel_id -> coord
  const coord = pixelIdToCoord(pid);
  if (coord.col !== col || coord.row !== row) {
    throw new Error(`pixelIdToCoord mismatch: (${coord.col}, ${coord.row}) !== (${col}, ${row})`);
  }

  // Bits
  const [hBits, mBits] = parsePixelId(pid);
  if (JSON.stringify(hBits) !== JSON.stringify(p.h_bits)) throw new Error(`hBits mismatch for ${pid}`);
  if (JSON.stringify(mBits) !== JSON.stringify(p.m_bits)) throw new Error(`mBits mismatch for ${pid}`);

  const reconstructedId = pixelIdFromBits(hBits, mBits);
  if (reconstructedId !== pid) throw new Error(`pixelIdFromBits mismatch: ${reconstructedId} !== ${pid}`);

  // Visual grid neighbors (torus)
  const neighbors = getGridNeighbors({ col, row });
  if (neighbors.length !== 4) throw new Error("Expected 4 grid neighbors");

  // Single flip neighbors (Hamming distance 1)
  const flipNeighbors = getAllSingleFlipNeighbors(pid);
  if (flipNeighbors.length !== 8) throw new Error("Expected 8 single flip neighbors");
}

console.log("TypeScript 16x16 Grid coordinate bijection: PASS (all 256 pixels)");
