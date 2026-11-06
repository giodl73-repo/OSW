"""Project retained scalar evidence into separate local-extent research collections.

No velocities, source requests, peak selection, distance calculation or indexing.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SUMMARY='research/eacc-coastal-reference-extent-result-v1.json'
SUPPORT='research/eacc-diagnostic-support-inspection-result-v1.json'
GEOGRAPHY='research/eacc-coastal-reference-extent-geographic-review-v1.json'
PROTOCOL='plans/current-local-extent-evidence-v1.md'
OUTPUT='research/eacc-local-extent-evidence-bundle-v1.json'
SUMMARY_SHA='db49b77d559c30dc77ae209322ec8fdbdc48511fd06b2e303568f90c622bc132'
SUPPORT_SHA='1d46d99855e02682295cf64f28c426c7288bbd51673c16441fc2f136c8fcdf4e'
SOURCE_COMMIT='89ff28ca4c911c48442ada9b1b58b7af6450c2ce'
TARGET='current:east-african-coastal'
QUANTITIES={
    'core_to_positive_normal_threshold_extent':'core-positive',
    'local_two_sided_threshold_span':'paired-span',
    'finite_paired_support_to_positive_threshold_extent':'support-positive',
    'shore_reference_to_positive_threshold_extent':'shore-positive'}
FORBIDDEN_VALUES=('whole_current_width_km','physical_uncertainty_km')


def finite(value):return type(value) in (int,float) and math.isfinite(value)
def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def project(summary,support,geography):
    """Validate and copy all attempted scalar results; never admit physical widths."""
    if (summary.get('schema')!='osw.eacc-coastal-reference-extent.compact-review.v1'
            or summary.get('case_count')!=72 or summary.get('source_model_year')!=2013
            or summary.get('provider_standard_output_depth_m')!=15
            or summary.get('new_current_measurements_admitted')!=0
            or summary.get('current_association_verified') is not False
            or any(summary.get(k) is not None for k in (*FORBIDDEN_VALUES,'physical_annual_width_range_km'))):
        raise ValueError('Changed scalar-evidence scope or admission')
    source=summary.get('source',{})
    if (source.get('case_run_id')!=40128227569 or source.get('case_run_attempt')!=1
            or source.get('case_source_commit')!=SOURCE_COMMIT
            or source.get('basis_run_id')!=40117999392 or source.get('basis_run_attempt')!=2
            or source.get('basis_source_commit')!='69cddec0412ca5b1a57c8416067a3e2fd10720af'
            or support.get('schema')!='osw.eacc-diagnostic-support.v1'
            or support.get('source',{}).get('run_id')!=source['basis_run_id']
            or support['source'].get('run_attempt')!=source['basis_run_attempt']
            or support['source'].get('source_commit')!=source['basis_source_commit']
            or support['source'].get('diagnostic_sha256')!=source.get('diagnostic_sha256')):
        raise ValueError('Mixed original or derived source identity')
    if (geography.get('schema')!='osw.eacc-local-extent.geographic-review.v1'
            or geography.get('run_id')!=source['case_run_id']
            or geography.get('run_attempt')!=1 or geography.get('source_commit')!=SOURCE_COMMIT
            or geography.get('monthly_maps_actually_inspected')!=list(range(1,13))
            or geography.get('independent_current_edge_association_verified') is not False
            or geography.get('independent_shore_reference_supplied') is not False
            or geography.get('whole_current_width_admitted') is not False):
        raise ValueError('Missing or overstated geographic review')
    raw_cases=summary.get('cases',[]);original=support.get('cases',[])
    if len(raw_cases)!=72 or len(original)!=72:raise ValueError('All72 original cases required')
    old={c['id']:c for c in original}
    if len(old)!=72 or len({c['case_id'] for c in raw_cases})!=72:
        raise ValueError('Duplicate case identity')
    expected={(m,o,s) for m in range(1,13) for o in (-1,0,1) for s in (5,10)}
    found=set();cases=[];records=[]
    for case in sorted(raw_cases,key=lambda c:c['case_id']):
        match=re.fullmatch(r'm(\d{2}):offset(-?\d):step(5|10)',case['case_id'])
        if not match or case['case_id'] not in old:raise ValueError('Unknown source case identity')
        month,offset,step=map(int,match.groups());found.add((month,offset,step))
        prior=old[case['case_id']];gate=case['legacy_regional_gate']
        if ((prior.get('month'),prior.get('native_latitude_offset'),prior.get('normal_sample_step_km'))!=(month,offset,step)
                or case['source_status']!=prior['status']
                or any(gate.get(k)!=prior.get(k) for k in ('status','all_five_local_axis_checks_pass','all_five_half_peak_spans_resolved'))
                or any(gate.get(k) is not False for k in ('all_five_local_axis_checks_pass','all_five_half_peak_spans_resolved'))
                or case['adapter_audit'].get('frame_and_support_verified') is not True):
            raise ValueError('Changed original regional gate or unverified frame')
        origin=prior.get('seed',{}).get('origin_lon_lat')
        if (not isinstance(origin,list) or len(origin)!=2 or not all(finite(v) for v in origin)
                or not -180<=origin[0]<=180 or not -90<=origin[1]<=90):
            raise ValueError('Missing original source-seed coordinates')
        peak=prior.get('initial_refinement_peak') or {}
        case_id='local-extent-case:eacc-hycom2013:'+case['case_id']
        case_row={'id':case_id,'source_case_id':case['case_id'],'investigated_current_id':TARGET,
            'year':2013,'month':month,'normal_sample_step_km':step,'native_latitude_offset':offset,
            'reference_origin_lon_lat':deepcopy(origin),
            'reference_position_kind':'original_model_seed_not_current_boundary_or_shore',
            'seed_bearing_degrees_true':case['adapter_audit'].get('seed_bearing_degrees_true'),
            'original_peak_offset_km':peak.get('peak_offset_km'),'original_peak_status':peak.get('status'),
            'source_status':case['source_status'],'status':case['status'],
            'legacy_regional_gate':deepcopy(gate),'adapter_audit':deepcopy(case['adapter_audit'])}
        cases.append(case_row)
        metrics=case.get('metrics',[])
        if (len(metrics)!=12 or {(m.get('fraction'),m.get('quantity')) for m in metrics}
                !={(f,q) for f in (.4,.5,.6) for q in QUANTITIES}):
            raise ValueError('Every fraction/quantity outcome required exactly once')
        for metric in sorted(metrics,key=lambda m:(m['fraction'],m['quantity'])):
            bracket=metric['extent_bracket_km'];passed=metric['source_scale_gate_passed']
            if (bracket is not None and (not isinstance(bracket,list) or len(bracket)!=2
                    or not all(finite(v) for v in bracket) or not 0<bracket[0]<=bracket[1])):
                raise ValueError('Malformed extent bracket')
            if (type(passed) is not bool or (metric['status']=='source_scale_supported_local_extent')!=passed
                    or any(metric.get(k) is not None for k in FORBIDDEN_VALUES)
                    or metric.get('width_rank_eligible') is not False
                    or metric.get('physical_state_join_eligible') is not False):
                raise ValueError('Changed local support status or physical eligibility')
            scale=metric['maximum_native_cell_scale_km'];span=metric['minimum_span_in_native_cell_scales']
            if passed and (bracket is None or not finite(scale) or scale<=0 or not finite(span) or span<4):
                raise ValueError('Unsupported native-scale claim')
            fraction=metric['fraction'];quantity=metric['quantity']
            row={'id':'local-extent:eacc-hycom2013:'+case['case_id']+f':f{round(100*fraction)}:'+QUANTITIES[quantity],
                'case_id':case_id,'source_case_id':case['case_id'],'investigated_current_id':TARGET,
                'year':2013,'month':month,'normal_sample_step_km':step,'native_latitude_offset':offset,
                'threshold_fraction':fraction,'quantity':quantity,'status':metric['status'],
                'extent_bracket_km':deepcopy(bracket),'unit':'km',
                'maximum_native_cell_scale_km':scale,'minimum_span_in_native_cell_scales':span,
                'source_scale_gate_passed':passed,'resolution_status':metric['resolution_status'],
                'conditional_on_inshore_flow_assumption':metric['conditional_on_inshore_flow_assumption'],
                'record_role':'model_local_extent_method_development','whole_current_width_km':None,
                'physical_uncertainty_km':None,'rank_eligible':False,'physical_state_join_eligible':False}
            records.append(row)
    if found!=expected or len(records)!=864:raise ValueError('Incomplete month/offset/step inventory')
    return {'schema':'osw.current-local-extent-evidence.v1','version':'eacc-local-extents-v1',
        'status':'research_scalar_projection_not_installed_atlas_or_physical_width_admission',
        'source':deepcopy(source),'source_scope':{'model_year':2013,'provider_standard_output_depth_m':15,
            'depth_coordinate_kind':'provider_standard_output_point_not_layer_average',
            'time_support':'daily00Z_sample_monthly_mean_fields_not_instantaneous_width_climatology',
            'coordinate':'signed_WGS84_geodesic_normal_km','positive_normal_is_verified_offshore':False},
        'collections':{'current_local_extent_cases':cases,'current_local_extents':records},
        'coverage':{'case_count':72,'attempted_metric_slots':864,'quantity_types':list(QUANTITIES),
            'counts_are_attempt_slots_not_independent_current_measurements':True},
        'admission':{'scientific_current_association_verified':False,'whole_current_width_admitted':False,
            'physical_annual_dimension_range_km':None,'physical_uncertainty_km':None,
            'width_inventory_count_increment':0,'state_joins_admitted':False,'physical_current_geometry':None},
        'method':{'new_velocity_processing':False,'new_distance_calculation':False,
            'new_peak_selection':False,'new_provider_requests':0,'source_values_copied_without_rounding':True,
            'no_interpolation_midpoint_or_one_sided_doubling':True}}


def build(root=ROOT):
    root=Path(root);raw=(root/SUMMARY).read_bytes();support_raw=(root/SUPPORT).read_bytes()
    if sha(raw)!=SUMMARY_SHA or len(raw)!=475855 or sha(support_raw)!=SUPPORT_SHA:
        raise ValueError('Changed executed scalar source')
    document=project(json.loads(raw),json.loads(support_raw),json.loads((root/GEOGRAPHY).read_bytes()))
    inputs=(SUMMARY,SUPPORT,GEOGRAPHY,PROTOCOL,'analysis/current_local_extent_evidence_v1.py',
        'analysis/test_current_local_extent_evidence_v1.py')
    document['input_sha256']={p:sha((root/p).read_bytes()) for p in inputs}
    return document


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true',help='Write only the scalar research bundle')
    args=parser.parse_args();document=build();raw=encoded(document)
    if args.prepare:
        with (ROOT/OUTPUT).open('xb') as stream:stream.write(raw)
    print(json.dumps({'bytes':len(raw),'sha256':sha(raw),'cases':72,'attempts':864,'physical_widths_admitted':0}))
