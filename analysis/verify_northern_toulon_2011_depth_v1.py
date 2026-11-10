"""First retained original HTML capture; qualified local reported depth only."""
import hashlib,json,os,re,signal,time,unicodedata,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://os.copernicus.org/articles/14/689/2018/'
OP='research/northern-toulon-2011-depth-operator-v1.json'
FACTS='research/northern-toulon-2011-depth-facts-v1.json'
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
    patterns=[r'Wind-induced variability in the Northern Current',r'10\.5194/os-14-689-2018',
        r'2\s*[–-]\s*19\s+December\s+2011',r'During Transect\s*1\s*\(2\s*[–-]\s*4\s+December\)',
        r'zonal geostrophic velocity.{0,180}computed along the transect',
        r'offshore limit and depth of the NC are approximately.{0,20}55.{0,20}km and.{0,20}175.{0,10}m, respectively',
        r'late.summer conditions at the beginning of the experiment',
        r'For the integrated transport computation, the\s*5.{0,12}cm',r'Creative Commons Attribution 4\.0']
    for pattern in patterns:
        if not re.search(pattern,text,re.I):raise ValueError('Missing original-source context: '+pattern)
    row=facts['row']
    if (row['entity_id'],row['approximate_value'],row['unit'],row['observation_start'],row['observation_end'])!=('current:northern-mediterranean',175,'m','2011-12-02','2011-12-04'):raise ValueError('Reviewed identity/value/date changed')
    if row['metric']!='reported_local_geostrophic_current_lower_extent':raise ValueError('Local geostrophic extent required')
    if row['source_velocity_cutoff_m_s'] is not None or row['thickness_m'] is not None or any(row['eligibility'].values()):raise ValueError('Unsupported boundary or promotion')
    if row['calendar_month']!=12 or row['hydrographic_regime']!='source_described_persistent_late_summer_conditions':raise ValueError('Calendar date and physical regime must remain distinct')
    if row['annual_range_m'] is not None or row['uncertainty_m'] is not None:raise ValueError('No manufactured envelope')
    tokens=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',text))
    if tokens>10000:raise ValueError('Source numeric-token bound')
    return [dict(row)],tokens
def main():
    start=float(os.environ['OSW_NORTHERN_TOULON_START']);out=ROOT/'northern-toulon-2011-depth-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.northern-toulon-2011-depth-case.v1','status':'RESERVED','provider_operation_cap':1,'attempts':0,'source_url':URL,'native_array_values_decoded':0,'new_canonical_references':0,'automatic_retries':0,'redirects_followed':0,'runtime_changed':False,'full_goal_complete':False}
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
        raw=response.read(1000001)
        (out/'primary-response.html').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>1000000:raise ValueError('Original source HTTP or size gate')
        length=response.headers.get('Content-Length')
        if length is not None and int(length)!=len(raw):raise ValueError('Incomplete original response')
        rows,tokens=verify(raw,facts)
        report={'schema':'osw.northern-toulon-2011-depth-descriptors.v1','source_url':URL,'source_doi':facts['source_doi'],'source_attribution':facts['source_attribution'],'source_locator':'Section4.1, Transect1, Figure3c discussion; original publisher HTML prose, no plot digitization','source_license':'CC BY4.0','raw_sha256':ledger['raw_sha256'],'facts_sha256':hashlib.sha256(factsraw).hexdigest(),'rows':rows,'caveats':facts['caveats'],'canonical_reference_admitted':False}
        encoded=(json.dumps(report,indent=2)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual descriptor roundtrip')
        assembled=len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',encoded+factsraw))
        ledger.update(source_numeric_tokens=tokens,descriptor_numeric_tokens=assembled,metadata_numeric_upper_bound=2000,case_numeric_upper_bound=tokens+assembled+2000)
        if ledger['case_numeric_upper_bound']>250000 or len(raw)+len(encoded)+20000>2400000:raise ValueError('Cumulative case scalar/output cap')
        (out/'descriptors.json').write_bytes(encoded)
        ledger.update(status='ONE_LOCAL_REPORTED_GEOSTROPHIC_DEPTH_VERIFIED',descriptor_rows=1,provider_case_closed=True,remaining_provider_operations=0,physical_bottoms_established=0,volumes_estimated=0)
    except BaseException as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
