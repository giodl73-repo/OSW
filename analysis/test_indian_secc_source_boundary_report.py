"""Complete actual-data preservation check beyond the small censoring kernels."""
import json

from indian_secc_source_boundary_audit import ROOT, REPORT, SOURCE, encoded


def test_complete_report_and_every_available_profile_direction_preserved():
    raw = (ROOT / REPORT).read_bytes()
    assert raw == encoded()
    report = json.loads(raw)
    source = json.loads((ROOT / SOURCE).read_bytes())
    assert len(report['attempt_inventory']) == len(source['cases']) == 144
    assert len(report['terminal_rows']) == 2 * sum(len(c['stations']) for c in source['cases'])
    lookup = {(r['case_id'], r['station_arc_parameter_km'], r['direction']): r for r in report['terminal_rows']}
    assert len(lookup) == len(report['terminal_rows'])
    for c, inventory in zip(source['cases'], report['attempt_inventory']):
        assert inventory == {'case_id': c['id'], 'month': c['month'],
                             'status': c['status'], 'available_stations': len(c['stations'])}
        for station in c['stations']:
            for name, index in [('negative_normal', 0), ('positive_normal', -1)]:
                row = lookup[c['id'], station['station_arc_parameter_km'], name]
                assert row['terminal_sample'] == (station['samples'][index] if station['samples'] else None)
                assert [t['direction_edge'] for t in row['thresholds']] == [t['edges'].get(name) for t in station['threshold_cases']]
    assert not any(report[k] for k in ['physical_width_admitted', 'physical_axis_admitted',
                                     'physical_length_admitted', 'annual_width_range_admitted'])
