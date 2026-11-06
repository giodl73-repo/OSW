"""Admit two manually reviewed published PGW descriptors, preserving v40."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v3 import load_inventory as previous,refresh
from compiled_depth_catalog_view_v4 import load_inventory
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,checked_piece
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v41.json'
FACTS='research/font-2024-pgw-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v40.json'
INVENTORY='research/current-depth-reference-inventory-v41.json'
ADDENDUM='research/current-depth-reference-addenda/font-2024-pgw-published-depths-v1.json'
CSV='research/current-depth-reference-addenda/font-2024-pgw-published-depths-v1.csv'
CONTEXT='font-2024-pgw-regional-glider-published-depths'
DOI='10.1029/2023JC020668'
OWNER='current:persian-gulf-saline-overflow'
URL='https://ueaeprints.uea.ac.uk/id/eprint/95037/1/JGR_Oceans_2024_Font_Ventilation_of_the_Arabian_Sea_Oxygen_Minimum_Zone_by_Persian_Gulf_Water.pdf'
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def verify_facts(facts,reserve):
    if facts['source_doi']!=DOI or facts['source_url']!=URL or facts['entity_id']!=OWNER or facts['id']!='font-2024-pgw-published-depths-v1':raise ValueError('Exact primary publication and outflow owner')
    if any(facts['eligibility'].values()) or facts['original_pdf_byte_custody_performed'] is not False or facts['original_pdf_pixels_inspected'] is not False or facts['closed_native_cases_reopened'] is not False or facts['new_native_or_provider_requests']!=0:raise ValueError('Manual published-text evidence only; no source/native/physical promotion')
    excerpts=facts['source_text_excerpts']
    if len(excerpts)!=2 or sum(len(s.split()) for s in excerpts)>25 or facts['source_text_excerpts_total_words']!=sum(len(s.split()) for s in excerpts):raise ValueError('Exactly two short bounded primary excerpts')
    reserve(sum(len(re.findall(r'\d+(?:\.\d+)?',s)) for s in excerpts))
    band=re.fullmatch(r'corresponding to depths from (\d+) to (\d+) m',excerpts[0])
    core=re.fullmatch(r'its core is located at a depth of (\d+) m',excerpts[1])
    if band is None or core is None:raise ValueError('Unambiguous original prose quantity and explicit metres required')
    values=[int(v) for v in band.groups()]+[int(core.group(1))]
    if values!=[150,400,200] or facts['reported_hydrographic_depth_band_m']!=values[:2] or facts['reported_core_depth_m']!=values[2]:raise ValueError('Exact reviewed source numbers, no bound/thickness substitution')
    if facts['source_potential_density_anomaly_interval_kg_m3']!=[25.5,27] or facts['vertical_datum']!='source_reported_depth_positive_down_datum_not_independently_qualified':raise ValueError('Original hydrographic population/unit/datum qualification')
    if 'not a maximum-speed core' not in facts['core_definition'] or 'Not paired upper/lower boundaries' not in facts['depth_band_definition'] or '2015-2016' not in facts['temporal_scope'] or '2021-2022' not in facts['temporal_scope']:raise ValueError('Property core, pooled regional extent and observing windows stay explicit')

def references(facts,facts_sha):
    if not re.fullmatch(r'[0-9a-f]{64}',facts_sha):raise ValueError('Exact source facts SHA256 required')
    if facts['entity_id']!=OWNER or facts['source_doi']!=DOI or facts['source_url']!=URL or any(facts['eligibility'].values()):raise ValueError('Known owner,source and no eligibility promotion')
    common={'entity_id':OWNER,'unit':'m','vertical_datum':facts['vertical_datum'],'lower_bound_m':None,'lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,
        'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':None,'calendar_months':None,'observed_period':None,
        'source_context_id':CONTEXT,'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],
        'evidence_kind':'manually_reviewed_primary_published_glider_hydrographic_descriptor','source_url':URL,'source_doi':DOI,'source_citation':facts['source_citation'],'source_locator':facts['source_locator'],
        'source_file':FACTS,'source_pointer':'/reported_core_depth_m','source_sha256':facts_sha,
        'source_potential_density_anomaly_interval_kg_m3':copy.deepcopy(facts['source_potential_density_anomaly_interval_kg_m3']),
        'source_original_pdf_byte_custody_performed':False,'source_original_pdf_pixels_inspected':False,
        'same_source_width_reference_id':None,**copy.deepcopy(facts['eligibility']),
        'qualification':'Regional source-reported property-defined PGW depth evidence. Core is not a velocity maximum; regional band is not one paired profile or a thickness. Source gridding/interpolation and distinct observing sections retained. No exact core station, shared annual mean, annual extrema, physical bottom, uncertainty or stored volume.'}
    core=copy.deepcopy(common);core.update(id='pgw-font-2024-glider-property-core-depth',metric='core_depth',approximate_value_m=facts['reported_core_depth_m'],range_m=None,range_interpretation=None,source_definition=facts['core_definition'])
    band=copy.deepcopy(common);band.update(id='pgw-font-2024-glider-regional-hydrographic-depth-band',metric='reported_hydrographic_outflow_depth_band',approximate_value_m=None,range_m=copy.deepcopy(facts['reported_hydrographic_depth_band_m']),range_interpretation=facts['depth_band_definition'],source_definition=facts['depth_band_definition'],source_pointer='/reported_hydrographic_depth_band_m')
    rows=[core,band];validate_rows(rows,facts);return rows

def validate_rows(rows,facts):
    if len(rows)!=2 or [r['id'] for r in rows]!=['pgw-font-2024-glider-property-core-depth','pgw-font-2024-glider-regional-hydrographic-depth-band']:raise ValueError('Two distinct source quantities only')
    for row in rows:
        if row['entity_id']!=OWNER or row['unit']!='m' or row['source_doi']!=DOI or row['source_url']!=URL or row['source_file']!=FACTS or row['source_context_id']!=CONTEXT or not re.fullmatch(r'[0-9a-f]{64}',row['source_sha256']):raise ValueError('Exact owner/unit/source/facts provenance')
        if any(row[k] is not None for k in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','phase_label','calendar_months','observed_period','same_source_width_reference_id','lower_bound_m','upper_bound_m']):raise ValueError('No thickness,exact time,width,uncertainty or bound promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['source_original_pdf_byte_custody_performed'] is not False or row['source_original_pdf_pixels_inspected'] is not False:raise ValueError('All physical/time/volume/independence/custody flags stay false')
        if row['source_potential_density_anomaly_interval_kg_m3']!=[25.5,27] or row['vertical_datum']!=facts['vertical_datum'] or row['geographic_scope']!=facts['geographic_scope'] or row['temporal_scope']!=facts['temporal_scope']:raise ValueError('Original population/datum/region/time scope')
    core,band=rows
    if core['metric']!='core_depth' or core['approximate_value_m']!=200 or core['range_m'] is not None or core['source_definition']!=facts['core_definition'] or core['source_pointer']!='/reported_core_depth_m':raise ValueError('Property core depth is not a boundary or velocity maximum')
    if band['metric']!='reported_hydrographic_outflow_depth_band' or band['approximate_value_m'] is not None or band['range_m']!=[150,400] or band['range_interpretation']!=facts['depth_band_definition'] or band['source_pointer']!='/reported_hydrographic_depth_band_m':raise ValueError('Regional hydrographic band is not one paired thickness')

def assemble(before,facts,facts_sha):
    if before['counts']['depth_references']!=908 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact 908-reference/111-identity predecessor')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate prior source study or context')
    rows=references(facts,facts_sha);old={r['id'] for r in before['evidence']}
    if any(r['id'] in old for r in rows):raise ValueError('Duplicate existing reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['evidence'][:-2]!=before['evidence'] or out.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Every old reference and canonical calendar preserved')
    if out['counts']!={'identities':111,'depth_references':910,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':908}:raise ValueError('Two scoped references only, no physical/identity coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_FONT_PGW_ADMISSION_START'])
    def stop(*a):raise TimeoutError('Shared60second source-test/admission deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline manual publication facts and admitted catalog only'))
    out=ROOT/'current-depth-reference-inventory-v41';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.font-2024-pgw-published-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,facts_raw),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v41','status':'PINNED_REFERENCES_WITH_FONT2024_PGW_PROPERTY_CORE_AND_REGIONAL_DEPTH_BAND','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},
                'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v41','status':'TWO_MANUALLY_REVIEWED_PRIMARY_PGW_GLIDER_DEPTH_REFERENCES_ADMITTED','interpretation':'Source-reported200mpropertycoreand150-400mregionalhydrographicband. Not maximum-speed depth,paired250mthickness,annualrange,physicalbottom,completeprofileorvolume. Manual primary PDF-text review; no original byte/pixel custody or native archive reopened.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete actual JSON/CSV/catalog roundtrip and calendar preservation')
            if any({k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'} for old,new in zip(before['records'],final['records'])):raise ValueError('All non-reference owner fields preserved')
            result={'schema':'osw.font-2024-pgw-admission-result.v1','status':'TWO_QUALIFIED_PUBLISHED_REFERENCES_ADMITTED_908_PRIOR_PRESERVED','counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_reference_ids':[r['id'] for r in rows],
                'new_native_ocean_values':0,'new_provider_requests':0,'original_pdf_bytes_or_pixels_verified':False,'manual_primary_published_text_review':True,'new_reference_records_not_new_OSW_observations':2,'runtime_changed':False,'full_goal_complete':False}
            result_raw=encode(result)
            if json.loads(result_raw)!=result:raise ValueError('Full admission result roundtrip')
        total=sum(len(v) for v in pieces.values())+len(result_raw)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[path])
        (out/'admission-result.json').write_bytes(result_raw)
        print(json.dumps({'result':result,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
