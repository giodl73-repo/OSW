# North Atlantic event missing-term audit

Status: bounded archive audit; no missing process is inferred

Date: 2026-09-12

## Scope

Audit the variables actually admitted by OSW's six daily NOAA RTOFS 00 UTC
nowcast retrievals for the 2026-08-07 through 2026-08-12 North Atlantic box.

## Result

| Needed budget term or diagnostic | Admitted by current retrieval | Disposition |
|---|---|---|
| potential temperature | yes | supports fixed-depth storage proxy |
| horizontal `u`, `v` | yes | supports offline Eulerian horizontal-advection screen |
| native tracer tendency / conservative flux convergence | no | unresolved |
| vertical velocity / vertical advective tendency | no | unresolved |
| vertical mixing or diffusion tendency | no | unresolved |
| shortwave penetration profile | no | unresolved |
| assimilation increment | no | unresolved |
| changing layer-depth/entrainment tendency | no | unresolved |
| GFS surface-energy forcing | separate crossed-system product | scale comparison only; not closure |

The RTOFS source fields used by `fetch_rtofs_mhw_upper_ocean.py` are
`temperature`, `u`, and `v` on standard depths. Its 2-D companion contributes
diagnostic mixed-layer thickness only to the separate D11/D12 surface screen.
Neither payload exposes a native conservative heat-budget tendency.

## Consequence

The 0–100/200 m candidate calculations may describe compatible fixed-column
storage and offline horizontal-advection scales within one newly retrieved
RTOFS response. They cannot close a budget, identify vertical mixing,
assimilation, or shortwave deposition, or be joined to the frozen D13/D14
chain until source-version reproducibility is resolved.

The remaining partial residual is therefore explicitly **unresolved**.
