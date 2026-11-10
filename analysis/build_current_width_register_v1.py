"""Normalize authenticated source width records, without runtime or index I/O."""
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH='research/current-width-register-v1.json'
CSV_PATH='research/current-width-register-v1.csv'


def pointer(document,path):
    value=document
    for token in path.strip('/').split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def first(record,*keys):
    return next((record[k] for k in keys if record.get(k) is not None),None)


def normalize(raw,document,path,location):
    source=document.get('source',{})
    if not isinstance(source,dict):source={}
    point=first(raw,'approximate_width_km','reported_width_km','reported_mean_width_km')
    interval=raw.get('width_range_km')
    constraint=raw.get('reported_width_constraint')
    lower=raw.get('lower_bound_km');upper=raw.get('upper_bound_km')
    for value in [point,lower,upper]:
        if value is not None and (not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0):
            raise ValueError('Non-positive or invalid width quantity: '+raw['id'])
    if interval is not None and (len(interval)!=2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in interval) or interval[0]>interval[1] or interval[1]<=0):raise ValueError('Invalid width range')
    if not any(value is not None for value in [point,interval,constraint,lower,upper]):raise ValueError('Unmapped width quantity: '+raw['id'])
    metric=first(raw,'width_metric','quantity')
    if not metric:raise ValueError('Missing width definition: '+raw['id'])
    url=raw.get('source_url') or document.get('source_url') or source.get('url') or source.get('source_url')
    if not url and raw.get('source_doi'):url='https://doi.org/'+raw['source_doi']
    quality=first(raw,'source_quality_note','scope_notes','source_scope_notes') or document.get('lineage_note')
    ambiguity=[r for r in document.get('source_ambiguities',[]) if r['id']==raw.get('operator_ambiguity_id')]
    if ambiguity:quality={'record_note':quality,'source_operator_ambiguity':ambiguity}
    locator=raw.get('source_locator') or document.get('source_locator') or source.get('source_locator')
    if not locator and document.get('passage'):
        passage=document['passage'];locator=f"{passage.get('section','Selected passage')}; printed page{passage.get('printed_page')} / PDF{passage.get('pdf_page')}; {passage.get('paragraph','')}"
    return {'id':raw['id'],'entity_id':'current:'+raw['current_id'].removeprefix('current:'),
        'point_km':point,'range_km':interval,'lower_bound_km':lower,'lower_bound_exclusive':bool(raw.get('lower_bound_exclusive')),
        'upper_bound_km':upper,'upper_bound_exclusive':bool(raw.get('upper_bound_exclusive')),
        'constraint':constraint,'metric':metric,'metric_label':raw.get('width_metric_label') or metric.replace('_',' '),
        'zero_range_endpoint_as_reported':bool(interval is not None and 0 in interval),
        'operator':first(raw,'boundary_rule','boundary_definition','operator','reported_operator','edge_operator'),
        'scope':first(raw,'geographic_scope','scope') or document.get('geographic_scope') or document.get('regional_support',{}).get('section'),
        'layer':first(raw,'layer','vertical_scope','layer_description','layer_note'),
        'time':first(raw,'time_convention','time_description','source_time_description','observation_period','observed_period'),
        'phase_kind':raw.get('phase_kind'),'phase_label':raw.get('phase_label'),'calendar_months':raw.get('calendar_months'),
        'range_interpretation':raw.get('range_interpretation'),
        'uncertainty_km':first(raw,'uncertainty_km','numerical_width_uncertainty_km','reported_width_uncertainty_km'),
        'reported_standard_deviation_km':raw.get('reported_width_standard_deviation_km'),
        'source_url':url,'source_citation':raw.get('source_citation') or document.get('source_citation') or source.get('title'),
        'source_locator':locator,'source_file':path,'source_pointer':location,
        'figure_file':first(raw,'figure_file','figure'),'quality_note':quality,
        'whole_current_representative':bool(raw.get('whole_current_representative')),
        'annual_range_km':raw.get('annual_width_range_km'),'evidence_role':'retained_scoped_evidence','raw_record':raw}


