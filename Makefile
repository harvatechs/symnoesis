.DEFAULT_GOAL := help

PYTHON := uv run --directory packages/py
PNPM := pnpm

.PHONY: help
help: ## Display available commands
	@echo "Symnoesis (SYMN-01) Gate Runner"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  setup         Install pinned toolchains from lockfiles"
	@echo "  lint          Run static analysis: ruff, mypy, eslint, tsc, markdownlint, codespell"
	@echo "  test          Run unit, property, and parity test suites"
	@echo "  mutation      Run mutation testing (mutmut & Stryker) [M1/M3]"
	@echo "  vectors       Generate golden vectors from specification [M1]"
	@echo "  vectors-check Check golden vectors for regressions [M1]"
	@echo "  gen           Generate types from JSON schemas [M1]"
	@echo "  build         Build distribution packages and static site"
	@echo "  e2e           Run end-to-end and accessibility test suites [M7/M8]"
	@echo "  a11y          Run standalone accessibility audit [M7]"
	@echo "  perf          Run Lighthouse CI performance budgets [M7]"
	@echo "  links         Run link verification on documentation [M7]"
	@echo "  repro         Run reference synthetic sweep and verify hashes [M5]"
	@echo "  docs          Build documentation pages [M7]"
	@echo "  site          Build Astro research website [M7]"
	@echo "  verify        Run all verification gates in order"
	@echo "  clean         Remove build artifacts and caches"

.PHONY: setup
setup: ## Install pinned toolchains from lockfiles
	@echo "==> Setting up Python environment..."
	cd packages/py && uv sync --all-extras
	@echo "==> Setting up Node environment..."
	$(PNPM) install --frozen-lockfile

.PHONY: lint
lint: ## Run linters across Python, TypeScript, Markdown, and spelling
	@echo "==> Linting Python (ruff)..."
	$(PYTHON) ruff check .
	$(PYTHON) ruff format --check .
	@echo "==> Typechecking Python (mypy --strict)..."
	$(PYTHON) mypy src tests
	@echo "==> Typechecking TypeScript (tsc --noEmit)..."
	$(PNPM) -r run typecheck
	@echo "==> Checking code formatting (prettier)..."
	$(PNPM) exec prettier --check .
	@echo "==> Checking markdown (markdownlint)..."
	$(PNPM) exec markdownlint-cli2
	@echo "==> Checking spelling (codespell)..."
	$(PYTHON) codespell ../../ --config ../../.codespellrc -S "*.lock,*/node_modules/*,*/.git/*,*/dist/*,*/.venv/*"

.PHONY: test
test: ## Run unit and parity tests
	@echo "==> Running Python test suite..."
	$(PYTHON) pytest
	@echo "==> Running TypeScript test suite..."
	$(PNPM) -r run test

.PHONY: mutation
mutation: ## Run mutation tests
	@echo "Mutation testing target (mutmut & Stryker) will be fully wired in Milestone 1 & 3."

.PHONY: vectors
vectors: ## Generate golden vectors
	@echo "Golden vector generation target will be fully wired in Milestone 1."

.PHONY: vectors-check
vectors-check: ## Verify golden vectors
	@echo "Golden vector verification target will be fully wired in Milestone 1."

.PHONY: gen
gen: ## Generate types from JSON schemas
	@echo "Type generation target will be fully wired in Milestone 1."

.PHONY: build
build: ## Build packages
	@echo "==> Building Python package..."
	cd packages/py && uv build
	@echo "==> Building TypeScript package..."
	$(PNPM) -r run build

.PHONY: e2e
e2e: ## Run E2E tests
	@echo "E2E tests will be fully wired in Milestone 7 & 8."

.PHONY: a11y
a11y: ## Run accessibility audit
	@echo "Accessibility audit will be fully wired in Milestone 7."

.PHONY: perf
perf: ## Run performance budgets
	@echo "Lighthouse performance audit will be fully wired in Milestone 7."

.PHONY: links
links: ## Check links
	@echo "Link checking target will be fully wired in Milestone 7."

.PHONY: repro
repro: ## Reproducibility sweep
	@echo "Reproducibility sweep target will be fully wired in Milestone 5."

.PHONY: docs
docs: ## Build documentation
	@echo "Docs target will be fully wired in Milestone 7."

.PHONY: site
site: ## Build website
	@echo "Site target will be fully wired in Milestone 7."

.PHONY: verify
verify: setup lint test build ## Run all gate checks
	@echo ""
	@echo "============================================="
	@echo " ALL ACTIVE GATES PASSED (Milestone Baseline)"
	@echo "============================================="

.PHONY: clean
clean: ## Clean build artifacts
	@echo "==> Cleaning artifacts..."
	rm -rf dist packages/py/dist packages/ts/dist .pytest_cache packages/py/.pytest_cache
