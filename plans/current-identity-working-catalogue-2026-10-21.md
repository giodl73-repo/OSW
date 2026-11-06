# Working catalogue: first identity admission

Baseline90cfaeaa02937ff7bf935fa456f4622512cad30b. Continue PR83 and the existing
branch. The full current measurement and catalogue objective remains active.

## Source decision

Admit the southern East Madagascar Current's identity from Nauw et al. (2008),
doi:10.1029/2007JC004639. Publisher full HTML explicitly identifies this
southward western boundary current; abstract and results describe near-surface
expression and variability. The institutional record is the same study, not an
independent measurement. Northern branch, undercurrent and offshore
countercurrent remain distinct; no global abbreviation or parent alias is
admitted.

The [identity protocol](current-identity-admission-protocol-v1.md) separates name
review from quantitative admission. Original-PDF access remains unavailable;
no source-file checksum or source-figure review is invented. The contextual
650km extent and April2001 near-surface120km width stay as separately gated
source reports. No ranked measurement, physical edge, annual range, coordinate,
observation date or seasonal animation is created by name admission.

## Official working data and presentation

The versioned identity extension and effective working catalogue are tracked
JSON documents. Draft0.2 combines100 historical v0.1 names with one admitted
identity. Base release files and IDs stay exact. The shared Rust store gains
the entity, source, stable name, explicit unranked length assessment, admission
and pending route-planning records. The working dashboard has241 objects and
101 named currents;28 proposals remain pending.

Main almanac entry, object page, atlas selector/directory, query interface,
dashboard and seasonal index expose the accepted identity. Existing incoming
proposal links still work. The main page distinguishes the working catalogue
from the historical package below it. There are100 mapped current stations and
one explicitly unlocated current; no point is invented to make the count101.
The seasonal index includes the new current with an empty, non-playable plan.

## Verification and defects found

Four focused Python tests check baseline preservation, collision rejection,
identity/dimension separation and explicit unknowns. Rust tests check exact
admission inputs and records, effective inventory completeness, promotion and
erasure rejection, and the non-playable seasonal plan.

The first native atlas gate caught the missing remaining-current planning
decision; an admission-bound pending worklist record now supplies it. Browser
checks then caught absent worklist display fields and an undisplayed source
classification; the complete worklist shape is validated and admission details
are now visible on the object page. Existing browser counts distinguish
historical map placements from the effective identity count instead of
requiring every name to have geography.

Before publication, verify the rebuilt engine, all main entrances, exact
native/WASM admission queries, old-row preservation, keyboard use,320px reflow
and staged dependency pins. Keep prior failed logs and earlier full-suite
results associated with their actual source revisions. No new release or main
merge is performed by this draft data revision.

## Remaining work

Review and admit source-scoped numerical dimensions separately, beginning with
the captured southern-branch extent and survey-width definitions. Continue
primary-source lengths, widths, repeated temporal support and geometry/state
associations for the existing currents. Name admission is not completion of
the measurement program; the existing89 unranked current-length gaps and the
new current's dimension-admission gaps remain explicit.

## Final local evidence

- 4 Python tests/4 subtests and87 Rust tests pass; native/WASM builds and native
  atlas snapshot pass.
- Main/object/query/atlas/seasons/dashboard admission browser passes, including
  exact native/WASM record equality, keyboard navigation,320px reflow and no
  page errors. Existing full atlas and general-query browser regressions pass.
  Dashboard receipt/projection rejection, coverage-light and update checks also
  pass, with241 records and one unlocated current.
- The new engine reopens the previous bundle. All100 prior seasonal plans and
  four raw source documents remain exact; only one non-playable plan is added.
- Every previous typed row remains exact. Six existing collections each gain
  one row;40 other collections,156 width records,463 width samples and2853
  section cases remain unchanged. All19 scientific report files and the full
  historical v0.1 package remain unchanged.
- 800 staged dependency blobs match pins. JavaScript syntax passes65 files;
  all14 page validation assignments are present (assignment is not proof of a
  full browser run). Source index contains400 documents.

The latest complete local Python baseline remains774e466, not this revision.
Independent scientific reproduction at90cfaea passed; new-head CI is reported
separately after push. No full-suite or public-release completion is claimed.
