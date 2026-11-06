"""One dated Antarctic coastal component velocity scale; cloud-only admission."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v19 import load_inventory as previous
from compiled_depth_catalog_view_v20 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v57.json'
FACTS='research/moffat2008-antarctic-coastal-velocity-scale-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v56.json'
INVENTORY='research/current-depth-reference-inventory-v57.json'
CONTEXT='moffat2008-antarctic-coastal-velocity-scale-v1'
ADDENDUM='research/current-depth-reference-addenda/'+CONTEXT+'.json'
CSV='research/current-depth-reference-addenda/'+CONTEXT+'.csv'
DOI='10.1016/j.dsr2.2007.10.003'
URL='https://www.vliz.be/imisdocs/publications/280146.pdf'
OWNER='current:antarctic-coastal'
SCOPE='initial_primary_pdf_text_methods_section2_and_results4_1_through_opening4_2'
REFERENCE_ID='antarctic-coastal-moffat2008-section-i-velocity-decay-scale'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'],facts['review_scope'],facts['id'])!=(DOI,URL,OWNER,SCOPE,CONTEXT):raise ValueError('Exact source, accepted regional owner and context')
    if facts['source_text_excerpt']!='approximately 80 m':raise ValueError('Exact short excerpt')
    reserve(1)
    value=int(re.findall(r'\d+',facts['source_text_excerpt'])[0])
    if value!=80 or facts['approximate_value_m']!=80:raise ValueError('Exact reported scale')
    if facts['source_observed_period']!=['2001-06-01','2001-06-01'] or facts['source_depth_cutoff_rule'] is not None or facts['decay_function_or_e_folding_definition'] is not None or facts['scale_is_current_bottom'] is not False:raise ValueError('Dated scale,not e-folding law or bottom')
    if any(facts['eligibility'].values()) or facts['new_provider_field_requests']!=0 or facts['original_source_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False:raise ValueError('No physical or custody promotion')
    if facts['method']!='Author-reported vertical velocity decay scale inSectionI;ADCP referenced with thermal-wind extrapolation above31m to surface.':raise ValueError('Exact surface treatment')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[{'id':REFERENCE_ID,'entity_id':OWNER,'metric':'reported_vertical_scale_length','unit':'m','range_m':None,'approximate_value_m':facts['approximate_value_m'],'upper_bound_m':None,'lower_bound_m':None,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'phase_label':None,'calendar_months':None,'observed_period':copy.deepcopy(facts['source_observed_period']),'same_source_width_reference_id':None,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':'Section2 firstBIOMAPERparagraph;Section4.1 lastparagraph beforeFig4/printed281/PDF5','source_file':FACTS,'source_sha256':digest,'source_pointer':'/approximate_value_m','source_context_id':CONTEXT,'source_definition':facts['method'],'evidence_kind':'published_observed_section_velocity_decay_scale','source_review_scope':SCOPE,'range_is_seasonal_extrema':False,'source_depth_cutoff_rule':None,'temporal_scope':'1June2001SectionI;not annual or seasonal extrema.','site_scope':facts['site_scope'],'vertical_datum':'author_reported_vertical_scale_length_not_boundary_coordinate','qualification':facts['source_limits'],'scale_is_current_bottom':False,'decay_function_or_e_folding_definition':None,'original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])}]
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=1:raise ValueError('One regional scale')
    row=rows[0]
    if (row['id'],row['entity_id'],row['metric'],row['unit'],row['approximate_value_m'])!=(REFERENCE_ID,OWNER,'reported_vertical_scale_length','m',80):raise ValueError('Exact scale descriptor')
    if any(row[k] is not None for k in ['range_m','upper_bound_m','lower_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','annual_range_m','uncertainty_m','phase_label','calendar_months','same_source_width_reference_id','source_depth_cutoff_rule','decay_function_or_e_folding_definition']):raise ValueError('No physical edges,thickness,season,width or e-folding law')
    if row['observed_period']!=['2001-06-01','2001-06-01']:raise ValueError('Exact observed date')
    if any(row[k] is not False for k in facts['eligibility']) or any(row[k] is not False for k in ['range_is_seasonal_extrema','scale_is_current_bottom','original_source_bytes_verified','original_source_pixels_inspected']):raise ValueError('No physical or custody promotion')
    if row['evidence_kind']!='published_observed_section_velocity_decay_scale' or row['source_definition']!=facts['method'] or row['source_doi']!=DOI or row['source_url']!=URL or row['source_pointer']!='/approximate_value_m':raise ValueError('Exact velocity-scale provenance')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=940 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact940predecessor and accepted owner')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate source')
    rows=references(facts,digest)
    if REFERENCE_ID in {r['id'] for r in before['evidence']}:raise ValueError('Duplicate reference')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':941,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':4,'m':937}:raise ValueError('One regional scale descriptor only')
    return out

def main():
    start=float(os.environ['OSW_ANTARCTIC_SCALE_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v57';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.moffat2008-antarctic-coastal-velocity-scale-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v57','status':'PINNED_REFERENCES_WITH_REGIONAL_ANTARCTIC_COASTAL_VELOCITY_SCALE','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v57','status':'ONE_REGIONAL_ANTARCTIC_COASTAL_VELOCITY_SCALE_ADMITTED','interpretation':'One dated AntarcticPeninsula coastal velocity decay scale;not bottom,e-folding law,seasonal extrema or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-1]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.moffat2008-antarctic-coastal-velocity-scale-admission-result.v1','status':'ONE_VELOCITY_SCALE_ADMITTED_940_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
