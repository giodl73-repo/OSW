"""Independent analytic geometry, barrier and observed-section checks."""
import copy
import json
import pytest
from unittest.mock import patch
import build_redsox_section3_spans as study


@pytest.fixture(scope='module')
def report():
    return study.build()


def test_source_rebuild_and_all_thirty_outcomes(report):
    assert study.encoded(report) == (study.ROOT/study.REPORT).read_bytes()
    assert sum(len(layer['cases']) for layer in report['layers']) == 30
    assert sum(c['span_km'] is not None for layer in report['layers'] for c in layer['cases']) == 10
    assert report['whole_current_width_km'] is None
    assert report['annual_width_range_km'] is None
    assert report['new_width_record_admitted'] is False


def test_geometry_and_normal_sign():
    # Equatorial eastward transect: right normal is south, not north.
    chain, bearings = study.geometry([[0,0],[1,0],[2,0]])
    assert chain == pytest.approx([0,111.31949079327357,222.63898158654714], abs=1e-9)
    assert bearings == pytest.approx([90,90,90])
    assert study.component(.4,-.6,90) == pytest.approx(.6)
    assert study.component(.4,-.6,0) == pytest.approx(.4)


def test_observed_primary_and_original_missingness(report):
    layer = report['layers'][0]
    southern, northern = layer['cases'][0], layer['cases'][5]
    assert southern['span_km'] == pytest.approx(4.971207, abs=1e-6)
    assert southern['peak_station'] == 73
    assert southern['saline_outflow_screen'] is True
    assert southern['fewer_than_four_native_spacings'] is True
    assert northern['span_km'] is None
    assert northern['unavailable_peak_stations'] == [61,63]
    p = next(p for p in layer['profiles'] if p['station']==74)
    assert p['usable'] is True
    assert p['hydrography'] is None
    assert p['hydrography_failure'] == 'no_distributed_same_filename_station_ctd'
    assert all(c['span_km'] is None for c in report['layers'][1]['cases'])


def test_independent_edge_readback(report):
    for layer in report['layers']:
        by = {p['station']:p for p in layer['profiles']}
        for case in layer['cases']:
            if case['span_km'] is None:
                continue
            for key in ['left_edge','right_edge']:
                edge = case[key]
                a,b = by[edge['inner_station']],by[edge['outer_station']]
                fraction = edge['fraction_from_inner']
                qi = a['normal_component_m_s']+case['uniform_component_offset_m_s']
                qo = b['normal_component_m_s']+case['uniform_component_offset_m_s']
                assert qi+(qo-qi)*fraction == pytest.approx(case['threshold_m_s'],abs=2e-8)
                assert 0 <= fraction <= 1
                distance = study.GEOD.inv(*a['position_lon_lat'], *edge['position_lon_lat'])[2]/1000
                assert distance == pytest.approx(fraction*edge['bracket_spacing_km'],abs=3e-6)
            assert case['span_km'] == pytest.approx(case['right_edge']['chainage_km']-case['left_edge']['chainage_km'],abs=2e-6)


def test_missing_peak_and_flank_are_barriers(report):
    profiles = copy.deepcopy(report['layers'][0]['profiles'])
    next(p for p in profiles if p['station']==74)['usable'] = False
    blocked = study.measure(profiles,'southern',.5,0)
    assert blocked['status'] == 'incomplete_branch_peak_search'
    assert blocked['span_km'] is None
    # Missing peak CTD cannot become a passing saline outflow screen.
    profiles = copy.deepcopy(report['layers'][0]['profiles'])
    next(p for p in profiles if p['station']==73)['hydrography'] = None
    result = study.measure(profiles,'southern',.5,0)
    assert result['saline_outflow_screen'] is None
    assert result['status'] == 'paired_span_with_unverified_saline_association'


def test_inputs_keep_exact_original_positions(report):
    source=json.loads((study.ROOT/'research/redsox-ladcp-source-inventory.json').read_bytes())
    positions={p['station']:p['position_lon_lat'] for p in source['profiles'] if p['campaign']=='RSX1'}
    for layer in report['layers']:
        for p in layer['profiles']:
            assert p['position_lon_lat'] == positions[p['station']]
    for path,pin in report['input_sha256'].items():
        assert study.digest(path)==pin


@pytest.mark.parametrize('file',[study.REPORT,'figures/redsox-winter-section3-component-spans.svg'])
def test_changed_new_evidence_invalidates_registry(file):
    import current_research_evidence as registry
    original = study.Path.read_bytes
    target = study.ROOT/file
    def altered(path):
        data = original(path)
        return data+b' ' if path==target else data
    with patch.object(study.Path,'read_bytes',altered), pytest.raises(ValueError):
        registry.verify()
