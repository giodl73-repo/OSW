---
skill: roles-check
topic: gebco-province-seed-neighborhoods
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — GEBCO province-seed neighborhoods

**Artifact type:** external scientific-data acquisition, derived local-grid
reference, and interactive cartographic layer

**Source commit:** `0075d87430a70636faf821b10cd59b8f023e9584`

**Reviewed artifact SHA-256:**

- raw elevation/TID receipt: `B0434C43A34D402E629731889D6258FB780C5DF7CE28D2383AE20CA02D25809B`
- derived 56-neighborhood payload: `1568B92A98526993E5AA62DE7B054D3A74E3FAF5710C487CD7054DA00B5325AE`
- summary: `628B61A05E7A51FFBDDA7CE23ACC0EBA3CBD16CAA2BA74C8A2969BA7C9A21730`
- browser data: `4CD0CEA61524F648494208A1DFBE3224B097E1E624415B023D4DC14B62327A01`
- browser logic: `D7226BBDE6A82E564A1E043872CCA7DA5D0FC4CE5E6E81F0F536FE6B6D588E99`
- browser HTML: `8D0B7F4F3E20A5A13EB9D9ADD8CE5597AE1D37D0F409EB6F5AAAA6AFEEA637EC`

All eight native roles review this stage because it admits a much larger
external sample, adds a spatial display, classifies source quality, and could
otherwise be mistaken for province-scale evidence.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Local topography does not identify a current, water mass, heat reservoir, or regime boundary. | P2 | Viewer interpretation | Label the display as seafloor shape and keep physical overlays separate. **Resolved.** |
| 2 | A seafloor depth class means only the deepest reference band locally reachable in the water column. | P2 | Depth mode | Do not describe the colored cells as occupied depth zones. **Resolved.** |
| 3 | Neighborhood bathymetry is useful future boundary evidence for flow studies but supplies no motion measurement itself. | P3 | Research sequence | Join it only to separately sourced velocity or hydrographic evidence. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Sixty-thousand values require the same custody as the earlier point screen. | P2 | Source receipt | Preserve all 112 exact query URLs, ASCII responses, checksums, release, DOI, and access time. **Resolved.** |
| 2 | Elevation and provenance are meaningful together only when their returned coordinate arrays match. | P2 | Acquisition/build | Query identical indices and fail on coordinate disagreement. **Resolved.** |
| 3 | GEBCO source type remains heterogeneous, its vertical reference has stated caveats, and the product is not for navigation. | P3 | Source register/method | Retain TID, datum, quality, and non-navigation qualifications. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An 8° longitude-latitude window is not equal-area and east-west cell scale varies with latitude. | P2 | Local map | State the grid geometry beside the map and avoid area comparisons. **Resolved.** |
| 2 | A categorical seafloor-band map could be read as continuous measured temperature or water-mass data. | P2 | Legend/title | Call the mode “seafloor depth” and define each swatch as a depth class reached. **Resolved.** |
| 3 | Land, bathymetric class, provenance class, and the center seed need distinct visual marks. | P3 | Rendering | Keep land separate, switch modes explicitly, and retain the gold seed outline. **Accepted.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Neighborhood” could imply adjacency inside an OSW province rather than a window around its approximate label seed. | P2 | Public wording | Repeatedly say “8° × 8° seed neighborhood” and “not province geometry.” **Resolved.** |
| 2 | Counts of regular geographic cells could be mistaken for percentages of ocean area. | P2 | Live summary | Say “cell counts are not area” and report wet/land samples, not coverage percentage. **Resolved.** |
| 3 | “Seafloor depth” and “source type” are clearer mode names than specialist abbreviations alone. | P3 | Controls | Keep the plain-language names and explain TID in the legend. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A canvas-only neighborhood would hide the result from nonvisual users. | P2 | Equivalent content | Mirror bounds, counts, depth range, and source distribution in a live text summary and canvas label. **Resolved.** |
| 2 | Source categories cannot depend on color alone. | P2 | Source mode | Provide a textual legend and exact class counts for the selected neighborhood. **Resolved.** |
| 3 | Mode changes must remain keyboard operable and preserve selection context. | P3 | Interaction | Use native buttons, visible state, and no focus stealing. **Accepted.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Routine builds and tests must not depend on 112 remote OPeNDAP requests. | P2 | Pipeline | Separate explicit concurrent acquisition from deterministic offline derivation. **Resolved.** |
| 2 | Shape, spacing, seam, parsing, or aggregation errors could silently distort the mosaics. | P2 | Validation | Assert 56 paired 33×33 arrays, 0.25° spacing, aligned coordinates, checksums, totals, and deterministic output. **Resolved.** |
| 3 | The committed payload contains 60,984 paired samples and remains practical for a static reference-lab viewer. | P3 | Browser delivery | Reassess tiling or compression before materially increasing spatial extent or resolution. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new evidence would be untraceable if only the browser payload were committed. | P2 | Project record | Commit source receipt, derived product, summary, acquisition/build scripts, tests, and review together. **Resolved.** |
| 2 | Documentation could accidentally promote the sample windows into completed province coverage. | P2 | Source register/roadmap/guide | Record their bounded result and retain exact province geometry as the next gate. **Resolved.** |
| 3 | History now records the 56-window result, including 29 fully wet and 27 mixed windows, without a release claim. | P3 | History | Keep deployment and remote publication outside this commit. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth bathymetric neighborhoods cannot be transferred as structures on gas giants. | P2 | Scope | Make no planetary inference from this integration. **Resolved by omission and Guide 15 boundary.** |
| 2 | A regular geographic seabed mosaic is not an analogue of a pressure surface or deep atmospheric boundary. | P2 | Interpretation | Require a planet-specific coordinate and observation model before comparison. **Resolved.** |
| 3 | The transferable element is methodological: bind every spatial sample to provenance and qualify interpolation. | P3 | Future comparison | Transfer the evidence contract, not the terrestrial geometry. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: an 8° seed neighborhood is neither an OSW province nor an
equal-area sample of one.

Cross-role consensus: preserve exact paired elevation/TID custody, expose
source class, supply equivalent text, and limit the result to local seafloor
context around approximate seeds.
```

All sixteen P2 findings are resolved for this bounded neighborhood screen. The
remaining condition is the same forward evidence gate at a more informed
scale: province-wide depth coverage requires exact licensed province geometry
and a controlled multi-cell intersection. These windows cannot be aggregated
as if they already supply province area, occupancy, volume, motion, or heat.

## Amendments

1. Added 56 paired 33×33 GEBCO elevation/TID neighborhoods at 0.25° spacing,
   retaining exact requests, responses, hashes, coordinates, and definitions.
2. Added switchable seafloor-depth and source-type local maps with a seed
   marker, explicit land class, legends, bounds, sample counts, and live text.
3. Updated source registration, guide, history, roadmap, deterministic build,
   and offline tests while keeping province-scale and physical claims blocked.

Fixed-point decision: approve the GEBCO_2026 8° × 8° province-seed
neighborhoods as bounded local reference evidence. No province geometry, area,
mean, profile, occupancy, volume, navigation, current, water mass, heat,
transport, planetary, deployment, or remote publication claim is authorized
by this review.
