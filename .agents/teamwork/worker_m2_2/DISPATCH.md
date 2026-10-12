## 2026-10-12T05:50:39Z
Read E:/Symnoesis/.agents/teamwork/ORIGINAL_REQUEST.md and E:/Symnoesis/CLAUDE.md.
Your working directory is E:/Symnoesis/.agents/teamwork/worker_m2_2.
You are the Replacement Implementation Worker for Milestone M2: Minimal Failure Cover & Longitudinal Diagnostics (R2).

Read:
- E:/Symnoesis/PROJECT.md
- E:/Symnoesis/CLAUDE.md
- E:/Symnoesis/.agents/teamwork/spec_miner_survey_1/analysis.md (§5 on Minimal Failure Cover & §6 on Temporal Engine)
- spec/SPEC.md (§9 Governance Zones & Temporal, §10 Minimal Failure Cover)
- spec/config/symn-01.v0.1.yaml (keys: cover, temporal)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File write ownership:
You own exclusively:
- packages/py/src/symnoesis/cover.py, counterfactual.py, temporal.py, __init__.py
- packages/py/tests/unit/test_cover.py, test_counterfactual.py, test_temporal.py
- packages/ts/src/cover.ts, counterfactual.ts, temporal.ts, index.ts
- packages/ts/tests/cover.test.ts, counterfactual.test.ts, temporal.test.ts

Tasks:
1. Python Implementation (packages/py/src/symnoesis/):
   - cover.py:
     - 256 vertices on 8-cube (8 binary variables).
     - Subcube generation/evaluation in {0, 1, *}^8.
     - Harm mass h(c) = n_eff(c) * max(0, -SQ(c))/100.
     - Rule purity pi(R) = sum_{c in R} h(c) / sum_{c in R} n_eff(c) >= config.cover.min_rule_purity (0.8).
     - Set-cover MILP optimization via scipy.optimize.milp with HiGHS solver minimizing subcube count subject to coverage >= config.cover.min_coverage (0.85).
     - Quine-McCluskey strict mode matching sympy.logic.boolalg.SOPform output for exact boolean minimization.
   - counterfactual.py:
     - Counterfactual repair diagnostics: given a non-mutualistic state, compute minimal L1/L2 variable adjustments to transition into Mutualism (SQ > 20, HNE > 0.2, SNE > 0.2).
   - temporal.py:
     - Longitudinal engine for multi-frame trajectories (days 1, 7, 28, 84, 182).
     - Minimum Detectable Change (MDC = 5.0) thresholding.
     - Negative trajectory requires two consecutive intervals with delta SQ < -MDC.
     - Status: improving, stable, deteriorating.
   - Export all in packages/py/src/symnoesis/__init__.py.
   - Unit tests in packages/py/tests/unit/: test_cover.py, test_counterfactual.py, test_temporal.py.
   - Ensure mypy --strict passes, ruff check/format pass, pytest passes with >= 95% coverage.

2. TypeScript Port (packages/ts/src/):
   - cover.ts: subcube evaluation, Quine-McCluskey minimizer, purity and coverage metrics.
   - counterfactual.ts: counterfactual repair projections matching Python.
   - temporal.ts: trajectory engine, MDC thresholds, negative trajectory detection.
   - Export all in packages/ts/src/index.ts.
   - Unit and parity tests in packages/ts/tests/: cover.test.ts, counterfactual.test.ts, temporal.test.ts.
   - Ensure tsc --noEmit, vitest, and build pass clean.

3. Verify:
   - uv run --directory packages/py pytest
   - uv run --directory packages/py mypy src tests
   - uv run --directory packages/py ruff check .
   - pnpm -r run typecheck
   - pnpm -r run test
   - uv run --directory packages/py python ../../tests/e2e/runner.py --all

4. Document all results, modified files, test outputs in E:/Symnoesis/.agents/teamwork/worker_m2_2/handoff.md. Send completion message when done.
