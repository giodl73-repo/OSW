# OSNAP 2016–2018: prospective sample-support audit v1

Prepared for a separately frozen, cloud-only execution. No original sample
arrays have been read by this version. Corrections after first original
execution require a new version and a new preflight.

## Purpose and source

Establish the usable *support* for later width methods: exact timestamps,
coordinate values, missing-data patterns, velocity-pair availability, pressure
variation and ADCP depth variation. This audit does not select a current edge,
rotate or detide velocity, interpolate across moorings, derive a width/length,
construct an annual physical range, or publish a current geometry.

Restore artifact `12558929959` from successful run `40092026859` rather than
contacting the provider again. Require exact original archive SHA-256
`5b49ea91547fd17b9b3f2e47c743dd2d377a4cdd7ebace5c56977214ec82dee9`,
the tracked first custody receipt, and the exact 78-member header report.
Recheck the original directory fingerprint, inventory, member sizes, CRCs,
SHA-256s and reconstructed headers before interpreting any sample arrays.
Preserve the original acquisition dates and first execution commit. Keep both
the repository CC BY link and the instrument-level license text in the evidence;
this stage does not resolve their differing language.

## Variables and interpretation

Read only `TIME`, `LATITUDE`, `LONGITUDE`, `DEPTH`, `PRES`, and, for the 37
velocity files, `UCUR`, `VCUR`, `BINDEPTH` and `INSTRDEPTH` when present.
Never infer an instrument from its filename alone. Match dimensions, units
and standard names to the exact retained header. UCUR/VCUR must be east/north
components in meter/second with equal `(TIME, DEPTH)` or `(TIME, BINDEPTH)`
shapes. Preserve provider direction/processing notes through the header link.

Use netCDF4 automatic mask/scale decoding. A cell is available only when it is
unmasked and finite after decoding; record raw-array mask and nonfinite counts
separately. This is **availability**, not proof of valid physical observations.
Do not replace missing values with zero, derive a new QC threshold, or claim
that the absence of a sample flag implies good quality. No velocity mean,
transport or sign-based current classification is calculated.

TIME must be one-dimensional, in the reviewed days-since-1950 epoch, with a
standard/Gregorian calendar. Record masked/nonfinite counts, actual earliest
and latest values, duplicates and negative increments between adjacent
available rows. Report median positive cadence and maximum adjacent positive
interval; also report whether every original row is present and strictly
increasing. Do not estimate missing sample counts from irregular cadence or
bridge missing timestamp rows silently. Assign months only to available
timestamps, using the decoded UTC Gregorian month; retain zero-count months
between the actual minimum and maximum month.

Read exact coordinate variables, including WGS84/reference attributes. Report
all coordinate values and their declared uncertainty as source metadata.
Do not use the rounded global geospatial attributes as surveyed positions.
Require singleton finite coordinate values within geographic bounds for a
station-position summary; otherwise record the failure for later review.
No station-to-current or station-to-state geometry is created.

Point-meter and hydrographic DEPTH values are nominal, not instrument motion.
Report PRES in decibar as a pressure proxy; do not convert it to depth with an
unstated latitude/density algorithm. For ADCPs, summarize the supplied
time-varying DEPTH separately from nominal bin and instrument-depth variables.
Availability of both velocity components is paired **per cell**, not merely
per timestamp. Report paired cells, profiles with any pair, profiles with all
bins paired, per-bin paired counts, and paired cells with finite observed
ADCP depth. Denominators are explicit and do not exclude missing cells.

For each month report timestamp rows, paired-cell counts and per-bin counts,
plus min/max of available pressure and supplied time-varying ADCP depth.
These are instrument support/extrema, **not seasonal current width ranges**.
Do not treat a moving bin's nominal label as a fixed analysis layer. A later
method must choose a common physical layer, processing/QC rules, cross-array
overlap, current identity and edge/censoring rules before dimensions are derived.

## Execution and custody

Run one serialized cloud job, one CPU, low priority, numeric workers one,
2 GiB free disk and available memory, 20-minute workflow budget. No local
original access. Require explicit `--cloud-audit` and a committed preflight
binding this operator, tests, protocol, role review, execution workflow, source
inventory/custody/header evidence, and all imported frozen helper bytes.
Run tiny synthetic fixtures first, including actual NetCDF synthetic samples.

Read at most one 64 MiB instrument member at a time. Use an exact-byte private
temporary file in the owned cloud workspace and remove it after processing.
Bound individual decoded arrays to 64 MiB and final JSON to 8 MiB; fail rather
than truncate. Never extract provider paths. No networking exists in the audit
operator. Retain the source artifact ID, original custody, preflight hash and
execution commit in the derived report. Write report bytes immutably.

## Review and delivery gates

The execution result is `PASS_SAMPLE_SUPPORT_AUDIT_ONLY`; individual support
anomalies remain explicit and may prevent a later width method. Successful
execution proves the audit ran, not that the array resolves both current edges.
All eight LS moorings remain distinct from the two additional deep moorings in
the cited ten-mooring study. Coastal, slope and deep currents remain distinct.

After actual results, review cadence, overlap, missingness, motion and declared
processing before proposing a width derivation. A public source/support viewer
must label custody, headers, sample support and measurements separately, retain
a text/table alternative, and pass keyboard/reflow checks in a later serialized
cloud browser gate. This workflow has no automatic data admission or release.
