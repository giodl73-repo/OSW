# Norwegian front-current measurement investigation

Continue draft PR83. This is source QA supporting the next measurement batch,
not a completed width extraction or a replacement for the corrected paper.

The publisher's authoritative article, doi:10.1029/2019GL084723, corrected
2020-09-28, reports 38 ± 2 km. The erratum explicitly describes corrected
georeferencing, recalculated parameters and updated supplementary material.
Older approximately 60 km results are not interchangeable. The Gaussian
integration rule includes positive poleward flow within a maximum ±2σ window;
its theoretical transport coverage is not a width confidence interval or FWHM.
Corrected supporting Table S1 remains unavailable through attempted publisher
access (403). HAL metadata identifies a record but supplies no main-file URL.

Two retained NMDC mission originals were newly checked, with exact SHA256
pins, CF time/component units, complete profile chronology and actual
coordinate alignment. Total 2,736 profile positions and 1,371 DAC records;
1,367 complete velocity pairs, with four missing pairs retained. Mission
history is Version 1, both created on 2019-02-28; MR2 continues past the
article's July 2017 scope. These files do not certify the 2020 correction.

Compare each overlapping DAC coordinate to the linearly interpolated profile
position at the same UTC timestamp, using WGS84 distance. Maximum offsets
are approximately 155 m and 41 m. This demonstrates internal agreement only,
without independent positioning truth or validation of the paper's
georeferenced interpolation. Glider position displacement rates are vehicle
motion, not ocean-current velocities.

**New metadata conflict:** in both originals, DAC_U's `standard_name` is
eastward, while its `long_name` calls it northward. Preserve both descriptions;
the visual uses direction-independent vector magnitudes. Validate direction
before fitting flow-normal widths. No axis swap or source correction made.

The audit retains exact positions, UTC times, missing components and original
metadata. A scientific SVG shows polar-stereographic sample positions,
coordinate offsets and recorded depth-average current magnitudes, with a
textual source/QA caption and JSON data alternative. These are sampling
positions, not a current track, width or occupied footprint.

Reproduce using the two original mission files downloaded from the audit's
NMDC source URLs into a local directory, then run:

```
python analysis/build_norwegian_front_source_alignment.py --source-directory <directory>
python analysis/build_norwegian_front_source_alignment_figure.py
python -m pytest -q analysis/test_norwegian_front_source_alignment.py
```

Attribution: Anthony Bosse and Ilker Fer (2019), Seaglider missions in the
Norwegian Sea during the PROVOLO project, University of Bergen / NMDC,
doi:10.21335/NMDC-980686647. The retained NMDC landing page explicitly lists
CC BY 4.0 and unrestricted access. Original binary files remain in the local
research cache; the public audit identifies download URLs, byte counts and
hashes. No placeholder original or alternative edition satisfies source guards.

The next scientific action is direction corroboration and independent
cross-front reconstruction, or recovery of corrected Table S1, rather than
copying 38 km to ambiguous canonical `norwegian`. Existing proposed Atlantic
branch identities remain separate from Norwegian Coastal Current. Canonical
inventory, measurement gaps, queries and dashboard fingerprints are unchanged.
This source audit and standalone figure are not yet wired into the atlas UI.

Verification: four focused tests passed, including independent coordinate
interpolation/distance checks, complete record/mask counts and metadata/admission
boundaries. Both source files reconstruct the audit from their pinned bytes.
The three-panel visual was inspected; the paper's July 2017 endpoint is marked
on both time plots. Core query engine and generated query/dashboard/index
artifacts are unchanged from the verified `a130c3e` batch. No new full-suite
result is claimed for this additive investigation.

## Subsequent atlas integration

The corrected Bosse width batch adds this audit to the checked source corpus
and links its visual and original-mission current records from the proposed
Norwegian Atlantic Front card. Source direction and corrected-method
reproduction remain unresolved; the new published width does not use these
raw records as its numerical reconstruction.
