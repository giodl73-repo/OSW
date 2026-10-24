# ASCA alignment-indicator readback v1

The full-source independent Linux reconstruction at `20b1017` reproduced all
fifteen other scientific reports exactly. In the ASCA report, only three
`/profiles/*/peak_alignment_indicator_deg` values differed, by at most
3.552713678800501e-15 degrees. Windows reconstruction matched the retained
report. Source packets, velocities, thresholds, boundaries, spans, masks,
timestamps, counts and all non-angle fields were identical.

Serialize this computed alignment indicator to six decimal degrees, using the
same Python round-to-nearest/ties-to-even convention as the existing scientific
readback policy. Preserve null indicators. This is reproducibility precision,
not observational accuracy, a new error bar or an angle acceptance threshold.

Apply readback only after every measurement and summary decision. Keep the
standalone `measure` operator at full precision. The indicator does not select
peaks, thresholds or crossings, and is not a physical flow-direction correction.
Do not round source U/v values, positions, original source array distances,
clock values, masks, thresholds, crossing fractions, metre coordinates or spans.

Keep the original component-span protocol and four frozen input packets
unchanged. Bind this declaration and the generator in the derived report;
renew its figure, query and engine bindings. Preserve all 931 profile outcomes
and 2,793 threshold cases, including every unresolved case. Verify that every
field except the declared indicator and provenance metadata remains exact.

Include ASCA full-source reconstruction in the independent Linux gate, alongside
the other fifteen reports. Strict report equality and byte equality remain
required; no tolerance is added to verification. This representation change
does not complete the full original-file checksum/corrigenda review, admit
physical current widths, establish annual ranges or alter any source-quality
limitations.
