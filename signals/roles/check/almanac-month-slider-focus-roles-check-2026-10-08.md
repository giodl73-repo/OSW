---
skill: roles-check
topic: almanac-month-slider-focus
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Monthly chart keyboard/publication review

Internal seven-role review of the focused input, asynchronous request lifecycle,
regression and accumulated source-data publication. Not independent scientific
review. Role selection: CURRENT for temporal meanings, SOUNDER for provenance,
CHART for selected-month rendering, BEACON for source explanation, HARBOR for
keyboard access, KEEL for CI reproducibility, LOGBOOK for publication accuracy.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Branching latitude is not length or width. | P2 | Chart/source scope | Existing metric limits unchanged; no dimension promoted. |
| 2 | Historical cycles are not current observations. | P2 | Source period | Period and nongeographic playback labels retained. |
| 3 | Wider annual dimension gaps remain. | P3 | Goal | Preserve unassessed and unknown values after consolidation. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Late source replies can mislabel selected month. | P2 | Request serial | Existing serial guard retained; held-reply regression added. |
| 2 | Source variability and reading allowances differ. | P2 | Native/WASM chart | Complete existing parity and envelope checks retained. |
| 3 | Original author fixtures depend on remote availability. | P3 | CI acquisition | Retain exact hashes and restricted-source boundary; no cache introduced. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Selected month must agree with chart and table. | P2 | Paint/view | Existing shared view remains; old reply cannot repaint. |
| 2 | New requests must not turn source curves into physical maps. | P2 | Evidence scope | Existing geographic ineligibility retained. |
| 3 | Narrow controls must remain usable. | P3 | Reflow | Retain 320 px and 44 px control assertions. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Loading state must remain visible while input is usable. | P2 | Status | Pending marker retained and checked. |
| 2 | A fixed browser failure does not establish main publication. | P2 | Plan/PR | Explicitly separate local result from protected-main checks. |
| 3 | New data counts are scoped evidence counts. | P3 | Consolidation | Keep editorial/nonuniform caveats in main PR. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Disabling focused slider loses keyboard continuity. | P2 | Controls | Keep ready slider enabled during refresh. |
| 2 | Test must use real keys across a pending request. | P2 | Regression | Home and ArrowRight retained; pending focus/value explicitly checked. |
| 3 | Real source failure needs disabled controls. | P3 | Error lifecycle | Existing unavailable-source assertions retained. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Failure was terminal and reproducible in control logic. | P2 | CI evidence | Correct control logic; no restarts or timeout inflation. |
| 2 | Final protected-main gate must run accumulated data. | P2 | Publication | Open: advance verified ancestor without force and await CI. |
| 3 | Scientific suite predates JS focus fix. | P3 | Local receipt | State exact verification scopes and affected browser result. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier dependent batches were outside PR30. | P2 | Ancestry | Include Agulhas and Norwegian commits in protected-main head. |
| 2 | Main PR counts and blockers are stale. | P2 | PR description | Refresh counts, local receipts and specific CI failure. |
| 3 | Draft batch PRs preserve review history. | P3 | Repository | Retain references; attach existing publication PR. |

## Synthesis

Seven roles, 21 findings: zero P1, fourteen P2 (thirteen addressed by code,
regression and proposed consolidation; exact-head CI remains open), seven P3.
APPROVED-WITH-CONDITIONS for publication review. Top finding: disabling a
focused input during asynchronous refresh prevents continuous keyboard use.
HARBOR, CHART and SOUNDER agree that active selection and final returned view
must remain coherent. KEEL and LOGBOOK require verified protected-main CI.

Amendments:

1. Keep the ready slider focused and enabled during loading.
2. Hold/release an older request around actual arrow-key input and verify no
   stale repaint, alongside all existing source and outage checks.
3. Consolidate reviewed data and update publication receipts without claiming
   main landing before the protected checks finish.
