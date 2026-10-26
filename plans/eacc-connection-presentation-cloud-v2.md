# EACC diagram cloud case v2

This case replaces the failed v1 verifier, not its evidence. Keep the exact v1
code/preflight and failed run40418857904/a2 unchanged; its request stays disabled.
The original parent engine, packet and WASM identities remain the same.

Before opening the browser, stream-verify every inherited manifest entry.
Use only the four exact historical bindings defined in the v2 source registry:
check both old archive and currently deployed bytes, with their recorded byte
lengths. Reject production-dependency rebinding. Report all unknown mismatches
in a retained failure receipt before stopping. No pin is ignored or dropped.

The overlay preserves existing workflow provenance pins through their checked
archives, explicitly repairs the two already-stale navigation HTML pins, changes
only the current-source UI bytes and adds the new EACC SVG. No deployed HTML is
rewritten, scientific source regenerated, query row added, or engine rebuilt.
Preserve all earlier manifest fields and compiled/data hashes.

Use a separate disabled request, frozen preflight and workflow on the existing
branch. Once source backup is verified and other jobs are terminal, activate
only v2. Shared concurrency, one cloud job/CPU, low priority, no local browser
or installed-data load. Preserve actual failures and disable the request after
the case terminates.

Browser and installation gates remain those of v1: exact installed EACC record,
loaded diagram, 320/390px screenshots without overflow, working keyboard query,
no page errors, unchanged full engine bytes after the check. Retain compact
receipts and three proposed presentation files only. Inspect actual screenshots
before separately installing a presentation overlay. No main merge, scientific
release, extra current measurement, new physical geometry or annual range.
