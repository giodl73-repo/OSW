# Coastal reference extents: numerical protocol v1

Status: prospective method-development protocol. No original EACC case has been
run under this operator. This protocol follows the retained2013 failures; it is
not blind validation. All62 executed source/support input paths remain immutable.

## Purpose and quantities

Estimate local cross-current dimensional evidence when a paired velocity-core
width is unsupported near an inshore data boundary. Preserve the complete
original case and its gate outcome. Compute the following distinct quantities
on every supplied profile and fraction40/50/60%, without choosing a favorable
quantity after observing a failure:

1. `local_two_sided_threshold_span`: bracket between two supported sampled
   fraction crossings. This does not replace the old five-station regional gate.
2. `core_to_positive_normal_threshold_extent`: one-sided distance from the
   retained candidate peak to the positive-normal crossing. Never double it.
3. `finite_paired_support_to_positive_threshold_extent`: bracket from the
   negative-side supported-domain transition to that same crossing. This is a
   model support reference, not surveyed shore or a physical full-current width.
4. `shore_reference_to_positive_threshold_extent`: geometric extent from a
   separately supplied, source-bound shore-position interval to the crossing.
   An unresolved inshore strip remains explicit conditional coverage. Do not
   manufacture a shoreline from the model mask or the display basemap.

The positive normal is a signed coordinate, not automatically offshore. Physical
offshore/current attribution requires independent geographic/source review.
Keep original current identity, all axis flags and failed cases alongside results.

## Inputs and frame

Use ordered rows with signed distance s in km on one WGS84 geodesic normal and
the retained Earth-frame velocity projected onto its local tangent, q in m/s.
The source adapter must prove this coordinate/projection convention and supply
source/case fingerprints. Do not use meridional V as q for a rotated section.
Retain the declared source sampling step and verify that every adjacent stored
offset agrees within the declared representation bounds. The72-case wrapper
also verifies that5/10km identities match their actual profiles.
Every interval between adjacent rows has an explicit support flag and maximum
native cell scale in km over all cells it touches, not only the origin cell.

The retained peak is fixed by the source case: require a positive finite value,
unique-peak verification and supported adjacent peak samples. Do not reselect
the strongest value, move the section or shorten the40km seed search. The new
operator does not recompute an anchor or mark the old missing endpoint as valid.
A one-sided boundary candidate may be retained only with an explicit separate
support-kind tag and seaward neighbor support. Its reference amplitude is not
asserted to be the physical maximum in the unobserved inshore strip. It cannot
supply an invented inshore crossing. A missing candidate, source frame, interval
support or native scale stays unresolved.

Source serialization uncertainty must be declared. For the retained packed
EACC diagnostic, q and peak q are rounded to8 decimal places and signed offsets
to6 decimal places. Use outward bounds at least5.000001e-9m/s and
5.000001e-7km when adapting those rows. These are numeric representation guards,
not physical error estimates. Synthetic exact fixtures may use zero guards.
Do not assert finer physical precision because a float has many digits.

## Connected sampled crossing

For each fraction f, bracket the unknown threshold by
`f * [q_peak - epsilon_q, q_peak + epsilon_q]`. Start at the retained peak and
walk each signed side independently. Every visited row and intervening segment
must be supported. Stop at the first missing row, unsupported segment or source
limit. Never bridge missing values or replace them with zero.

A sample is definitely above if its lower q bound exceeds the upper threshold
bound. It is definitely below/equal if its upper bound is at/below the lower
threshold bound. Rows ambiguous at stored precision stay in the bracket until
the first definite crossing; they do not force an invented interpolation point.
Return the last definitely-above and first definitely-below offset bounds.
If no definite crossing is found, retain the precise censoring reason.

Before the crossing, an outward rise whose upper possible value exceeds the
lowest prior lower q bound by more than1% of the lower peak bound is unresolved
possible competing-core support. Preserve that gate for each side. A sampled
crossing is not a proof that no sub-sample excursion exists.

