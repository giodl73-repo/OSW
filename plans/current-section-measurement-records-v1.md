# Current section measurement records v1

`current_section_measurements` is a shared query collection for measurements
at an observed section, with declared layer, epoch and boundary convention.
It includes unresolved cases. It does not replace the scoped published width
inventory or assert a representative whole-current width.

Providers are the two frozen REDSOX Section 3 reports (sixty cases) and the
ASCA 100 m report (2,793 cases from 931 dated source profiles). Retain every
declared case, including source-quality failures, weak peaks, missing
boundaries and failed water-property screens. Do not select only finite spans.

Each record requires:

* A stable ID containing provider, campaign, branch, layer, boundary fraction
  and velocity-offset convention; stable current ID and owner binding.
* Both source observation bounds in UTC, source campaign and branch.
* An explicit `vertical_reference` and `component_frame`. REDSOX uses
  `height_above_bottom` with height-layer endpoints; ASCA uses
  `depth_below_surface` at exactly 100 m. Inapplicable height/depth endpoints
  are null, never zero or a converted substitute. Boundary fraction, applicable
  component offset in m/s, component span in km or null, and source status.
* The unchanged saline-outflow screen, source peak station, primary-convention
  flag and exact complete source case, including missing brackets/failure reasons.
* Exact source file, checksum and JSON pointer, plus the applicable calculation
  protocol. This adapter computes no new velocities, boundaries or spans.
* Explicit false whole-current admission, ranking and verified current
  association. Whole-current width and annual range remain null. REDSOX has
  no tidal removal; ASCA tidal removal is unverified/null. A low-pass filter
  does not establish a particular tidal-correction procedure.

For REDSOX, `metric=local_section_normal_component_span`. This describes a
span along the observed bent section at a fraction of its local normal
component peak. It is not a verified flow-normal physical width. Both source
surveys retain their own geometry; no geographic interpolation or seasonal
range is added by this collection.

ASCA uses `metric=fixed_array_southwestward_v_component_span` and
`component_frame=source_fixed_array_negative_v`. Copy the provider's existing
−v-component threshold cases, with exact UTC source timestamp, profile ID,
source index, year/month and local peak metadata. Timestamp bounds are equal
because they identify the filtered, mapped source record, not an instantaneous
instrument observation or an asserted averaging window. The 20-hour output
and 500 m grid are not independent observational support. Record
`time_support=filtered_mapped_source_timestamp`; REDSOX uses
`non_synoptic_section_survey`. Null offsets, saline screens, branches and
stations in ASCA are inapplicable, not inferred zero offsets or failed tests.
The primary convention flag selects 50% for all 931 profiles, including
601 unresolved primary cases. The other thresholds are alternative
assumptions on the same data, not additional observations or annual ranges.

The Python bundle adapter and native/WASM validator independently reconstruct
all records from pinned source cases. Require all 2,853 records and each
current's exact owner ID list (60 REDSOX, 2,793 Agulhas), source pins and metadata. Reject edited, missing,
duplicated, orphaned or promoted records, even if an attempted edit rehashes
the surrounding bundle. The existing Antilles-specific collection remains
unchanged. Adding a future provider requires a declared compatible metric,
source adapter, validator and preservation/readback tests.

The current card links directly to a main query of these records. The existing
source-document queries and scientific figures remain available alongside it.
