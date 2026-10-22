# Norwegian Atlantic Slope Current: working data admission

Continue `codex/current-measurement-gaps`, draft PR83. Base commit before this
batch: `def4311686cd6600795d5653db7d568d353d49dc`. No new PR or main merge.

## Scope and evidence

The Norwegian Atlantic Slope Current (NwASC) is admitted separately from the
ambiguous legacy Norwegian Current, the Norwegian Coastal Current and western
frontal branch. Baumann et al. (2026), doi:10.5194/os-22-17-2026, supplies primary
identity and static mean-core context from retained CC BY4.0 originals. The
Norwegian Atlantic Current parent remains proposed; no alias or parent-current
measurement inheritance is introduced.

Orvik and Skagseth (2003), doi:10.1029/2003GL017932, introduction[3], reports an
approximate **3,500 km broad eastern shelf-edge branch extent**. Original
publisher full-text prose was inspected through web retrieval; direct original
HTML/PDF downloads returned403. Original2003 PDF and figure custody are not
claimed. This historical broad branch may overlap downstream West Spitsbergen
naming: it is neither an additive component length nor a modern regional axis.
Reference period, fixed layer, geographic endpoint coordinates, error and
annual length range remain unspecified.

The official ICES Library archive supplied the original Orvik and Niiler
2001/W:10 report, doi:10.17895/ices.pub.25636341.v1, file45728298. Its
1,090,240 bytes match provider MD5 `c1aed50bebfb0c577d9203c938fbdc2f` and SHA256
`104ea7802b778a8bba44d44d74b01c43d96a7b59d109308c6449d4455354a93a`.
Printed page3 describes the eastern branch from Shetland toward the Arctic
west of Svalbard at80°N. Pages1,3,7 were visually inspected. This supplies
geographic context, not an independent measured3500km axis. Publication2001
is distinct from repository deposit2024. Under its ICES Custom Licence,
only factual custody metadata and OSW paraphrases are redistributed; the PDF,
rendered source pages and provider abstract remain private.

## Six scoped widths

| Record | Quantity and support | Limit |
|---|---|---|
| Orvik2001 cited regional description |30–50km branch-width summary, retained through the audited Mork2010 source | Contextual cited literature; no annual range or independent new observation |
| Mork2010 | Approximate50km surface ADT branch scale | Source operator/grid context retained; not a full-current width |
| Fer2020 |25–30km Gimsøy relative-geostrophic span | Four occupation dates do not provide four dated numerical widths; integration depth unspecified |
| Baumann2026 Svinøy | Approximate50km lateral extent at50m in the1993–2022 static mean core | Width of mean field, not mean instantaneous width or monthly states |
| Baumann2026 Gimsøy | Approximate50km horizontal static mean-core extent,1993–2022 | Variable-depth core, no single fixed width plane |
| Orvik and Skagseth2003 | Explicit approximate40km Svinøy annual-mean-flow description, introduction[4] | Not the computed midpoint of30–50km; averaging dates unspecified;200–900m is bathymetry |

Five historical proposed records are preserved exactly and mapped to admitted
records with stable new IDs. The sixth contextual description is separately
identified. Six records do not mean six independent new observations. All
remain ineligible for width ranking, whole-current width, physical edge/area
inference, annual extrema and seasonal animation. The seven-row historical
`proposed_widths` source collection stays traceable; two front-branch records
remain unresolved after these five migrations.

## Working data and presentation

- **102 accepted currents /27 pending proposals;13 qualified reported-length
  estimates /89 unranked.** This admits a missing named branch; it does not
  claim to close the original89 whole-length gaps. The new source extent is
  working rank6; ties are retained and Madagascar650km becomes rank13.
- **164 scoped width records /84 owners;18 current identities without a scoped
  width remain.** No width is transferred to the ambiguous parent names.
- Effective catalogue and live measurement exports preserve older editions and
  include the preceding North Atlantic conditional bound and its method-source
  record. The current working index links these exports.
