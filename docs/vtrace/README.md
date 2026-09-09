# OSW VTRACE

This directory applies the NASA-inspired VTRACE systems-engineering discipline
to OSW. VTRACE governs product intent, traceability, verification, validation,
and review; it is not an ocean-atlas feature or a claim of NASA authorship,
endorsement, or review.

## Adoption scope

The scope is the existing OSW repository and its path from a research-rich
review branch to a coherent, evidence-linked public ocean atlas. The
[central roadmap](../../ROADMAP.md) controls product sequence. VTRACE records
why that sequence exists, what the product must do, and what evidence permits a
claim or release.

## Stage rule

Only one stage artifact is opened at a time. Each stage is reviewed through the
repo's native [`.roles`](../../.roles/ROLE.md), amended until no unresolved P1
or P2 finding remains, and recorded at a fixed point before the next stage
begins.

| Order | Stage | Artifact | Status |
|---|---|---|---|
| 1 | Mission / Need | [MISSION.md](MISSION.md) | fixed point — pass with bounded risk |
| 2 | CONOPS | [CONOPS.md](CONOPS.md) | fixed point — pass with bounded risk |
| 3 | Requirements | [REQUIREMENTS.md](REQUIREMENTS.md) | fixed point — pass with bounded risk |
| 4 | Specification baseline | [SPECIFICATION_BASELINE.md](SPECIFICATION_BASELINE.md) | fixed point — pass with bounded risk |
| 5 | Architecture | [ARCHITECTURE.md](ARCHITECTURE.md), [PACKAGE_BOUNDARIES.md](PACKAGE_BOUNDARIES.md) | fixed point — pass with bounded risk |
| 6 | Interfaces | [INTERFACES.md](INTERFACES.md) | fixed point — pass with bounded risk |
| 7 | Design and code rigor | [DESIGN.md](DESIGN.md), [CODE_RIGOR.md](CODE_RIGOR.md) | fixed point — pass with bounded risk |
| 8 | Implementation planning | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md), [WORK_PACKAGES.md](WORK_PACKAGES.md) | fixed point — pass with bounded risk; packages proposed |
| 9 | Verification | [VERIFICATION.md](VERIFICATION.md) | fixed point — pass with bounded risk; target evidence pending |
| 10 | Validation | [VALIDATION.md](VALIDATION.md) | fixed point — pass with bounded risk; execution evidence blocked |
| 11 | Trace | [TRACE.md](TRACE.md) | fixed point — pass with bounded risk; no status promotion |
| 12 | Review | [REVIEW.md](REVIEW.md) | fixed point — pass with bounded risk; WP-OSW-001 pulse 001-A entry only after immutable baseline commit |

The stage names express engineering control, not visitor-facing navigation.
Open risks discovered during any stage also enter the repo's
[pitfall register](../../design/pitfalls/README.md) when they describe a
recurring structural failure mode.

Mission-stage review:
[`mission-and-pitfall-foundation-roles-check-2026-09-06.md`](../../signals/roles/check/mission-and-pitfall-foundation-roles-check-2026-09-06.md).

CONOPS-stage review:
[`conops-roles-check-2026-09-06.md`](../../signals/roles/check/conops-roles-check-2026-09-06.md).

Requirements-stage review:
[`requirements-roles-check-2026-09-06.md`](../../signals/roles/check/requirements-roles-check-2026-09-06.md).

Specification-baseline review:
[`specification-baseline-roles-check-2026-09-06.md`](../../signals/roles/check/specification-baseline-roles-check-2026-09-06.md).

Architecture-stage review:
[`architecture-roles-check-2026-09-06.md`](../../signals/roles/check/architecture-roles-check-2026-09-06.md).

Interfaces-stage review:
[`interfaces-roles-check-2026-09-06.md`](../../signals/roles/check/interfaces-roles-check-2026-09-06.md).

Design-and-code-rigor-stage review:
[`design-code-rigor-roles-check-2026-09-07.md`](../../signals/roles/check/design-code-rigor-roles-check-2026-09-07.md).

Implementation-planning-stage review:
[`implementation-planning-roles-check-2026-09-07.md`](../../signals/roles/check/implementation-planning-roles-check-2026-09-07.md).

Verification-stage review:
[`verification-roles-check-2026-09-07.md`](../../signals/roles/check/verification-roles-check-2026-09-07.md).

Validation-stage review:
[`validation-roles-check-2026-09-07.md`](../../signals/roles/check/validation-roles-check-2026-09-07.md).

Trace-stage review:
[`trace-roles-check-2026-09-07.md`](../../signals/roles/check/trace-roles-check-2026-09-07.md).

Final Review roles check:
[`final-vtrace-review-roles-check-2026-09-07.md`](../../signals/roles/check/final-vtrace-review-roles-check-2026-09-07.md).
