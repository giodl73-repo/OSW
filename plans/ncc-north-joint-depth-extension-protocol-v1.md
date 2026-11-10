# Norwegian Coastal northward joint depth extension

Collect two new editorial latitude sections61.5N[3,7]E and62.25N[3.5,8.5]E,
at March/June/September/December15,2022 00Z. These extend the original west-Norway
regional probes north of60.75N. They are new declared sampling gates, not changes
to any prior gate and not published observed axes or physical current edges.
Albretsen et al.2012doi10.1093/icesjms/fsr187 establishes the broader northward
low-salinity coastal-current context and distinguishes the adjacent Atlantic
flow; it does not supply our exact gates or measurements. The source's deeper
Atlantic100-200m layer is not assigned as an NCC bottom. Enge2025 supplies the
existing conditional practicalS<35 interpretation, not an absolute water-mass
identity test or a northern measured depth. No claim of reproducing either model.

Use HYCOM GOFS3.1expt93.0uv3z2022 andts3z2022. Preflight all8targets before fields:
exact corresponding native lat/lon/depth arrays,40levels0-5000m including100m,
unique exact time/date/index matches and source metadata. No nearest-date selection.
Use the unchanged native5km latitude tolerance,3-150profiles and20000cells/patch.
Reserve all three scalar fields jointly: Nvelocitypairs plusNsalinity scalars,
2Nnative units and24Nconservative decoded bytes. Retry extras count individually
against250000nativeunits/7MB,with all future first reads reserved. No per-field
budget reset. Only literal NetCDF:I/Ofailure RuntimeErrors allow up to3identical
attempts after2/5seconds;successful patches never replayed. Retain every receipt.

Retain both velocity components and practical salinity for every original native
column. Apply frozen complete0-100m northward signed-integral selector with primary
velocity>0.1m/s and5/10/20cm/s diagnostic sensitivities. No surface gate, thermal
gate, salinity-guided core replacement or threshold retuning. Unresolved axes
remain unresolved. Only the unchanged selected velocity core is tested with frozen
NCCpracticalS<35/component>0.1 predicate. Store both velocity-only and joint
diagnoses, exact finite brackets and missing/domain censoring. Salty cores do not
prove NCCabsence. Geographic maxima plus fresh classification do not independently
validate a coastal axis or exclude all branch mixing.

These are instantaneous regional conditional depth probes, not seasonal means,
annual extrema, physical currentbottom, full thickness, width, area or volume.
Do not connect new sections to old ones as continuous whole-current coverage.
Do not admit reference rows until separate reproduction/review. No replay of old
source fields. All retrieval/numerics/tests CLOUDONLY on one idleCPU, one job and
the existing branch/PR. Metadata/code/retention only locally. Keep all publication
caps, prior validated methods, main/runtime/UI/eddy data unchanged.
