---
skill: roles-check
topic: baffin-latitude-gate-bound-v1
date: 2026-10-23
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 1
verdict: NEEDS-WORK
---

# Baffin described-latitude bound: prospective review

Manual application of seven installed functional lenses by the assistant,
not seven independent reviewers or external scientific peer review. ORBIT
does not apply: no planetary comparison is made. Base source commit:
`029bab1`; review covers the new prospective operator and tests in the working
tree, source review and protocol. The later preflight freezes their exact
bytes, including this review. No actual source-gate calculation was run before
this review. Synthetic tests use other latitude pairs.

Artifact type: source-stage scientific calculation and prospective delivery
contract. Review authority is limited to internal editorial, arithmetic and
engineering checks. This is not a release or scientific admission verdict.

| # | Role | Finding and evidence | Severity | Recommendation / disposition |
|---|---|---|---|---|
| 1 | CURRENT | The abstract reports observed latitude extent, not a connected whole-current axis (`length-source-review-v1.json`, extent interpretation). | P2 | Retain conditional geographic-floor wording; no guaranteed physical minimum. Encoded in protocol and report fields. |
| 2 | CURRENT | The Results opening paragraph changes the historical northern naming extent (original printed p183). | P2 | Keep the author naming convention next to the value and in source provenance. Present in report and prospective SVG. |
| 3 | CURRENT | Two summer studies do not establish paired dates, fixed layer, winter extent or seasonal variation. | P2 | Preserve null dates/layer/ranges and false playback eligibility; reject source support changes. Implemented in source validation. |
| 4 | SOUNDER | Retained institutional original digest matches the existing acquisition; only PDF pages 1 and 4 were inspected for this question. | P3 | Preserve exact byte count/hash, acquisition and selected review scope; no full-paper claim. |
| 5 | SOUNDER | The existing +/-0.5-degree convention is editorial sensitivity, not source error. | P2 | Keep all nine scenarios and the interpretation in report, query projection and visual caption. Source-stage report and protocol cover this; query projection remains pending. |
| 6 | SOUNDER | Original hosting does not establish redistribution rights. | P2 | Keep original PDF ignored and unbundled; publish only attributed facts and original OSW calculation. No new original fetch is needed. |
| 7 | CHART | Abstract longitude zero in a meridional calculation is not an ocean-current location. | P2 | Do not create a route or state intersection from it. Report geometry stays null; prospective SVG is explicitly scalar. |
| 8 | CHART | Lancaster intrusion and meanders add path length that latitude separation cannot recover. | P2 | Keep these exclusions visible and retain existing editorial route independently. Protocol and SVG state this. |
| 9 | CHART | The source's confinement within 100 km of the coast is not two transverse current edges. | P2 | Do not admit a new width or band. Existing Baffin widths remain untouched. |
| 10 | BEACON | A floor could be repeated as a published current length without nearby qualification. | P2 | Use conditional geographic floor and unranked in the value line; retain null source-reported and whole-current lengths. |
| 11 | BEACON | Six decimal kilometres support arithmetic reproduction, not physical accuracy. | P2 | Present rounded floor and one-decimal diagnostic distances; report arithmetic tolerance explicitly as non-physical. |
| 12 | BEACON | Source-stage success does not mean a delivered query/card feature. | P2 | Keep status not-working-dataset-admission and false admission flag; explain next delivery stage. |
| 13 | HARBOR | Prospective SVG has title/description and numeric text but has not yet been rendered at phone size. | P2 | Require actual narrow-screen image and equivalent HTML/data text before delivery; unresolved. |
| 14 | HARBOR | Meaning must survive loss of color and pointer interaction. | P3 | Value, evidence class, study context and caveats are text; accessible links and keyboard navigation remain required in the future card integration. |
| 15 | HARBOR | Scenarios are data, not an animation of seasonal change. | P2 | Provide keyboard-accessible scenario query/table and do not animate a seasonal envelope. Integration pending. |
| 16 | KEEL | Reusing the existing WGS84 operator preserves arithmetic convention, but needs an independent check. | P3 | Synthetic tests and runtime independently integrate meridional curvature for nominal and all nine scenarios; no actual source calculation before freeze. |
| 17 | KEEL | Dependency or source mutations after declaration could invalidate a calculation. | P2 | Pin operator/tests/protocol/facts/acquisition/environment specification/review; compare every byte to exact pre-execution Git commit. Implemented in freeze guard. |
| 18 | KEEL | A successful unit test is narrower than native/WASM and browser parity. | P2 | Preserve all sequential integration gates. Synthetic unit results do not close them. |
| 19 | LOGBOOK | No Baffin measurement is currently admitted or delivered; publication without preservation and full integration evidence would be false. | P1 | Blocks working delivery/release. Finish arithmetic, source preservation, native/WASM validation and actual card/query/browser checks before admitting. Source-stage freeze/calculation may proceed. |
| 20 | LOGBOOK | Remote Davidson validation is still active on its own pinned source head. | P2 | Commit next source work locally and hold remote publication until that run is terminal. Do not replace its artifacts or receipts. |
| 21 | LOGBOOK | General offline reproduction still has an unresolved source-acquisition gate. | P2 | Retain the Rotschi 1972 HTTP403 status; no skip or replacement to obtain a green release. No main merge or scientific release is authorized by this review. |

## Synthesis

Roles reviewed: 7. P1 blockers: 1; P2 issues: 17; P3 notes: 3.
Verdict: **NEEDS-WORK for admission/delivery**. Source-stage arithmetic may
proceed after the prospective files, tests and preflight are frozen in Git.

Top finding: 19, missing integrated working-delivery evidence. CURRENT,
CHART and BEACON agree that a conditional latitude floor must not become a
measured whole-current length. SOUNDER and KEEL agree on immutable inputs and
an independently verified calculation. HARBOR and LOGBOOK require actual
accessible delivery evidence before publication.

## Three amendments applied or required

1. Source review, report and SVG preserve historical naming scope, summer
   context and the distinction between conditional floor and measured length.
2. Freeze guard compares exact committed bytes; independent integration checks
   all nine scenarios and rounding. Subsequent corrections require a new version.
3. Carry findings 13, 15, 18 and 19 into a separate delivery receipt after actual
   verification. Do not edit this prospective review to retrospectively close
   them. Original PDFs and previous scientific products remain unchanged.
