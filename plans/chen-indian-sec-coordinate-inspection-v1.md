# Indian SEC coordinate metadata inspection

Inspect only lat, lon and time_year from the exact5,816,818-byte public HYCOM_CR original, SHA256 ce174a089a2379cd8c5a79ede226982749d9102a7e7b7d2d0a9180c75ac23cb7. This extends source metadata review; velocity and SSH fields remain excluded. Coordinate values describe the grid, not a current axis or physical boundary.

Reuse the frozen bounded acquisition helper. Refuse a changed original before any values are read. scipy.io.loadmat receives exactly the three coordinate names and must return only them, plus its normal administrative metadata. Require the shapes from the completed header inspection. Keep the full small coordinate vectors, their monotonic direction, bounds and spacing. Preserve a time-range mismatch rather than relabeling data to match the provider description.

The product is described as upper100m SON model fields during1993–2016. Even a matching year vector cannot establish units, averaging semantics or a physical current route. It does not supply a monthly climatology, annual length/width envelope or independent observations.

Use one cloud CPU at low priority, the existing shared queue, at most one original up to8MiB, a180-second command limit and a10-minute workflow limit. No local original download, velocity/SSH loading, measurement calculation, native/WASM build, browser task or installation. Upload only compact coordinate metadata and custody; discard the original cloud temporary file. Keep the global source-review phase unchanged.

After reviewing the actual coordinates, freeze any scientific route operator and regional gates separately before examining velocity fields or calculating length. Define model layer, direction, continuity, masking, sensitivity and visualization scope. Preserve the difference between a regional model-core proxy and a whole-current or observed surface route.
