"""Admit four published observational depth bounds; no native fields."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v10 import load_inventory as previous
from compiled_depth_catalog_view_v11 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v48.json'
FACTS='research/mukhopadhyay2017-eicc-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v47.json'
INVENTORY='research/current-depth-reference-inventory-v48.json'
ADDENDUM='research/current-depth-reference-addenda/mukhopadhyay2017-eicc-observed-depth-bounds-v1.json'
CSV='research/current-depth-reference-addenda/mukhopadhyay2017-eicc-observed-depth-bounds-v1.csv'
CONTEXT='mukhopadhyay2017-eicc-observed-depth-bounds'
DOI='10.1016/j.csr.2017.08.020'
URL='https://www.codar.com/images/about/2017Mukhopadhyay_CSR.pdf'
OWNER='current:east-india-coastal'
EXPECTED=[(40,'summer_2011_shallow_episodes','reported_vertical_extent','upper',True,False),(40,'october_december_2011_shallow_episodes','reported_vertical_extent','upper',True,False),(100,'february_march_2012_deep_flow','reported_censored_flow_reach','lower',True,False),(100,'winter_deep_intraseasonal_episodes','reported_censored_flow_reach','lower',False,True)]
SCOPE='primary_pdf_text_selected_methods_discussion_conclusions_and_caption'
PROCESSING={'authors_gap_filling_applied':True,'tidal_removal':'TASK2000_periods_at_or_below_one_day','lowpass_cutoff_hours':{'gopalpur':50,'cuddalore':75},'filter':'fourth_order_Butterworth','raw_native_reconstruction_by_OSW':False}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'])!=(DOI,URL,OWNER):raise ValueError('Exact source and current owner')
    if facts['review_scope']!=SCOPE or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False:raise ValueError('Reviewed text cannot become byte/pixel custody')
    if facts['shelf_depth_assignment_conflict_unresolved'] is not True or facts['source_figure_windows_assigned_to_bounds'] is not False or facts['source_exact_section_coordinates'] is not None or facts['source_depth_threshold_criterion'] is not None:raise ValueError('No silent caption repair or invented exact sampling criterion')
    if any(facts['eligibility'].values()) or facts['new_provider_field_requests']!=0:raise ValueError('No physical, geometry or native-field promotion')
    if facts['source_processing']!=PROCESSING:raise ValueError('Preserve authors gap filling and site-dependent filtering')
    texts=facts['source_text_excerpts']
    if len(texts)!=3 or len(facts['reported_rows'])!=4:raise ValueError('Three excerpts and four phase-qualified bounds')
    reserve(sum(len(re.findall(r'\d+',text)) for text in texts))
    values=[]
    for text,template in zip(texts,[r'<(\d+) m',r'beyond (\d+) m',r'\u223c(\d+) m or more']):
        match=re.fullmatch(template,text)
        if not match:raise ValueError('Exact source bound prose')
        values.append(int(match.group(1)))
    for row,expected,excerpt in zip(facts['reported_rows'],EXPECTED,[0,0,1,2]):
        if (row['depth_m'],row['phase'],row['metric'],row['bound_side'],row['exclusive'],row['approximate'])!=expected or row['depth_m']!=values[excerpt] or row['excerpt_index']!=excerpt:raise ValueError('Exact bound value, side, strictness, approximation and phase')
    if facts['reported_rows'][0]['site_scope']!='southeastern_eicc_northern_exception_excluded' or facts['reported_rows'][1]['site_scope']!='southeastern_eicc_northern_exception_excluded' or facts['reported_rows'][2]['site_scope']!='authors_multi_site_shelf_slope_summary_not_station_level_boundary' or facts['reported_rows'][3]['site_scope']!='regional_undated_deep_bursts_not_full_winter_state':raise ValueError('Regional exceptions and station ambiguity must remain')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[]
    for index,(source,expected) in enumerate(zip(facts['reported_rows'],EXPECTED)):
        value,phase,metric,side,exclusive,approximate=expected
        rows.append({'id':source['id'],'entity_id':OWNER,'metric':metric,'unit':'m','approximate_value_m':None,'range_m':None,'lower_bound_m':value if side=='lower' else None,'upper_bound_m':value if side=='upper' else None,'lower_bound_exclusive':exclusive if side=='lower' else False,'upper_bound_exclusive':exclusive if side=='upper' else False,'reported_bound_is_approximate':approximate,'bound_is_hard_measurement_error_limit':False,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':phase,'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'site_scope':source['site_scope'],'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':source['locator'],'source_file':FACTS,'source_sha256':digest,'source_pointer':'/reported_rows/'+str(index),'source_context_id':CONTEXT,'source_definition':'Author-reported observational flow-depth bound,not a digitized profile or a measured physical current bottom.','evidence_kind':'manually_reviewed_primary_observation_based_reported_depth_bound','source_review_scope':SCOPE,'source_processing':copy.deepcopy(facts['source_processing']),'source_cohort_context':facts['source_cohort_context'],'source_exact_section_coordinates':None,'shelf_depth_assignment_conflict_unresolved':True,'source_figure_windows_assigned_to_bound':False,'vertical_datum':'author_reported_depth_below_surface_positive_down_datum_not_independently_qualified','temporal_scope':facts['temporal_scope'],'qualification':'Local and transient observational summary;authors gap filling/filtering retained. No station-by-station boundary,exact episode date,annual extrema,layer thickness or compatible volume.','original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=4 or len({r['id'] for r in rows})!=4:raise ValueError('Four unique phase-qualified descriptors')
    for index,(row,expected,source) in enumerate(zip(rows,EXPECTED,facts['reported_rows'])):
        value,phase,metric,side,exclusive,approximate=expected
        if (row['entity_id'],row['unit'],row['metric'],row['phase_label'])!=(OWNER,'m',metric,phase):raise ValueError('Exact current, metric and phase')
        if (row['lower_bound_m'],row['upper_bound_m'],row['lower_bound_exclusive'],row['upper_bound_exclusive'],row['reported_bound_is_approximate'])!=(value if side=='lower' else None,value if side=='upper' else None,exclusive if side=='lower' else False,exclusive if side=='upper' else False,approximate):raise ValueError('No changed inequality, nominal depth or false exactness')
        if row['site_scope']!=source['site_scope'] or row['shelf_depth_assignment_conflict_unresolved'] is not True or row['source_figure_windows_assigned_to_bound'] is not False or row['source_processing']!=facts['source_processing'] or row['source_review_scope']!=SCOPE:raise ValueError('Preserve geographic exceptions, unresolved caption, processing and text-only review')
        if any(row[key] is not None for key in ['approximate_value_m','range_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id','source_exact_section_coordinates']):raise ValueError('No nominal, thickness, annual or exact-date promotion')
        if any(row[key] is not False for key in facts['eligibility']) or row['original_source_bytes_verified'] is not False or row['original_source_pixels_inspected'] is not False or row['bound_is_hard_measurement_error_limit'] is not False:raise ValueError('No physical, uncertainty or custody promotion')
        if row['source_doi']!=DOI or row['source_url']!=URL or row['source_pointer']!='/reported_rows/'+str(index) or row['source_context_id']!=CONTEXT:raise ValueError('Exact provenance')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=922 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact 922-reference predecessor and known current owner')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate source context or study')
    rows=references(facts,digest)
    if any(r['id'] in {e['id'] for e in before['evidence']} for r in rows):raise ValueError('Duplicate reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':926,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':924}:raise ValueError('Four metre bounds only;no physical coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_EICC_OBS_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v48';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.mukhopadhyay2017-eicc-observed-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v48','status':'PINNED_REFERENCES_WITH_OBSERVATIONAL_EICC_PHASE_DEPTH_BOUNDS','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v48','status':'FOUR_OBSERVATION_BASED_REPORTED_DEPTH_BOUNDS_ADMITTED','interpretation':'Four author-reported observational bounds retain inequality,phase,regional exceptions and unresolved station assignment;no current bottom,annual range or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-4]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.mukhopadhyay2017-eicc-depth-admission-result.v1','status':'FOUR_OBSERVATION_BASED_DESCRIPTORS_ADMITTED_922_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
