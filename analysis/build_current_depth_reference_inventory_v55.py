"""Two dated normalized Malvinas jet descriptors; cloud-only admission."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v17 import load_inventory as previous
from compiled_depth_catalog_view_v18 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v55.json'
FACTS='research/krechik2020-malvinas-jet-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v54.json'
INVENTORY='research/current-depth-reference-inventory-v55.json'
CONTEXT='krechik2020-malvinas-normalized-jet-depths-v1'
ADDENDUM='research/current-depth-reference-addenda/'+CONTEXT+'.json'
CSV='research/current-depth-reference-addenda/'+CONTEXT+'.csv'
DOI='10.2205/2020ES000715'
URL='https://rjes.wdcb.ru/v20/2020ES000715/2020ES000715.html'
OWNER='current:falkland'
SCOPE='primary_journal_html_methods2_2_2_3_results3_2_and_discussion'
REFERENCE_IDS=['falkland-krechik2020-main-normalized-core-extent','falkland-krechik2020-onshore-normalized-jet-band']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'],facts['review_scope'],facts['id'])!=(DOI,URL,OWNER,SCOPE,CONTEXT):raise ValueError('Exact source, owner and context')
    if facts['source_text_excerpt']!='surface to about 400 m;50-480 m depth range':raise ValueError('Exact excerpts')
    reserve(3)
    values=[int(x) for x in re.findall(r'\d+',facts['source_text_excerpt'])]
    if values!=[400,50,480] or facts['main_core_lower_extent_m']!=400 or facts['onshore_jet_depth_band_m']!=[50,480]:raise ValueError('Exact two feature descriptions')
    if facts['source_observed_period']!=['2020-01-12T16:00:00Z','2020-01-12T23:20:00Z'] or facts['lower_boundary_support_resolved'] is not None:raise ValueError('Exact dated section;unresolved support')
    if any(facts['eligibility'].values()) or facts['new_provider_field_requests']!=0 or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False:raise ValueError('No physical or custody promotion')
    if facts['velocity_definition']!='Meridional SADCP velocities normalized by whole-dataset mean;jet Vnorm>1,core Vnorm>2.':raise ValueError('Jet and core thresholds distinct')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    base={'entity_id':OWNER,'unit':'m','upper_bound_m':None,'lower_bound_m':None,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'phase_label':None,'calendar_months':None,'observed_period':copy.deepcopy(facts['source_observed_period']),'same_source_width_reference_id':None,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':'Methods2.2-2.3;Results3.2','source_file':FACTS,'source_sha256':digest,'source_context_id':CONTEXT,'source_definition':facts['velocity_definition'],'evidence_kind':'published_observed_normalized_velocity_jet_structure','source_review_scope':SCOPE,'range_is_seasonal_extrema':False,'source_depth_cutoff_rule':facts['source_depth_cutoff_rule'],'temporal_scope':'One12January2020section;not annual or seasonal extrema.','site_scope':facts['site_scope'],'vertical_datum':'author_reported_depth_below_surface_positive_down_datum_not_independently_qualified','qualification':facts['source_limits'],'lower_boundary_support_resolved':None,'surface_observation_at_zero_m_established':False,'original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])}
    rows=[{**copy.deepcopy(base),'id':REFERENCE_IDS[0],'metric':'core_lower_boundary_depth','range_m':None,'approximate_value_m':facts['main_core_lower_extent_m'],'source_pointer':'/main_core_lower_extent_m','feature_scope':'main_jet_high_velocity_core','normalized_velocity_threshold':2},{**copy.deepcopy(base),'id':REFERENCE_IDS[1],'metric':'reported_flow_depth_band','range_m':copy.deepcopy(facts['onshore_jet_depth_band_m']),'approximate_value_m':None,'source_pointer':'/onshore_jet_depth_band_m','feature_scope':'onshore_jet_without_explicit_core','normalized_velocity_threshold':1}]
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=2:raise ValueError('Two distinct feature descriptors')
    expected=[(REFERENCE_IDS[0],'core_lower_boundary_depth',None,400,'main_jet_high_velocity_core',2,'/main_core_lower_extent_m'),(REFERENCE_IDS[1],'reported_flow_depth_band',[50,480],None,'onshore_jet_without_explicit_core',1,'/onshore_jet_depth_band_m')]
    for row,exp in zip(rows,expected):
        if tuple(row[k] for k in ['id','metric','range_m','approximate_value_m','feature_scope','normalized_velocity_threshold','source_pointer'])!=exp or row['entity_id']!=OWNER or row['unit']!='m':raise ValueError('Exact feature/value/threshold binding')
        if any(row[k] is not None for k in ['upper_bound_m','lower_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m','phase_label','calendar_months','same_source_width_reference_id','lower_boundary_support_resolved']):raise ValueError('No physical edges,thickness,season,width or resolved support')
        if row['observed_period']!=['2020-01-12T16:00:00Z','2020-01-12T23:20:00Z']:raise ValueError('Exact observation period')
        if any(row[k] is not False for k in facts['eligibility']) or any(row[k] is not False for k in ['range_is_seasonal_extrema','surface_observation_at_zero_m_established','original_source_bytes_verified','original_source_pixels_inspected']):raise ValueError('No physical,surface or custody promotion')
        if row['evidence_kind']!='published_observed_normalized_velocity_jet_structure' or row['source_definition']!=facts['velocity_definition'] or row['source_depth_cutoff_rule']!=facts['source_depth_cutoff_rule'] or row['source_doi']!=DOI or row['source_url']!=URL:raise ValueError('Exact normalized-velocity provenance')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=936 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact936predecessor and accepted owner')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate source')
    rows=references(facts,digest)
    if set(REFERENCE_IDS)&{r['id'] for r in before['evidence']}:raise ValueError('Duplicate reference')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':938,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':4,'m':934}:raise ValueError('Two scoped jet descriptors only')
    return out

def main():
    start=float(os.environ['OSW_MALVINAS_JET_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v55';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.krechik2020-malvinas-jet-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v55','status':'PINNED_REFERENCES_WITH_TWO_MALVINAS_NORMALIZED_JET_DEPTHS','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v55','status':'TWO_REGIONAL_NORMALIZED_JET_DEPTHS_ADMITTED','interpretation':'Two dated regional normalized jet descriptors;support limits unresolved,no physical bottom,seasonal extrema or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-2]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.krechik2020-malvinas-jet-depth-admission-result.v1','status':'TWO_JET_DESCRIPTORS_ADMITTED_936_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
