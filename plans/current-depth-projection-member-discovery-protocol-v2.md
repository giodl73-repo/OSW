# Member depth discovery refresh for inventory v36

Retain all rules in protocol v1 and freeze its original artifacts. This revision
links the unchanged declared membership to regional inventory v36, which adds
eight non-additive shallow/deep Atlantic SECC cases under one canonical owner.
Retain literal source pointers, original ownership, method/date/branch/window
context and gaps. New diagnostics are search contexts, not independent layers
or observations. Preserve their diagnostic_context_id and both false additivity/
independence flags in JSON discovery references and CSV link rows. Older cases
without these fields stay unspecified; do not assign new semantics to them.

Reuse frozen v1 discovery and inventory loader functions. Parent scalar depths,
ranges and volumes stay unknown. Own coverage remains 84 of 111 currents with
235 supported regional cases and 18 unresolved cases; family links add no cases
or measurements. Pacific NEUC remains an explicit member gap. All joins/tests
cloud-only, sequentially on one idle CPU. No field reads, numerical kernels,
runtime/query/browser/server integration or publication-cap changes.
