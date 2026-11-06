# Current depth evidence cards

Build an offline, queryable presentation packet for all identities in canonical
inventory v38. Preserve each reference's original quantity, censor flags, units,
definition, citation and geographic/temporal qualifications. Organize quantities
into core position, transport selection, layer thickness, scoped boundary/proxy,
and published extent/component context. These are presentation roles, not a new
scientific taxonomy or confidence score. A proxy does not establish a physical
current bottom. A core is not a lower boundary. A thickness is not a depth below
the surface. Different references are never averaged or merged into an envelope.

No member evidence is inherited by parent systems. Missing data remain null.
There is no headline whole-current depth, inferred annual range, volume, new
measurement, new acquisition, or runtime/UI change. The output exposes the data
already held and distinguishes boundary/proxy support from context-only support.
It does not fill a measurement gap or establish independent observation counts.

Run synthetic semantic checks and the actual descriptor join sequentially on
one idle cloud CPU with one shared 60-second clock, absolute alarm and SIGTERM.
Use DescriptorQuery v3 with explicit zero prior counters: at most 250000 numeric
tokens, 32MB unique JSON, 2.5MB per packet, reservation before JSON decoding,
and no native/source-data reads. Keep all outputs together below 2.4MB. Check
the complete JSON and every CSV cell by actual roundtrip. Freeze v1 after a
successful run; future changes use a new version.
