---
skill: validate-design
topic: ocean object visual matrix
date: 2026-09-05
reviewer_count: 9
p1_count: 0
p2_count: 4
p3_count: 32
domain_roles_active: [Ocean Ontologist, Information-Visualization Designer, Accessibility Specialist]
---

# Design validation — ocean-object visual matrix

## BLOCK 0 — content signal catalogue

| Signal phrase | Domain category |
|---|---|
| “106-object registry” and “13 type columns” | ocean ontology |
| “visual channel,” “equal visual area,” and “evidence matrix” | information visualization |
| “complete `<desc>`” and “no meaning carried by colour alone” | accessibility |
| “CSV registries,” “byte-stable,” and “unknown enums” | scientific data provenance |

## BLOCK 1 — expert roster

Stock table:

| Reviewer | Role |
|---|---|
| Architect | Stock |
| Code-Quality | Stock |
| Documentation | Stock |
| Testing | Stock |
| Process | Stock |
| Implementation | Stock |

Domain expert table:

| Signal detected | Expert added | Reason |
|---|---|---|
| “106-object registry” and “13 type columns” | Ocean Ontologist | Primary-type and identity-test semantics govern every cell. |
| “visual channel,” “equal visual area,” and “evidence matrix” | Information-Visualization Designer | Density, order, and marks can imply false hierarchy or importance. |
| “complete `<desc>`” and “no meaning carried by colour alone” | Accessibility Specialist | The static SVG needs equivalent nonvisual access. |
| “CSV registries,” “byte-stable,” and “unknown enums” | No expert needed | Testing and Code-Quality jointly cover deterministic provenance contracts. |

`BLOCK 1 domain count = 3`

## BLOCK 1.5 — roster commitment

| Reviewer | Role | Source |
|---|---|---|
| Ocean Ontologist | Domain expert | Domain |
| Information-Visualization Designer | Domain expert | Domain |
| Accessibility Specialist | Domain expert | Domain |
| Architect | Stock discipline | Stock |
| Code-Quality | Stock discipline | Stock |
| Documentation | Stock discipline | Stock |
| Testing | Stock discipline | Stock |
| Process | Stock discipline | Stock |
| Implementation | Stock discipline | Stock |

Domain row count is 3 and every name matches BLOCK 1.

## BLOCK 2 — per-reviewer findings

### Ocean Ontologist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Equal type width correctly prevents frequency from becoming importance. | P3 | Visual structure | Preserve equal primary cards. |
| 2 | A single “evidence class” axis is underspecified because registry status and object type are different facets. | P2 | Decision ribbon | Name observed representation separately from object status. |
| 3 | Type order sourced from prose is fragile and could drift. | P2 | Data/generation | Put canonical ordered type metadata in the generator and test it against classification headings. |
| 4 | The non-exhaustive warning correctly rejects a natural hierarchy. | P3 | Non-goals | Place it visibly inside the SVG. |

### Information-Visualization Designer

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Thirteen side-by-side columns cannot sustain 14 px labels within 1600 px. | P2 | Visual structure | Use a 7+6 card grid and a separate matrix below. |
| 2 | Raw identity-test × type marks may be too dense without totals or ordering. | P3 | Evidence matrix | Sort rows by conceptual family and show text labels. |
| 3 | Shape plus label plus hue is appropriately redundant. | P3 | Encoding | Test grayscale and contrast. |
| 4 | The five-step ladder is the strongest entry point. | P3 | Visual structure | Give it the top third of the figure. |

### Accessibility Specialist

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Title and description are necessary but a 106-object enumeration would overwhelm `<desc>`. | P2 | Accessibility | Keep description concise and link the full guide as textual equivalent. |
| 2 | Native-size 14 px is insufficient as the only criterion. | P3 | Encoding | Require viewBox scaling, reflowing guide text, and 4.5:1 text contrast. |
| 3 | Semantic group labels benefit SVG navigation. | P3 | Accessibility | Add `role="group"` and `aria-label` to major bands. |
| 4 | Colour redundancy is explicitly designed. | P3 | Encoding | Test that grayscale retains type distinctions. |

