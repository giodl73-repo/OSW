# Abyssal Heat: Source or Transport?

## Status

This is a source-qualified research design, not a reported result. It defines
what OSW would need to map and test abyssal source-versus-transport
hypotheses. No focal input fields, solver outputs, or derived masks have been
imported into OSW.

## The question

Observed abyssal warming can reflect at least two different kinds of change:

1. a change in heat entering the ocean near the seafloor; or
2. a change in how circulation carries existing heat into the observed volume.

Those mechanisms may coexist, but a map of hot crust or known vents cannot by
itself establish either one. The decisive object is a budget on a declared
three-dimensional volume, with source, transport, storage, and uncertainty
kept separate.

## Four layers that must not be collapsed

| Layer | What it can show | What it cannot establish alone |
|---|---|---|
| Observed abyssal warming | the location, depth range, period, and uncertainty of a temperature tendency | the heat source or transport pathway |
| Conductive seafloor heat flux | an estimated spatial source field in watts per square metre | direct measurement in every cell or changing delivery to abyssal water |
| Lithosphere and vent opportunity | crustal age, spreading setting, and known or inferred vent locations | complete vent coverage, discharge power, or a global causal attribution |
| Circulation-mediated delivery | where a tagged source is carried under a specified velocity field and solver | truth independent of the reanalysis, remapping, boundary conditions, and numerics |

Temperature tendency, integrated heat content, source power, boundary heat
flux, and the fraction of a tagged source delivered to a target are different
quantities. OSW will not substitute one for another.

## Observational anchor and competing mechanisms

Johnson (2026) estimates that
globally averaged 4000–6000 dbar warming rose from `5.4 ± 4.9 TW` in 1988 to
`20.2 ± 3.9 TW` in 2018. The 2000–4000 dbar layer did not show a statistically
significant acceleration in that analysis. Those are sparse-hydrography,
globally averaged estimates—not a causal map of geothermal influence.

Conductive heat-flow estimates, crustal age, spreading context, and known vent
fields provide candidate source and opportunity layers. Testing a mechanism
requires more than spatial overlap: the warming field should be examined for
bottom intensification and water-mass structure, while a transport experiment
tests whether changing circulation alters delivery into the declared target.

## The clean transport experiment

The useful comparison changes one thing: the velocity history.

| Held identical | Compared |
|---|---|
| source field and normalization | monthly changing ORAS5 circulation for the declared period |
| target mask and vertical coordinates | the same months replaced by a repeating seasonal climatology |
| initial tracer and integration window | |
| ocean grid, source-to-ocean remapping, solver, boundaries, diffusion, time step, and output schedule | |

Before running it, the analysis must define:

- the exact geographic and vertical target support;
- whether `f` means target inventory/source input, target boundary flux/source
  input, or another dimensionally explicit ratio;
- the time interval over which both numerator and denominator are accumulated;
- treatment of heat leaving the domain or target; and
- the sign and magnitude that would count as evidence against the proposed
  circulation mechanism.

The primary contrast is

`delta_f_circ(t) = f_actual(t) - f_climatology(t)`.

It must be accompanied by, rather than substituted for:

- source and tracer conservation residuals through time;
- remap coverage, overlap, and power-conservation checks, including the ORCA
  tripolar fold;
- separate target inventory and target-boundary-flux diagnostics;
- basin, height-above-bottom, target-mask, diffusion, and resolution
  sensitivity tests; and
- uncertainty inherited from the observations and source construction.

## Evidence needed for an OSW result

To turn this case into maps or a reproduced result, OSW needs:

1. input source fields with provider, product, version, units, license, URLs,
   retrieval dates, and checksums;
2. the warming-acceleration field, uncertainty, positive-footprint rule, ocean
   mask, depth coordinates, and transformations;
3. exact ORAS5 variables, release/version, grid, monthly interval, and access
   recipe;
4. source-to-ocean remap weights plus coverage and conserved-power receipts;
5. solver source/version, configuration, numerical operators, boundary
   conditions, time-step record, and conservation log; and
6. matched actual and climatological outputs sufficient to recompute every
   plotted diagnostic.

Without those artifacts, OSW can map the question and candidate source
geography, but it cannot label a figure as a reproduced transport result.

## What OSW can contribute

- a public four-layer atlas that keeps observation, source opportunity, and
  modeled delivery visually distinct;
- co-located inspection of warming, bathymetry, crustal context, vents, and
  tagged transport without implying that overlap proves causation;
- a compact provenance receipt for every field and transformation;
- deterministic remap, conservation, and metric checks; and
- accessible maps that state what each view shows and cannot show.

## Stop conditions

OSW will pause causal interpretation if the compared experiments differ
in more than their declared velocity treatment, if the delivered fraction is
not dimensionally defined, if remapping fails its power-conservation check, or
if the result cannot be regenerated from shareable inputs and configuration.

## Sources

- [Johnson (2026), *Observed Multi-Decadal Acceleration of Globally Averaged Abyssal Ocean Warming*](https://doi.org/10.1029/2026GL124104)
- [Desbruyeres et al. (2016), *Deep and abyssal ocean warming from 35 years of repeat hydrography*](https://doi.org/10.1002/2016GL070413)
- [Davies (2013), *Global map of solid Earth surface heat flow*](https://doi.org/10.1002/ggge.20271)
- [Seton et al. (2020), present-day oceanic crustal age and spreading parameters](https://doi.org/10.1029/2020GC009214)
- [InterRidge Vents Database v3.4](https://doi.org/10.1594/PANGAEA.917894)
- [Zuo et al. (2019), *The ECMWF operational ensemble reanalysis-analysis system for ocean and sea ice: a description of the system and assessment*](https://doi.org/10.5194/os-15-779-2019)
