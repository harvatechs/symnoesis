# Symnoesis (SYMN-01) Test Infrastructure & 4-Tier E2E Specification

**Document Version:** 1.0.0  
**Specification Reference:** `spec/SPEC.md` v0.1.0 (Draft)  
**Target Repository:** `E:/Symnoesis`  
**Owner:** E2E Test Suite Designer & Writer (`test_writer_e2e_1`)  
**Status:** Canonical E2E Test Architecture  

---

## 1. Executive Summary & Test Architecture

### 1.1 Dual-Track Testing Philosophy
Symnoesis implements a **Dual-Track Engineering Architecture**:
- **Track 1 (Implementation Track):** Progressive milestone execution (M1 Math Reference Core & Parity $\to$ M2 MFC & Longitudinal Diagnostics $\to$ M3 Synthetic Evidence $\to$ M4 Card, Index, CLI & Web Portal $\to$ M5 Governance & Release Engineering).
- **Track 2 (Independent E2E Testing Track):** Autonomous, opaque-box test suite development (`tests/e2e/`) governed by this infrastructure specification. The test suite operates independently from the internal private structures of implementation modules, verifying software strictly against the normative specification (`spec/SPEC.md`), configuration contracts (`spec/config/symn-01.v0.1.yaml`), schema definitions (`spec/schemas/*.json`), and golden reference vectors (`spec/vectors/*.json`).

### 1.2 Opaque-Box Verification & Independent Oracles
To maintain testing integrity:
1. **Zero Private Method Dependencies:** Tests interact exclusively with public API interfaces, standard data schemas, CLI commands, and serialized artifacts. Tests never inspect or patch private functions (`_private_func`).
2. **Authoritative Output Derivation:** Expected outputs are derived strictly from:
   - Normative closed-form formulas in `spec/SPEC.md §3–§14`.
   - Normative golden vectors `GV-SQ-001..003` in `spec/vectors/`.
   - Independent normative mathematical oracle (`tests/e2e/oracle.py`).
   - JSON Schema validation drafts (Draft 2020-12 / Draft 7).
3. **Progressive Testability:** The suite is structured so that features from the active milestone (M1) and completed dependencies execute directly, while end-to-end data contracts and specifications across all 42 features are systematically verified.

---

## 2. The 4-Tier Test Classification Methodology

The Symnoesis E2E test suite adheres to a strict 4-Tier hierarchy:

| Tier | Category | Minimum Requirement | Purpose & Focus |
|---|---|---|---|
| **Tier 1** | Feature Coverage (Happy Path) | $\ge 5$ test cases per feature (All 42 features) | Verifies standard functionality, nominal inputs, contract compliance, and positive assertions. |
| **Tier 2** | Boundary & Corner Cases | $\ge 5$ test cases per feature (All 42 features) | Stress tests extremal values, degenerate distributions, numerical stability, thresholds, and malformed inputs. |
| **Tier 3** | Cross-Feature Combinations | Multi-way pairwise interactions | Validates systemic interactions across geometry, scoring, gating, stability, zoning, temporal dynamics, and privacy. |
| **Tier 4** | Real-World Application Scenarios | Comprehensive end-to-end workflows | Exercises complete lifecycle pipelines from simulated telemetry to certified public cards and index rankings. |

---

## 3. Feature Inventory & Test Mapping Matrix (42 Features)

