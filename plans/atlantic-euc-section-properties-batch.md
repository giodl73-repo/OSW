# Atlantic EUC original section properties batch

2026-10-08. Editorial source extraction; scientific admission pending.

## Evidence

Voituriez (1983), Oceanographie tropicale 18(2):163–183, institutional original
PDF, 1,887,693 bytes, SHA-256
`a1c4b1dfc46247cb9c7da90ea03aa1a240bc987bd26b21c9cdf49f027d457e0b`.
Tables I/II on printed pp165/168 and Figure 2 p167 were visually inspected.
Eight Table II records retain campaign/station labels, maximum eastward speed
and the depth of that maximum. The profiler's velocity reference is 500 m
assumed motionless. No exact station latitude or numerical errors are supplied.
The original is ignored because redistribution permission is unestablished.
Acquisition and the editorial extraction are shipped; no new fixture download
is required for default offline checks.

Campaign 7910 has June 1979 in Table II versus June 1980 in Table I. Campaign
7912 has November 1974 in Table II versus October–November 1979 in Table I.
Neither date is resolved. Table II's August 1978 / January 1979 property
months remain separate from broader Table I campaign periods.

The paper's upper-200-m / >=20-cm/s transport support is not horizontal width.
The FAO Paper 292 background 200 km lead does not supply these campaign widths.
Future Figure 2 paired-edge digitization needs declared depth, velocity metric,
geographic calibration and reading uncertainty. No width, monthly cycle,
annual extrema, occupied polygon or state intersection is added in this batch.

## Integration

The Atlantic route card adds two discrete property charts, hollow conflict
points, both original date claims and an accessible data table. Its source
query directly exposes all eight records. Source review lives in the existing
route_decisions query collection; no new collection or width type is invented.
Dashboard source fingerprints update; width coverage stays 92 records across
48 owners, with 44 unassessed. The lossless source index has 104 documents.

Python validates values, dates, method, owner, null support, admission exclusions
and protocol/acquisition hashes. Compiled Rust binds the complete source audit
and its planning record. Runtime verifies the compiled extraction rather than
possession of the paper. Renewed extraction can require original verification.

## Rebuild and checks

Run `python analysis/check_atlantic_euc_section_properties.py --require-original`
when the ignored original is available. Then build the dashboard, Rust query
bundle, source index and Rust engine in order using their `analysis/build_*.py`
commands. Run `python -m pytest -q`, the registered
`analysis/test_atlantic_euc_section_properties_browser.py` and generic query
browser check with the configured browser. The new browser check verifies
values, date conflicts, mobile text bounds/readability, source/native/WASM
equality and coherent receipt mutations. JavaScript and page assignments are
checked separately; assignments alone do not establish passing UI tests.

Previous PR #53's two remote offline runs failed while acquiring the existing
Djakoure Guinea fixture, before reaching tests. Both NetCDF fixture jobs
passed. That source download is not evidence against the Atlantic extraction;
remote protected validation remains required before main landing.

Confirmed locally: 854 Python tests and 918 subtests passed in 262.54 seconds.
The final engine rebuild passed 40 Rust tests and produced native/WASM engines.
The registered Atlantic check passed against the final artifacts, including
mobile text bounds and readability, exact source/native/WASM record equality
and coherent scope-mutation rejection. The mobile speed chart was visually
inspected. All 104 indexed original JSON documents and engine hash receipts
were verified. All 46 JavaScript modules pass syntax checks; all 14 pages retain
validation assignments. The generic query browser check also passed native/WASM parity, scoped joins,
sharing/export, invalid queries, pagination, mobile and failed integrity load.
The complete registered browser runner has not been claimed here.
