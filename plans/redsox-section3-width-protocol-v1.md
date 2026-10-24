# REDSOX winter Section 3: observed component spans, v1

Declared 2026-10-20, before computing the selected section's layer means,
projected components or spans. This is exploratory: the archive and earlier
cast 7–11 calculations were already inspected, and the original salinity
figure was viewed. It is not blinded or externally registered.

## Source selection

Use RSX1 cruise report Figure 7(a), printed/PDF page 21, titled Salinity Plume
Section 3, February 2001. Its left-to-right station order is
76, 75, 74, 73, 72, 71, 70, 59, 60, 61, 62, 63. Preserve that order, rather
than sorting velocities or joining another section. LADCP times span
22–23 February 2001: this is a non-synoptic section, not a seasonal mean.

Use the already verified NCEI 0146147 v1.2 ASCII LADCP and CTD archives,
their source inventories, filename joins and separate reviewed metadata.
The original LADCP README identifies ur/vr as east/north velocities relative
to Earth and hz as height above bottom. It does not explain tag upf or flag
up=0 sufficiently to resolve the previously excluded downcasts.

Pin the original cruise report and README in a source receipt; retain original
bytes outside the public packet. Do not redistribute original report imagery.
Use only source positions from LADCP for section geometry. CTD header/log
disagreements remain distinct in the companion inventory. Station 74 has no
distributed CTD companion; no salinity interpolation from other casts.

## Fixed operators and cases

* Geometry: WGS84 geodesic distance between consecutive source positions;
  cumulative chainage starts at station 76. At interior stations the local
  section bearing is the geodesic from the previous to next position; at
  endpoints use the adjacent leg. Right normal points toward the southeast
  for this source order. Do not reverse its sign using observed velocities.
* Component q = u cos(theta) - v sin(theta), theta the local section bearing
  clockwise from north. Keep both mean components and the normal azimuth.
  These are section-normal component spans along a bent observed section,
  not flow-normal physical current widths. No cosine width correction.
* Layers: primary 20–60 m above bottom, sensitivities 10–50 and 40–80 m.
  Reuse the existing REDSOX endpoint-interpolated trapezoidal layer operator:
  at least three original paired samples, complete monotonic height axis,
  both endpoints within observed support, no source gap over 20 m. CTD
  salinity uses the same source-depth knots and existing pressure-to-depth
  operator; never equate pressure with depth.
* Southern branch peak search: stations 75,74,73,72,71,70. Northern branch:
  59,60,61,62,63. These windows follow the two source-figure lobes, before
  the new velocity calculation. Ties select the first source-ordered cast.
* A primary branch peak search requires all its window's velocities usable.
  Reference=m (61,63) and unverified rejected-downcast treatment (63) are
  barriers, not zero velocity. An unsupported layer is also a barrier.
  Do not replace the peak with a convenient available cast. No conditional
  inclusion of excluded casts in this study.
* Peak q must be at least 0.2 m/s; its same-cast mean salinity must be at
  least 38 psu and speed at least 0.2 m/s for the saline outflow screen.
  Missing peak CTD means association unknown, never a passing screen.
* Walk contiguously from the peak in each direction, stopping at a missing
  value or an outer source-figure branch partition: Southern support is
  stations 76 through 59 inclusive; Northern support 70 through 63 inclusive.
  This allows flanking stations but prevents traversing the other branch.
  First below-or-equal threshold brackets each edge. Interpolate linearly
  in geodesic chainage between adjacent stations. Report both brackets,
  interpolated positions along their WGS84 leg and the chainage difference.
  No extrapolation beyond the section; retain single edges and null spans.
* Five scenarios per branch/layer: q fractions 0.5,0.4,0.6 without perturbation;
  fraction 0.5 with a uniform -0.03 and +0.03 m/s component offset. This
  finite perturbation is motivated by published winter velocity uncertainty;
  it is not an independent error model, confidence interval or tidal removal.
  Total 30 cases. Preserve every failure and every primary unknown.
* Report local spacing, span/maximum bracket spacing and span/median
  section spacing, plus peak vector obliquity to local section normal.
  Spans under four spacings receive a resolution flag, not suppression.

## Readback and admission

Decisions use unrounded calculations. Only derived output uses km 6 decimals,
angles 6, interpolated positions 8, mean/interpolated velocity 8 and salinity
6 decimals. Original source rows, positions, times and masks stay unchanged.
Public prose rounds km to one decimal, explicitly dated and local.

These measurements cannot establish a complete named-current width, annual
range, tidal correction, branch extent, whole-current length or physical OSW
intersection. Do not change the older lower Northern Channel result, physical
width inventory or rankings. An independently supported local section narrows
the observational gap while those larger admissions remain unresolved.
