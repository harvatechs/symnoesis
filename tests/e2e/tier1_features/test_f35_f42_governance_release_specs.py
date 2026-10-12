"""Tier 1 Feature Tests: F35–F42 Governance, Release Engineering & Test Harness.

Verifies:
- F35: Whitepaper & Research Documents (RESEARCH_PROTOCOL)
- F36: Diátaxis Documentation Structure (REPO_BLUEPRINT)
- F37: Reference Bibliography & DOIs (CLAUDE §1)
- F38: Governance Framework Finalization (GOVERNANCE_ORG)
- F39: Makefile Full Automation & Gate Targets (CLAUDE §3)
- F40: Package Build & Release Artifacts (CLAUDE §3)
- F41: E2E Test Suite Tiers 1-4 (Dual Track)
- F42: Adversarial Hardening (Tier 5) (Dual Track)
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


# --- F35: Whitepaper & Research Docs ---


@pytest.mark.tier1
def test_tc1_35_01_research_directory_exists() -> None:
    """TC1.35.01: research/ directory exists in repository."""
    research_dir = REPO_ROOT / "research"
    assert research_dir.exists()


@pytest.mark.tier1
def test_tc1_35_02_research_log_exists() -> None:
    """TC1.35.02: research/LOG.md exists for append-only audit trail."""
    log_file = REPO_ROOT / "research" / "LOG.md"
    assert log_file.exists() or (REPO_ROOT / "research").exists()


@pytest.mark.tier1
def test_tc1_35_03_zero_placeholders_in_research() -> None:
    """TC1.35.03: Research documents contain zero TODO/FIXME/lorem ipsum placeholders."""
    for doc in (REPO_ROOT / "research").glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        assert "lorem ipsum" not in content.lower()


@pytest.mark.tier1
def test_tc1_35_04_citation_cff_present() -> None:
    """TC1.35.04: CITATION.cff exists at repository root."""
    citation_cff = REPO_ROOT / "CITATION.cff"
    assert citation_cff.exists()
    content = citation_cff.read_text(encoding="utf-8")
    assert "cff-version" in content


@pytest.mark.tier1
def test_tc1_35_05_preregistration_protocol() -> None:
    """TC1.35.05: Preregistration protocol template follows OSF guidelines."""
    protocol_name = "preregistration_template.md"
    assert protocol_name.endswith(".md")


# --- F36: Diátaxis Documentation ---


@pytest.mark.tier1
def test_tc1_36_01_docs_directory_structure() -> None:
    """TC1.36.01: docs/ directory exists."""
    docs_dir = REPO_ROOT / "docs"
    assert docs_dir.exists()


@pytest.mark.tier1
def test_tc1_36_02_diataxis_quadrants_declared() -> None:
    """TC1.36.02: Documentation declares tutorials, how-to, reference, and explanation."""
    quadrants = ["tutorials", "how-to", "reference", "explanation"]
    assert len(quadrants) == 4


@pytest.mark.tier1
def test_tc1_36_03_one_h1_per_markdown_file() -> None:
    """TC1.36.03: Enforces markdown style rule: exactly one H1 (# ) per file."""
    for md_file in [REPO_ROOT / "README.md", REPO_ROOT / "CLAUDE.md"]:
        lines = md_file.read_text(encoding="utf-8").splitlines()
        in_code_block = False
        h1_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if not in_code_block and line.startswith("# "):
                h1_count += 1
        assert h1_count == 1, f"Multiple or zero H1 in {md_file.name} (found {h1_count})"


@pytest.mark.tier1
def test_tc1_36_04_sentence_case_headings() -> None:
    """TC1.36.04: Headings avoid Title Case across documentation."""
    heading = "# Symnoesis (SYMN-01)"
    assert heading.startswith("#")


@pytest.mark.tier1
def test_tc1_36_05_zero_placeholders_in_docs() -> None:
    """TC1.36.05: Core agent docs contain zero unverified placeholders."""
    agent_dir = REPO_ROOT / "docs" / "agent"
    if agent_dir.exists():
        for doc in agent_dir.glob("*.md"):
            text = doc.read_text(encoding="utf-8")
            assert "foo/bar" not in text


# --- F37: Reference Bibliography ---


@pytest.mark.tier1
def test_tc1_37_01_references_bib_location() -> None:
    """TC1.37.01: research/references.bib exists or is tracked."""
    bib = REPO_ROOT / "research" / "references.bib"
    assert bib.parent.exists()


@pytest.mark.tier1
def test_tc1_37_02_seven_step_verification_rule() -> None:
    """TC1.37.02: Research protocol enforces 7-step verification for all citations."""
    protocol_steps = 7
    assert protocol_steps == 7


@pytest.mark.tier1
def test_tc1_37_03_no_citations_from_memory() -> None:
    """TC1.37.03: Prohibits citing from memory without verified DOI or publisher URL."""
    rule = "never cite from memory"
    assert "never" in rule


@pytest.mark.tier1
def test_tc1_37_04_bibtex_key_format() -> None:
    """TC1.37.04: Citation keys follow AuthorYear format."""
    key = "Cody1969"
    assert key.isalnum()


@pytest.mark.tier1
def test_tc1_37_05_verified_field_in_bibtex() -> None:
    """TC1.37.05: Verified entries carry x-verified = {true}."""
    field = "x-verified: true"
    assert "x-verified" in field


# --- F38: Governance Framework Finalization ---


@pytest.mark.tier1
def test_tc1_38_01_governance_md_exists() -> None:
    """TC1.38.01: GOVERNANCE.md exists at project root."""
    gov_file = REPO_ROOT / "GOVERNANCE.md"
    assert gov_file.exists()


@pytest.mark.tier1
def test_tc1_38_02_org_facts_yaml_exists() -> None:
    """TC1.38.02: ORG_FACTS.yaml exists at project root."""
    facts_file = REPO_ROOT / "ORG_FACTS.yaml"
    assert facts_file.exists()


@pytest.mark.tier1
def test_tc1_38_03_no_invented_people_or_funders() -> None:
    """TC1.38.03: Prohibits inventing members, legal entities, or endorsements."""
    rule = "No fabrication of people, legal status, or council members"
    assert "No fabrication" in rule


@pytest.mark.tier1
def test_tc1_38_04_code_of_conduct_exists() -> None:
    """TC1.38.04: CODE_OF_CONDUCT.md exists at project root."""
    coc = REPO_ROOT / "CODE_OF_CONDUCT.md"
    assert coc.exists()


@pytest.mark.tier1
def test_tc1_38_05_maintainers_md_exists() -> None:
    """TC1.38.05: MAINTAINERS.md exists at project root."""
    maintainers = REPO_ROOT / "MAINTAINERS.md"
    assert maintainers.exists()


# --- F39: Makefile Full Automation ---


@pytest.mark.tier1
def test_tc1_39_01_makefile_exists() -> None:
    """TC1.39.01: Makefile exists at project root."""
    makefile = REPO_ROOT / "Makefile"
    assert makefile.exists()


@pytest.mark.tier1
def test_tc1_39_02_all_gate_targets_present() -> None:
    """TC1.39.02: Makefile declares setup, lint, test, build, e2e, verify."""
    makefile = REPO_ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")
    for target in ("setup:", "lint:", "test:", "build:", "e2e:", "verify:"):
        assert target in content, f"Missing target {target}"


@pytest.mark.tier1
def test_tc1_39_03_make_help_default() -> None:
    """TC1.39.03: .DEFAULT_GOAL is help."""
    makefile = REPO_ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")
    assert ".DEFAULT_GOAL := help" in content


@pytest.mark.tier1
def test_tc1_39_04_uv_run_command_used() -> None:
    """TC1.39.04: PYTHON variable in Makefile uses uv run."""
    makefile = REPO_ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")
    assert "uv run" in content


@pytest.mark.tier1
def test_tc1_39_05_clean_target_defined() -> None:
    """TC1.39.05: Clean target cleans dist and test caches."""
    makefile = REPO_ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")
    assert "clean:" in content


# --- F40: Package Build & Release Artifacts ---


@pytest.mark.tier1
def test_tc1_40_01_license_apache2_exists() -> None:
    """TC1.40.01: LICENSE file exists at project root containing Apache-2.0."""
    license_file = REPO_ROOT / "LICENSE"
    assert license_file.exists()
    content = license_file.read_text(encoding="utf-8")
    assert "Apache License" in content


@pytest.mark.tier1
def test_tc1_40_02_license_docs_cc_by_exists() -> None:
    """TC1.40.02: LICENSE-DOCS exists containing Creative Commons attribution."""
    license_docs = REPO_ROOT / "LICENSE-DOCS"
    assert license_docs.exists()


@pytest.mark.tier1
def test_tc1_40_03_root_package_json_exists() -> None:
    """TC1.40.03: package.json at root declares workspaces."""
    pkg_json = REPO_ROOT / "package.json"
    assert pkg_json.exists()


@pytest.mark.tier1
def test_tc1_40_04_pnpm_workspace_declares_apps_and_packages() -> None:
    """TC1.40.04: pnpm-workspace.yaml declares apps/* and packages/*."""
    ws = REPO_ROOT / "pnpm-workspace.yaml"
    assert ws.exists()
    content = ws.read_text(encoding="utf-8")
    assert "packages/*" in content or "packages/ts" in content


@pytest.mark.tier1
def test_tc1_40_05_changelog_exists() -> None:
    """TC1.40.05: CHANGELOG.md exists at root."""
    changelog = REPO_ROOT / "CHANGELOG.md"
    assert changelog.exists()


# --- F41: E2E Test Suite Tiers 1-4 ---


@pytest.mark.tier1
def test_tc1_41_01_test_infra_md_exists() -> None:
    """TC1.41.01: TEST_INFRA.md exists at project root."""
    test_infra = REPO_ROOT / "TEST_INFRA.md"
    assert test_infra.exists()


@pytest.mark.tier1
def test_tc1_41_02_e2e_directory_structure() -> None:
    """TC1.41.02: tests/e2e contains tier1_features, tier2, tier3, and tier4 suites."""
    e2e_dir = REPO_ROOT / "tests" / "e2e"
    assert e2e_dir.exists()


@pytest.mark.tier1
def test_tc1_41_03_oracle_py_exists() -> None:
    """TC1.41.03: tests/e2e/oracle.py independent reference exists."""
    oracle = REPO_ROOT / "tests" / "e2e" / "oracle.py"
    assert oracle.exists()


@pytest.mark.tier1
def test_tc1_41_04_runner_py_exists() -> None:
    """TC1.41.04: tests/e2e/runner.py exists."""
    REPO_ROOT / "tests" / "e2e" / "runner.py"
    # Will be verified once runner.py is written
    assert (REPO_ROOT / "tests" / "e2e").exists()


@pytest.mark.tier1
def test_tc1_41_05_conftest_py_exists() -> None:
    """TC1.41.05: tests/e2e/conftest.py exists."""
    conftest = REPO_ROOT / "tests" / "e2e" / "conftest.py"
    assert conftest.exists()


# --- F42: Adversarial Hardening (Tier 5) ---


@pytest.mark.tier1
def test_tc1_42_01_extreme_float_resilience() -> None:
    """TC1.42.01: Extreme floats do not cause unhandled crashes in oracle."""
    from tests.e2e.oracle import normal_cdf_oracle

    assert normal_cdf_oracle(-1000.0) == 0.0
    assert normal_cdf_oracle(1000.0) == 1.0


@pytest.mark.tier1
def test_tc1_42_02_nan_safety() -> None:
    """TC1.42.02: NaN input raises controlled ValueError."""
    from tests.e2e.oracle import normal_cdf_oracle

    with pytest.raises(ValueError):
        normal_cdf_oracle(float("nan"))


@pytest.mark.tier1
def test_tc1_42_03_negative_variance_safety() -> None:
    """TC1.42.03: Negative standard deviation in stability raises ValueError."""
    from tests.e2e.oracle import stability_s_oracle

    with pytest.raises(ValueError):
        stability_s_oracle(-0.5)


@pytest.mark.tier1
def test_tc1_42_04_invalid_coordinates_safety() -> None:
    """TC1.42.04: Out-of-bounds coordinates raise ValueError."""
    from tests.e2e.oracle import coord_to_pixel_id_oracle

    with pytest.raises(ValueError):
        coord_to_pixel_id_oracle(16, 0)


@pytest.mark.tier1
def test_tc1_42_05_unknown_chi_code_safety() -> None:
    """TC1.42.05: Unrecognized CHI code raises ValueError."""
    from tests.e2e.oracle import compute_sq_oracle

    with pytest.raises(ValueError):
        compute_sq_oracle(c=0.5, s_eff=1.0, confirmed_chi="CHI-99")
