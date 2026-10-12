# Progress — worker_m1_1

Last visited: 2026-10-12T05:07:00Z
Status: Completed

## Completed
- Python Core Bug Fixes:
  - Fixed `gray_to_int` in `gray.py` to fold `n` iteratively with `n ^= n >> shift`.
  - Added and verified `pixel_coord_to_id` in `grid.py`.
  - Fixed Z1 match logic in `zones.py` to allow Z7 primary with Z1 secondary tag.
  - Added `__version__ = "0.1.0.dev0"` and exports in `__init__.py`.
  - Fixed type narrowing for `operator` in `net_effects.py` and `gate_ceiling` in `sq.py`.
  - Added unit and property tests in `packages/py/tests/`, achieving 99% line coverage on core math.
  - Formatted and linted Python code with `ruff check` and `ruff format` (0 warnings).
  - Passed `mypy --strict src tests` with 0 errors across 24 files.
- JSON Schema Repairs:
  - Replaced empty key `""` with `"$schema": "https://json-schema.org/draft/2020-12/schema"` across all 16 JSON schema files in `spec/schemas/`.
- TypeScript Core Port (`packages/ts/src/`):
  - Implemented `math.ts` using Cody's rational Chebyshev erfc algorithm matching `scipy.special.ndtr` within machine epsilon (2.22e-16 vs target 1e-9).
  - Implemented `config.ts`, `gray.ts`, `grid.ts`, `variables.ts`, `assign.ts`, `net_effects.ts`, `stability.ts`, `gates.ts`, `sq.ts`, `classes.ts`, `zones.ts`, and `index.ts`.
  - Added Vitest test suites (`math.test.ts`, `gray.test.ts`, `grid.test.ts`, `assign.test.ts`, `golden_vectors.test.ts`).
  - Verified exact parity against GV-SQ-001, GV-SQ-002, GV-SQ-003 within 1e-6.
  - Verified `pnpm -r run typecheck` passes with 0 errors.
  - Verified `pnpm -r run test` passes with 16/16 tests across 6 files.
  - Verified `pnpm -r run build` compiles `dist/` cleanly.
- Documentation:
  - Updated BRIEFING.md.
  - Wrote comprehensive handoff report in `handoff.md`.
