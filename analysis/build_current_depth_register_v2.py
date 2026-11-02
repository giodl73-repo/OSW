"""Append typed depth ranges, strict bounds and core thickness to frozen v1."""
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path
import build_current_depth_register_v1 as legacy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/current-depth-source-facts-v2.json'
RULES = 'research/current-depth-rules-v2.json'
OUTPUT = 'research/current-depth-register-v2.json'
CSV = 'research/current-depth-register-v2.csv'


def numeric(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value >= 0


def validate_reference(row, identities, metrics):
    if row['entity_id'] not in identities or row['metric'] not in metrics:
        raise ValueError('Unknown identity or depth metric')
    if row['unit'] != 'm' or row['vertical_datum'] != 'local_sea_surface_positive_down':
        raise ValueError('Depth requires metres and the declared sea-surface datum')
    point, interval, bound = row['approximate_value_m'], row['range_m'], row['lower_bound_m']
    if sum(x is not None for x in [point,interval,bound]) != 1:
        raise ValueError('Require exactly one scalar, range or strict bound; never invent a midpoint')
    if point is not None and not numeric(point):
        raise ValueError('Invalid depth scalar')
    if interval is not None:
        if not isinstance(interval,list) or len(interval)!=2 or not all(numeric(x) for x in interval) or interval[0]>=interval[1] or not row.get('range_interpretation'):
            raise ValueError('Invalid or unexplained range')
    if bound is not None and (not numeric(bound) or row['lower_bound_exclusive'] is not True):
        raise ValueError('Strict source bound must remain strict')
    if bound is None and row['lower_bound_exclusive'] is not False:
        raise ValueError('Exclusivity without a bound')
    for key in ['geographic_scope','temporal_scope','source_definition','source_url','source_locator','source_citation','qualification','source_case_id']:
        if not row.get(key):raise ValueError('Missing source support: '+key)
    for key in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m']:
        if row[key] is not None:raise ValueError('Scoped prose does not establish whole-flow geometry or uncertainty')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible']:
        if row[key] is not False:raise ValueError('Unreviewed scientific promotion')
    if row['calendar_months'] is not None:
        months=row['calendar_months']
        if not isinstance(months,list) or not months or len(set(months))!=len(months) or any(type(m) is not int or not 1<=m<=12 for m in months) or not row.get('calendar_source_locator'):
            raise ValueError('Calendar months require explicit source support')
    if row['metric']=='core_vertical_thickness':
        if row['evidence_kind']!='published_model_climatology' or row.get('velocity_threshold_m_s')!=0.1 or row.get('velocity_threshold_operator')!='>' or not row.get('aggregation_statistic'):
            raise ValueError('Core thickness requires its threshold, product and aggregation')
        if row.get('model_product')!='BRAN2020' or row.get('climatology_years')!=[2001,2018]:
            raise ValueError('Core thickness model scope unresolved')
    if row['observed_period'] is not None:
        import datetime
        start,end=(datetime.date.fromisoformat(row['observed_period'][k]) for k in ['start','end'])
        if start>end or row['evidence_kind']!='published_observed_section':raise ValueError('Invalid dated section')


def build(root=ROOT):
    prior=legacy.build(root)
    saved=json.loads((root/legacy.OUTPUT).read_bytes())
    if saved!=prior:raise ValueError('Frozen v1 register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [legacy.OUTPUT,legacy.CSV,'analysis/build_current_depth_register_v1.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    rules=json.loads((root/RULES).read_bytes());source=json.loads((root/SOURCE).read_bytes())
    if source['previous_register_sha256']!=pins[legacy.OUTPUT]:raise ValueError('Prior register pin mismatch')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence}
    identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types'])
        if row['id'] in seen:raise ValueError('Duplicate reference ID')
        seen.add(row['id'])
        evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed'
        records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v2','status':'SCOPED_DEPTH_AND_CORE_THICKNESS_REFERENCES_NOT_WHOLE_ROUTE_PROJECTIONS','rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v2.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v2.py').read_bytes()).hexdigest(),'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),'coverage_interpretation':'Reference owners include core-depth and core-thickness context; coverage is not a count of completed lower boundaries, full thickness fields or volumes. Multiple statistics from one source case are not independent observations.','records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=['id','entity_id','metric','approximate_value_m','range_m','lower_bound_m','lower_bound_exclusive','unit','vertical_datum','phase_label','geographic_scope','temporal_scope','source_case_id','aggregation_statistic','source_definition','evidence_kind','source_url','source_locator','qualification']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for row in document['evidence']:
        value=dict(row)
        if value.get('range_m') is not None:value['range_m']=json.dumps(value['range_m'],separators=(',',':'))
        writer.writerow(value)
    return out.getvalue().encode('utf8')


if __name__=='__main__':
    d=build();(ROOT/OUTPUT).write_bytes((json.dumps(d,indent=2,ensure_ascii=False)+'\n').encode('utf8'));(ROOT/CSV).write_bytes(csv_bytes(d));print(json.dumps(d['counts']))
