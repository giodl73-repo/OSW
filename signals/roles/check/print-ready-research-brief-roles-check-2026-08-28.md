---
skill: roles-check
topic: print-ready-research-brief
date: 2026-08-28
source_commit: 6ef07bd
roles_used: [CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED
---

# Roles check: print-ready research brief

## Artifact identification

- **Type:** A4 print stylesheet and generated seven-page PDF rendering of the reviewed Research Note.
- **Reviewed:** print CSS, PDF metadata, extracted text, rasterized pages 1/2/4/7, and print-contract tests.
- **Scope:** private researcher handoff. The PDF changes presentation only; scientific claims retain their earlier reviews.

## Role selection

CHART checks evidentiary visual grammar; BEACON checks the printed reading path; HARBOR checks legibility and equivalent text; KEEL checks reproducible rendering and validation; LOGBOOK checks generated-artifact and release boundaries. CURRENT, SOUNDER, and ORBIT are excluded because no claim, source receipt, or planetary comparison changed.

## CHART — scientific visual presentation

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Evidence classes remain labeled in text and outlined tags when the dark screen palette becomes a light paper palette. | P3 | Claims page | Preserve the labels in any grayscale derivative. |
| 2 | The exact-byte receipt retains variable, reference, checksum, and artifact columns without clipping on A4. | P3 | Receipt page | Keep full checksums selectable rather than rasterizing the table. |
| 3 | The PDF contains no new map rendering that could lose projection, legend, or evidence-class context. | P3 | Scope | Link to the reviewed full map rather than embedding a reduced unreadable map. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The cover leads with the research question and immediately distinguishes temperature, heat content, and transport. | P3 | Cover | Retain this as page one in shared copies. |
| 2 | Each major scientific section starts on a new page, preserving the sequence from question to claims, receipt, literature, next work, and inspection. | P3 | Pagination | Avoid adding front matter that delays the claims ledger. |
| 3 | The closing page states that internal review does not replace external peer review. | P3 | Footer | Keep this sentence in every exported PDF. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | PDF text is selectable and extracts to 9,681 characters rather than being flattened into images. | P3 | Generated PDF | Preserve text output if a future PDF tool is substituted. |
| 2 | The light print palette uses dark text, visible rules, redundant labels, and underlined links; no meaning relies on background color. | P3 | Print stylesheet | Verify tagged-PDF structure before a public archival release. |
| 3 | Tables repeat header groups, rows avoid page breaks, and card groups retain readable two-column organization. | P3 | Print layout | Recheck if additional rows increase pagination. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Headless Edge generates a seven-page A4 PDF with no browser headers or footers. | P3 | PDF generation | Record the browser version if PDFs become canonical releases. |
| 2 | `pdfinfo`, `pdftotext`, and raster inspection confirm page count, page size, selectable content, and no visible clipping on sampled pages. | P3 | Output validation | Automate page/text assertions if the PDF is committed later. |
| 3 | The offline suite passes 29 tests and requires the A4 page rule, explicit page breaks, and print-color handling. | P3 | Regression test | Keep PDF generation optional because browser binaries are environment-specific. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The print contract is tracked while the generated binary remains a versioned private-package artifact, avoiding an unexplained binary in Git. | P3 | Artifact boundary | Continue packaging the PDF with its source commit and checksum. |
| 2 | The PDF calls itself a private Atlas 08 review preview and retains project version/citation guidance without claiming a new release. | P3 | Cover/footer | Update only after an authorized promotion. |
| 3 | No recipient identity, private-project reference, machine path, or endorsement request appears in the printable content. | P3 | Boundary scan | Keep recipient-specific email text outside the repository and PDF. |

## Synthesis

```text
Roles reviewed: 5
P1 blockers: 0  |  P2 issues: 0  |  P3 notes: 15

Verdict: APPROVED

Top finding: The Research Note now has a professional paper form without losing selectable evidence, exact receipts, claim boundaries, or private-preview status.
Cross-role consensus: The PDF is suitable for private researcher handoff because print polish does not outrun the reviewed scientific contract.
```

## Amendments applied

1. Added a dedicated A4 light-paper stylesheet with section-level pagination and print-safe evidence labels.
2. Removed browser-generated date, URL, and page chrome from the packaged PDF.
3. Verified seven-page metadata, selectable text, complete receipt columns, and representative raster pages before packaging.
