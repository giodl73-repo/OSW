# NOAA LSA geostrophic subset reuse decision packet

Status: open for the 2026-09-25 candidate velocity subset; no external request sent.

## Material and source

- The [NOAA CoastWatch LSA product page](https://coastwatch.noaa.gov/cwn/products/sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html)
  describes 0.25-degree daily altimetry-derived surface geostrophic currents.
- Exact NetCDF URL: `https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/rads_global_nrt_sla_20260925_20260926_001.nc`.
- NetCDF SHA-256: `53b1c541d4edf529bba2358f255890e2f0c392ef8e57208d04882c732c99f12f`.
- The candidate stores a 30–45°N, 80–45°W raw packed `ugos`/`vgos` subset,
  a reproducible frozen-time streamline, one unranked 2,277.3 km partial
  reach, and two approximate OSW state intersections.
- The repository also pins four research-only subsets dated 18, 24, 26, and
  27 September 2026 for a five-date repeat audit. They are outside the
  `v0.1.0/` package but still carry provider velocity values and therefore
  require the same source-use review before public repository publication.
- The source file identifies its product status as `Experimental`; its daily
  interval is 25 September 2026 UTC, with 26 September excluded.

## Use terms and citation

The NOAA product page says LSA data are distributed at no cost and asks
users of publications, presentations, or web pages to acknowledge the NOAA
Laboratory for Satellite Altimetry and NOAA CoastWatch. The page does not
explicitly grant an item-specific license for redistributing raw packed
regional subsets or clarify the terms of upstream altimetry contributors.
The candidate credits both NOAA groups and leaves source rights pending.

Before public repository publication or dataset deposition, record an
authoritative source-specific answer for redistribution of the five pinned
velocity subsets and derived diagnostic, required
data citation and contributor credit, and any product version or data-quality
note that must accompany this experimental daily file. If raw-subset terms
cannot be confirmed, publish only the derived factual diagnostic and links
to the NOAA files after review; keep the NetCDF and packed source subsets out
of the public repository and archive.
