"""Prospective numerical rules; synthetic inputs only before a committed freeze.

This module has no source reader or network access. Its result is a regional
filtered core section projection, never a whole-current dimension.
"""
import calendar
import math

BEARING_DEGREES_TRUE = 318.1
LAYER_M = (50.0, 100.0)
MAX_VERTICAL_GAP_M = 30.0
HOUR_TOLERANCE_SECONDS = 2.0
FILTER_PERIOD_HOURS = 36.0
FILTER_ORDER = 2
FILTER_PAD_HOURS = 108
FILTER_TRIM_HOURS = 108
MIN_FILTER_SEGMENT_HOURS = 240
MIN_MONTH_FRACTION = 0.70
MIN_MONTH_DAYS = 15
MAX_MONTH_GAP_HOURS = 168
MIN_PEAK_M_S = 0.10
THRESHOLD_FRACTIONS = (0.4, 0.5, 0.6)
PEAK_ANCHORS = ('LS4', 'LS5')


def values_and_mask(value):
    import numpy as np
    value = np.ma.asarray(value, dtype='float64')
    data = np.asarray(value.data)
    return data, ~np.ma.getmaskarray(value) & np.isfinite(data)


def align_hours(days_since_1950):
    """Round to UTC hour only within two seconds; preserve signed offsets."""
    import numpy as np
    data, valid = values_and_mask(days_since_1950)
    if data.ndim != 1 or not len(data) or not valid.all() or ((data < 0) | (data > 90000)).any():
        raise ValueError('TIME must be a complete finite reviewed-epoch vector')
    indices = np.rint(data * 24).astype('int64')
    offsets = data * 86400 - indices * 3600
    if (np.abs(offsets) > HOUR_TOLERANCE_SECONDS).any():
        raise ValueError('Timestamp exceeds the declared hourly alignment tolerance')
    if (np.diff(indices) <= 0).any():
        raise ValueError('Hourly alignment duplicates or reverses an observation')
    return indices, offsets


def rotate(east, north, bearing=BEARING_DEGREES_TRUE):
    """Positive along NW, positive transverse to its left (offshore SW)."""
    theta = math.radians(bearing)
    return (east * math.sin(theta) + north * math.cos(theta),
            -east * math.cos(theta) + north * math.sin(theta))


def layer_velocity(east, north, supplied_depth):
    """Piecewise-linear 50–100 m layer average with observed brackets."""
    import numpy as np
    u, um = values_and_mask(east)
    v, vm = values_and_mask(north)
    z, zm = values_and_mask(supplied_depth)
    if u.ndim != 2 or u.shape != v.shape or u.shape != z.shape:
        raise ValueError('Velocity and supplied depth must have equal TIME-by-bin shapes')
    along = np.full(u.shape[0], np.nan)
    cross = along.copy()
    reasons = []
    lower, upper = LAYER_M
    for index in range(len(u)):
        usable = um[index] & vm[index] & zm[index] & (z[index] >= 0)
        if usable.sum() < 3:
            reasons.append('insufficient_paired_depth_cells');continue
        order = np.argsort(z[index, usable])
        depth = z[index, usable][order]
        e, n = u[index, usable][order], v[index, usable][order]
        if (np.diff(depth) <= 0).any():
            reasons.append('duplicate_supplied_depth');continue
        if depth[0] > lower or depth[-1] < upper:
            reasons.append('layer_not_bracketed');continue
        left = int(np.searchsorted(depth, lower, side='right') - 1)
        right = int(np.searchsorted(depth, upper, side='left'))
        if (np.diff(depth[left:right + 1]) > MAX_VERTICAL_GAP_M).any():
            reasons.append('vertical_gap_exceeds_limit');continue
        inside = (depth > lower) & (depth < upper)
        nodes = np.concatenate(([lower], depth[inside], [upper]))
        ue = np.interp(nodes, depth, e)
        vn = np.interp(nodes, depth, n)
        mean_e = float(np.trapezoid(ue, nodes) / (upper - lower))
        mean_n = float(np.trapezoid(vn, nodes) / (upper - lower))
        along[index], cross[index] = rotate(mean_e, mean_n)
        reasons.append('available_layer')
    return along, cross, reasons


def filter_segments(hourly_values):
    """Second-order SOS Butterworth, forward/backward, no missing bridges."""
    import numpy as np
    from scipy.signal import butter, sosfiltfilt
    values, valid = values_and_mask(hourly_values)
    if values.ndim != 1:
        raise ValueError('Filter requires a dense one-hour vector')
    output = np.full(values.shape, np.nan)
    sos = butter(FILTER_ORDER, 1 / FILTER_PERIOD_HOURS, fs=1.0, output='sos')
    starts = np.flatnonzero(valid & ~np.r_[False, valid[:-1]])
    stops = np.flatnonzero(valid & ~np.r_[valid[1:], False]) + 1
    segments = []
    for start, stop in zip(starts, stops):
        start, stop = int(start), int(stop)
        record = {'start_hour_index': start, 'stop_hour_index_exclusive': stop,
                  'input_hours': stop - start}
        if stop - start < MIN_FILTER_SEGMENT_HOURS:
            record.update(status='short_segment', retained_hours=0)
        else:
            filtered = sosfiltfilt(sos, values[start:stop], padtype='odd', padlen=FILTER_PAD_HOURS)
            first, last = start + FILTER_TRIM_HOURS, stop - FILTER_TRIM_HOURS
            output[first:last] = filtered[FILTER_TRIM_HOURS:-FILTER_TRIM_HOURS]
            record.update(status='filtered_with_trimmed_edges', retained_hours=last - first)
        segments.append(record)
    return output, segments


