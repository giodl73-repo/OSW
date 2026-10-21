# Current section measurement records v1

`current_section_measurements` is a shared query collection for measurements
at an observed section, with declared layer, epoch and boundary convention.
It includes unresolved cases. It does not replace the scoped published width
inventory or assert a representative whole-current width.

The first providers are the two frozen REDSOX Section 3 reports. All thirty
cases from each report become records, including source-quality failures,
weak peaks and failed water-property screens. Do not select only finite spans.

Each record requires:

* A stable ID containing provider, campaign, branch, layer, boundary fraction
  and velocity-offset convention; stable current ID and owner binding.
* Both source observation bounds in UTC, source campaign and branch.
* Height-above-bottom layer endpoints in metres, boundary fraction, uniform
  component offset in m/s, local component span in km or null, and source status.
* The unchanged saline-outflow screen, source peak station, primary-convention
  flag and exact complete source case, including missing brackets/failure reasons.
* Exact source file, checksum and JSON pointer, plus the applicable calculation
  protocol. This adapter computes no new velocities, boundaries or spans.
* Explicit false whole-current admission, ranking, verified current association
  and tidal removal. Whole-current width and annual range remain null.

For REDSOX, `metric=local_section_normal_component_span`. This describes a
span along the observed bent section at a fraction of its local normal
component peak. It is not a verified flow-normal physical width. Both source
surveys retain their own geometry; no geographic interpolation or seasonal
range is added by this collection.

The Python bundle adapter and native/WASM validator independently reconstruct
all records from pinned source cases. Require all sixty records, their exact
current-owner ID list, source pins and metadata. Reject edited, missing,
duplicated, orphaned or promoted records, even if an attempted edit rehashes
the surrounding bundle. The existing Antilles-specific collection remains
unchanged. Adding a future provider requires a declared compatible metric,
source adapter, validator and preservation/readback tests.

The current card links directly to a main query of these records. The existing
source-document queries and scientific figures remain available alongside it.
