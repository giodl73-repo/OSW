# Contributing

OSW welcomes corrections, source improvements, map concepts, and
reproducible data layers.

Every contribution should preserve these boundaries:

- distinguish temperature, heat content, anomaly, and transport;
- declare depth, time interval, spatial support, and reference state;
- identify each artifact as conceptual, observational, modeled, or quantitative;
- cite the source supporting each scientific claim;
- state what the cited evidence cannot establish;
- keep surface products separate from full-depth inference;
- allow negative, regional, non-transfer, and observationally unresolved results.

Run the complete local checks before proposing a change:

```powershell
cd analysis
python -m unittest discover -p "test_*.py"
Get-ChildItem -Filter "*.py" | ForEach-Object { python -m py_compile $_.FullName }
node --check ..\atlas\app.js
```

Atlas releases are reviewed through the functional lenses in [`.roles/`](.roles/ROLE.md).
The synthesized review belongs under `signals/roles/check/` and records its
source commit, selected roles, severities, and verdict. These internal lenses
organize quality control; they do not replace external scientific peer review.

SVG figures must contain a `<title>` and `<desc>` accessibility element and
must remain legible at their declared view-box size.
