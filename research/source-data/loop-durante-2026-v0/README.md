# Yucatan Channel - Loop Current manuscript figure repository

This repository reproduces the manuscript figures represented by the MATLAB code supplied with the paper. It contains compact, figure-ready processed data rather than the complete daily Canek and CMEMS/AVISO source archives.

G. Durante, 2026

## Contents

- `make_all_figures.m` runs every plotting routine.
- `plotting/` contains self-contained MATLAB plotting functions.
- `data/` contains only the variables consumed by those functions.
- `analysis/` documents how the processed files were generated from the full local analysis archive.
- `figures/` receives the reproduced PNG files.

The plotting functions use MATLAB built-ins only. Coastlines are intentionally omitted, which removes the dependency on `pongolfo` and its private coastline files. The repository also does not require `funcas`, `rgb`, `cmocean`, `prepara_sec`, `batsec`, `getCanekSCoor`, `getCNKprops`, or jLab plotting helpers.

## Reproduce the figures

1. Download the repository without changing its directory structure.
2. Start MATLAB in the repository root.
3. Run:

```matlab
make_all_figures
```

The command writes `Figure2.png` through `Figure10.png`, plus
`FIG_S4_reconstruction_40d.png` and `FigureS5.png`, to `figures/`.

The repository was prepared and tested with MATLAB R2023b. No source-data paths need to be edited to reproduce the figures from the included processed files.

## Processed data

| File | Figures | Contents |
| --- | --- | --- |
| `Figures2_4_processed.mat` | 2-4 | Leading MCA patterns and coefficients, composite maps and sections, LC metrics, lag correlations, and deep-transport diagnostics |
| `Figures5_7_processed.mat` | 5-7 | Second MCA patterns and coefficients, phase composites, lag correlations, and evolving event composites |
| `Figure7_processed.mat` | 7 | Positive and negative event intervals, projected mode-2 coefficient, and five-stage time-normalized composites |
| `Figure8_processed.mat` | 8 | Lagged pointwise and multiple-correlation maps |
| `Figure9_processed.mat` | 9 | Testing skill maps, three example dates, lead-0/lead-20 reconstructions, and LC-area timeline |
| `FigureS4_processed.mat` | S4 | Observed examples, 40-day local testing skill and reconstructed fields, and the LC-area timeline |
| `Figure10_processed.mat` | 10 | Curated event matches, resolved ring outlines, and detachment/no-detachment composites |
| `FigureS5_processed.mat` | S5 | Full detachment catalogue, preceding mode-2 critical points, and conditional composites |
| `FigureS5_events.csv` | S5 | Human-readable event table corresponding to `FigureS5_processed.mat` |

Each MAT file includes a `metadata` structure identifying the author, description, and, where applicable, its local source product. MATLAB serial date numbers are used for time variables, longitude is degrees east (negative values denote degrees west), latitude is degrees north, depth is metres, velocities are metres per second, transport is Sverdrups where labeled, and sea surface height/ADT is metres.

## Scope and provenance

The processed files preserve numerical values needed for plotting; they do not replace the complete observational and satellite products needed to recompute the analyses from first principles. The scripts in `analysis/` record the local provenance and extraction steps used to create the public files. Their absolute paths refer to the authors' private working archive and are not needed by repository users.

The large working files excluded from this package include full daily section matrices, full PLS coefficient matrices, and the complete gridded CMEMS/AVISO time series. For Figure 9, only the displayed dates and testing-skill maps are retained from the approximately 2 GB PLS result.

## License and citation

Please cite the associated manuscript and the Zenodo record. See `CITATION.cff` for machine-readable citation metadata. A license should be selected before public release, taking account of the redistribution terms of the underlying Canek and CMEMS/AVISO-derived products.
