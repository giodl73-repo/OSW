# West Australian offshore diagnostic gap batch

Continues the same current-measurement branch and PR83. This adds an exact
archived vector section, twelve monthly component diagnostics and their
query/map/chart/source joins; it does not admit a full-current measurement.

Before velocity acquisition, OSW declared the 32 S / 60–116 E section,
80–105 E peak-search window, positive northward component, complete-pair
monthly support and 40/50/60% connected crossings. The exact OSCAR 2017.0
responses contain 72 archived times and 169 cells per time (12,168 vector
positions), including 144 missing pairs. The 1,055,888-byte CSV has SHA256
`cf9009f5b7d4797a7c0f7646262b93015cadafb59d546b2a06e127de7ff83a54`.
Provider metadata explicitly permits redistribution. Original bytes, exact
queries, version, timestamps and licensing are retained together.

Nominal monthly spans, January to December: **120, 190, 100, 150, 90, 90,
100, 90, 120, 110, 120, 90 km**. All 36 threshold scenarios have paired
crossings. Ten nominal spans are narrower than four native grid spacings.
The peak shifts from about 80.7 to 103 E. No tracked current identity,
continuity or annual physical width range follows from these values. The
90–190 km sample spread is a diagnostic spread, not a seasonal current range.
The historical narrow cyclonic-stream and broad government-synthesis width
conventions remain separate. Whole-current length/width and annual ranges
remain null; no route, footprint or seasonal map playback is added.

The full-domain twelve-panel figure shows all competing positive/negative
components, the editorial search window, crossings and missing support.
Missing support is hatched without claiming land. SVG title/description and
query data provide alternatives to color. The native/WASM query adds twelve
source-bound samples with frozen original-report verification. The dashboard
provides a monthly query link and profile-figure link for West Australian.

Counts: 214 exact source documents; 211 scoped query samples, including 84
monthly basin/component-section samples; 25 diagnostics and 17 series.
100 canonical names, 11 published lengths, 73 editorial routes, 136 scoped
source-width records and canonical scientific collections are unchanged.
Only the West Australian dashboard entry changes; observation dates remain
unchanged. This is additional diagnostic evidence, not physical gap closure.

Reproduce:

1. `python analysis/build_west_australian_oscar_spans.py`
2. `python analysis/build_west_australian_oscar_figure.py`
3. Rebuild motion dashboard, index corpus, query bundle, then Rust/native/WASM.
4. Run the full offline suite and basin-section/index-store browser gates.

Focused geometric/support gate: 13 tests and 11 subtests passed. Full suite
and browser gates passed; final results are recorded below.
Remote run 38521977446 at the preceding commit passed NOAA Florida acquisition
but stopped on a timeout at both Qiu institutional host forms. That failure
does not establish a checksum problem, a Melet failure or green remote CI.

## Final local verification

- Full offline suite: **1,358 tests / 995 subtests passed**, 1245.32 seconds (20m45s).
- Serialized native/WASM build: **46 Rust tests passed**.
- Basin browser: 84 monthly samples, seven owner charts/maps, native/WASM parity,
  manual selection/inspection/source links, 320 px reflow and five native/five
  WASM rejection cases passed. Additional native CLI check rejected a coherently
  rebound West Australian report and its samples.
- Index-store browser: 214 exact sources, twelve seasonal snapshots, independent
  NOAA oracle, native/WASM parity and checked-input failures passed.
- All 214 source hashes/byte counts and engine dependency pins verified.
  Prior scientific collections are unchanged; only the West Australian dashboard
  entry changes and all previous observation dates remain unchanged.
- Full-domain figure and mobile chart visually inspected. Internal role review
  permits this scoped diagnostic delivery; scientific admission remains pending.

Remote validation at the new publication head remains separate from these local
results. Neither a green remote CI result nor completion of the broader core-data
goal is asserted. The same draft PR remains the publication destination.
