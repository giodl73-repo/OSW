# Agulhas satellite core width summaries

Read Krug and Tournadre (2012), doi:10.1029/2012GL052335, as two
author-reported regional mean width estimates. The complete original six-page
journal PDF has been read and visually inspected. Retain its acquisition
receipt; the copyrighted PDF and page images remain ignored.

Keep the along-track altimetry mean of 64 km separate from the SST mean of
80 km. Both refer to the dynamical core along Topex/Jason Track 020 offshore
Port Elizabeth, rather than the full Agulhas Current. These are different
operators with different temporal support, not two seasonal endpoints,
independent current surveys, or uncertainty limits. Preserve the mean core
and mean edge distances as reported context, not geographic edge coordinates.

The altimetry operator fits a Gaussian to the local southward velocity
maximum. The prose specifies edges at plus/minus one fitted standard deviation
but also describes these as a half-maximum region. Those descriptions are not
equivalent for a standard Gaussian. Retain that ambiguity, label the 64 km
value an author-reported Gaussian-core mean, and do not recalculate it as a
half-maximum width. The SST operator uses a local temperature maximum and
neighboring temperature minima; it is not a velocity threshold.

The study describes an 18-year altimetry record and its overall analysis as
1992-2011; it describes nearly seven years of SST. Keep exact mean-estimation
dates and sample counts null. June 2004-October 2011 is stated for the SST
gradient test on page5; do not silently assign that exact interval to the
width mean. The one-third-degree merged altimetry supports position comparison
and does not supply a third numeric width mean.

Retain the reported failure to detect an annual width cycle as a scoped study
finding. It is neither a zero-amplitude measurement nor a proof that width
does not vary: the paper explicitly describes rapid changes. No monthly width
values, annual extrema, confidence intervals, fixed depth, current footprint,
OSW state membership or seasonal animation may be inferred.

Before generation, freeze the source facts, acquisition receipt, this protocol,
producer and its validation tests in Git. The producer checks the frozen input
hashes and the two source records, then makes an original comparison plot and
machine-readable preparation report. Default replay is offline from retained
facts. Exact-original replay is a separate optional custody check, not a fetch.
Do not digitize source curves or reconstruct individual observations.

The plot shows two mean bars on a kilometre axis with explicit method labels,
no uncertainty whiskers, and a visible limitation about seasonal ranges.
Individually inspect its rendered PNG. Keep the plot and preparation receipt
bound by hashes. Existing installed measurements and widths remain unchanged
until a later source-index/native/WASM/atlas delivery is verified.

For runtime delivery, add these records to the existing scoped `widths`
collection, preserve all 172 existing rows and the Agulhas owner's old joins,
and keep both new rows free of width samples or seasonal-playback claims.
Expose exact source pointers and the comparison plot on query, atlas and
seasonal views, with the finding about undetected annual width seasonality.
Use one separately scoped cloud job and the existing branch. Verify all data,
source-index preservation and desktop/phone visuals before installation.
