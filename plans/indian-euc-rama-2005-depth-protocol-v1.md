# Indian EUC observed daily depth and persistence pilot

Freeze February-May2005 before inspecting fields. At nominal0N90E collect
every provider daily profile; at0N80.5E collect days14-16 of each month as
sparse spatial/phase context. Primary observational literature includes both
sites in2005. Review context/source limitations in the pinned contextJSON.
The90E continuous window has120expected days; the80.5E comparison has12.

Reuse the retained NOAA metadata bytes, verified by source hash and frozen
metadata validator. No metadata, catalogue, existing field or artifact download
is replayed. Request original NOAA ERD pmelTaoDyAdcp rows with exact nominal
coordinates/time/depth bounds. Discover unique station/array identifiers in
returned rows. No guessed IDs, redirects, retries, fallback or best dates.

Use source40-300m because the primary Indian studies exclude near-surface
backscatter and gappy deeper observations. Retain original rows near10m using
the documented orderByClosest; no means/interpolation by the server. At most
30returned levels per profile, a tighter bound within the unchanged40level
ceiling. This source domain naturally has about27levels. Preserve all QC and
fill rows; admit quality1/2 only. Convert eastwardcm/s to m/s, bearing90true.

The independent Indian prior sets the core window60-160m, rather than the
Pacific pilot's50-250m. Keep the same first-tied-maximum selection, primary
0.1m/s,0.05/0.2contexts,15m maximum gap and core-locked connected-layer
kernel. Missing values, depth gaps and domain edges censor boundaries. Mark
core-window edges unresolved for the primary estimate. Crossings assume a
linear profile between adjacent retained rows and no hidden reversals; brackets
describe sampling resolution, not uncertainty or full original-bin structure.

For an OPERATIONAL EUC-context candidate, the original interior selected core
must exceed BOTH finite quality-valid40m and50m velocities by>=0.1m/s.
The contrast is a predeclared editorial gate, not measured uncertainty. At90E
binary-roundoff equality is allowed within1e-12m/s, not a physical error bar.
require31successive candidate daily labels, with missing/weak/rejected days
breaking the run and no month-boundary reset. This is a sequence of provider
daily means, not independently verified continuous physical EUC membership.
True surface velocity and thermocline membership remain unknown. At80.5E
report persistence as unassessed: never transfer90E qualification to it.
Retain all diagnostic lower contours/spans even if the context gate fails;
context failure is not current absence. No reference inventory admission here.

This is a new independent current programme, not a reset of the Pacific
18attempt/12520scalar case. Prove target URLs disjoint from retained Pacific
targets before network. Eight total field attempts, one each; max125kB for
monthly and50kB for three-day patches,900kB aggregate body. Source/decode
reserve132profiles*30levels*6numericcells=23760 plus1000metadata cells,
24760globally under250000scalars/7MB. Reserve3960source sample positions
plus1320boundary/core/nominal-point positions,5400nodes including run context,
under6000per case. No per-site/month resets. Max31profiles/930rows per patch,
under150profiles and20000cells. All outputs together below2.4MB.

Cloud only, sequential one idleCPU. Reuse frozen durable pre-request journal,
fsync/atomic response-before-parse transport,25s absolute alarms,210s internal
programme deadline with26s minimum before starting a request. Handle SIGTERM
by unwinding the producer; it exits before artifact upload. Persist attempts,
partials and all planned outcomes. Fresh source folder only; never rerun this
collector after any attempt. Later consumers use retained bytes and prove any
unattempted scope. All prior science/archives/842references/102eddyrefs/runtime
and main remain unchanged. No physical thickness, annual range or volume.
