# P14N contiguous underway averaging and component boundaries v1.0

Declared 2026-10-18 after native vectors, hourly component spans and all
native run durations/latitude endpoints have been inspected. This is an
exploratory operator, not a blinded preregistration. New averaged velocities
and boundary results have not yet been computed at declaration.

## Fixed inputs and scope

Use the unchanged, checksum-pinned native support report and its verifier.
Preserve its 100-300 m joint layer support, editing masks, source order,
actual ensemble intervals, 40-48 N selection and 1/2/3 m/s run scenarios.
Keep northern 44-46 N and southern 41-43 N windows. Do not reclassify station
occupations, merge runs, interpolate missing vectors or change source flags.

## Averaging

For every retained run and each fixed duration 30/60/150 minutes, partition
time into disjoint windows anchored at that run's first nominal ensemble
start. Retain every intersected window, including incomplete final windows.
Clip each contributor's nominal ensemble interval to its window. Compute
the exact union of these clipped intervals by splitting at all endpoints.
Within any overlapping interval, use the arithmetic mean of the active
profiles' supported u/v, then integrate over time. Thus overlap is retained
and explicitly measured, never counted twice in coverage or averaging.

Store contributor indices, clipped intervals, union seconds, missing seconds,
overlap seconds, integrated u/v, and union-time-weighted ensemble-end
latitude/longitude. A bin supports boundary analysis only at >=80% union
coverage of its full declared duration; do not shorten the denominator for a
terminal bin. Retain below-coverage values as contextual means, explicitly
ineligible. Preserve contributor latitude/longitude extrema and endpoint
track distance: the weighted location is a display summary of a moving
measurement footprint, not an instantaneous velocity at one point.

## Boundaries

For each speed/duration/branch combination, eligible bins must have >=80%
coverage and all contributing ensemble-end latitudes inside the fixed branch
window. Select the largest eastward mean, ties by earliest run then bin.
Require peak >=0.02 m/s. Retain candidate bins and the selected peak.

At fixed 40/50/60% of that peak, walk toward earlier/later bins within the
same run only. Stop at an absent bin, ineligible coverage, branch-window
edge or run end. Never jump to another run, even if its latitude is adjacent.
The first bin at or below the threshold brackets a crossing. Interpolate
linearly between weighted display positions, retain both complete bin
references and the interpolation fraction. Only two resolved sides yield
a WGS84 endpoint separation. Also retain half-peak threshold displacements
-0.06/-0.02/+0.02/+0.06 m/s as separate representation sensitivity, with
thresholds outside (0,peak) ineligible. No scenario is selected after results.

## Interpretation and admission

These are exploratory time-averaged eastward-component spans. Run barriers
may leave either or both sides unresolved; missing sides remain null. Do not
turn a window edge into a crossing or substitute an earlier hourly result.
The paper's GPS-related 2-SD estimates at one hour and 2.5 hours are context,
not calibrated uncertainty of these clipped, filtered OSW averages. Do not
infer uncertainty for the 30-minute case by scaling those estimates.

Retain u and v separately; eastward is not a newly estimated flow-normal
coordinate. Neither a resolved component span nor a selected peak establishes
named-current association, southern eddy separation, physical edges, whole
current width, annual extrema, seasonal playback or geometry for state joins.
No inventory width row or ranking admission is authorized by this operator.
Preserve all earlier reports and all 155 existing scoped width records.

Reference: Chen and Firing (2006), doi:10.1029/2005JC003064, section 2
paragraph 5 (GPS-related averaging context), section 3 paragraph 7 (branches
and southern eddy) and Figure 2 (underway cross-track comparison). The
present eastward-component operator does not reproduce that figure's
cross-track coordinate or geostrophic fit.
