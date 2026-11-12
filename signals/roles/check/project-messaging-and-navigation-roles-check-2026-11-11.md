---
topic: project-messaging-and-navigation
date: 2026-11-11
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — project messaging and navigation

Source commit: `19148702de6433253dbf412a0a28c0cb4f8e409e`.

Artifact: [revised plan and local delivery](../../../plans/project-messaging-and-navigation.md),
its priority statement in [ROADMAP.md](../../../ROADMAP.md), and the implementation
listed in the delivery record below. Source commit identifies the parent baseline;
this review covers the local revision saved with these files, not a published version.

This replaces the uncommitted Drake-focused plan and review after the owner
clarified the intended scope. The earlier review no longer applies. The new
objective is macro messaging and navigation across the existing work. The owner
subsequently preferred three plain-language entrances over four departmental
labels; this review reflects that accepted revision.

Final clarity pass: the plan now distinguishes agreed messaging from pending
site implementation and maps the six gaps from the initial assessment to work
in scope or explicitly separate work. The roadmap north star now permits equal
entry points instead of prescribing a single chain. These changes were
rechecked through the same functional lenses below.

Method: one assistant applied the eight functional lenses in
[ROLE.md](../../../.roles/ROLE.md), then reinspected the local implementation.
This is internal review, not independent scientific endorsement or formal
usability validation. Browser and visual checks are scoped below.
Each role records three findings. Conditions apply to the editorial implementation;
they do not create a new evidence-infrastructure workstream.

## CURRENT

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| The name “states” could imply physical compartments. The existing classification separates reference geography from moving objects. | P2 | Supporting About copy defines the metaphor and permits overlap/change. Keep it accessible from the introduction. |
| Change-area copy spans temperature, events, storage, and transport; its title could also suggest live data or long-term trends. | P2 | Preserve distinct quantities and identify actual time support. The plan explicitly limits the title's promise; no recalculation is required. |
| Explore the ocean, Follow the currents, and See what's changing organize reader interests rather than claiming a new ocean taxonomy. | P3 | Preserve this editorial distinction; accepted. |

## SOUNDER

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| Source details can disappear when simplifying entrances. Existing pages carry provider/evidence labels. | P2 | Keep essential scope beside views and sources one step deeper; verify during copy review. |
| Full almanac and screened preview have different source-use status, as described in `almanac/index.html`. | P2 | Navigation changes must retain their labels and existing publication boundaries. Do not promote an unscreened build. |
| The task reuses existing data and scientific outputs. | P3 | No new custody packet or evidence framework is justified by this change; accepted. |

## CHART

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| A homepage overview could imply the ocean has one physical partition. Atlas distinguishes reference regions and overlays. | P2 | If reusing a map, retain its role and explanatory caption; avoid a new zoning visual. |
| Page-specific headers currently compete with global orientation. Compare Atlas, almanac, Column, and Exchange headers. | P2 | Apply the same global choices while retaining local legends and map controls. |
| Ocean depths and neighbors have a natural place under Explore the ocean. | P3 | Use descriptive entries while preserving existing URLs and geographic qualifications; accepted. |

## BEACON

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| A prescribed chain or rigid content silos would undermine the three equal entrances. | P2 | The plan gives each surface a primary home with contextual cross-links; the roadmap north star now reflects equal entry points. Resolved for planning. |
| See what's changing could lead to an unexplained narrow event tool; moving guides out of primary navigation could hide explanations. | P2 | Broaden the existing event introduction, explain concepts beside content, and retain guides under Learn more. Required in plan. |
| Proposed opening copy explains the whole project before tools, counts, and methods. | P3 | Use the shared copy hierarchy across homepage and README; accepted. |

## HARBOR

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| Repeated generic card links can hide destinations from nonvisual readers. | P2 | Use descriptive area links and logical heading/text order as required by the homepage plan. |
| Consistent headers can still fail on narrow screens or with keyboard use. | P2 | Check keyboard, visible focus, current-area state, and collapsed navigation during implementation. |
| Three readable choices offer multiple independent entry points. | P3 | Keep them available without requiring a prescribed path or animation; accepted. |

## KEEL

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| Directory moves could break existing deep links across a large static corpus. | P2 | Prioritize labels/headers and preserve paths. Use existing relevant link/browser checks. |
| Adding navigation only to generated HTML would lose it on regeneration. The existing recorded-date equality test caught this. | P2 | Both Loop Current page builders now use `project_navigation.py`; regeneration and all three recorded-date tests pass. |
| The implementation reuses static assets and preserves scientific data and browser calculation code. | P3 | Retain the small shared stylesheet and existing scientific checks; accepted. |

## LOGBOOK

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| Keeping both focus plans active would add the confusion the owner identified. | P2 | Replace the uncommitted plan/review and update the roadmap's single priority statement. Resolved. |
| README, homepage, and status can diverge as links change; planning could be mistaken for completed UI work. | P2 | The plan explicitly requires visible status alignment on touched pages and distinguishes agreed copy from pending implementation. Broader historical cleanup stays separate. |
| The revision acknowledges its prior interpretation instead of describing the owner as approving a Drake-first direction. | P3 | Preserve that truthful scope/status distinction; accepted. |

## ORBIT

| Evidence and finding | Severity | Recommendation / plan disposition |
|---|---|---|
| Planetary comparison contributes to the oeuvre but could compete with the main OSW identity. | P2 | Keep it discoverable under Learn more: Further explorations, with contextual links. |
| Navigation simplification could strip analogy limits from linked descriptions. | P2 | Retain those limits; do not turn visual resemblance into a shared mechanism. |
| No new planetary study is required for the navigation work. | P3 | Organize existing material without expanding the scientific scope; accepted. |