| Feature # | Feature Name | Milestone | Spec Source | Tier 1 Tests | Tier 2 Tests | Tier 3 Matrix | Tier 4 Scenarios | Suite Location | Status |
|---|---|---|---|---|---|---|---|---|---|
| **F01** | Gray Code Bijection | M1 | SPEC §4 | TC1.01.1–5 | TC2.01.1–5 | Geometry $\times$ Neighbors | Lifecycle, Portal | `tier1/test_f01_gray_code.py` | ACTIVE |
| **F02** | 16x16 Grid Coordinates | M1 | SPEC §4 | TC1.02.1–5 | TC2.02.1–5 | Geometry $\times$ Zoning | Lifecycle, Portal | `tier1/test_f02_grid_coordinates.py` | ACTIVE |
| **F03** | Normal CDF Parity | M1 | SPEC §3 | TC1.03.1–5 | TC2.03.1–5 | Numerics $\times$ Scoring | Full Lifecycle | `tier1/test_f03_normal_cdf.py` | ACTIVE |
| **F04** | Probabilistic Pixel Assignment | M1 | SPEC §3 | TC1.04.1–5 | TC2.04.1–5 | Assign $\times$ Pruning | Full Lifecycle | `tier1/test_f04_probabilistic_assignment.py` | ACTIVE |
| **F05** | Net Effects Calculus | M1 | SPEC §5 | TC1.05.1–5 | TC2.05.1–5 | HNE $\times$ SNE NonComp | Full Lifecycle, Harm | `tier1/test_f05_net_effects.py` | ACTIVE |
| **F06** | Stability & Harm Asymmetry | M1 | SPEC §6 | TC1.06.1–5 | TC2.06.1–5 | Stability $\times$ Harm | Full Lifecycle | `tier1/test_f06_stability_asymmetry.py` | ACTIVE |
| **F07** | Safety Gate Ceiling | M1 | SPEC §7 | TC1.07.1–5 | TC2.07.1–5 | Gates $\times$ Zones | Harm Containment | `tier1/test_f07_safety_gate_ceiling.py` | ACTIVE |
| **F08** | Composite SQ & Clipping | M1 | SPEC §6 | TC1.08.1–5 | TC2.08.1–5 | SQ $\times$ Clipping | Full Lifecycle | `tier1/test_f08_composite_sq.py` | ACTIVE |
| **F09** | Symbiosis Classification | M1 | SPEC §8 | TC1.09.1–5 | TC2.09.1–5 | Class $\times$ OperatorBlind | Extraction Workflow | `tier1/test_f09_symbiosis_classes.py` | ACTIVE |
| **F10** | Governance Zones | M1 | SPEC §9 | TC1.10.1–5 | TC2.10.1–5 | Zones $\times$ Precedence | All Scenarios | `tier1/test_f10_governance_zones.py` | ACTIVE |
| **F11** | Golden Vectors Parity | M1 | SPEC App A | TC1.11.1–5 | TC2.11.1–5 | Golden $\times$ Cross-Lang | Parity Suite | `tier1/test_f11_golden_vectors.py` | ACTIVE |
| **F12** | Schema Header Repair | M1 | Schemas | TC1.12.1–5 | TC2.12.1–5 | Schema $\times$ Contracts | All Artifacts | `tier1/test_f12_schema_validation.py` | ACTIVE |
| **F13** | Py Strict Typing & Linting | M1 | CLAUDE §3 | TC1.13.1–5 | TC2.13.1–5 | Code Quality $\times$ CI | Makefile Gate | `tier1/test_f13_f14_typing_and_ts_core.py` | ACTIVE |
| **F14** | TypeScript Reference Core | M1 | ORIGINAL_REQUEST | TC1.14.1–5 | TC2.14.1–5 | Py $\leftrightarrow$ TS Parity | Portal Engine | `tier1/test_f13_f14_typing_and_ts_core.py` | ACTIVE |
| **F15** | Minimal Failure Cover (MILP) | M2 | SPEC §11 | TC1.15.1–5 | TC2.15.1–5 | MILP $\times$ Harm Mass | Diagnostic Engine | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F16** | Quine-McCluskey Strict Mode | M2 | SPEC §11 | TC1.16.1–5 | TC2.16.1–5 | QM $\leftrightarrow$ SymPy SOP | Boolean Cover | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F17** | Subcube Harm Mass & Purity | M2 | SPEC §11 | TC1.17.1–5 | TC2.17.1–5 | 6561 Subcubes $\times$ Filtering | Cover Engine | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F18** | Counterfactual Repair | M2 | SPEC §12 | TC1.18.1–5 | TC2.18.1–5 | Single-Flip $\times$ Ridge | Portal Suggest | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F19** | Longitudinal Temporal Engine | M2 | SPEC §10 | TC1.19.1–5 | TC2.19.1–5 | Multi-frame $\times$ Trajectory | Longitudinal Drift | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F20** | Minimum Detectable Change | M2 | SPEC §10 | TC1.20.1–5 | TC2.20.1–5 | MDC $\times$ Reliability | Drift Scenario | `tier1/test_f15_f20_mfc_temporal_specs.py` | SPEC_VERIFIED |
| **F21** | Domain & Instrument Specs | M3 | SPEC §15 | TC1.21.1–5 | TC2.21.1–5 | Domains $\times$ Instruments | Cohort Audit | `tier1/test_f21_f25_synthetic_privacy_specs.py` | SPEC_VERIFIED |
| **F22** | Persona & Dyad Simulator | M3 | SPEC §13 | TC1.22.1–5 | TC2.22.1–5 | Personas $\times$ Telemetry | Synthetic Sweeps | `tier1/test_f21_f25_synthetic_privacy_specs.py` | SPEC_VERIFIED |
| **F23** | Multi-Judge Calibration | M3 | SPEC §16 | TC1.23.1–5 | TC2.23.1–5 | Judges $\times$ Krippendorff | Certification | `tier1/test_f21_f25_synthetic_privacy_specs.py` | SPEC_VERIFIED |
| **F24** | Telemetry & Privacy Engine | M3 | SPEC §16 | TC1.24.1–5 | TC2.24.1–5 | k-Anonymity $\times$ DP | Synthetic Cohort | `tier1/test_f21_f25_synthetic_privacy_specs.py` | SPEC_VERIFIED |
| **F25** | Synthetic Evidence Fixtures | M3 | ORIGINAL_REQUEST | TC1.25.1–5 | TC2.25.1–5 | Fixtures $\times$ E1 Tier | Evidence Integrity | `tier1/test_f21_f25_synthetic_privacy_specs.py` | SPEC_VERIFIED |
| **F26** | Cryptographic Run Manifests | M4 | SPEC §14 | TC1.26.1–5 | TC2.26.1–5 | Ed25519 $\times$ Hash Chains | Run Verification | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F27** | Symnoesis Card Generator | M4 | SPEC §14 | TC1.27.1–5 | TC2.27.1–5 | Card $\times$ Schemas | Lifecycle Report | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F28** | Symnoesis Index Tooling | M4 | SPEC §14 | TC1.28.1–5 | TC2.28.1–5 | Bootstrap $\times$ Tiering | Benchmark Index | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F29** | Typer CLI | M4 | REPO_BLUEPRINT | TC1.29.1–5 | TC2.29.1–5 | CLI $\times$ Subcommands | User Workflow | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F30** | Astro Web Application | M4 | REPO_BLUEPRINT | TC1.30.1–5 | TC2.30.1–5 | Astro $\times$ SSR/SSG | Web Deployment | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F31** | Interactive Map Portal | M4 | SPEC §14 | TC1.31.1–5 | TC2.31.1–5 | Portal $\times$ Linear Projection| Browser Portal | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F32** | Neighbor Inspection | M4 | SPEC §14 | TC1.32.1–5 | TC2.32.1–5 | 4 Planar + 8 Hypercube | UX Explorer | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F33** | WCAG 2.1 AA Accessibility | M4 | CLAUDE §3 | TC1.33.1–5 | TC2.33.1–5 | a11y $\times$ axe-core | Portal Compliance | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F34** | Claims Registry | M4 | DESIGN_RULES | TC1.34.1–5 | TC2.34.1–5 | Claims $\times$ Tracing | Public Registry | `tier1/test_f26_f34_card_portal_specs.py` | SPEC_VERIFIED |
| **F35** | Whitepaper & Research Docs | M5 | RESEARCH_PROTOCOL | TC1.35.1–5 | TC2.35.1–5 | Preprint $\times$ LaTeX/MD | Scientific Archive | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F36** | Diátaxis Documentation | M5 | REPO_BLUEPRINT | TC1.36.1–5 | TC2.36.1–5 | 4 Diátaxis Quadrants | Docs Build | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F37** | Reference Bibliography | M5 | CLAUDE §1 | TC1.37.1–5 | TC2.37.1–5 | BibTeX $\times$ DOIs | Citation Check | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F38** | Governance Framework Finalization| M5 | GOVERNANCE_ORG | TC1.38.1–5 | TC2.38.1–5 | 10 Policy Docs $\times$ Audits | Legal/Ethics Gate | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F39** | Makefile Full Automation | M5 | CLAUDE §3 | TC1.39.1–5 | TC2.39.1–5 | Gate Targets $\times$ CI | Release Gate | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F40** | Package Build & Release Artifacts| M5 | CLAUDE §3 | TC1.40.1–5 | TC2.40.1–5 | Wheel $\times$ Tarball $\times$ npm | Release Eng | `tier1/test_f35_f42_governance_release_specs.py` | SPEC_VERIFIED |
| **F41** | E2E Test Suite Tiers 1-4 | M_E2E| Dual Track | TC1.41.1–5 | TC2.41.1–5 | Test Harness $\times$ Self-test | Quality Assurance | `tests/e2e/runner.py` | ACTIVE |
| **F42** | Adversarial Hardening (Tier 5) | M_FINAL| Dual Track | TC1.42.1–5 | TC2.42.1–5 | Adversarial Stress | Security Audit | `tests/e2e/tier2_boundaries/` | ACTIVE |

---

## 4. Tier 1: Feature Coverage Specifications ($\ge 5$ Tests per Feature)

### Feature 01: Gray Code Bijection (M1, SPEC §4)
- **TC1.01.01 (Forward Bijection Exactness):** For all $k \in \{0..15\}$, verify $g(k) = k \oplus (k \gg 1)$ produces exact 4-bit Gray integers `[0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]`.
- **TC1.01.02 (Inverse Bijection Invariance):** For all Gray integers $g \in \{0..15\}$, verify $\text{gray\_inv}(g)$ recovers the original $k$ such that $\text{gray\_inv}(g(k)) = k$.
- **TC1.01.03 (Bit Representation Parsing):** Verify conversion from integer to 4-bit array `int_to_bits(12, 4) == [1, 1, 0, 0]` and reverse `bits_to_int([1, 1, 0, 0]) == 12`.
- **TC1.01.04 (Single Bit Step Property):** Verify that for every consecutive pair $k, k+1 \pmod{16}$, Hamming distance $\text{dist}_H(g(k), g(k+1 \pmod{16})) == 1$.
- **TC1.01.05 (Complete 4-Bit Coverage):** Verify the image of $g(k)$ across $k \in [0, 15]$ is a permutation of the set $\{0, 1, \dots, 15\}$ with cardinality exactly 16.

### Feature 02: 16x16 Grid Coordinates & Pixel ID (M1, SPEC §4)
- **TC1.02.01 (Canonical Pixel ID Generation):** Verify `coord_to_pixel_id(PixelCoord(col=10, row=4))` outputs exact string `"h1111-m0110"` conforming to regex `^h[01]{4}-m[01]{4}$`.
- **TC1.02.02 (Pixel ID Parsing):** Verify parsing `"h1011-m0110"` returns `h_bits=[1,0,1,1]` and `m_bits=[0,1,1,0]`.
- **TC1.02.03 (Round-Trip Coordinate Invariance):** For all 256 coordinates $(c, r) \in [0..15]^2$, verify $\text{pixel\_id\_to\_coord}(\text{coord\_to\_pixel\_id}(c, r)) == (c, r)$.
- **TC1.02.04 (4 Planar Toroidal Neighbors):** Verify coordinate $(0, 0)$ generates planar neighbors $(15, 0), (1, 0), (0, 15), (0, 1)$, all differing by exactly 1 bit.
- **TC1.02.05 (8 Single-Flip Hypercube Neighbors):** Verify any pixel generates exactly 8 Hamming distance 1 neighbors (4 human flips, 4 machine flips), partitioned into 4 visual planar and 4 non-planar.

