# Continuous temporal support for the Ingoy current sections

Continues `codex/current-measurement-gaps` and draft PR 83. The published 8130086 interface candidate has a separate clean combined gate running. Research additions here are isolated from that checkout.

## Gap and requested outcome

The existing 2024 Norkyst sequence contains one hourly reading on the fifteenth of each month. It cannot supply monthly averages, tide-attenuated comparisons, seasonal width ranges or annual extrema. Acquire continuous hourly coverage at the same 10 m layer and spatial subset so the temporal limitation can be addressed explicitly.

The target is all twelve calendar months of 2024. Start with complete January and July acquisitions to verify the archive, parser, filter and temporal accounting, then acquire the other ten months under the same rules. Neither the two-month stage nor the full year by itself establishes a named-current boundary or a whole-current dimension.

## Declared before new within-month values

`research/source-data/norkyst-ingoy-months-2024/preflight.json` records the timestamp and exact input pins. January/July first-day DDS and DAS metadata have been inspected. No new within-month velocity or salinity values have been acquired or inspected when that declaration is written. The earlier twelve hourly snapshots are already public and were previously viewed; this work is **not fully blinded**.

1. Use the MET Norway/Institute of Marine Research Norkyst v3 hindcast, hourly, 2024, depth index 6 verified as 10 m on every daily response. Keep the existing Y `576:4:764`, X `2420:4:2616` subset. Its 3.2 km source spacing is a four-cell decimation of the 800 m native model.
2. Preserve original packed eastward/northward velocity and salinity, daily sea masks, actual time/depth and projected-coordinate axes, metadata, URLs, acquisition times and byte checksums. Read fill before scale/offset. Verify daily field units, packing, projection and project/license. Metadata is not velocity data.
3. Target every UTC hour in each complete calendar month, plus 36 hours on both sides. January and July each have 744 requested monthly hours and 816 acquired hours including the halo. The 2024 target has 8,784 monthly hours; no leap day may be omitted. Do not skip an unavailable day or silently replace pinned bytes.
4. At 24 E, retain the existing 191 section positions from 71.10 to 73.00 N. Bilinear interpolation requires all four wet, non-fill corners in all three fields. Approximately 1.1 km display spacing adds no spatial resolution.
5. Apply an explicitly defined 71-point symmetric kernel: convolution of normalized 24-, 24- and 25-hour boxcars. Its support is 35 hours on either side. Preserve the unused extra halo hour; do not pad or interpolate across gaps. Require all 71 paired hourly readings for each filtered section reading.
6. Keep raw hourly profiles and low-pass profiles distinguishable. Compute monthly mean, standard deviation and hourly-sample quantiles only for a complete monthly series at that section position; otherwise retain null summaries and the support count. These describe model temporal variation, not confidence intervals or measurement uncertainty. Monthly standard deviation uses the population convention (`ddof=0`).
7. Explain that this filter attenuates tidal bands and also changes other high-frequency variability. It is not a harmonic tidal solution or an assertion that every tidal contribution has been removed. Weather-driven variability, model bias and spatial sampling limitations remain.
8. Do not compute a current width, tune a threshold or join a physical footprint in this preparation. Independent current association, an explicit boundary operator, paired edge support, obliquity and spatial resolution still require review. The existing patch is offshore and does not establish a coastal boundary. Two months are not a seasonal climatology; twelve monthly profiles are not continuous annual physical width extrema.

## Primary method/source references

- Christensen et al. (2026), Norkyst v3, DOI `10.5194/gmd-19-2785-2026`, model description and Code and data availability: <https://gmd.copernicus.org/articles/19/2785/2026/>. Hindcast includes tidal and atmospheric forcing; the archive provides hourly output. Per-file metadata supplies the data license and packed variable conventions.
- USGS, tidal-filter utility documentation: <https://water.usgs.gov/usgs/osw/adaps/tidal_filter.html>, especially the 71-hour minimum and 35-hour trimming on each side. Its utility processes discharge; OSW implements the stated linear kernel independently for model section variables and does not claim the USGS utility validates this ocean-current application.
- The older OSW source, interpolation and map protocol remains separate: `plans/norkyst-ingoy-section-sampling-protocol-v1.md`. No old reading, receipt, map or frame is overwritten.

## Reproduction and presentation requirements

Retain deterministic original-response archives with per-member hashes and acquisition receipts. Default analysis/tests must use the local originals; refreshing a source is explicit. Reject incomplete cadence, duplicate times, changed packing/projection, out-of-domain sections and malformed arrays. Test filtering phase, normalization, constant/linear signals, synthetic oscillation attenuation, missing-support propagation and month/halo accounting.

Create a section-versus-time visualization and a comparison of the old single-hour reading with the complete raw and low-pass monthly profiles. Provide numeric support counts, units, date/layer/model/source labels, missing-data treatment and textual alternatives. Integrate only after the acquisition and method checks pass. Keep existing physical measurements, route geometry and source artifacts unchanged.
