# Screened atlas accessibility review record

Status: automated keyboard and semantic checks passed locally on 2026-09-30;
human visual and screen-reader review remains open. This record applies to
`site-review/ocean-motion-screened/` built from the current screened export.

## Automated evidence

Run:

```powershell
py analysis/build_ocean_motion_screened_site.py
py analysis/check_ocean_motion_screened_site.py
py analysis/test_ocean_motion_screened_site_browser.py
```

The Chromium test checks that the skip link focuses `main`, the search fields,
state selector, length table, and map have accessible roles and names, map
markers can receive focus, opening an object moves focus to its heading, and
state selection produces a short live status. It checks document-level
horizontal overflow at 390 pixels at normal and 200% CSS zoom, and at 1280
pixels with 400% CSS zoom (320 CSS-pixel effective width). Wide data tables
remain independently scrollable. CSS zoom is an automated reflow probe, not
a substitute for browser zoom and assistive-technology inspection.

## Human review to record

Use the exact built bundle and record browser, operating system, assistive
technology, reviewer, date, outcome, and issue IDs for each route:

1. Keyboard only: use the skip link; search for California Current; open its
   record; follow the source and length audit; return to the directory.
2. Keyboard only: choose an OSW state, expand source-reported, schematic,
   locator, and unresolved current groups plus the named-eddy groups; open an
   object and return with browser Back.
3. Screen reader: confirm the table captions and column headings preserve the
   association between each length, its evidence class, scope, source, and
   California/Kuroshio warning. Confirm that the six scientific-review labels
   are announced without reading the entire table on load.
4. Screen reader: confirm the map has a useful name and every marker has a
   distinct object name and explicitly approximate locator role. Confirm the
   text directory offers the same objects without using the map.
5. Visual: at 200% and 400% zoom and a narrow viewport, inspect focus
   visibility, text clipping, table scrolling, and source-warning legibility.
   Check contrast and color-independent meaning for the map markers and
   warning blocks.

Record any failure in this file or an issue linked from it, fix the bundle,
rebuild, and repeat the affected route. Automated checks do not constitute a
human screen-reader signoff or publication approval.
