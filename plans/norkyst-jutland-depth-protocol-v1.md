# New NorKyst Jutland-region depth collection

Reuse retained NorKyst_v3 metadata and the observed2024 zdepth URL recipe from
the Ingoy work; do not reacquire its metadata or original fields. New requested
grid support must be disjoint from Ingoy X2420:4:2616/Y576:4:764. Preserve all
earlier source arrays, operators, inventories,102eddy references and UI/runtime.

Before fields, project three editorial northern-Denmark centers8.55E57.25N,
9.25E57.55N,9.85E57.70N into the retained source polar stereographic CRS. Round
to the nearest800m source grid node. At fixed X take Y=center-38:2:center+38,
39profiles at1.6km retained spacing. These are search cuts, not source-measured
current axes, physical edges, flow-normal sections, widths or end points.
Require native source domain coverage and coordinate/projection closure<=1m.

Use March/June/September/December15,2024 at12UTC, all25 provider fixed z-levels,
and source u_eastward,v_northward,salinity,lon,lat,h,sea_mask. Retain exact packed
ASCII, maps, source URLs and hashes. Validate source time/depth/X/Y and the frozen
daily DAS packing/standard names/license before accepting values. Provider fixed
z values are interpolated from ROMS, not the40native terrain-following levels.
Minimum model bathymetry10m/smoothing and missing below-bed values do not prove
the physical seabed or current bottom. Land/missing are null, not zero flow.

The fixed positive northeast45degree component is independently motivated by
the northern-Denmark Jutland flow context, including the northeast bottom-flow
direction in Kuijpers1993. It is not changed after examining values. Salinity is
retained as context, without a salinity gate or automatic named-water-mass identity.
No North/SouthJutland alias or NCC identity inheritance is admitted.

Use the frozen analytic interval/connected-layer functions on this provider-z
sampling, explicitly labelled accordingly. Selection/core interval0-25m uses
actual returned z-level endpoints. The new product has no30m level; do not insert
an artificial level or silently equate this window with the earlier HYCOM0-30m
diagnostic. Primary cutoff remains0.1m/s, sensitivities0.05/0.2m/s. Greatest
complete positive signed integral with core>0.1 wins; first source index breaks
ties. Retain all candidate scores and unqualified/gate-edge/support-edge cases;
no weaker replacement. Sensitivities at the same selected column cannot fill a
primary gap. Missing/sign/threshold gaps stop tracing. Source-domain end, bed,
literature depths,25m selection bound and sample endpoints are not imposed flow
bottoms. Preserve censor bounds and unknown thickness where appropriate.

Preflight all12targets jointly: maximum250000decoded scalar values/7MB decoded,
25levels,39profiles and975velocity cell pairs per patch; count repeated decoded
coordinate maps. Source request budget12, one request per patch,25s socket timeout,
120000bodybytes per response, no redirects/retries/fallback. Reserve all future
targets in advance. Retain completed raw responses before derivation/next request;
on failure continue only to unattempted predeclared targets. No success replay.
Each case JSON<=70000B, combined preflight/manifest<=120000B, total outputs<=2.4MB.
Twelve120kBraw+70kBreport reservations plus120kBoverhead fit the unchanged batch cap.

Everything numerical, field acquisition, geometry, parsing, derivation and tests
runs only in cloud, sequentially one idle CPU. Local static editing/AST, source
document/metadata review, hashes and exact retention only. Four dated total-flow
snapshots include tide/weather/eddies; no seasonal means, annual extrema, residual
flow, independently validated current axis, physical layer, compatible width,
stored volume or whole-current profile is established. This is additional model
evidence, with all prior unresolved HYCOM cases retained. Goal remains incomplete.
