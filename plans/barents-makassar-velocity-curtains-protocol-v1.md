# Regional depth variation from retained North Cape and Makassar velocity sections

Use all 32 original 2022 quarterly cases, four cuts for each current context.
Reproduce the frozen geometry, signed component rotation, every candidate score,
horizontal selection and selected-column threshold layers before deriving new
spatial descriptors. Preserve unresolved gate/support-edge winners without
substituting an interior core. Source axes, dates, thresholds and windows remain
unchanged. No ocean retrieval is performed.

At the original interior primary core, trace only native horizontal/vertical
neighbors whose original signed component strictly exceeds 0.1m/s. No diagonals,
missing bridges, reseeding or interpolation between columns or cuts. Preserve
separate vertical runs even when a native horizontal detour connects them. For
each run reuse the frozen vertical connected-layer function, seeded at its first
native depth, and retain finite adjacent crossings and all missing/domain censor
statuses. The original core run must reproduce its original boundaries exactly.

This velocity-only metric is separate from coastal fresh-component curtains.
North Cape is an eastward BSO regional proxy; Indonesian Throughflow is the
southward Makassar branch proxy. Neither independently validates named-current
axis or water-mass identity. A threshold layer is not the physical current
bottom. Do not infer physical width, area, volume or seasonal extrema, or add
duplicate reference inventory rows. Run numerics and tests sequentially on one
idle cloud CPU. Preserve the existing 40-level, 150-profile, 6000-node and 2.4MB
output bounds. Main/runtime/UI and immutable reference registers stay unchanged.
