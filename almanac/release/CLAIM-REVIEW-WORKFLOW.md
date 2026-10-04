# Ocean motion claim review workflow

The candidate package has 14,063 normalized claim records. A claim may record
an unresolved atlas assessment, a source-reported number, or a dated
observation. Its locator is a place to check evidence, not a review decision.

Start with `almanac/release/v0.1.0/claim-science-review-first-pass.csv` (65
externally located claims). The eight ranked lengths come first. Check the
source passage or provider field, units, geographic and temporal scope,
current or eddy identity, evidence class, and the public wording. For derived
distance floors, inspect the gate-distance ledger and confirm the source
supports the gates; do not treat the source as reporting the derived number.

The separate `ranked-length-editorial-reviews.json` binds the eight existing
source-passage audit findings to exact claim fingerprints. It records whether
the quoted number is present and the scope warning to inspect. Its
`scientific_review_status` remains `not_individually_reviewed`; this editorial
index does not enter a decision in the scientific review ledger below.

Record each completed review in `research/ocean-motion-claim-reviews.json`:

```json
{
  "claim_id": "claim:measurement:0001",
  "review_fingerprint": "copy the exact 64-character value from the claim or review worklist",
  "reviewer": "reviewer's actual name or stable identifier",
  "review_date": "YYYY-MM-DD",
  "review_status": "verified",
  "review_note": "What the source supports, including any scope limit"
}
```

`review_status` may be `verified`, `needs_revision`, or `rejected`. The
builder refuses duplicate decisions and a review whose fingerprint no longer
matches the claim. A source, value, locator, scope, or method edit therefore
requires a fresh review. `needs_revision` and `rejected` are review findings,
not publication approvals. Reviewers should fix or remove a claim with either
finding before promotion.

Review the internal-ledger claims by evidence rule and source-record family.
For current/state and NASA crop/state rows, inspect the decision rules and a
stratified sample of positive, negative, boundary, and unresolved pairs, then
record individual decisions for any disputed row. For 7,504 named eddy/state
assessments, verify that unresolved physical containment remains unresolved;
regional gateways and source points do not establish a dated eddy footprint.
Every claim retains `not_individually_reviewed` until an actual decision is
entered for its exact fingerprint. The package validator checks the review
ledger and never converts a family audit into individual review statuses.

The separate source-use review queue governs redistribution and license terms.
Scientific verification does not grant permission to redistribute provider
data or imagery.
