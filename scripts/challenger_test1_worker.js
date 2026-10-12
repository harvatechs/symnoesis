import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { erfc, normalCdf } from "../packages/ts/dist/index.js";

const inputPath = resolve(process.cwd(), "scripts/cody_inputs.bin");
const outputPath = resolve(process.cwd(), "scripts/cody_outputs.bin");

const inBuf = readFileSync(inputPath);
const count = inBuf.length / 8;
const inView = new Float64Array(inBuf.buffer, inBuf.byteOffset, count);

// Output stores 2 float64 values per input: normalCdf and erfc
const outView = new Float64Array(count * 2);

for (let i = 0; i < count; i++) {
  const z = inView[i];
  outView[i * 2] = normalCdf(z);
  outView[i * 2 + 1] = erfc(z);
}

const outBuf = Buffer.from(outView.buffer, outView.byteOffset, outView.byteLength);
writeFileSync(outputPath, outBuf);
console.log(`Successfully evaluated ${count} points through TypeScript Cody erfc and normalCdf.`);
