---
skill: roles-check
topic: scientific-readback-repair
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Scientific readback repair review

Baseline3a49c092588bc7a081a1292cf266845a3ffd3ba6; implementation and batch
described in plans/scientific-readback-repair-batch-2026-10-20.md. Seven internal
functional lenses apply to scientific calculation, data, maps, accessibility,
engineering and repository state. No planetary analogy or atlas release;
ORBIT is excluded. This is not external scientific peer review.

| Role | Finding | Severity | Evidence / disposition |
|---|---|---|---|
| CURRENT | Calculation precision must not become physical uncertainty. | P2 | Protocol, source notes and flags distinguish readback increments from observational error/annual ranges; fixed. |
| CURRENT | Rounding inputs could change eligibility. | P3 | Threshold/support decisions remain before output normalization; counts and outcomes preserved in payload comparison. |
| CURRENT | Public source interpretation must remain stable. | P3 | No whole-current, width, annual, rank or footprint admission; nominal Loop1400/600km remains conditional contour geometry. |
| SOUNDER | Original native data cannot be normalized. | P3 | Explicit path whitelists exclude raw profiles, source coordinates, corner vectors, masks, clocks and QC; preservation tests and original-file audit retained. |
| SOUNDER | A Windows path key is a real metadata defect. | P2 | Producer now uses as_posix; the actual NorKyst dependency key is repaired, not ignored; fixed. |
| SOUNDER | Helper/protocol changes need reproducible bindings. | P3 | Both are pinned in affected report inputs and engine manifest; strict source and artifact checks retained. |
| CHART | Sub-millimetre differences do not warrant visual or physical claims. | P3 | Public rounding and geographic paths unchanged; source maps retain masks and unsupported/conditional status. |
| CHART | Figure receipts must track regenerated reports. | P3 | All affected figure/provenance records regenerated after report dependency order. |
| CHART | Model distance coordinates must agree across JSON/NPZ. | P2 | Shared derived distance array rounded consistently before both outputs;124arrays checked with only the declared distance change; fixed. |
| BEACON | Generic stale-report errors hid the useful diagnosis. | P2 | Read-only diagnostic now reports bounded field groups, exact hashes and float hex values; fixed. |
| BEACON | A precision table can imply better source resolution. | P3 | Protocol calls these calculation serialization increments and states originals/effective resolution remain separate. |
| BEACON | Portability repair is not measurement-gap completion. | P3 | Batch explicitly retains open current-length/width/annual/source gaps and existing inventory counts. |
| HARBOR | Revised evidence must remain keyboard and phone accessible. | P3 | Existing shared details/select/table/source interface retained; actual rebuilt browser matrix required before completion. |
| HARBOR | Scientific field explanations need source access. | P3 | Exact records retain protocol and implementation pins alongside original source/method links. |
| HARBOR | Rounding must not replace meaningful labels with visual-only status. | P3 | Categorical outcomes, source-null meanings and all54case rows remain exact. |
| KEEL | Linux exact reconstruction is not yet proven for the repair. | P2 | Open release condition: independent job must rebuild every targeted artifact byte-exact at declared precision. Do not infer this from Windows success. |
| KEEL | Old piece-sum equality ignored intentional stored precision. | P3 | Test now enforces N×0.5mm plus summation roundoff and independently checks actual geodesic vertices; no arbitrary broad tolerance. |
| KEEL | Interpolation readbacks require accounting. | P3 | Every stored vector is reconstructed from original corners and recorded weights within the declared four-weight plus vector-readback bound. |
| LOGBOOK | Existing full run must remain authoritative. | P3 | Live isolated ece1c14 job is preserved; latest repair successor begins only after terminal state. |
| LOGBOOK | Same-PR continuity must persist. | P3 | Same branch/draftPR83; no per-gap PR or main merge. |
| LOGBOOK | Remote test failures must not be described as fixture-only. | P3 | Prior734-test Linux failure and terminal diagnostic evidence recorded separately; no latest-green claim. |

## Synthesis

Roles reviewed:7. OpenP1:0. OpenP2:1. FourP2 findings corrected;16P3 notes.
Verdict: **APPROVED-WITH-CONDITIONS for draft delivery only**.
CURRENT/SOUNDER/KEEL agree on exact original data, explicit calculated precision
and full reproducibility. Top remaining condition is independent Linux proof.

## Amendments and conditions

1. Keep field whitelists and raw-source preservation; investigate any count,
   classification or public-value change instead of masking it.
2. Complete native/WASM UI/source/corruption checks and staged/committed pins
   against the actual regenerated artifacts.
3. Require Linux byte reconstruction and a clean latest full suite. Keep the
   earlier job undisturbed and keep draft/no-main status while gates are open.

## Verification addendum

Independent Linux run39517382843/job118952707192 at ca35472 passed all nine
byte-exact reconstructions. The open KEEL P2 is closed; openP1/P2 now0/0.
The prior clean ece1c14 full suite passed1843tests/1164subtests3643.33s and is
terminal. A latest repaired successor and final browser matrix remain required
release gates. The browser's legacy NECC fallback has an explicit Loop branch
with its own substantive assertions; no old NECC checks were removed.
The shared browser passed all six owners and27corruptions before its600second
aggregate execution deadline. That terminated process is retained in the log;
the full matrix is rerun with the same1800second budget as other large-corpus
checks. No interaction, document or corruption check is omitted.
