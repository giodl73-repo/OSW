"""One primary published NCC interface reference, never a current bottom."""
import copy,hashlib,json,os,re,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v4 import load_inventory as previous
from compiled_depth_catalog_view_v3 import refresh
from compiled_depth_catalog_view_v5 import load_inventory
from load_current_depth_reference_inventory_v1 import reference_csv_bytes
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v42.json'
FACTS='research/ncc-munk-1995-halocline-source-facts-v1.json'
PREVIOUS='research/current-depth-reference-inventory-v41.json'
INVENTORY='research/current-depth-reference-inventory-v42.json'
ADDENDUM='research/current-depth-reference-addenda/ncc-munk-1995-halocline-v1.json'
CSV='research/current-depth-reference-addenda/ncc-munk-1995-halocline-v1.csv'
OWNER='current:norwegian-coastal';DOI='10.3354/meps125021';CONTEXT='ncc-munk1995-may1992-published-halocline'
URL='https://backend.orbit.dtu.dk/ws/portalfiles/portal/3708269/Munk4.pdf'
encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def verify_facts(facts,reserve):
    if facts['id']!='ncc-munk-1995-halocline-v1' or facts['entity_id']!=OWNER or facts['source_doi']!=DOI or facts['source_url']!=URL:raise ValueError('Exact NCC owner and primary publication')
    if any(facts['eligibility'].values()) or any(facts[k] is not False for k in ['original_pdf_bytes_verified','original_pdf_pixels_inspected','native_source_case_reopened','runtime_changed','full_goal_complete']):raise ValueError('Manual primary text only,no promotion/native replay')
    text=facts['source_excerpt']
    if len(text.split())!=11 or facts['source_excerpt_words']!=11:raise ValueError('One eleven-word source excerpt only')
    reserve(len(re.findall(r'\d+(?:\.\d+)?',text)))
    match=re.fullmatch(r'halocline of the NCC \(at about (\d+) to (\d+) m depth\)',text)
    if match is None or [int(s) for s in match.groups()]!=[10,15] or facts['reported_halocline_depth_band_m']!=[10,15]:raise ValueError('Source halocline band/metres unchanged')
    if facts['source_survey_window']!=['1992-05-10','1992-05-21'] or facts['source_halocline_salinity_or_density_threshold'] is not None:raise ValueError('Survey context,no invented interface threshold')
    if facts['vertical_datum']!='source_reported_depth_positive_down_datum_not_independently_qualified' or 'not a measured velocity-zero' not in facts['definition']:raise ValueError('Hydrographic interface role and datum qualification required')

def reference(facts,digest):
    if not re.fullmatch('[0-9a-f]{64}',digest) or facts['entity_id']!=OWNER or any(facts['eligibility'].values()):raise ValueError('Exact facts SHA/owner/false eligibility')
    row={'id':'ncc-munk-1995-may1992-reported-halocline-depth-band','entity_id':OWNER,'metric':'reported_current_associated_halocline_depth_band','unit':'m',
        'approximate_value_m':None,'range_m':copy.deepcopy(facts['reported_halocline_depth_band_m']),
        'range_interpretation':'Source approximate regional halocline depth band,not one paired current thickness,annual range,confidence interval or velocity boundary.',
        'vertical_datum':facts['vertical_datum'],'upper_boundary_m':None,'lower_boundary_m':None,'lower_bound_m':None,'upper_bound_m':None,'lower_bound_exclusive':False,'upper_bound_exclusive':False,
        'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':None,'calendar_months':None,'observed_period':None,'same_source_width_reference_id':None,
        'geographic_scope':facts['geographic_scope'],'temporal_scope':facts['temporal_scope'],'source_definition':facts['definition'],'source_survey_window':copy.deepcopy(facts['source_survey_window']),
        'source_interface_criterion':None,'source_context_id':CONTEXT,'source_doi':DOI,'source_url':URL,'source_citation':facts['source_citation'],'source_locator':facts['source_locator'],
        'source_file':FACTS,'source_pointer':'/reported_halocline_depth_band_m','source_sha256':digest,
        'evidence_kind':'manually_reviewed_primary_published_current_associated_hydrographic_interface',
        'original_pdf_bytes_verified':False,'original_pdf_pixels_inspected':False,
        'qualification':'NCC-associated halocline only; do not transfer to Norwegian Atlantic or Jutland identities,assign a velocity bottom,subtract depth endpoints into thickness,or treat survey dates as exact occupation/seasonal extrema.',**copy.deepcopy(facts['eligibility'])}
    validate(row,facts);return row

