# Pelagia 2007 station date reconciliation v1

The integrated CCHDO bottle archive BOTTLE,20240919CCHHYDRO explicitly credits
corrected dates to Robert Key. Its 46 station/cast identities are independently
matched against the archived summary, which still prints dates in 2005.
The CCHDO cruise history records the corrected-date submission on 2018-09-12.
This is a source reconciliation, not a blanket year substitution.

Pin both products' byte counts and SHA-256. Parse every bottle row and retain
its source line address. All bottles for a station/cast must agree on cruise,
section, date, time, latitude and longitude. Reject invalid dates/positions,
duplicate summary cast identities, missing/extra cast matches, differing
cruise/section identities, differing month/day, and coordinates outside the
combined source rounding allowance (0.01 minute and 0.0001 degree: at most
0.00013334 degree per axis). Dates must fall inside the independently reported
2007-08-30 to 2007-09-27 voyage interval.

Preserve both timestamps. Three times differ by one minute between products;
record that difference explicitly and reject larger differences. The current
bottle product supplies the reconciled sampling date and time. The source
summary supplies station-event positions and raw event metadata; matching
positions corroborate the pairing, without establishing a geodetic datum,
coordinate accuracy, a current footprint, or the paper's model station index.

In the station-context audit preserve all original summary events, decoded
2005 dates and raw times. Only derived display points receive separate
sampling_date/sampling_time_utc fields and a pointer to the reconciliation row.
Select these points by the paper's original 2007 section sampling window.
Expose the reconciliation file and timestamp distinction beside the map and
in the exact-source query. Original source conflict remains recorded as
resolved by the newer corrected product, not erased.
