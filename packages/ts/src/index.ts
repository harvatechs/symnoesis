/**
 * Symnoesis (SYMN-01) TypeScript Reference Core.
 *
 * Browser-compatible, pure mathematical and algorithmic implementation of
 * normative specification SPEC.md §2–§14.
 */

export const VERSION = "0.1.0-dev.0";

// Configuration
export * from "./config.js";

// Math & Numerical Core
export * from "./math.js";

// Gray Code & Geometry
export * from "./gray.js";
export * from "./grid.js";

// Variables & Assignment
export * from "./variables.js";
export * from "./assign.js";

// Net Effects Calculus
export * from "./net_effects.js";

// Stability & Asymmetry
export * from "./stability.js";

// Safety Gates
export * from "./gates.js";

// Symnoesis Quotient
export * from "./sq.js";

// Symbiosis Classification
export * from "./classes.js";

// Governance Zones
export * from "./zones.js";

// Minimal Failure Cover (MFC) & Boolean Minimization
export * from "./cover.js";

// Counterfactual Repair Diagnostics
export * from "./counterfactual.js";

// Longitudinal Temporal Engine
export * from "./temporal.js";

// Privacy & Telemetry Protection
export * from "./privacy.js";
