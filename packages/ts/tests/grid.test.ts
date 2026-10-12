import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  coordToPixelId,
  getAllSingleFlipNeighbors,
  getGridNeighbors,
  parsePixelId,
  pixelCoordToId,
  pixelIdToCoord,
} from "../src/index.js";

describe("16x16 Grid and Pixel Coordinates", () => {
  it("matches grid-256-pixels.json golden vector", () => {
    const vectorPath = resolve(
      __dirname,
      "../../../spec/vectors/grid-256-pixels.json",
    );
    const data = JSON.parse(readFileSync(vectorPath, "utf-8")) as {
      pixels: Array<{
        pixel_id: string;
        col: number;
        row: number;
        h_bits: number[];
        m_bits: number[];
      }>;
    };

    expect(data.pixels.length).toBe(256);
    const seenIds = new Set<string>();

    for (const p of data.pixels) {
      expect(seenIds.has(p.pixel_id)).toBe(false);
      seenIds.add(p.pixel_id);

      const coord = { col: p.col, row: p.row };
      expect(coordToPixelId(coord)).toBe(p.pixel_id);
      expect(pixelCoordToId(p.col, p.row)).toBe(p.pixel_id);
      expect(pixelIdToCoord(p.pixel_id)).toEqual(coord);

      const [parsedH, parsedM] = parsePixelId(p.pixel_id);
      expect(parsedH).toEqual(p.h_bits);
      expect(parsedM).toEqual(p.m_bits);
    }
  });

  it("computes 4 grid-visible toroidal neighbors", () => {
    const neighbors = getGridNeighbors({ col: 0, row: 0 });
    expect(neighbors.length).toBe(4);
    expect(neighbors).toContainEqual({ col: 15, row: 0 });
    expect(neighbors).toContainEqual({ col: 1, row: 0 });
    expect(neighbors).toContainEqual({ col: 0, row: 15 });
    expect(neighbors).toContainEqual({ col: 0, row: 1 });
  });

  it("computes all 8 single-flip neighbors (4 human, 4 machine)", () => {
    const flips = getAllSingleFlipNeighbors("h0000-m0000");
    expect(flips.length).toBe(8);
    // 4 Human flips
    expect(flips).toContain("h1000-m0000");
    expect(flips).toContain("h0100-m0000");
    expect(flips).toContain("h0010-m0000");
    expect(flips).toContain("h0001-m0000");
    // 4 Machine flips
    expect(flips).toContain("h0000-m1000");
    expect(flips).toContain("h0000-m0100");
    expect(flips).toContain("h0000-m0010");
    expect(flips).toContain("h0000-m0001");
  });
});
