# Waves, Tides, and Oscillations

*A pattern can cross an ocean even when the same body of water does not.*

## Object cards

| Object | Restoring force or driver | Identifying signal | Typical motion |
|---|---|---|---|
| Surface gravity wave | gravity after surface displacement | surface height spectrum and direction | propagating orbital motion plus possible drift |
| Wind wave | local wind stress | short-period locally forced spectrum | propagating and growing/decaying |
| Swell | distant weather | organized wave energy beyond generating wind | freely propagating |
| Tide | lunar/solar gravitational forcing with rotation and geometry | harmonic water-level constituents | periodic vertical displacement |
| Tidal current | same tidal forcing | harmonic horizontal velocity | reversing or rotary flow |
| Internal wave | buoyancy in a stratified interior | displacement/velocity on density surfaces | propagating within the water column |
| Rossby wave | potential-vorticity dynamics on a rotating sphere | broad slow phase propagation | usually westward phase propagation |
| Kelvin wave | gravity and rotation with equatorial/coastal trapping | boundary-trapped height and velocity anomaly | directional propagation along guide |
| Inertial oscillation | Coriolis response after forcing | velocity near local inertial frequency | rotating horizontal motion |

## Pattern motion is not parcel motion

```text
wave crests:       /\      /\      /\                 travel →
                  /  \    /  \    /  \
water parcels:       ○↻      ○↻      ○↻                mostly orbit
mean drift:          ·──────►                         can remain
```

In the leading linear picture, water parcels oscillate while phase and energy
propagate. Real finite-amplitude waves can leave a residual **Stokes drift**;
breaking waves, wave-driven currents, and nonlinear internal waves can also
transport water and tracers. The useful distinction is therefore not “waves
never move water,” but “wave propagation does not by itself establish bulk
advective transport.”

