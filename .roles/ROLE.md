# OSW Review Roles

Eight functional lenses govern OSW atlas reviews. They are not personas
or simulated real people, and they do not replace external scientific peer
review. They make the repository's own quality claims explicit and testable.

## Core roles

| Role | Owns | Decisive question |
|---|---|---|
| **CURRENT** | Physical oceanography | Is the proposed mechanism physically and causally defensible? |
| **SOUNDER** | Climate-data stewardship | Can the displayed field be identified, interpreted, and reproduced exactly? |
| **CHART** | Ocean cartography | Does the map represent the data without visual or geographic distortion? |
| **BEACON** | Public-science editing | Will a curious reader understand both the insight and its limits? |
| **HARBOR** | Accessibility | Can people use and understand the atlas without relying on color, pointer, or motion? |
| **KEEL** | Reproducibility engineering | Would an automated, offline check catch a broken artifact? |
| **LOGBOOK** | Repository stewardship | Does the public repository truthfully expose its status, ownership, and next work? |
| **ORBIT** | Planetary comparison | Does an Earth–gas-giant analogy preserve mechanism without implying false equivalence? |

## Tiebreaker order

When recommendations conflict, earlier roles govern:

1. **CURRENT** — a physically false map is not rescued by presentation.
2. **SOUNDER** — an unidentified or irreproducible field cannot support a claim.
3. **CHART** — valid data can still become a misleading map.
4. **BEACON** — the public claim must not outrun the evidence.
5. **HARBOR** — access to the meaning is part of correctness.
6. **KEEL** — verified behavior protects all preceding contracts.
7. **LOGBOOK** — release state and maintenance must remain truthful.
8. **ORBIT** — comparison is valuable only after the Earth-side object is sound.

## Core tensions

| Pulls | Against | Resolution |
|---|---|---|
| CURRENT | CHART | Prefer physical qualification over a cleaner but false boundary. |
| SOUNDER | BEACON | Keep essential variable, depth, time, and baseline metadata even when simplifying prose. |
| CHART | HARBOR | Add redundant encodings rather than depending on a beautiful palette alone. |
| KEEL | SOUNDER | Default tests stay offline; source refreshes are explicit, separately reproducible operations. |
| ORBIT | BEACON | Use memorable analogy only with the transfer limit beside it. |

## Review protocol

Use at least the roles whose scopes intersect the artifact. Atlas releases
normally require all eight. Every selected role records at least three findings
with evidence, severity (`P1`, `P2`, or `P3`), and an actionable recommendation.

- **P1**: scientific invalidity, materially misleading output, unreproducible
  evidence claim, or a missing release gate that can publish broken results.
- **P2**: important limitation, ambiguity, accessibility failure, or maintenance
  risk that should be corrected.
- **P3**: non-blocking improvement or confirmed strength.

Write synthesized reviews under `signals/roles/check/`. Any P1 produces a
`NEEDS-WORK` verdict. A review artifact records the source commit and the roles
used so a later review can be compared rather than silently substituted.

## Adding a role

Add a role only when a recurring class of important defects lacks an owner.
Define its scope, checks, exclusions, tensions, and tiebreaker position. Keep
roles functional; do not model a living or historical person.
