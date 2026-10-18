# Agulhas dated component-span gap batch

Baseline `ad97d6af13a1e8d80b2533a5cb03df1bde8f65ed`; continuing the same
current measurement branch and draft PR83. No separate PR or main merge.

## Question and declared operator

The existing ASCA100m source supplies931processed velocity profiles and27
calendar sections. This batch applies the separately declared
`agulhas-asca-100m-component-span-protocol-v1.md` to every original profile,
using the global southwestward v-component peak, a0.3m/s minimum and
40%/50%/60% peak-connected thresholds. Missing values stop a boundary search;
there is no alternate-peak substitution, interpolation through a null, coast
extrapolation, source rotation or filled velocity component.

The protocol was declared after earlier source fields and method limitations
had been seen, before these spans were computed. No blinded-test claim is made.
The source values, timestamps and chronological monthly membership remain
unchanged. All2793threshold outcomes and931profile records are retained.

## Results and scientific limits

At the primary50% threshold,330profiles resolve paired component spans and601
remain unresolved. Their missing sides comprise596missing-data barriers and
five section-domain truncations.40% resolves271profiles;60% resolves406.
Different thresholds are alternative assumptions, not extra observations or
uncertainty bounds. The primary resolved numerical spans range38.37–178.79km,
with median64.39km; this is a **sampled, conditional-on-resolved diagnostic
distribution**, not physical annual extrema or a whole-current width range.

Full500m boundary-cell brackets and minimum/maximum bracket separations are
retained as interpolation support, not measurement error or confidence.
500m is mapped output spacing, not instrument resolution. Whole-kilometre
display rounding does not establish kilometre resolving power. Local peak
alignment uses paired U/v when available; it neither supplies a section-wide
flow axis nor rotates the measured component span. Missing U stays missing.

The provider's product2.0 includes corrected processed fields. Original2022
corrigenda remain unreviewed: a renewed publisher request returned403 and the
available author/institutional metadata did not supply their full text. No
independent rotation repair or old published transport number validates this
experiment.40-hour filtering and20-hour subsampling make adjacent profiles
dependent. The complete original2GB file checksum is still unverified; exact
retained HTTP slices and reconstructed values remain independently pinned.

## Required information and visualization

The standalone SVG/PNG shows all931primary outcomes, every monthly resolved/
attempted denominator for all three thresholds, and original source sections at
prespecified indices0,465,930. Nulls break the source curves. The first fixed
profile remains unresolved rather than being replaced by a cleaner example.

The shared atlas-card, seasons and diagnostic-query widget supplies27recorded
month choices, sensitivity tables, every timestamp including failures, rounded
spans, grid support, peak component/alignment, human-readable boundary reasons
and links to both derived and original profile source rows. No synthetic
seasonal animation or geographic current polygon is added.

The query packet gains one diagnostic and one series within45collections.
All931derived outcomes remain queryable in the exact source corpus. Existing
27monthly sections, all463width samples,44earlier diagnostics and26earlier
series remain identical by value. An initial integration ordering issue was
corrected before publication to preserve the old Agulhas series ID and link.

## Verification and release gates

18focused Python tests pass in7.39seconds, including known crossings, plateaus,
peak ties, disconnected lobes, null/domain barriers, weak/absent flow, invalid
coordinates/values, local alignment without rotation, rounding, denominator
accounting, exact source reconstruction, figure hashes and forbidden admission.
All69Rust tests pass; actual native atlas generation loads the generated packet.
The strict compiled contract binds source, protocol, operator, figure and owner
join, rejecting coherent source rebinding and inventory promotion.

Final preservation passes: only Agulhas changes,239other dashboard/query owners
are identical;155width rows/81owners,11published lengths,76routes, dates and
geometry are unchanged.106engine,180research and355indexed-source working
pins and four served assets match. Actual browser and committed-byte gates
are required before pushing this diagnostic batch.

Actual browser gate now passes card/seasons/diagnostic, all27month options,
three sensitivity rows and all timestamp/failure rows in selected months,
four exact source queries, native/WASM diagnostic parity and eight corruption
rejections. Keyboard selection, source links, horizontal scrolling,320px
reflow and reduced motion pass; no page errors or automatic originals occur.
A separate actual source-query pagination check returns500+431rows with exact
native/WASM parity: all931indices once,330resolved and601unresolved. Final
standalone figure and mobile source table were visually inspected.

The last terminal complete pass remains c749116:1741tests/1159subtests in
2687.78seconds. A clean complete successor at ad97d6a is running and covers
the Kuroshio batch. It does not cover this new Agulhas experiment. Preserve its
actual terminal result and run a complete latest successor before main release.
