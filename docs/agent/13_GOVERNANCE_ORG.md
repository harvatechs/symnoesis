# Governance and Organization

Symnoesis is an initiative by HarVa Groups, intended to operate as a not-for-profit, research-based, open project. This file specifies the governance documents the repo must contain and the rules for writing them. **The agent drafts structure and policy language; it never invents people, bodies that do not exist, legal status, funding, or endorsements.** Counsel reviews privacy, consent, trademark, safe-harbor, and any legal-status text before publication. This pack is not legal advice.

## 1. Writing rule for every governance document

Describe bodies and processes as **how the project will operate**, with a status line at the top: `Status: Proposed | In effect (adopted YYYY-MM-DD)`. A body is "in effect" only when `ORG_FACTS.yaml` lists its verified, consenting members. Until then the document says "Proposed" and lists roles to be filled, with no names.

## 2. Bodies (proposed)

| Body | Purpose | Composition rule | Decides |
| --- | --- | --- | --- |
| **Maintainers** | Day-to-day stewardship of the repo | ≥ 2 named maintainers; no organization holds more than half | Merges, releases, ADRs |
| **Scientific Advisory Board (SAB)** | Owns constructs, thresholds, weights, CHI list | Psychology, HCI, AI safety, measurement science, clinical expertise; ≥ 5 members; term limits | Spec changes via RFC |
| **Ethics Review Board** | Reviews all human-subject protocols; special protections | Includes ≥ 1 clinician, ≥ 1 ethicist, ≥ 1 independent lay member; independent of funders | Protocol approval; stopping rules; disclosure disputes |
| **Steering Council** | Strategy, funding transparency, conflict-of-interest, standards path | Balanced across AI labs, academia, civil society, clinicians, educators, regulators; no single funder or vendor holds a majority | Charter, budget, partnerships, certification scheme |
| **Independent auditors** | Verify Index and certification runs | Rotating; no conflict with evaluated systems | Audit reports |

Before these bodies exist, the founding group (named in `ORG_FACTS.yaml`) acts as interim maintainers and the repo states this plainly.

## 3. Required documents and contents

| File | Must contain |
| --- | --- |
| `GOVERNANCE.md` | Bodies, membership rules, term limits, decision procedures (lazy consensus, then vote with quorum and thresholds), how the RFC process works, how to amend governance, how to remove a member |
| `docs/governance/charter.md` | Mission; principles (SYMN-01 principles); scope; what the project will never do (pay-to-rank, hidden funding, proprietary scoring); dissolution clause: assets and IP remain open under their licenses |
| `docs/governance/ethics.md` | Human-subject principles (Belmont-style respect, beneficence, justice); approval requirement before any data collection; vulnerable-user protections; no minors in v1 cohorts; participant safety net; stopping rules; compensation; debriefing; data minimization |
| `docs/governance/disclosure.md` | Responsible disclosure of critical safety findings: developer notice, 45-day window by default, extension rules, publication, right of reply, handling of active-harm exceptions |
| `docs/governance/coi.md` | Declaration form; recusal rules; labs may submit systems but cannot alter scoring; funder separation; auditor rotation |
| `docs/governance/funding.md` | Transparency: funders, amounts bands, restrictions; policy that funders cannot influence results or ranks; "none" stated explicitly if true |
| `docs/governance/data-policy.md` | Data classes (public artifacts, derived features, private holdout, personal data); retention; access control; k-anonymity and differential privacy rules; deletion; cross-border handling; incident response |
| `docs/governance/privacy.md` | Website and portal privacy (no cookies, no analytics, local computation) and, separately, research-data privacy; applicable regimes listed for counsel review (for example GDPR, India's DPDP Act 2023, and local human-subjects rules) |
| `docs/governance/zones.md` | The seven governance zones, required actions, and the crosswalk table to NIST AI RMF functions, ISO/IEC 42001 controls, EU AI Act risk categories (each mapping cites the exact clause after verification; unverified mappings are not published) |
| `docs/governance/certification.md` | **Draft only.** Eligibility (Z1, E3, `n_eff ≥ n_cert`), independent audit, renewal, revocation, appeals. States clearly that no certification exists at v0.1 |
| `docs/governance/standards-path.md` | Plan to publish the open spec, solicit review, and submit to a standards body (ISO/IEC JTC 1/SC 42, IEEE, or a NIST-led consortium) with status honestly "not submitted" until true |
| `TRADEMARK.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` | As in `12_REPO_BLUEPRINT.md` |

## 4. Institutionalization path (for the roadmap page)

1. **Now:** founding group acts as interim maintainers; spec and code open under permissive licenses.
2. **Before any human cohort:** Ethics Review Board constituted or an existing accredited ethics committee engaged.
3. **Before the public beta:** Steering Council and SAB seated; conflict-of-interest declarations published; funding disclosure live.
4. **Fiscal home:** evaluate options (an academic host, a fiscal sponsor, or an independent foundation) against criteria: independence, ability to hold funds for research, legal protection for contributors, transparency requirements, jurisdiction, cost, exit terms. Record the comparison in an ADR. Do not name a chosen entity until a real decision is made.
5. **Before certification:** independent audit bodies and an appeals process exist.

## 5. Open-source hygiene

- Licenses: Apache-2.0 (code), CC BY 4.0 (spec, docs, site content), CC BY 4.0 for public data after privacy review. SPDX headers; REUSE compliance. Third-party notices generated at release.
- Contributor terms: Developer Certificate of Origin sign-off (`Signed-off-by`) rather than a CLA unless counsel advises otherwise.
- Security: private vulnerability reporting enabled; response targets published.
- Transparency: ADRs, RFCs, build logs, research logs, and corrections are public.

## 6. What the agent must flag for human decision

Legal form and jurisdiction; names for bodies and members; contact addresses; funding; license final choice; trademark filing; whether to submit to a standards body and when; who signs releases; anything involving real participants.
