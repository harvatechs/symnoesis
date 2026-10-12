## 2026-10-12T06:40:44Z
Read E:/Symnoesis/.agents/teamwork/ORIGINAL_REQUEST.md and E:/Symnoesis/CLAUDE.md.
Your working directory is E:/Symnoesis/.agents/teamwork/worker_m3_1.
You are the Implementation Worker for Milestone M3: Synthetic Evidence Generator & Verification Battery (R3 / M5).

Read:
- E:/Symnoesis/PROJECT.md
- E:/Symnoesis/CLAUDE.md
- E:/Symnoesis/.agents/teamwork/spec_miner_survey_1/analysis.md (§7 Synthetic Evidence Pipeline & Privacy)
- spec/SPEC.md §12 (Instruments and Protocols) & §13 (Evidence Tiers & Privacy)
- spec/schemas/ (dyad.schema.json, session.schema.json, telemetry_window.schema.json, persona.schema.json, run_manifest.schema.json)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File write ownership:
- spec/domains/*.yaml (learning.yaml, coding.yaml, health-information.yaml, advice-companionship.yaml)
- spec/instruments/*.yaml
- spec/modules/*.md
- packages/py/src/symnoesis/ (simulator/, judges/, telemetry/, privacy.py, __init__.py)
- packages/py/tests/unit/ (test_simulator.py, test_judges.py, test_privacy.py)
- packages/ts/src/ (privacy.ts, index.ts if relevant)
- data/fixtures/

Tasks:
1. Domain and Protocol Specifications:
   - Author spec/domains/ (learning.yaml, coding.yaml, health-information.yaml, advice-companionship.yaml) defining domain parameters, task matrices, instruments, and evaluation rubrics per SPEC §12.
   - Author spec/instruments/ and spec/modules/ per blueprint.
2. Synthetic Persona & Dyad Generation Pipeline (packages/py/src/symnoesis/):
   - Implement persona and dyad simulation with deterministic explicit seeds.
   - Output structured sessions adhering strictly to JSON schemas in spec/schemas/.
   - Produce reproducible E1 synthetic data fixtures in data/fixtures/ across all 4 domains.
3. Multi-Judge Calibration Harness:
   - Implement judge panel evaluation.
   - Implement exact calculation of Krippendorff's alpha (nominal, ordinal, interval).
   - Ensure calibrated judge panels achieve Krippendorff's alpha >= 0.80.
4. Privacy and Telemetry Engine:
   - Implement privacy filters in privacy.py:
     - No raw text storage (pseudonymous hashes only).
     - k-anonymity validation: cell suppression when cell size < k_min = 10.
     - Differential privacy: Laplace mechanism with epsilon = 1.0 (scale b = sensitivity / epsilon).
5. Testing & Verification:
   - Add unit tests in packages/py/tests/unit/ (test_simulator.py, test_judges.py, test_privacy.py).
   - Verify: uv run --directory packages/py pytest --cov=src (coverage >= 95% on calculation modules).
   - Verify: uv run --directory packages/py mypy src tests (0 errors under strict).
   - Verify: uv run --directory packages/py ruff check .
   - Verify: pnpm -r run typecheck and pnpm -r run test.
   - Verify: uv run --directory packages/py python ../../tests/e2e/runner.py --all (all 299 pass).
6. Deliver full report and test proofs in E:/Symnoesis/.agents/teamwork/worker_m3_1/handoff.md. Send completion message when done.
