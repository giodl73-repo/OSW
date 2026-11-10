"""Admit two manually reviewed published PGW descriptors, preserving v42."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v5 import load_inventory as previous
from compiled_depth_catalog_view_v3 import refresh
from compiled_depth_catalog_view_v6 import load_inventory
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,checked_piece
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v43.json'
FACTS='research/bidokhti2009-pgw-depth-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v42.json'
INVENTORY='research/current-depth-reference-inventory-v43.json'
ADDENDUM='research/current-depth-reference-addenda/bidokhti2009-pgw-published-depths-v1.json'
CSV='research/current-depth-reference-addenda/bidokhti2009-pgw-published-depths-v1.csv'
CONTEXT='bidokhti2009-pgw-regional-ctd-published-depths'
DOI='10.5194/os-5-1-2009'
OWNER='current:persian-gulf-saline-overflow'
URL='https://os.copernicus.org/articles/5/1/2009/os-5-1-2009.pdf'
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def verify_facts(facts,reserve):
    if facts['source_doi']!=DOI or facts['source_url']!=URL or facts['entity_id']!=OWNER or facts['id']!='bidokhti2009-pgw-published-depths-v1':raise ValueError('Exact primary source and owner')
    if any(facts['eligibility'].values()) or facts['original_pdf_byte_custody_performed'] is not False or facts['original_pdf_pixels_inspected'] is not False or facts['closed_native_cases_reopened'] is not False or facts['new_native_or_provider_requests']!=0:raise ValueError('Manual text mode,no promotion or native replay')
    excerpts=facts['source_text_excerpts']
    if len(excerpts)!=2 or sum(len(s.split()) for s in excerpts)!=11 or facts['source_text_excerpts_total_words']!=11:raise ValueError('Two bounded eleven-word excerpts')
    reserve(sum(len(re.findall(r'\d+(?:\.\d+)?',s)) for s in excerpts))
    thickness=re.fullmatch(r'about (\d+) m',excerpts[0]);band=re.fullmatch(r'between (\d+) and (\d+) m, especially for summer\.',excerpts[1])
    if thickness is None or band is None:raise ValueError('Explicit source quantities and metres')
    if [int(thickness.group(1))]+[int(v) for v in band.groups()]!=[200,200,500] or facts['reported_hydrographic_thickness_m']!=200 or facts['reported_hydrographic_depth_band_m']!=[200,500]:raise ValueError('Exact source values,no thickness/band substitution')
    if facts['source_survey_year']!=1992 or facts['source_occupation_dates'] is not None or facts['source_hydrographic_boundary_threshold'] is not None:raise ValueError('1992context,no invented occupations or threshold')
    if facts['vertical_datum']!='source_reported_depth_positive_down_datum_not_independently_qualified' or 'not a measured velocity-defined thickness' not in facts['thickness_definition'] or 'Not paired upper/lower boundaries' not in facts['depth_band_definition']:raise ValueError('Hydrographic thickness versus depth band and datum')


def references(facts,facts_sha):
    if not re.fullmatch('[0-9a-f]{64}',facts_sha) or facts['entity_id']!=OWNER or any(facts['eligibility'].values()):raise ValueError('Exact facts hash/owner/eligibility')
    common={'entity_id':OWNER,'unit':'m','vertical_datum':facts['vertical_datum'],'lower_bound_m':None,'upper_bound_m':None,'lower_bound_exclusive':False,'upper_bound_exclusive':False,'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':None,'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,'source_context_id':CONTEXT,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':facts['source_locator'],'source_file':FACTS,'source_sha256':facts_sha,'source_hydrographic_boundary_threshold':None,'source_survey_year':1992,'source_occupation_dates':None,'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],'evidence_kind':'manually_reviewed_primary_published_ctd_hydrographic_descriptor','source_original_pdf_byte_custody_performed':False,'source_original_pdf_pixels_inspected':False,'qualification':'Approximate regional hydrographic plume quantities from1992CTD reanalysis,not velocity-current bottom or mapped body. Thickness200m is not the300m depth-band span. No exact occupation,annual range,independent cohort,width join or volume.',**copy.deepcopy(facts['eligibility'])}
    thickness=copy.deepcopy(common);thickness.update(id='pgw-bidokhti2009-reported-hydrographic-plume-thickness',metric='reported_water_mass_plume_thickness',approximate_value_m=facts['reported_hydrographic_thickness_m'],range_m=None,range_interpretation=None,thickness_m=facts['reported_hydrographic_thickness_m'],source_definition=facts['thickness_definition'],source_pointer='/reported_hydrographic_thickness_m')
    band=copy.deepcopy(common);band.update(id='pgw-bidokhti2009-reported-regional-depth-band',metric='reported_hydrographic_outflow_depth_band',approximate_value_m=None,range_m=copy.deepcopy(facts['reported_hydrographic_depth_band_m']),range_interpretation=facts['depth_band_definition'],source_definition=facts['depth_band_definition'],source_pointer='/reported_hydrographic_depth_band_m')
    rows=[thickness,band];validate_rows(rows,facts);return rows


def validate_rows(rows,facts):
    if len(rows)!=2 or [r['id'] for r in rows]!=['pgw-bidokhti2009-reported-hydrographic-plume-thickness','pgw-bidokhti2009-reported-regional-depth-band']:raise ValueError('Exactly two distinct descriptors')
    for row in rows:
        if row['entity_id']!=OWNER or row['unit']!='m' or row['source_doi']!=DOI or row['source_url']!=URL or row['source_file']!=FACTS or row['source_context_id']!=CONTEXT or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']):raise ValueError('Exact owner,metres,source and provenance')
        if any(row[k] is not None for k in ['upper_boundary_m','lower_boundary_m','uncertainty_m','annual_range_m','phase_label','calendar_months','observed_period','same_source_width_reference_id','lower_bound_m','upper_bound_m','source_hydrographic_boundary_threshold','source_occupation_dates']):raise ValueError('No boundary,time,error,width or criterion promotion')
        if any(row[k] is not False for k in facts['eligibility']) or row['source_original_pdf_byte_custody_performed'] is not False or row['source_original_pdf_pixels_inspected'] is not False:raise ValueError('No physical/time/volume/independence/custody promotion')
        if row['source_survey_year']!=1992 or row['vertical_datum']!=facts['vertical_datum'] or row['geographic_scope']!=facts['geographic_scope'] or row['temporal_scope']!=facts['temporal_scope']:raise ValueError('Original region,year,datum and context')
    thickness,band=rows
    if thickness['metric']!='reported_water_mass_plume_thickness' or thickness['approximate_value_m']!=200 or thickness['thickness_m']!=200 or thickness['range_m'] is not None or thickness['source_definition']!=facts['thickness_definition'] or thickness['source_pointer']!='/reported_hydrographic_thickness_m':raise ValueError('Reported hydrographic thickness only')
    if band['metric']!='reported_hydrographic_outflow_depth_band' or band['approximate_value_m'] is not None or band['thickness_m'] is not None or band['range_m']!=[200,500] or band['range_interpretation']!=facts['depth_band_definition'] or band['source_pointer']!='/reported_hydrographic_depth_band_m':raise ValueError('Depth band is not paired thickness')


def assemble(before,facts,facts_sha):
    if before['counts']['depth_references']!=911 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact 911-reference/111-identity predecessor')
    if CONTEXT in before['source_contexts'] or any(DOI in str(r.get('source_doi',''))+' '+str(r.get('source_citation','')) for r in before['evidence']):raise ValueError('Duplicate prior source study or context')
    rows=references(facts,facts_sha);old={r['id'] for r in before['evidence']}
    if any(r['id'] in old for r in rows):raise ValueError('Duplicate existing reference identity')
    out=copy.deepcopy(before);out['evidence'].extend(rows);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['evidence'][:-2]!=before['evidence'] or out.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Every old reference and canonical calendar preserved')
    if out['counts']!={'identities':111,'depth_references':913,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':911}:raise ValueError('Two scoped references only, no physical/identity coverage promotion')
    return out

def main():
    start=float(os.environ['OSW_BIDOKHTI_PGW_ADMISSION_START'])
    def stop(*a):raise TimeoutError('Shared60second source-test/admission deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline manual publication facts and admitted catalog only'))
    out=ROOT/'current-depth-reference-inventory-v43';out.mkdir(exist_ok=False)
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
            addendum={'schema':'osw.bidokhti2009-pgw-published-depth-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,facts_raw),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':rows,'runtime_changed':False,'full_goal_complete':False}
            raw_addendum=encode(addendum);table=reference_csv_bytes(rows)
            manifest={'schema':'osw.current-depth-reference-inventory.v43','status':'PINNED_REFERENCES_WITH_BIDOKHTI2009_PGW_HYDROGRAPHIC_THICKNESS_AND_DEPTH_BAND','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,raw_addendum),'csv':piece(CSV,table)},
                'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v43','status':'TWO_MANUALLY_REVIEWED_PRIMARY_PGW_CTD_DEPTH_REFERENCES_ADMITTED','interpretation':'Approximate200mhydrographicplumethicknessandregional200-500mdepthband,1992CTDcontext. Not300mthickness,velocitybottom,annualrange,pairedprofileorvolume. ManualselectedprimaryPDFtextreview,nobyteorpixelcustody/nativearchive.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:raw_addendum,CSV:table}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete actual JSON/CSV/catalog roundtrip and calendar preservation')
            if any({k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'} for old,new in zip(before['records'],final['records'])):raise ValueError('All non-reference owner fields preserved')
            result={'schema':'osw.bidokhti2009-pgw-admission-result.v1','status':'TWO_QUALIFIED_PUBLISHED_REFERENCES_ADMITTED_911_PRIOR_PRESERVED','counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_reference_ids':[r['id'] for r in rows],
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