- Native/WASM entity, name, identity admission, measurement, claim, source,
  width, length assessment, dashboard and route-planning records share the same
  admission. Only seven previous working rank fields and the Norwegian card's
  evidence links change; previous values, scopes, samples and dates stay exact.
- The new current is selectable but **unlocated**: no route geometry, physical
  current axis, state passage or NASA identification is inferred. Geographic
  mapped-object counts remain separate from catalogue counts.
- The scalar figure and accepted-current card expose all six definitions and
  historical extent limits. Older proposal links resolve to the accepted
  identity, retaining their original source records below the current admission.
- The seasonal view permits inspection of six non-comparable source records,
  not a seasonal sequence. Playback and all six playback-step flags are false.

## Verification boundary

Thirty focused Python tests and four subtests pass; the canonical-import check
was repeated against the rebuilt main packet. All116 Rust tests pass, including
exact admitted-row recognition and rejection of edited regional copies. The
complete native atlas check and native/WASM builds pass. Actual Chrome passes all six native/WASM comparisons:102identities, the exact
identity admission, six admitted widths,13ranked assessments, the complete
measurement admission and the unlocated object. Index/object/atlas/proposal
navigation, exact atlas source bytes, working rank6/Madagascar13, keyboard
figure access,320px reflow and exports pass. The seasonal view retains all six
non-comparable source records with zero eligible playback steps and disabled
playback; its explanation explicitly rejects a seasonal sequence. Zero
originalPDF/XML/NetCDF/ZIP requests occurred. The scalar figure was visually
inspected. The actual atlas-directory regression also passes: all102current
and140eddy/detection entries, exact99shared-gateway source-role IDs, current
selection and map zoom, keyboard access, updated-record indication, empty
search and320px reflow. A current with no geometry now says Unlocated rather
than Locator only. Source screenshots were retained in the private review
cache; no provider figures were redistributed. All **28 scientific/admission reports reconstruct byte exactly on Linux** at
source commit `e8023a1371b7a15e670a4bb578e7d83d2250aff2`, run **39731439984**,
scientific job **119667156639**. Every retained/rebuilt SHA matches the
corresponding local report. NetCDF job **119667156843** also passed. Offline job
**119667156818** stopped before tests on `rotschi-secc-1972` HTTP403. This is not
a numerical reconstruction failure or an overall green CI result.

The follow-up receipt/review commit changes documentation only: all415engine
inputs, generated artifacts, sources and28report/producer files remain
identical to Linux-tested `e8023a1`. Internal seven-role review resolves20of21
scoped findings,zeroP1; the complete-suite release gate remains open.

All165 preservation file hashes pass, covering the frozen release and all27
previous scientific reports/producers. Main packet preservation verifies exact
old rows except seven declared rank updates and the Norwegian card's evidence
links. Historical proposed widths and all previous width/sample/date records
remain exact. Main data:51collections /59,850rows /169sources /55diagnostics;
242dashboard objects and77reference paths. All432 previous source-index
descriptors remain exact; all436 current original-file hashes verify. The new
engine has415 checked dependency hashes.

The full131-browser matrix and complete default suite are separate gates and
have not been claimed passed. The local4GiB free-space guard remains unmet;
the preceding remote offline job stopped before tests on a source-download403.
This stays a working draft, with no overall green CI or scientific release claim.

## Reproduce

```powershell
python analysis/nwasc_working_admission.py
python -m pytest analysis/test_nwasc_working_admission.py analysis/test_current_identity_admissions.py analysis/test_north_atlantic_gate_bound.py analysis/test_canonical_working_assertions.py -q
python analysis/build_motion_dashboard.py
python analysis/build_almanac_index_bundle.py
python analysis/build_rust_query_bundle.py
python analysis/build_rust_query_engine.py
$env:OSW_TEST_BROWSER='C:/Program Files/Google/Chrome/Application/chrome.exe'
python analysis/test_nwasc_working_admission_browser.py
python analysis/inspect_scientific_reproduction.py
```

Next: continue the remaining current data gaps on this same PR. A source-defined
branch, a broad historical extent, local width descriptions and an actual
dated current axis remain distinct deliverables.
