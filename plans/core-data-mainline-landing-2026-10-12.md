# Core data mainline landing

User authorized merge on 2026-10-12. PR82 is retargeted to main and carries
the accumulated data stack, including scoped current widths, transport and
velocity evidence, dated Thor/Ursa source panels, Ursa's editorial contour
candidate and the exact-pinned paper transport fallback. Scientific admission
limits and remaining gaps in the individual batch receipts remain applicable.

## Main reconciliation

Main `c61cb30620eb1873e330ccc1829fb05a08ae10a3` is the squash merge of PR46.
Its tree differs from ancestor `6002805ef8915bed93b5440fbc303033637ee7f1`
only in `analysis/test_rust_query_browser.py`: dynamic width-owner assertions
replace a fixed count. That change is already in the candidate tree.
Resolved historical conflicts retaining the candidate versions; reconciliation
commit `62d5e2d` changes no file content and records current main as a parent.

## Hosted evidence and correction

Run 38286029831 on `58557aa2fc4d31a75b5a3fa4461c9256fb832f88` acquired
the local originals, passed 45 Rust tests, the 552-test standard-library
baseline, and 1,283 pytest tests. Many shipped browser checks passed before
the atlas test failed on a stale count of five polygons.

The Ursa addition changes inventory display to six polygon owners and 99
shared-gateway names. The atlas test now verifies each polygon owner's mark
and the complete gateway membership, rather than counting selection overlays
or expecting the previous inventory. This correction does not change data or UI.

A local browser attempt during unresolved merge conflicts timed out; it is
not a valid settled-tree gate. The subsequent settled-tree run exposed the
second stale gateway expectation, which was also corrected.

Final corrected browser result and merge identifier are recorded below.
No claim that a complete hosted browser run has passed is made here.

Corrected settled-tree browser check passes: 100 current selectors, all 140
eddy records, six individual polygon owners, exact 99-name shared gateway,
zoom/pan, map-card return and mobile reflow. Generated review screenshots
were restored; they are not part of this landing change.

Additional local gates passed after publication: state directory and route/state
links, seasonal controls, cruise widths/station contexts, regional/model widths,
object cards, recurrence, atlas snapshot and saved timeline. A reused local server
briefly refused a connection; checks resumed after verifying the correct checkout.
Observed-section navigation then exposed a default 30-second standalone-page wait.
Aligned that wait with the existing 90-second loader allowance and added saved-link
failure diagnostics. The full observed-section gate passes, including saved
occupation reload, keyboard casts, standalone return and mobile reflow.
Automatic merge was disabled during investigation and will be re-enabled after
publishing the corrected test. No production data or UI was changed by this wait.
