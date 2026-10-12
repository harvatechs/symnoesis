# Original User Request

## 2026-10-12T04:26:33Z

Build the complete Symnoesis (SYMN-01) repository to release v0.1.0: normative specification, Python reference implementation, TypeScript port, synthetic evidence pipeline, Symnoesis Card and Index tooling, static research website, Interactive Map Portal, governance documentation, and release engineering.

Working directory: E:/Symnoesis
Integrity mode: development

## Requirements

### R1. Specification & Mathematical Reference Core (Milestones M1–M2)
Implement the normative specification (spec/SPEC.md §2–§14), Appendix A (golden vectors GV-SQ-001..003), and Appendix B configuration schema across both Python (packages/py/src/symnoesis/) and TypeScript (@symnoesis/core in packages/ts/). Ensure exact parity: Gray code bijections, 16x16 grid coordinates, variable scaling (normal CDF via erfc within 1e-9 of scipy.special.ndtr), probabilistic pixel assignment, net effects calculus (HNE, SNE, non-compensation rule, operator-blind parasitism suppression), stability factor, safety gate ceiling, composite SQ, symbiosis classification, and governance zones.

### R2. Minimal Failure Cover & Longitudinal Diagnostics (Milestones M3–M4)
Implement exact Minimal Failure Cover (MFC) optimization via MILP (scipy.optimize.milp with HiGHS) and Quine-McCluskey strict mode (matching sympy.logic.boolalg.SOPform). Implement counterfactual repair diagnostics and the temporal engine for multi-frame trajectories (days 1, 7, 28, 84, 182) with Minimum Detectable Change (MDC) thresholds.

### R3. Synthetic Evidence Generator & Verification Battery (Milestone M5)
Implement the synthetic persona and dyad generation pipeline across the 4 domains (learning, coding, health-information, advice-companionship) producing E1 synthetic data adhering to data contracts, k-anonymity (k_min = 10), and differential privacy.

### R4. Symnoesis Card, Index Tooling & Static Web Portal (Milestones M6–M8)
Implement card generation, cryptographic run manifests (Ed25519 signing and hash integrity), and the Interactive Map Portal with 16x16 Gray-coded visualization, 4 visible neighbors + 8 single-flip neighbor inspection, adaptive resolution (16x16, 8x8, 4x4), and WCAG 2.1 AA accessibility.

### R5. Governance Documentation & Release Engineering (Milestones M9–M10)
Finalize governance documents, verify all citations per research protocol, maintain release artifacts, and ensure automated end-to-end gate verification (`make verify`).

## Acceptance Criteria

### Code Quality & Parity
- [ ] `make verify` passes clean with zero errors across all targets (setup, lint, typecheck, test, build).
- [ ] Strict type checking passes in Python (`mypy --strict`) and TypeScript (`tsc --noEmit`).
- [ ] Python reference implementation and TypeScript port match within 1e-6 on all golden vectors (GV-SQ-001..003).
- [ ] Zero hardcoded numeric constants in application code outside of config loading.
- [ ] Test coverage >= 95% on core calculation modules.

### Verification Resources
- Existing repository test suite in `packages/py/tests/` and `packages/ts/tests/`.
- Normative specification `spec/SPEC.md` and configuration `spec/config/symn-01.v0.1.yaml`.
- Golden vectors in `spec/vectors/` and JSON schemas in `spec/schemas/`.
