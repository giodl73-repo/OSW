---
skill: roles-check
topic: guide 10 plumes upwelling vertical exchange
date: 2026-09-05
roles_used: 8
p1_count: 0
verdict: APPROVED
---

# Roles check — Guide 10: Plumes, Upwelling, and Vertical Exchange

## Artifact identification

- **Artifact type:** public-science guide plus controlled classification and
  relation registries
- **Primary artifact:** `guides/10-PLUMES-UPWELLING-AND-VERTICAL-EXCHANGE.md`
- **Companion artifacts:** 88-object classification CSV, 69-edge relation CSV,
  research grounding, source register, guide index, history, and contract tests
- **Source commit:** `556edacd5c5b9ca0b1829e804ae05384635a730b`
- **Review target:** working-tree snapshot on `atlas-08-private-preview`; the
  additions are not represented by the source commit alone
- **Validation:** `python -m pytest analysis -q` → 389 passed, 10 subtests passed

## Role selection

All eight installed OSW roles apply. CURRENT owns the vertical physics; SOUNDER
owns evidence identity; CHART owns schematic claims and future map implications;
BEACON owns public interpretation; HARBOR owns equivalent text access; KEEL owns
the registries and tests; LOGBOOK owns repository truth; ORBIT owns the
planetary-transfer paragraph.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Plume identity, upward velocity, heave, and transformation are correctly separated; this is the chapter's decisive physical contribution. | P3 | Body, motion, and conversion | Preserve this four-way distinction in every future map layer. |
| 2 | The initial registry encoded isopycnal heave as necessarily oscillatory even though heave can evolve without periodicity. | P2 | OBJ087 | **Resolved:** changed mobility from `oscillates` to `evolves`. |
| 3 | The heat warning correctly rejects vertical velocity alone as a heat budget and names geometry, reference, and closure requirements. | P3 | Decisive tests / OSW consequences | Carry those terms into any vertical-flux implementation contract. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Plume cards name source tracers and ambient endmembers as necessary evidence rather than inferring source from colour. | P3 | Object cards / decisive tests | Require actual variable IDs and detection thresholds when these concepts become data layers. |
| 2 | The original heave explanation lacked a direct source focused on reversible-versus-irreversible attribution. | P2 | Heave is not mixing | **Resolved:** added the Han preprint with an explicit non-universal-method caveat. |
| 3 | The web record documents 19 findings and separates conceptual grounding from global detection. | P3 | Research signal | Add exact CF/NVS concept identifiers before interoperability or API export. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Coast, equator, and open-ocean curl are shown as different geometries instead of one portable arrow convention. | P3 | Three upwelling geometries | Future mapped examples must name projection, date, depth, sign, and mask. |
| 2 | The coast schematic could be misread as globally prescribing one favorable wind direction, but the adjacent prose explicitly makes direction hemisphere- and coast-dependent. | P3 | Three upwelling geometries | Keep the qualification beside the diagram; add real regional arrows only from data. |
| 3 | No coloured measured field is presented, so the chapter does not imply unwarranted geographic coverage. | P3 | Whole guide | Treat any later plume boundary as diagnosed/thresholded, never decorative. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The opening sentence and first diagram give a repeatable, supported distinction between body, motion, and conversion. | P3 | Opening / body, motion, and conversion | Use this as the short entry path from maps to methods. |
| 2 | The original draft relied on the collection-level statement that diagrams are conceptual rather than labeling the chapter itself. | P2 | Opening | **Resolved:** added a local evidence-class statement before the object cards. |
| 3 | “Cold SST is supporting evidence, not the definition” prevents a visually memorable state from becoming an unsupported mechanism claim. | P3 | Upwelling geometries | Repeat this sentence near any future thermal overlay. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Every schematic has a prose equivalent that carries the scientific conclusion without spatial or colour perception. | P3 | All diagrams | Preserve text alternatives when diagrams migrate to SVG. |
| 2 | Tables use explicit column headings and distinctions are not encoded by colour. | P3 | Object cards | Keep narrow-screen rendering in mind if cards become interactive. |
| 3 | Unicode arrows and density symbols aid scanning but are not the sole carriers of meaning. | P3 | Diagrams | Retain the surrounding canonical prose in rendered versions. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Guide 10 is included in the same existence, section, and link contract as Guides 01–09. | P3 | `analysis/test_guides.py` | Keep all new guides in the formatted two-digit page list. |
| 2 | Registry counts, enums, uniqueness, relation endpoints, and source-ID uniqueness are executable checks. | P3 | Registry tests | Add exact external-ID schema checks when those identifiers are populated. |
| 3 | The complete offline suite passes: 389 tests and 10 subtests. | P3 | Validation | Preserve this command as the merge gate; keep source refresh outside it. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README, guide index, classification, history, source register, and tests agree on 10 guides and 88 objects. | P3 | Companion artifacts | Update these surfaces together on the next taxonomy increment. |
| 2 | History explicitly records that 88 is editorial and versioned, not a natural object count. | P3 | Project history | Preserve this qualification wherever the count is publicized. |
| 3 | The review identifies a working-tree snapshot and source commit without claiming the branch is published. | P3 | Artifact identification | Do not change release or remote status until an authorized commit/push stage. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The comparison names buoyant plumes, vertical motion, and displaced interfaces rather than relying on visual resemblance. | P3 | Planetary connection | Preserve property-by-property comparison in future figures. |
| 2 | The guide explicitly rejects cloud-top colour as a water-source tracer and ascent as automatic cross-isentropic transformation. | P3 | Planetary connection | Add matched nondimensional regimes before any stronger analogy. |
| 3 | The paragraph points back to the falsifiable comparison protocol in Guide 07. | P3 | Planetary connection | Keep Guide 07 as the governing comparison contract. |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 3 (all resolved)  |  P3 notes: 21

Verdict: APPROVED

Top finding: Guide 10 makes source identity, vertical motion, reversible
             interface displacement, and irreversible transformation distinct.
Cross-role consensus: Any future map must keep thermal appearance separate from
                      mechanism and label the evidence class at the point of use.
```

## Amendments applied

1. Changed isopycnal-heave mobility from `oscillates` to `evolves`, because
   reversible vertical displacement need not be periodic.
2. Added a direct heave-versus-transformation citation and stated that the
   recent decomposition is conceptual support, not a universal operational
   diagnostic.
3. Added a local evidence-class statement so readers do not have to infer from
   the collection index that all diagrams are conceptual.

## Remaining non-blocking work

- Map OSW terms to exact governed vocabulary identifiers before machine
  interoperability claims.
- Require variable, depth, interval, threshold, uncertainty, and provenance
  metadata when any Guide 10 concept becomes a detected atlas layer.
- Seek external domain review before describing the classification as a
  scientific standard.

