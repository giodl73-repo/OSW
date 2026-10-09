# M6 local velocity aggregation, version 1

Source: Darelius, Janout, Fer and Sallée (2024), PANGAEA
[964717](https://doi.pangaea.de/10.1594/PANGAEA.964717), CC BY 4.0.

Select the released nominal 228 m ADCP depth bin at M6, east of Filchner
Trough. Retain geographic eastward U and northward V in cm/s. Negative U
means westward. This station describes local Antarctic Slope Current
variability; it provides no current boundary, width, length or occupied area.

1. Verify the complete released TSV against its acquisition SHA256. Reject
   duplicate selected timestamps, nonfinite values, changed station positions
   and timestamps outside the documented hourly grid.
2. Average available paired U/V readings separately within each calendar
   month. No missing-hour interpolation, zero filling, axis rotation, low-pass
   filtering or additional quality filtering. These are OSW aggregations,
   not a reproduction of the article's processing.
3. Expected hourly slots are the intersection of a calendar month with the
   catalog interval, 2017-02-24T17:00 through 2021-02-13T10:00 inclusive.
   Report available pairs, expected slots and coverage. First and last months
   are partial; sparse sampling can bias every mean.
4. Seasonal composites give equal weight to each complete calendar-month
   mean. Exclude February 2017 and February 2021. February therefore has
   three contributing years and the other months four. Report their year
   lists, sample counts and min/max of the contributing monthly means.
   Those spans describe interannual variation, not confidence intervals,
   within-month extrema or measurement uncertainty.
5. Timestamp timezone is unspecified in the released TSV. Preserve source
   timestamp strings without adding UTC. Depth is nominal: released ADCP
   bins (52:8:316 m) differ from article Table 1 (26:8:298 m). Do not correct
   that disagreement or assign pressure/drawing differences as uncertainty.
6. Measurement uncertainty remains null. Charts use signed cm/s, fixed axes
   across filtering and pagination, discrete points, and explicit source
   coverage. Any playback highlights observed samples without interpolation
   or changing geographic current geometry.

The complete licensed source is retained unchanged inside deterministic gzip.
OSW's derived JSON and charts must remain reconstructable offline.
