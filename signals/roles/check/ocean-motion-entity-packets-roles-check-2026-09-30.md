---
skill: roles-check
topic: ocean-motion-entity-packets
date: 2026-09-30
roles_used: 5
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Rights-screened entity packets: role review

Artifact: the 213 per-object JSON packets in the rights-screened preview,
their build/check scripts, and the review-site download links. SOUNDER reviews
provenance, KEEL reproducibility, CHART spatial meaning, HARBOR access, and
LOGBOOK the publication boundary.

| Role | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| SOUNDER | A packet must include its exact screened source metadata and claim rows. | P2 | Packet closure | Verify source IDs and claim targets against the screened collections. Done. |
| SOUNDER | Cross-object evidence should remain labeled as related entities, not silently merged with the subject. | P2 | Packet structure | Keep `related_entities` separate from the focal entity. Done. |
| SOUNDER | Internal ledger pointers depend on the parent preview directory. | P3 | Source locators | Preserve the preview source-ledger excerpts and relative base path. Done. |
| KEEL | Each packet needs a stable safe filename for IDs containing punctuation and spaces. | P2 | Filename builder | Use sanitized names with an ID hash and validate unique indexed paths. Done. |
| KEEL | Rebuilds must remove stale packets after source-set changes. | P2 | Builder | Remove only obsolete direct child JSON files in the verified packet directory. Done. |
| KEEL | The preview and review-site manifests must cover all packet bytes. | P2 | Manifests | Include packet files and builder digest, and check the site file set. Done. |
| CHART | A center or editorial point must not become whole-eddy containment in an export. | P2 | Packet limitations | Retain assessment status and explicit point/footprint caveat. Done. |
| CHART | A state packet should keep both candidate and unresolved relations. | P3 | State records | Include applicable state assessments and relations without filtering by positive status. Done. |
| CHART | Related objects need stable IDs and labels for atlas navigation. | P3 | Related entities | Include screened entity stubs for related IDs. Done. |
| HARBOR | The per-object download must be reachable by keyboard and named as a review copy. | P2 | Object page | Use a standard anchor with descriptive text and download attribute. Done. |
| HARBOR | Readers need an equivalent text explanation of evidence limits. | P3 | Packet limitations | Include plain-language limits in the JSON and on the object page. Done. |
| HARBOR | File access should work on narrow screens without an extra control. | P3 | Browser route | Keep the link in the existing identity card; browser deep-link test passes. Done. |
| LOGBOOK | Packets must not reintroduce excluded provider URLs or source IDs. | P2 | Screening boundary | Validate packet text against all pending URLs and source closure. Done. |
| LOGBOOK | Review copies must not appear to have a released dataset citation. | P2 | Status | Mark every packet as unpublished and keep the owner gate open. Done. |
| LOGBOOK | Counts in the site and documentation must match generated artifacts. | P3 | Documentation | State 213 packets and include them in manifests. Done. |

Roles reviewed: 5. P1 blockers: 0; P2 issues: 9; P3 notes: 6.
Verdict: **APPROVED-WITH-CONDITIONS** for internal review distribution. The
packets do not authorize public dataset deposition or resolve the open source
and scientific reviews. Top finding: source and claim closure must survive
screening for every downloadable record. SOUNDER, KEEL, and LOGBOOK agree.

Amendments: (1) Validate source and claim closure for every packet; done.
(2) Include all packet files and builder code digest in the preview manifest;
done. (3) Keep the public release gate closed until source terms, scientific
claims, accessibility, and owner decisions are complete; open.
