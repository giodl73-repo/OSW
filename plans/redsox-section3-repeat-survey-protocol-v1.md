# REDSOX Section 3 repeat survey: fixed comparison, v1

Declared 2026-10-20 after viewing the original summer salinity figure and
LADCP/CTD availability, positions, references, quality notes and height ranges,
before computing selected summer layer velocities, salinities or spans.
Exploratory, not blinded or externally registered: the archive, winter section
and summer salinity figure have already been inspected.

## Source and station correspondence

Use the original RSX2 cruise report Figure 7, top panel titled Salinity Plume
Section 3 – August 2001, printed/PDF page 19. In source left-to-right order,
the twelve stations are 18 through 29 inclusive. The PDF text-object extraction
order places the rift title first; rendered page/title/labels govern selection.
Do not confuse the bottom along-rift panel (110,112,113,115,118,119,121,125)
with the transverse plume section.

Match these source-identified stations one-to-one, in figure order, to the
already measured winter section [76,75,74,73,72,71,70,59,60,61,62,63].
Retain both original positions and WGS84 pair separations. A pair must be
within 2 km to qualify as repeated station context. Never copy winter values
to summer, interpolate onto the other transect or assume identical geometry.
Preserve both source clocks: winter 22–23 February and summer 23 August 2001.

Pin the summer original PDF receipt and the original winter report, protocol
and generator. Original report imagery remains outside the public packet.
Use existing verified NCEI 0146147 v1.2 LADCP/CTD ZIP archives and parsers.

## Identical measurement conventions and explicit quality barriers

Reuse the frozen winter v1 geometry, local right-normal component, layer and
hydrography operators unchanged. Primary height above bottom is 20–60 m;
sensitivities 10–50 and 40–80 m. At least three original paired samples,
complete monotonic height support, both endpoints observed and maximum
20 m source gap. No bottom extrapolation. Preserve both Earth-frame means.

The source figure fixes corresponding peak windows: Southern 19–24 inclusive,
Northern 25–29 inclusive. Southern flanking support 18–25, Northern 24–29.
Use first source-ordered tie, require every peak-window velocity usable,
require peak normal component >=0.2 m/s and walk contiguously to the first
bracket on either side. Missing/excluded casts are barriers; do not jump over
them, substitute a convenient peak or enlarge the figure section.

The same-cast salinity >=38 source psu and mean-vector speed >=0.2 m/s screen
is unchanged. Its failure or missingness must remain visible. Summer source
salinity is already visibly lower; do not lower the screen to obtain matches.
A paired component span may be reported with a failed/unknown saline screen,
but cannot become a verified named-current width.

Summer cast22 has an authored bad-upcast note and tag downf. The distributed
product's component treatment is unverified: exclude it from all primary
peak searches and crossing support, retain its raw metadata, and leave the
affected branch unknown. A tag name is not proof that the bad component was
removed. Also exclude any uninterpretable reference=m and any other authored
component-quality note. Do not produce a conditional inclusion fallback.

Five cases per branch/layer: fractions 0.5/0.4/0.6 at zero offset, plus
fraction0.5 with uniform offsets -0.04/+0.04 m/s, following the existing
summer-quality convention. Winter's original -0.03/+0.03 scenarios remain
unchanged. These finite offsets are not error distributions or confidence
bounds. Preserve all thirty summer outcomes, including every failure.

## Comparison and readback

Form six branch-by-layer dated comparisons at fraction0.5, zero offset only.
Report both original spans, outcomes and saline-screen statuses. Only when
both same-branch spans are supported and both screens pass may their numeric
difference be supplied, explicitly a difference between these two dated
section metrics. Never compare winter Southern to summer Northern as a
seasonal change, or average branches to fill missing outcomes.

Preserve original winter report bytes and all previously admitted inventories.
Keep derived readback precision exactly as the winter v1 rules; decisions
remain at full precision. Station-pair geodesic separations use 6 decimal km.
Source coordinates, clocks, flags and joins remain unchanged. Record all
inputs and generator hashes and include this report in exact independent
Linux reconstruction. Unit checks must verify method identity after explicit
station renaming and prevent comparisons that combine different branches.

This provides two dated surveys, not a climatology, annual extrema, annual
width margins, tidal correction, physical current edges, current axes, ranked
whole-current widths or physical state intersections. No such admission is
authorized by a paired source section alone.
