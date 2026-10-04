---
skill: roles-check
topic: atlas-saved-sample-playback
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 2
verdict: APPROVED-WITH-CONDITIONS
---
# Saved sample playback in the custom atlas

Internal review through seven installed role lenses; not independent scientific
approval. Code, pinned series, browser checks and rendered mobile screenshot
reviewed. Physics, provenance, cartography, explanation, access, engineering
and repository status are relevant; ORBIT is not applicable.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Saved samples are diagnostics, not a whole-current axis | P3 | Pinned role and limitations shown in every frame. |
| CURRENT | Unsampled days cannot acquire interpolated geometry | P3 | Playback steps exact frames only; calendar gaps stated. |
| CURRENT | Trace truncation is not physical current termination | P3 | Stop reason displayed; distance-cap circulation explained. |
| SOUNDER | Processing changes can confound apparent ocean change | P3 | 2025 processing-change notice retained with per-frame algorithm. |
| SOUNDER | Date-specific source must survive card navigation | P3 | Source URL and pinned subset link checked for all 17 frames. |
| SOUNDER | System evidence must not transfer to its segment | P3 | Only exact Gulf Stream System identity exposes this series. |
| CHART | Older fronts beside playback can suggest simultaneous geometry | P2 | Saved front lines hidden during diagnostic display; restored on saved-view selection. |
| CHART | Automatic refitting per frame can mimic spatial motion | P3 | Combined sample bounds fitted once; scale stays fixed while stepping. |
| CHART | Coarse state ground cannot improve diagnostic precision | P3 | Existing atlas projection caveat retained; exact pinned coordinates used. |
| BEACON | Equal playback intervals can imply equal elapsed time | P3 | Sample-based playback and intervening unsampled calendar days explicit. |
| BEACON | Twelve dates cannot establish annual extrema | P3 | Sampling note and limitations shown; no annual ranges manufactured. |
| BEACON | Old selection status disagreed with active sample | P2 | Global status and share link now follow exact displayed sample. |
| HARBOR | Playback needs a keyboard and date selector path | P3 | Native buttons, selects and disclosure; no hover-only controls. |
| HARBOR | Long family details delayed access to date controls | P3 | Timeline placed immediately after saved-view controls; mobile screenshot inspected. |
| HARBOR | Narrow screens must retain a usable map card | P3 | 320 px overflow check and rendered screenshot pass. |
| KEEL | Timers must stop when card changes or closes | P3 | Cleanup on selection/reset, pause on disclosure close and hidden document. |
| KEEL | Async loads must not resurrect discarded cards | P3 | Disposed flag and request token reject stale loads; fetch failures shown locally. |
| KEEL | Shared dates require exact fresh-load restoration | P3 | Both sample sets restore final date; details page also accepts exact date. |
| LOGBOOK | New display does not mean new observations acquired | P3 | 17 existing pinned samples reused; canonical release unchanged. |
| LOGBOOK | Passing focused checks cannot support complete-suite claims | P3 | Only timeline, dated-view and global atlas browser checks claimed. |
| LOGBOOK | Internal role review is not scientific admission | P3 | Independent science and annual-coverage gates remain open. |

21 findings: 0 P1, 2 addressed P2, 19 P3 conditions. Approved for editorial
inspection: annual extrema, physical current endpoints and widths remain
unresolved. CURRENT and SOUNDER agree that playback preserves sampling and
source-method boundaries rather than establishing seasonal physical change.

Verification: analysis/test_atlas_timeline_browser.py checks every one of
17 exact projected geometries, dates, sources, scope and stable map scale;
fresh shared-date restoration for both sets; timer pause, saved-view return,
reset cleanup, mobile and system/segment separation. Existing dated surface
selection and global atlas browser regressions pass. Screenshot inspected:
figures/atlas-timeline-review.png. Installed Chromium headless shell 1223 used.
No full-suite or new provider acquisition claim. Earlier focus fix retained.
