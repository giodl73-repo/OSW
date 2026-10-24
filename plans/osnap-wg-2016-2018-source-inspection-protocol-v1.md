# OSNAP West Greenland 2016-2018: prospective source-header inspection

Status: prepared; no original archive execution, measurement admission or
cloud dispatch authorized by this file alone. The active delivery queue runs
first. A committed preflight and bound execution workflow are required before
this producer can access the archive. Freeze this version before original
execution; corrections after execution require a new version.

## Source and selection

Use dataset DOI `10.35090/fz80-6c32` and the exact provider archive address,
byte count, central-directory fingerprint and 78 instrument candidates in
`research/west-greenland-osnap-2016-2018-archive-inventory-v1.json`.
Retain the original ZIP bytes and original member names. Do not select only
`.nc` filenames: the reviewed archive contains two extensionless candidates.
Ignore resource forks, dotfiles and directory entries as instruments.

The README describes eight LS moorings. Do not claim complete coverage of the
ten-mooring paper array or silently merge the separate coastal, slope and deep
current components. Preserve this deployment's provider license and attribution;
do not inherit a license from another deployment.

## Before original access

Run the tiny synthetic guard/inventory tests. Review the source and resource
scope. Commit a prospective preflight binding the producer, tests, this protocol,
the two reviewed source records, pinned requirements and the eventual cloud
execution workflow, plus the repository role review. The producer checks committed bytes and hashes before
networking. Do not create that preflight until the execution workflow is ready.

## Execution and evidence

Run only in the cloud with explicit `--cloud-inspect`, one CPU and low process
priority. Require 2 GiB free disk and available memory. Download at most the reviewed archive size,
with a ten-minute download budget. Record the complete archive SHA-256 before
header inspection; verify its central directory and every selected member's
metadata and ZIP CRC. Read at most one 64 MiB instrument member in memory.
Never extract archive paths onto the filesystem.

Record acquisition start/completion times, request and response metadata,
provider license link, reported deployment period and first execution commit.
An exact replay preserves that first-acquisition record; do not replace its date
or source commit with the replay's values.

Inspect file signatures, NetCDF dimensions, variable names, data types, shapes
and attributes. Retain units, fill values, quality flags, accuracy and processing
notes as attributes, including explicit nonfinite representations. Do not read
observation variable arrays. Reject nested groups and user-defined enum, compound
or variable-length types rather than omit their structure; supporting them
requires an explicitly reviewed version. Cap each header at 256 KiB and the report at 8 MiB;
fail rather than silently truncate. Existing custody/report bytes may only be
reused when exactly identical. Raw originals remain in the cloud artifact store.

## Limits and next gate

The result establishes original custody and source schema only. It supplies no
current width, length, monthly distribution, annual range, mapped edge or state
intersection. Header attributes do not prove physical sample validity. Actual
timestamps, coordinates, depth coverage, missingness, motion/blowdown handling
and velocity processing need a later reviewed source-support stage.

Any width derivation needs its own prospective identity, layer, orientation,
edge and censoring protocol, synthetic checks and freeze before actual widths
are calculated. Source-header inspection does not authorize that calculation
or working-dataset admission.
