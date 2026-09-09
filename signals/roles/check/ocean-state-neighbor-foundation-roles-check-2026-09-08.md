---
skill: roles-check
topic: ocean-state-neighbor-foundation
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED
---

# Roles check — Ocean-State Neighbor Foundation

**Artifact type:** source-backed topology analysis, bathymetric method
prototype, interactive scientific atlas extension, evidence receipts, guide,
and frozen future-pilot rule

**Source commit:** `80a18986a1913558a52021571a0e560a86276b8e`
plus reviewed working-tree changes

**Core reviewed SHA-256:**

- adjacency acquisition: `2C52AE176F94321D0667BA91F1AE2531B0DF12EE2ED72558AAFBE276FA8EB35B`
- adjacency graph: `F835B46D5BA7B4385B033F41CAB7AAF459E856BF4A4BDE803A558C1B97625F3F`
- rejected contacts: `8F85BEF12A8083D663C1382E94F72CE0CB49D072F4D2BD3F7DFE556EEF094A27`
- hypsometry acquisition: `865EC0933358E2CFA55BD7F9A06178678AEFDC8E25131F12CA8DD5C2018A49AB`
- hypsometry prototype: `8D1E5C7CBD480F379A895A097258B0E7B7F58B9F44E15EE95A882A7DFFF933E3`
- browser logic: `13A9CA676A793FD81CD6EF0DF8D195B88BC5CFB3535E982ADF265B2AA4506A38`
- browser document: `BBFD9C62DA6E3A37FF3885BC73C5C047D8E97F9C50A9B1998DE25C0F947BC153`
- guide: `22118D079CF2701E9321A235633FA111161A363149A057E897E539009627DD10`
- pilot-selection plan: `0A0820DAEB0A85F31C731077C4C72914970744293FEF3D13FBA9F167F716A701`
- machine pilot rule: `24E34982540513C188440129D7D60C431826CC6D031ACF8205916D32C023B4E4`

## Role selection

CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, and LOGBOOK apply because the
slice introduces a scientific relationship graph, sampled depth curves,
source admissions, interactive views, accessible equivalents, deterministic
tests, and repository claims. ORBIT does not apply because the slice makes no
Earth–gas-giant transfer claim; any later planetary accounts require a
separate mechanism-level review.

## Findings

### CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Shared source geometry could be mistaken for a physical barrier or measured interaction. | P2 | Graph schema / browser / guide | Keep every physical class `undetermined_reference_edge` and place the non-wall, non-gateway, non-exchange boundary beside map and table. **Resolved.** |
| 2 | Extruding surface biogeographic footprints into depth curves could imply full-column ecological identity. | P2 | Hypsometry schema / guide | State that the curves are comparison-column bathymetry and do not establish ecology, water masses, heat, transport, or vertical coherence. **Resolved.** |
| 3 | The next pilot is selected by custody, grid support, controls, and numerics without inspecting transport outcomes. | P3 | Pilot-selection rule | Preserve null selection and prohibit dramatic-result ranking. **Accepted.** |

### SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Repeated WFS responses have different byte hashes despite identical geometry on the complete committed grid. | P2 | Adjacency source receipt | Record both raw response identity and normalized repaired-geometry identity; claim only 1,036,800-cell compatibility, not byte/native-coordinate identity. **Resolved.** |
| 2 | New receipts initially lacked complete reusable citation identifiers. | P2 | Source receipts | Add Marine Regions citation and consultation date, GEBCO DOI, license, query, acquisition time, response size/hash, headers, transformation, and output checksums. **Resolved.** |
| 3 | The 0.5° comparison is explicitly grid sensitivity rather than observational or bathymetric uncertainty. | P3 | Hypsometry method | Preserve that evidence boundary and source-quality limitations. **Accepted.** |

### CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Raster coloring cannot faithfully establish exact source topology; one short accepted edge is invisible at 0.25°. | P2 | Neighbor map | Derive identity from exact polygons, encode the raster only as display support, and expose `CNRY--MEDI` in the border table despite its absent cell contact. **Resolved.** |
| 2 | A continuous curve without declared axes and comparison grammar can read as a water profile. | P2 | Hypsometry view | Label percentage and depth axes, distinguish solid 0.25° from dashed 0.5°, and call it an area-weighted seafloor-depth quantile curve. **Resolved.** |
| 3 | Oceanic Mollweide remains a consistent equal-area orientation frame while exact graph evidence stays in the passports. | P3 | Workbench | Retain projection and sampling limitations near the map. **Accepted.** |

### BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Neighbor” may be repeated publicly as ecological interaction rather than shared geometry. | P2 | Heading / guide | Define three steps—shared edge, motion screen, measured exchange—and state which one the result earns. **Resolved.** |
| 2 | Economic-account language could imply sovereign, closed, or homogeneous ocean territories. | P2 | Guide / research program | Describe permeable accounting units and separate inventory, flow, change, balance, relationship, shock, and revision. **Resolved.** |
| 3 | The short public message is accurate: the states can be compared through time even when water crosses them. | P3 | Guide | Keep the analogy's limits in the same reading path. **Accepted.** |

### HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Neighbor color and curve line style cannot be the sole carriers of map or sensitivity meaning. | P2 | Workbench | Provide live summaries, keyboard province controls, border-passport table, quantile table, explicit legends, and data downloads. **Resolved.** |
| 2 | Real-browser inspection found that every render removed `#svg-desc` before updating it, causing a runtime exception and loss of the SVG description. | P2 | Column renderer | Recreate title and description inside the render root, add a static regression token, and repeat desktop/mobile browser checks. **Resolved.** |
| 3 | At a true 390 px viewport, document width equals client width and state changes update polite regions without programmatic focus movement. | P3 | Browser verification | Preserve narrow reflow and the no-forced-focus contract. **Accepted.** |

### KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The first live WFS request ended with an incomplete chunked response. | P2 | Network acquisition | Add three bounded retries and retain acquisition outside the default offline gate. **Resolved.** |
| 2 | Initial edge length used an unpinned new `pyproj` dependency. | P2 | Adjacency acquisition | Replace it with tested great-circle segments using OSW's already declared spherical Earth radius. **Resolved.** |
| 3 | Synthetic edge/point/seam tests, artifact invariants, checksum linkage, source compatibility, browser payload equality, JavaScript syntax, and real-browser error capture cover the new failure surface. | P3 | Verification | Keep live downloads explicit and compact derivatives committed. **Accepted.** |

### LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New quantitative claims would drift if only the browser or prose were updated. | P2 | Repository record | Register D57-D58 and update roadmap, README, method, guide index, history, plans, receipts, generated payloads, and tests together. **Resolved.** |
| 2 | Completing the first slice could be mistaken for authorizing transport, rezoning, publication, commit, or push. | P2 | Program status / pilot rule | Mark only the bounded foundation active and keep later acquisition, conclusions, release, and Git operations behind separate owner gates. **Resolved.** |
| 3 | The new source receipts preserve licenses and citations without committing provider payloads or local machine paths. | P3 | Source custody | Retain the compact-derivative posture. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED

Top finding: an exact shared province edge is a reproducible relationship in
reference geography, but it remains one full evidence stage below motion and
two stages below measured volume or heat exchange.

Cross-role consensus: the graph earns scientific value because exact topology,
raster support, physical interpretation, source identity, uncertainty, and
accessible explanation remain separate and mutually traceable.
```

## Amendments

1. Separated exact polygon topology from sampled-grid support, preserved ten
   rejected point contacts, and exposed the short source-real edge that the
   display grid misses.
2. Added normalized geometry identity, complete citations, source/output
   checksums, bounded network retries, spherical edge-length calculation, six
   frozen archetypes, and explicit 0.25°/0.5° sensitivity semantics.
3. Added the neighbor and continuous-depth views with complete tables, fixed
   the render-time SVG-description failure, verified true 390 px reflow, and
   froze a result-blind exchange-pilot selection rule.

No external scientific peer review is implied. This verdict closes only the
reviewed neighbor/hypsometry foundation; transport, zoning, public promotion,
commit, and push remain unauthorized.
