# Southern-current original-source review

Prepared source evidence for the same rolling PR83; no product registration,
new width record, coverage increase or merge claim.

## Recovered primary originals

-Stramma1992:10-page original from GEOMAR,916,643 bytes,
 SHA256`96b8af6dc2b3f3084fd65245a20564068b557bf200b50c48f53bd38b13761013`.
 The conclusion on printed p430 was visually reviewed. It explicitly identifies
 denser station sampling as necessary to investigate current width and seasonal
 variability. Full visual review of every original page is not claimed.
-Duran et al.2020:20-page published article from a coauthor,13,727,485 bytes,
 SHA256`e110e867b50df35706d4786ea493d25b82cd03733c683725324db856bfeb401e`.
 Original p17 was visually reviewed; AppendixB defines fixed transport control
 volumes around bathymetric contours. These are not diagnosed current edges.

Original PDFs, images and discovery OCR remain ignored. Source URLs, checksums,
page counts, citation and access/review limits are retained in the acquisition
receipts and `research/southern-current-width-source-limitations-audit.json`.

## Why the dimensions stay unknown

The100 km front value in Stramma/Lutjeharms1997 is associated with the western
Agulhas Front; it cannot fill the eastern South Indian Current width gap.
That1997 check used remote PDF parsed text only; no raw original or original-page
image review is claimed for that separate article.

Duran's latitude offsets around the700m isobath locate analysis boxes for
transport budgets. The isobath is neither a sampling-depth slab nor a physical
velocity boundary. No kilometre current width is calculated from those offsets.
Its CARS annual mean and climatologically forced MOM01 simulation do not
validate the separate2012HYCOM 100m current association or annual extrema.

## Reproduction and pending integration

```powershell
python analysis/check_southern_current_width_source_limits.py --acquire
python analysis/check_southern_current_width_source_limits.py
```

The optional acquisition flag reuses the existing strict source hydrator for
these two names; it does not extend the default42-paper gate or relax pins.
The checker verifies original bytes, acquisition receipts and complete page
counts. It cannot prove the scientific interpretation of a scanned page.

This prepared audit still needs role review and integration into the existing
current-card/source views. Missingness reasons should become queryable evidence
without turning them into numeric measurements or replacing the independent
surface-component diagnostics. Current product coverage remains149 records /
79 names; no whole-current or annual width measurement was added.
