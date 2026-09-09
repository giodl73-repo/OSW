---
skill: discover-websearch
topic: ocean plumes, upwelling, and vertical exchange
date: 2026-09-05
claims_checked: 5
confirmed: 5
---

# Web grounding — plumes, upwelling, and vertical exchange

## Scope

This pass tests the boundaries needed for OSW Guide 10. It does not attempt a
global plume or upwelling inventory. Searches paired definitions with mechanism
terms and preferred agency, institutional, review, or primary-literature pages.

## Claim 1 — upwelling is vertical motion, not a water-mass name

**Verdict: confirmed.**

1. NOAA defines upwelling as a “process in which deep, cold water rises,”
   explicitly classifying it as a process rather than a named body of water.
   <https://oceanservice.noaa.gov/facts/upwelling.html>
2. The same NOAA page states that it occurs both offshore and at coastlines;
   “upwelling” therefore does not imply one coastal geometry.
   <https://oceanservice.noaa.gov/facts/upwelling.html>
3. NOAA identifies downwelling as the reverse response when surface water
   accumulates at a coast and sinks. This supports paired but separate motion
   objects. <https://oceanservice.noaa.gov/facts/upwelling.html>
4. NOAA Fisheries describes its upwelling index as offshore surface transport,
   not a direct measurement of every vertical velocity. A forcing proxy and the
   realized flow must remain distinguishable.
   <https://www.fisheries.noaa.gov/west-coast/science-data/local-physical-indicators>

## Claim 2 — coastal, equatorial, and curl-driven upwelling require different geometry

**Verdict: confirmed.**

5. NOAA's coastal account says surface water is moved offshore and replaced
   from below; coast orientation and wind direction are part of the test.
   <https://oceanexplorer.noaa.gov/wp-content/uploads/2025/04/upwelling-information-handout.pdf>
6. Kessler's eastern tropical Pacific review reports that “Ekman divergence
   transports surface water away from the equator,” producing equatorial
   upwelling. <https://www.pmel.noaa.gov/pubs/outstand/kess2580/cycle.shtml>
7. The same review warns that the SST and nutrient response depends strongly on
   background stratification. Upward transport alone does not prescribe a fixed
   thermal signature. <https://www.pmel.noaa.gov/pubs/outstand/kess2580/cycle.shtml>
8. Kessler also ties Ekman pumping to wind-stress curl and documents strong
   curl-driven upwelling around the Costa Rica Dome. This is neither merely a
   coastline nor the equator. <https://www.pmel.noaa.gov/pubs/outstand/kess2580/dynamics.shtml>

## Claim 3 — a plume is source-tagged material whose rise and spread are processes

**Verdict: confirmed.**

9. NOAA PMEL states that hydrothermal fluid rises because it is buoyant and
   entrains ambient seawater until neutral buoyancy.
   <https://www.pmel.noaa.gov/pubs/outstand/bake1538/bake1538.shtml>
10. PMEL then distinguishes the later stage: the neutrally buoyant plume
    “begins to disperse laterally.” Rise, entrainment, and lateral intrusion are
    related stages, not synonyms. <https://www.pmel.noaa.gov/eoi/PlumeStudies/plumes-whystudy.html>
11. The Annual Review of Fluid Mechanics defines river plumes as buoyant river
    water entering the coastal ocean and emphasizes dynamically distinct
    regions, variable forcing, and geometry.
    <https://www.annualreviews.org/doi/10.1146/annurev-fluid-010313-141408>
12. A 2024 JGR study reports that a river plume can transition into a coastal
    current in the far field. The source-tagged body and organized velocity
    structure can overlap without being the same object.
    <https://www2.whoi.edu/staff/dralston/wp-content/uploads/sites/147/2024/09/RalstonEtal_JGR_2024_MobilePlume.pdf>

## Claim 4 — meltwater and sediment-bearing cases need source-specific tests

**Verdict: confirmed.**

13. An ice-shelf plume model includes both ambient-water entrainment and basal
    meltwater input as separate fluxes, so “meltwater plume” requires an ice
    source and buoyancy/property signature.
    <https://tc.copernicus.org/articles/12/49/2018/>
14. USGS observations identify a dilute turbidity current by excess density,
    sediment concentration, velocity, and down-canyon propagation—not by a
    generic discolored-water shape.
    <https://www.usgs.gov/publications/small-scale-turbidity-currents-a-big-submarine-canyon>
15. A larger Monterey experiment found both moving water-saturated sediment and
    sediment-laden water. “Turbidity current” cannot safely be reduced to an
    ordinary passive plume. <https://www.usgs.gov/news/large-underwater-experiment-shows-turbidity-currents-are-not-just-currents-involve-movement>

## Claim 5 — vertical displacement, cross-density mixing, and heat transport are distinct

**Verdict: confirmed.**

16. GFDL notes that interior ocean flow is predominantly along density surfaces;
    vertical movement in depth coordinates does not automatically imply
    cross-density conversion. <https://www.gfdl.noaa.gov/ocean-model/>
17. A NOAA-hosted Southern Ocean study separates surface transformation,
    interior diapycnal transformation, and isopycnal overturning in its volume
    budget. <https://repository.library.noaa.gov/view/noaa/50558/noaa_50558_DS1.pdf>
18. A 2026 Journal of Physical Oceanography study distinguishes small-scale
    diapycnal mixing from mesoscale isopycnal stirring and computes their
    thermohaline transformations separately.
    <https://doi.org/10.1175/JPO-D-25-0265.1>
19. A recent decomposition paper calls separation of “reversible isopycnal
    heaving” from irreversible transformation a fundamental attribution problem.
    This is recent methodological evidence, not yet a settled operational
    standard. <https://arxiv.org/abs/2605.23277>

## Classification decisions

- Keep `upwelling` and `downwelling` as generic vertical-motion structures.
- Add coastal and equatorial upwelling as geometry/forcing-qualified subtypes.
- Add Ekman pumping as a diagnosed wind-stress-curl process, not a synonym for
  every observed upwelling event.
- Keep river, hydrothermal, and meltwater plumes as source-tagged material
  bodies under a generic buoyant-plume parent.
- Add intrusion for the laterally spreading, neutrally buoyant material layer.
- Add isopycnal heave to name reversible vertical displacement without asserting
  cross-isopycnal transformation.
- Add turbidity current as a sediment-density-driven flow structure; its
  suspended plume may be only one component of the event.

## Limits

- These findings support conceptual object boundaries, not global detections.
- “Typically cold” is not an identity test for upwelling.
- A vertical velocity field alone does not close a heat budget.
- Exact external vocabulary identifiers remain a separate interoperability task.

