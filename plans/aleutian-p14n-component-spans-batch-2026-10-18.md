# P14N branch component-span batch

Continue branch `codex/current-measurement-gaps` and draft PR #83 from
`4f407bbce1b50c481a6ecd9e2fe74e8f6961f175`. No additional PR or main merge.

## Measurement progress

The fixed 44–46 N northern and 41–43 N southern windows both resolve their
40%, 50%, 60% eastward-component crossings. The source remains the original
JASADCP hourly product, using the unchanged joint-support 100–300 m means.
The separately declared operator precedes computation of the new spans, but
follows earlier velocity/hydrography inspection: no blinded preregistration.

| Window | 50% endpoint separation | Rounded nominal | Complete 40/50/60% envelope |
|---|---:|---:|---:|
| Northern | 102.002 km | approximately 100 km | 90–110 km |
| Southern | 78.748 km | approximately 80 km | 60–90 km |

These are dated **hourly-track eastward-component endpoint separations**.
Both native crossing brackets, actual timestamps, both velocity components,
layer support, geodesic spacing, bearings, lobe indices, temporal extent and
the four bracket-endpoint combinations are retained. Acquisition order,
missing values, repeated occupations and track reversals remain intact.
All fourteen declared boundary/velocity scenarios resolve in the unchanged
windows. Calculations retain unrounded values; the table's extra digits
identify the reproducible calculation, not measurement precision.

## Scientific decision

Do not admit an inventory width from this calculation. The northern
before-peak bracket moves only 0.339 km in one hour near an occupation, so
the crossing can reflect temporal variability rather than a spatial edge.
Nominal bracketing observations span 13.02 hours north and 13.97 hours south;
there are three and two northward steps respectively. Endpoint/maximum-leg
resolution ratios are 4.74 and 4.46; passing this attention guide is not
physical validation. The southern lobe also has a substantial northward
component and the paper places an eddy near its southern flank.

The separately specified velocity-comparator outcomes range from 43.012 to
151.938 km north and 55.929 to 90.185 km south. They are finite perturbation
scenarios motivated by the paper's GPS-related hourly velocity uncertainty,
not width confidence intervals, total error bounds, or annual ranges. They
are not pooled with the 40/50/60% boundary-choice envelope. No speed-magnitude
substitution, rotation, ship-speed correction or spatial filtering is applied.

The original vector and hydrography reports remain unchanged and nested by
value in the new source record. Preserve all 155 earlier scoped inventory
rows, four other research scenes, 42 other diagnostic rows and seasonal
route-frame bytes. Named physical current width and annual range remain
unknown; no physical edge, rank, ribbon, area or state intersection is added.

## Delivery and next evidence

The Aleutian card gains **Component spans and sensitivity**, with source queries
for all crossing brackets and figure provenance. The shared Rust/WASM record
retains the new calculations, complete original context and integrity guards.
Existing source/velocity/hydrography corruption cases remain; new cases target
span values, brackets, scenarios, metric, envelope, admission and protocol.

Next scientific work is an explicit underway section reconstruction or
independent transverse support that distinguishes temporal occupation changes
from spatial boundaries, together with branch/eddy attribution review. Do not
alter a window or discard an occupation after seeing this result to obtain a
preferred physical width. Seasonal support remains a separate gap.

Verification receipts distinguish focused tests, actual browser delivery,
predecessor full-suite status and the next clean combined gate. Hosted CI on
the parent failed during source acquisition (Van Aken Reading connection
refused in run39121015221; Qiu/Chen SOEST timeout in run39121020964). Neither
failure is a software test pass. Source hashes and TLS policy remain strict.
