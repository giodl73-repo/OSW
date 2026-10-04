---
skill: roles-check
topic: antilles-inline-atlas-card
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Antilles inline atlas card: internal editorial review

Scope: observed-section helper, atlas navigation, dashboard fingerprints and
focused browser checks. ORBIT excluded: no planetary comparison. These are
internal role lenses, not independent scientific admission.

| Role | Finding | Severity | Resolution or condition |
|---|---|---|---|
| CURRENT | Instrument positions could imply a current axis. | P2 resolved | Points only; transverse role explicit; no route admission. |
| CURRENT | Repeat span could imply full width. | P3 condition | One-sided sampled-peak span labeled; full width remains null. |
| CURRENT | Two surveys could imply seasonal evolution. | P3 condition | Dated selection only; no annual playback or interpolation. |
| SOUNDER | Coordinates and sample values need validation. | P3 verified | Finite coordinates, quality, timestamps and nullable velocities checked. |
| SOUNDER | Rejected data must not draw an authoritative map. | P3 verified | Invalid/missing response falls back to detailed-page link. |
| SOUNDER | New data must affect its update fingerprint. | P2 resolved | Series added to time-evidence group; changed diagnostic test isolates Antilles. |
| CHART | Survey stations must remain inside the selected extent. | P3 verified | Shared union extent; every displayed station checked in browser. |
| CHART | Background routes can distract from observations. | P3 verified | Reference lines and name locators fade during observation selection. |
| CHART | Hover names must also work on keyboard focus. | P3 verified | SVG station focus exposes name; Enter/Space activates cast details. |
| BEACON | Acquisition date could look like observation date. | P3 verified | May 2005 dates displayed beside survey selector and counts. |
| BEACON | Quality colors need an explanation. | P3 verified | Teal usable, orange caution, gray missing 400 m sample described. |
| BEACON | Update light could imply live ocean movement. | P3 condition | Existing inventory-edit explanation retained. |
| HARBOR | Map needs equivalent readable cast details. | P3 verified | Selected cast status and linked table retain date, velocity and quality. |
| HARBOR | Narrow card could overflow the document. | P3 verified | 320 px browser reflow checked. |
| HARBOR | Global reset must clear selected observations. | P3 verified | Overlay, selected card and section query removed. |
| KEEL | Async restoration could erase the chosen survey. | P2 resolved | Section query preserved atomically through initial selection and loading. |
| KEEL | A delayed fetch could resurrect a disposed card. | P3 verified | Disposed guard tested after Global view. |
| KEEL | Switching currents could retain unrelated stations. | P3 verified | Overlay and styling cleanup tested on Agulhas selection. |
| LOGBOOK | Inline display must not inflate admitted coverage. | P3 verified | Route, width and canonical inventory counts unchanged. |
| LOGBOOK | Review must disclose verification scope. | P3 condition | Focused checks only; full repository suite not rerun. |
| LOGBOOK | Scientific admission remains distinct. | P3 condition | Tides, threshold and boundary support still require independent review. |

## Synthesis

21 findings: zero P1; three P2 addressed; 18 P3 verified notes or remaining
conditions. APPROVED-WITH-CONDITIONS for local presentation. No new current
axis, full width, annual range or published measurement admitted.

Three amendments: preserve point roles and background distinction; fix atomic
survey URL restoration; include source-series fingerprints and dispose delayed
observation overlays. Fourteen dashboard tests and the focused inline atlas
browser pass. Detailed-section browser passes; updated screenshot inspected.
Shared navigation browser passes 100 current links, 62 route-card links,
27 phase deep links and six seasonal round trips. Canonical almanac SHA256
remains 6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e.
