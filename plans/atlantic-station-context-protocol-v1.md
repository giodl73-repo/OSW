# Atlantic station context protocol v1

This supplement recovers sampling geography for the Caínzos et al. (2023)
cruise-section spans. It does not change the width measurement protocol or
admit current boundaries, annual ranges, lengths, or state intersections.

## Source and identity

Archive the CCHDO integrated Dataset station summary bytes, URL, access date,
SHA-256, and byte count. Follow the CCHDO cruise citation and license policies.
The paper cruise identifier, archive page alias, and identifier printed in the
summary are separate fields. Never replace one with another silently.

## Events and positions

Parse each nonempty data line after the summary divider. Preserve its original
line number, raw text, station label, cast label, instrument, event code,
navigation code, date, time, and unparsed trailing metadata. Retain blank
section labels and repeated casts/events. Treat DOS end-of-file markers as
formatting. Fail on any other unparsed data line or invalid coordinate.

Convert degrees and minutes to signed decimal degrees; retain the original
degrees/minutes text. Archive values of exactly 60.00 minutes are carried
arithmetically to the next degree and explicitly flagged; larger minute values
are rejected. Coordinate precision is source rounding, not accuracy.
The geodetic datum and coordinate uncertainty remain unreported in this
extraction. No distance is recomputed from these positions.

WOCE manual chapter 3, section 3.3 specifies MMDDYY, UTC, and BE/BO/EN events.
Decode dates using the century of the paper's sampling window; retain the raw
date. Flag invalid dates and years outside the linked paper cruise windows.
Never repair a source date by substituting the cruise identifier's year.

## Visual context selection

For each published span select ROS/CTD events within its Table 1 sampling
window. Use one event per archive section/station/cast, preferring BO, MR, BE,
then EN, then another event in source-line order. This is a display selection,
not a paper station-index reconstruction or a quality certification. Preserve
all events in the audit. Show the selected positions as unconnected points on
the OSW basemap. No velocity, current path, width edges, footprint, or
intersected states may be inferred. If dates conflict, show an explicit gap
instead of a dated station map. Export exact records through the checked Rust
source store; use Rust cartography for browser display projection.

## Known unresolved mappings

The paper's sequential station-range labels may describe a model subset and
need not match archive station labels or counts. Rounded longitude agreement
alone cannot establish a boundary pairing. The 2018 A09.5 summary and Brian
King's 2018-04-23 CCHDO note identify a 24 S section, resolving the nominal
latitude conflict with Table 1's 19 S label. This evidence does not resolve
the paper's station indexing. The archived 2007 AR07E summary prints dates
ending in 05; preserve and quarantine this conflict before time-specific use.
