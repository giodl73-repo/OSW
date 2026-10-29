"""Source-bound query admission for the complete regional model-grid length series."""
import copy
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import quote

import chen_indian_sec_regional_ridge_lengths_v1 as science
import check_chen_indian_sec_ridge_parent_v1 as parent

ROOT=Path(__file__).resolve().parents[1]
FILE='research/chen-indian-sec-ridge-length-query-contract-v1.json'
MODULE='analysis/chen_indian_sec_ridge_query_v1.py'
PROTOCOL='plans/chen-indian-sec-ridge-length-query-contract-v1.md'
SELECTED='research/chen-indian-sec-ridge-parent-run-v1/selected-records.json'
RESULT='research/chen-indian-sec-ridge-parent-run-v1/result.json'
PARENT_REVIEW='research/chen-indian-sec-ridge-parent-execution-review-v1.json'
ENTITY='current:indian-south-equatorial'
FAMILY='current:south-equatorial'
PARENT='3e8dad713d264d5ae4bd4538a503a695174444f2e190803da445b72e62229a38'
KEY='indian_sec_model_grid_lengths_v1'
SERIES='current_length_series'
READINGS='current_length_readings'
SENSITIVITIES='current_length_sensitivities'
SERIES_ID='model_core_series:indian-sec:chen-2022:son65-105:v1'
SOURCE_IDS=['source:chen-indian-sec-2022','source:chen-indian-sec-model-deposit','source:osw-indian-sec-model-grid-length-v1']


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())


def query_url(collection,filters,limit=100,sort=None):
    request={'collection':collection,'filters':[{'field':k,'op':'eq','value':v} for k,v in filters],'limit':limit}
    if sort:request['sort']={'field':sort,'direction':'asc'}
    return 'query.html?q='+quote(json.dumps(request,separators=(',',':')),safe='')


def sources():
    common={'provider_asset_redistributed':False,'used_in_collections':[SERIES,READINGS,SENSITIVITIES],
            'source_facts_file':science.FILE,'source_facts_sha256':sha(science.FILE)}
    return [
        {**common,'id':SOURCE_IDS[0],'kind':'paper','year':2022,'doi':'10.1029/2022JC018969',
         'title':parent.PAPERS['chen_indian_sec_2022']['title'],'label':'Chen et al.2022: Indian SEC seasonal structure',
         'authors':['Gengxin Chen','Weiqing Han','Dongxiao Wang','Lei Zhang','Xiaoqing Chu','Yunkai He','Ju Chen'],
         'url':'https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022JC018969',
         'access_scope':'Publisher HTML methods and captions reviewed. Original Figure4 surface routes were not acquired or reproduced. Exact public model deposit independently acquired and reconstructed on the cloud.'},
        {**common,'id':SOURCE_IDS[1],'kind':'dataset','label':'Chen Indian SEC HYCOM/LOM model deposit',
         'title':parent.PAPERS['chen_indian_sec_model_deposit']['title'],
         'url':'https://data.scsio.ac.cn/metaData-detail/1567926827663917056',
         'provider_metadata_file':'research/source-data/chen-indian-sec-2022/model-provider-metadata-v1.json',
         'provider_record':'1567926827663917056','provider_checksum':None,'provider_license':None,
         'asset_name':'HYCOM_CR_1993_2016.mat','asset_bytes':5816818,
         'asset_sha256':'ce174a089a2379cd8c5a79ede226982749d9102a7e7b7d2d0a9180c75ac23cb7',
         'asset_url':'https://data.scsio.ac.cn/api/web/v1/file/load/metadata/1568072617497661440.mat',
         'scope_note':'Provider describes upper100m SON model means. Date encoding inferred; MAT component units undocumented. No speed measurement or physical current-axis claim.'},
        {**common,'id':SOURCE_IDS[2],'kind':'internal','label':'OSW Indian SEC regional model-grid length method v1',
         'title':'Reviewed regional model-core grid polylines and WGS84 pathlengths',
         'url':'../plans/chen-indian-sec-regional-ridge-length-protocol-v1.md','path':'plans/chen-indian-sec-regional-ridge-length-protocol-v1.md',
         'repository_path':'plans/chen-indian-sec-regional-ridge-length-protocol-v1.md',
         'source_locator':'Frozen core selector, source-map reviews, WGS84 length protocol and complete failure-preserving report.',
         'scope_note':'Method and resolution spans are not physical uncertainty, annual extrema or independent observations.'}]