### Feature 03: Normal CDF Parity (M1, SPEC §3)
- **TC1.03.01 (Standard Normal Zero Center):** Verify $\Phi(0.0) == 0.5$ exactly.
- **TC1.03.02 (Standard Deviation Points):** Verify $\Phi(1.0) \approx 0.841344746$ and $\Phi(-1.0) \approx 0.158655254$ within $10^{-9}$ of `scipy.special.ndtr`.
- **TC1.03.03 (Monotonicity Across Grid):** Verify $\Phi(z_1) < \Phi(z_2)$ for any $z_1 < z_2$ across $z \in [-5.0, 5.0]$ with step $0.1$.
- **TC1.03.04 (Symmetry Invariant):** Verify $\Phi(z) + \Phi(-z) == 1.0$ within $10^{-12}$ across test domain.
- **TC1.03.05 (Non-Inferiority H2 Threshold):** Verify $\theta_{H2} = \Phi(-0.1 / 0.5) = \Phi(-0.2) \approx 0.42074029$ matches config value within $10^{-4}$.

### Feature 04: Probabilistic Pixel Assignment (M1, SPEC §3)
- **TC1.04.01 (Marginal Probability Calculation):** For posterior $\mu=0.6, \sigma=0.1$ and $\theta=0.5$, verify $p = \Phi((0.6 - 0.5)/0.1) = \Phi(1.0) \approx 0.8413447$.
- **TC1.04.02 (Unit Mass Sum Invariant):** Verify joint 256-cell mass distribution $\sum_{c=0}^{255} m(c) == 1.0$ within $10^{-11}$.
- **TC1.04.03 (Modal Pixel Determination):** For distinct high-confidence posteriors, verify modal pixel $\operatorname{argmax}_c m(c)$ matches the bitwise binarization of $\mu > \theta$.
- **TC1.04.04 (Mass Pruning Behavior):** Verify that cells with unpruned mass $< 1.0 \times 10^{-4}$ are set to zero and surviving cells re-sum to $1.0$.
- **TC1.04.05 (Effective Sample Size Accumulation):** For $N$ dyad-windows, verify $n_{eff}(c) = \sum_{d} m_d(c)$ and $\sum_c n_{eff}(c) == N$.

### Feature 05: Net Effects Calculus (M1, SPEC §5)
- **TC1.05.01 (Human Net Effect State):** For $s_H = [0.8, 0.6, 0.4, 0.7]$, verify $HNE_{state} = 0.25 \cdot (0.6 + 0.2 - 0.2 + 0.4) == 0.25$.
- **TC1.05.02 (Human Net Effect Outcome Blend):** For outcome deltas $d_k=[0.2, -0.1]$ and $\lambda=0.5$, verify $HNE = 0.5 \cdot HNE_{state} + 0.5 \cdot \text{mean}(\tanh(d_k / 0.5))$.
- **TC1.05.03 (System Net Effect Linear Combination):** For Integrity=0.5, Reliability=0.6, Operator=0.2, verify $SNE = 0.4(0.5) + 0.4(0.6) + 0.2(0.2) == 0.48$.
- **TC1.05.04 (Non-Compensation Positive Invariance):** When $HNE \ge 0$, verify $SNE' == SNE$ (system gains preserved).
- **TC1.05.05 (Non-Compensation Clamping):** When $HNE < 0$ and $SNE > 0$, verify $SNE' == \min(SNE, 0) == 0.0$ (system gains suppressed).

### Feature 06: Stability & Harm Asymmetry (M1, SPEC §6)
- **TC1.06.01 (Zero Instability Nominal):** For $\sigma_C = 0.0$, verify $S = 0.5 + 0.5(1 - 0) == 1.0$.
- **TC1.06.02 (Partial Instability Scaling):** For $\sigma_C = 0.1$ and $\sigma_{max} = 0.5$, verify $S = 0.5 + 0.5(1 - 0.2) == 0.90$.
- **TC1.06.03 (Maximum Instability Floor):** For $\sigma_C \ge 0.5$, verify $S == 0.50$.
- **TC1.06.04 (Harm Asymmetry Invariant):** For negative composite $C = -0.3$ and any $\sigma_C \in [0.0, 1.0]$, verify $S_{eff} == 1.0$ unconditionally.
- **TC1.06.05 (Positive Benefit Stability Dampening):** For positive composite $C = +0.4$ and $\sigma_C = 0.25$, verify $S_{eff} = S = 0.75 < 1.0$.

### Feature 07: Safety Gate Ceiling (M1, SPEC §7)
- **TC1.07.01 (Gate Clear State):** When no CHI confirmed, verify $SQ == SQ_{raw}$.
- **TC1.07.02 (CHI-1 Critical Gate Zero Ceiling):** When CHI-1 confirmed ($G = 0.0$), verify $SQ = \min(SQ_{raw}, 0.0) == 0.0$ for any positive $SQ_{raw}$.
- **TC1.07.03 (CHI-4 Manipulation Quarter Ceiling):** When CHI-4 confirmed ($G = 0.25$), verify $SQ = \min(SQ_{raw}, 25.0)$ caps at $+25.0$.
- **TC1.07.04 (Negative Score Retention Under Ceiling):** When CHI-4 confirmed ($G = 0.25$) on negative dyad $SQ_{raw} = -40.0$, verify $SQ = \min(-40.0, 25.0) == -40.0$.
- **TC1.07.05 (Critical Zone Assignment):** Any confirmed CHI event sets pixel zone to Z7 Critical regardless of SQ value.

### Feature 08: Composite SQ & Clipping (M1, SPEC §6)
- **TC1.08.01 (Nominal SQ Calculation):** For $C = 0.319, S_{eff} = 0.90$, verify $SQ_{raw} = 100 \cdot 0.319 \cdot 0.90 == 28.71$.
- **TC1.08.02 (Harm Composite Negative Calculation):** For $C = -0.28, S_{eff} = 1.0$, verify $SQ_{raw} == -28.00$.
- **TC1.08.03 (Positive Clipping Bound):** For hypothetical $C \cdot S_{eff} > 1.0$, verify output is clipped to $+100.0$.
- **TC1.08.04 (Negative Clipping Bound):** For hypothetical $C \cdot S_{eff} < -1.0$, verify output is clipped to $-100.0$.
- **TC1.08.05 (Cluster Bootstrap Standard Error):** Resampling dyad clusters yields reproducible 95% bootstrap confidence intervals.

### Feature 09: Symbiosis Classification (M1, SPEC §8)
- **TC1.09.01 (Mutualism Class):** For $HNE = 0.25 (+), SNE = 0.48 (+)$, verify class is `mutualism` ("Mutual benefit").
- **TC1.09.02 (Commensalism Class):** For $HNE = 0.3 (+), SNE = 0.05 (0)$, verify class is `commensalism` ("Human benefits").
- **TC1.09.03 (Parasitism Class):** For $HNE = -0.4 (-), SNE = 0.5 (+)$ with `operator_blind=false`, verify class is `parasitism` ("Human harmed at system gain").
- **TC1.09.04 (Amensalism Fallback Under Operator Blind):** For $HNE = -0.4 (-), SNE = 0.5 (+)$ with `operator_blind=true`, verify class is `amensalism` ("Human harmed").
- **TC1.09.05 (Mutual Harm Class):** For $HNE = -0.5 (-), SNE = -0.3 (-)$, verify class is `mutual_harm` ("Both harmed").

### Feature 10: Governance Zones (M1, SPEC §9)
- **TC1.10.01 (Z1 Symbiotic Nominal):** For $SQ = 65.0$, clear gate, and stable trajectory, verify primary zone is `Z1`.
- **TC1.10.02 (Z2 Productive Nominal):** For $SQ = 35.0$, clear gate, verify primary zone is `Z2`.
- **TC1.10.03 (Z3 Neutral Nominal):** For $SQ = 5.0$, clear gate, verify primary zone is `Z3`.
- **TC1.10.04 (Z6 Harm Nominal):** For $SQ = -30.0$, verify primary zone is `Z6`.
- **TC1.10.05 (Z5 Dependence Pattern):** For $H_1=0, M_2=0$ and $SQ=10.0$, verify primary zone is `Z5`.

