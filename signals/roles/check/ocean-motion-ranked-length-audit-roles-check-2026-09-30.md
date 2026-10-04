---
skill: roles-check
topic: ocean-motion-ranked-length-audit
date: 2026-09-30
roles_used: 7
p1_count: 1
verdict: NEEDS-WORK
---

# Role review: ranked current-length source-passage audit

Artifact: `almanac/release/RANKED-LENGTH-EVIDENCE-AUDIT.md`, its public atlas
link, and the six `published_estimate` length assessments in candidate v0.1.0.
Type: scientific data and public atlas presentation. The relevant installed
roles are CURRENT (oceanographic meaning), SOUNDER (provenance), CHART
(geographic encoding), BEACON (public wording), HARBOR (accessible evidence),
KEEL (release reproducibility), and LOGBOOK (publication status).

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| C1 | The six values refer to circumpolar flow, basin pathway, regional current belts, and one seasonal compound coastal flow. Numerical order alone cannot compare like-for-like axes. | P2 | Audit table and rank | Keep the scope adjacent to every value and avoid claiming a global longest-current census. |
| C2 | The California source reports a northern geographic description and parenthetical latitude that disagree. Follow-up traced its reference [15] to Bograd and Lynn (2003), a *Southern* California Current System paper; NOAA independently supports the broad Vancouver Island–Punta Eugenia geography, while its nearly 3,000 km number describes the larger ecosystem. | P2 | California row | Keep the 3,000 km as a source quote only; do not treat the paper's latitude or NOAA's ecosystem extent as a measured current axis. |
| C3 | The Kuroshio number appears in a copepod paper's background introduction, rather than in a length analysis. A later field paper repeats a similar figure without tracing a current axis. | P2 | Kuroshio row | Seek direct oceanographic endpoint or path evidence; retain its lower-confidence wording. |

## SOUNDER — data stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| S1 | Every ranked value has a URL and passage locator in the claim worksheet. | P3 | Six ranked claims | Preserve locators and fingerprints when source records change. |
| S2 | The California PDF and Humboldt thesis are file-addressed, but most publisher passages are live HTML; the Crossref receipt pins bibliography, not quoted page bytes. | P2 | Source reproducibility | Pin passage excerpts or source response digests where terms allow, then record access dates. |
| S3 | The audit distinguishes the thesis's Humboldt belt from its smaller Peru study area. | P3 | Humboldt row | Keep both scopes separate in every reused measurement. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| G1 | A single rank column can imply common path endpoints although the sources do not define a shared axis. | P2 | Current table | Keep “source-reported estimate” and scope in the table; add geographic gates only from explicit source evidence. |
| G2 | The rank is separate from drawn-arrow span and source-gate lower bounds. | P3 | Length methods | Preserve those evidence classes when map layers change. |
| G3 | The Australian source describes a winter shelf-edge system across several named currents. | P3 | Australian row | Never draw the 5,500 km as a permanent Leeuwin-only line. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| B1 | The atlas now places the audit link and its two source-quality flags above the rank table. | P3 | Current section introduction | Keep this visible explanation with the first encounter of the numbers. |
| B2 | The revised heading says “published length estimates,” matching the six-source ranking. | P3 | Current section heading | Preserve this bounded heading as the inventory grows. |
| B3 | A tied 3,000 km rank could be repeated as equal scientific confidence. | P2 | California and Kuroshio rows | Keep the audit's differing evidence-quality descriptions next to those values. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| H1 | The audit link uses visible descriptive text and the rank is in table text, independent of map color. | P3 | Current section | Preserve this text route to evidence. |
| H2 | The long current table needs a human keyboard, zoom, and screen-reader pass to confirm that scope and source remain associated with each value. | P2 | Current table | Record a human accessibility pass before public promotion. |
| H3 | The downloadable Markdown audit has a heading and tabular text, but wide rows may be hard to scan on narrow screens. | P3 | Audit table | Keep concise row prose and test narrow reflow in the public renderer. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| K1 | The audit is copied into the manifest-hashed candidate, and the release validator passes after regeneration. | P3 | Release manifest | Keep the audit in the deterministic build. |
| K2 | The audit records editorial conclusions but does not alter scientific review fields; all six claim fingerprints remain unreviewed. | P2 | Review workflow | Record individual decisions through the fingerprint-bound ledger after domain review. |
| K3 | Browser and package checks exercise the atlas and source rows, but they cannot judge whether length definitions match. | P3 | Validation | Keep evidence interpretation in the audit and reviewer workflow. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| L1 | Seventeen used external sources still have open rights decisions, including provider values redistributed in the candidate. | P1 | Public release gate | Resolve those terms or make an explicitly partial package before external deposition. |
| L2 | The audit explicitly says it is editorial and leaves the six claims individually unreviewed. | P3 | Audit status | Retain that distinction in release notes and citation text. |
| L3 | The candidate has no final dataset DOI or owner publication decision. | P2 | Publication record | Keep the status “candidate” until the source, scientific, and accessibility gates pass. |

## Synthesis

Roles reviewed: 7  
P1 blockers: 1 | P2 issues: 9 | P3 notes: 11  
Verdict: **NEEDS-WORK** for public dataset publication.

Top finding: source rights for provider values remain unresolved. CURRENT,
CHART, and BEACON agree that the rank must remain a comparison of six quoted
estimates with visibly different definitions and evidence strength. SOUNDER
and KEEL agree that exact locators make review possible but do not complete it.

Three amendments:

1. Resolve or exclude the 17 rights-pending source uses before public deposition.
2. Obtain individual scientific decisions for the six ranked claims, prioritizing the California source's inconsistent coordinate and southern-system citation, and the secondhand Kuroshio length.
3. Complete a human accessibility pass of the rank table and preserve the scope warning beside the public values.