def display_geometry(points):
    dense=[]
    for a,b in zip(points,points[1:]):
        count=max(0,math.ceil(science.GEOD.inv(*a,*b)[2]/10000)-1)
        dense.append(list(a))
        if count:dense.extend([list(p) for p in science.GEOD.npts(*a,*b,count)])
    dense.append(list(points[-1]))
    return {'type':'LineString','coordinates':dense}


def model_records(report):
    readings=[];sensitivities=[]
    for index,original in enumerate(report['rows']):
        case=original['case'];year=None if case.startswith('mean-') else int(case.rsplit('-',1)[1])
        suffix=case+':k'+str(original['kernel_cells'])
        ident='model_core_length:indian-sec:chen-2022:'+suffix+':v1'
        valid=original['length_km'] is not None
        row={k:copy.deepcopy(v) for k,v in original.items() if k not in ['id','status','resolution_scenarios','coordinates']}
        label='Indian SEC · '+('mean field' if year is None else 'SON '+str(year))+' · kernel '+str(original['kernel_cells'])
        row.update(id=ident,label=label,series_id=SERIES_ID,entity_id=ENTITY,current_id='indian-south-equatorial',
                   reading_order=index,provider_year=year,reading_kind='regional_model_core_grid_trace',
                   status='regional_model_grid_estimate' if valid else 'withheld_failed_trace',unit='km',
                   unrounded_length_km=original['length_km'],source_id=SOURCE_IDS[0],dataset_source_id=SOURCE_IDS[1],
                   method_source_id=SOURCE_IDS[2],source_ids=list(SOURCE_IDS),
                   exact_observation_time=None,season='SON',layer_scope='provider-described upper100m mean',
                   rank_eligible=False,physical_state_join_eligible=False,seasonal_playback_eligible=False,
                   geometry_role='regional_model_grid_reference' if valid else None,
                   geometry=display_geometry(original['coordinates']) if valid else None,
                   geometry_source_vertex_count=len(original.get('coordinates',[])) if valid else 0,
                   geometry_display_max_leg_km=10 if valid else None,
                   geometry_vertex_kind='source_grid_vertices_and_geodesic_display_interpolation' if valid else None,
                   scientific_report_file=science.FILE,scientific_report_sha256=sha(science.FILE),
                   scientific_report_pointer='/rows/'+str(index))
        readings.append(row)
        for scenario in original['resolution_scenarios']:
            sensitivities.append({
                'id':'model_core_sensitivity:indian-sec:chen-2022:'+suffix+':s'+str(scenario['stride'])+':p'+str(scenario['phase'])+':v1',
                'series_id':SERIES_ID,'reading_id':ident,'entity_id':ENTITY,'current_id':'indian-south-equatorial',
                'case':case,'provider_year':year,'kernel_cells':original['kernel_cells'],
                'stride':scenario['stride'],'phase':scenario['phase'],'retained_vertices':scenario['retained_vertices'],
                'length_km':scenario['length_km'],'unit':'km','source_id':SOURCE_IDS[0],
                'dataset_source_id':SOURCE_IDS[1],'method_source_id':SOURCE_IDS[2],
                'interpretation':'Computed vertex-sampling choice; not a physical bound or confidence interval.',
                'is_observation':False,'is_physical_uncertainty':False,'is_annual_range':False,
                'rank_eligible':False,'seasonal_playback_eligible':False})
    header={'id':SERIES_ID,'schema':'osw.regional-model-core-length-series.v1','entity_id':ENTITY,
            'current_id':'indian-south-equatorial','label':'Indian SEC regional model-core grid lengths',
            'quantity':'regional_model_core_grid_polyline_length','evidence_kind':'derived_regional_model_grid_trace',
            'unit':'km','sample_collection':READINGS,'sensitivity_collection':SENSITIVITIES,
            'reading_count':75,'qualified_grid_length_count':8,'withheld_reading_count':67,
            'model_year_count':24,'qualified_nominal_model_year_count':3,'mean_field_withheld':True,
            'source_id':SOURCE_IDS[0],'dataset_source_id':SOURCE_IDS[1],'method_source_id':SOURCE_IDS[2],
            'source_ids':list(SOURCE_IDS),'scientific_report_file':science.FILE,'scientific_report_sha256':sha(science.FILE),
            'figure_file':science.FIGURE,'figure_sha256':sha(science.FIGURE),
            'geographic_gates_degrees_east':[105.15,64.76700000000017],
            'gate_role':'Editorial regional comparison gates; not physical current endpoints.',
            'time_support':{'provider_start_year':1993,'provider_end_year':2016,'season':'SON',
                            'source_date_encoding':'inferred MATLAB serial dates','exact_observation_dates_recovered':False,
                            'supports_calendar_month_dimensions':False},
            'layer_scope':'Provider-described upper100m seasonal model means',
            'nominal_kernel_cells':3,'display_rounding_km':100,'case_summaries':copy.deepcopy(report['cases']),
            'computed_span_kind':'smoothing_and_vertex_sampling_choices','physical_uncertainty_km':None,
            'whole_current_length_km':None,'annual_length_range_km':None,'physical_width_km':None,
            'geographic_centerline':None,'physical_current_axis_admitted':False,'physical_state_join_eligible':False,
            'whole_current_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
            'recovered_observed_sample_count':0,
            'scope':'Regional native-grid model-core ridge lengths. Eight qualified method cases across three model years;67 withheld cases remain explicit. Not whole-current lengths, author surface axes, streamlines, physical error bounds or annual extrema.'}
    return header,readings,sensitivities


