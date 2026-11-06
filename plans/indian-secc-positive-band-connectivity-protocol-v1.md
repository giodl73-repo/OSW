# Indian SECC investigation: positive-band connectivity v1

Declared 2026-10-21 before computing this diagnostic. The twelve surrounding
2013 OSCAR monthly fields and the earlier two meridians are already known.
This is exploratory, not an independent validation or a fitted current model.

Use the retained source report without changing its monthly operator, masks,
grid, nominal depth or original vectors. For every month and all 121 native
longitudes, sort latitude south to north. Enumerate every maximal consecutive
run of finite paired cells with strictly positive eastward velocity. An exact
zero breaks a run. Missing paired support breaks a run and remains missing.
Keep weak runs and boundary-censored runs, including those outside the earlier
2.5–6 S peak-search region. Do not assign these bands to the named current.

Retain each run's native row indices, global peak, equal-peak ties, every local
maximum plateau, and zero-crossing brackets. Exact zero and interpolated zero
are distinct. A source boundary or missing neighbor cannot close an edge.
Use the existing fixed-longitude component-span operator at 0.4/0.5/0.6 of
the run's positive global peak, requiring at least 0.02 m/s for that operator.
Resolve each threshold crossing in the full column, as in the original method;
record explicitly when a threshold interval extends outside its positive run
(it must not). Retain ties and multi-peak ambiguity; choosing the first equal
peak for compatibility does not prove a unique physical axis.

Connect runs only across adjacent native longitude columns when their native
positive row sets overlap. This is four-neighbor grid connectivity, not an
interpolated flow trajectory, transport connection or physical current edge.
Retain every eastward link, splits and merges; do not prune to a desired path.
Record undirected connected components and their source-boundary contact.
Threshold diagrams may visualize 0.4/0.5/0.6 spans but cannot replace this
strict-positive topology, and no diagonal or missing-cell bridge is allowed.

At each of the two previous 80⅓/80⅔ E sections, independently select the
strongest finite eastward cell in the historical 2.5–6 S search window, south
first on ties, requiring 0.02 m/s. Identify its positive run and connected
component, without clipping the run to that search window. Report absence,
weak support, splits, merges, competing equatorial reach and source truncation.
Compare all 72 historical monthly threshold cases at these two meridians to
the prior 2013 section calculations on their original 0–12 S domain. The new
domain ends at 10 S and extends to 2 N: retain changed, gained or lost edges
as domain-support differences; do not force exact agreement by repinning.

Report local meridional component spans with WGS84 geodesic distance, native
brackets and resolution flags. These are neither flow-normal widths nor
whole-current widths. No crest polyline length, velocity-axis admission,
physical annual range, state intersection or NASA identification is inferred.
Connectivity does not prove named-current identity. Render twelve section-band
maps, all runs and prior anchors, and a semantic monthly summary/source query.
Use consistent signed velocity colors and state missing/zero/boundary meanings.

Required verification: synthetic split/merge/diagonal/zero/missing/weak/tied
cases, independent graph partition, actual source/report reconstruction,
historical section comparison, figure inspection, native/WASM source queries,
keyboard/mobile card navigation, prior scientific-byte/typed-row preservation,
and exact staged source/dependency pins. Full-suite status remains separate.
