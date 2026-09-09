# GEOMAR Agulhas derived replication subset

These three compact NetCDF files are unmodified selections from the final data
archive for Schmidt, Schwarzkopf, Rühs, and Biastoch (2021), *Characteristics
and robustness of Agulhas leakage estimates: an inter-comparison study of
Lagrangian methods*.

- Archive: https://hdl.handle.net/20.500.12085/b704e917-09dd-4a73-b6a1-ea24a549920c
- Paper: https://doi.org/10.5194/os-17-1067-2021
- License: Creative Commons Attribution 4.0 International
- Original creator metadata and license attributes remain embedded in each
  NetCDF file.

`fetch_geomar_agulhas_derived.py` pins SHA-256 checksums and retrieves only the
published section geometry, four example trajectories, and annual transport by
exit section. Raw INALT20 model output is not redistributed by the archive and
is not present here.

OSW's JSON receipt recalculates `West + Northwest` from the archived annual
section transports. It is an attributed replication of the published model
output, not a new OSW simulation or observation-only estimate.
