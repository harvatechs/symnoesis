import { describe, expect, it } from "vitest";
import { VERSION } from "../src/index.js";

describe("core package sanity", () => {
  it("exports correct version", () => {
    expect(VERSION).toBe("0.1.0-dev.0");
  });
});
