---
skill: roles-check
topic: osnap-wg-sample-support-v1
date: 2026-10-24
source_commit: 199e1acc7597b2bdf0fea099ee8402e15508b1d3
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 7
p3_count: 14
verdict: APPROVED-WITH-CONDITIONS
---

# OSNAP sample-support audit v1: prospective functional review

One assistant applies the seven repository functional lenses to the new
operator, tests, protocol and reusable workflow in the working tree based on
the source commit above. This is not independent scientific review. ORBIT is
excluded because the work concerns an Earth observation array only.

The preceding header case actually succeeded in cloud run `40092026859`.
This new producer has not read original observations. Approval is conditional
on committing and verifying the complete prospective preflight before original
sample access and running the synthetic suite first in the bound cloud job.
The prepared workflow and producer enforce that condition. The phase remains
review-only until the committed freeze is verified remotely.

## CURRENT — physical support and interpretation

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 1 | Paired availability is calculated per cell, with explicit full denominators. | P3 | `paired_support`; opposite-component-mask synthetic case. | Retain separate paired cells, any-bin profiles and all-bin profiles. |
| 2 | Pressure variation and supplied ADCP moving depth have distinct meanings. | P3 | Nominal DEPTH is labeled; no pressure-to-depth conversion; actual synthetic NetCDF point/ADCP cases. | Keep those fields separate in the later viewer and layer selection. |
| 3 | Physical QC, tidal processing, common-layer coverage and both current edges remain unproved. | P2 | Output explicitly denies physical validity; no rotation, interpolation or width method exists. | Review actual audit results and freeze a separate dimension method before deriving any widths. |

## SOUNDER — identity, decoding and custody

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 4 | The exact existing artifact is restored and every selected original member is checked again. | P3 | Archive SHA, custody equality, reviewed directory, CRC, member SHA and exact reconstructed header guards. | Preserve the original acquisition record; never download a replacement silently. |
| 5 | Masked and nonfinite observations remain unavailable, and absent time rows do not become bridged cadence. | P3 | `finite_values`, `audit_time`; mask, NaN/Inf and missing-time fixtures. | Keep availability separate from scientific QC in all later projections. |
| 6 | Repository and instrument-level licensing statements differ. | P2 | All original headers retain the PI-contact language; custody retains the landing-page CC BY link. | Preserve both verbatim source statements in evidence and resolve their relationship before claiming a unified redistribution/commercial-use status. This audit makes no such claim. |

## CHART — coordinates, footprint and edges

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 7 | Actual coordinate variables are read instead of rounded global position attributes. | P3 | `coordinates` retains source attributes, values and singleton/range checks. | Carry datum/reference and uncertainty into any later observation map. |
| 8 | A partial coordinate vector cannot be promoted to a singleton station position. | P3 | Cardinality checks include the original array size; masked-extra-coordinate fixture. | Retain explicit position failure rather than silently selecting a value. |
| 9 | No mapped sample footprint, current band or state intersection is established. | P2 | Output has zero new geometry/state joins; no geographic interpolation. | Require a reviewed observation-footprint and current-identity stage before map admission. |

## BEACON — understandable scope

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 10 | The result says sample-support audit, with zero derived physical dimensions. | P3 | `PASS_SAMPLE_SUPPORT_AUDIT_ONLY` and explicit zero fields. | Preserve that status next to future progress indicators. |
| 11 | Instrument pressure/depth extrema are not labeled annual current ranges. | P3 | Protocol separates support extrema from seasonal widths; field names retain source units. | Keep this distinction in the later seasonal visualization. |
| 12 | A successful audit may still reveal that a width cannot be resolved. | P2 | Availability is not edge coverage or physical validity; anomalies are reported rather than interpreted away. | Review actual results before using a measurement-ready label. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 13 | The planned result is structured text with explicit counts and month labels. | P3 | JSON instrument/month records and human-readable protocol. | Maintain a data table equivalent in the future viewer. |
| 14 | Empty months and unavailable depth are represented explicitly. | P3 | Continuous actual month range, zero row counts and null unsupported depth fields. | Do not use color alone to distinguish absent observations from zero values. |
| 15 | No public keyboard, focus, reflow or contrast validation has been performed for a sample viewer. | P2 | This change supplies no public viewer and launches no browser. | Require a later serialized cloud browser gate before public UI admission. |

## KEEL — bounded, reproducible execution

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 16 | Original access is cloud-only and requires a committed transitive freeze. | P3 | `main` guard precedes file access; `verify_preflight` binds the source helper and its frozen dependency set. | Commit preflight and verify all bytes remotely before selecting the support phase. |
| 17 | Resource limits avoid a local rebuild and overlap with other heavy work. | P3 | Parent shared concurrency; no competing reusable-workflow lock; one CPU, numeric workers one, 64 MiB array/member and 8 MiB output caps. | Keep artifact restoration, audit and later browser work sequential. |
| 18 | Actual observations have not yet exercised the prepared decoder/shape rules. | P2 | Tests use only tiny synthetic arrays and actual synthetic NetCDF files. | First run those tests in the pinned cloud environment; if original execution reveals a defect, preserve v1 and create a corrected version. |

## LOGBOOK — truthful state and ownership

| # | Finding | Severity | Evidence | Action |
|---|---|---|---|---|
| 19 | The prior executed header producer, tests, workflow and receipts remain unchanged. | P3 | New versioned support files and transitive hash checks. | Retain the original freeze and source first-execution provenance. |
| 20 | Working-data publication and scientific release are absent from this workflow. | P3 | Read-only workflow permissions; artifact output only; no publisher. | Review and separately admit any later measurement and visualization work. |
| 21 | Header success does not complete the active current/eddy gap-filling objective. | P2 | Existing global gaps and later support/dimension/viewer gates remain. | Continue through actual support review and prioritized physical measurements; do not claim the catalogue is measured. |

## Synthesis and amendments

Roles reviewed: 7. P1: 0. P2: 7. P3: 14.
**APPROVED-WITH-CONDITIONS for source-support execution only.**
CURRENT and SOUNDER agree that finite paired availability does not establish
physical validity. CHART and CURRENT agree that a mooring array is not a
measured current boundary. HARBOR and BEACON require explicit missing support
and stage labels in the later viewer.

Three amendments incorporated before freeze:

1. Keep nominal depths and pressure proxies separate from supplied ADCP depth;
   add synthetic original-format fixtures for both instrument classes.
2. Prevent masked extra coordinates from appearing as a singleton position;
   record strict time ordering, nonadjacent duplicates and gaps without filling.
3. Restore the first source artifact, preserve full custody, bind all imported
   helper dependencies, and retain the review-only phase until the preflight
   is committed and verified. No original access or release approval is inferred.

Remaining P2 findings are downstream scientific/visualization requirements or
the actual cloud execution gate. None is represented as closed by preparation.
