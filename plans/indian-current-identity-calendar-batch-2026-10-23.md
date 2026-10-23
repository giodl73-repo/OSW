# Indian current identities and reported direction calendars

Source-stage work on `codex/current-measurement-gaps`, existing draft PR83.
No main merge. Canonical identity/query/native/WASM delivery remains a batched
gate; the live catalogue has not gained four currents or monthly measurements.

## Identity decisions

`research/indian-coastal-current-identity-review-v1.json` records four supported
separately named current identities, pending canonical admission:

| Proposed ID | Preferred name | Source-supported distinction |
|---|---|---|
| `current:west-india-coastal` | West India Coastal Current | India west-coast flow, distinct from the inter-basin monsoon-current label. |
| `current:east-india-coastal` | East India Coastal Current | India east-coast flow; sources vary in their treatment of poleward WBC versus equatorward EICC. |
| `current:east-african-coastal` | East African Coastal Current | Tanzania/Kenya current; the review explicitly contrasts its prevailing northward regime with the reversing downstream Somali Current. |
| `current:south-java` | South Java Current | Separately named coastal current, not a synonym of Indonesian Throughflow. |

The naming caption and current-specific sections of the retained CC-BY4
Vinayachandran et al.2021 original support these decisions. The2024 Indian
coastal-transport paper's accessible publisher text distinguishes the coastal
currents from the inter-basin monsoon currents and supports the West/East
Indian Coastal spelling variants. It supplies no admitted width here: its
three-degree transport integration domain is not a current-width measurement.

East Gyral remains unresolved against the existing South Indian Current
identity. Wijeratne et al.2018 uses both East and Eastern Gyral in the same
publication, with EGC, and distinguishes it from SICC. That distinction alone
does not prove EGC differs from SIC. No new EGC entity, alias to SIC, dimension
or footprint is admitted. The ignored2018 original retains its existing rights
boundary; no full publication is newly redistributed.

## New seasonal information and visual

The source stage now includes two **qualitative annual-direction calendars**:

- WICC: the accessible Shetye1998 publisher abstract assigns northward flow
  to November–February and southward flow to April–September. March/October
  remain unspecified. Only the short excerpt was retained; the full original
  was not accessed, retained or independently checked.
- EACC: the retained2021 review, section2.4.1, describes northward orientation
  throughout the year. Its original bytes and relevant section were checked.
- The same2021 review's section2.7.3 says WICC can flow either way on shorter
  timescales. This limitation appears beside the calendar, preventing a
  daily-direction guarantee.

The24 month-indexed rows are descriptions of these source statements, not24
observations. No observed velocities, sampled years, dimensions, annual ranges,
geographic masks, state intersections or physical seasonal playback are added.
Highlighting a description for a selected calendar month is a separate potential
UI capability. It does not license animated physical flows or changing widths.

Products:

| Product | SHA256 |
|---|---|
| `research/indian-current-reported-direction-calendars-v1.json` | `ea1399d45121884279686675d0cc8f42200fd59ac14e9203d38f77e40c401374` |
| `figures/indian-current-reported-direction-calendars-v1.svg` | `a9528d58a4af9a34fead12d50d47642c6f31ac6b6a182f17712f2cfa9fa34cac` |

## Freeze and checks

Commit **9500981452c82c696aae0eb71766bb8cbfef913d** froze the producer,
source facts, identity review, protocol, synthetic tests, preflight and
line-ending rules before the actual report/SVG existed. Preserve those
executed inputs and products; corrections require a new version. The initial
five-name candidate record remains unchanged and traceable.

First actual generation and immediate read-only replay passed with the exact
hashes above. The saved SVG was rendered with PyMuPDF and visually inspected;
native-size labels, month cells and qualifications fit without observed
collisions. No browser was started. This does not establish mobile host access.

All30 focused checks passed:27 prospective synthetic cases and3 independent
actual source/product/identity checks. The synthetic cases cover cross-year
periods, single-month versus full-year intervals, invalid months, overlaps,
unknowns and rejection of invented observations or physical quantities.

```powershell
python -m pytest -q analysis/test_reported_current_direction_calendars_v1.py analysis/test_indian_direction_calendar_admission.py
python analysis/reported_current_direction_calendars_v1.py check
```

The30 checks and exact report/SVG replay are added to conformance. The central
scientific replay driver now includes this report as its41st registered target;
Brazil's ignored-original-dependent report retains separate verified replay
coverage. New Linux results remain unverified until their actual jobs finish.

## Remaining batch gates

1. Integrate the four identities as an extension, preserving old IDs, existing
   measurements and links; retain EGC as unresolved. Carry the explicit
   seasonal/intraseasonal naming caveat for EICC into taxonomy controls.
2. Correct the inventory-wide source projection/count issues already captured
   in the Brazil batch. Add the Brazil regional reach and these source
   descriptions with exact provenance and non-promotion guards.
3. Admit the calendars to a clearly qualitative collection and verify native/
   WASM parity, accessible host text, narrow-screen keyboard access, links and
   rejection of coherent rehash/promotion attempts. Do not advertise monthly
   measured coverage or physical seasonal animation from these rows.
4. Complete independent current lengths, widths, seasonal dimension support,
   eddies and state joins as evidence permits. These products do not close
   those broader gaps. Full regression remains a separate final gate.

Local work stayed BelowNormal on one logical CPU, with one worker and no
build/browser/regression overlap. Native/WASM builds remain held by the local
disk preflight; source checks and this diagram require only small outputs.
