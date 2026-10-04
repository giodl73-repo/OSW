# NOAA MUNSTER eddy detections: reuse decision packet

Status: open for the v0.1.0 candidate; no provider inquiry sent.

## Exact material

The candidate uses 12 dated NOAA CoastWatch [MUNSTER v1.0 daily
eddy-identification NetCDF files](https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html)
from March 2021 through December 2023. The generated
[`source-review-queue.csv`](../almanac/release/v0.1.0/source-review-queue.csv)
lists each exact file URL, date, source digest, and exported row count.
Together they support 92,891 detection rows in `v0.1.0/observations/`.
Those rows carry provider eddy-center coordinates, radius, area, amplitude,
polarity, and source ordinal. OSW adds stable local IDs and approximate
contained/intersected state codes. The source NetCDF files and full eddy
contours are not copied, but these extracted provider values are a material
dataset redistribution.

## Existing source guidance

NOAA labels MUNSTER experimental. Its product page's **Data license** section
lists credits to NOAA, the Copernicus Program for Sentinel data, and AVISO+
Products. It does not explicitly identify a reuse license for a third party
to republish nearly 93,000 extracted records as downloadable CSV, nor does it
identify which AVISO+ input terms attach to the released MUNSTER output.
The candidate retains the stated credit and leaves source rights pending.
NOAA's [CoastWatch help desk](https://coastwatch.noaa.gov/cwn/about/contact-us.html)
is the documented product-question route.

## Decision required before publication

Obtain an authoritative answer covering:

1. Public website and versioned dataset-archive redistribution of the 92,891
   extracted daily eddy records and derived OSW state joins, with no original
   NetCDF files or full contours.
2. Required license label, data citation, NOAA/CoastWatch, Copernicus/Sentinel,
   AVISO+, and any other upstream acknowledgments for that reuse.
3. Whether source version 1.0 and experimental status must be carried on every
   exported row or whether collection-level metadata and notices suffice.
4. Whether later dates, contours, or track records require a different review.

If the answer does not cover public redistribution of the detection values,
retain the full receipt internally and make a separately manifested public
release with only source links and aggregate OSW factual summaries whose use
has been reviewed. Do not leave the row files accessible while marking the
source as merely linked. Record the answer, its provenance and date, and the
exact reviewed scope in `research/ocean-motion-source-use-reviews.json` before
changing the release status.
