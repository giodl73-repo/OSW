# Indian SECC finer-grid source selection v1

Declared2026-10-22 before new velocity fields were acquired. The failed2013
OSCAR local-axis/normal tests are known;this is not a blind comparison.
Use official GOFS3.1 HYCOM+NCODA GLBv0.08 expt53.X2013 reanalysis;fixed75-85E,
12S-equator viewport,exact provider15m z-level,paired Earth east/north water_u/v.
Check original DDS/DAS and coordinate vectors before any velocity request.
Keep original coordinate representation,packing/units/fill flags and provenance.
Reject a missing15m level or unverifiable frame/units;do not substitute a layer.

Select exact daily00Z times over Gregorian2013. Provider gaps remain explicit;
index stride must never shift the clock across missing time coordinates. Split
requests into checked regular source-index runs as needed. Retain all original
responses,request URLs,byte lengths,hashes,timestamps and validation failures.
Every response is capped at20MB;never request or buffer a whole global cube.
A failed/partial acquisition remains resumable without replacing old sources.

Monthly vector means use only paired valid native samples,with the same times
for both components at each cell. Requireceil(0.8*calendar days) pairs per cell;
keep inadequate counts/missing means. Preserve source coordinates and every
monthly outcome;no smoothing,filling,extrapolation or post-result month selection.
Daily00Z model sample means are not full3-hourly monthly means,observations or
climatology. Provider product/year/depth differences prevent attributing any
change from OSCAR solely to resolution. Archive known missing-data notes.

The viewport and source mask are not a current outline or a coast/bathymetry
proof. Source preparation admits no named-current axis,width,annual extrema,
endpoint,state passage,NASA identity or seasonal route playback. Later local
axis/normal calculations must retain source resolution and source-association
checks;source frequency-mode latitude limits do not become physical edges.
Keep all previous OSCAR sources,reports,operators and results byte unchanged.
Use original provider distribution statement and citation;do not infer license
from public URL access alone. Subsequent source/analysis gates and independent
scientific approval remain separate. Work stays in existing draft PR83.

Decode the declared Float32 packing scale as its exact binary32 value promoted
to float64 (not the decimal number 0.001). Sum paired valid packed integers in
int64 before scaling/dividing. Retain float64 monthly arrays without rounding.
Freeze all source-index requests before requesting any velocity fields.

Acquisition-only amendment 2026-10-22T09:46Z: the first six-day response
validated, but a 24-day request timed out before response headers. Preserve
that failed request and the original selection manifest. Split regular runs
into at most six daily samples, with two concurrent requests. Clock, domain,
variables, depth, thresholds and monthly estimand stay exactly the same.
