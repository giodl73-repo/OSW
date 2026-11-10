"""Observed Agulhas Return band and upstream Agulhas model extent; cloud-only admission."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v18 import load_inventory as previous
from compiled_depth_catalog_view_v19 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v56.json'
FACTS='research/agulhas-system-published-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v55.json'
INVENTORY='research/current-depth-reference-inventory-v56.json'
CONTEXT='agulhas-system-observed-band-and-model-extent-v1'
ADDENDUM='research/current-depth-reference-addenda/'+CONTEXT+'.json'
CSV='research/current-depth-reference-addenda/'+CONTEXT+'.csv'
DOIS=['10.1016/S0967-0645(02)00377-6','10.1029/2018JC014333']
OWNERS=['current:agulhas-return','current:agulhas']
REFERENCE_IDS=['agulhas-return-boebel2003-observed-deep-velocity-band','agulhas-zhu2018-ecco2-mean-velocity-extent']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if facts['id']!=CONTEXT or len(facts['cases'])!=2:raise ValueError('Exact context and two sources')
    a,b=facts['cases']
    if [c['source_doi'] for c in facts['cases']]!=DOIS or [c['entity_id'] for c in facts['cases']]!=OWNERS:raise ValueError('No source/current identity swaps')
    if a['source_url']!='https://www7320.nrlssc.navy.mil/pubs/2003/barron4.pdf' or b['source_url']!='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JC014333':raise ValueError('Exact reviewed originals')
    if [c['source_text_excerpt'] for c in facts['cases']]!=['1000-1150 m depth range','1,000-m depth']:raise ValueError('Exact normalized short excerpts')
    reserve(3)
    nums=[[int(x.replace(',','')) for x in re.findall(r'\d[\d,]*',c['source_text_excerpt'])] for c in facts['cases']]
    if nums!=[[1000,1150],[1000]] or a['range_m']!=[1000,1150] or a['approximate_value_m'] is not None or b['range_m'] is not None or b['approximate_value_m']!=1000:raise ValueError('Band distinct from model scalar')
    if a['metric']!='reported_flow_depth_band' or b['metric']!='reported_model_mean_current_vertical_extent' or a['evidence_kind']!='published_observed_float_velocity_band' or b['evidence_kind']!='published_ecco2_model_mean_velocity_extent':raise ValueError('Observation/model provenance distinct')
    if a['reported_period_years']!=[1997,1999] or b['reported_period_years']!=[1993,2016] or a['source_velocity_cutoff_m_s'] is not None or b['source_velocity_cutoff_m_s']!=0.1 or a['model_name'] is not None or b['model_name']!='ECCO2_cube92':raise ValueError('Exact periods/model/threshold roles')
    if any(facts['eligibility'].values()) or facts['new_provider_field_requests']!=0 or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False:raise ValueError('No physical or custody promotion')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[]
    for i,c in enumerate(facts['cases']):
        rows.append({'id':REFERENCE_IDS[i],'entity_id':c['entity_id'],'metric':c['metric'],'unit':'m','range_m':copy.deepcopy(c['range_m']),'approximate_value_m':c['approximate_value_m'],'upper_bound_m':None,'lower_bound_m':None,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'phase_label':None,'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'source_doi':c['source_doi'],'source_url':c['source_url'],'source_citation':c['source_citation'],'source_locator':c['source_locator'],'source_file':FACTS,'source_sha256':digest,'source_pointer':'/cases/'+str(i),'source_context_id':CONTEXT,'source_definition':c['definition'],'evidence_kind':c['evidence_kind'],'temporal_scope':c['temporal_scope'],'reported_period_years':copy.deepcopy(c['reported_period_years']),'site_scope':c['site_scope'],'vertical_datum':'author_reported_depth_positive_down_datum_not_independently_qualified','qualification':c['qualification'],'source_velocity_cutoff_m_s':c['source_velocity_cutoff_m_s'],'model_name':c['model_name'],'range_is_seasonal_extrema':False,'depth_band_endpoints_are_current_edges':False,'original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=2:raise ValueError('Two distinct owners and source descriptors')
    for i,(row,c) in enumerate(zip(rows,facts['cases'])):
        fields=['entity_id','metric','range_m','approximate_value_m','source_doi','source_url','source_citation','source_locator','evidence_kind','reported_period_years','temporal_scope','site_scope','source_velocity_cutoff_m_s','model_name','qualification']
        if row['id']!=REFERENCE_IDS[i] or row['unit']!='m' or any(row[k]!=c[k] for k in fields) or row['source_definition']!=c['definition'] or row['source_pointer']!='/cases/'+str(i):raise ValueError('Exact source-owner-value-method binding')
        if any(row[k] is not None for k in ['upper_bound_m','lower_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m','phase_label','calendar_months','observed_period','same_source_width_reference_id']):raise ValueError('No edge,thickness,season,date or width promotion')
        if any(row[k] is not False for k in facts['eligibility']) or any(row[k] is not False for k in ['range_is_seasonal_extrema','depth_band_endpoints_are_current_edges','original_source_bytes_verified','original_source_pixels_inspected']):raise ValueError('No physical or custody promotion')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=938 or len(before['records'])!=111 or not set(OWNERS)<={r['entity_id'] for r in before['records']}:raise ValueError('Exact938predecessor and accepted owners')
    if CONTEXT in before['source_contexts'] or any(any(doi in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for doi in DOIS) for r in before['evidence']):raise ValueError('Duplicate source')
    rows=references(facts,digest)
    if set(REFERENCE_IDS)&{r['id'] for r in before['evidence']}:raise ValueError('Duplicate reference')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':940,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':4,'m':936}:raise ValueError('Two different owner descriptors only')
    return out

def main():
    start=float(os.environ['OSW_AGULHAS_SYSTEM_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v56';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    def reserve(count):
        if query.ledger['reserved_numeric_tokens']+count>query.numeric_cap:raise ValueError('Prospective excerpt numeric cap')
        query.ledger['reserved_numeric_tokens']+=count;query.ledger['new_numeric_tokens']+=count;query.ledger['primary_excerpt_numeric_conversions_reserved']=count;save(query.ledger)
    piece=lambda p,b:{'file':p,'bytes':len(b),'sha256':sha(b)}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            raw_facts=reader(FACTS);facts=json.loads(raw_facts);verify_facts(facts,reserve)
            raw_prior=reader(PREVIOUS);before=previous(json.loads(raw_prior),reader);after=assemble(before,facts,sha(raw_facts));rows=references(facts,sha(raw_facts))
            addendum={'schema':'osw.agulhas-system-published-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v56','status':'PINNED_REFERENCES_WITH_AGULHAS_RETURN_OBSERVED_BAND_AND_AGULHAS_MODEL_EXTENT','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v56','status':'DISTINCT_OBSERVED_RETURN_FLOW_BAND_AND_UPSTREAM_MODEL_EXTENT_ADMITTED','interpretation':'Observed return-current deep flow band distinct from upstream Agulhas model mean extent;neither physical bottom nor seasonal extrema or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-2]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.agulhas-system-published-depth-admission-result.v1','status':'TWO_DISTINCT_OWNER_DESCRIPTORS_ADMITTED_938_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
