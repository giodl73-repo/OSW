---
skill: roles-check
topic: osw-rebrand
date: 2026-08-29
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK, ORBIT]
p1_count: 0
verdict: APPROVED
---

# OSW rebrand roles check

## Artifact

- Type: repository-wide naming, interface, metadata, and generated-artifact rebrand
- Reviewed source commit: `4eccc1a` (`Rename project to OSW`)
- Formal name: **Ocean States of the World**
- Colloquial name: **The Ocean States**
- Compact repository/interface mark: **OSW**
- Remote verified: `https://github.com/giodl73-repo/OSW`

All eight native roles were selected because this repository-wide change touches
scientific language, map interpretation, public explanation, accessibility,
machine interfaces, release truth, and the existing planetary-comparison scope.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “States” could imply fixed, sealed regions, but the README immediately says provinces move, leak, split, merge, and change with depth. | P3 | `README.md` introduction | Keep this dynamic qualification in the first reading path. |
| 2 | The history explicitly says states are an analogy, not sovereign, fixed, exhaustive-through-depth, or published boundary geometry. | P3 | `HISTORY.md` rename entry | Preserve this limitation whenever the naming story is condensed. |
| 3 | Temperature, heat content, transport, and delivery limitations remain intact after the rename. | P3 | README and Atlas 10 footer | Do not let future OSW slogans replace these budget distinctions. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Versioned `oceanlines.*` schemas and `window.OCEANLINES_*` observation globals remain unchanged. | P3 | observation data and `atlas/app.js` | Treat these identifiers as compatibility interfaces. |
| 2 | New relation-only interfaces correctly use `window.OSW_RELATION_*`. | P3 | `atlas/app.js` | Use OSW for new machine contracts while documenting any future migration. |
| 3 | Dataset attribution, receipts, checksums, units, and baselines were not rewritten as branding. | P3 | data files and source register | Continue separating provider metadata from project identity. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Ocean States” matches the 56-province surface map better than a line-only name. | P3 | province atlas | Keep “approximate,” “classic vocabulary,” and “schematic geometry” beside the map. |
| 2 | The name does not erase the 36 overlapping waters, flows, edges, floor, life, and event shapes. | P3 | atlas controls and README | Continue presenting states as a base geography crossed by other systems. |
| 3 | All fourteen active figure names and embedded titles consistently use the `osw-`/OSW identity. | P3 | `figures/` | Regenerate through the renamed output defaults to prevent drift. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The three-level naming contract is short and unambiguous. | P3 | README opening | Always expand OSW on first use outside the repository. |
| 2 | “The Ocean States” provides a memorable spoken name without creating another classification label. | P3 | README naming contract | Keep it colloquial, not as a competing formal title. |
| 3 | The entry invitation now leads with the actual discovery: 56 states, 36 features, and depth. | P3 | `Enter the Ocean States` | Preserve the direct route to map, method, sources, and limitations. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The wordmark is short and the full expansion is adjacent in the masthead. | P3 | atlas and projection headers | Do not rely on the initialism alone in page titles or accessible names. |
| 2 | Existing semantic controls, live status, text directory, and non-color cues remain unchanged. | P3 | atlas interface | Re-run keyboard and reflow checks whenever the masthead layout changes. |
| 3 | Renamed SVGs retain titles, descriptions, and meaningful image alternatives. | P3 | figures and embedding pages | Keep accessible text synchronized with future figure regeneration. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The exact offline CI suite passes: 77 tests before the additional naming-contract test. | P3 | `.github/workflows/validate.yml` | Keep the full discovery command as the default gate. |
| 2 | Feature geometry validation and browser JavaScript syntax checks pass. | P3 | validator and `atlas/app.js` | Continue running both after generated-artifact changes. |
| 3 | Edge loads the renamed assets and reports `data-smoke="passed"` for the relationship engine. | P3 | local Atlas 10 smoke test | Retain a test for the split between legacy observation and new OSW relation globals. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | GitHub repository, origin URL, homepage, description, README links, badge, and citation now agree on OSW. | P3 | remote and repository metadata | Verify this alignment again before the next public promotion. |
| 2 | The rename is recorded as a dated conceptual milestone, while dated reviews keep their historical prose. | P3 | `HISTORY.md` and `signals/` | Preserve historical names rather than rewriting the evidentiary record. |
| 3 | The private preview branch was not pushed during the remote rename. | P3 | publication status | Keep publication as a separate owner decision. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new name centers the Earth-ocean atlas and does not elevate the gas-giant analogy into the project identity. | P3 | repository title | Keep planetary comparison as a disciplined secondary lens. |
| 2 | OCEANBELTS remains a named map family rather than being silently folded into “states.” | P3 | README map families | Continue naming which mechanism is compared across planets. |
| 3 | Existing warnings against equating visible temperature patterns with full-depth heat remain intact. | P3 | OCEANBELTS and Atlas 10 | Preserve forcing, stratification, depth, and boundary differences beside comparisons. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 0 | P3 notes: 24

**Verdict: APPROVED**

**Top finding:** The name is strong only because the primary reading path makes
clear that ocean states are dynamic, overlapping, depth-dependent scientific
objects—not fixed political territories.

**Cross-role consensus:** CURRENT, CHART, BEACON, and LOGBOOK agree that the
state-map metaphor is both the hook and the principal interpretation risk; its
limitations must remain adjacent to the name and maps.

## Amendments

1. Add an automated naming/compatibility contract so active OSW branding cannot
   silently rewrite versioned observation interfaces. Applied after review in
   `analysis/test_atlas.py`.
2. Add an inline compatibility note where the atlas consumes legacy observation
   globals. Applied after review in `atlas/app.js`.
3. Align the public GitHub description and homepage with the formal name while
   keeping preview publication separate. Applied through repository metadata;
   the private branch remains unpushed.