def build_contract():
    report=science.build()
    if (json.dumps(report,indent=2)+'\n').encode()!=(ROOT/science.FILE).read_bytes() or science.figure(report).encode()!=(ROOT/science.FIGURE).read_bytes():
        raise ValueError('Frozen scientific outputs changed')
    selected=read(SELECTED);result=read(RESULT);review=read(PARENT_REVIEW)
    if result['logical_sha256']!=PARENT or review['request_disabled'] is not True or review['candidate_prefix_matches']:
        raise ValueError('Actual completed parent audit required')
    if any(r['status']!='MISSING' for r in result['publication_resolutions'].values()):
        raise ValueError('Existing source identity requires reconciliation')
    header,readings,sensitivities=model_records(report)
    prior=selected['identities'][ENTITY];old=prior['object'];owner=copy.deepcopy(old)
    owner['source_ids']=sorted(set(old['source_ids'])|set(SOURCE_IDS));owner['linked_source_count']=len(owner['source_ids'])
    owner['capabilities']['regional_length_series']=1
    owner['regional_length_series_ids']=[SERIES_ID]
    owner['series'].append({'id':SERIES_ID,'label':header['label'],'collection':SERIES,'sample_collection':READINGS,
                            'quantity':header['quantity'],'qualified_grid_length_count':8,'withheld_reading_count':67,
                            'qualified_model_year_count':3,'is_observed_time_series':False})
    owner['evidence_links'] += [
        {'label':'Regional model lengths and method sensitivity','url':'../'+science.FIGURE},
        {'label':'Inspect all75 model cases, including67 withheld','url':query_url(READINGS,[('series_id',SERIES_ID)],sort='reading_order')},
        {'label':'View the three regional model traces','url':query_url(READINGS,[('series_id',SERIES_ID),('kernel_cells',3),('status','regional_model_grid_estimate')])+'#query-map-section'},
        {'label':'Inspect all120 resolution scenarios','url':query_url(SENSITIVITIES,[('series_id',SERIES_ID)])},
        {'label':'Read the model-series scope and provenance','url':query_url(SERIES,[('id',SERIES_ID)],limit=1)}]
    new_sources=sources()
    for section,value in [('measurements',{'header':header,'readings':readings,'sensitivities':sensitivities}),
                          ('sources',new_sources),('routes_geometry',[r['geometry'] for r in readings if r['geometry'] is not None]),
                          ('time_evidence',header['time_support'])]:
        owner['section_fingerprints'][section]=fingerprint({'prior_fingerprint':old['section_fingerprints'][section],'added_regional_model_evidence':value})
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    assessments=prior['length_assessments']
    if len(assessments)!=1:raise ValueError('One audited prior length assessment required')
    assessment=copy.deepcopy(assessments[0])
    assessment.update(evidence_status='regional_model_core_grid_series',whole_current_evidence_status='unmeasured',
                      regional_length_series_id=SERIES_ID,measurement_admission_file=FILE,
                      length_source_id=SOURCE_IDS[0],length_source_locator='Public HYCOM_CR model deposit and frozen regional grid-length protocol.',
                      range_kind='computed_method_resolution_span_per_model_case',
                      scope=header['scope'])
    pins=[MODULE,PROTOCOL,SELECTED,RESULT,PARENT_REVIEW,'research/chen-indian-sec-ridge-parent-run-v1/run-receipt.json',
          'research/chen-indian-sec-ridge-parent-run-v1/executed-request.json',parent.REQUEST,parent.PREFLIGHT,
          science.FILE,science.FIGURE,science.PREFLIGHT,'analysis/chen_indian_sec_regional_ridge_lengths_v1.py',
          'research/chen-indian-sec-ridge-length-execution-review-v1.json',
          'research/chen-indian-sec-passing-map-visual-review-v1.json',
          'research/source-data/chen-indian-sec-2022/model-provider-metadata-v1.json']
    counts=result['collection_counts'];totals=dict(counts)
    for name,amount in [(SERIES,1),(READINGS,75),(SENSITIVITIES,120),('sources',3)]:totals[name]=totals.get(name,0)+amount
    return {'schema':'osw.chen-indian-sec-ridge-length-query-contract.v1','status':'PREPARED_NOT_COMPILED_OR_INSTALLED',
            'parent_logical_sha256':PARENT,'parent_collection_counts':counts,'prior_records':selected,
            'series_record':header,'reading_records':readings,'sensitivity_records':sensitivities,
            'new_sources':new_sources,'final_owner':owner,'final_length_assessment':assessment,
            'input_sha256':{p:sha(p) for p in pins},'expected_totals':totals,
            'new_series':1,'new_readings':75,'qualified_grid_lengths':8,'withheld_readings':67,'new_sensitivities':120,
            'new_publication_sources':1,'new_dataset_sources':1,'new_internal_method_sources':1,
            'new_reported_lengths':0,'new_reference_routes':0,'new_widths':0,'new_independent_observations':0,
            'physical_state_joins_added':0,'seasonal_dimension_playback_added':False}


