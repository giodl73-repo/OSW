"""Source custody, event distinctions, date conflicts and geographic scope."""
import json
from pathlib import Path
import pytest
import build_atlantic_station_context as module


def test_checked_extraction_is_reproducible():
    actual = module.build()
    assert actual == json.loads((module.ROOT / module.OUTPUT).read_bytes())
    assert len(actual['cruises']) == 18
    assert sum(c['source_event_count'] for c in actual['cruises']) == 4772
    assert len(actual['measurement_contexts']) == 30
    assert sum(bool(c['points']) for c in actual['measurement_contexts']) == 30
    for context in actual['measurement_contexts']:
        assert context['geometry_role'] == 'cruise_sampling_context_not_current_boundary'
        assert context['boundary_station_mapping_status'] == 'unresolved'
        assert context['current_footprint_eligible'] is False
        assert context['state_intersection_eligible'] is False
        assert context['annual_series_eligible'] is False
        assert context['coordinate_datum'] is None
        assert context['coordinate_uncertainty_degrees'] is None
        assert context['point_count'] == len(context['points'])
        for point in context['points']:
            assert context['sampling_window']['start'] <= point['sampling_date'] <= context['sampling_window']['end']
            assert point['instrument'] in ('ROS', 'CTD')


def test_original_date_conflict_is_preserved_and_independently_reconciled():
    actual = module.build()
    cruise = next(c for c in actual['cruises'] if c['paper_cruise_id'] == '64PE20070830')
    assert len(cruise['source_date_conflict_lines']) == 46
    assert all(e['decoded_date'].startswith('2005-') for e in cruise['events'])
    contexts = [c for c in actual['measurement_contexts'] if c['paper_cruise_id'] == cruise['paper_cruise_id']]
    assert len(contexts) == 3
    assert all(c['points'] and c['date_reconciliation_file'] for c in contexts)
    for context in contexts:
        for point in context['points']:
            assert point['decoded_date'].startswith('2005-')
            assert point['sampling_date'].startswith('2007-')
            assert point['date_reconciliation_pointer'].startswith('/records/')


def test_archive_aliases_and_blank_sections_are_retained():
    cruises = {c['paper_cruise_id']: c for c in module.build()['cruises']}
    assert cruises['06M220130509']['archive_cruise_labels'] == ['06MM20130509']
    assert any(e['archive_section_label'] is None for e in cruises['18HU20050526']['events'])
    assert any(e['instrument'] == 'XBT' for e in cruises['74DI19921222']['events'])
    assert any(e['source_minutes_equal_sixty'] for e in cruises['740H20180228']['events'])


def test_source_line_errors_fail_closed():
    source = b'header\n------\nthis is not a station row\n'
    with pytest.raises(ValueError, match='Unparsed source line 3'):
        module.parse_events(source, 2000)


def test_invalid_minutes_rejected_and_sixty_carried():
    template = 'header\n------\nTEST A01 1 1 ROS 010101 0000 BO 23 {minutes} S 1 00.00 W GPS\n'
    with pytest.raises(ValueError, match='Invalid source coordinate'):
        module.parse_events(template.format(minutes='60.01').encode(), 2000)
    row = module.parse_events(template.format(minutes='60.00').encode(), 2000)[0]
    assert row['coordinates'] == [-1.0, -24.0]
    assert row['raw_latitude'] == '23 60.00 S'
    assert row['source_minutes_equal_sixty']


def test_event_choice_retains_cast_identity_and_prefers_bottom():
    raw = ('header\n------\n'
           'TEST A01 1 1 ROS 010101 0000 BE 23 00.00 S 1 00.00 W GPS\n'
           'TEST A01 1 1 ROS 010101 0010 BO 23 00.01 S 1 00.01 W GPS\n'
           'TEST A01 1 2 CTD 010101 0100 BE 23 00.02 S 1 00.02 W GPS\n'
           'TEST A01 1 1 XBT 010101 0110 DE 23 00.03 S 1 00.03 W GPS\n')
    events = module.parse_events(raw.encode(), 2000)
    points = module.context_points(events, {'start': '2001-01-01', 'end': '2001-01-01'})
    assert [(p['cast_label'], p['event_code']) for p in points] == [('1', 'BO'), ('2', 'BE')]
    assert len(events) == 4
