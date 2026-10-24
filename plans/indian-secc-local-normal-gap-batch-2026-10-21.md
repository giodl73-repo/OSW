# Indian SECC: local velocity-normal sections and candidate-axis checks

Baseline25bbdbb, with the same numerical artifacts as Linux-tested5bad057.
The previous goal turn repaired a real cross-platform comparison defect and
verified all25 scientific reports byte exactly. This batch implements the
previously declared local-normal method, not another source acquisition.
Same continuing draft PR83; no new PR/main merge.

## Method and actual findings

The protocol was declared before calculation. Two pre-calculation numerical
clarifications retain maxima within1e-10m/s as ties and allow a short final
RK4 station remainder. No gates were relaxed after inspecting results.

All twelve2013 monthly source fields retain paired OSCAR2017.0 support,
nominal15m mapped upper-ocean interpretation and exact original inputs. Two
historical meridian seeds, three native latitude offsets and two normal
sampling steps give144 attempts. Velocity-normal geodesics use transported
tangents and signed projected velocity. All four bilinear corners and each
sample rectangle must be supported. Refine once within40km; retain weak,
tied, search-edge, contrast and source failures.

The central seed attempts test local transverse peaks at−100/−50/0/+50/+100km
along a short adaptive-RK4 monthly mean-field streamline. These arc parameters
are not travel time, particle trajectories or a named-current length. Native
offsets have central sections only and cannot pass the five-station test.

-144 attempts /48 central-seed attempts /120 sampled station sections.
-88 station sections have paired nominal half-peak diagnostic edges;36 are
  central sections. They are not independent observations of a current width.
- One10km November80⅓E attempt passes all five local checks. It fails at5km;
  **zero primary seeds pass all five checks at both sampling steps**.
- Status counts: one five-check pass,19 unresolved candidate attempts,
  20 insufficient-contrast refinements,80 search-edge refinements,
  20 offset-sensitivity sections and four weak/non-eastward seeds.
- All initial failures, partial paths, peak margins, normal samples, source-cell
  indices, projected components,0.4/0.5/0.6 edges and interpolation residuals
  remain available. Step, seed and threshold changes are not a confidence
  interval or a physical annual range. Native grid-scale resolution flags are
  separate from5/10km numerical sampling.

No robust named-current axis, canonical width/length, physical annual range,
state intersection or NASA identification is admitted. A coarser-step pass is
not selected in preference to the failed finer-step case.

## Required information and visualization

Twelve geographic monthly panels show5km central candidates, original/refined
seeds, partial or failed paths and paired normal spans.10km/offset cases stay
in the data and are explicitly distinguished. Colors label the two meridians;
line style labels local/five-station support. Gray is outside interpolation
support, not a land claim. Signed eastward source colors share one clipped
scale; geographic degrees are not used as a distance ruler.

Standalone SVG has a named image role, title and description; semantic monthly
and case summaries are the data equivalent. The current card links maps,
144 outcomes,12 monthly rows,72 step comparisons and full section/source-cell
records through the existing Rust/WASM source query. Source report is registered
as scientific reconstruction target26. No new original source is redistributed.

## Local verification and pending gates

18 tests pass: normal transport/orthogonality, analytical straight-jet half-peak
width, positive five-station control, actual arc geometry, missing-corner stop,
numeric ties, flat/weak failures, exact real-source report reconstruction and
independent source-grid interpolation for over1000 retained sample vectors.
PNG visually inspected, captions spaced, SVG parsed. A Windows text-encoding
issue in SVG postprocessing was fixed by explicit UTF-8 before finalization.

Integrated dashboard/index/packet/native-atlas/WASM builds and109 Rust tests
pass. Actual Chrome passes all144 scalar outcomes,12 monthly summaries and72
step comparisons exactly against native queries, plus one complete five-check
candidate and one complete weak/failed case. Keyboard card/figure, accessible
standalone SVG,320px reflow, export availability and zero automatic original
requests pass. All403 staged engine dependency hashes match.

All25 prior reports/producers and428 indexed originals remain exact; all430
current source hashes verify. All prior scientific typed rows, capabilities
and observation dates remain exact; only the SECC fingerprint/evidence links
change. Nine superseded generated packet parts retired after exact length/SHA
and workspace containment checks; originals retained.

Packet139,755,756 bytes/nine parts; WASM49,477,159 bytes. Source corpus
315,176,178 original bytes/48,297,867 compressed bytes. Fresh Linux reconstruction passes at5070eec/run39720938432/scientific
job119633957327: all26 reports encode byte exactly; every retained/rebuilt SHA
matches its local report. NetCDF119633956968 also passes. Main50 collections/59,828 rows,165 sources and
55 diagnostics remain unchanged; source index430 documents. Accepted101 names/28 proposals,
12 ranked lengths/89 unranked and158 scoped widths/83 owners with18 uncovered
owners remain. Only the SECC source fingerprint/evidence links should change.
Offline119633957201 fails before tests on Stramma1992 primary and institutional
mirror HTTP403. This run does not reach or resolve the earlier IRD Rotschi403.
The complete-suite/local4GiB disk gate remains open; no overall green claim.

## Workspace source retention

Space was recovered by keeping byte-exact compressed copies of four generated
old indexes and retiring their uncompressed temporary copies. The redundant
8,108,045,936-byte EAC extracted cache was also verified against its retained
381,438,579-byte original ZIP member before retirement; all original bytes
remain recoverable, with length/SHA receipts. Primary source/data files and
the other running servers were preserved. This is not a new data acquisition.

## Reproduce

```powershell
python analysis/indian_secc_local_normals.py
python analysis/build_indian_secc_local_normal_figure.py
python -m pytest analysis/test_indian_secc_local_normals.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_indian_secc_local_normals_browser.py
```

Next: inspect the failed ridge-alignment/contrast and sampling-step evidence
before any axis-method revision; seek independent current-association support.
Do not tune gates to force admission. Continue other current gaps on PR83.

All20 scoped review findings are resolved; one complete-suite P2 gate remains
open,zeroP1. This receipt/review update changes documentation only: every
numerical input and generated artifact remains identical to Linux-tested5070eec.