## Inshore references and connectivity

For the model-supported-domain reference, walk negatively from the same peak.
Require connected supported segments until the first unsupported sample or
segment. Bracket the boundary between that point and its adjacent supported
point, including offset representation bounds. A source-domain crop is not an
inshore reference. Preserve the underlying missing-corner/rectangle reason.

For an independent shoreline reference, require a declared finite positional
interval, nonempty source fingerprint/citation and geometry-review status.
Its interval must lie on the negative side of the retained peak and reach no
farther seaward than the retained peak. Derive the supported start by walking
the original connected path from the peak, then selecting the inshore row that
brackets the declared shore interval when that interval lies within model
support. Never let a caller choose a more favorable later starting sample.
Explicitly report any
inshore strip without model support. A coastline intersection alone cannot
establish flow continuity across that strip.

The supported inshore point and every sampled point between it and the peak
must be definitely above the same fractional threshold. A point definitely
below, a representation-ambiguous point or an unsupported segment means that
reference is not a demonstrated connected sampled core. Report it; do not switch
to another boundary. This allows a detached offshore jet to retain its local
two-sided span while rejecting a shore-attached interpretation.

The peak row shares its own positive reference amplitude with the threshold;
it is therefore above its fraction even when conservative independent interval
arithmetic would otherwise overlap. Every other sampled row uses the stated
above/below/ambiguous interval rules.

## Reported brackets and resolution

If the offshore crossing lies in `[e_low,e_high]` and the reference position in
`[r_low,r_high]`, the reference-to-edge extent is bounded by
`[e_low-r_high,e_high-r_low]`. Require the entire bracket to be positive. A
two-sided span uses the analogous difference of the two edge brackets. Do not
invent a midpoint, double a one-sided distance or label these brackets confidence
intervals. A shoreline-to-edge result with an unresolved inshore strip remains
conditional, even if its geometric bounds exist.

Evaluate source-scale support using the smallest extent bound divided by the
largest native cell scale over the full connected path and both boundary
brackets. Require at least4 cell scales. An unknown scale stays unresolved;
insufficient source-scale support is not zero width. This gate does not verify
effective model resolution or observational accuracy.

For an independent shore reference with an unresolved inshore strip, use the
smaller known supported model span for the source-scale test. A long unsupported
strip must not inflate the apparent resolved cell count. Preserve conditional
shore-flow connectivity and source-scale status separately.

Retain an explicit conditional-inshore-flow flag and resolution status even
when both limitations apply. Missing profiles retain all three fractions and
four attempted quantity slots with null extents; no month or metric disappears
from coverage counts because an input was unsupported.

Outputs retain reference kind, source and numeric representation bounds,
crossing/reference bracket endpoints, support/censoring reasons, local native
scale and the unchanged original regional status. All whole-current width,
length, physical annual extrema and physical uncertainty fields stay null;
rank/state-join eligibility stays false. Physical measurement admission requires
an additional source/geographic/definition review.

## Verification and original-data execution

Use tiny exact coastal-decay and detached-jet profiles with analytically known
crossings, explicit inshore positional intervals, missing points and segments,
competing rises, altered native scales and threshold quantization ambiguity.
Include a rotated-frame fixture whose q is constructed from unequal Earth-frame
components. Retain all12 months/3 offsets/2 steps, including missing inputs.

The prospective cloud adapter must use the saved completed fields or diagnostic
with exact fingerprints. Retained rounded rows require the representation guards
above. It must not import/call diagnose_year, source compilation/acquisition or
figure producers, nor edit the old case. Freeze adapter, tests, source definition,
protocol, review and execution request before original-data access. One cloud
case at a time, one CPU, no local original arrays, builds or browser automation.
Keep all metrics and failures; assess independent field/year/observational
support before claiming generalization or a physical seasonal width series.
