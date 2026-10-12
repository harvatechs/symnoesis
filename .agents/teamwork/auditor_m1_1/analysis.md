# Forensic Integrity Audit Report: Milestone 1 (Math Reference Core & Parity)

**Work Product**: Milestone 1 Deliverables (`packages/py/src/symnoesis/`, `packages/ts/src/`, `spec/schemas/`, tests)  
**Profile**: General Project  
**Integrity Mode**: Development (Ground Truth: `ORIGINAL_REQUEST.md`)  
**Auditor**: Forensic Integrity Auditor (`auditor_m1_1`)  
**Timestamp**: 2026-10-12T05:47:00Z  
**Verdict**: **CLEAN**

---

## 1. Executive Summary

Milestone 1 implements the mathematical reference core and cross-language parity for the Symnoesis (SYMN-01) specification. An unsparing forensic audit was conducted across both Python (`packages/py`) and TypeScript (`packages/ts`) codebases to detect cheating, hardcoded outputs, facade implementations, test circumvention, and configuration leakage.

Every forensic check passed unequivocally:
1. **Zero Cheating & Hardcoding**: No golden vector identifiers or static expected outputs exist in application code. All calculations are genuine algebraic transformations.
2. **Authentic Cody erfc Implementation**: Cody's (1969) rational Chebyshev polynomials are implemented with high-precision minimax coefficients across three intervals, yielding a maximum deviation of $2.220 \times 10^{-16}$ against `scipy.special.ndtr` (surpassing the $< 10^{-9}$ spec requirement).
3. **Algebraic Normative Conformance**: SPEC §3–§9 equations (Gray bijections, probabilistic mass assignment with $\sigma_{\text{floor}} = 0.01$ and $10^{-4}$ pruning, HNE/SNE calculus, non-compensation, stability harm asymmetry, safety gate ceilings, and zone precedence) are authentically executed.
4. **Zero Test Circumvention**: Zero skipped (`@pytest.mark.skip`), expected fail (`xfail`), mocked, or relaxed assertions exist in the test suites.
5. **Configuration Integrity**: Zero domain constants exist outside configuration structures.
6. **Schema Header Integrity**: All 16 JSON Schema Draft 2020-12 files in `spec/schemas/` have valid `"$schema"` declarations and no empty keys.
7. **Parity Conformance**: Python and TypeScript match within $10^{-6}$ on all golden reference vectors (GV-SQ-001, GV-SQ-002, GV-SQ-003).

---

## 2. Phase-by-Phase Forensic Check Results

### Phase 1: Cheating & Hardcoding Detection

- **Check 1.1: Golden Vector Identifiers in Source**:
  - Target: `GV-SQ-001`, `GV-SQ-002`, `GV-SQ-003`, `GV-SQ`, `vector`, `golden`
  - Command: `rg -i "GV-SQ" packages/py/src packages/ts/src`
  - Result: **PASS** — 0 matches found in application source code.
- **Check 1.2: Hardcoded Numerical Outputs in Source**:
  - Target: `28.71`, `-28.0`, `0.319`, `0.48`, `0.25`, `60.0`
  - Search: Checked all numeric literals across `packages/py/src` and `packages/ts/src`.
  - Findings: `28.71`, `-28.0`, `0.319`, `0.48` do not appear anywhere in source files. `0.25` appears only in docstrings and as normative configuration weights/ceilings in `packages/ts/src/config.ts` (CHI-4..7 ceiling = 0.25; state_weights = [0.25, 0.25, 0.25, 0.25]).
  - Result: **PASS** — No hardcoded calculation results.
- **Check 1.3: Input Branching on Test Cases**:
  - Inspected all conditionals in `packages/py/src` and `packages/ts/src`.
  - Result: **PASS** — Branching occurs only on mathematical domain conditions ($HNE < 0$, $C \ge 0$, gate ceiling presence, threshold comparisons, array length validation).

---

### Phase 2: Dummy / Facade Implementation Detection

