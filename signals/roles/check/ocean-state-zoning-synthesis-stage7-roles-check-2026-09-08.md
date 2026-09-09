---
skill: roles-check
topic: ocean-state-zoning-synthesis-stage7
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean-state zoning synthesis Stage 7

**Artifact type:** frozen disposition policy, complete evidence matrix,
side-by-side candidate overlay, and public explanation

**Reviewed artifact SHA-256 values**

- frozen policy: `33A840895B0A3596A52F5B96CA70F02496ED0166ACFB3A71D440F6D8C795AF28`
- synthesizer: `10863878E7D088B601F6D490E8437412648180CB17A45E7970ED361718DC5BBB`
- evidence matrix: `C7A13DD03EE93C3C4931CFBAC5F655E8F3FCFAA08514435ED0C1CEB0A89F584C`
- browser payload: `47026024D57613551BD6B749CB73A77EDF66A0343D5680B2ADA3C448618ECC63`
- stage logic: `93764964D87991FB4E0D3E60C46D49D6B814665DA112CEEEF7C10FB8394B2792`
- workbench HTML: `035D6BB23C3C92D3B59E5192BCB226D0A8086F190F22AF52C2DFBDD8B4B11AB4`

ORBIT is not selected because the synthesis contains no gas-giant transfer.

## Findings

### CURRENT

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | One scalar would make global geometry look equivalent to one regional physical test. | P2 | Keep geometry, depth, contents, exchange, stability, control, event, gate, and uncertainty columns separate. **Resolved.** |
| 2 | A segment failure could be generalized to a 29,690 km global source edge. | P2 | Scope demotion to 16 tested faces and retain the complete reference edge. **Resolved.** |
| 3 | `127 unknown / 1 demote / 0 source changes` is the evidence-shaped outcome, not an aesthetic failure. | P3 | Preserve unknown as the dominant conclusion. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Matrix synthesis could drift from its seven inputs. | P2 | Bind canonical hashes for policy, adjacency, hypsometry, contents, exchange, stability, and events. **Resolved.** |
| 2 | A disposition without its rule and reversal path is not auditable. | P2 | Store rationale, frozen decision rule, and explicit falsification/upgrade text per edge. **Resolved.** |
| 3 | Candidate overlay metadata names source edition, empty source changes, one annotation, and display rule. | P3 | Preserve these fields in later editions. **Accepted.** |

### CHART

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | One annotated map did not fully satisfy the “shown beside source” requirement. | P2 | Add literal side-by-side source and candidate-overlay Mollweide views. **Resolved.** |
| 2 | The full source-edge length beside a small tested mark could imply complete coverage. | P2 | Label it “global source edge” and repeat 16-face scope under the map. **Resolved.** |
| 3 | Quiet unknown hairlines plus one magenta segment accurately encode the evidence imbalance. | P3 | Do not assign categorical colors to unsupported borders. **Accepted.** |

### BEACON

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | “New zoning” or “border rejected” would overstate the result. | P2 | Lead with “the method advances; the map does not redraw itself.” **Resolved.** |
| 2 | `demote` needs an object: a physical-boundary claim, not the source edge. | P2 | Repeat that distinction in rationale, scope, public finding, map note, and history. **Resolved.** |
| 3 | The public finding gives counts, evidence basis, unchanged source, and missing authority in plain language. | P3 | Retain it as the canonical short explanation. **Accepted.** |

### HARBOR

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | A 128-row matrix needs orientation and filtering without hiding completeness. | P2 | Provide border selection, disposition filter, live count, evidence passport, and full scrollable table. **Resolved.** |
| 2 | Candidate/source difference cannot depend on magenta alone. | P2 | Use headings, captions, counts, ARIA labels, and prose in both side-by-side cards. **Resolved.** |
| 3 | A 390-pixel browser check preserves exact edge/filter URL state, one-column revision cards, and zero page overflow. | P3 | Keep this baseline. **Accepted.** |

### KEEL

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Missing or duplicated borders would invalidate global counts. | P2 | Assert exactly 128 unique matrix rows and exact disposition totals. **Resolved.** |
| 2 | Event adjacency could leak into a physical transport disposition. | P2 | Assert `GFST--NWCS` remains unknown with geometric-only event status and unsupported heat transport. **Resolved.** |
| 3 | Policy safety, all-row trace fields, selected scope, source preservation, and exact browser equality pass focused tests. | P3 | Keep synthesizer deterministic and offline. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | Repository approval could be presented as scientific adoption. | P2 | Store owner, external-review, and publication states separately as not requested/conducted/authorized. **Resolved.** |
| 2 | Completion could omit negative and unknown evidence from canonical records. | P2 | Register D63 and update plan, roadmap, guide, README, history, receipt, workbench, and review together. **Resolved.** |
| 3 | No retain, merge, split, or move rule is satisfied, and no source geometry changes are proposed. | P3 | Close the bounded program without inventing a cartographic result. **Accepted.** |

## Synthesis

```text
Roles reviewed: 7
P1 blockers: 0  |  P2 issues: 14  |  P3 notes: 7

Verdict: APPROVED-WITH-CONDITIONS
```

All 14 P2 findings are repaired. Stage 7 meets its exit gate: every disposition
traces to evidence, a frozen rule, and an upgrade/falsification condition;
unknown remains acceptable; source and candidate views are separate; and
repository, owner, external-review, and publication authority are distinct.

The program's bounded scientific conclusion is final: no global zoning change
is earned. One short `SANT--SSTC` physical-overlay candidate is demoted, all
source reference edges remain, and 127 borders await better evidence.
