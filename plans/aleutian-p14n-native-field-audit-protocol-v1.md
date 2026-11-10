# P14N native vectors and ship-motion support v1.0

2026-10-18. Declared after reading the original product headers, before
inspecting native ocean/ship velocity arrays. Earlier hourly vectors and
component spans are already known; this is not a blinded preregistration.

1. Preserve both original native products and their frozen acquisition,
   metadata audit and declaration. Select the same 40–48 N, 178–180 E,
   7–18 July 1993 reach. Normalize longitude modulo360 for selection only;
   retain original longitude and source index/time. Time is days since
   1993-01-01 UTC at ensemble end; retain raw decimal days and convert to UTC
   at datetime microsecond precision. Do not assume an exact five-minute grid.
2. Read actual CONFIG1_avg_interval from the long product in seconds. Retain
   every selected value. A finite interval in (0,450] seconds supplies a
   nominal ensemble-start time; other intervals remain in the record but
   cannot enter run/occupation-overlap calculations. Check short/long time
   coordinates exactly before using the same index across products.
3. Use short-product ocean u/v as already Earth-referenced. Retain the source
   ship uship/vship; do not add them again to short u/v. Audit, without forcing
   success, whether short u/v correspond to long relative-water u/v plus long
   absolute-ship components within1e-5m/s absolute tolerance on jointly finite,
   unflagged selected cells. Record counts and maximum component differences.
   This finite representation check is not an instrument-error tolerance.
4. Apply source finite/missing conventions; never use metadata data_min/max
   as quality limits. Primary cells require paired finite u/v, finite nominal
   depth and short editing flag exactly0. Retain flag counts for0–7 and any
   invalid values, finite-but-flagged counts, and short/long flag differences.
   CODAS bits1/2/4 mean bad-bin/bad-percent-good/below-bottom, not CTD WOCE QC.
   Raw values and masks remain recoverable in the unchanged original NetCDF.
5. For each selected profile, use its actual120 depth centres, require finite
   strictly increasing depths, and reuse the prior midpoint-cell weighting
   clipped to100–300m. Require at least160m joint valid support. Preserve the
   support and both means; do not interpolate vertically or replace a missing
   vector component. Unsupported/invalid-depth profiles remain null.
6. Calculate source ship-speed magnitude only when both components are valid.
   Label <=0.5m/s slow, >=2m/s underway-eligible, and the remainder intermediate;
   missing speed stays unknown. These are OSW context cutoffs, not verified
   ship activity or current velocity thresholds. GPS-related ship-motion
   uncertainty can affect these labels. Also retain complete run sensitivity
   at fixed1/2/3m/s underway cutoffs, with no preferred-cutoff selection.
7. A run consists only of consecutive source indices meeting the chosen speed
   cutoff, supported layer means and valid nominal duration. Break at any
   ineligible observation, missing coordinate, nonconsecutive source index,
   nonpositive end-time step or end-time gap>7.5minutes. Keep all runs, including
   short ones; no minimum-duration pruning, sorting by latitude, station-gap
   bridging, temporal ocean-velocity averaging or new width calculation.
   Retain member indices, first/last times, position-track length, endpoint
   distance, northward steps and observed duration. None is current length.
8. Match a nominal ensemble interval against all selected CTD BE–EN intervals
   from the pinned original station log. Require unique BE/EN events and
   ordered times. Retain every positive-duration overlap and its duration;
   touching an endpoint alone is not overlap. This nominal event overlap
   is not measured depth-specific simultaneity, proof of station occupation,
   or a new CTD-wire interference flag. Do not require that overlap and ship
   speed classifications agree; display discrepancies for review.
9. Deliver selected native-layer/ship-motion records, quality/support counts,
   all three run scenarios and an actual-data time/position plot. Any raw
   native velocity display must explain GPS-related five-minute uncertainty
   from Chen and Firing(2006) and must not present noise as resolved current
   edges. The source paper's hourly/2.5hour uncertainty estimates cannot be
   transferred to these unaveraged records as width error bars.
10. This support audit does not admit a current width, identify physical
    boundaries, assign a named eddy, supply annual ranges or enable seasonal
    playback. Keep branch windows44–46N and41–43N unchanged for any later
    operator declaration. Original hourly/CTD/component reports and155earlier
    inventory rows remain unchanged.

Primary context: Chen and Firing(2006), doi:10.1029/2005JC003064, section2
paragraph5, section3 paragraph7 and Figure2. The provider's CODAS_variables
and CODAS_processing_note headers govern product frames, time support and
editing semantics. Native metadata has11,455records/120depth cells per full
cruise product; a local count is not known until this declared selection runs.
