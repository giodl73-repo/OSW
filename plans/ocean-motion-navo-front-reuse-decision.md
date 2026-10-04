# NAVO Gulf Stream frontal coordinates: reuse decision packet

Status: open for the v0.1.0 candidate; no provider inquiry sent.

The candidate preserves 510 north- and south-wall coordinates from the
Naval Oceanographic Office's 28 September 2026 Gulf Stream frontal bulletin,
distributed through [NOAA Ocean Prediction Center's Gulf Stream ASCII page](https://ocean.weather.gov/gulf_stream_text.php).
It exports two dated line geometries, their geodesic lengths, and eight
approximate OSW state intersections. The source bulletin and its SHA-256 are
pinned in `research/gulf-stream-navo-front-20260928.json`.

The OPC page identifies NAVO as provider. General NWS public-domain guidance
does not settle whether these NAVO coordinates have item-specific reuse or
attribution conditions. The bulletin is a dated infrared-satellite frontal
analysis, not a full Gulf Stream footprint or axis.

Before public repository publication or dataset deposition, obtain an
authoritative provider answer for redistribution of the 510 coordinates and
derived lines/state metrics; preferred citation and NAVO/OPC credit; coordinate
datum; and whether historical bulletin dates may be preserved in a versioned
atlas. Record the answer and exact scope in the source review ledger. If that
scope is not available, omit the coordinate-bearing source receipt and
geometry from a separately manifested public package, retaining source links
and reviewed factual summaries only.
