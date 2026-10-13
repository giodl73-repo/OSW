---
skill: roles-check
topic: pinned-paper-mirror-acquisition
date: 2026-10-09
roles_used: [SOUNDER, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Original-paper acquisition: internal review

Source commit: parent `48f09ee07289915e1b75f2d64a3f6ea34e8b1304` / draft PR76.
Reviewed working-tree branch `codex/pinned-paper-mirror-acquisition`.
SOUNDER applies to original identity and provenance; KEEL to acquisition and
failure behavior; LOGBOOK to source rights and publication truth. Other roles
have no changed physical claim, cartography, browser interaction, prose science
or planetary analogy to assess. This is internal review, not peer review.

| Role | Finding | Severity | Resolution and evidence |
|---|---|---|---|
| SOUNDER | A matching title does not prove matching source edition. | P2 | Only exact original SHA accepted. NOAA candidate has different bytes and is excluded; no PDF content equivalence asserted. |
| SOUNDER | Mirror eligibility must not transfer to a new fixture or source pin. | P2 | Registry key includes name, primary URL and SHA; mutation tests reject all three mismatches. |
| SOUNDER | Original provenance must survive fallback. | P2 | Existing acquisition manifest and all scientific receipts unchanged; successful fallback logs its actual institutional URL and checksum. |
| SOUNDER | Hosting does not expand redistribution rights. | P2 | No source license changed, no public source copy/cache introduced; original remains ignored. |
| SOUNDER | Availability of one local URL does not prove hosted-runner access. | P2 | Real download confirms bytes locally; shared GEOMAR host limitation explicit and remote verification remains a condition. |
| KEEL | Integrity failure could be misclassified as network failure. | P2 | Only transport exceptions enter fallback; changed primary or mirror bytes stop immediately, before another location or staging. |
| KEEL | Nontransient failure could lead to unbounded retries. | P2 | Existing three-attempt transient limit; 403 does not retry a URL; finite two-location whitelist and exhaustion test. |
| KEEL | A partial mirror response could become a trusted original. | P2 | Existing signature/size/checksum and atomic staging preserved; corrupt-mirror test leaves no PDF or temporary file. |
| KEEL | Existing acquisitions could change implicitly. | P2 | Registry only matches one exact original; existing offline-copy, retry, PDF transport identity and path-restriction gates retained. All 24 local fixtures verify. |
| KEEL | An opaque traceback hides the next provider blocker. | P2 | Terminal exception notes include exact fixture and URL, preserving exception type; fallback logs each failed location. |
| LOGBOOK | Failed CI must not be described as scientific-test failure. | P2 | Both PR76 runs failed during source acquisition before code gates; exact terminal logs recorded. |
| LOGBOOK | A draft fix must not imply mainline recovery. | P2 | Publication remains stacked draft above PR76; hosted-runner outcome reported separately. |
| LOGBOOK | Unlicensed originals must not enter the staged change. | P2 | Only downloader, focused tests, batch receipt and review are changed. No fixture PDF staged. |
| LOGBOOK | Parent tests are not tests of the modified commit. | P2 | Receipt distinguishes parent full-suite evidence from current focused acquisition checks; remote complete workflow remains required. |
| LOGBOOK | One fallback cannot resolve unrelated provider timeouts or science gaps. | P2 | Qiu/Chen timeout and all dimension/footprint gaps remain explicit; active goal unchanged. |

Roles reviewed: 3. Findings: 15 P2, addressed in the batch; 0 P1 blockers.
Verdict: **APPROVED-WITH-CONDITIONS**. Conditions: remote acquisition and full
validation, scientific admission and mainline publication remain unproven.

Three amendments: make transport alternatives contingent on exact original
identity; preserve fail-fast integrity and atomic staging; identify source
failures accurately while recording remote and parent evidence separately.

Top finding and SOUNDER/KEEL consensus: fallback is a transport operation only;
an accessible but different PDF must not silently replace the reviewed original.
