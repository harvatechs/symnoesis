# Symnoesis (SYMN-01)

Symnoesis (SYMN-01) is an open specification and toolkit for measuring the quality, safety, and cognitive impact of long-term human-AI interaction by treating the human and the machine as one unit, the **Dyadic State**, over time.

Model benchmarks evaluate an AI system on isolated prompt-response pairs, which cannot detect subtle degradation in human cognitive independence, skills, or beliefs across weeks of continuous use. Nor can single-turn benchmarks evaluate two-sided interaction dynamics such as machine sycophancy, boundary drift, or unreciprocated reliance. Symnoesis places each observed dyad-window onto a 16 × 16 Gray-coded state map, scores it via the Symnoesis Quotient under a strict safety gate, and isolates harmful regions using the Minimal Failure Cover.

```
       Human Side (H1: Agency, H2: Trajectory, H3: Calibration, H4: Wellbeing)
            [0000]   [0001]   ...   [1111]   ...   [1000]  (16 Gray columns)
Machine [0000]
Side    [0001]             THE SYMNOESIS MAP (16 × 16)
(M1-M4)  ...               256 Dyadic States, Single-Flip Adjacent
        [1000]
```
*(Demonstration layout. Synthetic data only, evidence tier E1.)*

## Status

| Subsystem | Scope | Status | Evidence Tier |
|---|---|---|---|
| **Normative Specification** | `spec/SPEC.md` | v0.1.0 (Draft) | E0 (Specified) |
| **Python Reference Implementation** | `packages/py` | v0.1.0-dev | E1 (Synthetic) |
| **TypeScript Browser Core** | `packages/ts` | v0.1.0-dev | E1 (Synthetic) |
| **Research Website** | `apps/web` | Planned (M7) | E0–E1 |
| **Interactive Map Portal** | `apps/web/src/pages/portal` | Planned (M8) | E0 (Uncalibrated prototype) |
| **Symnoesis Index** | `symnoesis index` | Planned (M6) | E1 (Methodology preview) |
| **Human Cohort Validation** | Independent trials | Roadmap (Phase 3+) | Requires ethics review & funding |

## Quick Start (< 5 Minutes)

```bash
# Clone the repository
git clone https://github.com/harvatechs/symnoesis.git
cd symnoesis

# Install pinned toolchains across Python and Node
make setup

# Run static analysis and tests
make lint
make test

# Run a synthetic baseline sweep and generate a card
uv run symnoesis sweep --fixture fixture-a
uv run symnoesis card --system fixture-a --version v1
```

## How to Cite

See [`CITATION.cff`](./CITATION.cff) or use the following reference:

```bibtex
@software{symnoesis2026,
  author = {{HarVa Groups}},
  title = {Symnoesis (SYMN-01): Measuring Long-Term Human-AI Interaction},
  url = {https://github.com/harvatechs/symnoesis},
  version = {0.1.0},
  year = {2026}
}
```

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for workflow guidelines, Conventional Commits formatting, gate commands, and the RFC process.

## Governance & Ethics

Symnoesis is governed under an open, multi-stakeholder charter outlined in [`GOVERNANCE.md`](./GOVERNANCE.md). No human-subject data is collected without accredited institutional ethics review. See [`docs/agent/08_RESEARCH_PROTOCOL.md`](./docs/agent/08_RESEARCH_PROTOCOL.md) for details.

## License

- Software code is licensed under the [Apache License 2.0](./LICENSE).
- Specification, research documents, and site copy are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](./LICENSE-DOCS).

---

*An initiative by HarVa Groups.*
