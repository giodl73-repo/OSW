# South Australian Current: original-source model-width report

Continue branch `codex/current-measurement-gaps`, PR83. No new PR or main merge.

## Result and limits

The complete Miller (December2006) dissertation was acquired from the Naval
Postgraduate School Library's Internet Archive deposit. Original:431pages,
31,509,443bytes, SHA256
`c2a90767085d99e788ae93f6fd7422f00fd687e4c0ccb78341da0c78f600743b`.
The original setup, numeric passage and section figure were checked at PDF
pages79,80,264 (printed48,49,233). The complete dissertation was not reviewed
page by page. Its public-release/unlimited-distribution statement is retained;
no public-domain or Creative Commons license is inferred.

One local source-defined model-width report is recorded in
`research/south-australian-miller-2006-model-width-scope-audit.json`, under the
companion protocol. The source label and experiment remain explicit. Original
numerical model output and paired boundary rules remain unavailable; this is
an author-reported scale, not an OSW boundary extraction. Existing HYCOM
diagnostics are separate evidence, not validation of the dissertation model.

The atlas current card now shows the report's annotated numeric summary and
text alternative with direct source/query links. Generic Rust source querying
returns the exact retained measurement record. Existing canonical names,
ranked lengths,155 inventory widths,463 width samples, route geometry and
seasonal series remain unchanged. Scoped width coverage remains81owners;
this batch closes source acquisition and source-context gaps, not physical
whole-current or seasonal measurement gaps. Formal width-inventory admission
of the source-defined local model scale remains a subsequent task.

## Integration and checks

Python verifies the source bytes and the report's numeric/temporal exclusions.
Rust binds the complete report and dependencies to its owner, rejecting changed
quantities, source inputs, elapsed model day, observed dates, annual-mean
promotion and erased/duplicated ownership. The scope-note index was regenerated;
its13 assessments and original frozen inputs remain unchanged.

The first native atlas check caught omission of the new scope audit from the
dashboard's returned object data. That conditional was corrected and the whole
dashboard/index/bundle/engine chain rerun. The first Rust test run passed82tests;
seven focused Python scope tests also passed. Final rebuild and browser results
are recorded when execution completes, rather than inferred from those tests.

## Broader verification status

Prior head30d4d8e: scientific reproduction job119104438981 passed in
run39564811299. Its offline job119104439277 failed **before tests** acquiring
the existing Stramma1992 fixture from GEOMAR (HTTP403). No source bytes, test
assertions or acquisition policy were weakened. These results do not certify
this new batch. The last complete local Python baseline remains774e466.

## Final focused verification

- Rebuilt dashboard, lossless index (396 source documents), query bundle and
  engine manifest;82 Rust tests passed, locked offline native/WASM builds and
  native atlas snapshot passed.
- Seven Python scope tests passed. JavaScript syntax and Git whitespace checks
  passed. The original source-byte validator passed.
- Actual Chrome browser: exact one-row Rust source query, source-query link
  activated by keyboard, image loading,320px card reflow, zero page errors and
  zero original-PDF requests. Mobile rendering visually inspected.
- All44 other typed collections are byte-for-value unchanged against30d4d8e.
  Only the South Australian object changes, plus its route decision's
  `scope_reviews`. Numeric records and geometry are preserved.
- Rust's new direct validation test rejects altered value/day, annual-mean
  promotion, invented observation dates/ranges, wrong owner and erased report.
  Additional invalid full-bundle imports are rejected by the existing
  dashboard projection checks; these do not replace the new direct checks.

These checks establish the new report's source binding and presentation. They
do not establish an observed physical width or certify a full new Python gate.