## Verdict and validation

**APPROVED-WITH-CONDITIONS for the local editorial implementation.** Zero P1
findings, 16 P2 findings addressed by scope, copy, navigation, and regeneration
controls, and eight P3 findings. Conditions retain the existing source-use and
release boundaries; this verdict is not publication or scientific approval.

## Implementation evidence

| Check | Observed result |
|---|---|
| Homepage, copy, and visual hierarchy | Desktop and mobile screenshots inspected. Agreed headline and three equal entrances precede the overview map and supporting material. |
| Navigation across the working site | All 22 HTML pages checked at 1440 px and 390 px: 44 combinations, zero runtime errors and zero horizontal overflow. Correct global labels, active-area state, home links, and minimum 44 px global targets verified. |
| Real reader tasks | Homepage → Atlas → ocean depths → homepage; change area → Argo anomaly mode; populated motion map, loaded event finding, and depth region options verified. Keyboard and no-JavaScript navigation also pass. Reduced motion and 720 px layout checked. |
| Link integrity | All local HTML links resolve and IDs are unique across the 22 pages, including regenerated diagnostics. Existing URLs are retained. |
| Focused existing tests | `python -m pytest analysis/test_atlas.py analysis/test_event_journey.py analysis/test_loop_current_recorded_dates.py analysis/test_guides.py -q`: 67 passed. Old editorial expectations were updated to the agreed labels; scientific assertions remain intact. |
| Build and syntax | Native query CLI built successfully. Python compilation, primary browser JS syntax, all 54 almanac JS files, and all 14 existing almanac validation assignments pass. |
| Diff and scope | CRLF-aware whitespace check passes for the repository's mixed existing newline conventions. Scientific source/derived datasets and citation/version metadata are unchanged. |

The local Windows checkout initially converted checksum-bound text assets to
CRLF. Restoring their Git LF bytes resolved the focused geometry-checksum failure;
byte-identical index entries were refreshed without staging content changes.
Repository-local `core.autocrlf=false` now keeps those scientific input bytes
stable. These are checkout corrections, not changes to the dataset checksums.

The full existing scientific suites were attempted without skipping or weakening
their guards. This clone lacks ignored checksum-pinned journal originals, for
example `research/source-data/park-acc-2019/journal-article.pdf`. Those missing
inputs prevent a green full scientific run. An initial missing native CLI was
built; the generated-page mismatch introduced by navigation was fixed in the
builder and verified separately. Full-suite results are not used as scientific
acceptance or release proof for this delivery.

The final default `unittest discover` run completed 552 tests: 367 passed and
185 errored. All 185 errors are `FileNotFoundError` for ignored source originals
from five paper-fixture families (Chen, Archer, Liu/Gan, Deng, and Qiu/Chen).
There are no remaining assertion failures in that run. The separately passing
67-test focused run covers the changed entrances, guides, and generated diagnostic page.
The larger optional `pytest analysis -q` attempt was stopped at 89% after
repeated missing-fixture failures; it is not claimed as a completed or passing
full-suite run. The complete default unittest run above supplies the repository's
required baseline result. Restoring the ignored originals is separate work.

This delivery adds no case study, evidence framework, or mandatory reader-study
gate. Guide chapters remain Markdown; frozen screened/release snapshots remain
unchanged. No formal screen-reader certification, external scientific review,
remote push, or publication was performed.

## Follow-up editorial pass

BEACON: the guide index now groups all 17 chapters under reader questions rather
than exposing one flat technical directory. Six motion subpages identify their
local view instead of repeating the OSW masthead.

HARBOR: Exchange now marks the change area as a parent location, not the current
page. Related-view summaries and links have 44 px targets and visible focus.
Keyboard disclosure operation passes. Thirty-six additional browser cases cover
the nine adjusted pages at 320, 390, 768, and 1440 px with no document overflow
or runtime errors; every guide chapter remains linked.

LOGBOOK: About copy now describes historical branch records without hardcoding
the current branch into the visitor-facing explanation. Local source delivery
and publication remain distinct. These refinements preserve the existing verdict
and its source-use/release conditions.

## Required-CI integration repair — 2026-11-12

The owner subsequently requested push and merge via
[PR #84](https://github.com/giodl73-repo/OSW/pull/84). The earlier no-push/no-deployment
statements describe the 11 November local review, not the later integration.
Visitor-facing status now links to deployment records instead of hardcoding a
not-deployed assertion that would become stale after integration.

SOUNDER: the SOEST author PDF retains its original URL and SHA-256
`b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987`.
A live verified download is still 3,012,493 bytes. No paper bytes, extraction
calibration, or scientific result changed.

KEEL: the university's newer chain requires emSign Root TLS CA - G1 on Linux.
The bundled certificate comes from the [issuer repository](https://repository.emsign.com/certs/roottlscag1.crt);
its DER fingerprint `cef71e70b7c29addf6c30cd19e614b38fd5f02a435a0eeddd0087e183d101a51`
matches the [Microsoft CCADB included-CA report](https://ccadb.my.salesforce-sites.com/microsoft/includedcacertificatereportformsft).
It is applied only to the exact fixture name/primary URL/PDF pin. The context
retains `CERT_REQUIRED` and hostname checks, and does not alter the system store.
Changed or appended certificates fail before network access; unrelated fixtures,
URLs, and PDF pins receive no extra trust. All 86 acquisition/editorial tests pass.

LOGBOOK: this repairs an existing required-CI acquisition failure also observed
on the parent `main` run; it does not waive branch protection or relax source
checksum checks. Integration remains governed by the PR's required checks.
