"""Admit two manually reviewed published PGW descriptors, preserving v45."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v8 import load_inventory as previous
from compiled_depth_catalog_view_v3 import refresh
from compiled_depth_catalog_view_v9 import load_inventory
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,checked_piece
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v46.json'
FACTS='research/xie2019-redsea-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v45.json'
INVENTORY='research/current-depth-reference-inventory-v46.json'
ADDENDUM='research/current-depth-reference-addenda/xie2019-redsea-published-depths-v1.json'
CSV='research/current-depth-reference-addenda/xie2019-redsea-published-depths-v1.csv'
CONTEXT='xie2019-redsea-phase-and-model-mean-depths'
DOI='10.1029/2018JC014478'
OWNER='current:red-sea-saline-overflow'
URL='https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2018JC014478'
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

EXPECTED=[([-50],'northern_side_of_hanish_sill','winter_two_layer_pattern','1995-05'),([-100],'perim_narrows','winter_two_layer_pattern','1995-05'),([-100],'northern_side_of_hanish_sill','summer_three_layer_pattern','1996-07'),([-150,-200],'perim_narrows','summer_three_layer_pattern','1996-07'),([50],'hanish_sill_section',None,None)]

def verify_facts(facts,reserve):
    if facts['source_doi']!=DOI or facts['source_url']!=URL or facts['entity_id']!=OWNER or facts['id']!='xie2019-redsea-published-depths-v1':raise ValueError('Exact primary source and owner')
    if any(facts['eligibility'].values()) or facts['original_html_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False or facts['closed_native_cases_reopened'] is not False or facts['new_native_or_provider_requests']!=0:raise ValueError('Manual HTML only,no promotion/native replay')
    texts=facts['source_text_excerpts'];rows=facts['reported_rows']
    if len(texts)!=5 or len(rows)!=5 or sum(len(t.split()) for t in texts)!=17 or facts['source_text_excerpts_total_words']!=17:raise ValueError('Five short17wordexcerpts')
    reserve(sum(len(re.findall(r'\d+(?:\.\d+)?',t)) for t in texts))
    templates=[r'about \u2212(\d+) m',r'approximately \u2212(\d+) m',r'approximately \u2212(\d+) m',r'between \u2212(\d+) and \u2212(\d+) m',r'approximately (\d+) m']
    for i,(text,row,expected) in enumerate(zip(texts,rows,EXPECTED)):
        match=re.fullmatch(templates[i],text)
        if match is None:raise ValueError('Exact published metre-coordinate prose')
        signed=[int(v)*(-1 if i<4 else 1) for v in match.groups()]
        if signed!=expected[0] or row['source_signed_depths_m']!=signed or (row['site'],row['phase'],row['source_survey_month_context'])!=expected[1:]:raise ValueError('Exact value/sign/site/phase/campaign')
        if row['metric']!=('reported_current_associated_halocline_depth_band' if i<4 else 'net_section_transport_zero_depth') or row['role']!=('hydrographic_interface_comparison' if i<4 else 'zero_of_time_mean_model_transport_profile'):raise ValueError('Hydrography versus mean transport role')
    if facts['source_occupation_dates'] is not None or facts['source_hydrographic_boundary_threshold'] is not None or facts['mean_definition']!='zero_of_time_mean_transport_profile_not_mean_of_instantaneous_interface_depths':raise ValueError('No invented dates/criterion/averaging switch')

def references(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest) or facts['entity_id']!=OWNER or any(facts['eligibility'].values()):raise ValueError('Exact hash/owner/no promotion')
    rows=[]
    for i,source in enumerate(facts['reported_rows']):
        values=[abs(v) for v in source['source_signed_depths_m']]
        rows.append({'id':source['id'],'entity_id':OWNER,'metric':source['metric'],'unit':'m','approximate_value_m':values[0] if len(values)==1 else None,'range_m':values if len(values)>1 else None,'range_interpretation':'Approximate reported interface depth span,not thickness/uncertainty/annualrange.' if len(values)>1 else None,'upper_boundary_m':None,'lower_boundary_m':None,'lower_bound_m':None,'upper_bound_m':None,'lower_bound_exclusive':False,'upper_bound_exclusive':False,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':source['phase'],'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'site_scope':source['site'],'source_campaign_month_context':source['source_survey_month_context'],'source_quantity_role':source['role'],'source_signed_depths_m':copy.deepcopy(source['source_signed_depths_m']),'vertical_datum':facts['vertical_datum'],'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],'source_definition':source['role']+';'+facts['mean_definition'] if i==4 else 'Reported lower salinity interface in regional model-observation comparison,notvelocityboundary/currentthickness.','source_context_id':CONTEXT,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':source['locator'],'source_file':FACTS,'source_pointer':'/reported_rows/'+str(i),'source_sha256':digest,'evidence_kind':'manually_reviewed_primary_published_model_mean_transport_descriptor' if i==4 else 'manually_reviewed_primary_published_hydrographic_model_observation_comparison','source_original_html_bytes_verified':False,'source_original_pixels_inspected':False,'qualification':'Different-yearphasecomparisonsnotannualrange;meantransportzeroisboundaryofmean,notmeaninstantaneousboundaries. No source interface thickness/currentbottom/localvelocityzero/independentcohort/volume inferred.',**copy.deepcopy(facts['eligibility'])})
    validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=5 or len({r['id'] for r in rows})!=5:raise ValueError('Five unique source descriptors')
    for i,(row,source,expected) in enumerate(zip(rows,facts['reported_rows'],EXPECTED)):
        values=[abs(v) for v in expected[0]]
        if row['id']!=source['id'] or row['entity_id']!=OWNER or row['unit']!='m' or row['metric']!=source['metric'] or row['source_quantity_role']!=source['role'] or row['site_scope']!=expected[1] or row['phase_label']!=expected[2] or row['source_campaign_month_context']!=expected[3] or row['source_signed_depths_m']!=expected[0]:raise ValueError('Exact quantity/site/phase/campaign/sign')
        if row['approximate_value_m']!=(values[0] if len(values)==1 else None) or row['range_m']!=(values if len(values)>1 else None):raise ValueError('Source depth,not thickness/pressure')
        if any(row[k] is not None for k in ['upper_boundary_m','lower_boundary_m','lower_bound_m','upper_bound_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id']):raise ValueError('No physicalboundary/thickness/error/annual/date promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['source_original_html_bytes_verified'] is not False or row['source_original_pixels_inspected'] is not False:raise ValueError('No physical/custody/independence promotion')
        if row['source_doi']!=DOI or row['source_url']!=URL or row['source_file']!=FACTS or row['source_context_id']!=CONTEXT or row['source_pointer']!='/reported_rows/'+str(i) or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']) or row['vertical_datum']!=facts['vertical_datum']:raise ValueError('Exact source/facts provenance')
        if i==4 and facts['mean_definition'] not in row['source_definition']:raise ValueError('Zero of time mean is not mean of zeroes')

def assemble(before,facts,facts_sha):
    if before['counts']['depth_references']!=915 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact 915-reference/111-identity predecessor')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate prior source study or context')
    rows=references(facts,facts_sha);old={r['id'] for r in before['evidence']}
    if any(r['id'] in old for r in rows):raise ValueError('Duplicate existing reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['evidence'][:-5]!=before['evidence'] or out.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Every old reference and canonical calendar preserved')
    if out['counts']!={'identities':111,'depth_references':920,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':918}:raise ValueError('Two scoped references only, no physical/identity coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_XIE_REDSEA_ADMISSION_START'])
    def stop(*a):raise TimeoutError('Shared60second source-test/admission deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline manual publication facts and admitted catalog only'))
    out=ROOT/'current-depth-reference-inventory-v46';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    def reserve(n):
        if query.ledger['reserved_numeric_tokens']+n>query.numeric_cap:raise ValueError('Prospective primary-excerpt numeric cap before conversion')
        query.ledger['reserved_numeric_tokens']+=n;query.ledger['new_numeric_tokens']+=n;query.ledger['primary_excerpt_numeric_conversions_reserved']=n;save(query.ledger)
    piece=lambda p,b:{'file':p,'bytes':len(b),'sha256':sha(b)}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            facts_raw=reader(FACTS);facts=json.loads(facts_raw);verify_facts(facts,reserve)
            prior_raw=reader(PREVIOUS);before=previous(json.loads(prior_raw),reader);after=assemble(before,facts,sha(facts_raw))
            rows=references(facts,sha(facts_raw))
            addendum={'schema':'osw.xie2019-redsea-published-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,facts_raw),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v46','status':'PINNED_REFERENCES_WITH_XIE2019_REDSEA_REGIONAL_PHASE_AND_MODEL_MEAN_DEPTHS','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},
                'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v46','status':'FIVE_MANUALLY_REVIEWED_PRIMARY_REDSEA_DEPTH_REFERENCES_ADMITTED','interpretation':'Fourregionalhydrographicphase/siteinterfacesplusseparatemodelmeantransportzero. Different1995/1996campaignsnotannualrange;boundaryofmeannotmeanboundary;nocurrentthickness/physicalbottom/volume. ManualprimaryHTMLtextreview.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete actual JSON/CSV/catalog roundtrip and calendar preservation')
            if any({k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'} for old,new in zip(before['records'],final['records'])):raise ValueError('All non-reference owner fields preserved')
            result={'schema':'osw.xie2019-redsea-admission-result.v1','status':'FIVE_QUALIFIED_PUBLISHED_REFERENCES_ADMITTED_915_PRIOR_PRESERVED','counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_reference_ids':[r['id'] for r in rows],
                'new_native_ocean_values':0,'new_provider_requests':0,'original_pdf_bytes_or_pixels_verified':False,'manual_primary_published_text_review':True,'new_reference_records_not_new_OSW_observations':5,'runtime_changed':False,'full_goal_complete':False}
            result_raw=encode(result)
            if json.loads(result_raw)!=result:raise ValueError('Full admission result roundtrip')
        total=sum(len(v) for v in pieces.values())+len(result_raw)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(result_raw)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
