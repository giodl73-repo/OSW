"""Append Pacific depth cases, preserving strict upper bounds and method differences."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v5 as previous
from build_current_depth_register_v2 import numeric

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v6.json'
RULES='research/current-depth-rules-v6.json'
OUTPUT='research/current-depth-register-v6.json'
CSV='research/current-depth-register-v6.csv'


def validate_reference(row,identities,metrics):
    if row['entity_id'] not in identities or row['metric'] not in metrics:
        raise ValueError('Unknown identity or depth metric')
    if row['unit']!='m' or row['vertical_datum']!='local_sea_surface_positive_down':
        raise ValueError('Require metres and sea-surface datum')
    point,interval,lower,upper=(row.get(k) for k in ['approximate_value_m','range_m','lower_bound_m','upper_bound_m'])
    if sum(v is not None for v in [point,interval,lower,upper])!=1:
        raise ValueError('Require one scalar, range or one-sided bound')
    if point is not None and not numeric(point):raise ValueError('Invalid scalar')
    if interval is not None and (not isinstance(interval,list) or len(interval)!=2 or not all(numeric(v) for v in interval) or interval[0]>=interval[1] or not row.get('range_interpretation')):
        raise ValueError('Invalid or unexplained range')
    for label,value in [('lower',lower),('upper',upper)]:
        if value is not None:
            if not numeric(value) or value==0 or row.get(label+'_bound_exclusive') is not True:
                raise ValueError('Strict positive bound must retain exclusivity')
        elif row.get(label+'_bound_exclusive',False) is not False:
            raise ValueError('Exclusivity without bound')
    for key in ['geographic_scope','temporal_scope','source_definition','source_url','source_locator','source_citation','qualification','source_case_id']:
        if not row.get(key):raise ValueError('Missing source support: '+key)
    for key in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m']:
        if row[key] is not None:raise ValueError('Scoped reference cannot become whole-flow geometry')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible']:
        if row[key] is not False:raise ValueError('Unreviewed scientific promotion')
    if row['calendar_months'] is not None:
        months=row['calendar_months']
        if not isinstance(months,list) or not months or len(set(months))!=len(months) or any(type(m) is not int or not 1<=m<=12 for m in months) or not row.get('calendar_source_locator'):
            raise ValueError('Months require explicit source support')
    if row['observed_period'] is not None:raise ValueError('These source cases use separate averaging windows')
    if row.get('core_vertical_thickness') is not None or row['metric'] in ['core_vertical_thickness','vertical_thickness','observation_layer']:
        raise ValueError('This batch supplies no thickness or instrument-layer measurements')


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat count established')
    case=row['source_case_id']
    if case=='mindanao-zhang-2014-mooring-mean':
        if row['entity_id']!='current:mindanao-current' or row.get('mooring_lon_lat')!=[127.05,8] or row.get('averaging_period')!={'start':'2010-12-01','end':'2012-12-07'}:
            raise ValueError('Mindanao mooring context changed')
        if row['evidence_kind']!='published_mooring_mean' or row.get('overlaps_case_id')!='mindanao-ren-2018-monthly-climatology':raise ValueError('Retain overlapping observation context')
    elif case=='mindanao-ren-2018-monthly-climatology':
        if row['entity_id']!='current:mindanao-current' or row.get('mooring_lon_lat')!=[127.05,8] or row.get('climatology_period')!={'start_month':'2010-12','end_month':'2014-08'}:
            raise ValueError('Mindanao climatology changed')
        if row['evidence_kind']!='published_observational_climatology' or row.get('processing')!='daily means, vertical interpolation, regression gap filling, monthly climatology':
            raise ValueError('Gap-filled climatology processing must remain explicit')
        if row.get('overlaps_case_id')!='mindanao-zhang-2014-mooring-mean':raise ValueError('Retain overlapping support')
    elif case=='ngcuc-azminuddin-2022-140E-mean':
        if row['entity_id']!='current:new-guinea-coastal-undercurrent' or row['evidence_kind']!='published_model_climatology' or row.get('model_product')!='GLORYS2V4' or row.get('climatology_period')!={'start_month':'1994-01','end_month':'2015-12'} or row.get('section_longitude_degrees_east')!=140:
            raise ValueError('Model section is not an observed whole-route profile')
        if row.get('depth_uncertainty_inferred_from_velocity') is not False:raise ValueError('Velocity error is not depth error')
    elif case=='ngcuc-spray-southern-track-climatology':
        if row['entity_id']!='current:new-guinea-coastal-undercurrent' or row['metric']!='reported_vertical_extent' or row.get('lower_bound_m')!=1000 or row['evidence_kind']!='published_glider_climatology_summary' or row.get('sampling_limit_is_flow_boundary') is not False:
            raise ValueError('Below-sampling reach must remain a censored flow reference')
    elif case=='alaska-coastal-stabeno-1996-regional-summary':
        if row['entity_id']!='current:alaska-coastal-gulf' or row['metric']!='reported_vertical_extent' or row.get('upper_bound_m')!=150 or row['evidence_kind']!='published_literature_synthesis':
            raise ValueError('Regional shallow-current bound must not become Alaska Current depth')
    elif case in ['pacific-euc-azminuddin-2022-introduction','pacific-nscc-azminuddin-2022-introduction']:
        expected='current:pacific-equatorial-undercurrent' if 'euc-' in case else 'current:pacific-north-subsurface-countercurrent'
        if row['entity_id']!=expected or row['metric']!='reported_flow_depth_band' or row['evidence_kind']!='published_literature_synthesis':
            raise ValueError('Regional flow band cannot fill a family or thickness')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v5.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v6','status':'SCOPED_DEPTH_REFERENCES_WITH_PACIFIC_CASES_AND_ONE_SIDED_BOUNDS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v6.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v6.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Strict upper bounds are not point estimates. Overlapping mooring studies and model/observational cases remain distinct, without constructing numerical uncertainty or annual ranges.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    # Preserve earlier exported columns, and expose new bound and averaging semantics.
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['upper_bound_m','upper_bound_exclusive','evidence_kind','model_product','averaging_period',
              'climatology_period','mooring_lon_lat','section_longitude_degrees_east','overlaps_case_id']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
