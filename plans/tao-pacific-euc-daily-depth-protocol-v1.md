# Pacific EUC daily observed velocity-layer pilot

Use NOAA PMEL ERDDAP dataset pmelTaoDyAdcp, whose primary metadata identify
daily ADCP eastward velocity in cm/s, quality flags, nominal coordinates and
depth in metres positive down. Daily observations represent provider averages
starting00UTC, labelled12UTC; they are not instantaneous noon samples.
Metadata license permits free redistribution with NOAA/PMEL GTMBA credit.
Primary methodological context doi10.1175/JTECH-D-23-0013.1 identifies the
same four monitoring sites and record intervals that include2005. This supports
the fixed pilot year before acquisition, not a promise of gap-free target days.

Before velocities, retain exact info/index.json and a distinct station catalogue
containing only array, station and nominal coordinates. Select the four fixed
equatorial nominal longitudes165,190,220,250degreesE from that catalogue.
Station IDs must be discovered, never guessed. Missing/ambiguous stations block
their own targets without replacement. For each selected station request
March14-16,June14-16,September14-16,December14-16 of2005, inclusive daily
centred times. These dates are fixed before looking at current speeds.

Request original rows between5and350m using the documented
orderByClosest("station,time,depth/10") server function: at most40 returned
levels per daily profile and120rows per three-day temporal patch. This retains
original depth/value/quality tuples near10m intervals; it does not average
vertical bins or reconstruct all original ADCP bins. Do not filter quality at
the server or select the best finite velocity; invalid rows remain missing.
Keep exact returned depths and gaps. Nominal station coordinates are not the
measured deployment coordinates or an independently located current axis.

Decode u only, eastward component/bearing90degrees, dividing cm/s by100.
Quality1and2 are admitted; all other flags and source fills are null. Select
the first tied maximum above threshold within50-250m. Use the frozen
connected-layer kernel with primary0.1m/s and0.05/0.2contexts. Never connect
across missing/rejected values or a returned-depth gap greater than15m:
restrict the kernel to the contiguous depth segment containing the same
original selected core. No alternate core is substituted after segmentation.
Linear interpolation applies only between adjacent retained samples, under
an explicit piecewise-linear profile assumption; it is not a claim about
unsampled original5m structure. Keep the interpolation brackets as resolution
context, not uncertainty. Core-window-edge cases remain qualified/unresolved.

Report derived daily-mean eastward threshold lower depth and, where both
boundaries resolve, the threshold-layer span. They are observed-field proxies
in the EUC geographic context, not independently verified current membership,
physical current thickness, along-current continuity, annual extrema or stored
volume. Preserve all missing dates, weak/reverse profiles and censors. A daily
mean-field contour is not the mean instantaneous depth. No cross-station or
cross-date interpolation or pooling into a seasonal range is authorized.
The provider labels the values daily averages, but underlying within-day sample
counts and coverage are not supplied here; do not claim complete24hr support.

Acquisition is cloud-only, sequential one idle CPU. Max18HTTPattempts total
(2metadata+16fields), one per exact target, no redirects/retries/fallbacks;
25s absolute per request,210s in-process programme deadline and stop starting
requests with less than26s left. Maximum200kB metadata response,50kB field
response,1.2MB total body bytes; source/derived artifact chunk below2.4MB.
Reserve16patches*3profiles*40levels*6numericcells=11520field scalars,
plus1000metadata-coordinate scalars=12520 globally for this new observation
programme, below unchanged250000scalars/7MB. No month/site reset and no new
request in the NorKyst programme; its existing246018reserve stays frozen.

Persist and fsync a pre-request journal row before any HTTP. Atomically retain
the bounded response and its receipt before parsing. Handle termination and
absolute alarms in the producer; it must exit before artifact upload. Persist
unknown/interrupted attempts as attempted, never infer unattempted from missing
raw bytes. Fresh-output-only source invocation; never rerun successful/partial
collection. Any continuation requires a new scoped consumer of retained bytes
and proven unattempted targets. No runtime/UI changes or inventory promotion
are part of acquisition. Credit NOAA/PMEL GTMBA; no messages are sent.
