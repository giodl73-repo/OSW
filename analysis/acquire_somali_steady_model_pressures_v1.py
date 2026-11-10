"""One original-source capture and explicit Somali model pressure descriptors."""
import hashlib,json,os,re,signal,time,unicodedata,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/somali-steady-model-pressure-operator-v1.json'
URL='https://accedacris.ulpgc.es/bitstream/10553/4615/1/0617537_00000_0000.pdf'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
def normalize(text):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',text)).strip()
def extract(text):
    text=normalize(text)
    for pattern in [r'Wind.driven cross.equatorial flow',r'2003.{0,3}2009',r'steady model',r'Argo']:
        if not re.search(pattern,text,re.I):raise ValueError('Primary study identity/method missing:'+pattern)
    winter=re.search(r'Winter Monsoon.{0,100}?\(?[^0-9]{0,5}(200)\s*dbar',text,re.I)
    deep=re.search(r'Summer Monsoon and Transitional Periods.{0,150}?\(?[^0-9]{0,5}(650)\s*dbar',text,re.I)
    if winter is None or deep is None:raise ValueError('Explicit seasonal pressure extents not established')
    rows=[]
    for phase,match,flow in [('winter_monsoon',winter,'southward'),('summer_monsoon',deep,'northward'),('transitional_periods',deep,'southward')]:
        rows.append({'id':'somali-steady-2003-2009-'+phase+'-reported-pressure-extent','entity_id':'current:somali','metric':'reported_steady_model_current_lower_extent_pressure','approximate_value':int(match.group(1)),'unit':'dbar','source_phase':phase,'source_statistic':'author_reported_approximate_model_section_extent','source_basis':'NCEP wind stress and Argo temperature/salinity, steady model; seven-year2003-2009study','geographic_scope':'Cross-equatorial Indian Ocean/Somali Current section; exact endpoint position unresolved','source_flow_direction':flow,'vertical_coordinate':'source_reported_pressure; no metre conversion','lower_boundary_metres':None,'thickness_metres':None,'annual_extrema_dbar':None,'pressure_uncertainty_dbar':None,'calendar_months':None,'source_velocity_cutoff_m_s':None,'physical_current_bottom_established':False,'independent_direct_observation':False,'whole_current_representative':False,'seasonal_playback_eligible':False,'physical_depth_ranking_eligible':False,'route_state_join_eligible':False,'volume_eligible':False,'qualification':'Approximate model extent from source abstract, cutoff criterion not independently reconstructed. Direction reverses between source phases; shared summer/transition value is one author statement, not two independent observations. Pressure is not metres, thickness or current bottom; phases not a monthly animation or annual uncertainty envelope.'})
    return rows

def main():
    import pymupdf
    start=float(os.environ['OSW_SOMALI_PRESSURE_START']);out=ROOT/'somali-steady-model-pressure-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.somali-steady-model-pressure-case.v1','status':'RESERVED','provider_operation_cap':1,'attempts':0,'source_url':URL,'native_array_values_decoded':0,'new_canonical_references':0,'automatic_retries':0,'redirects_followed':0,'raw_bytes':0,'runtime_changed':False,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Absolute source deadline or SIGTERM')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(60);save();response=None
    try:
        if not 0<=time.monotonic()-start<30:raise ValueError('Shared cloud phase clock')
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        ledger.update(attempts=1,status='ATTEMPT_RESERVED_TARGET_CLOSED');save()
        req=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept':'application/pdf','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=25)
        except urllib.error.HTTPError as error:response=error
        ledger['http_status']=response.code
        with (out/'primary-response.bin').open('xb') as f:
            while True:
                chunk=response.read(min(65536,1900001-ledger['raw_bytes']))
                if not chunk:break
                f.write(chunk);ledger['raw_bytes']+=len(chunk)
                if ledger['raw_bytes']>1900000:raise ValueError('Raw source byte cap')
        raw=(out/'primary-response.bin').read_bytes();ledger['raw_sha256']=hashlib.sha256(raw).hexdigest();save()
        if response.code!=200 or not raw.startswith(b'%PDF-'):raise ValueError('Original PDF source not retrieved')
        length=response.headers.get('Content-Length')
        if length is not None and int(length)!=len(raw):raise ValueError('Complete source body required')
        with pymupdf.open(stream=raw,filetype='pdf') as doc:
            if not 1<=len(doc)<=40:raise ValueError('Bounded primary document page scope')
            pages=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
            full=' '.join(p['text'] for p in pages)
            if len(full)>160000:raise ValueError('Source text bound')
            rows=extract(full);source_tokens=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',full))
            if source_tokens>10000:raise ValueError('Source numeric-token bound')
            report={'schema':'osw.somali-steady-reported-pressure-extents.v1','source_url':URL,'source_title':'Wind-driven cross-equatorial flow in the Indian ocean','raw_sha256':ledger['raw_sha256'],'source_locator':'Original abstract; model definition in original study. Full citation pending primary-document visual review.','rows':rows,'canonical_reference_admitted':False,'runtime_changed':False,'full_goal_complete':False}
            encoded=(json.dumps(report,indent=2)+'\n').encode();inspection=(json.dumps({'source_url':URL,'raw_sha256':ledger['raw_sha256'],'pages':pages},indent=2)+'\n').encode()
            if json.loads(encoded)!=report:raise ValueError('Actual full descriptor roundtrip')
            if len(raw)+len(encoded)+len(inspection)>2200000:raise ValueError('Shared raw/derived output cap')
            (out/'descriptors.json').write_bytes(encoded);(out/'inspection.json').write_bytes(inspection)
            remaining=2300000-len(raw)-len(encoded)-len(inspection);rendered=[]
            for index in range(min(2,len(doc))):
                image=doc[index].get_pixmap(dpi=75).tobytes('png')
                if len(image)<=remaining:(out/('page-'+str(index+1)+'.png')).write_bytes(image);remaining-=len(image);rendered.append(index+1)
            ledger.update(status='THREE_MODEL_PHASE_PRESSURE_DESCRIPTORS_PENDING_MANUAL_SOURCE_REVIEW',source_pages=len(doc),source_numeric_tokens=source_tokens,descriptor_rows=len(rows),distinct_author_pressure_values=len({r['approximate_value'] for r in rows}),rendered_pdf_pages=rendered,source_case_metadata_upper_bound=1000,source_case_numeric_upper_bound=source_tokens+1000)
    except BaseException as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400]);raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
