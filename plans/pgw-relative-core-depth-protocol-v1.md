# Persian Gulf outflow source-relative core-depth scenarios

Use only the already retained and source-reviewed Pous2004 downstream context:
the approximately300km source path from R14 to R02 has net core shoaling less
than30m. Depth means depth of the salinity maximum, positive downward. The source
does not give exact absolute endpoint depths or a mapped current axis here.
Keep all original registers, source methods and unresolved route cases intact.

Construct a separate conditional regional scenario family. Let x be source-path
distance from R14 in [0,300]km and s be an illustrative endpoint shoaling with
0<s<30m. OSW assumes linear relative change delta_z(x)=-s*x/300. This assumption
is additional to the source's endpoint constraint: neither monotonicity nor
pointwise intermediate limits are established by the paper. Querying outside
the domain or at the excluded shoaling limits must fail. No endpoint rounding
may silently convert the strict30m bound into an admissible scenario.

The primary profile is relative: no absolute depth datum is required or inferred.
For an explicit optional illustration only, use z_R14=200m based on the coarse
regional near200m description. This is an assumed R14 datum, not an observed R14
anchor or an exact assignment of the R18-R17 depth reference to R14. Label every
absolute sample accordingly; retain the null-datum relative profile beside it.

Predeclare s=5/15/25m as three unweighted illustrations. None is a preferred
estimate, probability quantile or uncertainty interval. Evaluate at50km display
spacing, with arbitrary interior query support. Spacing is not station spacing
or measurement resolution. Neither the scenario family nor source spatial
variation is an annual/seasonal range. Do not combine these samples with the
post-R17 approximately200km description as independent lengths or an exact join.

Campaign sections were occupied on different dates. No exact common occupation
time, geographic geometry/state intersection, flow-top/bottom/thickness,
cross-sectional shape, width join, area or stored volume is inferred. This
partial core-depth scenario belongs in a separate source-relative class, not
the old geographic native-velocity projection class. No new primary observations
or depths are claimed; the improvement is an evaluable, source-constrained depth
scenario over a previously unprojected regional reach.

Cloud only, sequential single idle CPU. No ocean-field requests, PDF/figure
downloads, archive parsing or curve digitization in this operator. Pin all
inputs and the previously validated source review. Output<=2.4MB; perfile<=2.5MB.
Retain exact successful JSON/CSV artifact once and record its cloud review.
No UI/runtime changes or original copyrighted assets are distributed.
