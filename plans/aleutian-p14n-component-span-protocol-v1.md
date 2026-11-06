# P14N Subarctic branch component spans v1.0

2026-10-18. Exploratory measurement following inspection of the hourly velocity
and coeval CTD companions. This is not a blinded preregistration. Adds a dated
section diagnostic under the general current width protocol; preserves the
earlier source reports and their admission flags.

## Operator fixed before computing spans

1. Use the pinned original observed-vector report, unchanged joint-support
   100–300 m means, source order, indices and timestamps. Retain the coeval
   hydrography companion as context. The paper identifies branches near 45 N
   and 42 N on this cruise, with an eddy near 41.5 N; this is same-cruise
   interpretation, not independent validation of OSW boundaries.
2. Keep the earlier northern 44–46 N and southern 41–43 N search windows.
   Select each window's largest positive eastward mean; ties select the
   earliest source index. Require at least 0.02 m/s, as in the existing basin
   component protocol. This is an eligibility rule, not a physical threshold.
   Flag a peak at a window edge. Keep both measured velocity components.
3. For each branch evaluate thresholds 40%, 50%, 60% of that peak. Starting
   at the peak, walk consecutive observations in acquisition order. Find the
   first value at or below the threshold on each side. Stop at missing means,
   a time gap greater than 90 minutes, or the first sample outside the fixed
   window. Do not sort by latitude, bridge a gap, enlarge a window, choose a
   different peak for a preferred span, or combine branches.
4. Retain both observations of each crossing bracket: source index, time,
   position, u, v and support. Interpolate only between those adjacent valid
   observations, linearly in latitude and longitude, using the fraction of
   the eastward-component threshold crossing. Compute shortest WGS84 endpoint
   separation. This is an **hourly-track eastward-component relative-peak
   endpoint separation**, not a flow-normal width or total current envelope.
   Missing either crossing yields null separation, never zero.
5. Retain acquisition-order lobe indices, elapsed time, track segment lengths
   and bearings, northward steps, track length between interpolated crossings,
   and track-length/endpoint-distance ratio. No latitude monotonicity or
   straight crossing is assumed. Report endpoint separation divided by the
   largest native spacing among the crossing brackets and intervening legs;
   flag fewer than four spacings. This is an attention flag, not validation.
6. Preserve unrounded calculations; nominal display rounds to nearest 10 km
   (half up). The three-threshold sensitivity envelope is available only if
   all three resolve, rounded outward to 10 km. Retain unresolved scenarios.
   Also preserve the four distances between the two bracket endpoint pairs,
   labelled endpoint-combination spread, not confidence or rigorous bounds.
7. Additional finite velocity-error sensitivity uses the *same* peak and
   threshold fraction 0.5. Evaluate threshold displacements of -0.06, -0.02,
   +0.02 and +0.06 m/s on the original u values. A common +0.04 m/s velocity
   offset gives -0.02 in this comparison; the opposite common offset gives
   +0.02. Opposing peak/edge perturbations of ±0.04 give ±0.06. These are
   declared scenarios motivated by the paper's GPS-related hourly two-SD
   0.04 m/s estimate, not a total error budget or probabilistic width interval.
   Threshold <=0 or >=peak is ineligible and retained. Do not pool these
   outcomes with the boundary-choice envelope or treat its endpoints as
   uncertainty bounds. Heading/amplitude errors and correlated temporal errors
   remain unmodelled; no RSS combination is claimed.
8. Preserve the original source and all observed means, including stationary
   CTD occupations. These hourly means are not the paper's exclusively underway
   cross-track velocities. Do not infer an underway filter, normalize by ship
   speed, rotate the flow frame, or silently correct the source processing.
   A crossing spans several observation times, not one simultaneous snapshot.
9. This report alone does not admit an inventory width, resolve named-current
   association, reconstruct physical edges, supply annual ranges, justify
   area/state joins, identify NASA features or enable seasonal playback.
   Review nominal/sensitivity failures and track geometry before any separately
   specified admission. All 155 earlier scoped measurement rows remain intact.

## Primary interpretation and uncertainty context

Chen and Firing (2006), doi:10.1029/2005JC003064, section 2 paragraph 5 gives
GPS-related two-SD velocity uncertainties at 5 minutes, 1 hour and 2.5 hours;
section 3 paragraph 7 identifies the two branches and southern eddy; Figure 2
uses underway cross-track velocities averaged over 100–300 m. Reviewed at
<https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005JC003064>.
The original JASADCP and CCHDO acquisition records remain authoritative for
the bytes and processing history. The CTD temperature-correction notice and
QC7 edited cells remain disclosed by the companion; no new water-mass
classification or hydrographic interpolation is introduced here.
