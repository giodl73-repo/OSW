---
skill: roles-check
topic: gebco-province-seed-depths
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — GEBCO province-seed depths

**Artifact type:** external scientific-data acquisition, derived reference
table, and interactive cartographic layer

**Source commit:** `0a3d72e09b2d2cc8b4c6afe3bceee4e52fb36d37`

**Reviewed artifact SHA-256:**

- raw elevation/TID receipt: `5E825660417938C55B413F2B7E7A53E0D73B0CF3CC14A1BB65FF15B3F10E2EB7`
- derived 56-cell table: `7B39D13501F9CB1BCB5DB2106DC5D969B7CC361440945EABBA0F84263CE8651A`
- summary: `2528181F08FA3EBE72896A82A15C9318EC2C2EC177EB12D4E30A4EB7C6D1595B`
- browser data: `9B2CBE4EB68D9613FABA063AE0000ACD0A992B9790DBB0EDEFD866CC640ABF2C`
- browser logic: `E575FA4E59FF435A712EF21A5D6C0D0110626203D4FB5EE4BE5B458712C641CE`
- browser HTML: `66228D19983AE4F21C1EAEC801B6E318E62B08C1B2380B673483BB68391EB576`

All eight native roles review this stage because it admits external data,
classifies source quality, changes the main visualization, and creates a new
public claim about vertical reach.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One bathymetric value cannot establish water-mass structure, motion, or heat transport. | P2 | Viewer boundary | Restrict it to geometric depth and depth-band reach. **Resolved.** |
| 2 | A seed deeper than a band proves only local vertical availability, not physical occupation by a regime. | P2 | Live result | Use spans/truncates/does-not-reach for reference bands and keep regimes hypothetical. **Resolved.** |
| 3 | Bathymetric truncation now changes the reference stack without changing its interval definitions. | P3 | Column rendering | Preserve that distinction when measured water properties arrive. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “GEBCO cell” does not mean direct sounding; source type varies by cell. | P2 | TID layer | Acquire the matching TID cell and expose its code and definition. **Resolved.** |
| 2 | Remote values need byte-level custody and exact spatial queries. | P2 | Source receipt | Preserve every elevation/TID URL, ASCII response, coordinate, release, DOI, and checksum. **Resolved.** |
| 3 | GEBCO assumes mean sea level but notes heterogeneous inputs and shallow-water datum exceptions. | P3 | Source register/method | Retain this limitation and prohibit navigational use. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A selected-seed column could look like a province cross-section. | P2 | SVG title/status | Label it “selected seed cell,” show exact coordinates, and repeat the single-cell boundary. **Resolved.** |
| 2 | Dry approximate seeds could be silently moved to produce prettier ocean columns. | P2 | Non-wet rendering | Render a distinct non-wet column with elevation and “retained · not moved.” **Resolved.** |
| 3 | Side-by-side measured-cell and teaching-archetype labels let readers distinguish evidence classes. | P3 | Four-column view | Keep observed and conceptual encodings explicitly named. **Accepted.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Calling all depths “measured” would overstate interpolated and predicted cells. | P2 | Public wording | Say “GEBCO seed cell” and give the TID provenance phrase. **Resolved.** |
| 2 | The surprising three dry results need explanation rather than concealment. | P2 | Method/history | Explain that they falsify the assumption that display seeds are validated ocean samples. **Resolved.** |
| 3 | “Spans / truncated part / does not reach” is a clear vocabulary for local band geometry. | P3 | Live output | Reuse this language in future section summaries. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source-quality class cannot be conveyed only by styling. | P2 | Status/readout | Report TID code, class, and definition in text for every selected province. **Resolved.** |
| 2 | Non-wet status needs an equivalent nonvisual result. | P2 | Live output | Announce elevation, no occupancy, and no offshore relocation. **Resolved.** |
| 3 | Band selection remains keyboard operable and the live region explains the measured-cell relation. | P3 | Interaction | Retain no-focus-steal behavior. **Accepted.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Default tests must not depend on 112 remote OPeNDAP calls. | P2 | Pipeline | Separate explicit acquisition from deterministic offline derivation. **Resolved.** |
| 2 | Elevation and TID grids could be sampled at misaligned cells. | P2 | Acquisition | Use identical indices and fail if returned latitude/longitude coordinates differ. **Resolved.** |
| 3 | Tests verify 56 receipts, hashes, coordinate tolerance, 53/3 wet split, TID distribution, and deterministic outputs. | P3 | Verification | Keep source refresh explicit and rerun the full suite after changes. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source D5 still described GEBCO as candidate-only. | P2 | Source register | Promote only the bounded 56-cell screen and record DOI, access, result, and exclusions. **Resolved.** |
| 2 | The workbench method still said no GEBCO bytes were present. | P2 | Method | Document acquisition/rebuild commands, attribution, TID counts, and next gate. **Resolved.** |
| 3 | History and roadmap distinguish the new single-cell evidence from province-wide completion. | P3 | Project record | Commit source receipt, derived products, code, tests, and review together. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth bathymetry supplies no lower-boundary measurement for a gas giant. | P2 | Scope | Grant no planetary transfer from GEBCO integration. **Resolved by omission and Guide 15 boundary.** |
| 2 | A depth-band reach result cannot be treated as a planetary pressure-layer analogue. | P2 | Interpretation | Require a separately defined planetary vertical coordinate and boundary model. **Resolved.** |
| 3 | The evidence-discipline—coordinate plus provenance plus uncertainty—can transfer methodologically. | P3 | Future work | Reapply the contract rather than the Earth cutoffs. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: a GEBCO grid value is not automatically a direct sounding and one
seed cell is not a province.

Cross-role consensus: retain dry seeds, expose matching TID provenance, bind
every remote response, and limit the claim to local depth-band reach.
```

All sixteen P2 findings are resolved for the 56-cell screen. The remaining
condition is a forward evidence gate: province-wide depth coverage requires
exact licensed horizontal geometry and a controlled multi-cell intersection;
this artifact cannot be aggregated as if it already supplied either.

## Amendments

1. Added 56 matching GEBCO TID queries, coordinate-alignment failures, source
   definitions, checksums, and a visible four-class quality summary.
2. Added a measured seed column with exact coordinates and explicit complete /
   truncated / absent band reach; retained three non-wet seeds unchanged.
3. Updated source registration, method, history, roadmap, deterministic builds,
   and offline tests while keeping province-scale and physical claims blocked.

Fixed-point decision: approve the GEBCO_2026 province-seed screen as bounded
single-cell reference evidence. No province mean, profile, occupancy, volume,
navigation, physical regime, heat, transport, planetary, deployment, or remote
publication claim is authorized by this review.
