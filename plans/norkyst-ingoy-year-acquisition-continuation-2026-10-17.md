# Continue the declared full-year temporal acquisition

The January/July source and figure checkpoint is f3572c1, on the existing current-gap branch and PR 83. Its acquisition receipt identifies the original collector by file checksum; that version remains in Git history. The continuation does not relabel the earlier producer.

## Scope

Keep the frozen twelve-month 2024 declaration and existing section/layer/packing/filter rules. Complete-year acquisition requests 8,784 calendar hours plus 36 hours on each side of the year, for 8,856 distinct source timestamps across 370 archive dates. Reuse the already retained days; acquire the missing days explicitly with two workers.

```text
python -u analysis/fetch_norkyst_ingoy_continuous.py --all-months
```

The journal is `research/source-data/norkyst-ingoy-months-2024/acquisition-year.json`. It remains partial until every daily request passes. Failures preserve the source evidence and cannot become zero flow or a completed year. Do not edit the collector or source validator during the live run: startup code pins are checked before completion.

## Preservation and verification

- Restore missing cache members from the validated retained ZIPs, rather than downloading those originals again. Existing cache corruption rejects.
- Preserve frozen ZIP containers without recompressing them. Check their prior byte pins, member sets and every original member.
- Metadata belongs to the archive day; a new hourly cut must keep the known daily metadata pin. Its different field response must not inherit the earlier hourly cut's field-byte pin.
- Save the progress journal atomically. Source acquisition timestamps survive revalidation, including the qualified initial metadata-probe time bounds.
- Dedicated final check: 20 tests and 20 subtests passed in 11.85 seconds, including full two-month reconstruction and four collector-extension tests. No existing scientific array or generated figure changes in this continuation.

The clean combined UI gate at 8130086 completed: 1,619 tests and 1,061 subtests passed in 2,171.89 seconds. That run predates the continuous-month research and is not represented as its combined gate. The final rolling release gate remains required after the new temporal data and UI are integrated.

## Remaining deliverables

After the source run completes, reconstruct all twelve monthly sections under the same gap/filter/statistics rules, review the year visualization and integrate the temporal support into the shared current/query views. Preserve the original two-month capsule. Complete temporal sampling does not by itself resolve current association, coastal coverage, physical boundaries, whole-current widths or annual physical width extrema.
