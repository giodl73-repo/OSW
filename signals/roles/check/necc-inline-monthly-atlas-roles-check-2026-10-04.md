---
skill: roles-check
topic: necc-inline-monthly-atlas
date: 2026-10-04
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# NECC inline monthly atlas review

Artifact: monthly-section card renderer, global atlas integration, shared links,
standalone-page return and browser checks. Seven installed role lenses cover
science, provenance, cartography, explanation, accessibility, lifecycle and
repository status; ORBIT is inapplicable. Internal editorial review only,
not independent scientific measurement admission.

| Role | Finding | Severity | Artifact | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Animated monthly means could imply whole-current evolution | P2 | Card wording | Addressed: local monthly-mean component, longitude, year and unresolved climatology stated; no current footprint rendered. |
| CURRENT | Width of a monthly mean differs from mean instantaneous width | P3 | Status | Averaging-order distinction accompanies every selected month. |
| CURRENT | Zonal-velocity sign is not a full flow direction or transport | P3 | Sample activation | Signed zonal component with m/s units; no arrows, volume or heat transport inferred. |
| SOUNDER | Grid samples could be mistaken for instrument casts | P3 | Map legend | Satellite-product grid samples and nominal 15 m layer explicitly identified. |
| SOUNDER | Saved month must retain source support | P3 | Renderer | Profile count, sample dates, year, units/metric conventions and null annual dimensions validated. |
| SOUNDER | Unsupported annual admission or reversed edges must be rejected | P3 | Invalid data check | Render fallback tested for false annual range and reversed south boundary. |
| CHART | Main zoom must not resize the card's geographic extent | P3 | Section map | Fixed card view checked after main-map zoom. |
| CHART | Section support is not a current axis | P3 | Overlay | Only grid points and cross-boundary marks shown; route layer faded while selected. |
| CHART | Monthly plot needs common axes for comparison | P3 | Chart | Fixed 0–12 N and -1 to 1 m/s axes with explicit labels; no per-month rescaling. |
| BEACON | Users need source scope in the main reading path | P3 | Status/note | Saved year/month, sample count, product class and calculated span appear together. |
| BEACON | Diagnostic playback must differ from admission as seasonal geometry | P3 | Naming | Play monthly profiles; seasonal measurement eligibility remains false in source data. |
| BEACON | Review page should preserve the chosen context on return | P3 | Details link | Month query maps back to exact atlas-section ID. |
| HARBOR | Hover values need equivalent keyboard access | P3 | Grid points | Focus labels and Enter/Space activation report latitude, signed velocity and sample count. |
| HARBOR | Playback must remain under user control | P3 | Controls | No autoplay; pause, previous/next, hidden-page pause and end stop tested. |
| HARBOR | Card must reflow without document overflow | P3 | Mobile | 320 px check passes; natural stacked 860 px screenshot inspected. |
| KEEL | Switching cards could leave timers or late overlays | P2 | Lifecycle | Addressed: disposal stops timers/removes overlays; delayed fetch, switch and reset checks pass. |
| KEEL | Existing observed-section navigation shares URL infrastructure | P3 | Regression check | Antilles observed card and standalone NECC navigation checks pass. |
| KEEL | Invalid data must leave a usable navigation path | P3 | Fallback | Missing/relabeled/reversed evidence hides map/chart and retains review-page link. |
| LOGBOOK | Selected months could disappear from shared links | P2 | URL | Addressed: atlas-section persists across share/reload and detailed-page return; clears on world reset. |
| LOGBOOK | An interface addition does not add measurements | P3 | Counts | Source inventory, canonical ledger and pending-admission status unchanged. |
| LOGBOOK | Focused browser checks do not establish release readiness | P3 | Review | Local checks named; no full suite, clean checkout, commit or publication claim. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 3 addressed. P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for the saved diagnostic interface.
Top finding: selected product profiles must remain distinct from a current's
whole-year footprint. CURRENT, SOUNDER and CHART agree on preserving local
section support and averaging semantics.

## Three amendments

1. State local monthly-mean/product scope beside each frame and retain separate
   diagnostic playback versus scientific seasonal-measurement eligibility.
2. Dispose timers, overlays and asynchronous callbacks on current/world changes;
   keep a working standalone link on evidence failure and test delayed responses.
3. Preserve the selected month in shared and round-trip URLs; check current reset,
   keyboard values, fixed card extent and narrow reflow before delivery.

## Verification and remaining gates

Monthly card browser verifies twelve months, 37 grid samples, boundaries,
playback/pause/December stop, shared month reload, details return, keyboard
values, narrow reflow, switch/reset and delayed/invalid fallback. Antilles
observed-card and standalone NECC browser checks pass. Screenshot inspected.
Canonical ledger SHA256 unchanged:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Source-product error, component identity, independent admission, repeat years
and representative seasonal dimensions remain open. No full current route,
canonical dimension or annual whole-current extrema created by this interface.
