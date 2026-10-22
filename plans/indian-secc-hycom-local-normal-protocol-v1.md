# Indian SECC HYCOM local-normal diagnostic v1

Declared before calculating any velocity-derived HYCOM peaks or spans.
This follows the unsuccessful OSCAR candidate-axis test. It is exploratory,
not a blinded reproduction or an isolated experiment on grid resolution.

Use all twelve source-preflight monthly paired daily-00Z HYCOM vector means
at the exact provider 15m level. Inadequately sampled cells stay missing.
Keep each monthly OSCAR seed's original longitude and selected latitude from
`research/indian-secc-positive-band-connectivity.json`; do not choose new
seeds by inspecting the new field. A missing original seed remains missing.
The existing case operator snaps the seed to the nearest native latitude,
then tests native offsets -1/0/+1. Their physical distances differ between
products and must not be described as identical seed perturbations.

Reuse the unchanged `analysis/indian_secc_local_normals.py` case, profile,
peak, geodesic normal, threshold, four-corner support and adaptive RK4 logic.
Retain all 144 attempts: twelve months, two historical meridians, three
native offsets and both 5/10km profile sampling steps. Record every failure,
all normal samples, 40/50/60% threshold crossings and interpolation residuals.
The 0.02m/s seed/peak guard, unique peak tolerance 1e-10m/s, +/-40km refinement,
1% endpoint contrast, <=10km peak displacement and <=15 degree direction
checks remain unchanged. Primary seeds test five stations from -100 to +100km
at 50km arc-parameter increments. Offset seeds only test central sections.

Keep the existing source-resolution screen of at least four native cell
spacings for every paired diagnostic span. Report axis checks separately
from paired-edge, resolution and equator screens. A stronger candidate must
pass all five station axis checks at BOTH sampling steps, have paired nominal
half-peak edges at all stations, retain >=4 native spacings at all stations,
and have no edge at or north of the equator. An eligible candidate still has
unverified named-current association and admits no catalog width or length.

Step, source product, seed, depth definition and threshold differences are
method sensitivities, not measurement errors or physical seasonal ranges.
Retain all months including zero eligible cases. No annual extrema, coast or
state joins, NASA feature identities or seasonal route playback are admitted.
Source, source preparation and diagnostic results remain distinct artifacts.
