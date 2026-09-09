---
skill: roles-check
topic: ocean-state-hydrography-stage3
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean-state hydrography Stage 3

**Artifact type:** regional scientific-data receipt, explanatory guide, and
interactive evidence workbench

**Reviewed artifact SHA-256 values**

- acquisition: `3216C6810A5AF138AE0B1471D8B41F915B4B052DB95D1D7EFF9B8B4108765DD5`
- research receipt: `952B5A91D305B53781028D407A4198F5A96BE0C422DD701C13576DCAAA8C8149`
- browser HTML: `FCF42845A4E276DBCAE24D4036A6AFC21A8DF51DC0876836467F192144C90737`
- browser logic: `E7C108568F387509D2C8B7E819EC2A99F566DF864686A8EC43F11EB274708E31`
- browser payload: `4D3749031EA16376FCCFDC6AB343EEEEC26CCAF73EEC810FC11589BE89A9CBA1`
- primary CSS: `7E250837E0D4F0727BDFE28ECBBD821C4E59F6AFB6E99F494FA577BA07048E04`
- responsive CSS: `6AC937D3470825AA67F04E1E8C2B7F21E9266F9D232751552B2C082ED4F09664`

ORBIT is not selected for this gate because Stage 3 makes no planetary
comparison or transfer claim. Its absence cannot be read as approval for a
gas-giant analogy.

## Findings

### CURRENT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A Drake-only sample initially painted the entire global footprint of every supported province. | P2 | Clip all property and support color to the native coordinate extent and leave the rest out of domain. **Resolved.** |
| 2 | A province contrast could be mistaken for a measured front or exchange. | P2 | Label every comparison descriptive and keep autocorrelation and multiple-comparison limits adjacent. **Resolved.** |
| 3 | Four seasonal snapshots reveal within-year contrasts but not climate or interannual persistence. | P3 | Preserve the explicit four-month, one-year support in every downstream use. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A mutable WFS response cannot be identified only by its URL. | P2 | Bind acquisition time, response hash, normalized-geometry hash, provider citation, and license. **Resolved.** |
| 2 | Reanalysis files and their mesh must remain independently receipted. | P2 | Record each local path, byte hash, valid time, provider, DOI, and license. **Resolved.** |
| 3 | The browser derivative could drift from the scientific receipt. | P2 | Test exact JSON equality between `hydrography.js` and the committed research artifact. **Resolved.** |

### CHART

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Equal province fill outside the sampled grid would visually overstate spatial support. | P2 | Use cell-level support inside the declared extent and a distinct quiet out-of-domain fill elsewhere. **Resolved.** |
| 2 | Temperature and coverage need separate visual questions. | P2 | Pair two same-projection maps and never encode coverage as temperature saturation. **Resolved.** |
| 3 | Six state footprints and a small regional sample remain readable in Oceanic Mollweide, but this is a support map rather than native-grid geometry. | P3 | Keep coordinates and exact counts in the receipt and avoid claiming cartographic measurement from pixels. **Accepted.** |

### BEACON

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “Heat inventory” would substitute temperature for energy. | P2 | Use “temperature distribution” and repeat that heat content is unsupported. **Resolved.** |
| 2 | “Complete coverage” could be heard as global or observational completeness. | P2 | Qualify it as complete expected native samples for the selected regional model passport. **Resolved.** |
| 3 | The workbench opens with the question a visitor can answer, while the evidence boundary is visible before interaction. | P3 | Retain the border/question framing as later stages become available. **Accepted.** |

### HARBOR

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Canvas maps alone would exclude nonvisual readers. | P2 | Provide dynamic ARIA labels, a live passport summary, and a complete six-state table. **Resolved.** |
| 2 | Wide comparison tables can force a whole mobile page wider than its viewport. | P2 | Constrain the page and retain horizontal scrolling inside the table wrapper; verify a 390 × 844 emulated viewport. **Resolved.** |
| 3 | Province, depth, and month state must remain recoverable and shareable. | P3 | Keep labeled native controls, visible focus, and URL state with a deterministic reset. **Accepted.** |

### KEEL

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Generated counts need invariants, not visual inspection alone. | P2 | Test 96 passports, 128 contrasts, zero assignment overlaps, exact extent, evidence class, ordering, and uncertainty status. **Resolved.** |
| 2 | A new browser surface could bypass CI syntax checks. | P2 | Add `exchange/app.js` to the workflow's Node syntax gate. **Resolved.** |
| 3 | Remote acquisition should not make default verification network-dependent. | P3 | Keep acquisition explicit and run offline tests against the committed derivative. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Stage 3 implementation could remain invisible in the canonical project record. | P2 | Update README, roadmap, history, guide index, source register, and program status together. **Resolved.** |
| 2 | The original first-slice authorization text conflicts with the owner's later full-program goal. | P2 | Record the later activation while retaining publication and claim-scope gates. **Resolved.** |
| 3 | Stage completion could be misread as authorization for exchange results. | P3 | Enable only Contents and keep Exchange, Stability, Events, and Decisions visibly disabled until their own gates pass. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED-WITH-CONDITIONS
```

All 14 P2 findings are repaired in the reviewed Stage 3 artifacts. The
remaining conditions define the boundary for Stage 4: this is a regional,
temperature-only, assimilative-reanalysis contents screen; it is not heat
content, observation-only evidence, a front, exchange, transport, or zoning
authority.

The gate passes only with the focused offline tests, full analysis suite,
JavaScript syntax checks, diff check, and 390-pixel browser metrics passing on
the final working tree. Stage 4 must begin from its frozen selection rule and
must not choose a boundary from the contrast results above.
