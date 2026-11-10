# S1 moored current profiles: original case

Investigate the public Italian Arctic Data Center S1 mooring, upward-looking
ADCP dataset 8e2f4c44-d784-40ed-94aa-ef5fa505761a. The provider's tabledap
index explicitly links this dataset. Its metadata is the first original cloud
request, using the documented ERDDAP info JSON API. Web lookup of the data form
returned a cache miss; no original info response or native values are held.

One shared acquisition/analysis case covers this mooring investigation, not
separate budgets per upward/downward instrument, file, month, threshold, current,
or phase. Caps: 8 provider operations, 1.6MB cumulative original response bytes,
250000 scalar upper bound, 60 cumulative active seconds, 3–150 selected profiles,
40 selected native levels per profile, 20000 decoded cells, 6000 measurement
nodes, 5km spatial tolerance, 2.4MB whole output. Redirects and retries disabled.
Reserve each target durably before requesting, retain raw before parsing, enforce
absolute deadline and SIGTERM, use fresh output directories. Failures close the
case and surrender unused operations. Never renew budgets or replay targets.

Run sequentially on one idle cloud CPU. First inspect exact provider metadata:
position, actual date interval, measured versus nominal depth, bin coordinates,
velocity reference frame, processing, quality flags, units and license. Instrument
deployment depth (420m in title) is not a current boundary. No native query is
authorized by a CF variable label alone, no pressure-to-depth equivalence, no
invented magnetic correction, and no current identity inferred just from a broad
Fram Strait location. Native selection and any depth proxy require an additional
explicit operator carrying this original ledger, after reviewing metadata.

The nearest relevant catalog current may be West Spitsbergen, but that owner must
be qualified using independent regional circulation evidence and the actual site.
Reverse/tidal flow, missing bins, surface sidelobes, instrument motion and lower
sampling censoring must stay explicit. No whole-route depth or volume claim.
