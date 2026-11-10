# Direct NOAA source with retained metadata and an aggregate request ledger

Preserve v1 and its successful13cloud checks. Source41974149297 retained
validated PMEL metadata but its catalogue request returned302 and was not
followed. Journal proves two metadata attempts, zero field attempts and producer
finalization before upload. Do not request either old target again.

The independently reviewed NOAA ERD primary catalogue at
https://coastwatch.pfeg.noaa.gov/erddap/info/pmelTaoDyAdcp/index.html
identifies the same dataset, provider, eastwardcm/s variable, quality flags,
metre positive-down depth, nominal coordinates and daily00UTC/noonlabel
semantics. Reuse the retained PMEL metadata bytes; no claim that the two
servers' full metadata bytes are identical. The ERD catalogue and tabledap
documentation publish the direct source service. No automatic redirect,
fallback, failed-target replay or metadata re-download is permitted.

Preserve all sixteen original nominal-location/three-day patches,2005dates,
near10m original-row selection, quality1/2,50-250m core search and frozen
0.1primary/0.05/0.2threshold/15m gap rules. Instead of a separate station
catalogue, constrain the field request by the exact predeclared nominal latitude
and longitude. Read the returned station/array identifiers, require one unique
identifier pair across the patch and validate every returned coordinate. Never
guess a station ID or select it by velocity. An empty patch remains empty.

This is a scoped remaining-fields consumer, not a fresh source programme:
import both historical attempts into the new durable journal unchanged.
Two historical attempts plus sixteen new field requests exhaust, but never
increase, the original18attempt cap. Field scalar reserve remains11520;
metadata reserve1000; prior fieldscalars0. Totalbodybytes carry forward14059
and stay under1.2MB. Conservatively charge50seconds for the two earlier25s
request allowances, leaving160seconds of the original210s programme budget.
No reset by site/month/run. Other original caps and pre-request/fsync/raw-before-
parse/deadline/termination rules remain unchanged. Stop rather than relax caps.

Run only in cloud, sequential one idle CPU. Preserve every raw success and
failed/unfinished target. Exact retained output reconstruction and typed
reference admission remain later scientific work. Do not claim physical
current bottom/thickness, independent membership, complete within-day sample
coverage, seasonal means, annual ranges, volume or runtime integration.
