"""Tiny synthetic case/scalar metadata; no field, source archive or real index."""
from copy import deepcopy
import math

import pytest

import current_local_extent_evidence_v1 as evidence


@pytest.fixture
def inputs():
    source={'case_run_id':40128227569,'case_run_attempt':1,'case_source_commit':evidence.SOURCE_COMMIT,
        'basis_run_id':40117999392,'basis_run_attempt':2,
        'basis_source_commit':'69cddec0412ca5b1a57c8416067a3e2fd10720af','diagnostic_sha256':'a'*64}
    summary={'schema':'osw.eacc-coastal-reference-extent.compact-review.v1','source':source,
        'case_count':72,'source_model_year':2013,'provider_standard_output_depth_m':15,
        'new_current_measurements_admitted':0,'current_association_verified':False,
        'physical_annual_width_range_km':None,'whole_current_width_km':None,'physical_uncertainty_km':None,'cases':[]}
    support={'schema':'osw.eacc-diagnostic-support.v1','source':{'run_id':40117999392,'run_attempt':2,
        'source_commit':source['basis_source_commit'],'diagnostic_sha256':'a'*64},'cases':[]}
    geography={'schema':'osw.eacc-local-extent.geographic-review.v1','run_id':40128227569,
        'run_attempt':1,'source_commit':evidence.SOURCE_COMMIT,'monthly_maps_actually_inspected':list(range(1,13)),
        'independent_current_edge_association_verified':False,'independent_shore_reference_supplied':False,
        'whole_current_width_admitted':False}
    for month in range(1,13):
        for offset in (-1,0,1):
            for step in (5,10):
                case_id=f'm{month:02d}:offset{offset}:step{step}'
                gate={'status':'synthetic_original_failure','all_five_local_axis_checks_pass':False,
                    'all_five_half_peak_spans_resolved':False}
                original={'id':case_id,'month':month,'native_latitude_offset':offset,'normal_sample_step_km':step,
                    **gate,'seed':{'origin_lon_lat':[40.1,-9.04]},
                    'initial_refinement_peak':{'status':'synthetic_retained_peak','peak_offset_km':0}}
                support['cases'].append(original)
                case={'case_id':case_id,'source_status':gate['status'],'legacy_regional_gate':deepcopy(gate),
                    'status':'synthetic_unresolved','adapter_audit':{'frame_and_support_verified':True,
                        'seed_bearing_degrees_true':340},'metrics':[]}
                for fraction in (.4,.5,.6):
                    for quantity in evidence.QUANTITIES:
                        case['metrics'].append({'fraction':fraction,'quantity':quantity,'status':'synthetic_missing',
                            'extent_bracket_km':None,'maximum_native_cell_scale_km':None,
                            'minimum_span_in_native_cell_scales':None,'source_scale_gate_passed':False,
                            'resolution_status':'unresolved','conditional_on_inshore_flow_assumption':False,
                            'whole_current_width_km':None,'physical_uncertainty_km':None,
                            'width_rank_eligible':False,'physical_state_join_eligible':False})
                summary['cases'].append(case)
    metric=summary['cases'][0]['metrics'][0]
    metric.update(status='source_scale_supported_local_extent',extent_bracket_km=[10.0000001,15.0000001],
        maximum_native_cell_scale_km=2,minimum_span_in_native_cell_scales=5.00000005,source_scale_gate_passed=True)
    return summary,support,geography


def test_projection_copies_every_slot_and_separates_cases_without_mutation(inputs):
    before=deepcopy(inputs);result=evidence.project(*inputs)
    assert inputs==before
    cases=result['collections']['current_local_extent_cases'];records=result['collections']['current_local_extents']
    assert len(cases)==72 and len(records)==len({r['id'] for r in records})==864
    source=inputs[0]['cases'][0]['metrics'][0]
    row=next(r for r in records if r['source_scale_gate_passed'])
    assert row['extent_bracket_km']==source['extent_bracket_km']
    assert row['unit']=='km' and row['rank_eligible'] is False
    assert all(r['whole_current_width_km'] is None and not r['physical_state_join_eligible'] for r in records)
    assert all(c['reference_origin_lon_lat']==[40.1,-9.04] for c in cases)
    assert result['admission']['width_inventory_count_increment']==0
    assert set(result['collections'])=={'current_local_extents','current_local_extent_cases'}
    assert result['method']['new_distance_calculation'] is False
    row['extent_bracket_km'][0]=999
    assert inputs==before


