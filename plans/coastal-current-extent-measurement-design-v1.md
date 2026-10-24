# Coastal current dimensions: prospective design after the EACC support audit

Status: design questions and acceptance criteria; no new numerical method has
been approved or executed. The objective remains defensible current dimensions,
seasonal information and atlas/query presentation. The EACC width gap remains
open. Keep the completed two-sided diagnostic and all failures unchanged.

## Evidence that motivates the work

The original EACC case has82 source requests,12 months and72 retained attempts.
The subsequent saved-output inspection, run40122083877, shows66 failed seed
refinements. In those cases the negative40km endpoint is unsupported:60 profiles
stop before reaching it and6 reach an unsupported sample. All66 corresponding
positive40km endpoints are supported. The first negative unsupported sample has
missing paired-corner support and lies west of the seed. The inspected maps
place that direction shoreward. This does not prove every missing corner is
physical land, and it does not justify a zero velocity or an invented edge.

January's primary central spans resolve, but surrounding station axis checks
fail. Retain these as station diagnostics; they do not pass the regional gate.

## Quantities to distinguish before implementation

These are proposed project definitions, not claims of a universal standard.

| Quantity | Required boundaries | Treatment in the atlas |
|---|---|---|
| Two-sided velocity-core width | Two supported crossings of a declared velocity fraction on the same local normal | Keep the existing method and eligibility gates intact. |
| Coast-referenced offshore extent | A declared geographic shore reference and a supported offshore boundary | State shoreline source/precision, unresolved inshore support and offshore criterion; do not silently label it a two-sided velocity-core width. |
| Wet-support-referenced offshore extent | A boundary of finite model support and a supported offshore boundary | Model diagnostic only; the wet mask is not independently surveyed coastline. |
| Core-to-offshore-edge distance | A verified core origin and one supported offshore crossing | Partial dimensional evidence; never double it to invent a full width. |

The target is to obtain defensible coastal width estimates using a quantity that
matches the current's geometry and source support. Partial extents remain
explicit partial evidence until the remaining boundary can be supported. They
do not close the full measurement objective by changing its label.

## Decisions that must be frozen prospectively

1. Select the reference boundary and justify its positional support. The existing
   NaturalEarth1:10million layer is display context and supplies no asserted
   sub-grid coastal accuracy. Distinguish shore, model wet-mask boundary and
   first fully supported interpolation cell.
2. Define the section orientation and core/edge criteria once. Keep Earth-frame
   velocity components, geodesic distance and local projection conventions
   explicit. Do not move a section, shorten a search or select a more favorable
   row after observing a failure.
3. Preserve missing corners and unsupported intervening cells as censoring.
   Require connected support from reference/core to the offshore edge. Declare
   assumptions about any unresolved inshore strip separately from observations.
4. State whether a result is a whole width, a bounded extent or a one-sided
   partial distance. Do not pool these quantities in one ranking. Specify how
   positional bounds, source spacing, numerical sampling, method sensitivity and
   physical uncertainty differ.
5. Fix the year, depth/layer and temporal operation. The retained2013 daily-00Z
   monthly means at15m are not observations or climatology; a width of a monthly
   mean is not mean instantaneous width. Monthly extrema are not automatically
   a physical annual range. Use explicit month/monsoon labels where appropriate.

## Small synthetic verification before another original-data case

- A coast-adjacent decaying current with known offshore threshold position;
  preserve the expected absence of an inshore velocity crossing.
- An offshore jet with two known crossings, to show when the original full
  width remains the appropriate quantity.
- A core with an unresolved inshore strip, a missing offshore cell, an offshore
  domain edge and a competing current; retain each censoring reason.
- Rotated/curved section geometry, unequal components, native-grid changes and
  both threshold brackets; no silent symmetry assumption or zero fill.
- A frozen12-month fixture retaining every month, including unsupported cases,
  with explicit uncertainty/sensitivity and quantity-type distinctions.

These fixtures validate operations, not EACC physical attribution. This design
is informed by the retained2013 results and must be labeled method development.
Any subsequent physical admission needs independently supported geographic/
source validation and a transparent comparison with the unchanged failed case.
Use an independent field/year or observations to validate generalization before
claiming a broadly applicable seasonal measurement method.

## Sources and limits

The primary EACC paper [Zheng et al.2024](https://journals.ametsoc.org/view/journals/clim/37/17/JCLI-D-23-0563.1.xml)
describes regional averaging from the coast to an eastern current boundary in
publicly indexed text. Direct opening returned403; its full methods were not
independently inspected. This is context for keeping boundary definitions
explicit, not validation of a new OSW threshold or shoreline rule.

The open primary model benchmark [Fofonova et al.2021](https://gmd.copernicus.org/articles/14/6945/2021/index.html)
examines a buoyancy-driven plume and its coastal extent, with sensitivity to
numerical mixing. Its physical mechanism and dimensional predictions are not
transferred to the EACC. Obtain suitable EACC method/source evidence before
presenting any new metric as an established EACC measurement.

## Execution sequence

Prepare a new numerical protocol, synthetic implementation and internal roles
review in new files. Preserve all62 executed input paths from the source and
support cases, including both old parent workflows. Keep local heavy processing
off. Only after a new complete freeze should one cloud case reuse the retained
fields; it must not reacquire or rerun the completed original case. Keep all
outcomes and compare the new quantity explicitly to the retained result.

Only a reviewed typed cohort proceeds to data/query projection, native checks,
WASM checks and browser/map/card verification, one stage at a time. Main and the
installed working data remain unchanged by this design.
