---
skill: roles-check
topic: selected-depth-band-volume-map
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Selected depth-band volume map

**Artifact type:** interactive scientific cartography, horizontal × vertical
reference-address view, quantitative ranking, and selected-state passport

**Source commit:** `eda5b22`

**Reviewed artifact SHA-256:**

- browser logic: `466FDB8FF2E80D166B1D8D3177B12FAE0772010B9C540A5567379192B36730FC`
- browser HTML: `6807E9B630ABCF73FC547D0CC634B5C74C044987AF77862AA8C02EB8844FA42C`
- scientific tests: `FF0D408853851FC75B7380BC304013DDB585C21A611AF33A44B890EDE7347861`
- viewer tests: `AB96DB855AA3288A6BD80DDE4AF7CD1C9879303BBCDCF6D5DF921CC47802ADD9`
- workbench method: `8BD76952E41E2856269B4BC66A3499EBBD8C10B900B2D7D1DE1D3D793F1CA2D8`
- address guide: `D4C06047B6266564FA2E108DD430CC9169920810D879476AC085FC916B40132F`

## Role selection

All eight OSW roles apply. This view couples a user-selected vertical band to
a global quantitative map, changes eligibility by depth, adds three ratios to
the passport, and could otherwise imply ecological occupancy, heat, physical
absence, or a transferable planetary depth coordinate.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Water volume inside a fixed depth address is not heat content, transport, residence, or water-mass occupancy. | P2 | Scientific meaning | Call it selected-band reference volume and retain those exclusions beside the map. **Resolved.** |
| 2 | “Share of state” and “share of global band” use different denominators and answer different questions. | P2 | Passport | Label both denominators explicitly and never merge them into one percentage. **Resolved.** |
| 3 | Changing the selected band changes the mapped support but not the static province boundaries. | P3 | Interaction model | Rerender ranks and eligibility while preserving the geometry edition. **Resolved.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Band maps must close to the D53 per-province and global volume ledger. | P2 | Data lineage | Compute from committed band volumes and test every rounded province sum against its global band total. **Resolved.** |
| 2 | Eligibility differs materially by band: 54/54/54/50/29. | P2 | Missing support | Rank only positive-volume states and preserve zero separately. **Resolved.** |
| 3 | Zero under the sampled grid does not prove absence at finer resolution. | P3 | Evidence boundary | Label it “no sampled volume,” not “band absent.” **Resolved.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Fixed rank bins would become misleading when only 29 hadal states are eligible. | P2 | Choropleth scale | Recompute five near-equal rank classes from the positive-state count for each band. **Resolved.** |
| 2 | Zero volume requires a visual class distinct from both ranked ocean and out-of-domain land. | P2 | Map legend | Use a separate gray province fill and explicit no-sampled-volume legend entry. **Resolved.** |
| 3 | The active depth must be visible beside the map, not inferred from a distant control. | P3 | Title | Put the band name and “largest first” in the live map-field title. **Resolved.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Where the hadal ocean is” would overstate a coarse center-sampled reference screen. | P2 | Public wording | Say which states contain positive sampled prisms in the fixed hadal interval. **Resolved.** |
| 2 | A high share of the global hadal band need not mean a high share of the state's own volume. | P2 | Main insight | Present both percentages together, as demonstrated by NPSW's 21.62% versus 0.46%. **Resolved.** |
| 3 | Named leaders are capacity findings, not rankings of importance. | P3 | Documentation | Keep SPSG/NPSW findings adjacent to the address-volume limitation. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Band changes must update map meaning for nonvisual readers. | P2 | Live output | Include the active band in the live map label, canvas text, legend, and passport terms. **Resolved.** |
| 2 | Gray cannot be the only indication of zero sampled volume. | P2 | Equivalent meaning | Add a text legend and “no sampled volume” passport state. **Resolved.** |
| 3 | The new map mode must remain keyboard and URL operable. | P3 | Controls | Use a native pressed-state button and preserve `band` plus `map=band` in the URL. **Resolved.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Per-band totals, positive counts, and leaders are regression-sensitive scientific claims. | P2 | Scientific tests | Pin closure, 54/54/54/50/29 counts, and SPSG/NPSW leaders. **Resolved.** |
| 2 | Quantile labels must match the rank-to-color algorithm for nonmultiples of five. | P2 | Browser logic | Derive legend endpoints with the same ceiling boundaries used by rank assignment. **Resolved.** |
| 3 | The view requires no new remote data and must stay offline. | P3 | Reproducibility | Read the committed D53 browser payload and retain syntax/interface checks. **Resolved.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The completed horizontal × vertical view needs a registered evidence identity. | P2 | Source register | Add D55 with support counts, leaders, admitted use, and zero-class caveat. **Resolved.** |
| 2 | Landing page, roadmap, guide, method, history, and data notes must agree. | P2 | Repository record | Update all six in the same reviewed stage. **Resolved.** |
| 3 | Private-preview completion does not change public Atlas 07. | P3 | Release state | Commit locally only after verification. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earth metre-depth bands and seafloor-truncated volumes do not map to gas-giant pressure layers. | P2 | Planetary scope | Keep the selected-band map Earth-only. **Resolved.** |
| 2 | A gas-giant equivalent would require pressure/mass coordinates, density, compressibility, and a declared lower domain. | P2 | Analogy contract | Define those independently before reusing the interaction. **Accepted.** |
| 3 | The linked-selection grammar can transfer even when the bands and quantities cannot. | P3 | Method transfer | Reuse the interaction pattern only after defining a valid planetary coordinate. **Accepted.** |

## Synthesis

Roles reviewed: 8

P1 blockers: 0 | P2 issues: 16 | P3 notes: 8

**Verdict: APPROVED-WITH-CONDITIONS**

**Top finding:** The view succeeds only if local state share, global band share,
and eligible-state rank remain visibly separate denominators.

**Cross-role consensus:** CURRENT, SOUNDER, CHART, BEACON, and HARBOR agree
that zero must mean no positive sampled prism under D53—not proven physical
absence—and must be distinct in color and text.

## Amendments

1. Rank only states with positive volume and derive five class boundaries from
   that changing count. **Applied in browser logic and legend generation.**
2. Add band volume, eligible-state rank, within-state share, and global-band
   share to the selected passport. **Applied without merging denominators.**
3. Test all five closures, eligibility counts, leaders, and interface controls.
   **Applied in scientific and viewer tests.**

The selected-band map may be committed to the private-preview branch after the
full suite. Ecological occupancy, heat, transport, public promotion, and the
54/56 edition decision remain outside this stage.