def build():
    pins={}
    def read(path):
        raw=(ROOT/path).read_bytes();pins[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    reconciliation=read('research/current-width-record-owner-reconciliation-v1.json')
    lengths=read('research/current-length-estimate-register-v1.json')
    identities={r['entity_id']:r for r in lengths['records']}
    if len(identities)!=111:raise ValueError('Complete111-identity inventory required')
    evidence=[];seen=set()
    for group in reconciliation['source_width_groups']:
        path=group['source_file'];document=read(path)
        if pins[path]!=group['source_sha256']:raise ValueError('Width source changed: '+path)
        selected=pointer(document,group['source_pointer']);items=selected if isinstance(selected,list) else [selected]
        if [(r['id'],r['current_id']) for r in items]!=[(r['id'],r['current_id']) for r in group['rows']]:raise ValueError('Source selection differs')
        for number,raw in enumerate(items):
            if raw['id'] in seen:raise ValueError('Duplicate width record')
            seen.add(raw['id']);location=group['source_pointer']+('/'+str(number) if isinstance(selected,list) else '')
            row=normalize(raw,document,path,location)
            if row['entity_id'] not in identities:raise ValueError('Unknown width owner')
            evidence.append(row)
    if len(evidence)!=190:raise ValueError('All190 retained width records required')
    retained_owners={r['entity_id'] for r in evidence}
    extra_path='research/current-width-register-additions-v1.json';extra=read(extra_path)
    for number,raw in enumerate(extra['records']):
        if raw['id'] in seen or 'current:'+raw['current_id'] not in identities:raise ValueError('Invalid new reference identity')
        row=normalize(raw,extra,extra_path,'/records/'+str(number));row['evidence_role']='new_qualified_reference'
        evidence.append(row);seen.add(row['id'])
    source_inventory=read('research/ocean-current-width-inventory.json')
    decisions={r['current_id']:r for r in reconciliation['current_decisions']}
    family=read('research/current-length-family-conventions-v1.json')
    family_members={r['entity_id']:r['members'] for r in family['conventions'] if r['convention']=='longest_catalogued_member'}
    rows=[]
    for identifier,current in identities.items():
        owned=sorted((r for r in evidence if r['entity_id']==identifier),key=lambda r:r['id'])
        decision=decisions[identifier.removeprefix('current:')]
        references=[{'entity_id':member,'name':identities[member]['name'],
            'evidence_ids':[r['id'] for r in evidence if r['entity_id']==member],
            'current_card_url':identities[member]['current_card_url']} for member in family_members.get(identifier,[])]
        rows.append({'entity_id':identifier,'name':current['name'],'basin':current['basin'],'identity_level':current['identity_level'],
            'status':'new_qualified_reference' if owned and all(r['evidence_role']=='new_qualified_reference' for r in owned) else 'scoped_evidence' if owned else 'member_references' if references else 'needs_width_evidence',
            'evidence_ids':[r['id'] for r in owned],'metric_count':len({r['metric'] for r in owned}),
            'member_references':references,'member_reference_is_parent_measurement':False,
            'whole_current_representative_width_km':None,'annual_width_range_km':None,
            'next_action':decision.get('next_action') or 'Review named-flow definition and recover source-supported width evidence.',
            'prior_width_decision':decision['width_decision'],'current_card_url':current['current_card_url'],
            'length_context_url':'lengths.html','physical_area_from_length_times_width_eligible':False})
    owners={r['entity_id'] for r in evidence}
    return {'schema':'osw.current-width-register.v1','status':'WIDTH_GAP_FILLING_IN_PROGRESS',
        'generator_file':'analysis/build_current_width_register_v1.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':pins,'rules_file':'plans/current-width-register-v1.md',
        'rules_sha256':hashlib.sha256((ROOT/'plans/current-width-register-v1.md').read_bytes()).hexdigest(),
        'measurement_protocol_file':'plans/ocean-current-width-measurement-protocol-v1.md',
        'measurement_protocol_sha256':hashlib.sha256((ROOT/'plans/ocean-current-width-measurement-protocol-v1.md').read_bytes()).hexdigest(),
        'counts':{'identities':111,'source_records':len(evidence),'retained_scoped_records':190,
            'identities_with_retained_scoped_evidence':len(retained_owners),'new_qualified_reference_records':len(extra['records']),
            'identities_with_direct_width_reference':len(owners),
            'identities_without_direct_width_reference':111-len(owners),'family_entries_with_member_references':len(family_members),
            'whole_current_representative_widths':sum(r['whole_current_representative'] for r in evidence)},
        'records':rows,'evidence':evidence,'compatible_seasonal_groups':source_inventory['seasonal_summaries'],
        'range_rules':['No midpoint for range-only records.','No pooling of incompatible definitions, sections or layers.','No annual extrema or occupied polygons inferred.'],
        'scientific_measurements_changed':False,'runtime_changed':False,'full_goal_complete':False}


def main():
    document=build();(ROOT/JSON_PATH).write_bytes((json.dumps(document,indent=2,ensure_ascii=False)+'\n').encode())
    fields=['entity_id','id','metric','point_km','range_min_km','range_max_km','lower_bound_km','lower_bound_exclusive','upper_bound_km','upper_bound_exclusive','constraint_json','scope','layer','time','operator','range_interpretation','source_url','source_locator','source_file','source_pointer','whole_current_representative']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
    for r in document['evidence']:
        writer.writerow({**r,'range_min_km':r['range_km'][0] if r['range_km'] else None,'range_max_km':r['range_km'][1] if r['range_km'] else None,
            'constraint_json':json.dumps(r['constraint'],ensure_ascii=False) if r['constraint'] else '',
            'time':r['time'] if isinstance(r['time'],str) else json.dumps(r['time'],ensure_ascii=False) if r['time'] else None})
    (ROOT/CSV_PATH).write_bytes(out.getvalue().encode())
    print(json.dumps(document['counts']))


if __name__=='__main__':main()
