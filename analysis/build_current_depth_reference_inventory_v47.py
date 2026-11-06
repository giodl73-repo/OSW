"""Admit two explicitly abstract-reported model descriptors; no native fields."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v9 import load_inventory as previous
from compiled_depth_catalog_view_v10 import load_inventory
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v47.json'
FACTS='research/rahman2024-indian-euc-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v46.json'
INVENTORY='research/current-depth-reference-inventory-v47.json'
ADDENDUM='research/current-depth-reference-addenda/rahman2024-indian-euc-model-depths-v1.json'
CSV='research/current-depth-reference-addenda/rahman2024-indian-euc-model-depths-v1.csv'
CONTEXT='rahman2024-abstract-reported-indian-euc-model-depths'
DOI='10.1038/s41598-024-58464-2'
URL='https://www.nature.com/articles/s41598-024-58464-2'
OWNER='current:indian-equatorial-undercurrent'
EXPECTED=[([50,100],'fall','reported_flow_depth_band'),([100,150],'spring','core_depth')]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encode=lambda value:(json.dumps(value,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def verify_facts(facts,reserve):
    if (facts['source_doi'],facts['source_url'],facts['entity_id'])!=(DOI,URL,OWNER):raise ValueError('Exact source and current owner')
    if facts['review_scope']!='publisher_abstract_and_opening_model_configuration_only' or facts['full_results_reviewed'] is not False or facts['original_source_bytes_verified'] is not False:raise ValueError('Partial review cannot become full source custody')
    if any(facts['eligibility'].values()) or facts['new_provider_field_requests']!=0:raise ValueError('No observation, geometry or native-field promotion')
    texts=facts['source_text_excerpts']
    if len(texts)!=2:raise ValueError('Two source excerpts')
    reserve(sum(len(re.findall(r'\d+',text)) for text in texts))
    for text,row,expected in zip(texts,facts['reported_rows'],EXPECTED):
        match=re.fullmatch(r'between (\d+) and (\d+) m',text)
        if not match or [int(x) for x in match.groups()]!=expected[0] or (row['depths_m'],row['phase'],row['metric'])!=expected:raise ValueError('Exact published band, phase and metric')
        if row['quantity_role']!=('reported_model_flow_depth_band' if expected[1]=='fall' else 'reported_model_core_depth_band'):raise ValueError('Fall flow band is not a spring core band')
    if len(facts['reported_rows'])!=2 or facts['source_analysis_averaging_window'] is not None or facts['source_exact_section_coordinates'] is not None:raise ValueError('No invented sampling or spatial support')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Facts hash required')
    rows=[]
    for index,(source,expected) in enumerate(zip(facts['reported_rows'],EXPECTED)):
        rows.append({'id':source['id'],'entity_id':OWNER,'metric':expected[2],'unit':'m','approximate_value_m':None,'range_m':copy.deepcopy(expected[0]),'range_interpretation':'Author-reported model depth band;not thickness,confidence interval or annual extrema.','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':expected[1],'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':'Publisher abstract, final Indian Equatorial Undercurrent comparison.','source_file':FACTS,'source_sha256':digest,'source_pointer':'/reported_rows/'+str(index),'source_context_id':CONTEXT,'source_definition':source['quantity_role'],'evidence_kind':'manually_reviewed_primary_publisher_abstract_reported_model_descriptor','source_review_scope':facts['review_scope'],'model_experiment_context':facts['model_experiment_context'],'source_analysis_averaging_window':None,'source_exact_section_coordinates':None,'vertical_datum':'author_reported_metres_depth_datum_not_independently_qualified','geographic_scope':'Indian Equatorial Undercurrent;exact section and matched route support not established by reviewed abstract.','temporal_scope':'Authors spring/fall labels in a 1992-2005 model experiment;averaging window and exact months not verified.','qualification':'Model descriptor from a partial primary review;not an OSW observation,physical current bottom,connected layer,annual range or co-located width/volume.','original_source_bytes_verified':False,'original_source_pixels_inspected':False,**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=2 or len({r['id'] for r in rows})!=2:raise ValueError('Exactly two unique references')
    for index,(row,expected) in enumerate(zip(rows,EXPECTED)):
        if (row['entity_id'],row['unit'],row['metric'],row['range_m'],row['phase_label'])!=(OWNER,'m',expected[2],expected[0],expected[1]):raise ValueError('Exact owner, metric and phase')
        if row['source_review_scope']!='publisher_abstract_and_opening_model_configuration_only' or row['evidence_kind']!='manually_reviewed_primary_publisher_abstract_reported_model_descriptor':raise ValueError('Preserve abstract/model evidence role')
        if any(row[key] is not None for key in ['approximate_value_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id','source_analysis_averaging_window','source_exact_section_coordinates']):raise ValueError('No physical, annual, date or geometry promotion')
        if any(row[key] is not False for key in facts['eligibility']) or row['original_source_bytes_verified'] is not False or row['original_source_pixels_inspected'] is not False:raise ValueError('No observation or custody promotion')
        if row['source_doi']!=DOI or row['source_url']!=URL or row['source_pointer']!='/reported_rows/'+str(index) or row['source_context_id']!=CONTEXT:raise ValueError('Exact provenance')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=920 or len(before['records'])!=111:raise ValueError('Exact 920-reference predecessor')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate source context or study')
    rows=references(facts,digest)
    if any(r['id'] in {e['id'] for e in before['evidence']} for r in rows):raise ValueError('Duplicate reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':922,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':920}:raise ValueError('Only two metre references, no physical coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_RAHMAN_EUC_ADMISSION_START'])
    def stop(*args):raise TimeoutError('Shared 60-second test/admission limit')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-reference-inventory-v47';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.rahman2024-indian-euc-model-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v47','status':'PINNED_REFERENCES_WITH_PARTIALLY_REVIEWED_PUBLISHER_ABSTRACT_MODEL_DEPTHS','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v47','status':'TWO_ABSTRACT_REPORTED_MODEL_DEPTH_BANDS_ADMITTED','interpretation':'Fall flow-depth band versus spring core-depth band;partial publisher abstract review,not observations,current bottom,annual range or volume.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-2]!=before['evidence'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete JSON/CSV catalog and prior-reference parity')
            for old,new in zip(before['records'],final['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Every non-reference owner field preserved')
            result={'schema':'osw.rahman2024-indian-euc-depth-admission-result.v1','status':'TWO_MODEL_DESCRIPTORS_ADMITTED_920_PRIOR_PRESERVED','counts':after['counts'],'new_reference_ids':[r['id'] for r in rows],'new_observations':0,'new_provider_field_requests':0,'full_results_reviewed':False,'whole_route_profiles':0,'physical_volumes':0,'runtime_changed':False,'full_goal_complete':False};raw_result=encode(result)
            if json.loads(raw_result)!=result:raise ValueError('Full result roundtrip')
        total=sum(map(len,pieces.values()))+len(raw_result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(raw_result)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
