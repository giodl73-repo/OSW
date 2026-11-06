# West Spitsbergen interval depth diagnostic

This method adds a separate model diagnostic to the retained January 15 and
July 15, 2022 West Spitsbergen sections. It uses the same eight horizontal gates,
native coordinates and original velocity profiles as the surface-screened
experiment. Original cases, operators and source files remain immutable.

Menze et al. (2019), section 4.3, maps currents averaged over 20–500 m. This is
context for OSW's selection interval, not a published current-bottom definition
or validation of the model's axes. The source covers northern Svalbard summers;
extending this diagnostic to the retained 73–79.6 N reach and both 2022 dates is
an OSW exploratory choice. No source curve or field is digitized.

Source: <https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JC014299>.

## Selection rules

1. Use the original signed northward component, held at 0 degrees true through
   depth. Require actual native levels at both 20 and 500 m.
2. Require every native velocity sample within that interval to be finite.
   Missing values remain null. Do not interpolate across missing support.
3. Compute the signed trapezoidal integral over those native levels. A column
   qualifies only when this integral is positive and its maximum in the interval
   is strictly greater than the primary cutoff of 0.1 m/s.
4. Apply no surface-velocity qualification. Missing or opposing surface flow is
   allowed; the subsequent contour calculation still retains its upper-boundary
   consequences.
5. Select the largest integral. Exact ties keep the first western native index.
   Retain every candidate score, qualification flag and local maximum.
6. A selected gate-edge maximum or a maximum adjacent to missing interval support
   remains unresolved for along-route projection. Do not substitute a weaker
   interior column or select using whether its depth happens to resolve.

## Vertical boundaries and projection

Reuse the frozen connected-layer calculation at 0.05, 0.1 and 0.2 m/s, with each
cutoff's own maximum constrained to 20–500 m. Starting from that seed, follow
connected support up and down through the entire retained native depth axis.
The lower crossing may therefore lie below 500 m. The interval endpoints are
selection limits, not assumed current boundaries.

Crossings require adjacent finite samples bracketing the cutoff. Missing/dry
support and the sampled domain edge censor the corresponding boundary. A top
of zero requires connected threshold support reaching the actual surface.
Retain upper depth, lower depth, their statuses and brackets, supported-reach
bounds, and thickness when both boundaries resolve. Lower depth and thickness
remain different quantities.

Reuse the frozen adjacent-anchor interpolation. Only adjacent original anchors
with interior selection and resolved primary lower depths support a connector.
Paired layer-span interpolation additionally needs both vertical boundaries.
Unselected sections retain explicitly unsampled midpoint reference geometry.
No gap skipping, extrapolation or replacement by another cutoff is permitted.

## Provenance and interpretation

The derived report contains diagnostics and pointers, not duplicate velocity
arrays. Raw profile pointers target the immutable original source; contour
pointers target the derived report. Preserve the original surface-selected index
and diagnosis reference alongside the new selection.

The comparison group is `model_interval20_500_no_surface_gate`. Do not pool it
with surface-screened cases into an apparently observed seasonal range or treat
the two methods as independent evidence. Reanalysis makes no new provider field
requests and adds no independent observations. Original transport, publication
and processing caps remain unchanged.

Geographic maxima do not establish named-current or Atlantic Water membership.
No temperature/salinity gate, bathymetric axis, physical whole-current thickness,
annual envelope, width/depth area, volume or state join is admitted. All current
coverage outside the retained regional reach remains unfinished.

## Required checks

Cloud verification must cover subsurface flow with opposing/missing surface
support, nonzero upper boundaries, lower crossings below 500 m, censoring,
signed integration, native-level requirements, western ties, selection/support
edges, and preservation of the original surface method. Pipeline checks must
verify all 16 original section/date cases, distinct raw/derived pointers,
operator/source mutation rejection, every earlier scenario and CSV cell,
ownership, exact hashes, fixed byte caps and explicit method separation.

All ocean-profile processing, geometry, interpolation and tests run sequentially
in the cloud on one idle CPU. Local work is limited to code, metadata, source-text
review, hash checks and retention of exact cloud-produced artifacts.
