# Kuroshio axis and boundary dataset, Wang et al. (2026), edition1

Wang, Jiahao; Chen, Xi; Mao, Kefeng; Zhang, Chengzhuo. **A daily
three-dimensional dataset of the Kuroshio axis and boundaries in the East China
Sea and Luzon Strait.** Scientific Data13,915 (2026).
[Paper](https://doi.org/10.1038/s41597-026-07275-3).
[Dataset edition1](https://doi.org/10.6084/m9.figshare.30267070.v1),
[CC BY4.0](https://creativecommons.org/licenses/by/4.0/).

The provider metadata snapshot inventories32 annual originals,1993–2024.
Only2024 is acquired here: the latest complete year, selected before extraction.
The original contains366 day groups, each with30 depth groups. The included
provider plotting example is retained byte-exact for documentation, never run.

`kuroshio_2024.nc.gz` is a byte-exact compressed provider original, not a new
NetCDF serialization or a selected-variable subset. The original has130603298
bytes; SHA256:
`82375f6da17f83f462fc574ea8fc710f79e11cc8e63f5fd010091ea8d3a6946c`.
Provider MD5: `945fd3bba891a2d12e640ee0ea582348`.
The acquisition receipt records both compressed and uncompressed hashes and
retrieval time. The locally retained uncompressed file is ignored by Git.

The producer verifies gzip and original hashes, reads the original directly
from memory, checks day/level inventories and units, and extracts the three
predeclared levels without requiring network or creating another disk copy:

```powershell
python analysis/kuroshio_wang_dimensions.py
python -m unittest analysis.test_kuroshio_wang_dimensions -v
```

See `plans/kuroshio-wang-2024-dimensions-protocol-v1.md` for conventions and
`research/kuroshio-wang-2024-regional-dimensions.json` for every case and
rejection. The map derivative is
`figures/kuroshio-wang-2024-monthly-snapshots.svg`. Derivatives add WGS84 regional
lengths and fixed-latitude spans; displayed source coordinates are rounded to
six decimals. Original data bytes are unchanged. These model boundaries can
include unflagged search-window fallbacks and do not establish observed widths.

The other31 years and27 unextracted depth levels remain work. Typed native/WASM
query and atlas linkage use the separate integration contract
`research/kuroshio-wang-2024-query-contract.json` and protocol
`plans/kuroshio-wang-query-atlas-protocol-v1.md`. Scientific source data carry no
live UI-status flag. Whole-current ranking and width inventories are unchanged.
