import datetime as dt
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("detect_oisst_marine_heatwave.py")
SPEC = importlib.util.spec_from_file_location("detect_oisst_marine_heatwave", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def event_rows(flags):
    start = dt.date(2026, 7, 1)
    return [[(start + dt.timedelta(days=index)).isoformat(), 2000 if flag else 1000] for index, flag in enumerate(flags)]


def flat_climatology():
    return [10.0] * 366, [15.0] * 366


def test_type_7_percentile_interpolates():
    assert MODULE.percentile([0, 10], 90) == 9


def test_canonical_day_preserves_february_29_slot():
    assert MODULE.canonical_doy(dt.date(2024, 3, 1)) == 61
    assert MODULE.canonical_doy(dt.date(2025, 3, 1)) == 61


def test_four_day_spike_is_not_an_event():
    mean, threshold = flat_climatology()
    _, events = MODULE.detect(event_rows([False, True, True, True, True, False]), mean, threshold)
    assert events == []


def test_five_day_run_is_detected():
    mean, threshold = flat_climatology()
    _, events = MODULE.detect(event_rows([False, True, True, True, True, True, False]), mean, threshold)
    assert len(events) == 1
    assert events[0]["duration_days"] == 5
    assert events[0]["maximum_intensity_above_threshold_c"] == 5


def test_two_day_gap_joins_qualified_events_but_three_day_gap_does_not():
    mean, threshold = flat_climatology()
    _, joined = MODULE.detect(event_rows([True] * 5 + [False] * 2 + [True] * 5), mean, threshold)
    _, separate = MODULE.detect(event_rows([True] * 5 + [False] * 3 + [True] * 5), mean, threshold)
    assert [event["duration_days"] for event in joined] == [12]
    assert [event["duration_days"] for event in separate] == [5, 5]


def test_build_climatology_is_complete_and_smoothed():
    rows = []
    for year in range(1991, 2021):
        date = dt.date(year, 1, 1)
        while date.year == year:
            rows.append([date.isoformat(), 1000 + MODULE.canonical_doy(date)])
            date += dt.timedelta(days=1)
    mean, threshold = MODULE.build_climatology(rows)
    assert len(mean) == len(threshold) == 366
    assert all(value > 0 for value in threshold)
