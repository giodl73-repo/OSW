# Gulf Stream fitted-depth sensitivity to reported velocity-fit standard errors

Use all65 retained SprayS8TC9W selected profiles:five sections,one mean and12
fitted day15phases each. Preserve original product versions,2015-07-16to
2023-05-30fit period,provider timestamps and nominal phase labels. These are
fits,not instantaneous observations or monthlymeans. Existing100-level10-1000m
profiles are retained unchanged;this is not a new HYCOM retrieval or a change
to its40-level cap. Do not infer unselected deep sections from upper-layer data.

First reconstruct ALL retained10-200m horizontal candidate audits and original
selection with frozen select_axis. Only upper20native levels affect this audit;
fill unretained candidate deep levels with explicit missing,never invent values.
Reproduce original locked100m-direction projection and every nominal5/10/20cm/s
and half-core layer exactly. Do not select a more favorable axis/core/phase.

Provider uncertainty variables explicitly have CF standard_error names andm/s
units in retained metadata,confirmed against officialERDDAPmetadata pages.
For fixed source directiontheta,nominal downstreamm=u*sin(theta)+v*cos(theta).
Set h=abs(sin(theta))*SEu+abs(cos(theta))*SEv. This is the exact projection half
width of the componentwise +/-one-reported-SE rectangle. It is NOT a joint
confidence region,combined downstreamSE or Gaussian/covariance model. Both
componentSEs must be finite/nonnegative;missing remains missing,not zero.

For each original nominal half-core descriptor,LOCK its original core index
and numeric cutoff t=one-half original sampled nominal core component. Trace
frozen connected_layer from that single locked seed for m,m-h,m+h at fixedt.
No core reselection,threshold recalculation from perturbed peaks or direction
changes. A weak/missing lower-scenario core remains no_qualifying_core even if
another depth qualifies. Preserve first adjacent crossings and every missing/
domain censor. Only when both scenario lower crossings and nominal are finite,
retain their ordered sensitivity range. Fixed-cutoff pointwise ordering makes
lower/nominal/upper crossing order testable. No missing or1000m-to-bottom claim.

This is a deterministic sensitivity of a fixed nominal diagnostic cutoff. It
excludes cutoff,core-selection,direction and geolocation uncertainty and is not
a physical-current depth confidence interval or full error budget.10m is not
surface,1000m not bottom. Phase winners may move between source cells;cutoff is
fixed WITHIN each phase scenario,not shared across the year. Do not claim annual
extrema,physical seasonal envelopes,width joins or volumes. Source mapping
scales are not widths;fitcounts are not independent replicates.

Primary documentation reviewed: https://spraydata.ucsd.edu/products/gulf-stream-climatology/
and officialERDDAPinfo/gsMean/index.html andinfo/gsAnnualCycleDaily/index.html.
No new document custody or fields;retained provider attributes are the pinned
semantic evidence. Cloud-only sequential one idleCPU tests/numerics/build;
blockDataset/urlopen in newcohort tests. Local code/meta/hash/exactretention only.
Output2.4MB,file2.5MB,publication3MB caps retained. Original source,808-reference
inventory,102eddy refs,main/runtime/UI unchanged. No new scalar reference rows.
