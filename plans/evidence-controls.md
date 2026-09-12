# Evidence controls

Status: active implementation contract; no release promotion authorized

Date: 2026-09-12

## Product question

What kind of claim is this view making, what receipt supports it, and what has
not been established?

## Delivered behavior

OSW surfaces share a compact evidence-control vocabulary:

| Token | Meaning | Allowed action |
|---|---|---|
| conceptual | interpretive teaching geometry | inspect its source and stated boundary |
| observed | direct or analysis-derived field/footprint | inspect source, support, and identity test |
| derived | deterministic product comparison or transformation | inspect inputs and method boundary |
| model-screen | forecast, assimilative, or offline model diagnostic | inspect product, support, and missing terms |
| sensitivity | declared alternative policy/method result | inspect the parameter and non-uniqueness |
| unresolved | a named missing term or unsupported inference | read the absence; do not convert it into a cause |

Atlas receives a URL-addressable Evidence filter beside its existing depth,
property, and clock controls. It filters only the 36 conceptual feature cards
and shapes; observed Atlas map modes remain separately and visibly labeled as
observed fields, never hidden by a feature filter. Each filtered result retains
its source and limitation in the existing detail route. A zero result says so
in text.

Event and Exchange receive a persistent plain-text evidence legend and direct
receipt route for every active stage. They do not pretend that a single screen
can be reclassified by a filter: the control is explanatory there, while Atlas
is the cross-record filter.

## Boundaries

- Evidence class is not confidence, importance, or a scientific ranking.
- A filter never changes a record's claim, source, geometry, depth, time, or
  limitation.
- `unresolved` describes an absence and never hides a record or becomes a
  process label.
- No new derived result, aggregation, source acquisition, or release decision
  belongs to this slice.

## Acceptance

1. Atlas filter tokens are URL-addressable, keyboard operable, non-color, and
   announce match counts.
2. Every displayed token maps deterministically from the committed feature
   record; tests cover conceptual, observed, synthesis/derived, and model
   cases plus a zero-result unresolved/sensitivity filter.
3. Event and Exchange show their evidence class and a receipt link in the
   ordinary reading order without hover.
4. The full offline suite, syntax checks, narrow browser review, and native
   role review pass.