def longest_false_run(available):
    import numpy as np
    missing = ~np.asarray(available, dtype=bool)
    starts = np.flatnonzero(missing & ~np.r_[False, missing[:-1]])
    stops = np.flatnonzero(missing & ~np.r_[missing[1:], False]) + 1
    return int(max(stops - starts, default=0))


def monthly_profiles(utc_hours, station_values):
    """All station means use the exact same eligible hours in each month."""
    import numpy as np
    hours = np.asarray(utc_hours, dtype='datetime64[h]')
    values, available = values_and_mask(station_values)
    if (hours.ndim != 1 or not len(hours) or np.isnat(hours).any()
            or (np.diff(hours) != np.timedelta64(1, 'h')).any()
            or values.ndim != 2 or values.shape != (len(hours), 8)):
        raise ValueError('Monthly support requires a complete hourly grid and eight ordered stations')
    result = []
    labels = hours.astype('datetime64[M]')
    for month in np.unique(labels):
        rows = labels == month
        observed = hours[rows]
        year, number = map(int, str(month).split('-'))
        denominator = calendar.monthrange(year, number)[1] * 24
        start = month.astype('datetime64[h]')
        full = bool(observed[0] == start and observed[-1] == start + np.timedelta64(denominator - 1, 'h'))
        common = available[rows].all(axis=1)
        calendar_available = np.zeros(denominator, dtype=bool)
        indices = (observed - start).astype('timedelta64[h]').astype(int)
        calendar_available[indices] = common
        days = len(np.unique(observed[common].astype('datetime64[D]')))
        count = int(common.sum())
        gap = longest_false_run(calendar_available)
        eligible = bool(full and count / denominator >= MIN_MONTH_FRACTION
                        and days >= MIN_MONTH_DAYS and gap <= MAX_MONTH_GAP_HOURS)
        means = values[rows][common].mean(axis=0).tolist() if count else [None] * 8
        result.append({'month': str(month), 'calendar_hours': denominator,
                       'represented_grid_hours': int(rows.sum()), 'full_calendar_month': full,
                       'common_available_hours': count, 'common_fraction': count / denominator,
                       'common_available_days': days, 'max_unsupported_run_hours': gap,
                       'eligible_for_core_span': eligible, 'conditional_mean_along_m_s': means,
                       'station_available_hours': available[rows].sum(axis=0).astype(int).tolist()})
    return result


def core_span(projected_cross_km, monthly_mean, station_ids, fraction=0.5):
    """A connected relative-peak span, with both brackets or explicit censoring."""
    import numpy as np
    x, xm = values_and_mask(projected_cross_km)
    v, vm = values_and_mask(monthly_mean)
    if (x.ndim != 1 or x.shape != v.shape or len(x) != len(station_ids) or len(x) < 3
            or not xm.all() or (np.diff(x) <= 0).any() or len(set(station_ids)) != len(station_ids)
            or fraction not in THRESHOLD_FRACTIONS):
        raise ValueError('Invalid transverse coordinates, identities or prospective threshold')
    result = {'status': 'unresolved', 'fraction_of_peak': fraction, 'span_km': None,
              'left_bracket': None, 'right_bracket': None, 'peak_station': None,
              'metric': 'regional_filtered_layer_core_transverse_projection',
              'full_current_width': False}
    if not vm.all():
        return {**result, 'status': 'missing_station_no_interpolation'}
    peak_value = float(v.max())
    peaks = np.flatnonzero(v == peak_value)
    if len(peaks) != 1:
        return {**result, 'status': 'ambiguous_peak'}
    peak = int(peaks[0]);result['peak_station'] = station_ids[peak]
    if peak_value < MIN_PEAK_M_S:
        return {**result, 'status': 'peak_below_diagnostic_floor'}
    if station_ids[peak] not in PEAK_ANCHORS:
        return {**result, 'status': 'peak_outside_upper_slope_anchors'}
    threshold = fraction * peak_value
    result.update(peak_m_s=peak_value, threshold_m_s=threshold)

    def edge(direction):
        high = peak
        while 0 <= high + direction < len(v):
            low = high + direction
            if v[low] == threshold:
                farther = low + direction
                if not 0 <= farther < len(v):
                    return None, None, 'exact_threshold_at_section_end'
                if v[farther] == threshold:
                    return None, None, 'threshold_plateau'
                if v[farther] > threshold:
                    return None, None, 'threshold_touch_without_exit'
                return float(x[low]), [low, low], None
            if v[low] < threshold:
                value = x[low] + (threshold - v[low]) * (x[high] - x[low]) / (v[high] - v[low])
                return float(value), sorted([low, high]), None
            high = low
        return None, None, 'edge_outside_observed_section'

    left, lb, le = edge(-1)
    right, rb, re = edge(1)
    result.update(left_bracket=lb, right_bracket=rb,
                  left_cross_km=left, right_cross_km=right,
                  left_censoring=le, right_censoring=re)
    if le or re:
        return {**result, 'status': 'censored'}
    index = lb[-1]
    while index <= rb[0]:
        end = index
        while end + 1 <= rb[0] and v[end + 1] == v[index]:
            end += 1
        if (index > 0 and end < len(v) - 1 and not index <= peak <= end
                and any(station_ids[i] not in PEAK_ANCHORS for i in range(index, end + 1))
                and v[index] > threshold and v[index] > v[index - 1] and v[end] > v[end + 1]):
            return {**result, 'status': 'merged_secondary_core'}
        index = end + 1
    return {**result, 'status': 'resolved_regional_core_span', 'span_km': right - left}
