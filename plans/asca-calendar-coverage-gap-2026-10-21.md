# Agulhas calendar coverage and conditional distributions

Baseline: e5fde03600835b23b0917c8ec30fc7c1a5090005. Continue branch
`codex/current-measurement-gaps` and draft PR83; no separate PR or main merge.

## Gap filled

The retained 931 ASCA profiles had dated outcomes and consecutive monthly bins,
but no pooled calendar-month or source-year distribution view. The declared
[protocol](asca-component-calendar-distribution-protocol-v1.md) now produces
48 cohort/threshold records: whole source period, three calendar years, twelve
pooled months, each at the source's 40%, 50% and 60% conventions. The 50%
primary convention was fixed before calculation.

The Agulhas card and diagnostic query expose a figure, accessible table, exact
cohort queries, citation and retained source limitations. Filtering creates
correlated samples; percentiles describe resolved cases, not confidence or
physical current boundaries. Source timestamps remain unmodified.

2017 has full nominal calendar coverage but only 131/438 primary attempts
resolve. 2016 and 2018 are partial years. Failures remain in coverage counts,
status counts and membership. Physical annual ranges remain unknown.

## Preservation and verification

- All 49 previous diagnostics remain exact; one diagnostic is added.
- All 44 other typed collections remain exact, including 156 scoped width
  records, 463 width samples and 2,853 dated section cases.
- Only the Agulhas object's diagnostic/navigation fingerprints change.
- Five focused Python tests and 84 Rust tests pass. Native/WASM builds and
  native atlas snapshot pass. Nineteen scientific reports regenerate byte for
  byte locally, including the new report; independent new-head Linux CI is
  recorded separately after publication.
- Browser checks cover the new calendar view and existing ASCA dated view,
  including exact source queries, keyboard use and 320px reflow.

The earlier complete local Python baseline belongs to 774e466, not this batch.
No whole-current width, length, source-file checksum or corrigendum-review
completion is admitted here. Overall current measurement gap filling remains
incomplete. Continue source-backed dimensions and temporal support on PR83.
