# WP-OSW-001A Python Tool Bakeoff

## Decision

Do not add a formatter, linter, or type-checker dependency in pulse 001-A.
Retain the stdlib compile/AST checks, focused contract tests, full dual-runner
suite, line-length inspection, and native-role review as the controlled gate.

This is an explicit pulse-scoped tool decision for WAIVER-OSW-003, not a claim
that linting or type checking has no value. Revisit when a later package adds a
dependency manifest/CI toolchain or when the existing checks miss a qualifying
defect.

## Candidates and observations

| Candidate | Availability on entry host | Useful signal | Overlap / cost | Decision |
|---|---|---|---|---|
| `ruff` | not installed | Fast formatting and broad static linting for new Python. | Adoption now adds a new versioned development dependency/configuration surface for two stdlib modules; no repo-wide Python tool policy exists. | reject for 001-A; revisit at shared-toolchain trigger |
| `mypy` | not installed | Checks annotated identity/envelope boundaries and caller types. | Requires dependency/configuration and a deliberate coverage policy across a large untyped analysis corpus; partial enforcement could imply more assurance than it provides. | reject for 001-A; revisit when two typed contract consumers exist |
| `pyright` | not installed | Strong type narrowing and editor/CI feedback. | Adds a Node/package/configuration path not otherwise present and overlaps the same unsettled repository-wide typing decision. | reject for 001-A; revisit with browser/Python shared tooling decision |
| `black` | not installed | Deterministic formatting. | Adds a formatter/version/configuration commitment solely for a bounded pulse. | reject for 001-A; apply and inspect 120-column discipline manually |
| stdlib `compileall` + `ast` inventory | installed with Python 3.14.2 | Syntax validity, parseability, function-span and import inspection with no new dependency. | Does not provide semantic typing or broad lint rules. | adopt for 001-A L0/L1 with limitations explicit |
| `unittest` + `pytest` | installed/current project baseline | Behavioral, negative, immutability, redaction, exact-identity, and regression evidence. | Behavioral coverage is authored and can share misconceptions with implementation. | adopt with adversarial fixtures and eight-role review |

No candidate was installed or downloaded. The bakeoff made no network request
and changed no dependency, workflow, or package manifest.

## Measured implementation

Before final evidence, the three new Python files contained no line over 120
characters. AST inspection reported maximum function spans below the 60-line
soft cap:

| File | Nonblank/noncomment logical lines | Largest function span |
|---|---:|---:|
| `analysis/osw_diagnostics.py` | 178 before readability expansion | 19 |
| `analysis/osw_contracts.py` | 233 | 15 |
| `analysis/test_osw_contracts.py` | 218 before final tests | 24 |

The registry data table was expanded vertically for reviewability; it is data,
not one control-flow function. Final closeout recomputes these metrics rather
than treating the preliminary counts as immutable.

## Trigger to reconsider

Re-open the bakeoff if any of these occurs:

- a second production consumer depends on these typed contracts;
- 001-B adds nontrivial adapters or a dependency/configuration manifest;
- CI and contributor commands are standardized across the analysis corpus;
- review finds a type/format/import defect the adopted checks did not catch; or
- an owned function crosses the size/branch thresholds in CODE_RIGOR.

Until then, the absence of a new tool is not a waiver from syntax, size,
behavioral, negative, mutation, secret/redaction, full-suite, or role-review
evidence.
