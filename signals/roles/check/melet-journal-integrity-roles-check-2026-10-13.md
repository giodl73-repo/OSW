---
skill: roles-check
topic: melet-journal-integrity
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# Melet generated-cover source-integrity review

Internal review of acquisition reliability and measurement provenance. ORBIT
does not apply; no delegation or independent scientific admission claimed.
Publication requires final offline gates and observed remote acquisition results.

| Role | # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- | --- |
| CURRENT | 1 | Matching prose could hide changed figures or numerical source data | P3 | identity | Complete 143-object journal/resource graph frozen; all encoded streams, figure/font assets and page properties protected. |
| CURRENT | 2 | A source fix could admit previously unknown full widths | P3 | science | 100/40 km confinement scales unchanged; paired edges, full widths, annual ranges and uncertainty remain unknown. |
| CURRENT | 3 | Publisher/repository packaging could be confused with a scientific edition | P3 | version | Same complete journal edition demonstrated; only generated repository-cover objects vary. |
| SOUNDER | 1 | Later download might overwrite or impersonate reviewed bytes | P3 | cache | Separate unchanged repository-current.pdf; reviewed original pin/receipt retained. |
| SOUNDER | 2 | Corrupt retained original might be hidden by fallback | P3 | integrity | Existing wrong original fails; a valid rendition cannot mask corruption. |
| SOUNDER | 3 | Historical source fields could be misread as current raw hashes | P3 | provenance | Reviewed-snapshot meaning explicit; actual response SHA recorded at acquisition. |
| CHART | 1 | Text equality does not prove unchanged figure rendering | P3 | visual proof | All eighteen journal pages rasterize identically at 72 dpi, in addition to encoded resource/data proof. |
| CHART | 2 | Cover-font changes could be mistaken for science-page changes | P3 | object scope | Fourteen changed cover/catalog/metadata objects identified and disjoint from the journal graph. |
| CHART | 3 | Source integrity changes could alter atlas footprints | P3 | map | No source velocity/axis/width digitization or new physical geometry; prior route/seasonal frames retained. |
| BEACON | 1 | “Original verified” might falsely describe regenerated wrapper bytes | P3 | acquisition output | Distinct exact-original and verified-rendition messages; actual SHA and original pin identified. |
| BEACON | 2 | Metadata-only normalization might understate the font/content changes | P3 | method | No byte normalization, PDF patch, typesetting or reconstruction; full received rendition retained. |
| BEACON | 3 | Fixed CI could imply completed core measurement gaps | P3 | status | Delivery reliability only; counts and unresolved physical dimensions unchanged. |
| HARBOR | 1 | Integrity policy might be inaccessible to source-query readers | P3 | evidence access | Contract indexed as the 211th exact source document; confinement audit links it. |
| HARBOR | 2 | Changed source binding could disrupt existing card interactions | P3 | UI | Existing model/cited confinement cards, mobile, source/inspector/query parity and rejection checks passed. |
| HARBOR | 3 | Failure messages could hide whether identity or transport changed | P3 | errors | Separate journal/resource, object inventory, metadata, contract and retained-original errors. |
| KEEL | 1 | Fresh checkout could depend on unavailable reviewed wrapper | P3 | reproducibility | Fresh live isolated hydration succeeds from current HAL bytes; query/dashboard outputs identical between source modes. |
| KEEL | 2 | Parsed cache could ignore later source or contract corruption | P3 | caching | Cache keyed by full raw SHA; contract SHA checked before cache lookup; corruption tests. |
| KEEL | 3 | Parser behavior could drift between local and CI | P3 | dependency | pypdf 6.11.0 pinned; typed canonical encoding documented and tested with content/geometry/identity mutations. |
| LOGBOOK | 1 | Publishing an old PDF or binary patch could violate source boundary | P3 | rights | Originals, current renditions, delta and raster comparisons remain outside Git; public contract contains fingerprints only. |
| LOGBOOK | 2 | Another repair could fragment the gap PR | P3 | delivery | Continuing branch/draft PR83; no separate PR or merge. |
| LOGBOOK | 3 | Successful local hydration might be reported as green remote CI | P3 | gates | Local and remote evidence separate; remote outcome recorded only after observed job state. |

Seven roles; zero unresolved P1/P2 findings for this explicit same-edition
source policy, 21 advisory findings. APPROVED-WITH-CONDITIONS pending final
offline/remote checks. Scientific measurement admission remains unresolved.
CURRENT/SOUNDER/KEEL agree: a generated repository wrapper is accepted only
with the frozen complete journal/resource identity, not text-only similarity.

Amendments applied: separate full-rendition filename and acquisition output;
preserve original pin and reject corrupt-original fallback; explicit historical
source-field meaning and stable journal-integrity inputs. The final receipt
records full-suite, source/engine/staged-byte and remote acquisition evidence.
