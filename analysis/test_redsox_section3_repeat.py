"""Same operator, matched geography and no invented seasonal width range."""
import copy
from pathlib import Path
import pytest
import build_redsox_section3_repeat as study


@pytest.fixture(scope='module')
def report():
    return study.build()


def test_exact_rebuild_and_complete_case_inventory(report):
    assert study.encoded(report)==(study.ROOT/study.REPORT).read_bytes()
    cases=[case for layer in report['summer_layers'] for case in layer['cases']]
    assert len(cases)==30
    assert sum(c['span_km'] is not None for c in cases)==4
    assert all(c['span_km'] is None for c in cases if c['branch']=='southern')
    assert not report['new_width_record_admitted']
    assert report['annual_width_range_km'] is None
    assert report['whole_current_width_km'] is None
    assert report['seasonal_climatology'] is False


def test_original_station_correspondence_and_quality(report):
    assert len(report['station_correspondence'])==12
    assert all(p['within_two_km'] and p['separation_km']<.3 for p in report['station_correspondence'])
    for pair in report['station_correspondence']:
        separation=study.GEOD.inv(*pair['winter_position_lon_lat'],*pair['summer_position_lon_lat'])[2]/1000
        assert separation==pytest.approx(pair['separation_km'],abs=1e-6)
    bad=next(p for p in report['summer_layers'][0]['profiles'] if p['station']==22)
    assert bad['usable'] is False
    assert bad['source_processing_tag']=='downf'
    assert bad['source_component_quality_notes']
    assert 'authored_component_quality_treatment_unverified' in bad['exclusion_reasons']


def test_weak_northern_candidate_does_not_pass_saline_or_error_screen(report):
    primary=report['summer_layers'][0]['cases'][5:]
    assert primary[0]['span_km']==pytest.approx(3.100424,abs=1e-6)
    assert primary[0]['peak_station']==28
    assert primary[0]['saline_outflow_screen'] is False
    assert primary[0]['peak_salinity_psu']==pytest.approx(37.410598,abs=1e-6)
    assert primary[3]['span_km'] is None
    assert primary[3]['status']=='peak_below_component_floor'
    assert all(c['span_km'] is None for c in report['summer_layers'][1]['cases'])


def test_six_comparisons_never_join_different_branches(report):
    assert len(report['comparisons'])==6
    assert not any(c['comparison_supported'] for c in report['comparisons'])
    assert all(c['summer_minus_winter_dated_component_span_km'] is None for c in report['comparisons'])
    primary=report['comparisons'][:2]
    assert primary[0]['branch']=='southern'
    assert primary[0]['winter_span_km']==pytest.approx(4.971207,abs=1e-6)
    assert primary[0]['summer_span_km'] is None
    assert primary[1]['branch']=='northern'
    assert primary[1]['winter_span_km'] is None
    assert primary[1]['summer_span_km']==pytest.approx(3.100424,abs=1e-6)


def renumber(value,mapping,key=''):
    if isinstance(value,dict):return {k:renumber(v,mapping,k) for k,v in value.items()}
    if isinstance(value,list):return [renumber(v,mapping,key) for v in value]
    station_fields={'peak_station','inner_station','outer_station','peak_search_stations',
        'support_stations','unavailable_peak_stations','blocking_stations'}
    return mapping[value] if key in station_fields and value is not None else value


def test_operator_is_identical_to_frozen_winter_after_station_renaming():
    old=study.winter.build()
    mapping=dict(zip(study.winter.STATIONS,study.STATIONS));inverse={b:a for a,b in mapping.items()}
    for layer in old['layers']:
        renamed=copy.deepcopy(layer['profiles'])
        for p in renamed:p['station']=mapping[p['station']]
        for branch in study.BRANCHES:
            for fraction,offset in [(.5,0),(.4,0),(.6,0),(.5,-.03),(.5,.03)]:
                result=study.measure(renamed,branch,fraction,offset)
                assert renumber(result,inverse)==study.winter.measure(layer['profiles'],branch,fraction,offset)


def test_comparison_requires_both_screens_even_with_two_finite_spans(report):
    old=study.winter.build()['layers'];new=copy.deepcopy(report['summer_layers'])
    # Synthetic supported summer southern values cannot bypass an explicit
    # failed saline screen or a geographic mismatch.
    target=new[0]['cases'][0]
    target.update(span_km=3.,saline_outflow_screen=False,status='paired_span_with_unverified_saline_association')
    result=study.comparisons(old,new,True)[0]
    assert result['comparison_supported'] is False
    assert result['summer_minus_winter_dated_component_span_km'] is None
    assert 'summer_saline_screen_not_passed' in result['unresolved_reasons']
    target['saline_outflow_screen']=True
    target['status']='paired_local_component_span'
    supported=study.comparisons(old,new,True)[0]
    assert supported['comparison_supported'] is True
    assert supported['summer_minus_winter_dated_component_span_km']==pytest.approx(3.-4.971207,abs=1e-6)
    result=study.comparisons(old,new,False)[0]
    assert result['comparison_supported'] is False
    assert 'station_correspondence_exceeds_declared_limit' in result['unresolved_reasons']


def test_inputs_and_frozen_winter_report_are_exact(report):
    assert study.digest(study.winter.REPORT)==report['winter_report_sha256']
    for path,pin in report['input_sha256'].items():assert study.digest(path)==pin


@pytest.mark.parametrize('file',[study.REPORT,'figures/redsox-section3-repeat-surveys.svg'])
def test_changed_repeat_evidence_invalidates_registry(file,monkeypatch):
    import current_research_evidence as registry
    original=Path.read_bytes;target=study.ROOT/file
    def altered(path):
        data=original(path)
        return data+b' ' if path==target else data
    monkeypatch.setattr(Path,'read_bytes',altered)
    with pytest.raises(ValueError):registry.verify()