### Architect

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | CSV → generator → SVG/summary is a clean one-way architecture. | P3 | Artifacts | Keep generated outputs free of hand edits. |
| 2 | Guide 13 should consume generated summary rather than duplicate counts manually. | P3 | Accessibility | Embed a generated table between stable markers or validate prose counts. |
| 3 | Relations are input but no relation view is specified. | P3 | Artifacts | Use relations only for the decision-path examples or remove input dependency. |
| 4 | Static-first scope is bounded. | P3 | Non-goals | Defer interaction until semantics stabilize. |

### Code-Quality

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Standard-library-only generation reduces dependency risk. | P3 | Generation | Use csv, collections, pathlib, and XML escaping. |
| 2 | Stable ordering and no timestamp support byte stability. | P3 | Generation | Test two consecutive builds byte-for-byte. |
| 3 | SVG text must escape registry names safely. | P3 | Generation | Centralize XML escaping. |
| 4 | Generator responsibilities are currently broad. | P3 | Artifacts | Separate load, validate, summarize, layout, and render functions. |

### Documentation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Four audience questions give a clear reading contract. | P3 | Audiences | Mirror them in Guide 13 navigation. |
| 2 | “Measured colour” could imply all inputs are continuous rasters. | P3 | Decision ribbon | Say “mark, region, line, or colour.” |
| 3 | Non-goals clearly bound scientific status. | P3 | Non-goals | Repeat compactly in figure footer. |
| 4 | Build command and ownership are missing. | P3 | Data/generation | Add exact command and generated-file warning. |

### Testing

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Count and category coverage checks are explicit. | P3 | Acceptance | Assert totals computed from CSV, not literals alone. |
| 2 | Accessibility checks need concrete assertions. | P3 | Acceptance | Test title, desc, roles, labels, font floor, and warning text. |
| 3 | Layout overflow is not testable as written. | P3 | Acceptance | Assert every card and label coordinate stays inside viewBox. |
| 4 | Byte stability should use a temporary output. | P3 | Acceptance | Compare generated bytes without overwriting user files. |

### Process

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | Design-before-build sequence is correct. | P3 | Status | Record amendments before implementation. |
| 2 | No external review is implied. | P3 | Non-goals | Route through OSW roles after build. |
| 3 | Exact external IDs remain explicitly deferred. | P3 | Non-goals | Keep as a tracked condition. |
| 4 | Acceptance lacks an explicit visual inspection step. | P3 | Acceptance | Open rendered SVG and record inspection. |

### Implementation

| # | Finding | Sev | Section | Recommendation |
|---|---|---|---|---|
| 1 | 1600×1100 is feasible with a 7+6 card grid, not 13 columns. | P3 | Visual structure | Adopt two card rows. |
| 2 | Full identity matrix needs compact dots and row labels. | P3 | Evidence matrix | Provide counts/tooltips only in later interactive version. |
| 3 | Guide link cannot be clickable from every SVG host. | P3 | Accessibility | Put path text in SVG and real link in README/guide. |
| 4 | Current tests provide a natural extension point. | P3 | Acceptance | Add a dedicated matrix test module. |

## BLOCK 3 — synthesis

```text
Overall verdict: APPROVED-WITH-CONDITIONS

P1 blockers (must resolve before implementation):
  None -- proceed to implementation

P2 conditions (must resolve before sign-off):
  - OO-2 Ocean Ontologist -- separate representation class from object status
  - OO-3 Ocean Ontologist -- make type order deterministic and tested
  - IV-1 Information-Visualization Designer -- replace 13 columns with 7+6 grid
  - A11Y-1 Accessibility Specialist -- keep SVG description concise; guide is full alternative

Cross-reviewer consensus:
  The five-step evidence ladder should lead. The registry matrix must expose
  facets without implying frequency, hierarchy, geography, or certainty.

Strongest signal:
  Thirteen columns would make the intended overview unreadable; hierarchy must
  come from bands and a 7+6 card grid instead.
```

## AMEND

1. In Visual structure, replace 13 columns with a 7+6 equal-card grid and give
   the evidence ladder the top third of the SVG.
2. In Encoding, distinguish observed representation class from registry status,
   and make the non-exhaustive/count warning visible in the SVG.
3. In Accessibility and Acceptance, require concise `<desc>`, semantic groups,
   4.5:1 text contrast, grayscale differentiation, in-viewBox coordinates,
   deterministic type order, exact build command, and rendered inspection.
