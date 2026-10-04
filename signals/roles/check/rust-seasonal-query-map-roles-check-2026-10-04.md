---
skill: roles-check
topic: rust-seasonal-query-map
date: 2026-10-04
source_commit: 913a8457dde0338f2807606d7a220fff85ae783d
working_branch: codex/seasonal-query-map
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Rust seasonal query map review

Artifact: Rust/Python query implementation, generated bundle/WASM and browser UI.
This is an internal review of the working-tree changes from the source commit above,
not external scientific peer review or approval of canonical source admission.

Seven installed roles apply to seasonal geography, provenance, map presentation,
navigation and reproducibility. ORBIT is excluded because no planetary comparison
is introduced. Findings below include confirmed strengths and resolved defects.

## CURRENT — layer, time support and defensible scope

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Six regional phases do not establish whole-current annual extrema. | P3, verified | Imported comparability decisions preserve false eligibility and null length/width ranges; source validator and Rust load reject promotion. | Preserve these exclusions until comparable source axes and edges exist. |
| 2 | Month conventions must remain separate from observation dates. | P2, resolved | Rust rejects combined `seasonal`/`geometry_time`; seasonal features cannot carry observation dates; UI switches selection modes explicitly. | Keep exact-day and source-phase selectors distinct. |
| 3 | A historical Davidson width cannot become a route buffer. | P3, verified | Original width-support role/scope are retained in phase record; renderer receives only line coordinates. | Require paired-edge evidence before rendering occupied widths. |

## SOUNDER — exact provenance and missing support

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 4 | Seasonal inventory pinned an older width inventory. | P2, resolved | Revalidated all six associations, including the same Davidson record, against current width inventory; refreshed its SHA-256 receipt. Candidate hashes remain exact. | Run the seasonal receipt validator after every width inventory refresh. |
| 5 | Somali winter has no explicit supported month range. | P3, verified | Null calendar remains selectable by phase ID and excluded from all month queries. | Add months only from an explicit source convention. |
| 6 | Regional drawings retain transformed/source identities. | P3, verified | Phase records and map/spatial features carry URLs, locators, candidate/inventory hashes and source roles; source vertices compare exactly. | Keep source geometry separate from densified spatial/display geometry. |

## CHART — geographic and visual interpretation

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 7 | New source role was initially styled as dated evidence. | P2, resolved | Browser CSS and native SVG now recognize `osw_editorial_reference_route` as a solid editorial line. | Continue matching legend meaning to semantic role rather than geometry type alone. |
| 8 | Month/state queries must use the same phase feature. | P3, verified | Rust filters spatial relation indexes through seasonal selection; native/WASM tests compare three states and January/July against original feature indexes. | Never let another route of the same object supply the selected phase's intersection. |
| 9 | Local maps still use coarse OSW coastline context. | P3, verified | Reviewed Sri Lanka screenshot; Fit matches and direct phase links use regional framing; legend states display-only coastline. | Retain the explicit coarse-map limitation for local scale interpretation. |

## BEACON — readable claims and evidence access

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 10 | A blank month can be mistaken for zero flow. | P3, verified | April/May return empty scenes; adjacent UI prose says coverage unavailable, with no substituted geometry. | Keep gap meaning beside playback and selectors. |
| 11 | The recorded-day playback caption was misleading in month mode. | P2, resolved | Caption now distinguishes observation steps from source-month steps and states no interpolation. | Maintain separate explanations if a future observed monthly-field mode is added. |
| 12 | Phase labels and direct links should explain the current's evidence. | P3, verified | Friendly source-phase labels replace raw IDs in primary map caption; current card links map each phase and preserves full source notes. | Keep machine IDs in structured records, with readable labels in navigation. |

## HARBOR — keyboard, reflow and motion

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 13 | Relevant phase links were hidden behind a collapsed card section. | P2, resolved | Seasonal selection opens the current's seasonal evidence group; keyboard mark selection reaches both Somali phase links. | Continue exposing evidence for the active selection. |
| 14 | Color alone cannot communicate seasonal direction/scope. | P3, verified | Focus/hover text includes phase label and flow direction; card provides months, sources and comparability prose; result JSON remains downloadable. | Retain these textual alternatives if directional visual marks are added. |
| 15 | Playback must be optional and pausable. | P3, verified | Manual Play/Pause controls with pressed state; generation guard stops on pause, other queries, failure, hidden page and December; 320 px reflow tested. | Preserve manual initiation and stopping rules. |

## KEEL — reproducible query and artifact checks

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 16 | A source phase can be corrupted independently of its map mark. | P3, verified | Rust binding tests reject ownership, geometry type, source URL, calendar and date tampering; importer validates source bytes before joining. | Require tests for any new joined metadata. |
| 17 | Native and WASM must select identical phases and gaps. | P3, verified | Browser test covers all 12 months, six named phases, malformed selectors, state joins, pagination-independent scenes and SVG byte parity. | Run the documented standalone browser check after engine changes. |
| 18 | Shared playback changes could break exact-day maps. | P3, verified | Existing 17-frame regression passes with retained stopped traces, receipts, exact dates, playback/pause and mobile layout. | Keep the recorded-day regression beside the source-month check. |

## LOGBOOK — truthful operational status

| # | Finding | Severity/status | Evidence | Recommendation |
|---|---|---|---|---|
| 19 | Four covered currents are a partial seasonal inventory. | P3, verified | Six records across four IDs; canonical inventory and published rankings are unchanged. | Expand through explicit evidence admission, without calling this a complete annual atlas. |
| 20 | Source snapshot changes affect local proposal journals. | P3, verified | Bundle hash changes; existing journal archive/rebase path remains; contract documents the requirement. | Preserve old source snapshots and explicit rebase decisions. |
| 21 | This working-tree feature has not been merged or published. | P3, verified | Branch is `codex/seasonal-query-map`; previous main merge remains the recorded base. Contract and review name local verification commands. | Use the protected PR/check path for any subsequent main integration. |

## Synthesis

Roles reviewed: 7. Open P1 blockers: 0. Open P2 issues: 0. P3 notes/confirmed
strengths: 16. Five P2 findings were corrected during implementation.

Verdict: **APPROVED-WITH-CONDITIONS** for this local editorial query capability.
Scientific admission, complete seasonal coverage and public release are separate
outstanding work. CURRENT, SOUNDER and BEACON agree that the month selector must
never imply observed monthly fields or annual whole-current extrema.

Three amendments completed:

1. Validate/refresh the stale seasonal width receipt while retaining original
   candidate geometry and Davidson's regional width context.
2. Separate exact dates from seasonal source conventions in query validation,
   UI navigation, map styling, captions and exported provenance.
3. Expose phase links in the selected current card and exercise keyboard access,
   month gaps, manual playback/pause, December stop and narrow layout.

Verification commands and interpretation contract are in
`plans/rust-query-store-v1.md`, section "Source-defined seasonal routes".