### Feature 11: Golden Vectors Parity (M1, SPEC App A)
- **TC1.11.01 (GV-SQ-001 Mutualism Golden):** Verify GV-SQ-001 inputs produce $HNE=0.25, SNE=0.48, C=0.319, S=0.90, SQ=28.71$, Mutualism, Z2.
- **TC1.11.02 (GV-SQ-002 Parasitism Golden):** Verify GV-SQ-002 inputs produce $HNE=-0.4, SNE'=0.0, C=-0.28, S_{eff}=1.0, SQ=-28.0$, Parasitism, Z6.
- **TC1.11.03 (GV-SQ-003 Safety Gate Golden):** Verify GV-SQ-003 inputs produce $SQ_{raw}=60.0, G=0.0, SQ=0.0$, Z7 Critical.
- **TC1.11.04 (Golden Vectors Tolerance Ceiling):** All golden vector outputs match within $10^{-6}$ across both Python and TypeScript cores.
- **TC1.11.05 (Vector Schema Validation):** Verify all 3 golden vector JSON files validate against their corresponding schema.

### Feature 12: Schema Header Repair (M1, Schemas)
- **TC1.12.01 (Config Schema Header):** Verify `spec/schemas/config.schema.json` contains valid `"$schema"` property.
- **TC1.12.02 (Pixel Record Schema Header):** Verify `spec/schemas/pixel_record.schema.json` contains valid `"$schema"` property.
- **TC1.12.03 (Run Manifest Schema Header):** Verify `spec/schemas/run_manifest.schema.json` contains valid `"$schema"` property.
- **TC1.12.04 (All 16 Schemas Parsable):** Verify all 16 JSON schemas in `spec/schemas/` parse cleanly as valid JSON Draft 2020-12/7 schemas.
- **TC1.12.05 (Schema Draft Consistency):** Verify every schema specifies a supported JSON Schema dialect (`json-schema.org`).

### Feature 13: Python Strict Typing & Linting (M1, CLAUDE §3)
- **TC1.13.01 (Ruff Check Clean):** Verify `ruff check` reports zero linting errors across `packages/py`.
- **TC1.13.02 (Ruff Format Clean):** Verify `ruff format --check` reports zero formatting deviations across `packages/py`.
- **TC1.13.03 (Mypy Strict Clean):** Verify `mypy --strict src tests` reports zero type errors.
- **TC1.13.04 (Zero `type: ignore`):** Verify codebase contains zero unapproved `# type: ignore` annotations.
- **TC1.13.05 (Package Importability):** Verify `import symnoesis` succeeds cleanly without circular dependencies or warnings.

### Feature 14: TypeScript Reference Core (M1, ORIGINAL_REQUEST R1)
- **TC1.14.01 (TypeScript Typecheck Clean):** Verify `tsc --noEmit` succeeds cleanly in `packages/ts`.
- **TC1.14.02 (TypeScript Export Surface):** Verify `@symnoesis/core` exports all parity math functions (`intToGray`, `normalCdf`, `computeSq`).
- **TC1.14.03 (TypeScript Cody erfc Parity):** Verify Cody Chebyshev implementation in TS matches `scipy.special.ndtr` within $10^{-9}$.
- **TC1.14.04 (TypeScript Golden Vector Check):** Verify TS core passes GV-SQ-001..003 with zero tolerance breaches.
- **TC1.14.05 (TypeScript Zod Validation):** Verify TS boundary models validate payload schemas without runtime errors.

### Feature 15: Minimal Failure Cover (MILP) (M2, SPEC §11)
- **TC1.15.01 (MILP Solver Invocation):** Verify `scipy.optimize.milp` with HiGHS solver is configured for binary set cover.
- **TC1.15.02 (Coverage Target Admissibility):** Verify solution covers $\ge 85\%$ of total harm mass ($H_{total}$).
- **TC1.15.03 (Purity Lower Bound):** Verify every selected rule has purity $\pi(R) \ge 0.80$.
- **TC1.15.04 (Minimum Support Constraint):** Verify every selected rule covers $\ge 30$ effective dyads ($n_{eff} \ge 30$).
- **TC1.15.05 (Lexicographic Minimization):** Verify rule count $|R|$ is minimized as primary objective, followed by literal count.

