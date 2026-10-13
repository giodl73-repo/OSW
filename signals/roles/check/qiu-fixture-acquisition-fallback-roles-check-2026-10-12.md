---
skill: roles-check
topic: qiu-fixture-acquisition-fallback
date: 2026-10-12
roles_used: [sounder, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Acquisition fallback review

Artifact: fixture allowlist, regression tests, source verification receipt.
Selected SOUNDER for identity/provenance, KEEL for acquisition integrity and
reproducibility, LOGBOOK for publication claims. Scientific measurement,
cartography and interface code are unchanged; their roles are outside this scope.
This is an internal role-lens review, not independent scientific verification.

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Alias fetched bytes match the existing original pin. | P3 | Verification receipt | Retain the original manifest; satisfied. |
| 2 | Alias shares the same institution/service. | P3 | Receipt limitations | Avoid claiming independent archival redundancy; documented. |
| 3 | Actual response size and page count were checked. | P3 | Receipt identity | Preserve both requested and resolved addresses; recorded. |
| 4 | Controlled primary failure differs from an observed outage. | P3 | Live exercise | Label the controlled failure explicitly; satisfied. |
| 5 | Publisher and CiteSeer candidates provided no verified bytes. | P3 | Excluded candidates | Keep them out of the allowlist; satisfied. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Timeout retries precede fallback. | P3 | Regression tests | Assert request order and delays; satisfied. |
| 2 | Changing pin or original URL disables this alias. | P3 | Regression tests | Exercise both identity changes; satisfied. |
| 3 | Wrong alias bytes fail before staging. | P3 | Regression tests | Check absent destination and temporary files; satisfied. |
| 4 | Local cached originals do not prove remote acquisition. | P3 | Batch checks | Describe the 25 checks as offline verification; satisfied. |
| 5 | Hosted availability remains unproven. | P3 | Hosted gate | Observe fresh hosted run; retain pending/failed status until evidence. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---------|----------|---------|----------------|
| 1 | Parent run stopped before software gates. | P3 | Batch evidence | Record exact failed run and skipped gates; satisfied. |
| 2 | Narrow suite differs from parent full suite. | P3 | Checks | Label both scopes; satisfied. |
| 3 | Source originals must remain outside Git. | P3 | Publication | Stage only code, tests and metadata; verify staged paths. |
| 4 | This change closes no scientific measurement gap. | P3 | Remaining gaps | Preserve existing coverage counts; satisfied. |
| 5 | Publication is a stacked draft, not mainline admission. | P3 | Publication | Record draft/base and hosted handles after push. |

## Synthesis and amendments

Roles reviewed: 3. P1 blockers: 0; P2 issues: 0; P3 notes: 15.
Verdict: APPROVED-WITH-CONDITIONS for the narrow acquisition change.
Top finding: local alias success does not establish hosted availability.
KEEL and LOGBOOK agree that cache checks and skipped gates must remain explicit.

1. Preserve exact source identity and excluded-candidate evidence: implemented.
2. Cover timeout order, identity refusal and corrupt-download staging: implemented.
3. Publish as a stacked draft and record hosted outcomes without claiming
   success before observation: publication follow-up required.
