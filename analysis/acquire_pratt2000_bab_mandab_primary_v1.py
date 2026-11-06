"""One-shot cloud custody and bounded primary-paper inspection, no field reads."""
import hashlib,json,os,re,signal,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/pratt2000-bab-mandab-primary-operator-v1.json'
URL='https://www.whoi.edu/science/PO/dept/Pratt%20Personal%20Research%20web%20page/Larry%27s%20web%20page/JPO2000_30_10__2515-2534.pdf'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def inspect(document):
    if len(document)!=20:raise ValueError('Original20page source required')
    pages=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(document)]
    text=' '.join(' '.join(p['text'].split()) for p in pages)
    if len(text)>180000:raise ValueError('Primary text size bound')
    for phrase in ['Continuous Dynamical Modes','Bab al Mandab','PRATT','MURRAY','JOHNS']:
        if phrase not in text:raise ValueError('Source identity missing: '+phrase)
    numbers=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',text))
    if numbers>10000:raise ValueError('Source numeric-token bound')
    return pages,numbers

def main():
    import pymupdf
    start=time.monotonic();out=ROOT/'pratt2000-bab-mandab-primary-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.pratt2000-bab-mandab-primary-ledger.v1','status':'RESERVED','source_url':URL,'reserved_provider_operations':1,'attempted_provider_operations':0,'automatic_retries':0,'redirects_followed':0,'body_bytes':0,'native_array_values_decoded':0,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False}
    def save():
        p=out/'ledger.json';tmp=p.with_suffix('.tmp');tmp.write_bytes((json.dumps(ledger,indent=2)+'\n').encode());os.replace(tmp,p)
    def stopped(*args):raise TimeoutError('Absolute producer deadline or SIGTERM')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(60)
    save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        if op['source_url']!=URL or op['maximum_provider_operations']!=1 or any(op['eligibility'].values()):raise ValueError('Exact source and non-promotion')
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed: '+p)
        ledger.update(status='ATTEMPT_RESERVED_TARGET_CLOSED',attempted_provider_operations=1);save()
        req=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-document-custody/1.0','Accept':'application/pdf','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=25)
        except urllib.error.HTTPError as error:response=error
        ledger['http_status']=response.code
        with (out/'primary-response.bin').open('xb') as f:
            while True:
                chunk=response.read(min(65536,2000001-ledger['body_bytes']))
                if not chunk:break
                f.write(chunk);ledger['body_bytes']+=len(chunk)
                if ledger['body_bytes']>2000000:raise ValueError('Raw source byte limit')
        raw=(out/'primary-response.bin').read_bytes();ledger['body_sha256']=hashlib.sha256(raw).hexdigest();save()
        if response.code!=200 or not raw.startswith(b'%PDF-'):raise ValueError('Complete original PDF required')
        length=response.headers.get('Content-Length')
        if length is not None and int(length)!=len(raw):raise ValueError('Truncated source')
        with pymupdf.open(stream=raw,filetype='pdf') as doc:
            pages,numbers=inspect(doc);ledger.update(source_pages=20,source_numeric_tokens=numbers)
            inspection={'schema':'osw.pratt2000-primary-inspection.v1','source_url':URL,'body_sha256':ledger['body_sha256'],'pages':pages,'new_depth_references_admitted':0,'raw_velocity_profiles_decoded':0,'figure_digitization_performed':False}
            encoded=(json.dumps(inspection,indent=2)+'\n').encode()
            if len(raw)+len(encoded)>2200000:raise ValueError('Whole source/inspection output bound')
            (out/'inspection.json').write_bytes(encoded)
            remaining=2300000-len(raw)-len(encoded);rendered=[];skipped=[]
            for n in [11,12,13,14]:
                image=doc[n-1].get_pixmap(dpi=65).tobytes('png')
                if len(image)>remaining:skipped.append(n);continue
                (out/('page-'+str(n)+'.png')).write_bytes(image);remaining-=len(image);rendered.append(n)
            ledger.update(status='PRIMARY_PDF_CAPTURED_PENDING_SCIENTIFIC_SCOPE_REVIEW',rendered_pdf_pages=rendered,render_skipped_for_output_bound=skipped)
    except Exception as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400]);raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
