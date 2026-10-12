import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  coordToPixelId,
  getAllSingleFlipNeighbors,
  getGridNeighbors,
  grayToInt,
  intToGray,
  parsePixelId,
  pixelIdToCoord,
} from "../packages/ts/dist/index.js";

const inputPath = resolve(process.cwd(), "scripts/inv_inputs.json");
const outputPath = resolve(process.cwd(), "scripts/inv_outputs_ts.json");

const inputs = JSON.parse(readFileSync(inputPath, "utf-8"));
const results = {};

// 1. Gray code 0..65535
const grayResults = [];
for (const k of inputs.gray_test_values) {
  const g = intToGray(k);
  const kRec = grayToInt(g);
  grayResults.push({ k, g, kRec });
}
results.gray = grayResults;

// 2. Grid coordinates for all 256 pixels
const gridResults = [];
for (let col = 0; col < 16; col++) {
  for (let row = 0; row < 16; row++) {
    const pid = coordToPixelId({ col, row });
    const coordRec = pixelIdToCoord(pid);
    const neighbors = getGridNeighbors({ col, row });
    const singleFlips = getAllSingleFlipNeighbors(pid);
    gridResults.push({
      col,
      row,
      pid,
      coordRec,
      neighborsCount: neighbors.length,
      singleFlipsCount: singleFlips.length,
      neighbors,
      singleFlips,
    });
  }
}
results.grid = gridResults;

writeFileSync(outputPath, JSON.stringify(results));
console.log("TypeScript invariant tests completed successfully.");
