---
skill: roles-check
topic: ocean-motion-horizon-alternative-source
date: 2026-09-30
roles_used: 5
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: alternatives to the Horizon named-eddy register

Artifact: `plans/ocean-motion-horizon-alternative-source-audit.md` and the
Horizon reuse decision packet. Type: scientific source and publication-rights
assessment. Quick review selected CURRENT (eddy identity), SOUNDER (source
provenance), BEACON (reader interpretation), KEEL (reproducibility), and
LOGBOOK (public boundary).

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| C1 | A station interval associated with a named frontal feature does not establish that eddy's separation date, lifetime, or footprint. | P2 | BOEM row | Keep interval, event date, and footprint as different claim types. |
| C2 | Paper-specific Kraken, Thor, and Ursa observation windows corroborate selected events, not the whole 96-record name register. | P3 | Decision | Preserve source-set counts and avoid global completeness wording. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| S1 | NOAA attributes U.S. eddy naming to Horizon; the BOEM study uses Woods Hole Group frontal analyses. These are not fully independent replacement name sources. | P2 | Source table | Keep observation corroboration separate from naming authority. |
| S2 | The BOEM copy has a 2025-008 cover identifier but a differently numbered URL in its availability paragraph. | P2 | Source citation | Cite the exact govinfo copy and cover identifier, and reconcile later with the publisher. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| B1 | “Alternative source” can imply that a complete replacement was found. | P2 | Title and decision | State the negative result immediately and keep the 96 excluded count visible. |
| B2 | “Independent published observations” could be read as independently assigned names. | P2 | Three-event row | Say independent observations of named events, not independent naming. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| K1 | The audit is a dated manual source check; no parser proves that all 96 Horizon rows are covered by alternatives. | P2 | Method | Do not convert this audit to a rights-cleared coverage count. |
| K2 | The existing screened bundle excludes Horizon rows and passes its boundary validator. | P3 | Release handling | Keep this gate until a field-specific provider decision or new source graph is validated. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| L1 | The full Horizon compilation still has no recorded redistribution decision for the website, repository, and DOI archive. | P1 | Publication gate | Obtain scoped written terms or continue excluding the 96 rows. |
| L2 | The provider inquiry remains an unsent draft, as stated in both packets. | P3 | Status | Preserve that status and record any future response before changing rights flags. |

## Synthesis

Roles reviewed: 5  
P1 blockers: 1 | P2 issues: 6 | P3 notes: 3  
Verdict: **NEEDS-WORK** for restoring the full Horizon-derived register.

Top finding: individual government and research mentions cannot replace the
complete provider compilation or settle its reuse terms. CURRENT and SOUNDER
agree that named-feature mentions and observed station intervals cannot be
promoted into full eddy identities, dates, or footprints.

Three amendments:

1. Keep the 96 Horizon rows excluded from the screened atlas until exact reuse
   terms or a separately modeled source set is available.
2. Retain the BOEM identifier discrepancy and naming-authority caveat in the
   source audit; cite the exact copy used.
3. If building a paper-supported subset, mint and review its provenance and
   identity links instead of silently relabeling Horizon records.
