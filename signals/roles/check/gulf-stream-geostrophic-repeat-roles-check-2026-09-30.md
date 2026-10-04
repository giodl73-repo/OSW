---
skill: roles-check
topic: gulf-stream-geostrophic-repeat
date: 2026-09-30
roles_used: 6
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: five-date Gulf Stream geostrophic repeat audit

Artifact: four newly pinned NOAA LSA velocity subsets, the existing 25
September subset, the repeat-date analysis, reproducibility test, methods
statement, and source-use packet. This is a scientific research receipt with
no new map surface. CURRENT, SOUNDER, CHART, BEACON, KEEL, and LOGBOOK are
relevant; HARBOR and ORBIT have no new interface or explanatory analogy to
review.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | The same selected seed reaches 50°W on four adjacent dates but stops on 18 September; this does not establish a stable axis. | P2 | Repeat summary | Keep the analysis research-only and unranked. |
| C2 | Only three of ten adjacent-seed traces reach 50°W; threshold and seed choice determine whether a reach exists. | P2 | Trace rows | Do not infer width, continuous transport, or permanent state passage. |
| C3 | The daily altimetry-derived surface geostrophic field omits ageostrophic flow and depth structure. | P3 | Field and limitations | Retain the physical qualifier beside any future reuse of these values. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | Each of the five source NetCDF responses and regional packed subsets has an explicit SHA-256 and daily time bounds. | P3 | Pinned source receipts | Keep acquisition separate from normal offline builds. |
| S2 | The five dates are deliberately selected and contain no quantified field or positional error. | P2 | Sampling design | Use a predeclared time window and product uncertainty information before estimating route persistence. |
| S3 | Four new packed NOAA field subsets sit outside the release package but still need source-specific redistribution and citation review before public repository publication. | P1 | Source-use packet | Resolve terms for all five subsets or omit packed values from the public repository. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| G1 | The repeat receipt reports only first eastward longitude crossings; meanders or backtracking can create later crossings. | P2 | Checkpoints | Label crossings as first eastward and avoid treating them as a unique route coordinate. |
| G2 | The 18 September selected trace has westward steps and stops before the downstream gate. | P3 | Trace diagnostics | Preserve stop and backtracking metrics in future map exploration. |
| G3 | The repeat receipt has no visual corridor or confidence envelope. | P3 | Research receipt | Draw neither until the spatial and temporal sampling can support one. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | The four successful lengths could be mistaken for a stable whole-current length. | P2 | Methods summary | State “partial seed-to-50°W reach” whenever the values are shown. |
| B2 | “Four of five dates” is descriptive for this chosen sample, not a frequency estimate for the Gulf Stream. | P2 | Repeat summary | Identify the selected dates wherever the fraction appears. |
| B3 | The early-stop case and nearby-seed failures are easy to find in the JSON summary and release methods. | P3 | Summary | Keep negative evidence alongside successful traces. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | Explicit fetch checks exact source hashes; default analysis reads pinned subsets without network calls. | P3 | Fetch and analyze scripts | Keep source refresh separate from package build. |
| K2 | A dedicated test recomputes the receipt and checks the stop case, adjacent-seed failures, and source hashes. | P3 | Test | Retain these scientific checks as method changes. |
| K3 | The research output is not in the release manifest. | P2 | Package provenance | Keep the research-only label; if the audit enters a release, add it and its code and inputs to the manifest. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | The source-use packet now scopes public repository publication as well as dataset deposition. | P3 | Decision packet | Resolve it before either public action. |
| L2 | The audit states its deliberately selected dates and no claim of temporal census or stable route. | P3 | Methods | Preserve the explicit sampling limit. |
| L3 | The expanded research remains in a modified, untracked worktree without a reviewed source commit. | P2 | Git state | Freeze and review the source set before public release. |

## Synthesis

Roles reviewed: 6  
P1 blockers: 1 | P2 issues: 8 | P3 notes: 9  
Verdict: **NEEDS-WORK** for public publication. The research-only repeat
audit is useful evidence against promoting one day's line to a permanent
route. CURRENT, CHART, and BEACON agree that four successful neighboring days
do not create a whole-current path or length. SOUNDER and LOGBOOK agree that
the extra NOAA velocity subsets expand the source-use decision.

Three amendments:

1. Resolve NOAA LSA redistribution and citation terms for all five pinned subsets before publishing this repository or a derived dataset.
2. Predeclare a longer temporal sampling design and obtain field uncertainty before estimating path persistence or a map corridor.
3. If repeat observations become part of a release, include their inputs, analysis code, and outputs in that release manifest and rerun its checks.
