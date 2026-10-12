# Contributing to Symnoesis

Thank you for your interest in contributing to Symnoesis (SYMN-01). As an open research initiative, we value correctness, reproducibility, transparent methodology, and careful evidence labeling.

## Development Setup

```bash
# 1. Clone repository
git clone https://github.com/harvatechs/symnoesis.git
cd symnoesis

# 2. Setup pinned toolchains
make setup

# 3. Verify installation
make lint
make test
```

## Workflow and Conventions

1. **State the Task**: Trace your work directly to a normative section in `spec/SPEC.md` or a planned milestone in `docs/agent/04_PLAN.md`.
2. **Tests First**: For all mathematical and logic changes, write property tests (Hypothesis/fast-check) or golden vectors before implementation.
3. **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(core): ...`
   - `fix(web): ...`
   - `docs(spec): ...`
   - `test(py): ...`
4. **Gates**: Run `make verify` before submitting pull requests. All checks must pass.

## Proposing Specification Changes (RFC Process)

Any modification to normative formulas, thresholds, weights, or zones requires an RFC:
1. Copy `rfcs/0000-template.md` to `rfcs/NNNN-proposal-title.md`.
2. Detail rationale, evidence, and backward-compatibility impact.
3. Submit for review by maintainers and the Scientific Advisory Board (SAB).

## Reporting Security Issues

Please review [`SECURITY.md`](./SECURITY.md) for responsible disclosure procedures.
