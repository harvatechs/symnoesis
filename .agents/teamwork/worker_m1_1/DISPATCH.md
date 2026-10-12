## 2026-10-12T04:45:50Z
Read E:/Symnoesis/.agents/teamwork/ORIGINAL_REQUEST.md and E:/Symnoesis/CLAUDE.md.
Your working directory is E:/Symnoesis/.agents/teamwork/worker_m1_1.
You are the Implementation Worker for Milestone 1: Math Reference Core & Parity (M1-M2 Core).

Read:
- E:/Symnoesis/PROJECT.md
- E:/Symnoesis/CLAUDE.md
- E:/Symnoesis/.agents/teamwork/spec_miner_survey_1/analysis.md
- E:/Symnoesis/.agents/teamwork/explorer_survey_pyts_1/analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File write ownership:
You own exclusively:
- packages/py/src/symnoesis/ (core modules)
- packages/py/tests/
- spec/schemas/*.schema.json
- packages/ts/src/
- packages/ts/tests/

Tasks:
1. Python Core Bug Fixes & Improvements:
   - packages/py/src/symnoesis/gray.py: Fix gray_to_int inverse loop (accumulate into n with n ^= n >> shift or 4-bit iterative folding).
   - packages/py/src/symnoesis/grid.py: Verify pixel_id_to_coord and pixel_coord_to_id with the fixed gray code.
   - packages/py/src/symnoesis/zones.py: Fix line 59 so Z1 condition evaluates correctly into matches and secondary_tags when has_confirmed_chi is true (Z7 is primary, Z1 in secondary_tags per SPEC §9).
   - packages/py/src/symnoesis/__init__.py: Add __version__ = "0.1.0.dev0".
   - packages/py/src/symnoesis/net_effects.py & sq.py: Fix type narrowing for operator and gate_ceiling so mypy --strict passes with 0 errors.
   - Run ruff check --fix and ruff format on packages/py/.
   - Add property tests in packages/py/tests/property/ (Hypothesis tests for Gray code bijection, normal CDF, mass conservation, SQ clipping bounds) and unit tests ensuring >= 95% coverage on math modules.
2. Fix 16 JSON Schemas in spec/schemas/:
   - Replace empty key "" with "$schema": "https://json-schema.org/draft/2020-12/schema" across all 16 schema files.
3. TypeScript Core Port (packages/ts/src/):
   - Implement math.ts with Cody's rational Chebyshev erfc algorithm matching scipy.special.ndtr within 1e-9.
   - Implement gray.ts (intToGray, grayToInt, 4-bit Gray code bijection).
   - Implement grid.ts (bit interleaving to col, row and reverse).
   - Implement variables.ts (variable scaling and CDF).
   - Implement assign.ts (probabilistic pixel assignment with sigma_floor = 0.01 and 1e-4 pruning).
   - Implement net_effects.ts (HNE, SNE, non-compensation rule).
   - Implement stability.ts (stability factor, harm asymmetry).
   - Implement gates.ts (safety gate ceiling G in [0, 0.25]).
   - Implement sq.ts (composite SQ calculation, clipping to [-100, +100]).
   - Implement classes.ts (symbiosis classification).
   - Implement zones.ts (governance zones Z1-Z7 with primary and secondary tags).
   - Implement index.ts exporting all public functions and types.
   - Add Vitest unit tests and golden vector tests in packages/ts/tests/ verifying parity against GV-SQ-001..003 within 1e-6.
4. Verification Commands:
   - uv run --directory packages/py pytest --cov=symnoesis (must achieve >= 95% coverage on core math).
   - uv run --directory packages/py mypy src tests (must pass with 0 errors).
   - uv run --directory packages/py ruff check . (must pass with 0 errors).
   - pnpm -r run typecheck (must pass with 0 errors).
   - pnpm -r run test (all tests pass).
5. Document all modified files, test outputs, and coverage in E:/Symnoesis/.agents/teamwork/worker_m1_1/handoff.md. Send completion message back to caller.