def validate(row,facts):
    if row['id']!='ncc-munk-1995-may1992-reported-halocline-depth-band' or row['entity_id']!=OWNER or row['metric']!='reported_current_associated_halocline_depth_band' or row['unit']!='m' or row['range_m']!=[10,15] or row['approximate_value_m'] is not None:raise ValueError('One scoped hydrographic interface quantity')
    if any(row[k] is not None for k in ['upper_boundary_m','lower_boundary_m','lower_bound_m','upper_bound_m','thickness_m','uncertainty_m','annual_range_m','phase_label','calendar_months','observed_period','same_source_width_reference_id','source_interface_criterion']):raise ValueError('No velocity boundary,thickness,time,error or criterion inferred')
    if any(row[k] is not False for k in facts['eligibility']) or row['original_pdf_bytes_verified'] is not False or row['original_pdf_pixels_inspected'] is not False:raise ValueError('No physical/independence/custody promotion')
    if row['source_survey_window']!=['1992-05-10','1992-05-21'] or row['source_definition']!=facts['definition'] or row['geographic_scope']!=facts['geographic_scope'] or row['temporal_scope']!=facts['temporal_scope'] or row['vertical_datum']!=facts['vertical_datum'] or row['source_doi']!=DOI or row['source_url']!=URL or row['source_context_id']!=CONTEXT or row['source_file']!=FACTS or row['source_pointer']!='/reported_halocline_depth_band_m' or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']):raise ValueError('Source owner/role/window/facts provenance preserved')

def assemble(before,facts,digest):
    if before['counts']['depth_references']!=910 or len(before['records'])!=111 or OWNER not in {r['entity_id'] for r in before['records']}:raise ValueError('Exact910-reference111-identity predecessor')
    row=reference(facts,digest)
    if CONTEXT in before['source_contexts'] or any(e['id']==row['id'] or DOI in str(e.get('source_doi',''))+' '+str(e.get('source_citation','')) for e in before['evidence']):raise ValueError('No duplicate prior source study/context/reference')
    out=copy.deepcopy(before);out['evidence'].append(row);out['source_contexts'][CONTEXT]=copy.deepcopy(facts);refresh(out)
    if out['counts']!={'identities':111,'depth_references':911,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or out['coordinate_unit_counts']!={'dbar':2,'m':909}:raise ValueError('Exactly one scoped metre reference,no physical/identity promotion')
    return out

def main():
    start=float(os.environ['OSW_NCC_HALOC_ADMISSION_START'])
    def stop(*a):raise TimeoutError('Shared60second test/admission deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline manual facts and admitted catalog only'))
    out=ROOT/'current-depth-reference-inventory-v42';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    q=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=q.reader(lambda p:(ROOT/p).read_bytes())
    def reserve(n):
        if q.ledger['reserved_numeric_tokens']+n>q.numeric_cap:raise ValueError('Prospective source-excerpt cap before conversion')
        q.ledger['reserved_numeric_tokens']+=n;q.ledger['new_numeric_tokens']+=n;q.ledger['primary_excerpt_numeric_conversions_reserved']=n;save(q.ledger)
    piece=lambda p,b:{'file':p,'bytes':len(b),'sha256':sha(b)}
    try:
        with q.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            raw_facts=reader(FACTS);facts=json.loads(raw_facts);verify_facts(facts,reserve)
            raw_prior=reader(PREVIOUS);before=previous(json.loads(raw_prior),reader);after=assemble(before,facts,sha(raw_facts))
            addition={'schema':'osw.ncc-munk1995-halocline-addendum.v1','id':facts['id'],'source_facts':piece(FACTS,raw_facts),'source_contexts':{CONTEXT:copy.deepcopy(facts)},'evidence':[after['evidence'][-1]],'runtime_changed':False,'full_goal_complete':False}
            ar=encode(addition);csvraw=reference_csv_bytes(addition['evidence'])
            manifest={'schema':'osw.current-depth-reference-inventory.v42','status':'PINNED_REFERENCES_WITH_NCC1992_REPORTED_HALINE_INTERFACE','previous_inventory':piece(PREVIOUS,raw_prior),'reference_addendum':{'id':facts['id'],'json':piece(ADDENDUM,ar),'csv':piece(CSV,csvraw)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
                'view_metadata':{'schema':'osw.current-depth-reference-view.v42','status':'ONE_MANUALLY_REVIEWED_PRIMARY_NCC_HALOCLINE_REFERENCE_ADMITTED','interpretation':'Author-reportedapprox10-15mNCC-associatedhaloclineMay1992context,notvelocityboundary/fullthickness/annualrange/othercurrentdepth. ManualprimaryPDFtextreview,nobyteorpixelcustody/nativecaseclaim.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:ar,CSV:csvraw};final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['evidence'][:-1]!=before['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts'] or final.get('calendar_depth_series')!=before.get('calendar_depth_series'):raise ValueError('Complete actual JSONCSV/catalog preservation and roundtrip')
            if any({k:v for k,v in a.items() if k!='depth_reference_ids'}!={k:v for k,v in b.items() if k!='depth_reference_ids'} for a,b in zip(before['records'],final['records'])):raise ValueError('All non-reference owner fields preserved')
            result={'schema':'osw.ncc-munk1995-admission-result.v1','counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_reference_id':addition['evidence'][0]['id'],'previous_references_preserved':910,'manual_primary_published_text_review':True,'source_pdf_bytes_or_pixels_verified':False,'new_native_values':0,'new_provider_requests':0,'runtime_changed':False,'full_goal_complete':False};rr=encode(result)
            if json.loads(rr)!=result:raise ValueError('Actual admission result roundtrip')
        total=sum(map(len,pieces.values()))+len(rr)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        for p,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[p])
        (out/'admission-result.json').write_bytes(rr)
        print(json.dumps({'result':result,'query_numeric_tokens':q.ledger['reserved_numeric_tokens'],'query_bytes':q.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