## Follow-up — 2026-09-30

The six editorial passage findings now have an index keyed to exact claim IDs
and review fingerprints. The screened atlas displays the two source warnings
beside the California and Kuroshio ranked values and object details. Package
validation checks the fingerprints, and the browser check verifies that all
six values retain a visible pending scientific-review label. This resolves the
traceability and warning-display parts of S1, B3, and K2's workflow concern;
the individual scientific decisions, provider rights, and human accessibility
pass remain open. The NEEDS-WORK publication verdict remains in force.

## Corroboration follow-up — 2026-09-30

A PICES ocean review independently quotes the broad California Current
*System* as 3,000 km from Baja California Sur to northern Vancouver Island.
A 2015 observational *Oceanography* paper describes a roughly 3,000 km
Kuroshio journey from about 12°N to 35°N. Both are linked beside the two
ranked values in the screened atlas. They improve geographic and disciplinary
context but do not measure a common whole-current axis. The original claim
sources and fingerprints are unchanged, the two warning labels remain, and
individual scientific review is still pending.

## Canonical-source migration follow-up — 2026-09-30

The preceding C2/C3 and corroboration findings describe the former ranked
citations. The California ranked claim now cites the [PICES North Pacific
Ecosystem Status Report section, PDF page 3](https://meetings.pices.int/publications/special-publications/NPESR/2004/File_10_pp_177_192.pdf),
which reports a 3,000 km **California Current System** extent. The Kuroshio
claim now cites [Yang et al. (2015), PDF page 3](https://tos.org/oceanography/assets/docs/28-4_yj-yang.pdf),
which describes a roughly 3,000 km journey in an oceanographic article.
These replace the PLOS and copepod papers as canonical ranked sources. Neither
article supplies a measured whole-current axis under a common length method.

| Role | Finding | Severity | Resolution or next action |
| --- | --- | --- | --- |
| CURRENT | The source discipline and quoted geography improved, but system extent and introductory journey still differ physically. | P2 | Retain the scope warnings and obtain individual scientific decisions. |
| SOUNDER | Both new locators, bibliographic records, and complete PDF response-byte SHA-256 digests are pinned in the source registry. The PDFs are linked rather than repackaged. | P3 | Recheck a live file against its digest if the publisher replaces it. |
| CHART | The two values remain source-reported estimates, not geometry for drawing a whole-current path. | P2 | Keep them outside gate, arrow-span, and traced-path classes. |
| BEACON | The screened atlas displays a warning beside both 3,000 km entries. | P3 | Preserve those warnings in any public rendering. |
| HARBOR | Browser checks cover visible warning text and narrow layouts; human keyboard and screen-reader review remains open. | P2 | Complete the human accessibility pass before promotion. |
| KEEL | Exact claim fingerprints changed to `a248aaeffbcf8e12277ff25c9fc6e97a0385a996e8fbbb630d851070b164ffd0` and `c840ef925e67315b36ba4b5552d948956df20965cfe384f7e8f4068d81a04bf3`; release, preview, site, and browser validators pass. | P3 | Keep fingerprint checks in the generated package. |
| LOGBOOK | Seventeen used external sources still need rights decisions; the two ranked claims remain scientifically unreviewed. | P1 | Keep public deposition and publication closed pending rights and scientific review. |

This follow-up supersedes the earlier statement that the original claim
sources and fingerprints are unchanged. Verdict remains **NEEDS-WORK** for
public publication. The three highest-priority amendments are (1) resolve or
exclude the 17 rights-pending source uses, (2) obtain scientific decisions on
the six ranked claims using their current fingerprints, and (3) complete the
human accessibility review before promotion.

## Florida Current and Gulf Stream proper follow-up — 2026-09-30

The six-claim count in preceding sections is historical. The current candidate
has eight ranked claims. Tomczak and Godfrey's *Regional Oceanography*, Chapter
14, PDF page 11 (printed page 239), reports approximately 1,200 km to Cape
Hatteras for the Florida Current segment and the next 2,500 km for the Gulf
Stream proper. NOAA's glossary independently separates these two segments
within the larger Gulf Stream System. The chapter PDF's SHA-256 is pinned in
the source registry; only the two attributed numerical facts are packaged.

| Role | Finding | Severity | Resolution or next action |
| --- | --- | --- | --- |
| CURRENT | The textbook's two values describe different, contiguous flow segments; neither measures a fixed reference streamline or the full system. | P2 | Keep the segment names and boundaries beside both values, and obtain scientific review. |
| SOUNDER | Both values have a page locator, versioned chapter citation, and complete source PDF digest. | P3 | Retain the source digest and check it if the host changes the file. |
| CHART | The previous 2,200 km Cape Hatteras-to-Grand Banks gate floor and the 2,500 km reported path estimate are different evidence classes. | P2 | Supersede the floor as primary length evidence; do not add it to the reported length. |
| BEACON | The rank now has eight values, with California and Kuroshio scope warnings and separate Florida/Gulf Stream rows. | P3 | Keep the eight-claim audit visible beside the rank. |
| HARBOR | Browser checks can verify text and links, but a human screen-reader pass is still absent. | P2 | Complete the human accessibility review before promotion. |
| KEEL | The Gulf Stream and Florida claims have new fingerprints, and later measurement IDs shifted by one; the editorial index binds all eight exact IDs. | P3 | Validate package and browser output after every regeneration. |
| LOGBOOK | The added book chapter has a narrow linked-factual use decision; 17 provider or cartographic uses remain pending. | P1 | Keep public deposition closed until those uses are resolved or excluded. |

Verdict remains **NEEDS-WORK** for public publication. The added numerical
evidence improves the ranked almanac without creating a global completeness
claim. Prior scientific and rights amendments remain open, now for eight
ranked claims.
