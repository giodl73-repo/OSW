---
skill: roles-check
topic: rust-route-evidence-queries
date: 2026-10-04
source_commit: 7f114b94e546e972a25151d8bd2b62f06aee5393
working_branch: codex/route-evidence-queries
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Route evidence query review

Artifacts: complete remaining-length worklist import, Rust source/owner
validation, query controls and current-card joins, Pacific SECC source preview
audit, regenerated catalog/dashboard/bundle/WASM, documentation and browser
checks. This is an internal functional review, not scientific peer review.

Roles: CURRENT for measurement support; SOUNDER for source access and receipts;
CHART for envelope/axis and dateline distinctions; BEACON for next-action/source
navigation; HARBOR for equivalent access; KEEL for loader and parity checks;
LOGBOOK for scope, versioned artifacts and release claims. ORBIT is excluded:
no planetary comparison is introduced.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Source envelopes cannot establish a current axis. | P3, verified | New audit retains null axis and length. Recover longitudinal velocity support before route calculation. |
| 2 | CURRENT | Latitude limits do not establish paired velocity edges. | P3, verified | Spring 5–13 S remains an envelope; widths and annual ranges are null. Require compatible edge/layer evidence. |
| 3 | CURRENT | Family/system scope must remain distinct. | P3, verified | Eight family decisions keep their construction strategy; no route sum or member inheritance. Resolve member identities first. |
| 4 | SOUNDER | Full-method access was unavailable. | P2, resolved | Audit and inspector explicitly say preview inspected, full methods/figures not acquired. Keep exact access level visible. |
| 5 | SOUNDER | Source season names alone cannot supply month membership. | P3, verified | Phase calendars and averaging period remain null. Read source methods before assigning month filters. |
| 6 | SOUNDER | Queries need original source and receipt. | P3, verified | Decisions retain source payload/catalog hash and complete scope audits; direct catalog/source/audit links supplied. Preserve receipts on updates. |
| 7 | CHART | Wrapped longitudes could be misread as nearly global extent. | P3, verified | Source spans calculate eastward modulo 360: 40 and 70 degrees. Retain seam convention beside limits. |
| 8 | CHART | An envelope rectangle could imply an occupied footprint. | P3, verified | Audit supplies no footprint; worklist introduces no map geometry. Require geographic support before an overlay. |
| 9 | CHART | Existing route/state relations must survive metadata updates. | P3, verified | Join diff changes catalog hash only; 124 candidate/state pairs remain. Preserve original geometry and relation class. |
| 10 | BEACON | Unresolved currents needed an actionable query path. | P2, resolved | All 89 decisions are selectable; cards expose next evidence needed, candidate counts and strategies. Keep evidence requests specific. |
| 11 | BEACON | A construction decision is not an approved classification. | P3, verified | Inspector and contract retain editorial status and scientific review gates. Keep this distinction beside strategies. |
| 12 | BEACON | Original audit files need direct navigation. | P3, verified | Source-review details contain evidence-source/audit links; catalog receipt link added. Keep source context close to claims. |
| 13 | HARBOR | Changing sort could drop an active worklist filter. | P2, resolved | Visible current/strategy/status controls preserve filters; additional and duplicate predicates are retained and disclosed. Test form resubmission. |
| 14 | HARBOR | Selection must work without a pointer. | P3, verified | Native table buttons and labelled selects; Enter opens the original decision card. Keep focus styles and semantic controls. |
| 15 | HARBOR | Evidence must reflow on small screens. | P3, verified | 320 px browser check passes without page overflow; expandable text audits are available independently of maps. Retain text alternatives. |
| 16 | KEEL | Import could omit a remaining current. | P3, verified | Exact 89-current source membership and native complete-owner validation; missing-decision mutation rejected. Keep coverage checks on regeneration. |
| 17 | KEEL | Candidate counts/ownership could drift. | P3, verified | All 62 IDs match imported routes and owner joins; coverage and cross-owner mutations rejected. Validate links rather than count presence alone. |
| 18 | KEEL | Native and WASM could execute different worklists. | P3, verified | Full query parity for all, unbuilt and family selections; 20 Rust tests and stock browser regression pass. Keep executable parity evidence. |
| 19 | LOGBOOK | Local implementation must not be reported as published. | P3, verified | Work remains on codex/route-evidence-queries; no commit/push/merge in this slice. Keep delivery status explicit. |
| 20 | LOGBOOK | Canonical release and measurement counts could change accidentally. | P3, verified | Canonical release diff empty; 11 ranked lengths, 62 candidates and 30 unbuilt remain. Require separate admission review. |
| 21 | LOGBOOK | Generated records must identify current inputs/code. | P3, verified | Engine/bundle source and generator SHA checks pass; planning.rs pinned in manifest. Rebuild explicitly when source artifacts change. |

Amendments applied: (1) preserve preview-only access and unknown calendars/axes;
(2) import the complete 89-name worklist with source audits and direct card links;
(3) add visible planning selectors and preserve additional structured predicates.

Verification: 20 Rust tests; 34 focused Python checks and 57 subtests; complete
worklist browser/native/WASM checks including seven loader rejections, form
sorting and additional-filter retention; stock query and width-sample browser
regressions; JavaScript syntax, SHA manifests and whitespace checks. Screenshot
inspected. Full default CI has not been run for this local slice. Conditions:
independent source/method/scientific admission and broader inventory coverage
remain open; these query decisions assign no new current dimensions.
