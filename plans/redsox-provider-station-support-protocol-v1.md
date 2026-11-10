# REDSOX provider station-record support audit v1

Exploratory, after selected original methods and several existing records were
read. Freeze this protocol, operator, source review and input checksums before
the first full-archive classification. This audits445 velocity profiles and
all461 CTD metadata records; it does not calculate velocities or widths.

Reconstruct both existing metadata inventories from their retained original
archives with the frozen upstream parsers. Require complete equality with the
published inventories. Require one velocity profile per cruise/station and
one CTD profile per cruise/filename station; duplicates are errors, never a
nearest-neighbor choice. For every velocity profile retain its exact original
filename join or explicit missing companion. Retain all unmatched CTD records.

The documentary basis establishes a combined instrument package, not exact
sample synchronization. A pair has `consistent_provider_station_records` only
when campaign and filename station match, the CTD header independently states
that same station, both decoded inventory position values match exactly, and
both valid UTC timestamps fall on the same reported UTC date. These are
provider-record consistency checks, not independent geographic or physical
cast verification. Preserve all failed checks and missing fields. A different
reported date needs review, not an invented correction or a claim that the
records must describe different physical casts. Never select another station
by closest position or time, accept a tolerance, or substitute reviewed fields
for raw header fields. Copy existing reviewed support separately.

Retain both original timestamp roles and their exact integer-second difference.
Either sign may occur; do not reject a pair solely on timestamp order. This
difference is not cast duration, an instrument lag estimate, or a shift to apply
to data. Retain the original filename-join object and all source quality notes,
reference-family/processing tags and header conflicts. Metadata consistency
does not clear rejected profiles, unknown reference tags, lack of tide removal
or sampling-resolution gates. Explicit synchronization limitation applies to
the documented REDSOX-2/REDSEA packet-loss context; do not assert it occurred
in REDSOX-1 or claim that winter synchronization was verified instead.

Every output keeps `physical_cast_identity_verified=false` and
`sample_level_synchronization_verified=false`. The new positive result means
only provider station-record fields agree under the declared rule. Never
rewrite old inventories, their historical false flags, section reports,
measurements, width-owner counts, current identities or geometry. Retain
failure/missing outcomes and both campaigns in equivalent form. Reconstruct
the entire new report byte exactly offline, and test the actual445/461 coverage
independently of the report's own count fields.
