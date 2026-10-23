# Indian SECC source-boundary audit and visual inventory

Continues branch `codex/current-measurement-gaps`, draft PR83. No separate
gap PR or main merge. Source/operator/protocol preflight commit `ecb789a`
precedes the first calculation. This is exploratory: the earlier May failure
was known; the audit is not blinded or a changed width estimator.

## What the complete audit establishes

All144 existing attempts (12 months ×2 meridians ×3 offsets ×2 steps) remain.
Their available78 stations yield156 terminal-direction records. Every original
terminal, immediate inward sample and40/50/60% edge result is copied. The
144-row attempt inventory preserves early seed failures with zero stations.
Empty months do not establish absence of a current.

Of68 outside-source terminal stops, only4 stop the nominal half-peak search
before a crossing. All4 occur in May's two primary attempts passing the five
axis checks: upstream stations−100 and−50km, at both5/10km profile steps.
All4 exit the northern source boundary at the equator. Other outside-source
stops occur after resolved edges or in attempts without usable threshold peaks.

The last finite serialized projected velocities for those4 failures are
approximately0.93–0.95m/s, versus serialized half-peak thresholds around0.24m/s.
These values do not resolve the remaining unsampled interval, exclude an
intervening crossing/return, or identify which current supplies the flow.
No extrapolation, added velocities, boundary-root calculation, physical span,
annual range, footprint or parent-current width is admitted. The old
operator's equator screen remains unchanged. A larger window alone would
not establish a southern-hemisphere edge or current association.

## Presentation

`/figures/indian-secc-source-boundaries-2013/` exposes all12 months, source
coverage, last sampling intervals, all attempts and equivalent terminal/edge
tables. Orange marks denote unresolved half-peak source stops, not current
edges. Linear longitude/latitude axes are explicitly a support diagram.
The source JSON, unchanged diagnostic and frozen method have direct links.
Permalinks, history and invalid-month fallback preserve the selection.

The standalone report/view is complete; the generated main atlas index,
typed diagnostic query, current-card links and WASM delivery for this addition
are still pending the next integrated batch. The preceding Red Sea original
review also awaits that batch. Do not claim full atlas delivery yet.

## Verification and preservation

The eight-input preflight binds the source report, canonical arrays, quality,
selection, acquisition, protocol, operator and synthetic tests. Every pin
matches; exact offline report reconstruction passes. Four focused tests cover
boundary equality/corner exits, decimal threshold equality, missing-value
semantics and complete actual attempt/profile/edge preservation.

Actual Chrome passes all12 months,144 attempts and156 complete serialized
terminal rows, equivalent DOM statuses, every available plotted interval,
keyboard selection, back history, permalinks, invalid month fallback and320px
reflow with plot labels≥10CSSpx. No automatic original-data requests or page
errors. Phone plot visually inspected. The new check is registered alongside
all existing browser checks, and CI adds the exact report/focused tests and
standalone browser gate without removing earlier coverage. Fresh Linux
execution is pending publication. All prior scientific files remain unchanged.

The full local suite at isolated snapshot1f4e017 remains live at this checkpoint
and has emitted failures. It does not include this later audit. Preserve it
until terminal output identifies the failures; no restart or overall-green
claim. Independent1f4/c9 full source/property browser jobs also remain live.

## Next measurement step

Before expanding the source domain, investigate the final native-cell support
under a separately frozen terminal-interval protocol. Retain every censored
case and sensitivity, resolve paired boundaries and current association, and
keep the hemisphere gate. Censoring bookkeeping does not close the named
current's physical width gap. Integrate the new source evidence/view into the
main query atlas in the same continuing PR, then address the full-suite failures
when their terminal diagnostics are available.
