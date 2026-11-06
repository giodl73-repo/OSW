"""Four section/snapshot model depth extents, cloud-only admission."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v12 import load_inventory as previous
from compiled_depth_catalog_view_v14 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v51.json'
FACTS='research/halo2014-semc-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v49.json'
INVENTORY='research/current-depth-reference-inventory-v51.json'
CONTEXT='halo2014-semc-mean-and-snapshot-depths-v1'
ADDENDUM='research/current-depth-reference-addenda/'+CONTEXT+'.json'
CSV='research/current-depth-reference-addenda/'+CONTEXT+'.csv'
DOI='10.1002/2014JC009820'
URL='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014JC009820'
OWNER='current:southern-east-madagascar'
SCOPE='selected_primary_publisher_html_methods_and_vertical_structure_results'
EXPECTED=[('mean-25s',1800,'seven_year_mean',0,'latitude_25S_longitude_47.5E_to_50E'),('mean-45e',1000,'seven_year_mean',1,'longitude_45E_from_madagascar_shelf_to_30S'),('snapshot-sep19-y10',1500,'model_year_10_september_19',2,'southeast_madagascar_cyclone_inshore_edge'),('snapshot-apr9-y7',1500,'model_year_7_april_9',2,'southeast_madagascar_anticyclone_interaction')]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'],facts['review_scope'])!=(DOI,URL,OWNER,SCOPE):raise ValueError('Exact primary source and accepted owner')
    if facts['source_text_excerpts']!=['1800 m','1000 m','1500 m']:raise ValueError('Three short primary numeric excerpts')
    reserve(3)
    values=[int(text.split()[0]) for text in facts['source_text_excerpts']]
    if len(facts['reported_rows'])!=4:raise ValueError('Four section/snapshot contexts')
    for row,(suffix,value,phase,excerpt,site) in zip(facts['reported_rows'],EXPECTED):
        if (row['id'],row['depth_m'],row['phase'],row['excerpt_index'],row['site_scope'])!=('semc-halo2014-'+suffix,value,phase,excerpt,site) or row['depth_m']!=values[excerpt]:raise ValueError('Exact value, phase, section and reused excerpt')
    if any(facts['eligibility'].values()) or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False or facts['new_provider_field_requests']!=0:raise ValueError('No physical or custody promotion')
    if facts['source_model']!={'name':'SWIM_ROMS','horizontal_grid_degrees':0.2,'vertical_sigma_layers':45,'run_years':10,'spinup_years':3,'output_averaging_days':2,'mean_figure_caption_years':7,'exact_mean_model_year_indices_resolved':False}:raise ValueError('Exact model basis and unresolved mean indices')
    if facts['source_depth_cutoff_rule'] is not None or facts['model_underrepresents_EMUC'] is not True or facts['seasonal_range_from_sections_allowed'] is not False:raise ValueError('No invented cutoff, undercurrent repair or seasonal range')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[]
    for i,source in enumerate(facts['reported_rows']):
        rows.append({'id':source['id'],'entity_id':OWNER,'metric':'reported_model_mean_current_vertical_extent' if i<2 else 'reported_model_snapshot_current_vertical_extent','unit':'m','approximate_value_m':source['depth_m'],'range_m':None,'upper_bound_m':None,'lower_bound_m':None,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'phase_label':source['phase'],'calendar_months':None,'observed_period':None,'model_year_is_calendar_year':False,'same_source_width_reference_id':None,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':source['locator'],'source_file':FACTS,'source_sha256':digest,'source_pointer':'/reported_rows/'+str(i),'source_context_id':CONTEXT,'source_definition':'Author-reported approximate vertical extent in a model mean section or selected model snapshot; no independently reconstructed boundary.','temporal_scope':source['temporal_scope'],'site_scope':source['site_scope'],'evidence_kind':'manually_reviewed_primary_model_reported_vertical_extent','source_review_scope':SCOPE,'source_model':copy.deepcopy(facts['source_model']),'source_depth_cutoff_rule':None,'model_underrepresents_EMUC':True,'vertical_datum':'author_model_depth_positive_down_below_surface_datum_not_independently_qualified','qualification':'Mean-field extent is not mean instantaneous boundary. Separate geography and selected eddy-interaction model snapshots cannot form seasonal extrema, annual uncertainty or continuous route profile. Published comparison observations are not new velocity profiles.','original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=4 or len({r['id'] for r in rows})!=4:raise ValueError('Four distinct descriptors')
    for i,(row,(suffix,value,phase,excerpt,site)) in enumerate(zip(rows,EXPECTED)):
        if (row['id'],row['entity_id'],row['approximate_value_m'],row['phase_label'],row['site_scope'],row['metric'])!=('semc-halo2014-'+suffix,OWNER,value,phase,site,'reported_model_mean_current_vertical_extent' if i<2 else 'reported_model_snapshot_current_vertical_extent'):raise ValueError('Exact section, mean versus snapshot and current identity')
        if any(row[k] is not None for k in ['range_m','upper_bound_m','lower_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m','calendar_months','observed_period','same_source_width_reference_id','source_depth_cutoff_rule']):raise ValueError('No boundary, seasonal, width or date promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['model_year_is_calendar_year'] is not False or row['original_source_pixels_inspected'] is not False or row['original_source_bytes_verified'] is not False:raise ValueError('No physical, custody or calendar promotion')
        if row['source_model']!=facts['source_model'] or row['model_underrepresents_EMUC'] is not True or row['source_doi']!=DOI or row['source_url']!=URL or row['source_pointer']!='/reported_rows/'+str(i):raise ValueError('Exact model/provenance limitations')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=928 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact predecessor and accepted owner')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate study')
    rows=references(facts,digest)
    if {r['id'] for r in rows}&{e['id'] for e in before['evidence']}:raise ValueError('Duplicate reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':932,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':930}:raise ValueError('Four model descriptors only')
    return out

def main():
    start=float(os.environ['OSW_SEMC_MODEL_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v51';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=13821,prior_bytes=5875559);reader=query.reader(lambda p:(ROOT/p).read_bytes())
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
            addendum={'schema':'osw.halo2014-semc-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v51','status':'PINNED_REFERENCES_WITH_SEMC_MODEL_SECTION_AND_SNAPSHOT_EXTENTS','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v51','status':'FOUR_SEMC_MODEL_DESCRIPTORS_ADMITTED','interpretation':'Four model section and snapshot extents preserve geographic and temporal contexts; no observed physical bottom or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-4]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.halo2014-semc-depth-admission-result.v1','status':'FOUR_MODEL_DESCRIPTORS_ADMITTED_928_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
