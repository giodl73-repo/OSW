"""Original crossing support, averaging definitions and frozen source guards."""
import copy
import json
import shutil
import pytest
import check_gulf_stream_published_widths as source


def test_three_complete_occupations_and_author_mean():
    row=source.records()[0];source.validate_row(row)
    context=row['original_regional_context'];occupations=context['complete_crossing_occupations']
    assert [o['crossing_number'] for o in occupations]==[1,3,4]
    assert [o['width_km'] for o in occupations]==[145,140,120]
    assert [o['transport_sv'] for o in occupations]==[58,67,64]
    assert [o['observed_period'] for o in occupations]==[
        {'start':'1967-06-30','end':'1967-07-05'},
        {'start':'1967-07-11','end':'1967-07-15'},
        {'start':'1967-07-16','end':'1967-07-18'}]
    values=[o['width_km'] for o in occupations]
    assert sum(values)/len(values)==row['approximate_width_km']==135
    assert [min(values),max(values)]==row['width_range_km']==[120,145]
    assert not context['mean_is_independent_occupation'] and context['partial_crossing_without_width']==2
    assert all(o['source_clock_timezone'] is None and not o['is_synoptic_snapshot'] for o in occupations)


def test_author_zero_extrapolation_and_orientation_remain_visible():
    row=source.records()[0];c=row['original_regional_context']
    assert c['author_boundary_extrapolation_present'] and not c['inshore_negative_transport_observed']
    assert c['offshore_negative_transport_observed_complete_crossing_count']==2
    assert not c['all_paired_edges_observed_sign_reversals']
    assert c['baseline_bearing_degrees_true']==135 and not c['baseline_bearing_is_width']
    assert not c['width_is_exact_flow_normal_projection']
    assert row['fixed_layer_bounds_m'] is None and row['section_geometry'] is None


def test_climatology_pressure_contours_do_not_supply_fixed_depth_or_local_dates():
    row=source.records()[1];source.validate_row(row);c=row['original_regional_context']
    assert row['approximate_width_km']==300 and row['width_range_km'] is None
    assert c['pressure_contours_dbar']==[100,400] and not c['pressure_contours_are_fixed_depth_bounds']
    assert c['archive_available_as_of']=='1990-04' and c['basin_archive_years_context']==[1904,1990]
    assert not c['basin_archive_years_are_exact_local_period'] and row['observed_period'] is None
    assert c['source_meander_envelope_context_km']==500 and c['source_local_smoothing_context_km']==100
    assert not c['meander_envelope_is_current_width_or_uncertainty']
    assert not c['factor_two_comparison_defines_instantaneous_measurement']
    assert row['calendar_months'] is None and row['fixed_layer_bounds_m'] is None


@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',300),('width_range_km',[135,300]),('uncertainty_km',25),
    ('fixed_layer_bounds_m',[0,3000]),('current_id','gulf-stream-system'),
    ('current_id','florida'),('calendar_months',[7]),('seasonal_playback_eligible',True),
    ('annual_width_range_km',[120,145]),('whole_current_representative',True),
    ('width_rank_eligible',True),('observed_period',{'start':'1967-07-18','end':'1967-07-18'}),
])
def test_source_bound_width_cannot_change_scope_or_become_annual_range(key,value):
    row=source.records()[0];row[key]=value
    with pytest.raises(ValueError):source.validate_row(row)


def test_missing_duplicate_reassigned_or_erased_context_records_are_rejected():
    inventory=json.loads((source.ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    source.validate_inventory(inventory)
    for mode in ['missing','duplicate','owner','erased','old']:
        bad=copy.deepcopy(inventory)
        row=next(r for r in bad['measurements'] if r['id']==source.records()[0]['id'])
        if mode=='missing':bad['measurements'].remove(row)
        if mode=='duplicate':bad['measurements'].append(copy.deepcopy(row))
        if mode=='owner':row['current_id']='gulf-stream-system'
        if mode=='erased':row.pop('original_regional_context')
        if mode=='old':next(r for r in bad['measurements'] if r['id']==source.load()['existing_current_records'][0]['id'])['approximate_width_km']=135
        with pytest.raises(ValueError):source.validate_inventory(bad)


def test_same_length_source_corruption_is_rejected(tmp_path,monkeypatch):
    audit=source.load();row=source.records()[0]
    paths=[source.AUDIT,audit['protocol_file']]
    for item in audit['sources']:paths += [item['source_document_file'],item['acquisition_file']]
    for name in paths:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source.ROOT/name,target)
    target=tmp_path/audit['sources'][0]['source_document_file'];raw=target.read_bytes()
    target.write_bytes(raw[:20]+bytes([raw[20]^1])+raw[21:])
    monkeypatch.setattr(source,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='original or provenance'):source.validate_row(row)
