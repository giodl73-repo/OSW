# S1 local flow-span measurement

Carry the original S1 case ledger (metadata operation completed, seven provider
operations left). One new CSV query requests all bins during 2023-07-10 UTC.
The metadata reports half-hourly updates, at most 32 native vertical coordinates
within the observed domain, metre coordinates, a fixed site, moored upward ADCP,
delayed-mode velocity components with BODC metres-per-second units, and L20 QC.
The query is a documented tabledap subset, not an archive/range/mirror bypass.
Reject the entire response if it exceeds the original caps; do not retry a smaller
date window. Parse at most 150 profiles and 40 native levels per profile, 20000
cells, 6000 shared threshold nodes. Raw CSV must be retained before CSV parsing.

The source's negative coordinates contradict its positive-down declaration.
Its component labels do not independently establish magnetic/true reference.
Neither is repaired. Measure only a quantity invariant to a common vertical
sign change and a common horizontal rotation: the difference between native bin
coordinates in a connected flow component aligned to each profile's strongest
good-QC horizontal vector. Use QC1 finite pairs only, core-relative component
thresholds 0.05, 0.10, 0.20m/s, and maximum adjacent native spacing 10m. All
thresholds share these same profiles, numeric and source-operation budgets.

Extend from the core through adjacent admitted bins. Stop at missing/QC bins,
spacing gaps, threshold brackets, or sampled boundaries. Never interpolate or
bridge a gap. A single bin has no resolved vertical span (null), not a zero-depth
current. Record sampled endpoint censoring. Do not map native numeric order to
shallow/deep. Exact scalar and full JSON roundtrip checks run in the cloud.

This is a dated local sampled flow span, not an absolute depth, physical full
layer thickness, current bottom, annual range, daily mean or volume. Tides remain
in the instantaneous samples. S1 is at a confluence of water sources: no named
current owner or water-mass attribution is admitted. It is a native observation
packet for later qualified use, not a canonical depth-reference admission.

Original case caps and cumulative clock persist. Close after this measurement,
surrender the six unused operations, and forbid instrument/month/version budget
resets. Use one idle cloud CPU sequentially, absolute timeout and SIGTERM, fresh
output directory, original-source byte custody, and no UI/runtime integration.
