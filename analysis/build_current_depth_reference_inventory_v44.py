"""Admit two manually reviewed published PGW descriptors, preserving v43."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v6 import load_inventory as previous
from compiled_depth_catalog_view_v3 import refresh
from compiled_depth_catalog_view_v7 import load_inventory
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,checked_piece
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v44.json'
FACTS='research/johns2003-hormuz-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v43.json'
INVENTORY='research/current-depth-reference-inventory-v44.json'
ADDENDUM='research/current-depth-reference-addenda/johns2003-hormuz-published-depths-v1.json'
CSV='research/current-depth-reference-addenda/johns2003-hormuz-published-depths-v1.csv'
CONTEXT='johns2003-hormuz-velocity-depths'
DOI='10.1029/2003JC001881'
OWNER='current:persian-gulf-saline-overflow'
URL='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2003JC001881'
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def verify_facts(facts,reserve):
    if facts['source_doi']!=DOI or facts['source_url']!=URL or facts['entity_id']!=OWNER or facts['id']!='johns2003-hormuz-published-depths-v1':raise ValueError('Exact source and owner')
    if any(facts['eligibility'].values()) or facts['original_html_bytes_verified'] is not False or facts['original_source_pixels_inspected'] is not False or facts['closed_native_cases_reopened'] is not False or facts['new_native_or_provider_requests']!=0:raise ValueError('Manual HTML evidence,no promotion/native replay')
    text=facts['source_text_excerpts']
    if len(text)!=3 or sum(len(s.split()) for s in text)!=16 or facts['source_text_excerpts_total_words']!=16:raise ValueError('Three bounded16wordexcerpts')
    reserve(sum(len(re.findall(r'\d+(?:\.\d+)?',s)) for s in text))
    site=re.fullmatch(r'at (\d+) m depth',text[0]);core=re.fullmatch(r'at depths of (\d+)–(\d+) m',text[1]);interface=re.fullmatch(r'at a depth of (\d+) m',text[2])
    if site is None or core is None or interface is None:raise ValueError('Explicit original quantities/metres')
    if [int(site.group(1))]+[int(v) for v in core.groups()]+[int(interface.group(1))]!=[110,60,70,45] or facts['reported_site_water_depth_m']!=110 or facts['reported_velocity_core_depth_band_m']!=[60,70] or facts['author_transport_interface_depth_m']!=45:raise ValueError('Exact site/core/interface values,no40m substitution')
    if facts['source_occupation_dates'] is not None or facts['source_velocity_threshold_m_s'] is not None or facts['vertical_datum']!='source_reported_depth_positive_down_datum_not_independently_qualified' or 'not a zero-velocity boundary' not in facts['interface_definition']:raise ValueError('No invented date/threshold/physical boundary')


def references(facts,facts_sha):
    if not re.fullmatch('[0-9a-f]{64}',facts_sha) or facts['entity_id']!=OWNER or any(facts['eligibility'].values()):raise ValueError('Exact facts hash/owner/no promotion')
    common={'entity_id':OWNER,'unit':'m','vertical_datum':facts['vertical_datum'],'lower_bound_m':None,'upper_bound_m':None,'lower_bound_exclusive':False,'upper_bound_exclusive':False,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':None,'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'source_context_id':CONTEXT,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':facts['source_locator'],'source_file':FACTS,'source_sha256':facts_sha,'source_velocity_threshold_m_s':None,'source_site_water_depth_m':facts['reported_site_water_depth_m'],'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],'evidence_kind':'manually_reviewed_primary_published_moored_velocity_summary','source_original_html_bytes_verified':False,'source_original_pixels_inspected':False,'qualification':'Averaged velocity core and chosen transport interface are distinct quantities;site110mbed is context,not independently resolved currentbottom. Instrumentgaps/nearbedundersampling retained. No exact per-period depth or annualrange/widthjoin/volume.',**copy.deepcopy(facts['eligibility'])}
    core=copy.deepcopy(common);core.update(id='pgw-johns2003-hormuz-mean-velocity-core-depth-band',metric='core_depth',approximate_value_m=None,range_m=copy.deepcopy(facts['reported_velocity_core_depth_band_m']),range_interpretation=facts['core_definition'],source_definition=facts['core_definition'],source_pointer='/reported_velocity_core_depth_band_m')
    interface=copy.deepcopy(common);interface.update(id='pgw-johns2003-hormuz-selected-transport-interface-depth',metric='transport_selected_upper_depth',approximate_value_m=facts['author_transport_interface_depth_m'],range_m=None,range_interpretation=None,source_definition=facts['interface_definition'],source_pointer='/author_transport_interface_depth_m')
    rows=[core,interface];validate_rows(rows,facts);return rows


def validate_rows(rows,facts):
    if len(rows)!=2 or [r['id'] for r in rows]!=['pgw-johns2003-hormuz-mean-velocity-core-depth-band','pgw-johns2003-hormuz-selected-transport-interface-depth']:raise ValueError('Exactly two descriptors')
    for row in rows:
        if row['entity_id']!=OWNER or row['unit']!='m' or row['source_doi']!=DOI or row['source_url']!=URL or row['source_file']!=FACTS or row['source_context_id']!=CONTEXT or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']):raise ValueError('Exact source/owner/unit/provenance')
        if any(row[k] is not None for k in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','phase_label','calendar_months','observed_period','same_source_width_reference_id','lower_bound_m','upper_bound_m','source_velocity_threshold_m_s']):raise ValueError('No physicalboundary/thickness/time/error/width promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['source_original_html_bytes_verified'] is not False or row['source_original_pixels_inspected'] is not False:raise ValueError('No physical/annual/independence/custody promotion')
        if row['source_site_water_depth_m']!=110 or row['vertical_datum']!=facts['vertical_datum'] or row['geographic_scope']!=facts['geographic_scope'] or row['temporal_scope']!=facts['temporal_scope']:raise ValueError('Same site and temporal context')
    core,interface=rows
    if core['metric']!='core_depth' or core['approximate_value_m'] is not None or core['range_m']!=[60,70] or core['source_definition']!=facts['core_definition'] or core['source_pointer']!='/reported_velocity_core_depth_band_m':raise ValueError('Core band,not thickness or annual range')
    if interface['metric']!='transport_selected_upper_depth' or interface['approximate_value_m']!=45 or interface['range_m'] is not None or interface['source_definition']!=facts['interface_definition'] or interface['source_pointer']!='/author_transport_interface_depth_m':raise ValueError('Chosen45m transport interface,not abstract40m or physical boundary')


def reference_layer(facts,digest):
    references(facts,digest)
    if facts['reported_site_water_depth_m']!=110 or facts['author_transport_interface_depth_m']!=45:raise ValueError('Exact local source-defined interval')
    return {'schema':'osw.hormuz-johns2003-local-reference-layer.v1','entity_id':OWNER,'role':'local_author_transport_layer_geometry_reference_scenario','source_file':FACTS,'source_sha256':digest,'source_doi':DOI,'source_locator':facts['source_locator'],'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],'reference_top_depth_m':facts['author_transport_interface_depth_m'],'reference_bottom_depth_m':facts['reported_site_water_depth_m'],'reference_thickness_m':facts['reported_site_water_depth_m']-facts['author_transport_interface_depth_m'],'reference_core_depth_band_m':copy.deepcopy(facts['reported_velocity_core_depth_band_m']),'vertical_datum':facts['vertical_datum'],'assumption':'Apply authors chosen45m transport interface at their110mdeep mooring site;bed closes a local transport-box reference,not an independently measured flow boundary. Thickness is calculated reference geometry,not a new observed currentthickness.','near_bed_layer_directly_resolved':False,'longitudinal_extent_km':None,'mapped_geometry':None,'width_km':None,'physical_current_thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'volume_km3':None,'physical_volume_eligible':False,'whole_route_depth_eligible':False,'new_observation':False,'source_eligibility_overridden':False,'runtime_changed':False,'full_goal_complete':False}


def assemble(before,facts,facts_sha):
    if before['counts']['depth_references']!=913 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact 913-reference/111-identity predecessor')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate prior source study or context')
    rows=references(facts,facts_sha);old={r['id'] for r in before['evidence']}
    if any(r['id'] in old for r in rows):raise ValueError('Duplicate existing reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['evidence'][:-2]!=before['evidence'] or out.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Every old reference and canonical calendar preserved')
    if out['counts']!={'identities':111,'depth_references':915,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':913}:raise ValueError('Two scoped references only, no physical/identity coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_JOHNS_HORMUZ_ADMISSION_START'])
    def stop(*a):raise TimeoutError('Shared60second source-test/admission deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline manual publication facts and admitted catalog only'))
    out=ROOT/'current-depth-reference-inventory-v44';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.johns2003-hormuz-published-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,facts_raw),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v44','status':'PINNED_REFERENCES_WITH_JOHNS2003_HORMUZ_VELOCITY_CORE_AND_TRANSPORT_INTERFACE','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},
                'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v44','status':'TWO_MANUALLY_REVIEWED_PRIMARY_HORMUZ_VELOCITY_DEPTH_REFERENCES_ADMITTED','interpretation':'Localmeanvelocitycore60-70mandauthorselected45mtransportinterfaceat110msite. SeparateOSWreferencegeometry,nophysicalboundary,annualrange,whole-routeprofileorvolume. ManualprimaryHTMLtextreview,nobyteorpixelcustody/nativearchive.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete actual JSON/CSV/catalog roundtrip and calendar preservation')
            if any({k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'} for old,new in zip(before['records'],final['records'])):raise ValueError('All non-reference owner fields preserved')
            result={'schema':'osw.johns2003-hormuz-admission-result.v1','status':'TWO_QUALIFIED_PUBLISHED_REFERENCES_ADMITTED_913_PRIOR_PRESERVED','counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_reference_ids':[r['id'] for r in rows],
                'new_native_ocean_values':0,'new_provider_requests':0,'original_pdf_bytes_or_pixels_verified':False,'manual_primary_published_text_review':True,'new_reference_records_not_new_OSW_observations':2,'runtime_changed':False,'full_goal_complete':False}
            layer_raw=encode(reference_layer(facts,sha(facts_raw)))
            if json.loads(layer_raw)!=reference_layer(facts,sha(facts_raw)):raise ValueError('Actual localreferenceJSONroundtrip')
            result_raw=encode(result)
            if json.loads(result_raw)!=result:raise ValueError('Full admission result roundtrip')
        total=sum(len(v) for v in pieces.values())+len(result_raw)+len(layer_raw)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(result_raw)
        (out/'reference-layer.json').write_bytes(layer_raw)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
