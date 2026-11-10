"""Two local, mixed-circulation monsoon depth descriptors; cloud only."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v11 import load_inventory as previous
from compiled_depth_catalog_view_v12 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v49.json'
FACTS='research/wijesekera2016-monsoon-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v48.json'
INVENTORY='research/current-depth-reference-inventory-v49.json'
CONTEXT='wijesekera2016-monsoon-local-mean-depths-v1'
ADDENDUM='research/current-depth-reference-addenda/'+CONTEXT+'.json'
CSV='research/current-depth-reference-addenda/'+CONTEXT+'.csv'
DOI='10.5670/oceanog.2016.44'
URL='https://tos.org/oceanography/assets/docs/29-2_wijesekera.pdf'
OWNER='current:monsoon'
SCOPE='selected_primary_pdf_methods_results_and_conclusions_text'
EXPECTED=[('winter_mean_upper_extent','reported_mean_flow_upper_layer_extent',100,None),('summer_meridional_maximum','reported_meridional_velocity_core_depth_band',None,[50,100])]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'],facts['review_scope'])!=(DOI,URL,OWNER,SCOPE):raise ValueError('Exact source, existing owner and review scope')
    if facts['source_text_excerpts']!=['confined to upper 100 m','50\u2013100 m depth']:raise ValueError('Exact primary excerpts')
    reserve(3)
    values=[int(x) for text in facts['source_text_excerpts'] for x in re.findall(r'\d+',text)]
    if values!=[100,50,100] or len(facts['reported_rows'])!=2:raise ValueError('Three reserved conversions, two descriptors')
    for row,expected in zip(facts['reported_rows'],EXPECTED):
        if (row['phase'],row['metric'],row['upper_bound_m'],row['range_m'])!=expected:raise ValueError('Exact phase, metric and reported coordinate')
    if any(facts['eligibility'].values()) or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False:raise ValueError('No custody or physical promotion')
    if facts['eddy_contamination_resolved'] is not False or facts['new_provider_field_requests']!=0:raise ValueError('Mixed circulation remains unresolved')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[]
    for i,source in enumerate(facts['reported_rows']):
        rows.append({'id':source['id'],'entity_id':OWNER,'metric':source['metric'],'unit':'m','approximate_value_m':None,'range_m':copy.deepcopy(source['range_m']),'upper_bound_m':source['upper_bound_m'],'lower_bound_m':None,'upper_bound_exclusive':False,'lower_bound_exclusive':False,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'phase_label':source['phase'],'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':source['locator'],'source_file':FACTS,'source_sha256':digest,'source_pointer':'/reported_rows/'+str(i),'source_context_id':CONTEXT,'source_definition':source['definition'],'temporal_scope':source['temporal_scope'],'site_scope':source['site_scope'],'evidence_kind':'manually_reviewed_primary_observation_based_local_mixed_circulation_descriptor','source_review_scope':SCOPE,'source_processing':copy.deepcopy(facts['source_processing']),'source_cohort_context':facts['source_cohort_context'],'eddy_contamination_resolved':False,'source_exact_depth_cutoff_criterion':None,'vertical_datum':'author_reported_depth_below_surface_positive_down_not_independently_qualified','qualification':'Regional monsoon-phase descriptor including unresolved eddy contributions. Winter extent of mean flow is not mean instantaneous boundary; summer meridional maximum is not total-speed core or current bottom. Not transferable to a Sri Lanka reference route or 2016 width campaign.','original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=2 or len({r['id'] for r in rows})!=2:raise ValueError('Two unique descriptors')
    for i,(row,expected) in enumerate(zip(rows,EXPECTED)):
        if (row['phase_label'],row['metric'],row['upper_bound_m'],row['range_m'])!=expected:raise ValueError('Exact mean extent versus component core')
        if row['entity_id']!=OWNER or row['source_doi']!=DOI or row['source_url']!=URL or row['source_pointer']!='/reported_rows/'+str(i):raise ValueError('Exact provenance and owner')
        if any(row[k] is not None for k in ['approximate_value_m','lower_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m','calendar_months','observed_period','same_source_width_reference_id','source_exact_depth_cutoff_criterion']):raise ValueError('No boundary, seasonal range or width join promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['eddy_contamination_resolved'] is not False or row['original_source_pixels_inspected'] is not False or row['original_source_bytes_verified'] is not False:raise ValueError('No physical or custody promotion')
        for key in ['source_processing','source_review_scope']:
            if row[key]!=(facts['source_processing'] if key=='source_processing' else SCOPE):raise ValueError('Preserve processing and review scope')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=926 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact predecessor and existing owner')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate study')
    rows=references(facts,digest)
    if {r['id'] for r in rows}&{e['id'] for e in before['evidence']}:raise ValueError('Duplicate reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':928,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':926}:raise ValueError('Two descriptors only')
    return out

def main():
    start=float(os.environ['OSW_MONSOON_OBS_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v49';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.wijesekera2016-monsoon-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v49','status':'PINNED_REFERENCES_WITH_LOCAL_MONSOON_PHASE_DEPTHS','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v49','status':'TWO_LOCAL_MIXED_MONSOON_DEPTH_DESCRIPTORS_ADMITTED','interpretation':'Two local mixed-circulation monsoon descriptors preserve mean-flow versus meridional-core meaning; no physical bottom or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-2]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.wijesekera2016-monsoon-depth-admission-result.v1','status':'TWO_LOCAL_DESCRIPTORS_ADMITTED_926_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
