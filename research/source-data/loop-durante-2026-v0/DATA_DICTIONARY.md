# Processed-data dictionary

G. Durante, 2026

All MAT files are MATLAB v7.3 files. Variables retain the names used in the analysis where this helps comparison with the archived scripts.

## Shared geometry and time conventions

- `xdu`, `ydu`: longitude/latitude grids.
- `inma`, `inmaf`: linear indices of valid ocean cells in a grid.
- `Xy`, `Zy`: Yucatan section horizontal coordinate and depth grids.
- `Xf`, `Zf`: Florida section horizontal coordinate and depth grids.
- `tid`, `htimef`, `tPC`, `timeline`: MATLAB serial date numbers.
- `U`, `V`, `ug`, `vg`: eastward and northward velocity components in m s^-1.
- `mg` and composite speed fields: geostrophic speed in m s^-1.
- `ad`, `absADT`: absolute dynamic topography in m.
- `anomADT` and `ADT*_a`: dynamic-topography anomalies in m.

## Figures 2-4

- `E_1`, `E_2`: Yucatan and Loop Current MCA spatial patterns.
- `T_1`, `T_2`: concurrent MCA temporal coefficients.
- `B_k_f`: Loop Current MCA coefficients projected over the full satellite record.
- `Cmax`, `Cmin`, `Umax`, `Umin`, `Vmax`, `Vmin`: positive/negative phase surface composites.
- `Uymax`, `Uymin`, `Ufmax`, `Ufmin`: section composites.
- `RR*`: correlation fields used in Figure 4.
- `DeepTime`, `DeepTransport`, `dum3`: deep-transport series and its integrated/smoothed form.

## Figures 5-7

- Variables ending in `2` are second-mode equivalents of the leading-mode fields.
- `RR2`: mode-2 lag-correlation maps.
- `mgEvo_m`, `adEvo_m`, `ugEvo_m`, `vgEvo_m`: onset-to-peak composite evolution.
- `m2`: thresholds, reference points, and event settings.

`Figure7_processed.mat` contains the manuscript Figure 7 event sequences:

- `projectedPC`, `htime`: full projected second-mode coefficient and dates.
- `positive`, `negative`: positive- and negative-event composites.
- `onsetDates`, `peakDates`: curated interval endpoints for each event family.
- `adAnom`, `adAbs`, `u`, `v`: five-stage time-normalized composite fields.
- `pc`: time-normalized coefficient for each individual event.

## Figure 8

- `RR_x`: correlation with Yucatan Current core longitude.
- `RR_y`: correlation with Yucatan Current transport.
- `RR_multi`: multiple correlation with both predictors.
- `lags`: lag in days; negative means the surface field leads and positive means the Yucatan metric leads.

## Figure 9

- `skillR2`: testing-period gridpoint R^2 at 0-, 20-, and 40-day lead.
- `observed`: observed fields for the three displayed dates.
- `predicted`: lead-0 and lead-20 reconstructed fields for the displayed dates.
- `LCArea`, `LCEddyArea`, `timeline`: lower-panel area series.
- `testPeriod`, `canekGap`: interval endpoints used for plot shading.

## Figure S4

- `skillR2`: local testing R2 for the reconstruction using Canek observations 40 days earlier.
- `predicted`: geostrophic speed, velocity components, and ADT for the three displayed reconstructions.
- `observed`: corresponding observed AVISO/CMEMS surface fields for the three target dates.
- `targetDates`, `predictorDates`: dates of each reconstructed field and the corresponding Canek observations 40 days earlier.
- `meanR2`, `meanR2Zero`, `relativeReduction`: domain-mean 40-day skill, simultaneous reference skill, and percentage reduction.
- `LCArea`, `LCEddyArea`, `timeline`, `testPeriod`, `canekGap`: lower-panel LC-area record and interval markers copied from Figure 9.

## Figure 10

- `Figure10.MeanderMatch`, `Figure10.MildnerMatch`: curated event-to-detachment matches.
- `Figure10.RingMeander`, `Figure10.RingMildner`: first resolved detached-ring geometry.
- `Figure10.PostComp*`, `Figure10.NoDetComp*`: composite ADT and velocity fields.

## Figure S5

- `Results`: one row per objectively detected detachment.
- `EventCritical*`: most recent preceding mode-2 critical point within the lookback window.
- `Separation*`: resolved detachment location and geometry.
- `CompNeg*`, `CompPos*`: composites conditioned on the sign of the preceding critical point.
- `Comp*NoDet*`: curated no-detachment comparison composites.