def test_failed_but_geometrically_bounded_attempt_is_retained_as_failed(inputs):
    metric=inputs[0]['cases'][0]['metrics'][0]
    metric.update(status='insufficient_native_scale_support',source_scale_gate_passed=False,
        extent_bracket_km=[1,2],minimum_span_in_native_cell_scales=.5)
    result=evidence.project(*inputs)
    row=next(r for r in result['collections']['current_local_extents'] if r['extent_bracket_km'] is not None)
    assert row['extent_bracket_km']==[1,2] and not row['source_scale_gate_passed']
    assert row['status']=='insufficient_native_scale_support'


@pytest.mark.parametrize('change',['case_missing','duplicate_case','wrong_case','metric_missing','duplicate_metric',
    'extra_quantity','wrong_fraction','original_status','original_gate','original_identity','frame','coordinate',
    'physical_width','physical_uncertainty','rank','state_join','invalid_bracket','nonfinite','zero_scale',
    'underresolved','gate_status','missing_geography','overstated_geography','mixed_source','wrong_depth','wrong_year'])
def test_bad_inventory_source_support_or_admission_is_refused(inputs,change):
    summary,support,geo=inputs;case=summary['cases'][0];metric=case['metrics'][0]
    if change=='case_missing':summary['cases'].pop()
    if change=='duplicate_case':summary['cases'][-1]=deepcopy(case)
    if change=='wrong_case':case['case_id']='m13:offset0:step5'
    if change=='metric_missing':case['metrics'].pop()
    if change=='duplicate_metric':case['metrics'][-1]=deepcopy(metric)
    if change=='extra_quantity':metric['quantity']='whole_current_width'
    if change=='wrong_fraction':metric['fraction']=.7
    if change=='original_status':case['source_status']='improved'
    if change=='original_gate':case['legacy_regional_gate']['all_five_local_axis_checks_pass']=True
    if change=='original_identity':support['cases'][0]['month']=2
    if change=='frame':case['adapter_audit']['frame_and_support_verified']=False
    if change=='coordinate':support['cases'][0]['seed']['origin_lon_lat']=[-9,999]
    if change=='physical_width':metric['whole_current_width_km']=100
    if change=='physical_uncertainty':metric['physical_uncertainty_km']=1
    if change=='rank':metric['width_rank_eligible']=True
    if change=='state_join':metric['physical_state_join_eligible']=True
    if change=='invalid_bracket':metric['extent_bracket_km']=[15,10]
    if change=='nonfinite':metric['extent_bracket_km']=[10,math.inf]
    if change=='zero_scale':metric['maximum_native_cell_scale_km']=0
    if change=='underresolved':metric['minimum_span_in_native_cell_scales']=3.99
    if change=='gate_status':metric['source_scale_gate_passed']=False
    if change=='missing_geography':geo['monthly_maps_actually_inspected']=[1,7]
    if change=='overstated_geography':geo['whole_current_width_admitted']=True
    if change=='mixed_source':support['source']['run_attempt']=1
    if change=='wrong_depth':summary['provider_standard_output_depth_m']=0
    if change=='wrong_year':summary['source_model_year']=2024
    with pytest.raises(ValueError):evidence.project(*inputs)


def test_ordered_projection_does_not_depend_on_input_order(inputs):
    expected=evidence.encoded(evidence.project(*inputs))
    summary,support,_=inputs
    summary['cases'].reverse();support['cases'].reverse()
    for case in summary['cases']:case['metrics'].reverse()
    assert evidence.encoded(evidence.project(*inputs))==expected
