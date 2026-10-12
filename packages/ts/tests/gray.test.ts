import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  bitsToInt,
  grayToInt,
  hammingDistance,
  intToBits,
  intToGray,
  isAdjacentOnTorus,
} from "../src/index.js";

describe("Gray code operations and bijections", () => {
  it("matches gray-code-16.json golden vector", () => {
    const vectorPath = resolve(
      __dirname,
      "../../../spec/vectors/gray-code-16.json",
    );
    const data = JSON.parse(readFileSync(vectorPath, "utf-8")) as {
      elements: Array<{
        index: number;
        code_int: number;
        bits: number[];
      }>;
    };

    expect(data.elements.length).toBe(16);

    for (const item of data.elements) {
      expect(intToGray(item.index)).toBe(item.code_int);
      expect(grayToInt(item.code_int)).toBe(item.index);
      expect(intToBits(item.code_int, 4)).toEqual(item.bits);
      expect(bitsToInt(item.bits)).toBe(item.code_int);
    }
  });

  it("satisfies single-bit flip adjacency on periodic torus", () => {
    for (let i = 0; i < 16; i++) {
      const curr = intToGray(i);
      const next = intToGray((i + 1) % 16);
      expect(hammingDistance(curr, next)).toBe(1);
      expect(isAdjacentOnTorus(i, (i + 1) % 16, 16)).toBe(true);
    }
  });

  it("rejects invalid inputs", () => {
    expect(() => intToGray(-1)).toThrow();
    expect(() => grayToInt(-1)).toThrow();
    expect(() => intToBits(16, 4)).toThrow();
    expect(() => bitsToInt([0, 2])).toThrow();
  });
});
