# North Brazil legacy-section depth contours

Process all 14 original full latitude-section cases, seven definitions on January
15 and July 15, 2022 00Z, in one explicit owner export below 2.4 MB. Preserve all
14 interior selections and both original primary lower censors. Traced support is
not an uncensored physical bottom; never fill a censored core from neighbors.

First validate the exact original NBC schema, top-level owner/operator, definitions,
timestamps, raw decoded-column checksum and diagnosis with the original collector.
The older records use signed_northwest_component_m_s, definitions without owner/axis
fields, and no temperature fields. Create a reversible IN-MEMORY view: rename that
component key without changing any values, add only definition owner and explicit
nonthermal null labels, and checksum the alias view. Enrich only config definitions
with owner and temperature_gate=None. Reversing the alias/null/owner changes and
restoring the original checksum must reproduce every original field exactly.
Do not insert a mixed-geometry tag, fixed-axis field or native-latitude column key.

Use a NEW scoped binary32 validation binding. Its tracing function body must be
AST-identical to the frozen three-current curtain; its pre-tag geometry validation
body must be AST-identical to the frozen Pacific/Madagascar validator. Reuse exact
v2 graph/runs/connected_layer and exact original NBC selection/diagnose. Never edit
those old functions or weaken equality to a tolerance. Original decoded u/v arrays
were binary32: 63440 pairs/507520 bytes. The older collector rotated those arrays
before converting to JSON numbers. Newer float64 reconstruction differs at rounding
bits and cannot replace those stored values. Require every decoded u/v value to
round-trip exactly through binary32; replay the exact original along_velocity
operation/order on binary32 arrays and compare signed components exactly. This is
source representation, not physical accuracy or an uncertainty claim. Pin original
NumPy2.3.4 for replay. The first cloud check rejected a float64 generic binding;
that failed check is evidence for this source-specific audit, not a relaxed gate.

The binding restores original column names/definition/null/checksum fields and
runs the original legacy audit, then checks exact binary32 component reproduction.
Strict copied geometry checks retain native indices/hyperslabs/gates and original
-45-meridian distance convention. Every original candidate/selection/core/layer and
seed-run boundary reproduces. Record original and alias-view checksums, exact
binary32 audit flag and source SHA from ORIGINAL bytes, not alias encoding. No
old method/source edits, numeric alias changes, interpolation, new fields acquired
or thermal screen. Alias checksum is not original source/wire-byte evidence.

Preserve fixed 315-degree northwest component, primary 0.1 m/s, surface gate0.05 m/s,
complete finite positive 0-200 m signed integral/core search, original thresholds
and first-native-longitude tie. No weaker replacement, threshold fill or frame
change. Two model states are not annual ranges, seasonal means or historical data.
Keep four-neighbor graph/runs/boundaries, missing/domain/lateral censors and nonzero
upper crossings. Brackets are not uncertainty, missing is not zero/bed/absence,
and model spans are not physical thickness or volume.

The 5S-7N regional surface branch excludes upstream NBUC, Guiana north of10N,
retroflected NECC/EUC continuations and rings. This full-section revision followed
an inspected blocked corridor pilot; it was exploratory, not blinded registration.
Old pilot outcomes stay frozen. No within-run gate expansion or success-dependent
source geometry. Do not inherit Amazon altimetry filters/errors/1993-2017 widths,
source oblique-section endpoints or independently validated axes/normal widths.

Tests/build sequential one idle CLOUD CPU, zero retrieval. Local static editing/
AST, metadata/hashes and exact retention only. Keep existing source/graph/file/
output/publication bounds, all old validated methods/main/runtime/UI and 102 eddy
size references. No whole-route physical profiles, annual bounds or volumes.
