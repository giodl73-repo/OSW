"""One-shot original Jin2026 HTML capture; regional descriptive SAC bound only."""
import hashlib,json,os,re,signal,time,unicodedata,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2026JC024251'
OP='research/sac-jin2026-shallow-bound-operator-v1.json'
FACTS='research/sac-jin2026-shallow-bound-facts-v1.json'
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
    patterns=[r'Projected Future Changes of Australian Boundary Currents',r'10\.1029/2026JC024251',
        r'weak and steady SAC.{0,110}shallow structure\s*\(\s*<\s*250\s*m\)',
        r'Historical Mean Transports.{0,80}1993.{0,4}2023',
        r'SAC.{0,60}122.{0,30}34.{0,30}35.{0,30}250.{0,20}eastward',
        r'2071.{0,5}2090',r'CMIP6']
    for pattern in patterns:
        if not re.search(pattern,text,re.I):raise ValueError('Missing original-source context: '+pattern)
    row=facts['row']
    if (row['entity_id'],row['metric'],row['unit'])!=('current:south-australian','reported_regional_current_vertical_extent_upper_bound','m'):raise ValueError('Exact segment and descriptive bound required')
    if row['upper_bound_m']!=250 or row['upper_bound_exclusive'] is not True or row['approximate_value'] is not None:raise ValueError('Strict upper bound is not a measured depth')
    if row['statement_basis']!='introductory_regional_description_not_digitized_model_boundary' or row['source_lower_cutoff_resolved'] is not False:raise ValueError('Introductory scope and unresolved physical cutoff retained')
    if any(row[k] is not None for k in ['calendar_month','annual_range_m','uncertainty_m','thickness_m','volume_m3','range_m','observation_start','observation_end']):raise ValueError('No combined source range, dates, thickness or volume')
    if row['combined_with_legacy_over200m_as_range'] is not False or row['transport_integration_limit_is_current_bottom'] is not False or any(row['eligibility'].values()):raise ValueError('No promotion from separate source bounds or integration limits')
    tokens=len(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',text))
    if tokens>10000:raise ValueError('Source numeric-token bound')
    return [dict(row)],tokens
def main():
    start=float(os.environ['OSW_SAC_JIN2026_START']);out=ROOT/'sac-jin2026-shallow-bound-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.sac-jin2026-shallow-bound-case.v1','status':'RESERVED','provider_operation_cap':1,'attempts':0,'source_url':URL,'native_array_values_decoded':0,'new_canonical_references':0,'automatic_retries':0,'redirects_followed':0,'runtime_changed':False,'full_goal_complete':False}
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
        report={'schema':'osw.sac-jin2026-shallow-bound-descriptors.v1','source_url':URL,'source_doi':facts['source_doi'],'source_attribution':facts['source_attribution'],'source_locator':'Section1, shallow SAC structure description; Table1 is separate transport-integration context; original HTML prose, no digitization','source_license':'not_independently_qualified_original_retained_privately','raw_sha256':ledger['raw_sha256'],'facts_sha256':hashlib.sha256(factsraw).hexdigest(),'rows':rows,'caveats':facts['caveats'],'canonical_reference_admitted':False}
        encoded=(json.dumps(report,indent=2)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual descriptor roundtrip')
        assembled=len(re.findall(rb'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',encoded+factsraw))
        ledger.update(source_numeric_tokens=tokens,descriptor_numeric_tokens=assembled,metadata_numeric_upper_bound=2000,case_numeric_upper_bound=tokens+assembled+2000)
        if ledger['case_numeric_upper_bound']>250000 or len(raw)+len(encoded)+20000>2400000:raise ValueError('Cumulative case scalar/output cap')
        (out/'descriptors.json').write_bytes(encoded)
        ledger.update(status='ONE_REGIONAL_SAC_DESCRIPTIVE_UPPER_BOUND_VERIFIED',descriptor_rows=1,provider_case_closed=True,remaining_provider_operations=0,physical_bottoms_established=0,volumes_estimated=0)
    except BaseException as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
