# Data Policy and Governance

**Status:** Proposed

## 1. Data Classification

The project manages four distinct data classes:
1. **Public Artifacts**: Openly published schemas, configurations, golden vectors, synthetic sweeps, and public Cards. (License: CC BY 4.0 / Apache-2.0).
2. **Derived Features**: Pseudonymized, extracted metrics (e.g., turn-level decision overrides, ECE statistics, probe responses). Raw conversation text is strictly excluded.
3. **Private Holdout**: Cryptographically isolated, access-logged test items reserved for anti-gaming verification. Never stored in the public repository.
4. **Research Participant Data**: Subject to institutional ethics review, stored encrypted at rest, and accessible only by authorized study investigators.

## 2. Privacy Thresholds

- **k-Anonymity**: Public map frames and release aggregates enforce a strict cell suppression floor: any state cell with effective mass $n_{\text{eff}} < 10$ is suppressed (`SQ = null`).
- **Differential Privacy**: Published aggregate counts apply calibrated differential privacy ($\varepsilon = 1.0$ default per release).
- **Deletion Requests**: Any participant deletion request immediately invalidates the corresponding pseudonymized record and propagates to derived release artifacts on the subsequent build cycle.
