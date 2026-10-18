---
skill: roles-check
topic: south-atlantic-secondary-band
date: 2026-10-17
source_commit: a2f00b926e19adb93663d7836f857fc286918ad9
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# South Atlantic component source and presentation review

Artifact: source-scoped historical width record, query/index/atlas integration
and independent graphic. Physical oceanography, provenance, cartography,
editing, accessibility, reproducibility and stewardship lenses apply. ORBIT
does not apply. This is review through installed lenses, not human sign-off.

| Role / # | Finding | Severity / state | Evidence / recommendation |
|---|---|---|---|
| CURRENT1 | The200 km band is only the southern SAC component. | P2 resolved | Frozen scope and visible caption keep total-current and secondary-core width unknown; no full-width inference or ranking. |
| CURRENT2 | Reference depth and transport layer are distinct. | P2 resolved | sigma4=45.87 and3470–3560 m reference retained; upper1000 m remains field/transport context, fixed width slab null. |
| CURRENT3 | Core position, displacement and transport cannot define edges or errors. | P2 resolved | Source audit separates all quantities;26 source mutation/identity/geometry tests pass. No paired geographic edges or numerical error inferred. |
| SOUNDER1 | Facts must trace to the correct original section and month. | P2 resolved | Original p854, Table1/2(k), Figure5 visually reviewed; October1983 is month precision; publication1990 not observation date. |
| SOUNDER2 | Original response and authored products need independent pins. | P2 resolved |1,284,252-byte14-page original SHA frozen; separate acquisition/protocol/figure hashes and immutable audit.71 engine dependencies verify. |
| SOUNDER3 | Existing modern surface diagnostics have different support. | P2 resolved |2013 and1995–2016 at30 W retained separately; no pooling with historical1 E subsurface band. Source/Southern inventory27-test gate passes. |
| CHART1 | A geographic200 km buffer would imply unsupported boundaries. | P2 resolved | No new geometry or footprint; independent statement graphic and scalar comparison point only. |
| CHART2 | One historical month cannot support seasonal animation. | P2 resolved | Calendar-month membership and day interval remain null; actual seasons page has playback disabled. No annual range. |
| CHART3 | Primary-front and southern-band extents must remain distinguishable. | P2 resolved | Visible caption explains additional SAC flow at primary front. Atlas retains existing route and component diagnostic links. |
| BEACON1 | The headline needs to name the component. | P2 resolved | Phase/metric label, independent graphic and first caption explicitly identify southern component breadth and unknown total width. |
| BEACON2 | Similar200 km numbers risk being conflated. | P2 resolved | Separate source fields for band breadth and core displacement; method note distinguishes them; source guards reject promotion. |
| BEACON3 | Readers need a short source path. | P3 verified | Actual source query /measurement matches native result; record inspector works and no PDF is fetched automatically. |
| HARBOR1 | Numeric meaning and scope cannot depend on the point's color. | P2 resolved | Numeric text, descriptive aria label, caption and method note accompany the point. |
| HARBOR2 | Narrow screens must preserve qualifications and source access. | P3 verified |320 px reflow and source link checked; actual mobile screenshot visually inspected. |
| HARBOR3 | New data should reuse established controls. | P3 verified | Existing semantic source links and inspector controls reused. New actual UI test covers inspector return, reduced-motion viewport and disabled playback; prior100-card baseline covers general keyboard controls. |
| KEEL1 | Updated scientific suite must run from a clean source commit. | P2 pending | Full offline invocation started from clean a2f00b9 after actual integration checks. Record terminal result before final verdict. Prior1512-test baseline is reported separately. |
| KEEL2 | New guards must reject coherent edits and owner/deletion tricks. | P2 resolved | All nine coherent mutations reject in both native and WASM;47 Rust tests pass. Source identity frozen independently of editable owner/context. |
| KEEL3 | Existing scientific records must survive unchanged. | P2 resolved | All147 prior widths /34 diagnostics and41 collections compare equal. Six seasonal routes and four other cards change only parent hash. All canonical imports and25 series unchanged. |
| LOGBOOK1 | Count changes must not imply whole-current measurement coverage. | P2 resolved |148 scoped records /78 names include71 numeric-description owners and7 constraint-only owners; whole-current width and annual extrema remain unestablished. |
| LOGBOOK2 | Copyrighted source pages must remain outside Git. | P2 resolved | Acquisition receipt, factual audit, protocol and own SVG only; original PDF and OCR ignored.27 staged files matched disk exactly. |
| LOGBOOK3 | Local gate status and external provider failures need separate reporting. | P2 pending | Changed South Pacific/Radenac/Qiu transports pass remote84ae8bf; unchanged Reading VanAken source refuses connection. No remote-green or merge-readiness claim. Same draftPR83 retained. |

Roles reviewed:7. Outstanding P1 blockers:0. Outstanding P2 gates:2
(full updated-data suite and complete remote acquisition). Local focused source,
Rust and changed UI gates pass. Verdict: **APPROVED-WITH-CONDITIONS**.

Top finding: source-reported component breadth is useful almanac evidence but
cannot supply total SAC width. CURRENT, SOUNDER and CHART agree that component,
month, reference and unresolved boundary rule must travel with the number.

## Three amendments

1. Completed: freeze component identity, month precision, reference and excluded
   interpretations in Python and Rust; preserve scalar/data provenance and
   prohibit owner reassignment, deletion and coherent audit forgery.
2. Completed: expose component scope and unknown total width beside the number,
   with source/inspector access, mobile reflow and existing diagnostic navigation.
3. Pending: append terminal new full-suite result and current remote acquisition
   outcome; update this same PR. Do not claim the earlier147-record suite proves
   this148-record update or that external source availability is resolved.
