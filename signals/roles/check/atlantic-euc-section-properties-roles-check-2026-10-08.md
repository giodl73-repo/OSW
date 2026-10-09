---
skill: roles-check
topic: atlantic-euc-section-properties
date: 2026-10-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Internal functional review

Seven relevant installed roles reviewed the source extraction, query binding,
atlas card and checks. ORBIT is excluded because no analogy is used. This is
an internal review; it does not establish independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | Core maxima are not horizontal widths. | P2 | Protocol / chart | Separate cm/s and m panels; no width admission. Addressed. |
| CURRENT | Velocity is relative to an assumed motionless layer. | P2 | Methods pp164–165 | Retain 500 m reference and profiler method beside chart. Addressed. |
| CURRENT | A transport threshold cannot supply paired edges. | P2 | Table II footnote | Upper 200 m / >=20 cm/s retained as transport context only. Addressed. |
| SOUNDER | Printed dates disagree for two campaigns. | P2 | Tables I/II | Both claims retained, unresolved date null, hollow markers. Addressed. |
| SOUNDER | Campaign periods differ from property months. | P2 | 7802 / 7902 | Narrow Table II months and broader Table I periods both retained. Addressed. |
| SOUNDER | Original redistribution rights are unestablished. | P2 | Acquisition | Original ignored; institutional URL, size/hash and citation shipped. Addressed. |
| CHART | Connecting observations would imply an unsupported cycle. | P2 | Charts | Discrete campaign categories in printed order; no connecting lines. Addressed. |
| CHART | Station latitudes are not reported in the extracted table. | P2 | Scope | Null station latitude; no occupied map geometry. Addressed. |
| CHART | Figure contours offer a potential local width extraction. | P3 | Figure 2 | Paired-edge definition, depth and digitization uncertainty remain future work. |
| BEACON | FAO 200 km could be mistaken for a measured campaign width. | P2 | Caption / protocol | Lead explicitly unresolved and separated from these properties. Addressed. |
| BEACON | Subsurface data could be inherited by the cross-basin family. | P2 | Owner / guard | Atlantic identity only; compiled complete audited source binding. Addressed. |
| BEACON | Source review does not mean a dimension gap is closed. | P2 | Batch | Width counts unchanged; describes eight core-property records only. Addressed. |
| HARBOR | Conflict color alone would be inaccessible. | P2 | Charts / table | Hollow markers, asterisks and explicit conflict text. Addressed. |
| HARBOR | Mobile text was initially below 12 px. | P2 | Browser check | Font raised to 30 SVG units; bounds/readability checked at 320 px. Addressed. |
| HARBOR | SVG values need a textual alternative. | P2 | Details table | Semantic headers, units, dates and all eight rows. Addressed. |
| KEEL | Coherent receipt mutations can conceal source changes. | P2 | Rust guard | Exact compiled audit and planning-document equality; native mutation check. Addressed. |
| KEEL | Fresh offline checkouts cannot require a new paper download. | P2 | Python validator | Runtime authenticates extraction; original verification is explicit and local. Addressed. |
| KEEL | Main landing depends on protected checks. | P3 | Publication | Remote checks still required; prior failure is an existing fixture timeout. |
| LOGBOOK | Local passing checks must not be called mainline completion. | P2 | Batch / draft | Stacked draft publication, remote state reported explicitly. Addressed. |
| LOGBOOK | Source and protocol revisions must regenerate their consumers. | P2 | Build commands | Rebuild dashboard, query, index and engine in order. Addressed. |
| LOGBOOK | Scientific admission is separate from internal role review. | P3 | Status | Remains pending. |

Roles reviewed: 7. P1 blockers: 0. P2 issues: 18 addressed. P3 notes: 3 remain.
Verdict: APPROVED-WITH-CONDITIONS.

Top finding: the source's date conflicts cannot be silently repaired or played
as an annual cycle. CURRENT, SOUNDER, CHART and BEACON agree that these records
do not establish horizontal width or seasonal occupied geometry.

Amendments: preserve both date claims; bind the entire extraction in Rust;
provide readable discrete charts and an equivalent source table. Independent
scientific admission and remote protected checks remain conditions.
