---
skill: roles-check
topic: norwegian-front-bosse-corrected-width
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# Corrected Norwegian front-width review

Seven installed lenses applied internally. ORBIT does not apply. No delegation
or independent scientific approval claimed. Review covers editorial source
extraction and atlas presentation, conditional on final offline publication gates.

| Role | # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- | --- |
| CURRENT | 1 | Gaussian integration width could be called FWHM | P3 | operator | Positive poleward boundaries inside maximum ±2 fitted-sigma interval; half-peak restriction describes fitting, not the reported width. |
| CURRENT | 2 | Depth average could become width of a fixed 1000 m slab | P3 | layer | Profiling/depth-average context retained; fixed width-layer bounds and paired geometry remain null. |
| CURRENT | 3 | Local front width could fill a parent/whole-current dimension | P3 | identity | Proposed Front only; generic Norwegian/coastal aliases and parent width unresolved. |
| SOUNDER | 1 | Stale approximately 60 km edition could replace corrected result | P3 | version | Corrected publisher version dated 2020-09-28, 38 ± 2 retained; source correction/access explicit. |
| SOUNDER | 2 | Reported ±2 could silently become annual range or 95% CI | P3 | uncertainty | Separate reported-error field; width-specific statistic interpretation pending Table S1; no assigned confidence level or width range. |
| SOUNDER | 3 | Reviewed text could be described as original PDF/SI acquisition | P3 | evidence | Access limitations explicit; original corrected PDF/SI not acquired and raw reconstruction not claimed. |
| CHART | 1 | Same axis could imply directly comparable trends | P3 | comparison | Locations/methods explicit; no connecting trend line or midpoint; distinct Mohn/Svinoy scopes. |
| CHART | 2 | Point graphic might hide reported uncertainty | P3 | chart | ±2 shown in label and explained beside figure; no unverified error bar or annual envelope. |
| CHART | 3 | Source tracks could create current footprints | P3 | QA links | Original-mission source visual and records linked with unchanged QA status; no current axis, buffer or state containment. |
| BEACON | 1 | Unknown 2010 mean could be overwritten by 2019 value | P3 | narrative | 2010 Svinoy mean stays null; 2019 Mohn result is a separate record. |
| BEACON | 2 | Seasonal agreement could generate three copies of 38 km | P3 | seasons | Qualitative statement only; no numeric seasonal means, twelve-month series or playback. |
| BEACON | 3 | New record could imply reduced canonical gap counts | P3 | status | Four proposed records / two branches; canonical 136/72 width evidence, 13 unassessed widths and 89 length gaps unchanged. |
| HARBOR | 1 | Screen-reader title could still call the new point ADT | P3 | semantics | Method-aware aria label distinguishes corrected glider statistic from ADT scalar. |
| HARBOR | 2 | Compact chart could clip mean/range labels | P3 | mobile | 320 px reflow and glyph readability checked; mean/range/caption image visually inspected. |
| HARBOR | 3 | Source QA could remain inaccessible from its card | P3 | navigation | Direct visual and source-query links, checked native/WASM record parity; exact JSON alternative indexed. |
| KEEL | 1 | Coherent receipt rewrite could change reported ±2 | P3 | integrity | Compiled whole-record equality and Python source pin; native/WASM reject coherently altered proposal uncertainty. |
| KEEL | 2 | New proposal checksum could stale equatorial extractions | P3 | dependencies | Endpoint and two dependent receipt hashes refreshed; numerical series/originals preserved. |
| KEEL | 3 | Source corpus additions might be missing from mainline checks | P3 | coverage | 210 exact documents verified; dedicated browser registered in mainline; full offline gate recorded separately on completion. |
| LOGBOOK | 1 | New gap could create another PR | P3 | delivery | Existing branch and draft PR83 retained; no separate PR or merge. |
| LOGBOOK | 2 | Earlier standalone-QA note could claim UI wiring absent | P3 | receipts | Earlier receipt updated with subsequent integration; source audit and corrected measurement remain distinct. |
| LOGBOOK | 3 | Local green could imply remote CI or independent approval | P3 | publication | Local results and prior Melet checksum failure reported separately; source pins not waived. |

Seven roles; zero unresolved P1/P2 issues for editorial extraction and
presentation; 21 advisory findings. APPROVED-WITH-CONDITIONS, with scientific
admission unresolved. Shared CURRENT/SOUNDER/CHART condition: preserve the
source's local boundary definition and separate reported error from physical
seasonal/annual ranges.

Amendments applied: method-aware point labels and adjacent statistic text;
distinct 2010/2019 geographic and mean scopes; indexed raw-QA links with
native/WASM source and coherent-mutation checks. Publication also requires
final full-suite and source/engine/staged-byte checks in the batch receipt.
