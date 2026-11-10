# Source-reported current direction calendars: prospective protocol v1

## Quantity and support

Represent **qualitative source descriptions indexed by month**, not monthly
observations, model vectors, velocities, climatological averages with a known
baseline, dates in a sampled year, seasonal dimensions or predictions.

Two profiles are in scope. Shetye1998's accessible publisher abstract assigns
the West India Coastal Current a northward November–February phase and a
southward April–September phase. A short attributed excerpt was retained after
online inspection; the full paper was not accessed or retained. No independent
full-asset validation is claimed for that source. This narrower support is
visible in the report and diagram. The abstract alone directly supplies the
categorical month intervals; no quantitative flow analysis is attempted.

Vinayachandran et al.2021 section2.4.1 describes northward EACC orientation
throughout the year and contrasts it with the reversing Somali Current.
Use the pinned CC-BY4 original, PDF17 / printed5983. Section2.7.3, PDF26 /
printed5992, supplies an essential WICC qualification: shorter-term currents
can flow either way. This qualification prevents the calendar from becoming
a daily-direction guarantee. The complete review has not been reviewed page
by page; selected sections support this extraction.

Publication1998/2021 is not an observation year. Existing proposed current
identities remain separately gated; this source-stage product cannot itself
increment the live current catalogue or assert state intersections.

## Mapping rules

1. Each period has inclusive start/end months1–12 and a reported `northward`
   or `southward` category. Permit a period to cross December. Start=end
   represents one month, not an automatically full year.
2. Reject Boolean/non-integer/out-of-range months, unsupported directions,
   duplicate/overlapping assignments, wrong owner identity, invented years or
   observation windows, physical values and promoted admission flags.
3. Emit exactly12 ordered month records per profile. A month not covered by a
   reported period has null direction and `not_specified_by_source` status.
   Do not infer March or October as transition months or interpolate direction.
4. Preserve every month as a description of the source's annual pattern,
   including unspecified months. These24 categorical rows are not24 independent
   observations. All observed velocities, dates and physical dimension ranges
   remain null. Geographic seasonal playback and ranking remain false.
5. A calendar playhead could highlight a source description in the future;
   it must not imply moving physical axes, speed, width or geographic masks.

## Prospective freeze and verification

Freeze producer, source facts, identity review, protocol, synthetic tests and
preflight before actual report/SVG execution. Pin the retained review original
and acquisition receipt. The primary abstract excerpt is retained as explicitly
curated source support, not falsely presented as a complete original file.
No original publication is modified. Corrections after actual execution require
a new scientific version and retained failure history.

Synthetic cases cover year wrap, single-month/full-year periods, overlap,
invalid values, unknown months, non-promotion and accessible textual meaning.
The actual report and saved SVG must replay byte for byte. Independently
inspect the two actual calendars, source/access distinctions and preserved
unknowns; render and inspect the saved SVG without starting Chromium.
Native/WASM/query/card admission and browser validation remain batched gates.
