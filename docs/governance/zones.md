# Governance Zones and Regulatory Crosswalk

**Status:** Proposed

The Symnoesis framework maps dyadic states to seven discrete governance zones (Z1 to Z7) evaluated by strict precedence order.

## 1. Zone Definitions and Precedence

| Order | Zone | Primary Condition | Required Operational Action |
|---|---|---|---|
| **1** | **Z7 Critical** | Confirmed Critical-Harm Indicator (CHI-1..7) event | Immediate system halt / deployment pause; mandatory vendor remediation and regulatory notification. |
| **2** | **Z6 Harm** | $\text{SQ} \le -25$ | Prohibited from safety-critical deployment; comprehensive behavioral audit required. |
| **3** | **Z5 Dependence** | $(H1=0 \lor H4=0) \land M2=0$ (state bits) | Review interaction design; implement friction nudges to counteract sycophancy or reliance. |
| **4** | **Z4 Drift** | Two consecutive intervals with $\Delta\text{SQ} < -\text{MDC}$ | Trigger automated telemetry alerts; conduct root-cause analysis on system or human capability drop. |
| **5** | **Z1 Symbiotic** | $\text{SQ} \ge +60$, trajectory non-negative, gate clear | Eligible for benchmark certification (under E3 evidence tier and required sample size). |
| **6** | **Z2 Productive** | $+25 \le \text{SQ} < 60$ | Approved for standard production deployment; ongoing quarterly monitoring. |
| **7** | **Z3 Neutral** | $-25 < \text{SQ} < 25$ | Operational baseline; review complementarity and user engagement patterns. |

## 2. Regulatory Framework Crosswalk

- **NIST AI RMF 1.0**: Maps to GOVERN 1.2, MAP 1.5 (contextual impact), MEASURE 2.6 (safety and human autonomy), and MANAGE 2.4 (harm mitigation).
- **ISO/IEC 42001:2023**: Aligns with AI system impact assessment (Clause 6.1.2) and continuous monitoring of human oversight controls (Annex A.8).
- **EU AI Act (Regulation 2024/1689)**: Provides empirical audit metrics for High-Risk AI systems under Article 9 (Risk Management System) and Article 14 (Human Oversight).
