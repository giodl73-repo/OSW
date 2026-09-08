---
skill: roles-check
topic: ocean-column-workbench
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Ocean Column Address workbench

**Artifact type:** interactive scientific reference-geography and teaching viewer

**Source commit:** `d24c523cafa331316cd7628fc60fbf9b9c6ac777`

**Reviewed artifact SHA-256:**

- HTML: `77D495F1B1E867E4E2FEBC64DF4F05B0A65ED4715B174CAED1F1C0B6A6E97B6A`
- CSS: `46EC19C4F3C348F7E5D7985A363BD69691E07C1274124DB631B74B6F2CE3E817`
- JavaScript: `A7C16A493365DA5E53D179D0ACF4FB35AFFA3A6472769C133F849690E7A38255`
- generated data: `3BFD1C63DFA4140BBEDD90D81B8C247AEFD73F876870ECABC1D367A12DD8722B`
- method: `14E1B0930AC807723A41A7AB7693E6FF4275F6F4C4F113C5195D716767159045`

All eight native roles review this stage because it converts a scientific
definition into cartography, interaction, accessible text, generated data, and
a visible repository claim.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | An arbitrary province × band selection could be mistaken for proof that wet volume exists there. | P2 | Live readout | Call it an address class and require bathymetry plus exact horizontal geometry before claiming occupancy. **Resolved.** |
| 2 | Hypothetical mixed-layer and gradient ranges could look canonical. | P2 | Overlay controls | Put “example” and exact “hypothetical” wording in every control and the live output. **Resolved.** |
| 3 | The address remains independent when several physical regimes overlap it. | P3 | SVG model | Preserve independent regime tests when observed layers arrive. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Browser data could drift from the two canonical inputs. | P2 | Generated bundle | Embed paths and SHA-256 hashes and require deterministic regeneration. **Resolved.** |
| 2 | The teaching seabeds lack source identity because they are invented archetypes. | P2 | Method | State their exact depths and conceptual status; do not attach GEBCO attribution until bytes are used. **Resolved.** |
| 3 | The address contract retains datum, direction, units, masks, and interval semantics. | P3 | Data bundle | Carry these fields unchanged into a future measured receipt. **Accepted.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Equal band heights strongly distort metric depth. | P2 | Scale modes | Badge the view “not to scale” and provide a proportional 0–8,000 m alternative. **Resolved.** |
| 2 | Province-specific-looking seabeds would imply nonexistent local sampling. | P2 | Three columns | Keep the same named shelf/basin/trench teaching columns for every selection and repeat the boundary. **Resolved.** |
| 3 | Selected bands use outline plus label and position rather than color alone. | P3 | SVG | Retain redundant encoding when measured values are introduced. **Accepted.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Locate one wet volume” outran the evidence. | P2 | Control heading | Replace it with “Compose one address class.” **Resolved.** |
| 2 | Readers need the stable-address/changing-ocean distinction before controls. | P2 | Hero and reading cards | Put that contrast in the deck, formula, and interpretation sequence. **Resolved.** |
| 3 | Shelf, basin, and trench make bathymetric truncation immediately legible. | P3 | Main view | Preserve these as examples until real profiles are independently admitted. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Programmatic focus movement after each change would steal keyboard or screen-reader position. | P2 | Interaction | Use the polite live region without calling `.focus()`. **Resolved.** |
| 2 | Active hatching and colors were not originally repeated in the text result. | P2 | Live readout | Name every enabled overlay and its hypothetical range in controls/output. **Resolved.** |
| 3 | Desktop and narrow Edge renders expose selected address, controls, and meaning with semantic HTML. | P3 | Render check | Retain wrap, minimum-width, focus-visible, keyboard, and reduced-motion rules. **Accepted.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A manually copied 56 × 5 directory would be fragile. | P2 | Builder | Generate committed runtime data from the canonical CSV and JSON. **Resolved.** |
| 2 | Visual behavior needs offline structural gates. | P2 | Tests | Check deterministic bytes, counts, claim stage, keyboard hooks, live output, reflow contract, and JS syntax. **Resolved.** |
| 3 | The page has no runtime network dependency. | P3 | Delivery | Keep remote source acquisition outside the default test path. **Accepted.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A discoverable viewer needs a method and rebuild route. | P2 | Navigation | Link it from root README, Atlas, Guide 15, and its own method page. **Resolved.** |
| 2 | “GEBCO candidate” could imply GEBCO data are already present. | P2 | Method and roadmap | State that no GEBCO bytes were downloaded and list the future evidence gate. **Resolved.** |
| 3 | History and roadmap now distinguish interaction-grammar completion from measured occupancy. | P3 | Project record | Preserve this boundary in the commit message and handoff. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The workbench's solid seabed and Earth sunlight bands do not transfer to gas giants. | P2 | Scope | Grant no planetary inference from this visualization. **Resolved by Guide 15 boundary.** |
| 2 | Similar-looking vertical stripes could invite an unearned analogy. | P2 | Public claim | Keep the page Earth-only and omit gas-giant language from its headline and controls. **Resolved.** |
| 3 | Independent reference coordinates and diagnosed regimes remain a useful abstract distinction. | P3 | Future comparison | Re-derive coordinates and boundaries before any planetary use. **Accepted.** |

## Synthesis

```text
Roles reviewed: 8
P1 blockers: 0  |  P2 issues: 16  |  P3 notes: 8

Verdict: APPROVED-WITH-CONDITIONS

Top finding: composing a province × depth-band class does not establish that
wet ocean occupies that class.

Cross-role consensus: keep every teaching geometry visibly hypothetical,
bind the browser bundle to canonical inputs, and require exact horizontal
geometry plus pinned bathymetry before any local occupancy claim.
```

All sixteen P2 findings are resolved for the conceptual workbench. The
conditions are forward gates: observed province sections, occupancy counts, or
volume claims require a separately reviewed bathymetry intersection and data
receipt.

## Amendments

1. Replaced the false “locate wet volume” implication with address-class
   language and an explicit unverified-occupancy statement.
2. Added deterministic source hashes, hypothetical overlay ranges, equivalent
   live text, no-focus-steal behavior, and narrow-screen reflow repairs.
3. Added method, provenance, rebuild, navigation, roadmap, and measured-data
   admission gates, while keeping GEBCO candidate-only.

Fixed-point decision: approve the Ocean Column Address workbench as conceptual
reference geography. No local bathymetry, wet-volume occupancy, observed
physical regime, heat, transport, deployment, or remote publication claim is
authorized by this review.
