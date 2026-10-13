# Basin surface section span protocol v1

2026-10-13. Local OSW diagnostics for the offshore Portugal, South Atlantic
and eastern South Pacific contexts. Applies the general current width
protocol; does not admit whole-current widths, ranked widths or annual extrema.

## Fixed rules

1. Preserve the declared 2013 OSCAR 2017.0 query, metadata and original CSV
   bytes. The nominal 15 m coordinate represents satellite-derived near-surface
   flow, not an instrument depth or subsurface velocity. Preserve all 72 actual
   timestamps (January 1–December 26, four six-day gaps).
2. Use the three sections, domains and peak-search windows in the pinned input.
   Portugal uses southward velocity (`-v`) at 40 N; the other sections use
   eastward velocity (`u`) at 30 W and 100 W. The source identity contexts
   justify investigating these locations, not declaring every selected peak
   to be that current. Existing editorial route layers remain separate.
3. Average complete `u,v` pairs at each native cell within each UTC month.
   Require at least five complete pairs at each cell; missing cells remain
   missing. Keep pair counts and both mean components. Monthly span of the
   monthly-mean profile is not the mean of instantaneous spans.
4. Select the strongest positive directional component within the declared
   search window. Ties choose the lowest coordinate. Require a peak of at least
   0.02 m/s; this is an OSW diagnostic eligibility rule, not a universal physical
   current threshold. Flag a peak at a search-window edge.
5. Retain three relative boundary thresholds: 0.4, 0.5 and 0.6 of that peak.
   Walk outward through its connected component. Stop at the first threshold
   crossing on each side and interpolate linearly within that native bracket.
   A missing value or domain edge before a crossing leaves that side unresolved.
   Do not bridge missing cells, join disjoint peaks or choose a farther crossing.
6. Compute shortest WGS84 geodesic separation of the two boundary coordinates.
   Preserve raw calculation values and native brackets; report approximately
   to the nearest 10 km. Flag spans narrower than four native grid spacings.
   These fixed-orientation component spans are not diagnosed flow-normal widths.
7. Report the complete three-threshold sensitivity envelope only when all three
   scenarios resolve. Round the lower bound down and upper bound up to 10 km.
   Retain unresolved scenarios and partial values without an invented envelope.
   Native sampling brackets, threshold sensitivity and measurement uncertainty
   are separate; the last remains unknown.
8. Preserve all 12 monthly profiles, including weak/unresolved months. The
   spread of local monthly values is not an annual physical width range or
   uncertainty interval. One year is not climatology. A chart can compare or
   step through these profiles; no seasonal current footprint is reconstructed.
9. Retain source/config/protocol/generator and identity-context hashes. Current
   association, obliquity, resolution, model error and representativeness require
   review. No buffer polygon, current area, OSW state containment or NASA feature
   identification follows from these sections.

## Geographic context

Portugal's 24–12 W peak-search window is based on the offshore statistical
region reviewed from Martins et al. (2002); its box edges are not current edges.
The wider 32–8 W sampling domain permits finding crossings or recording their
absence. Coastal northward flows and missing coastal data stay visible.

The South Atlantic section investigates surface flow; it does not inherit the
Antarctic Intermediate Water layer of the existing western float reference
route. SAC/ACC and branch attribution remain unresolved diagnostics gates.

The South Pacific section investigates surface velocity near the eastern
source frontal region. A hydrographic front at 150 m is not a surface velocity
axis, and multiple bands need separate association review.
