"""Independent product matching must reject alternative station/date pairings."""
import copy
import json
import pytest
import build_pelagia_date_reconciliation as module


def fixtures():
    acquisition = json.loads((module.ROOT / (module.DIRECTORY + 'acquisition.json')).read_bytes())
    casts = module.extract_casts((module.ROOT / acquisition['file']).read_bytes())
    events = module.parse_events((module.ROOT / module.SUMMARY).read_bytes(), 2000)
    return events, casts


def test_exact_reconciliation_and_timestamp_distinctions():
    document = module.build()
    assert document == json.loads((module.ROOT / module.OUTPUT).read_bytes())
    assert len(document['records']) == 46
    assert sum(r['bottle_minus_summary_time_minutes'] != 0 for r in document['records']) == 3
    assert all(r['original_summary_date'].startswith('2005-') for r in document['records'])
    assert all(r['corrected_bottle_date'].startswith('2007-') for r in document['records'])
    assert all(r['bottle_minus_summary_coordinates_degrees'] == [0, 0] for r in document['records'])
    assert all(r['bottle_source_lines'] for r in document['records'])


@pytest.mark.parametrize('field,value,expected', [
    ('EXPOCODE', 'another-cruise', 'Cruise or section mismatch'),
    ('SECT_ID', 'another-section', 'Cruise or section mismatch'),
    ('date', '2007-09-06', 'Source month/day mismatch'),
    ('LATITUDE', '52', 'Source position mismatch'),
    ('TIME', '1040', 'Source time mismatch'),
])
def test_match_rejects_metadata_changes(field, value, expected):
    events, casts = fixtures()
    casts[('2', '1')]['record'][field] = value
    with pytest.raises(ValueError, match=expected):
        module.reconcile(events, casts)


def test_missing_or_extra_casts_fail_closed():
    events, casts = fixtures()
    casts.pop(('2', '1'))
    with pytest.raises(ValueError, match='missing archive cast'):
        module.reconcile(events, casts)
    events, casts = fixtures()
    casts[('invented', '1')] = copy.deepcopy(casts[('2', '1')])
    with pytest.raises(ValueError, match='Extra bottle casts'):
        module.reconcile(events, casts)
