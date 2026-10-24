# Agulhas dated cases in the shared measurement inventory

Continue draft PR83. Source baseline: fba615abc3946e2310fe637af14d8e3c2cf9a657.
The gap is access to already calculated measurements: the ASCA source report
has 2,793 threshold cases from 931 dated profiles, but the shared query
inventory previously exposed only sixty REDSOX section cases.

## Required record rules

Extend `plans/current-section-measurement-records-v1.md` with explicit vertical
reference, component frame and time support. REDSOX heights above bottom
cannot be compared as depths with ASCA's nominal 100 m source level. The
REDSOX local normal component and the ASCA fixed-array −v component remain
different metrics. Inapplicable fields are null. The ASCA tidal-correction
method is unverified, not inferred from its 40-hour low-pass filter.

Copy every existing case and its peak metadata exactly. Retain stable
timestamp/fraction IDs, source profile IDs, exact UTC timestamps, source
index, year/month, exact source file checksum and per-case JSON pointer.
Each current owns only its own measurement IDs. All 2,853 cases are required:
60 REDSOX and 2,793 ASCA. There are 1,007 finite ASCA cases; 330 of 931 primary
cases resolve, and 601 primary cases remain unresolved. Three thresholds
reuse the same observations; they are not three independent measurements.

The adapter calculates no new velocities, peaks, boundaries, spans, geometry
or statistical ranges. Existing scientific reports, raw sources, widths,
width samples, routes, time series and figures must remain unchanged.
Whole-current width, annual range, verified association and ranking stay
unadmitted.

## Required query and visual access

The Agulhas card links to its filtered shared inventory. The query table
shows fixed-array component spans, nominal depth, source frame, threshold,
filtered/mapped time support and unresolved status. Date/year/month,
primary-convention and finite-value filters operate on the copied fields.
Record detail links to the exact source case and back to the atlas card.
Keep the existing 27-month source plots and all primary failures accessible.

The Python adapter and Rust validator independently rebuild every record
from the pinned source report. Reject altered values, frames, vertical
references, peaks, source pointers, duplicate/missing cases and mixed owner
lists. Verify actual native/WASM parity across every page, source-case
navigation, export and 320 px layout. Register these and the existing
REDSOX repeat-survey checks in the shipped browser validation runner.

The preceding EAC repair is separately pushed. Its 18-target Linux check and
the local dashboard tests retain their own tested-head scope; do not relabel
them as validation of this inventory extension.

## Verification

Four focused adapter tests and all 81 Rust tests pass. Actual native/WASM
parity covers every ASCA page, all 2,793 cases and the 931-primary/330-finite
filter counts. Exact source-case navigation, date filters, export and 320 px
layout pass. The REDSOX regression retains all sixty typed cases, thirty
summer cases, six unresolved comparisons, source links and mobile access.

Preservation against fba615a confirms all 44 other query collections and all
240 objects are exact except Agulhas's new owner-ID list. Every existing
REDSOX case and pre-existing metadata field is exact; only the five declared
vertical/frame/time fields are added. All eighteen scientific report bytes,
the source index and the width inventory remain exact. Browser source-object
queries return one row per property; the navigation check reconstructs the
entire exact source case rather than incorrectly expecting one object row.
