"""Bounded one-shot primary HTML custody and published descriptor verification."""
import csv,hashlib,io,json,os,re,signal,time,unicodedata,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/oman-2025-published-depth-operator-v1.json'
FACTS='research/oman-2025-published-depth-facts-v1.json'
URL='https://os.copernicus.org/articles/22/3369/2026/'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
def normalize(value):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',value)).strip()
def verify(raw,facts):
    parser=Text();parser.feed(raw.decode('utf8'));text=normalize(' '.join(parser.parts))
    patterns=[r'Hydrographic transformation of the Persian/Arabian Gulf outflow',
       r'51\s+Conductivity',r'9\s+and\s+18\s+July\s+2025',
       r'composite-tracer approach',r'threshold of.{0,15}0\.3',r'core is defined.{0,35}0\.55',
       r'current measurements are unavailable',
       r'top of the outflow occurs at depths of\s+50\s*[–-]\s*100\s*m',
       r'thickness of\s+10\s*[–-]\s*30\s*m',
       r'upper depth of the P/AG\s+outflow increases up to\s+170\s*m',
       r'reaching\s*[∼~]?\s*130\s*[–-]\s*140\s*m',
       r'thickness increases up to\s+200\s*m']
    for pattern in patterns:
        if not re.search(pattern,text,re.I):raise ValueError('Primary source check missing: '+pattern)
    expected=[('reported_water_mass_plume_upper_boundary_depth',50,100),('reported_water_mass_plume_upper_boundary_depth',None,170),('reported_water_mass_plume_upper_boundary_depth',130,140),('reported_water_mass_plume_thickness',10,30),('reported_water_mass_plume_thickness',None,200)]
    if [(r['metric'],r['minimum_m'],r['maximum_m']) for r in facts['rows']]!=expected:raise ValueError('Reviewed descriptor values changed')
    if len({r['id'] for r in facts['rows']})!=5 or any(facts['eligibility'].values()):raise ValueError('Identity or promotion gate')
    if facts['survey_window']!=['2025-07-09','2025-07-18'] or facts['plume_definition']!={'metric':'source_composite_tracer_PAG_water_fraction','minimum_fraction':0.3,'distinct_core_minimum_fraction':0.55}:raise ValueError('Survey or selection gate')
    numbers=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',text))
    if numbers>10000:raise ValueError('Source token budget')
    rows=[]
    for original in facts['rows']:
        row=dict(original,current_id=facts['current_id'],unit='m',survey_start=facts['survey_window'][0],survey_end=facts['survey_window'][1],source_doi=facts['source_doi'],selection_fraction=0.3,vertical_direction='positive_down_for_top_depth; thickness_is_distance',exact_position=None,vertical_datum='source_depth_datum_not_independently_qualified',lower_boundary_depth_m=None,uncertainty_m=None,annual_depth_range=None,whole_route_depth_m=None,volume_m3=None)
        rows.append(row)
    return rows,numbers
def csv_bytes(rows):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);return s.getvalue().encode('utf8')
def main():
    started=time.monotonic();out=Path('oman-2025-published-depth-v1');out.mkdir(exist_ok=False)
    ledger={'schema':'osw.oman-2025-published-depth-ledger.v1','status':'RESERVED','reserved_provider_operations':1,'attempted_provider_operations':0,'automatic_retries':0,'redirects_followed':0,'raw_native_arrays_decoded':0,'source_numeric_tokens':0,'new_canonical_references':0}
    def save():
        (out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def deadline(signum,frame):raise TimeoutError('Absolute producer deadline or SIGTERM')
    signal.signal(signal.SIGALRM,deadline);signal.signal(signal.SIGTERM,deadline);signal.alarm(60)
    save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Pinned input changed: '+p)
        if op['source_url']!=URL or op['maximum_provider_operations']!=1 or op['maximum_source_bytes']!=1000000:raise ValueError('Frozen bounds changed')
        facts=json.loads((ROOT/FACTS).read_bytes())
        ledger['attempted_provider_operations']=1;ledger['status']='ATTEMPT_RESERVED_TARGET_CLOSED';save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-document-custody/1.0','Accept':'text/html','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(1000001)
        (out/'primary-response.html').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if len(raw)>1000000 or response.code!=200:raise ValueError('Source size or HTTP gate')
        rows,tokens=verify(raw,facts);ledger['source_numeric_tokens']=tokens;save()
        report={'schema':'osw.oman-2025-published-depth-descriptors.v1','source_url':URL,'source_doi':facts['source_doi'],'source_attribution':facts['source_attribution'],'raw_sha256':ledger['raw_sha256'],'source_facts_sha256':hashlib.sha256((ROOT/FACTS).read_bytes()).hexdigest(),'rows':rows,'caveats':facts['caveats'],'eligibility':facts['eligibility']}
        encoded=(json.dumps(report,indent=2)+'\n').encode();csvraw=csv_bytes(rows)
        assert json.loads(encoded)['rows']==rows
        reread=list(csv.DictReader(io.StringIO(csvraw.decode())))
        assert len(reread)==len(rows) and [r['id'] for r in reread]==[r['id'] for r in rows]
        for expected,actual in zip(rows,reread):
            for key,value in expected.items():assert actual[key]==('' if value is None else str(value)),key
        numeric_assembly_tokens=len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',encoded))+len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',csvraw))+len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',(ROOT/FACTS).read_bytes()))
        ledger['descriptor_numeric_tokens_conservative']=numeric_assembly_tokens
        if tokens+numeric_assembly_tokens>250000 or len(raw)+len(encoded)+len(csvraw)>2300000:raise ValueError('Cumulative case output/scalar bound')
        (out/'descriptors.json').write_bytes(encoded);(out/'descriptors.csv').write_bytes(csvraw)
        ledger.update(status='PUBLISHED_DESCRIPTORS_VERIFIED',descriptor_rows=len(rows),upper_depth_rows=sum(r['metric'].endswith('boundary_depth') for r in rows),thickness_rows=sum(r['metric'].endswith('thickness') for r in rows),raw_data_files_requested=0)
    except Exception as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error));raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-started;save();signal.alarm(0)
        print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