def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied contract and audited parent required')
    counts=contract['parent_collection_counts']
    for name in ['objects','entities','sources','length_assessments',SERIES,READINGS,'widths','reference_routes']:
        rows=collections.get(name)
        if not isinstance(rows,list) or len(rows)!=counts[name]:raise ValueError('Parent count differs: '+name)
        ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):raise ValueError('Unique parent IDs required: '+name)
    if SENSITIVITIES in collections:raise ValueError('Unexpected existing sensitivity collection')
    for owner,audited in contract['prior_records']['identities'].items():
        for name,key in [('objects','object'),('entities','entity')]:
            if [r for r in collections[name] if r['id']==owner]!=[audited[key]]:raise ValueError('Changed audited identity: '+owner)
        for name,expected in audited['linked_records'].items():
            found=[r for r in collections.get(name,[]) if r.get('entity_id')==owner or r.get('current_id')==owner.removeprefix('current:') or r.get('family_entity_id')==owner]
            if found!=expected:raise ValueError('Changed audited owner evidence: '+owner+'/'+name)
    matches,resolutions=parent.publications(collections['sources'])
    if any(matches.values()) or any(r['status']!='MISSING' for r in resolutions.values()):raise ValueError('Source identity changed after audit')
    old_sources={r['id']:r for r in collections['sources']}
    if any(i in old_sources for i in SOURCE_IDS):raise ValueError('New source ID already exists')
    for audited in contract['prior_records']['identities'].values():
        if any(old_sources.get(r['id'])!=r for r in audited['owner_sources']):raise ValueError('Existing owner source changed')
    if any(r.get('id','').startswith(parent.PREFIXES) for rows in collections.values() for r in rows):raise ValueError('Candidate ID prefix already exists')
    pins={**contract['input_sha256'],FILE:fingerprint(contract)}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=h for p,h in pins.items()):raise ValueError('Historical source pin would change')
    after=dict(collections)
    after[SERIES]=[*collections[SERIES],copy.deepcopy(contract['series_record'])]
    after[READINGS]=[*collections[READINGS],*copy.deepcopy(contract['reading_records'])]
    after[SENSITIVITIES]=copy.deepcopy(contract['sensitivity_records'])
    after['sources']=[*collections['sources'],*copy.deepcopy(contract['new_sources'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==ENTITY else r for r in collections['objects']]
    after['length_assessments']=[copy.deepcopy(contract['final_length_assessment']) if r['entity_id']==ENTITY else r for r in collections['length_assessments']]
    updated=dict(manifest)
    updated['input_sha256']={**manifest.get('input_sha256',{}),**pins}
    updated[KEY]={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':FILE,
                  'contract_sha256':fingerprint(contract),'parent_logical_sha256':PARENT,
                  'series_added':1,'readings_added':75,'sensitivities_added':120,
                  'qualified_model_grid_lengths':8,'withheld_readings':67,'reported_lengths_added':0,
                  'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
    return after,updated


def main():
    raw=encoded(build_contract());path=ROOT/FILE
    if path.exists():raise ValueError('Query contract already exists; preserve frozen version')
    path.write_bytes(raw)
    print(json.dumps({'status':'QUERY_CONTRACT_PREPARED','bytes':len(raw),'series':1,'readings':75,'withheld':67,'sensitivity_rows':120,'new_sources':3}))


if __name__=='__main__':main()