- **Check 2.1: Cody Rational Chebyshev erfc**:
  - Location: `packages/ts/src/math.ts`
  - Inspection: Genuine Cody (1969) minimax rational approximation with three domains:
    - $|x| \le 0.46875$: Rational polynomial $R(y^2) = y \cdot A(y^2) / B(y^2)$ with coefficients $A[0..4]$, $B[0..3]$
    - $0.46875 < |x| \le 4.0$: Rational polynomial $e^{-y^2} \cdot C(y) / D(y)$ with coefficients $C[0..8]$, $D[0..7]$ and split exponentiation $y_{\text{sq}} = \lfloor 16y \rfloor / 16$ to eliminate precision cancellation
    - $4.0 < |x| < 26.543$: Asymptotic rational approximation $(1/(\sqrt{\pi}y)) - (1/y) \cdot P(1/y^2) / Q(1/y^2)$ with coefficients $P[0..5]$, $Q[0..4]$
    - $|x| \ge 26.543$: Underflow to $0.0$
    - $x < 0$: Symmetry transformation $\text{erfc}(x) = 2 - \text{erfc}(|x|)$
  - Empirical verification against `scipy.special.ndtr`:
    - Evaluated across 200,001 points in $[-10, 10]$
    - Maximum absolute error: $2.220 \times 10^{-16}$
  - Result: **PASS** — Highly authentic, genuine double-precision implementation.
