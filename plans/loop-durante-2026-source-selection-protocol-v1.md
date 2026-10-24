# Loop Current Durante2026 source intake v1

20 October 2026, before downloading or decoding numerical MAT members.
Metadata, README and source/plotting MATLAB scripts have been read. Existing
OSW Loop Current diagnostics and Manta et al.(2023) are known. This is a new
archive, not Manta's2023supplement or an independent replication of it.

## Exact public archive

Zenodo22652650, DOI10.5281/zenodo.22652650, Durante, Analysis and
Figure-Reproduction Code for Loop Current-Yucatan Channel Covariability from
Altimetry and Canek Mooring Observations. Published2026-09-08, record version0.
Public API snapshot SHA256
`ca9e7925815c108c6afcd43f95cd223fb984a3eff3ac5395d4ca8d4204a73c9a`.
The API declares open access and CC BY4.0. README still says a license should
be selected before release; retain that documentary disagreement. CITATION.cff
says1.0.0, unlike record version0. The associated manuscript DOI is a
placeholder. Do not infer peer-review/publication status from journal metadata.

Numerical archive:
`https://zenodo.org/records/22652650/files/data.zip?download=1`,
exact14,212,662bytes, provider MD5`db5a3615a6b103ff8b2311530785e0c0`.
Verify provider checksum, compute SHA256, preserve bytes and UTC/HTTP receipt.
Use ordinary certificate-verified HTTPS, max20MB per response. No overwrite
of earlier originals. Save source bytes before validation; preserve failures.
No execution of downloaded MATLAB code.

Already acquired source references, to preserve with original responses:

- README.md: SHA256`d6ef4f328147f1bf7dd467282728ab99056b4aa8d7d8db071289bb132b337631`.
- CITATION.cff: SHA256`f71d9191d3f929a771f4a4b89ffc48bb7cf3c5a6387fe05d7cfbb5bf7d979767`.
- analysis.zip: SHA256`08f305cbbab18348bdd43064597eace684538abbf4479a5893761ca4fb584ba6`.
- plotting.zip: SHA256`ef9e395e0d422be37f460c0b95a290fe7ba31258f60218754dd911f9ccfe94aa`.

## Selection and initial inspection

1. Inspect every ZIP entry name, size, checksum/CRC and compression support.
   Reject duplicate names, absolute/traversing paths or symlinks. Enforce
   total uncompressed limit150MB and per-member limit50MB. Extract by explicit
   address; never blindly unpack an archive into the workspace.
2. Read any data dictionary/license/manifest as metadata before numerical
   interpretation. The record mentions DATA_DICTIONARY.md and MANIFEST.sha256;
   do not assume they exist or silently invent their contents if absent.
3. Initial numerical focus is the complete `Figures2_4_processed.mat` member,
   wherever the ZIP actually locates it. Preserve every field and source bits,
   including missing values. Retain array names, dtype, shape, MATLAB class,
   dimension ordering and native object/reference structure before converting.
   Initial schema inventory may inspect every numerical member's headers and
   metadata, but no other member's scientific arrays are selected for analysis.
4. Inspect source fields named by the author's plotting/preparation scripts:
   `CurAxisPositive`, `CurAxisNegative`; associated positive/negative U/V and
   ADT composites; grids/masks and author phase-selection indices; `tid`,
   `tisp`, `htimef`, `area_loop`, `AMR_loop`. Preserve all source positions and
   timestamps, not only apparently complete or appealing examples. If these
   differ or do not exist, record the discrepancy and stop that claim.
5. MATLAB times use serial date numbers according to README. Verify source
   time dimensions, actual encoded hours, ordering, duplicates, gaps and support.
   Do not flatten distinct time bases or assign observations to processing dates.
6. The author constructs the two axes by pointwise means over selected phase
   indices. They are conditional composite coordinates, not daily paths or
   seasonal axes. Recover dimension correspondence, finite-mask support and
   endpoint/gate meaning before treating their points as a continuous path.
   No bridge across missing coordinates, extrapolated endpoints or inferred
   ordering. Do not equate length of a pointwise mean with mean path length.

## Initial outputs and inference limits

Produce source custody/metadata/schema and quality records: source field
coverage, coordinate/time association, finite/missing values, source units
where explicitly documented and unresolved meanings otherwise. Preserve
private-author provenance paths only in the retained original; public derived
records use archive-relative addresses, not dependencies on those paths.

Do not rename `AMR_loop` as a particular physical area without dictionary/code
support. Never infer length from area, width from area/length, or a physical
current footprint from the enclosed area of a streamline. Reconstructed/modal
fields, conditional composites and original mapped fields stay distinct.

This archive contains processed source products, not full CMEMS/Canek raw
observations. Actual variable presence, manuscript status, source effective
resolution, parent-product rights/attribution and scientific quantity meaning
must remain visible. No current length, width, annual extrema, route inventory
admission, OSW-state join or new eddy identity is authorized during intake.
Declare any geometry measurement and visualization protocol separately before
calculating new distances or interpreting source polygons.
