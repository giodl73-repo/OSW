# P14N native-product source follow-up

2026-10-18. Declared after the exploratory hourly component spans, before
acquiring or inspecting fields in the two higher resolution products.

The original JASADCP gateway links `00016_short.nc` (Earth-coordinate ocean
velocities and selected ancillary parameters) and `00016_long.nc` (water
velocity relative to ship, ship velocity and ancillary parameters). HEAD
requests return 200, with 22,493,508 and 37,012,360 bytes respectively. These
response metadata establish availability, not field interpretation or quality.

1. Acquire both exact original responses, with URLs, UTC retrieval time,
   byte counts, hashes, this declaration and acquisition-code hashes. Default
   execution verifies local bytes offline. Explicit acquisition refuses to
   replace originals or an existing receipt. Validate NetCDF magic and size;
   retain source filenames in the receipt.
2. First audit metadata only: dimensions, variable names/attributes, source
   identity, coordinate/time units, missing-value conventions, QC semantics,
   navigation and velocity frames. Do not infer archived sample interval or
   bin spacing solely from the paper's instrument configuration. Do not inspect
   new ocean-velocity or ship-motion arrays before the next operator declaration.
3. The scientific question is whether underway section support can distinguish
   spatial branch boundaries from temporal crossings near CTD occupations.
   Keep the existing northern 44–46 N and southern 41–43 N windows. Do not
   enlarge them, select a preferred speed cutoff after viewing field results,
   or silently average through missing intervals or branch/eddy transitions.
4. Do not equate five-minute sampling with five-minute width accuracy. Chen
   and Firing (2006), section 2 paragraph 5, gives GPS-related two-SD velocity
   uncertainty 0.47 m/s at five minutes and 0.016 m/s for typical 2.5-hour runs.
   Neither is a complete width uncertainty model. Declare averaging, temporal
   support, orientation and independent physical-association checks before
   calculating a new span from these products.
5. Identify whether Earth-frame velocities already incorporate ship motion;
   never add it a second time. Ship-velocity standard deviation is not a
   current-width error bar. Native processing flags, original nulls and joint
   u/v/depth support must be retained and interpreted from source metadata.
6. Source acquisition/metadata audit does not admit a width, resolve a named
   branch, reconstruct physical edges or supply seasonal/annual ranges. Keep
   the earlier hourly velocity, CTD correspondence and component-span reports
   unchanged. The new files are a separate source stage on the same PR.

Primary gateway: <https://uhslc.soest.hawaii.edu/sadcp/DATABASE/00016.html>.
Paper: <https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005JC003064>.
