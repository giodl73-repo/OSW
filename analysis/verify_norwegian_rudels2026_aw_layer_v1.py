"""First retained original review HTML; advected Atlantic-water layer thickness only."""
import hashlib,json,os,re,signal,time,unicodedata,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://os.copernicus.org/articles/22/3287/2026/'
OP='research/norwegian-rudels2026-aw-layer-operator-v1.json'
FACTS='research/norwegian-rudels2026-aw-layer-facts-v1.json'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
def normalize(text):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',text)).strip()
def verify(raw,facts):
    parser=Text();parser.feed(raw.decode('utf8'));text=normalize(' '.join(parser.parts))
    patterns=[r'The circulation and water mass',r'10\.5194/os-22-3287-2026',
        r'thickness of the Atlantic water layer entering the Norwegian Sea is\s*300\s*[–-]\s*400\s*m',
        r'Atlantic water flows north as the Norwegian Atlantic Current in two branches',
        r'One follows the continental slope',r'second branch separates from the slope at the',
        r'Creative Commons Attribution 4\.0']
    for pattern in patterns:
        if not re.search(pattern,text,re.I):raise ValueError('Missing original-source context: '+pattern)
    row=facts['row']
    if (row['entity_id'],row['metric'],row['unit'])!=('current:norwegian','reported_advected_atlantic_water_layer_thickness','m'):raise ValueError('Parent current and water-mass thickness metric required')
    if row['water_mass_thickness_range_m']!=[300,400] or row['approximate_value'] is not None or row['thickness_m'] is not None:raise ValueError('Source water-mass range is not an exact physical current thickness')
    if row['evidence_kind']!='published_review_synthesis' or row['independent_direct_observation'] is not False or row['branch_assignment_performed'] is not False:raise ValueError('Review and parent/branch scope required')
    if any(row[k] is not None for k in ['calendar_month','observation_start','observation_end','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m','volume_m3']):raise ValueError('No invented dates, boundaries or volume')
    if any(row['eligibility'].values()):raise ValueError('No physical, whole-route or temporal promotion')
    tokens=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',text))
    if tokens>10000:raise ValueError('Source numeric-token bound')
    return [dict(row)],tokens
def main():
    start=float(os.environ['OSW_NORWEGIAN_RUDELS2026_START']);out=ROOT/'norwegian-rudels2026-aw-layer-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.norwegian-rudels2026-aw-layer-case.v1','status':'RESERVED','provider_operation_cap':1,'attempts':0,'source_url':URL,'native_array_values_decoded':0,'new_canonical_references':0,'automatic_retries':0,'redirects_followed':0,'runtime_changed':False,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Absolute case deadline or SIGTERM')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped)
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared case clock')
    signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for path,digest in op['input_sha256'].items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen input changed: '+path)
        if op['source_url']!=URL or op['maximum_provider_operations']!=1:raise ValueError('Source reservation changed')
        factsraw=(ROOT/FACTS).read_bytes();facts=json.loads(factsraw)
        ledger.update(attempts=1,status='ATTEMPT_RESERVED_TARGET_CLOSED');save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-source-custody/1.0','Accept':'text/html','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(1900001)
        (out/'primary-response.html').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>1900000:raise ValueError('Original source HTTP or size gate')
        length=response.headers.get('Content-Length')
        if length is not None and int(length)!=len(raw):raise ValueError('Incomplete original response')
        rows,tokens=verify(raw,facts)
        report={'schema':'osw.norwegian-rudels2026-aw-layer-descriptors.v1','source_url':URL,'source_doi':facts['source_doi'],'source_attribution':facts['source_attribution'],'source_locator':'Section4, paragraph contrasting Bering Strait and Greenland-Scotland Ridge inflows; original review HTML prose, no plot digitization','source_license':'CC BY4.0','raw_sha256':ledger['raw_sha256'],'facts_sha256':hashlib.sha256(factsraw).hexdigest(),'rows':rows,'caveats':facts['caveats'],'canonical_reference_admitted':False}
        encoded=(json.dumps(report,indent=2)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual descriptor roundtrip')
        assembled=len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',encoded+factsraw))
        ledger.update(source_numeric_tokens=tokens,descriptor_numeric_tokens=assembled,metadata_numeric_upper_bound=2000,case_numeric_upper_bound=tokens+assembled+2000)
        if ledger['case_numeric_upper_bound']>250000 or len(raw)+len(encoded)+20000>2400000:raise ValueError('Cumulative case scalar/output cap')
        (out/'descriptors.json').write_bytes(encoded)
        ledger.update(status='ONE_ADVECTED_AW_LAYER_THICKNESS_RANGE_VERIFIED',descriptor_rows=1,provider_case_closed=True,remaining_provider_operations=0,physical_bottoms_established=0,volumes_estimated=0)
    except BaseException as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
