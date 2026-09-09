---
skill: roles-check
topic: ocean-column-volume-ledger
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean Column water-volume ledger

**Artifact type:** scientific derivation, machine-readable reference layer,
interactive cartographic profile, and public explanation

**Source commit:** `82cfcc8`

**Reviewed artifact SHA-256:**

- acquisition and derivation: `D582B7AEA0F556D78C51242C90106A213DB21F5CDD33B9CC11104AED7D756829`
- source receipt: `1FC5A56AFDD0C7EA676BF2AADB7F0168E2CDD0169D6394865B1EFDFED22A25F8`
- research payload: `54D8AA0E09FED51709D298474C97089C1E0123D43306E32E15FEBE7D15FAC798`
- browser payload: `B3D8AC008DBD579398B84DC44C74A6514C0343FA5489D899C03E9D5699692233`
- browser logic: `4FD958F2B1BE14873F0C83DC225DB9F926B1F75BA894C9C542E0B5263A8F047B`
- browser HTML: `BF20C4FFE1A11B572CF63EAAD3C55F578641A9462F02C8CF9FB9DF89709CFEB3`

## Role selection

All eight OSW roles apply. CURRENT reviews the physical meaning of integrated
volume; SOUNDER reviews the GEBCO and geometry lineage; CHART reviews the map
and paired profiles; BEACON reviews the public claim; HARBOR reviews equivalent
mode access; KEEL reviews numerical and offline reproducibility; LOGBOOK reviews
source/status alignment; ORBIT guards against exporting Earth-specific depth
and seafloor assumptions to gas giants.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Area × bathymetry-truncated thickness estimates reference water volume, not heat content, ecological occupancy, or transport. | P2 | Scientific interpretation | State those exclusions beside the profile and in the payload boundary. **Resolved.** |
| 2 | Fixed pelagic depth bands are conventional address intervals rather than physical discontinuities. | P2 | Volume bands | Retain the edition-1 bounds and describe the result as a ledger, not natural ocean layers. **Resolved.** |
| 3 | The volume calculation is time-independent except for chosen geometry, bathymetry, mask, and sea/ice convention. | P3 | Temporal support | Do not infer present-day circulation or transient storage from this reference volume. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every volume must inherit the exact Longhurst, GEBCO elevation, grid, stride, datum caveat, and source checksum already recorded. | P2 | Provenance | Generate the volume inside the receipted acquisition rather than a detached spreadsheet. **Resolved.** |
| 2 | Coastal center assignment, 2,772 wet seam cells, 5,519 non-wet polygon centers, and the ice-surface product limit province values. | P2 | Missing/mask handling | Preserve those diagnostics and name the prismatic and partial-cell omissions. **Resolved.** |
| 3 | The USGS 1.338-billion-km³ value is independent context, not a tuning target or validation dataset. | P3 | Cross-check | Store the comparison, URL, difference, and non-calibration interpretation explicitly. **Resolved.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Water-volume share and seafloor-reaching area answer different questions despite using the same five colors. | P2 | Profile encoding | Give them an explicit two-state control and change the profile title, legend percentages, and text together. **Resolved.** |
| 2 | The geographic canvas still maps static surface geometry; it must not appear volumetrically shaded. | P2 | Mollweide map | Keep the map’s province/biome grammar stable and confine quantitative volume encoding to the labeled bar. **Resolved.** |
| 3 | Kilometer-scale coastal cells do not warrant decimals in public cubic-kilometre labels. | P3 | Numerical typography | Retain machine precision in JSON but round browser province volumes to the nearest 1,000 km³ and global prose to 1.338 billion. **Resolved.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Close agreement with a familiar global total could be repeated as “proof” that every province volume is correct. | P2 | Public claim | Call the 0.0258% agreement a scale check and explicitly deny calibration or provincial validation. **Resolved.** |
| 2 | “Actual water volume” would overstate a sampled prismatic estimate. | P2 | Viewer copy | Use “sampled water-volume ledger,” “approximately,” and the precision boundary consistently. **Resolved.** |
| 3 | The core insight is that a surface partition can gain an auditable vertical reference without becoming a water mass. | P3 | Narrative | Put that distinction in the history, guide, method, roadmap, and viewer note. **Resolved.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A changing stacked color bar alone does not expose which quantity is active. | P2 | Mode change | Update a visible live profile title and the full textual summary whenever the mode changes. **Resolved.** |
| 2 | Profile selection must work without a pointer and preserve direct-link state. | P2 | Controls | Use native buttons, `aria-pressed`, keyboard behavior, and a `profile` URL parameter. **Resolved.** |
| 3 | Older-only NPSE/OCAL selections cannot inherit a stale volume label or distribution. | P3 | Missing-edition state | Clear the bar and announce that the Version 4 depth profile is unavailable. **Resolved.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Band integration needs a small exact fixture that exercises shallow truncation and all five bands. | P2 | Unit validation | Test three cells at 90, 500, and 7,000 m against hand-computed area × thickness totals. **Resolved.** |
| 2 | Aggregate drift could pass broad range checks while changing the published story. | P2 | Regression gate | Pin the rounded global total, five fractions, per-province closure, and research/browser byte-equivalent payload. **Resolved.** |
| 3 | Default validation must remain offline even though regeneration downloads WFS and OPeNDAP products. | P3 | Build boundary | Commit generated artifacts and keep source refresh an explicit optional-dependency command. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The new quantitative claim needs a distinct source-register identity while inheriting D52/D5 limitations. | P2 | Source register | Add D53 with method, result, independent context, and limitations. **Resolved.** |
| 2 | The method, guide, roadmap, history, landing page, and viewer must report the same evidence class. | P2 | Repository record | Update them together and keep the public branch/release state unchanged. **Resolved.** |
| 3 | This private-preview work does not authorize remote publication. | P3 | Release state | Commit locally after verification; do not push or promote Atlas 07. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Solid-seafloor truncation and metre-based pelagic bands do not transfer directly to deep gas-giant atmospheres. | P2 | Planetary boundary | Keep the volume ledger Earth-only. **Resolved.** |
| 2 | Similar vertical fractions would not establish analogous stratification, heat flow, or jets on Jupiter or Saturn. | P2 | Analogy | Require pressure/mass coordinates, compressibility, forcing, and lower-boundary assumptions before comparison. **Accepted.** |
| 3 | The transferable idea is an exhaustive declared address plus separately diagnosed dynamic overlays. | P3 | Comparative method | Transfer the evidence architecture, not the geographic polygons or band cutoffs. **Accepted.** |

## Synthesis

Roles reviewed: 8
P1 blockers: 0 | P2 issues: 16 | P3 notes: 8

**Verdict: APPROVED-WITH-CONDITIONS**

**Top finding:** Global agreement is an excellent scale check but cannot
validate any individual province volume.

**Cross-role consensus:** CURRENT, SOUNDER, CHART, and BEACON agree that the
0.25° prismatic result must remain visibly approximate and separate from
ecological occupancy, physical layers, heat content, and transport.

## Amendments

1. Round public volume labels while retaining deterministic values in the
   machine-readable artifact. **Applied in `column/app.js` and public prose.**
2. Make the profile quantity redundant in control state, visible title, live
   summary, URL, and accessible name. **Applied in the workbench.**
3. Add a non-calibrating independent global scale check and prevent it from
   being presented as province validation. **Applied in D53, the payload,
   method documentation, and public boundary copy.**

The stage may be committed to the private-preview branch after full tests and
final diff checks. Public promotion remains separately gated, and the 54/56
horizontal-edition decision remains open.