[NOAA's introductory explanation](https://oceanservice.noaa.gov/facts/wavesinocean.html)
emphasizes energy propagation; operational wave models separately diagnose
Stokes drift and transport
([NOAA WaveWatch III manual](https://polar.ncep.noaa.gov/waves/wavewatch/manual.v5.16.pdf)).

## Tide is not tidal current

```text
                   water level                    horizontal velocity

high tide       ───────────────                  flood  ─────────►
mean level      ─ ─ ─ ─ ─ ─ ─                  slack       0
low tide        _______________                  ebb    ◄─────────

                   TIDE                           TIDAL CURRENT
```

They are two components of the same forced response but different measured
objects. Tide is conventionally the periodic vertical rise and fall. Tidal
current is the horizontal motion, which may reverse in a channel or rotate
offshore. High water need not occur at maximum flood, so local phase belongs in
the object record.

NOAA represents both as sums of harmonic constituents with amplitude, phase,
frequency, and astronomical identity
([Tides and Currents glossary](https://tidesandcurrents.noaa.gov/glossary.html)).

## Surface tide and internal tide

When barotropic tidal flow crosses rough topography in a stratified ocean, some
energy can convert into an internal tide. Density surfaces then rise and fall
far below the sea surface.

```text
surface tide  ─────────────────────────────────────────
                  → flow over ridge
upper layer   ───────────────\       /\       /\
                               \____/  \_____/  \__  internal tide →
lower layer   ___________________/\___________________
seafloor                          ridge
```

Generation, propagation, breaking, and mixing are separate claims. Internal
waves can transfer energy and momentum through the interior; only their
breaking and associated turbulence establish irreversible mixing. GFDL
describes tides and winds as major sources of internal-wave energy for
stratified-ocean mixing
([GFDL Ocean Mixing](https://www.gfdl.noaa.gov/ocean-mixing/)).

## Rotation creates different wave grammars

| Mode | What makes it distinctive? | Classification warning |
|---|---|---|
| Rossby | potential-vorticity dynamics and latitude-dependent rotation; very broad and slow | not an ordinary surface swell |
| Equatorial Kelvin | trapped near the equator, with a preferred propagation direction | a warm tongue is not automatically the wave itself |
| Coastal Kelvin | boundary-trapped, with coast and rotation selecting direction | coast shape and stratification matter |
| Inertial | local frequency set principally by latitude and rotation | a looping drifter path may also contain tides and mean flow |

Oceanic Rossby waves can strongly displace the thermocline while producing much
smaller sea-surface-height signals
([NOAA Rossby waves](https://oceanservice.noaa.gov/facts/rossby-wave.html)).
That is another reason a surface map can understate subsurface motion.

## Similar coastal heights, different objects

```text
ASTRONOMICAL TIDE   predictable harmonic forcing
STORM SURGE         storm-driven residual above predicted tide
TSUNAMI             long wave from sudden large displacement
SEICHE              standing oscillation selected by basin geometry

observed water level = tide + surge + waves + other residuals
```

A high water mark does not identify its cause. Storm tide combines surge with
astronomical tide; ordinary wind waves can ride on top. A tsunami is not a
“tidal wave,” and a seiche can continue sloshing after its initiating weather
or seismic disturbance.

The sum is a conceptual decomposition, not permission to add arbitrary reported
heights. Components must share a vertical datum, location, time support, and
compatible statistic; instantaneous crest height, significant wave height,
predicted tide, and peak surge are not directly additive maxima.

See the [National Hurricane Center surge definition](https://www.nhc.noaa.gov/surge/),
[U.S. Tsunami Warning Centers](https://preview-tsunami8.ncep.noaa.gov/?page=tsunamiFAQ),
and [NOAA's seiche guide](https://oceanservice.noaa.gov/facts/seiche.html).

## The decisive tests

1. Name the observed variable: elevation, pressure, velocity, density-surface
   displacement, acceleration, or wave spectrum.
2. Declare sampling interval, record length, frequency band, and aliasing risk.
3. Identify forcing and restoring mechanism rather than classifying by shape alone.
4. Report wavelength, period, phase direction, group/energy direction, and depth structure.
5. Separate oscillatory velocity, residual current, Stokes drift, and net transport.
6. Test latitude, stratification, coast, basin, and bathymetric sensitivity.
7. For mixing claims, diagnose dissipation or irreversible property change—not
   merely the presence of internal-wave energy.

## OSW consequences

OSW's monthly ORAS5 gate experiments resolve mean opposing branches but not the
full tidal cycle or submonthly covariance. This matters especially in narrow,
shallow Indonesian passages where tides and mixing can be dynamically large.
A monthly section result must not be described as the total instantaneous
current, tidal exchange, or native time-stepped tracer transport.

[Compare Indonesian grid readiness](../figures/osw-m3-indonesian-grid-bakeoff-2018.svg)
and [return to the gate measurement contract](04-GATES-TRANSPORTS-AND-RELAYS.md).

## Planetary connection

Gas-giant atmospheres also contain waves, jets, vortices, and oscillations, but
their restoring forces, vertical modes, compressibility, forcing, and observed
levels must be matched explicitly. Similar undulations in two images do not
identify the same wave mode.

[Apply the planetary comparison protocol](07-OCEANS-AND-GAS-GIANTS.md).

## Common mistakes

- Saying waves transport no water under any circumstances.
- Treating crest speed as current speed or parcel velocity.
- Calling tidal current “the tide” without naming the measured component.
- Assuming high tide coincides with maximum flood current everywhere.
- Equating internal-wave presence with irreversible mixing.
- Calling any slow broad anomaly a Rossby wave without testing phase propagation.
- Calling a tsunami a tidal wave or adding storm surge and wave height as if
  they shared one datum and statistic.
- Averaging away an oscillation and then concluding it was dynamically absent.

## Next

[Plumes, Upwelling, and Vertical Exchange](../CLASSIFICATION.md#next-research-layers)
will distinguish source-tagged material bodies from vertical-motion processes.

[Field Guide index](README.md) · [Seafloor and Topographic Steering](08-SEAFLOOR-COASTS-AND-TOPOGRAPHIC-STEERING.md) · [Classification](../CLASSIFICATION.md)