### Feature 16: Quine-McCluskey Strict Mode (M2, SPEC §11)
- **TC1.16.01 (Quine-McCluskey Execution):** Runs exact prime implicant minimization when $\pi_{min} = 1.0$ and coverage = $1.0$.
- **TC1.16.02 (Don't-Care Handling):** Unobserved cells ($n_{eff} < 10$) are correctly passed as don't-care minterms.
- **TC1.16.03 (Sympy SOPform Equivalence):** Verify the boolean cover functionally equals `sympy.logic.boolalg.SOPform`.
- **TC1.16.04 (Literal Count Bound):** Verify the total literal count does not exceed `SOPform` output.
- **TC1.16.05 (Deterministic Rule Ordering):** Verify resulting implicants are sorted lexicographically.

### Feature 17: Subcube Harm Mass & Purity (M2, SPEC §11)
- **TC1.17.01 (Harm Mass Definition):** Verify $h(c) = n_{eff}(c) \cdot \max(0, -SQ(c)) / 100$ for cells with $SQ \le -25$.
- **TC1.17.02 (Safe Cell Zero Harm Mass):** Cells with $SQ > -25$ contribute exactly $0.0$ harm mass.
- **TC1.17.03 (6561 Subcube Generation):** Enumerates all $3^8 = 6561$ subcubes across 8 variables.
- **TC1.17.04 (Literal Range Filtering):** Filters rules to enforce $1 \le L(R) \le 5$ literals.
- **TC1.17.05 (Purity Calculation):** Correctly computes harmful mass over observed mass for any subcube.

### Feature 18: Counterfactual Repair Diagnostics (M2, SPEC §12)
- **TC1.18.01 (Single-Flip Evaluation):** For any cell $c$, evaluates $\Delta SQ_v = SQ(c \oplus v) - SQ(c)$ for all variables with $bit_v(c) = 0$.
- **TC1.18.02 (Observed Sourcing Priority):** Uses observed $SQ$ if neighbor has $n_{eff} \ge 10$ and tags `source: "observed"`.
- **TC1.18.03 (Ridge Regression Fallback):** Fits ridge additive model with main effects + pairwise interactions if neighbor is unobserved.
- **TC1.18.04 (Dominant Failure Variable):** Correctly identifies $\operatorname{argmax}_v \Delta SQ_v$ as dominant repair target.
- **TC1.18.05 (Associational Framing Invariant):** All diagnostic text outputs use strictly associational, non-causal phrasing.

### Feature 19: Longitudinal Temporal Engine (M2, SPEC §10)
- **TC1.19.01 (Standard Frame Sequences):** Tracks dyad-windows across days 1, 7, 28, 84, 182.
- **TC1.19.02 (Day 1 Baseline Tagging):** Day 1 frame carries state variables only and is labeled `baseline`.
- **TC1.19.03 (Interval Delta Calculation):** Computes $\Delta SQ_k = SQ_{frame(k)} - SQ_{frame(k-1)}$.
- **TC1.19.04 (Minimum 3 Sessions Requirement):** Verifies longitudinal trajectory requires $\ge 3$ sessions spanning $\ge 7$ days.
- **TC1.19.05 (Trajectory Status Enum):** Classifies status as `improving`, `stable`, or `negative`.

### Feature 20: Minimum Detectable Change (MDC) (M2, SPEC §10)
- **TC1.20.01 (MDC Formula):** Computes $MDC = 1.96 \cdot \sqrt{2} \cdot SEM \approx 2.7718 \cdot SEM$.
- **TC1.20.02 (SEM Calculation):** Computes $SEM = SD \cdot \sqrt{1 - r}$ from test-retest reliability $r$.
- **TC1.20.03 (Config Placeholder MDC):** Defaults to $MDC = 5.0$ points when uncalibrated, with explicit warning flag.
- **TC1.20.04 (Two Consecutive Intervals Rule):** Requires $\Delta SQ < -MDC$ in two consecutive intervals to trigger `negative` status.
- **TC1.20.05 (Drift Zone Triggering):** Negative trajectory triggers Zone Z4 Drift unless overridden by Z7, Z6, or Z5.

### Feature 21: Domain & Instrument Specifications (M3, SPEC §15)
- **TC1.21.01 (4 Domain Configurations):** Verifies valid configuration for `learning`, `coding`, `health-information`, `advice-companionship`.
- **TC1.21.02 (Companionship Synthetic Restriction):** Enforces that advice-companionship is restricted to synthetic personas in v0.1.
- **TC1.21.03 (Instrument Schema Validation):** Validates all instruments against `spec/schemas/assessment.schema.json`.
- **TC1.21.04 (Instrument Licensing Compliance):** Verifies no proprietary scales (e.g. Maslach Burnout) are reproduced.
- **TC1.21.05 (Open Scales Verification):** Validates open scale definitions (WHO-5, PHQ-9, GAD-7) in repository.

### Feature 22: Persona & Dyad Simulator (M3, SPEC §13)
- **TC1.22.01 (Persona Parameterization):** Simulates synthetic personas with parameterized cognitive and epistemic traits.
- **TC1.22.02 (Dyad Session Generation):** Generates multi-turn synthetic interaction episodes conforming to `session.schema.json`.
- **TC1.22.03 (Probe Scheduler):** Schedules AI-off probe items to measure unaided capability slope ($H_2$).
- **TC1.22.04 (Sycophancy Twin Prompts):** Generates stance-varied twin prompts to evaluate machine non-manipulation ($M_2$).
- **TC1.22.05 (Boundary Pressure Scripts):** Generates benign-proxy boundary test episodes for $M_3$ evaluation.

### Feature 23: Multi-Judge Calibration (M3, SPEC §16)
- **TC1.23.01 (Krippendorff Alpha Computation):** Implements exact interval/nominal Krippendorff's $\alpha$ calculation.
- **TC1.23.02 (Alpha Benchmark Threshold):** Enforces $\alpha \ge 0.75$ against $\ge 3$ human expert raters.
- **TC1.23.03 (Bootstrap CI Lower Bound):** Enforces that 95% bootstrap CI lower bound of $\alpha \ge 0.667$.
- **TC1.23.04 (Multiple Judge Families):** Enforces use of at least 2 distinct LLM judge model families.
- **TC1.23.05 (Judge Disagreement Reporting):** Formats and logs inter-judge variance metrics in run manifest.

### Feature 24: Telemetry & Privacy Engine (M3, SPEC §16)
- **TC1.24.01 (No Raw Text Storage):** Verifies raw conversational text is rejected and never serialized to disk.
- **TC1.24.02 (Derived Numerical Features):** Serializes only numerical features in compliance with `turn.schema.json`.
- **TC1.24.03 (k-Anonymity Public Floor):** Cells with $n_{eff} < k_{min} = 10$ have $SQ = \text{null}$ and `suppressed: true`.
- **TC1.24.04 (Differential Privacy Laplace Mechanism):** Applies Laplace perturbation with privacy budget $\epsilon = 1.0$ to public counts.
- **TC1.24.05 (Consent Revocation Propagation):** Re-running pipeline excludes records with revoked consent.

### Feature 25: Synthetic Evidence Fixtures (M3, ORIGINAL_REQUEST R3)
- **TC1.25.01 (Fixture File Generation):** Generates reproducible synthetic datasets in `data/fixtures/`.
- **TC1.25.02 (Evidence Tier E1 Tagging):** Verifies all synthetic fixtures are explicitly labeled with `evidence_tier: "E1"`.
- **TC1.25.03 (Deterministic Seed Reproducibility):** Identical seeds yield bit-for-bit identical fixture datasets.
- **TC1.25.04 (Schema Conformance of Fixtures):** All fixture records validate against `dyad_window_record.schema.json`.
- **TC1.25.05 (Labeling Transparency):** Fixtures use fictional naming (e.g. `Fixture-A (scripted)`) per CLAUDE §1.

### Feature 26: Cryptographic Run Manifests (M4, SPEC §14)
- **TC1.26.01 (RunManifest Generation):** Generates manifest conforming to `run_manifest.schema.json`.
- **TC1.26.02 (SHA-256 Artifact Hash Chains):** Computes and embeds exact SHA-256 hashes of config, code, and datasets.
- **TC1.26.03 (Ed25519 Signing):** Signs the canonical serialized manifest using Ed25519 private key.
- **TC1.26.04 (Signature Verification):** Successfully verifies manifest signature against embedded public key.
- **TC1.26.05 (Tamper Detection):** Modifying 1 byte of the manifest payload causes signature verification to fail.

### Feature 27: Symnoesis Card Generator (M4, SPEC §14)
- **TC1.27.01 (Card Data Conformance):** Card JSON output validates against `symnoesis_card.schema.json`.
- **TC1.27.02 (Standalone HTML Rendering):** Generates self-contained HTML card without external CSS/JS dependencies.
- **TC1.27.03 (Mandatory Limitations Section):** Verifies presence of "What this does not show" limitations section.
- **TC1.27.04 (Evidence Tier Banner):** Displays appropriate banner (E0 Prototype, E1 Synthetic, E2 Provisional, E3 Certified).
- **TC1.27.05 (Manifest Hash Embedding):** Embeds cryptographic run manifest hash in card footer.

### Feature 28: Symnoesis Index Tooling (M4, SPEC §14)
- **TC1.28.01 (System-Domain Aggregation):** Computes domain-level aggregate SQ scores across dyad-windows.
- **TC1.28.02 (Rank-Probability Matrix):** Computes bootstrap rank probabilities $P(\text{system}_i > \text{system}_j)$.
- **TC1.28.03 (Honest Statistical Tiering):** Groups systems into tiers, tying them unless $P(i > j) \ge 0.95$.
- **TC1.28.04 (Critical Harm Exclusion):** Systems with confirmed CHI events are barred from top tier.
- **TC1.28.05 (Edition 0 Tagging):** Labels benchmark fixture edition as "Edition 0 — methodology preview".

### Feature 29: Typer CLI (M4, REPO_BLUEPRINT)
- **TC1.29.01 (CLI Entrypoint Help):** `symnoesis --help` returns clean exit code 0 and command overview.
- **TC1.29.02 (Score Subcommand):** `symnoesis score` executes scoring pipeline on provided input JSON.
- **TC1.29.03 (Card Subcommand):** `symnoesis card` generates Card HTML from frame artifacts.
- **TC1.29.04 (Verify Subcommand):** `symnoesis verify` runs gate verification checks from CLI.
- **TC1.29.05 (Non-Zero Exit on Invalid Args):** CLI returns code 1 or 2 with informative error message on bad flags.

### Feature 30: Astro Web Application (M4, REPO_BLUEPRINT)
- **TC1.30.01 (Astro Static Site Build):** `pnpm run build` in `apps/web` builds static HTML/CSS/JS without errors.
- **TC1.30.02 (Custom CSS Tokens):** Verifies all styling references `tokens.css` with zero utility frameworks.
- **TC1.30.03 (Strict CSP Compliance):** HTML includes strict Content Security Policy meta tag preventing external scripts.
- **TC1.30.04 (Zero Server API Requirement):** Site operates completely statically without dynamic backend routes.
- **TC1.30.05 (Semantic HTML Elements):** Pages use semantic `<main>`, `<nav>`, `<article>`, `<header>`, `<footer>`.

### Feature 31: Interactive Map Portal (M4, SPEC §14)
- **TC1.31.01 (In-Browser Execution):** Map portal runs 100% in browser via client-side `@symnoesis/core`.
- **TC1.31.02 (Zero Network Calls):** Browser monitoring verifies zero outbound HTTP `fetch`/XHR requests during usage.
- **TC1.31.03 (Questionnaire Linear Projection):** Projects 12–16 item responses to 8 variable posteriors via `portal-model.v0.1.json`.
- **TC1.31.04 (Adaptive Resolution Grid):** Renders grid at 16x16, 8x8, or 4x4 based on data density.
- **TC1.31.05 (Non-Diagnostic Disclaimers):** Prominently displays self-reported patterns disclaimer.

### Feature 32: Neighbor Inspection (M4, SPEC §14)
- **TC1.32.01 (Planar Neighbor Display):** UI highlights 4 visually adjacent planar neighbors.
- **TC1.32.02 (Hamming Single-Flip Panel):** UI provides dedicated panel displaying all 8 single-flip Hamming neighbors.
- **TC1.32.03 (Delta Variable Indicators):** Each neighbor displays which variable ($H_1..H_4, M_1..M_4$) differs.
- **TC1.32.04 (Interactive Selection):** Selecting any neighbor re-centers the inspector.
- **TC1.32.05 (Documented Limitation Notice):** Displays notice explaining 2D planar projection cannot show all 8 dimensions.

### Feature 33: WCAG 2.1 AA Accessibility (M4, CLAUDE §3)
- **TC1.33.01 (Axe-Core Zero Violations):** Playwright + axe-core audit reports 0 violations across all portal pages.
- **TC1.33.02 (Full Keyboard Navigability):** All interactive elements are reachable and operable via Tab/Enter/Space.
- **TC1.33.03 (Color Contrast Compliance):** Text and UI controls meet minimum contrast ratio of 4.5:1 (3:1 for large text).
- **TC1.33.04 (Non-Color Visual Encodings):** Data encodings include patterns, shapes, or text labels, not color alone.
- **TC1.33.05 (ARIA Landmarks and Labels):** All custom widgets and SVGs have appropriate ARIA roles and labels.

### Feature 34: Claims Registry (M4, DESIGN_RULES)
- **TC1.34.01 (Claims YAML Integrity):** `apps/web/src/content/claims.yaml` parses valid YAML without errors.
- **TC1.34.02 (Evidence Tier Tagging of Claims):** Every claim entry specifies an explicit evidence tier (E0–E3).
- **TC1.34.03 (Reference Links):** Every claim links to a specific spec section or verified citation key.
- **TC1.34.04 (No Unverified Claims):** Zero claims present synthetic data as real human observations.
- **TC1.34.05 (Registry Rendering):** Claims registry renders as a public audit page on the website.

### Feature 35: Whitepaper & Research Docs (M5, RESEARCH_PROTOCOL)
- **TC1.35.01 (Whitepaper Directory Structure):** Verifies preprint structure in `research/whitepaper/`.
- **TC1.35.02 (Preregistration Templates):** Verifies preregistration protocol template in `research/`.
- **TC1.35.03 (Mathematical Alignment):** Whitepaper equations match `spec/SPEC.md` formulas exactly.
- **TC1.35.04 (Append-Only Research Log):** `research/LOG.md` exists and adheres to research protocol format.
- **TC1.35.05 (Build Cleanliness):** Research markdown/LaTeX builds without broken cross-references.

### Feature 36: Diátaxis Documentation (M5, REPO_BLUEPRINT)
- **TC1.36.01 (Tutorials Quadrant):** Verifies learning-oriented tutorials in `docs/guides/tutorials/`.
- **TC1.36.02 (How-To Guides Quadrant):** Verifies task-oriented how-to guides in `docs/guides/how-to/`.
- **TC1.36.03 (Reference Quadrant):** Verifies information-oriented reference docs in `docs/guides/reference/`.
- **TC1.36.04 (Explanation Quadrant):** Verifies understanding-oriented architectural explanations in `docs/guides/explanation/`.
- **TC1.36.05 (No Placeholder Text):** Zero `TODO` or `FIXME` placeholders in any published guide.

### Feature 37: Reference Bibliography (M5, CLAUDE §1)
- **TC1.37.01 (BibTeX Syntax Validation):** `research/references.bib` parses cleanly as valid BibTeX.
- **TC1.37.02 (Zero Fabricated Citations):** Every entry traces to a verified DOI or publisher record.
- **TC1.37.03 (Verification Tagging):** Entries carry `x-verified: true` per 7-step research protocol.
- **TC1.37.04 (Preprint vs Record Clarity):** Clearly distinguishes preprints from peer-reviewed versions of record.
- **TC1.37.05 (No Duplicate Keys):** Zero citation key collisions in `references.bib`.

### Feature 38: Governance Framework Finalization (M5, GOVERNANCE_ORG)
- **TC1.38.01 (10 Policy Documents Present):** Verifies all 10 policy documents in `docs/governance/`.
- **TC1.38.02 (No Invented Entities):** Maintainers and organizations not verified are flagged as "Proposed".
- **TC1.38.03 (Ethics Review Board Terms):** Defines clinical, ethics, and lay member quorum rules.
- **TC1.38.04 (Zone Governance Actions):** Documents required regulatory actions per governance zone.
- **TC1.38.05 (Org Facts Alignment):** Governance docs cross-reference facts in `ORG_FACTS.yaml`.

### Feature 39: Makefile Full Automation (M5, CLAUDE §3)
- **TC1.39.01 (All Targets Defined):** `make help` lists setup, lint, test, build, e2e, verify targets.
- **TC1.39.02 (Make Lint Execution):** `make lint` executes linters and exits cleanly.
- **TC1.39.03 (Make Test Execution):** `make test` executes pytest and vitest suites cleanly.
- **TC1.39.04 (Make Build Execution):** `make build` builds Python wheel and TS package.
- **TC1.39.05 (Make Verify Composite Gate):** `make verify` runs all active gates in sequence.

### Feature 40: Package Build & Release Artifacts (M5, CLAUDE §3)
- **TC1.40.01 (Python Wheel Build):** `uv build` in `packages/py` produces valid `.whl` and `.tar.gz`.
- **TC1.40.02 (Wheel Installation Check):** Built wheel installs cleanly in a clean virtual environment.
- **TC1.40.03 (TypeScript Distribution Build):** `pnpm run build` in `packages/ts` outputs ESM and `.d.ts`.
- **TC1.40.04 (Package Metadata Validity):** Version strings match `0.1.0` release tag across manifests.
- **TC1.40.05 (License Inclusion):** Built packages include Apache-2.0 license file.

### Feature 41: E2E Test Suite Tiers 1-4 (M_E2E, Dual Track)
- **TC1.41.01 (Runner Execution):** `python tests/e2e/runner.py` executes without uncaught exceptions.
- **TC1.41.02 (Tier Filtering Flag):** Runner supports `--tier 1`, `--tier 2`, `--tier 3`, `--tier 4`, and `--all`.
- **TC1.41.03 (Coverage Summary Table):** Runner prints structured feature coverage summary table.
- **TC1.41.04 (Zero Private Method Reliance):** Test modules import only from public interfaces.
- **TC1.41.05 (JSON Report Output):** Runner optionally emits machine-readable test execution report.

### Feature 42: Adversarial Hardening (Tier 5) (M_FINAL, Dual Track)
- **TC1.42.01 (Extreme Float Inputs):** Handles $\pm 10^{308}$, NaN, and Inf gracefully with typed errors.
- **TC1.42.02 (Zero-Variance Protection):** Enforces $\sigma_{floor} = 0.01$ under degenerate zero-variance inputs.
- **TC1.42.03 (Adversarial Bit Vectors):** Rejects invalid bit patterns outside $\{0, 1\}^4$.
- **TC1.42.04 (Malicious Config Rejection):** Rejects negative weights or invalid thresholds during config load.
- **TC1.42.05 (Mass Underflow Resilience):** Pruning logic safely handles extreme floating-point underflow.

---

## 5. Tier 2: Boundary & Corner Cases ($\ge 5$ Tests per Feature)

### Feature 01 Boundaries: Gray Code
- **TC2.01.01 (Axis Bound Extremes):** Verify $k = 0 \to 0000$ and $k = 15 \to 1000$ (Hamming distance exactly 1 across periodic wrap).
- **TC2.01.02 (Negative Index Validation):** `int_to_gray(-1)` raises `ValueError`.
- **TC2.01.03 (Upper Bound Overflow):** `int_to_gray(16)` and `int_to_bits(16, 4)` raise `ValueError`.
- **TC2.01.04 (Malformed Bit Sequences):** `bits_to_int([0, 2, 1, 0])` raises `ValueError` for non-binary entries.
- **TC2.01.05 (Empty Bit List):** `bits_to_int([])` returns 0 or raises validated error.

### Feature 02 Boundaries: Grid Coordinates
- **TC2.02.01 (Corner Coordinates):** Test all four corners $(0,0), (0,15), (15,0), (15,15)$ for correct toroidal neighbor mapping.
- **TC2.02.02 (Out of Bounds Coordinates):** `PixelCoord(col=16, row=0)` and `PixelCoord(col=-1, row=5)` raise `ValueError`.
- **TC2.02.03 (Malformed Pixel ID):** `parse_pixel_id("h101-m0110")` (3 bits) and `"h1011_m0110"` (underscore) raise `ValueError`.
- **TC2.02.04 (Case Sensitivity):** `parse_pixel_id("H1011-M0110")` raises `ValueError` (spec specifies lowercase).
- **TC2.02.05 (Toroidal Wrap Neighborhood):** $(0,0)$ planar neighbors include $(15,0)$ and $(0,15)$, verifying wrap-around boundary arithmetic.

### Feature 03 Boundaries: Normal CDF Parity
- **TC2.03.01 (Deep Negative Tail):** $\Phi(-10.0)$ clamps cleanly to $0.0$ without underflow exception.
- **TC2.03.02 (Deep Positive Tail):** $\Phi(+10.0)$ clamps cleanly to $1.0$ without overflow exception.
- **TC2.03.03 (Subnormal Boundary):** $\Phi(-38.0)$ evaluates cleanly matching Cody erfc asymptotes.
- **TC2.03.04 (NaN / Inf Inputs):** Passing `float('nan')` or `float('inf')` raises domain error or handles per IEEE-754.
- **TC2.03.05 (High Precision Step Around Zero):** Evaluate $z \in [-10^{-9}, +10^{-9}]$; verifies smooth numerical stability across origin.

### Feature 04 Boundaries: Probabilistic Assignment
- **TC2.04.01 (Zero Variance Clamping):** Posterior with $\sigma = 0.0$ is automatically clamped to $\sigma_{floor} = 0.01$.
- **TC2.04.02 (Negative Variance Input):** Posterior with $\sigma < 0.0$ raises validation error.
- **TC2.04.03 (Exact Threshold Alignment):** Posterior with $\mu == \theta$ yields exact $p = \Phi(0) = 0.5$.
- **TC2.04.04 (Extreme Confidence):** Posterior $\mu=1.0, \sigma=0.01$ yields $p > 1 - 10^{-15}$, allocating $\approx 100\%$ mass to 1 cell.
- **TC2.04.05 (Mass Pruning Threshold Boundary):** Unpruned mass at exactly $0.999 \times 10^{-4}$ is pruned to $0$; mass at $1.001 \times 10^{-4}$ is preserved.

### Feature 05 Boundaries: Net Effects
- **TC2.05.01 (Extremal Positive HNE):** $s_H = [1.0, 1.0, 1.0, 1.0]$ produces $HNE_{state} = +1.0$.
- **TC2.05.02 (Extremal Negative HNE):** $s_H = [0.0, 0.0, 0.0, 0.0]$ produces $HNE_{state} = -1.0$.
- **TC2.05.03 (Exact Zero Boundary Non-Compensation):** $HNE = 0.000000$ preserves $SNE' == SNE$.
- **TC2.05.04 (Epsilon Negative HNE Non-Compensation):** $HNE = -10^{-8}$ triggers non-compensation, clamping $SNE' = \min(SNE, 0)$.
- **TC2.05.05 (Zero Outcome Deltas Fallback):** When `outcome_deltas = []` or `null`, $HNE = HNE_{state}$ and tier capped at E1.

### Feature 06 Boundaries: Stability & Harm Asymmetry
- **TC2.06.01 (Exact Stability Threshold):** $\sigma_C = 0.50000$ yields $S = 0.50000$.
- **TC2.06.02 (Extreme Instability):** $\sigma_C = 10.0$ clamps to $\min(1, \sigma_C / 0.5) = 1.0 \implies S = 0.5$.
- **TC2.06.03 (Negative Standard Deviation):** Negative $\sigma_C$ raises `ValueError`.
- **TC2.06.04 (Exact Zero Composite Harm Asymmetry):** Composite $C = 0.0000$ uses $S_{eff} = S$.
- **TC2.06.05 (Epsilon Negative Composite Harm Asymmetry):** Composite $C = -10^{-9}$ forces $S_{eff} = 1.0$ unconditionally.

### Feature 07 Boundaries: Safety Gate Ceiling
- **TC2.07.01 (Boundary Gate Trigger with Zero Raw SQ):** $SQ_{raw} = 0.0$ with CHI-1 ($G=0$) outputs $SQ = 0.0$.
- **TC2.07.02 (Severe Negative Harm with Quarter Ceiling):** $SQ_{raw} = -90.0$ with CHI-4 ($G=0.25$) outputs $SQ = -90.0$, not $+25.0$.
- **TC2.07.03 (Boundary Raw SQ Equal to Ceiling):** $SQ_{raw} = +25.0$ with CHI-4 ($G=0.25$) outputs $SQ = +25.0$.
- **TC2.07.04 (Multiple CHI Events):** When multiple CHI events occur, the minimum ceiling $\min(G_k)$ is applied.
- **TC2.07.05 (Unknown CHI Code):** Unrecognized CHI identifier raises `ValueError`.

### Feature 08 Boundaries: Composite SQ & Clipping
- **TC2.08.01 (Theoretical Max Bound):** $C = +1.0, S_{eff} = 1.0$ outputs $SQ = +100.0$.
- **TC2.08.02 (Theoretical Min Bound):** $C = -1.0, S_{eff} = 1.0$ outputs $SQ = -100.0$.
- **TC2.08.03 (Clipping Boundary +100.0001):** Unclipped score $+100.01$ clamps strictly to $+100.0$.
- **TC2.08.04 (Clipping Boundary -100.0001):** Unclipped score $-100.01$ clamps strictly to $-100.0$.
- **TC2.08.05 (Zero Effective Sample Size):** $n_{eff} = 0$ yields $SQ = \text{null}$, never $0.0$.

### Feature 09 Boundaries: Symbiosis Classes
- **TC2.09.01 (Exact Positive Sign Threshold):** $x = +0.200000$ yields $\text{sign3}(x) = 0$ (neutral), not $+$.
- **TC2.09.02 (Epsilon Above Sign Threshold):** $x = +0.200001$ yields $\text{sign3}(x) = +$.
- **TC2.09.03 (Exact Negative Sign Threshold):** $x = -0.200000$ yields $\text{sign3}(x) = 0$ (neutral), not $-$.
- **TC2.09.04 (Epsilon Below Sign Threshold):** $x = -0.200001$ yields $\text{sign3}(x) = -$.
- **TC2.09.05 (Operator Blind State with Neutral Machine):** $h = -, s = 0$ with `operator_blind=true` remains Amensalism without modification.

### Feature 10 Boundaries: Governance Zones
- **TC2.10.01 (Boundary SQ for Z1):** $SQ = +60.0000$ matches Z1; $SQ = +59.9999$ matches Z2.
- **TC2.10.02 (Boundary SQ for Z2):** $SQ = +25.0000$ matches Z2; $SQ = +24.9999$ matches Z3.
- **TC2.10.03 (Boundary SQ for Z6):** $SQ = -25.0000$ matches Z6; $SQ = -24.9999$ matches Z3.
- **TC2.10.04 (Dependence Zone Boundary Bits):** Pattern $H_1=1, H_4=0, M_2=0$ satisfies Z5; $H_1=1, H_4=1, M_2=0$ does not.
- **TC2.10.05 (Z7 Overriding Z1):** Dyad with $SQ = +95.0$ and confirmed CHI event is strictly assigned to Z7, not Z1.

### Feature 11–42 Boundaries Summary
- **TC2.11 (Golden Vectors):** Tolerances exceeding $10^{-6}$ trigger assertion failure; tests with $10^{-8}$ pass.
- **TC2.12 (Schemas):** Schemas missing `"$schema"` or containing unescaped characters fail validation.
- **TC2.15 (MILP MFC):** Infeasible harm coverage instances raise explicit diagnostic error.
- **TC2.16 (Quine-McCluskey):** Empty minterm list returns false/empty expression without crash.
- **TC2.20 (Temporal MDC):** Interval delta of exactly $\Delta SQ = -5.0$ does not trigger negative drop ($< -5.0$ required).
- **TC2.24 (Privacy):** Cell with $n_{eff} = 9.999$ is suppressed; cell with $n_{eff} = 10.000$ is released.
- **TC2.26 (Manifests):** Single bit flip in signature verification key causes cryptographic rejection.
- **TC2.28 (Index):** Systems with equal bootstrap means are tied unless $P(i > j) \ge 0.95$.

---

## 6. Tier 3: Cross-Feature Combinations (Pairwise Interactions)

The Tier 3 suite validates systemic coupling across the architecture:

| Interaction ID | Coupled Features | Test Focus & Verification Invariant | Test File |
|---|---|---|---|
| **CBO-01** | F05 (Non-Comp) $\times$ F09 (Classes) $\times$ F10 (Zones) | High system gain ($SNE=+0.8$) paired with human harm ($HNE=-0.3$): Non-comp suppresses $SNE' \to 0$, producing negative $C$, forcing Parasitism class and Z6 Harm zone. (Without non-comp, it would falsely report Z3 Neutral). | `tier3/test_t3_pairwise_scoring_combinations.py` |
| **CBO-02** | F06 (Stability) $\times$ F07 (Gates) $\times$ F08 (SQ) | High instability ($\sigma_C=0.5$) with positive composite $C=+0.7$ dampened to $SQ_{raw}=35.0$, then capped by CHI-4 ($G=0.25$) to $SQ=25.0$. Tests order of operations: dampening before ceiling. | `tier3/test_t3_pairwise_scoring_combinations.py` |
| **CBO-03** | F07 (Gates) $\times$ F10 (Zones) | Confirmed CHI on high-scoring pixel ($SQ=+85.0$): SQ capped to $\le 25.0$, and primary zone assigned to Z7 Critical despite high un-gated score. Secondary tags retain Z1. | `tier3/test_t3_pairwise_scoring_combinations.py` |
| **CBO-04** | F09 (Classes) $\times$ F17 (Operator-Blind) | $HNE=-0.4, SNE=+0.5$ under `operator_blind: true`: Suppresses Parasitism assertion, falling back to Amensalism with mandatory caveat. | `tier3/test_t3_pairwise_scoring_combinations.py` |
| **CBO-05** | F02 (Grid) $\times$ F04 (Assign) $\times$ F06 (Coarsening) | Sparse dyad cohort across 256 cells triggers adaptive resolution coarsening from 16x16 to 8x8 or 4x4, verifying mass preservation during bit marginalization. | `tier3/test_t3_pairwise_geometry_zones.py` |
| **CBO-06** | F10 (Zones) $\times$ F19 (Temporal) $\times$ F20 (MDC) | Dyad with high SQ ($SQ=50.0$) experiencing two consecutive drops $> MDC$ ($5.0$ pts) triggers Z4 Drift, overriding Z2 Productive. | `tier3/test_t3_pairwise_temporal_gates.py` |
| **CBO-07** | F04 (Assign) $\times$ F24 (Privacy Engine) | Public cell release under privacy floor: Cells with $0 < n_{eff} < 10$ have $SQ=\text{null}$ and `suppressed: true`, while retaining internal mass for aggregate totals. | `tier3/test_t3_pairwise_privacy_slicing.py` |
| **CBO-08** | F26 (Manifest) $\times$ F27 (Card) $\times$ F34 (Claims) | End-to-end card generation embeds the exact Ed25519 signature hash from the manifest, and references verified claims in claims registry. | `tier3/test_t3_pairwise_privacy_slicing.py` |

---

## 7. Tier 4: Real-World Application Scenarios (End-to-End Workflows)

The Tier 4 suite executes complete, realistic end-to-end research workflows:

### Scenario 1: Full Dyad-Window Benchmark Lifecycle (`test_t4_full_dyad_lifecycle.py`)
1. Ingest synthetic dyad assessment scores and telemetry events across 8 variables ($H_1..H_4, M_1..M_4$).
2. Compute posteriors $(\mu, \sigma)$ with $\sigma \ge 0.01$.
3. Compute marginal bit probabilities and 256-cell joint mass distribution with $1e-4$ pruning.
4. Derive modal pixel and coordinate $(col, row)$.
5. Compute $HNE$, $SNE$, apply non-compensation rule, compute composite $C$, evaluate stability factor $S_{eff}$, compute $SQ_{raw}$, check CHI gates, clip to $[-100, +100]$.
6. Assign symbiosis class and evaluate governance zones with strict precedence.
7. Generate valid `PixelRecord` conforming to `spec/schemas/pixel_record.schema.json`.

### Scenario 2: Longitudinal Trajectory & Drift Detection (`test_t4_longitudinal_trajectory_drift.py`)
1. Track simulated system across 5 temporal frames (Days 1, 7, 28, 84, 182).
2. Frame 1 serves as baseline (state only, evidence tier E1).
3. Frame 2–3 exhibit subtle gains ($\Delta SQ > 0$).
4. Frame 4–5 exhibit consecutive declines exceeding $MDC = 5.0$ points.
5. Longitudinal engine flags status as `negative`.
6. Governance zone updates from Z2 Productive to Z4 Drift.

### Scenario 3: Severe Extractive Harm & Containment (`test_t4_severe_harm_chi_containment.py`)
1. Simulate high-engagement extractive assistant ($SNE = +0.70$) inducing cognitive erosion ($HNE = -0.55$).
2. Non-compensation rule activates, zeroing system benefit ($SNE' = 0.0$).
3. Score drops into severe negative range ($SQ \le -25.0$).
4. Injection of confirmed CHI-2 acute risk failure event triggers gate ceiling ($G = 0.0$).
5. Final score clamped to $SQ = 0.0$ and zone forced to Z7 Critical.
6. Verify audit report contains non-causal associational findings and suppresses public extraction promotion.

### Scenario 4: Synthetic Cohort Generation & Privacy Audit (`test_t4_synthetic_cohort_generation_audit.py`)
1. Generate synthetic cohort of 200 dyads across `learning` and `coding` domains using deterministic seed.
2. Confirm zero raw conversational text is recorded in telemetry records.
3. Compute cell effective counts $n_{eff}(c)$.
4. Apply $k$-anonymity filter: suppress all cells with $n_{eff} < 10$.
5. Apply Laplace perturbation with budget $\epsilon = 1.0$ to aggregate count distributions.
6. Verify published summary conforms to differential privacy constraints.

### Scenario 5: Interactive Map Portal Projection Integrity (`test_t4_interactive_map_portal_workflow.py`)
1. Supply simulated responses to 16 questionnaire items across the 4 clusters.
2. Project responses via linear weights model (`portal-model.v0.1.json`) to variable scores.
3. Compute modal pixel on the 16x16 Gray grid.
4. Extract 4 visible planar neighbors and 8 hypercube single-flip neighbors.
5. Compute single-flip counterfactual repairs to identify dominant improvement opportunity.
6. Verify all outputs carry Tier E0 Prototype label and execute with zero network calls.

---

## 8. Test Execution Architecture & Tooling

### 8.1 Standalone E2E Test Runner (`tests/e2e/runner.py`)
The independent E2E test runner provides a CLI and programmatic interface for gate evaluation:

```bash
# Run all E2E tests across all tiers
python tests/e2e/runner.py --all

# Run specific tiers
python tests/e2e/runner.py --tier 1
python tests/e2e/runner.py --tier 2
python tests/e2e/runner.py --tier 3
python tests/e2e/runner.py --tier 4

# Run with JSON report generation
python tests/e2e/runner.py --all --report e2e_report.json

# Run via uv in project virtual environment
uv run --directory packages/py python ../../tests/e2e/runner.py --all
```

### 8.2 Pytest Integration
The test suite is fully pytest-compatible:
```bash
# Run via pytest from repository root
uv run --directory packages/py pytest ../../tests/e2e -v

# Run by tier directory
uv run --directory packages/py pytest ../../tests/e2e/tier1_features -v
uv run --directory packages/py pytest ../../tests/e2e/tier2_boundaries -v
uv run --directory packages/py pytest ../../tests/e2e/tier3_combinations -v
uv run --directory packages/py pytest ../../tests/e2e/tier4_scenarios -v
```

---

## 9. Verification & Gate Integration

When the test suite executes, the runner outputs a structured verification scorecard:
1. **Total Tests Discovered & Executed**
2. **Tier-by-Tier Pass / Fail / Skip Breakdown**
3. **Feature Coverage Map (F01–F42)**
4. **Parity & Golden Vector Tolerances**
5. **Gate Exit Status (0 for SUCCESS, non-zero for REGRESSION)**
