# Open Questions and Founder Inquiries

Every open question or decision that cannot be autonomously resolved by the specification is tracked here.

| ID | Topic | Question | Options & Recommendation | Status | Resolution / Decision |
|---|---|---|---|---|---|
| **OQ-001** | GitHub & Domain | What is the production repository URL and custom domain? | Default to `https://github.com/harvagroups/symnoesis` and GitHub Pages until confirmed. | Open | Awaiting founder input |
| **OQ-002** | Legal Status | What is the legal registration status and jurisdiction of HarVa Groups? | Default to unincorporated research initiative in `ORG_FACTS.yaml` with `verified: false`. | Open | Awaiting founder input |
| **OQ-003** | Named Personnel | Who are the named maintainers and scientific advisors consenting to be listed? | Default to empty roster in `ORG_FACTS.yaml` (`people: []`). | Open | Awaiting founder input |
| **OQ-004** | Contact Endpoints | What are the verified email endpoints for general, security, and ethics communications? | Default to `null` in `ORG_FACTS.yaml` (`verified: false`). | Open | Awaiting founder input |
| **OQ-005** | Funding Disclosures | Are there active institutional grants, funding lines, or sponsor credits? | Default to `null` (unverified) until explicitly confirmed. | Open | Awaiting founder input |
| **OQ-006** | Windows Make Toolchain | How should the gate runner execute on Windows developer machines without native Make? | Install GNU Make via Winget (`ezwinports.make`) and provide cross-platform runner fallback. | **Resolved** | GNU Make 4.4.1 installed and operational via `WinGet/Links`. |
