---
skill: roles-check
topic: kuroshio-luzon-mooring-state
date: 2026-10-02
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Kuroshio local instrument-point state admission

Reviewed the primary 2025 Frontiers paper, source/citation ledgers, canonical
observation and supporting relation, claim binding, full and screened views,
and packets. The seven relevant installed lenses are CURRENT (physical
meaning), SOUNDER (source support), CHART (state lookup), BEACON (reading),
HARBOR (equivalent access), KEEL (reproducibility), and LOGBOOK (release status).
ORBIT is omitted because no planetary analogy is introduced. This is in-task
review, not independent scientific or human accessibility approval.

| Role | Finding | Severity | Evidence and disposition |
| --- | --- | --- | --- |
| CURRENT | Instrument positions are not the current axis. | P3 | Observation, relation and pages state that the core is west of the array and the whole-current passage is unresolved. |
| CURRENT | The deeper flow is a distinct undercurrent. | P3 | Depth note distinguishes the Luzon Undercurrent; no separate undercurrent presence assertion is admitted. |
| CURRENT | Independent scientific claim review remains outstanding. | P2 | Both new claims remain not_individually_reviewed and enter the source-located worklist. |
| SOUNDER | The 2025 publication describes a 2018-2020 observation window. | P3 | Publication date and month-level observation interval are separate; no invented deployment/recovery days. |
| SOUNDER | Depth coverage is incomplete. | P3 | Source section 2 identifies the failed middle downward ADCP and excludes the upper 50 m; pages and packets preserve these limits. |
| SOUNDER | Citation and source reuse are pinned. | P3 | Five authors, DOI, publication date, primary page and Crossref response digest retained; publisher notice and its CC BY 4.0 link checked. |
| CHART | A name-associated state cannot substitute for a coordinate lookup. | P3 | All three reported positions project into CHIN, not an assumed KURO assignment. Checker recomputes membership against coast-masked display polygons. |
| CHART | Point membership does not establish containment of the current. | P3 | Relation is source_reported_local_current_presence with explicit instrument-point/whole-current limit; all global current/state unknown rows remain unchanged. |
| CHART | Coordinate metadata must not be overstated. | P3 | Source-reported instrument coordinates stay in the observation record; no new CRS84 geometry, surveyed state boundary, interpolated transect, or footprint is exported. |
| BEACON | Dates need an intelligible precision statement. | P3 | Time detail says months, absent exact days and no continuous valid coverage at all stations/depths. |
| BEACON | Source and scope should be beside the observation. | P3 | Full and screened pages show coordinates, instrument limits, article link, author credit, license link and local-observation limit together. |
| BEACON | The atlas should answer the state's question directly. | P3 | CHIN passport exposes one local-presence row with dates and a Kuroshio link; full CHIN entity page exposes the corresponding observation. |
| HARBOR | Coordinate meaning should not depend on a map. | P3 | Longitude/latitude order and three stations are ordinary text. No new color or motion encoding is required. |
| HARBOR | Downloaded evidence must match the page. | P3 | Screened packet retains three points, month precision, depth note, source and matching observation_support in the claim. Browser exercises the packet. |
| HARBOR | Human accessibility review remains open. | P2 | Automated visibility/link checks do not substitute for a full assistive-technology review. |
| KEEL | Adding a local observation must preserve existing IDs. | P3 | New relation appends after previous admissions. All 14,304 prior claims, 5,760 relations, seven observations, 157 geometries, 330 names and 29 measurements retain identical record content. |
| KEEL | Support changes must invalidate old approvals. | P3 | Claim fingerprint includes instrument points, time precision, depth note and state limit; checker binds support back to the target observation. |
| KEEL | A state lookup must be reproducible from pinned inputs. | P3 | Manifest pins state SVG and lookup helper; release checker recomputes all three memberships offline. Crossref refresh retained 65 old receipts and fetched the new one. |
| LOGBOOK | Counts must reconcile. | P3 | Full: 318 entities, 14,306 claims, 5,761 relations, eight local observations. Screened: 218 entities, 8,697 claims, eight local observations, 137 sources, 270 site files. |
| LOGBOOK | Admission is narrower than publication. | P2 | Seventeen used source-use decisions elsewhere, independent science, human accessibility, and owner publication gates remain open. Candidate remains unpublished. |
| LOGBOOK | Notices and methods must describe the actual transformation. | P3 | Author attribution, CC BY link and OSW point-to-display-state method are recorded; no instrument series, model fields, article or figure reproduced. |

Roles reviewed: 7. Findings: 21 (P1 0, P2 3, P3 18).
Verdict: APPROVED-WITH-CONDITIONS for local instrument-point evidence admission.
The three P2 findings are outstanding release conditions, not concealed claim
approvals. CURRENT/CHART agree on point versus whole-current support;
SOUNDER/BEACON agree on month precision and incomplete depth coverage.

Amendments implemented:

1. Preserve month precision and instrument/depth limitations in canonical
   records, claim fingerprints, both current pages and packets.
2. Append the presence relation and verify prior records remain unchanged.
3. Expose reciprocal CHIN/current navigation, source credit and license, and
   reconcile methods, notices, source-use decisions and citation counts.

Verification: full release checker, screened preview/site checker, motion
almanac checker and both JavaScript syntax checks pass. Both browser suites
pass with current observation, state link and instrument details; reciprocal CHIN/current navigation checks pass in both full and screened
views, including the CHIN passport local-presence group.
