---
skill: roles-check
topic: zeehan-historical-width
date: 2026-10-08
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Zeehan historical width and Strahan comparison

Artifact: attributed regional width, qualitative occupation comparison,
provenance, Python/Rust guards and visual card/inspector. CURRENT selected for
physical scope; SOUNDER for provenance; CHART for visual evidence; BEACON for
reader interpretation; HARBOR for access; KEEL for executable checks; LOGBOOK
for publication. ORBIT excluded: no analogy. Internal review is not independent
scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | Western Bass Strait slope width cannot cover the whole Zeehan system. | P2 | Geographic scope | One regional point; whole-current representation/ranking false. |
| CURRENT | Relative width change is not a numerical ratio. | P2 | Section comparison | Ratio and both occupation widths null. |
| CURRENT | Instrument range does not define the historical width layer. | P2 | Method context | ADCP coverage, bottom exclusion, mooring isobaths and drogue depth separated. |
| SOUNDER | Historical value is attributed to another paper. | P2 | Width source | Baines et al. (1983) attribution retained; one record, no duplicate. |
| SOUNDER | Complete Baines original bytes remain unavailable. | P3 | Source access | Web-readable archived text recorded separately; no byte pin or independently extracted boundary claimed. |
| SOUNDER | Original Cresswell has a restrictive archive license. | P2 | Acquisition | PDF ignored, personal research copy only; license link and attribution retained. |
| CHART | A point marker could imply a measured occupation. | P2 | Width chart | Explicit historical/background caption and unknown uncertainty. |
| CHART | Drawing unequal bars would invent a width ratio. | P2 | Comparison panel | Text categories in equal cards; no numeric geometry or scaled bars. |
| CHART | Seasonal 2007 context and static 2004 route use other supports. | P2 | Protocol/card | Both independently retained; no route morphing or dimension pooling. |
| BEACON | 40 km must not attach to March or December 1997. | P2 | Both views | Visible separation; each occupation explicitly says numerical width unknown. |
| BEACON | Two occupations cannot establish annual extrema. | P2 | Comparison | Visible warning, null numerical ratio and annual/climatology eligibility false. |
| BEACON | Readers need the full source context from the visual. | P2 | Links | Source locators, scope query and two-record source query preserved. |
| HARBOR | Meaning cannot rely on colored/scaled cards. | P2 | Panel | Text month, relative description, unknown width and station labels. |
| HARBOR | Comparison must reflow at narrow widths. | P2 | Grid | Automatic single-column reflow and 320 px overflow/browser check. |
| HARBOR | Navigation must work without pointer-only controls. | P2 | Links | Native anchors; no hover-only evidence or animation. |
| KEEL | Coherent receipt edits could manufacture dated width support. | P2 | Rust/Python | Compiled row/audit binding and mutation checks preserve null dates, widths and layer. |
| KEEL | Fresh fixture acquisition must match the pinned bytes. | P2 | Acquisition helper | Fresh helper request verified SHA/size; thirteenth fixture registered. |
| KEEL | Numerical dated widths still require new extraction. | P3 | Remaining gates | Compatible operator and paired boundaries needed; not solved by this batch. |
| LOGBOOK | Full goal remains incomplete. | P3 | Batch | 40 width owners unassessed; 89 published length gaps remain. |
| LOGBOOK | OCR could introduce a wrong voyage year. | P2 | Figure 1 | Visually read 1997; OCR 1991 excluded; exact Strahan day still unknown. |
| LOGBOOK | Dashboard counts cannot treat comparison cards as measurements. | P2 | Dashboard | Exactly Zeehan changed; one scoped width, zero new dated width samples. |
| CURRENT | A transport identifier change must not change scientific bytes. | P2 | Source acquisition | Two responses differ only in one 32-character second PDF ID; every other byte remains identical. |
| SOUNDER | Actual response and canonical fixture checksums must remain distinct. | P2 | Transport note/helper | Actual response SHA logged on restoration; historical reference fixture SHA unchanged. |
| KEEL | Normalization must never become arbitrary source acceptance. | P2 | Acquisition helper | Named source, pin, size, offset, first-ID prefix and hexadecimal field checked; resulting whole-file hash must match the original pin. |
| LOGBOOK | Parent CI failure must be diagnosed from the actual failed log. | P2 | PR58 job 113682019691 | Sasaki checksum mismatch before tests confirmed; not described as a Qiu/Chen timeout. |

25 findings: 22 P2 addressed, three P3 followups, no P1.
Verdict: APPROVED-WITH-CONDITIONS, subject to recorded final validation and
independent scientific review. Consensus: preserve attribution, regional scope
and comparison precision without numeric promotion.

Amendments: separate the historical point from survey months; preserve null
numerical occupation widths and ratio; validate original bytes while keeping
the complete copyrighted source outside Git.
