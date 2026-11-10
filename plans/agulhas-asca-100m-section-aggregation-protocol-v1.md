# ASCA100 m section aggregation rules v1

Effective17October2026. Source profile and calendar-month descriptions only;
no current width, boundary, footprint, annual extrema or climatology admitted.

1. Use only the frozen ASCA record20515068, product2.0, exact source100 m
   slices verified by analysis/check_asca_100m_source.py. Preserve all931 times,
   601 source distance cells, and separate temp/sal/v/U availability. Dataset
   interpolation and regression are not independent measurements at500 m spacing.
2. Preserve original float32 epoch seconds exactly in numeric and ISO UTC form.
   Use supplied calendar years/months. Nominal20-hour clock restoration remains
   a sensitivity check: deviations -64/0/+64 seconds produce no calendar changes.
3. Raw JSON transcribes each finite float32 value exactly to a JSON number;
   source NaN becomes JSON null. Original NaN bits remain in retained byte ranges.
   No zero filling, missing-value interpolation, temporal resampling or rounding.
4. For each of27 represented year-month bins, compute each field/cell mean using
   only its finite supplied values, equal source-record weights and float64
   accumulation. Keep integer valid counts. Count0 gives null mean and spread.
   Count1 gives its value and null sample SD. For n>1, descriptive sample SD
   uses denominator n-1. This is within-bin spread, not measurement error,
   standard error, a confidence interval or independent-sample uncertainty.
5. Keep scalar/component means separate from paired-vector means. For the latter,
   require both v and U finite at the same original time/cell; use identical
   masks and counts for both means. Never combine independently sampled means
   into a geographic vector, or interpret v alone as total speed.
6. A bin has complete calendar-time support only when its first sample lies
   within one nominal20-hour interval of month start and its last lies within
   one such interval of month end, allowing the64-second source float32 clock
   quantization bound in this coverage test only. Retain the tolerance explicitly;
   do not alter timestamps or field membership. Without this allowance, four
   genuinely complete nominal schedules would be labeled incomplete by64 seconds. This is temporal coverage, not every-cell
   completeness. April2016 and June2018 are partial. Retain all bins with labels,
   exact first/last supplied dates and their source profile IDs; do not drop the
   partial months silently or call the27 bins27 complete monthly observations.
7. Preserve source distance0-300000 m, depth100 m, degrees C, PSU and m/s.
   v is across-array, southwest negative; U is along-array, southeast positive.
   Do not restore missing U offshore, derive density from unlike T/S populations,
   rotate incomplete pairs, invent latitude/longitude edges or apply a buffer.
8. Chronological profile playback may step between recorded year-month means.
   It must retain years, incomplete-bin labels and support counts. No interpolation
   between frames, annual wraparound, seasonal extrema or typical-season claim.
9. Scientific boundary, core, reference-flow, interpolation-error and obliquity
   rules require original-method/corrigendum review before any dimensional record.
   Neither negative-flow span nor absence of a component establishes a full width.
