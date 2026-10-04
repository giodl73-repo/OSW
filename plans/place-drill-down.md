# Place drill-down

Status: proposed implementation contract; no release promotion authorized

Date: 2026-09-12

## Product question

When a visitor selects one OSW ocean state, what does the repository actually
know about that reference geography, and which questions remain unmeasured?

## Intended result

Make a selected province a durable, shareable reading context rather than a
temporary map highlight.  The Atlas should provide a compact **state handoff**
that names the selected reference geography, states its edition and limits, and
links only to existing, compatible evidence in the Column workbench, Exchange
Observatory, and event route.

The first slice is a federated handoff, not a new province aggregation service
and not a new scientific result.  It must work for every classic 56-code Atlas
identity, while making the 54-footprint edition and the `NPSE`/`OCAL` absence
visible where relevant.

## Truth contract

- A province is a declared horizontal reference address.  Selection does not
  establish a water mass, a closed container, an ecological identity at depth,
  or a physical boundary.
- The Atlas's 56 classic identities, the Column workbench's 56 selectable seed
  records, and the source-aligned Longhurst 2007 Version 4 footprint layer are
  related but not interchangeable.  Version 4 contains 54 territories;
  aliases and absent identities must remain explicit.
- A handoff may summarize data already committed by its destination.  It must
  not calculate province means, heat content, transport, event exposure, or
  border performance in the Atlas merely because a province is selected.
- A destination is shown as **available evidence**, **not available for this
  state**, or **not joined to this state/time/product**.  Absence is a result,
  never an empty card quietly omitted from the interface.
- The 2018 Drake temperature screen is limited to its six admitted provinces,
  depths, months, native grid, and model-screen evidence class.  The
  `SANT--SSTC` exchange pilot is not a general property of either province.
- The 2026 marine-heatwave route may be linked only for the committed GFST and
  NWCS state-address evidence.  It does not establish heat delivered across
  their shared edge or join to the 2018 Drake studies.

## Interaction contract

### Atlas state handoff

When a visitor selects a province from the map or existing selector, add a
visible, semantic `Selected ocean state` panel adjacent to the Atlas's current
province readout.  It contains:

1. code, source name, classic-56 status, and the current display/map context;
2. a short reference-geography boundary statement and link to the province
   directory/method;
3. the existing schematic rendered-overlap feature summary, still labeled as
   a display relationship rather than an observed crossing; and
4. a `Continue with this state` list of destination cards.

Cards always render in a stable order:

| Destination | Availability rule | Canonical handoff |
|---|---|---|
| Ocean Column | all 56 selectable codes | `../column/?province={CODE}` while preserving only the Column defaults for other controls |
| Exchange Observatory | only a code admitted by the committed hydrography screen | `../exchange/?province={CODE}&depth=0-200m&month=201802` |
| Heat-event route | only GFST or NWCS event-address evidence | `../event/?scene=event`, with state-specific explanatory copy; do not add a fictitious `province` event parameter |

For a destination without state-specific support, retain a disabled/textual
card explaining the exact limit and offer the destination's general route only
when that does not imply the selected state was loaded.  Examples: an ordinary
province gets an Exchange card stating that the bounded Drake screen has no
passport for it; `SANT`/`SSTC` get their explicit pilot-boundary wording;
`GFST` gets the event-address wording and an event-route link.

### URL and history

- Atlas remains canonical at `atlas/?province={CODE}` and preserves its
  existing valid lens/view/filter state.
- An explicit province selection pushes one history entry. Reset and passive
  lens/filter changes replace the current entry. A `popstate` handler applies
  the URL through the same validated selection path without creating a new
  history entry. Thus selecting, resetting, browser back/forward, and a direct
  valid URL keep the selected panel, map emphasis, textual readout, and
  destination cards in agreement.
- An invalid or missing `province` does not invent a selection.  It follows
  current Atlas fallback behavior and announces the result without shifting
  focus.
- Cross-app links pass only declared, destination-valid parameters.  The
  destination owns its own validation and defaults; Atlas never carries an
  unrelated feature, event, depth, or month into it.

### Accessible and narrow-screen behavior

- The handoff has an `aria-labelledby` heading, ordinary links, and complete
  text alternatives; it does not rely on hover, color, or canvas inspection.
- On selection, do not move focus.  If a visitor explicitly activates a
  `Continue` link, normal link navigation supplies focus behavior.
- At 390 CSS pixels, state identity, support/absence wording, and at least the
  Column continuation remain together in reading order with no horizontal
  page overflow.  Destination cards may stack.
- The selected-state summary and availability changes are announced through
  the existing polite live status, with a concise non-numeric sentence.

## Implementation shape

Primary changes are intentionally Atlas-local:

```text
atlas/index.html                    handoff landmark, heading, and card shell
atlas/state-handoffs.js             declarative, tested destination contract
atlas/app.js                        selection/history integration and renderer
atlas/styles.css                    state-handoff/card responsive treatment
analysis/test_place_drill_down.py  offline URL, availability, text, and link tests
plans/place-drill-down.md           this contract
```

`atlas/state-handoffs.js` owns a small declarative registry, not duplicated
research values. Each destination record declares its availability predicate,
evidence class/limitation copy, and URL builder. Its committed support lists
are checked offline against Column's selectable province codes, Exchange's
hydrography province records, and the event-state route's state passports.
`atlas/app.js` only renders that contract. A code must not appear in a handoff
merely because it shares a name with another dataset.

No new network source, source refresh, scientific computation, generated
geometry, or publication metadata change is in this slice.

## Verification

- Unit-test the destination registry for all 56 classic codes, including
  aliases/absent V4 identities, an Exchange-supported code, a non-supported
  code, GFST, and NWCS.
- Assert that every enabled destination link resolves locally, carries only
  allowed parameters, and that a disabled/limited card contains its boundary
  text rather than a dead button.
- Assert Atlas selection/reset/direct-URL behavior remains compatible with the
  current province and feature URL contract.
- Assert no place-drill-down source contains new computed headline science
  values or language equating a province with a physical boundary/container.
- Run the standard offline suite, Python compilation, JavaScript syntax checks,
  generated-SVG parsing, `git diff --check`, and desktop/390px keyboard browser
  review.  Review GFST, NWCS, SANT, SSTC, a regular V4 state, and `NPSE` or
  `OCAL` before closeout.

## Acceptance gate

1. Every selected classic province exposes a persistent, URL-addressable
   handoff with clear source-edition status.
2. Every destination is either a valid state-scoped link or a visible,
   state-specific bounded absence; no unsupported aggregation is implied.
3. Column, Exchange, and event handoffs preserve their independent evidence,
   depth, time, and product boundaries.
4. Keyboard, no-color, narrow-screen, direct-URL, reset, and browser-history
   paths pass review.
5. Tests and native role review find no unresolved P1/P2 issue.
6. Completion of this slice neither promotes Atlas 07 nor authorizes a public
   release or a zoning decision.

## Non-goals

- a universal province dashboard or cross-source score;
- province-level observed heat, transport, ecology, or causal event claims;
- a new event detector, boundary diagnostic, or data acquisition;
- changing 56/54 source editions, province geometry, or organizational zones;
- automatic merge, remote push, or public promotion.
