---
skill: roles-check
topic: australia-published-section-transports
date: 2026-10-09
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Australian section transport review

Artifact: pinned scientific table extraction, Rust query projection, dashboard
coverage and shared browser cards. Reviewed working changes based on
`f52db2ed2b79e85565cd2dd83879fd03a93806dd`; this is an internal functional
review, without independent scientific admission. ORBIT is excluded because
the batch makes no planetary comparison.

## CURRENT — statistical and physical support

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 1 | Transport cannot supply a current dimension or seasonal width margin. | P2 resolved | Original Table 1; audit null width/length and false eligibility flags. | Keep Sv records in separate collections; no added width phases or playback. |
| 2 | Depth limits and overlapping variants differ across sections. | P2 resolved | Protocol rules; original p7; frozen projection guard. | Retain explicit eastern 0–2000 m only; preserve western core bounds as null, do not add full-westward/recirculation quantities. |
| 3 | No formal assimilation does not imply a closed freely evolving budget. | P2 resolved | Original methods p4; audit relaxation note and visible method details. | State HYCOM surface relaxation and boundary forcing; no inferred budget closure. |

## SOUNDER — source identity and uncertainty

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 4 | Publication, copyright and original bytes need exact identity. | P3 | Acquisition metadata, complete institutional PDF, reproduced SHA256/byte count. | Track metadata and audit; leave copyrighted original ignored and reproduce no source figures. |
| 5 | Table 1(b) plus/minus notation lacks an explicit statistic definition. | P2 resolved | Original p7 versus Table 1(a)'s explicit SD column. | No SE/CI whiskers; display notation with qualification, keep validation SD separate. |
| 6 | Source contradictions and incomplete monthly sampling must survive extraction. | P2 resolved | M1 W/S; M6 source count 18 versus 17 calendar months; native guard fixtures. | Preserve both source statements without corrections or invented dates/matched masks. |

## CHART — cartography and graphic grammar

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 7 | A partial coordinate cannot locate a measured transect or footprint. | P2 resolved | Scene geographic role and caption; source supplies only one coordinate per section. | Render dashed coordinate guides over OSW context; prohibit section geometry/state joins. |
| 8 | Mixed directions and unequal integration scopes cannot form a universal signed ranking. | P2 resolved | Native scene common 0–40 Sv magnitude axis; full table directions/layers/variants. | Show magnitudes, separate directions and scopes; no additive or signed current budget. |
| 9 | Permanent coordinate labels collide in the complete 35-entry query. | P2 resolved | Duplicate longitudes and shared section coordinates. | Reveal guide labels on hover/focus; retain every coordinate in the data table. |

## BEACON — reader understanding

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 10 | Sv needs a plain-language definition. | P3 | Scene scope says one million cubic metres per second. | Keep this next to the chart in all three consumers. |
| 11 | Internal raw JSON is unsuitable as the main method explanation. | P2 resolved | Shared renderer method details. | Show model, grid, period, vertical levels, forcing and validation method as prose. |
| 12 | Source labels without canonical identities must remain searchable. | P2 resolved | Fifteen unowned model entries/two validation pairs; full query tables. | Show unassigned identity, retain original names, avoid silent alias/family transfer. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 13 | Fixed-size charts can overflow narrow pages or shrink labels. | P2 resolved | 320 px browser checks and reviewed Hiri mobile screenshot. | Use local focusable scroll regions with visible instructions; verify page reflow and effective font size. |
| 14 | Hover-only map labels deny keyboard access. | P2 resolved | Focusable SVG coordinate groups with aria labels and focus/blur events. | Reveal the same labels on focus; provide the complete source-coordinate table. |
| 15 | Graphic color cannot be the sole route to meaning. | P3 | Tables, directions, numeric magnitudes, source discrepancies and source-row links. | Preserve semantic table headers and 44 px link/button targets; no motion required. |

## KEEL — coherent scientific validation

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 16 | Updating record receipts alone must not legitimize altered scientific fields. | P3 | Frozen Rust projection and shared native/WASM mutation bytes. | Reject altered mean, depth, uncertainty kind, direction, count, owner and missing collection. |
| 17 | Optional legacy loading must not bypass proof for current transport owners. | P2 resolved | Validator's legacy-absence branch and tenth native/WASM guard. | Proof is required when collections, source pin or object transport joins/capabilities are present; stripped proof is rejected. |
| 18 | A new dashboard metric changes menu and snapshot validation contracts. | P2 resolved | Browser caught missing option and overly strict absent-field validation. | Add the metric option; treat an absent new capability as zero, without changing all 240 fingerprints. |

## LOGBOOK — truthful publication state

| # | Finding | Severity | Evidence | Recommendation / resolution |
|---|---|---|---|---|
| 19 | Hosted source access failure remains independent of local validation. | P2 retained limitation | Parent PR77 runs 37938395659 / 37938436349 stop on Qiu/Chen timeouts. | Record that GEOMAR fallback was not reached; do not claim green remote CI. |
| 20 | Source-index/query coverage needs a reproducible receipt. | P3 | 42 collections, 151 indexed JSON sources, registered browser check, page assignments. | Finalize exact passing commands and artifact sizes before draft publication. |
| 21 | This transport batch does not close the complete atlas goal. | P2 retained limitation | Width/route inventories unchanged; 89 length gaps and many physical eddy footprints unresolved. | Publish a scoped draft receipt and carry dimension/geometry/seasonal work forward. |

## Synthesis

Seven roles, 21 findings. No P1. Thirteen P2 findings are resolved, one additional P2
engineering amendment is resolved, two P2 limitations remain explicit and five
P3 findings record verified strengths. Fourteen resolved P2 findings include the
engineering amendment. Verdict remains conditional on independent source
admission and publication gates; local checks pass with the documented ENOSPC
recovery (53 selected tests), without a wholly passing full-suite invocation.

Top finding: a volume-flow statistic does not establish an annual geometric
current envelope. CURRENT, SOUNDER and CHART agree that temporal, spatial and
uncertainty support must remain separate across source and UI layers.

## Amendments

1. Preserve exact frozen statistical support and the two source discrepancies;
   carry native-verified mutation bytes into WASM rejection checks.
2. Keep map guides as partial coordinate context with focus/hover labels and
   table alternatives; never publish them as measured transects or state joins.
3. The proof-erasure guard is closed and the verification receipt records the
   ENOSPC recovery; use a stacked
   draft PR and retain source-access/mainline limitations in its description.