- **Check 2.2: Net Effects Calculus (HNE, SNE, Non-Compensation)**:
  - Locations: `packages/py/src/symnoesis/net_effects.py`, `packages/ts/src/net_effects.ts`
  - Inspection: Formulas match SPEC §5:
    - $HNE_{\text{state}} = \sum a_i (2s_i - 1)$
    - $HNE_{\text{outcome}} = \text{mean}(\tanh(d_k / d_0))$
    - $HNE = (1 - \lambda) HNE_{\text{state}} + \lambda HNE_{\text{outcome}}$
    - $SNE = 0.4 \cdot \text{Integrity} + 0.4 \cdot \text{Reliability} + 0.2 \cdot \text{Operator}$
    - Non-compensation: if $HNE < 0$, $SNE' = \min(SNE, 0)$ else $SNE$
    - $C = (0.7 \cdot HNE + 0.3 \cdot SNE') / (0.7 + 0.3)$
  - Result: **PASS** — Fully authentic algebraic implementation.
- **Check 2.3: Stability Factor & Harm Asymmetry**:
  - Locations: `packages/py/src/symnoesis/stability.py`, `packages/ts/src/stability.ts`
  - Inspection: $S = 0.5 + 0.5 \cdot (1 - \min(1, \sigma_C / \sigma_{\text{max}}))$. Harm asymmetry: $S_{\text{eff}} = S$ if $C \ge 0$ else $1.0$.
  - Result: **PASS** — Fully authentic.
- **Check 2.4: Safety Gate & Ceilings**:
  - Locations: `packages/py/src/symnoesis/gates.py`, `packages/ts/src/gates.ts`
  - Inspection: Gate ceiling $G = \min(G_i)$ for confirmed CHIs; $SQ = \min(SQ_{\text{raw}}, 100 \cdot G)$.
  - Result: **PASS** — Fully authentic.
- **Check 2.5: Governance Zones & Precedence**:
  - Locations: `packages/py/src/symnoesis/zones.py`, `packages/ts/src/zones.ts`
  - Inspection: Evaluates all matching zones; primary selected by strict precedence $[Z7, Z6, Z5, Z4, Z1, Z2, Z3]$; all other matching zones returned as `secondary_tags`.
  - Result: **PASS** — Fully authentic.

---

### Phase 3: Test Circumvention Detection

- **Check 3.1: Test Skipping or Expecting Failure**:
  - Grep for `skip`, `xfail`, `.skip()`, `.todo()` across `packages/py/tests/` and `packages/ts/tests/`.
  - Result: **PASS** — Zero skipped or xfailed tests.
- **Check 3.2: Mocking & Stubbing in Tests**:
  - Grep for `mock`, `patch`, `jest.fn`, `vi.fn` in test directories.
  - Result: **PASS** — Zero mocks; tests exercise real calculation engines.
- **Check 3.3: Assertion Tolerances**:
  - Checked tolerances in golden vector and parity tests:
    - Python: `pytest.approx(..., abs=1e-6)`
    - TypeScript: `expect(...).toBeCloseTo(..., 6)` (tolerance $\le 5 \times 10^{-7}$)
  - Result: **PASS** — Strict $10^{-6}$ tolerance maintained across all calculations.

---

### Phase 4: Hardcoded Constants Detection

- **Check 4.1: Domain Constants in Application Logic**:
  - Searched for hardcoded numbers outside config loading.
  - Python: All weights, scales, thresholds, ceilings, and zone boundaries are read directly from `SymnoesisConfig` (`spec/config/symn-01.v0.1.yaml`).
  - TypeScript: `DEFAULT_CONFIG` is defined in `packages/ts/src/config.ts` for browser portability and matches `spec/config/symn-01.v0.1.yaml` verbatim across every single key and value.
  - Result: **PASS** — Clean separation of configuration and logic.

---

### Phase 5: Schema Header Repair Verification

- **Check 5.1: JSON Schema Draft 2020-12 Declarations**:
  - Validated all 16 schema files in `spec/schemas/`:
    `assessment.schema.json`, `config.schema.json`, `consent.schema.json`, `cover_rule.schema.json`, `dyad.schema.json`, `dyad_window_record.schema.json`, `map_frame.schema.json`, `memory_event.schema.json`, `pixel_record.schema.json`, `run_manifest.schema.json`, `session.schema.json`, `symnoesis_card.schema.json`, `tool_call.schema.json`, `turn.schema.json`, `variable_score.schema.json`, `window.schema.json`.
  - Verified: Every file has `"$schema": "https://json-schema.org/draft/2020-12/schema"` and zero empty keys `""`.
  - Result: **PASS** — All 16 schemas verified.

---

### Phase 6: Independent Behavioral Execution

- **Command 1**: `uv run --directory packages/py pytest --cov=symnoesis -v`
  - Output: 37 passed in 5.08s. Total coverage: 99% (assign: 100%, classes: 100%, evidence: 100%, gates: 100%, gray: 100%, grid: 100%, net_effects: 95%, sq: 100%, stability: 100%, variables: 100%, zones: 100%, __init__: 100%, config: 97%).
- **Command 2**: `uv run --directory packages/py mypy src tests`
  - Output: Success: no issues found in 24 source files.
- **Command 3**: `uv run --directory packages/py ruff check . && uv run --directory packages/py ruff format --check .`
  - Output: All checks passed! 25 files already formatted.
- **Command 4**: `pnpm -r run typecheck`
  - Output: `tsc --noEmit` exited 0 with 0 errors.
- **Command 5**: `pnpm -r run test`
  - Output: 6 test files passed, 16 tests passed.
- **Command 6**: `pnpm -r run build`
  - Output: `tsc` produced complete distribution in `packages/ts/dist` (52 artifacts).
- **Command 7**: Independent Python Parity Verification (`verify_parity.py`)
  - Output:
    - GV-SQ-001: HNE diff 0.0, SNE diff 0.0, C diff 5.55e-17, SQ diff 3.55e-15, mutualism, Z2 [PASS]
    - GV-SQ-002: HNE diff 0.0, SNE diff 0.0, SNE' diff 0.0, C diff 5.55e-17, SQ diff 3.55e-15, parasitism, Z6 [PASS]
    - GV-SQ-003: C diff 0.0, SQ_raw diff 0.0, SQ diff 0.0, Z7 [PASS]
    - Dense normal_cdf max diff across 200,001 points: $2.220 \times 10^{-16}$ [PASS]
    - 16 Gray code bijections [PASS]
- **Command 8**: Independent TypeScript Parity & Stress Testing (`verify_parity_ts.cjs`)
  - Output:
    - All 3 golden vectors match within $10^{-6}$ [PASS]
    - Cody erfc & normalCdf edge cases and symmetry [PASS]
    - Non-compensation rule across all 4 quadrants [PASS]
    - Harm asymmetry stability override ($C < 0 \implies S_{\text{eff}} = 1.0$) [PASS]
    - Safety gate ceilings and status evaluation [PASS]
    - Symbiosis matrix (9 classes) and operator-blind parasitism suppression [PASS]
    - Zone precedence under simultaneous triggers ($Z7 > Z6 > Z5 > Z4 > Z1 > Z2 > Z3$) [PASS]
    - Gray code bijections and Torus toroidal neighbor wrapping [PASS]

---

## 3. Forensic Verdict

```
## Forensic Audit Report

Work Product: Milestone 1 Deliverables (Math Reference Core & Parity)
Profile: General Project
Verdict: CLEAN

### Phase Results
- Hardcoded test results: PASS (zero detected)
- Facade implementations: PASS (zero detected; genuine Cody erfc & normative equations)
- Fabricated verification outputs: PASS (all tests independently executed and verified)
- Self-certifying tests: PASS (tests validate against normative vectors and specs)
- Test circumvention: PASS (zero skips, zero mocks, strict 1e-6 tolerances)
- Hardcoded constants: PASS (clean configuration abstraction)
- Schema repair: PASS (all 16 schemas conform to Draft 2020-12)
- Type safety & style: PASS (mypy strict 0 errors, tsc 0 errors, ruff clean)
- Test coverage: PASS (99% on core calculation modules, target >= 95%)
```
