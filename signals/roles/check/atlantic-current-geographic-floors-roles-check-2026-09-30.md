---
skill: roles-check
topic: atlantic-current-geographic-floors
date: 2026-09-30
roles_used: 6
p1_count: 2
verdict: NEEDS-WORK
---

# Atlantic current geographic floors: quick role review

Artifact: the three new source-gated lower-bound records, gate-distance audit,
full data candidate, and rights-screened atlas. Selected CURRENT for physical
interpretation, SOUNDER for provenance, CHART for geographic representation,
HARBOR for reader access, KEEL for reproducibility, and LOGBOOK for release
state. This is a quick review (two findings per role).

| Role | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| CURRENT | Benguela, Brazil, and DWBC appear at multiple latitude sections, but the cruises and decade solutions do not trace one simultaneous streamline. | P2 | `research/ocean-current-almanac.json`, three new bounds | Keep these as conditional source-gated geographic floors; do not rank as physical path lengths. Done. |
| CURRENT | The DWBC entry is scoped to the North Atlantic even though the paper also identifies South Atlantic sections. | P3 | DWBC `length_scope` | Retain the North Atlantic segment label and avoid extrapolating to a whole-Atlantic length. Done. |
| SOUNDER | The source needs a verified DOI, publisher, date, terms, and exact section locators. | P2 | metadata override and source-use review | Recorded the article metadata, CC BY 4.0 statement, DOI, and sections 3.1.2, 3.1.3, 3.2.3; fetched Crossref record. Done. |
| SOUNDER | Derived distances need a regenerable geodesic and a stated rounding rule. | P2 | `analysis/build_ocean_current_gate_distances.py` | Pin WGS84 latitude gates and rounded-down floors; validate 1,218.4 km and 2,496.6 km. Done. |
| CHART | A meridional abstract gate could be mistaken for an observed current axis. | P2 | gate-distance audit and site | Keep latitude-only gate type, geographic-floor label, and no traced line. Done. |
| CHART | Benguela ecosystem extent and cross-stream section widths could be confused with along-current distance. | P2 | Benguela scope | State the distinction in the source ledger and use only section latitude separation. Done. |
| HARBOR | Readers need text labels for the evidence class and rank exclusion. | P3 | screened length inventory | Browser check verifies geographic-floor and no-whole-current labels. Done. |
| HARBOR | Human accessibility review is still open for public presentation. | P1 | publication gate | Obtain human review before publishing; automation is not signoff. Open. |
| KEEL | New measurements could renumber earlier claim IDs and invalidate ranked editorial reviews. | P2 | release builder | Append the three new measurements after existing records; release build confirms eight ranked decisions still match. Done. |
| KEEL | Counts and file hashes must be regenerated and checked after code and ledger changes. | P2 | release/check scripts | Rebuild and rerun all relevant checks, browser test, and boundary audit. Done. |
| LOGBOOK | Current plan counts were stale after the Thor/Ursa additions. | P2 | publication plan | Update to 134 source-scoped eddy records, 38 screened eddies, and seven geographic floors. Done. |
| LOGBOOK | Seventeen used external sources still have pending terms, and eight ranked lengths still await scientific review. | P1 | public release | Keep the public release gate closed. Open. |

Roles reviewed: 6. P1 blockers: 2 findings on the same public-release gate;
P2 issues: 8; P3 notes: 2. Verdict: **NEEDS-WORK for publication**.
Top finding: publication remains blocked by pending rights and scientific and
human review, despite a reproducible reviewed preview. Cross-role consensus:
the new floors cannot be presented as measured along-current lengths.

Amendments: (1) Keep the three floors unranked with explicit section and
time-scope caveats; (2) retain publisher citation, license notice, and exact
WGS84 gate calculation; (3) keep the public gate closed until the remaining
source and human reviews are completed.
