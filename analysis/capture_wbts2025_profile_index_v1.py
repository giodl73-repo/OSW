"""One original NOAA directory capture, first stage of one bounded source case."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.aoml.noaa.gov/ftp/phod/pub/WBTS/Global_Class/GC_2025_02/FINAL_ADCP_PRODUCTS/'
OP='research/wbts2025-native-depth-case-operator-v1.json'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            href=dict(attrs).get('href','')
            if re.fullmatch(r'[A-Za-z0-9_.-]+\.(?:asc|txt|dat|nc|mat|pdf|csv)',href,re.I):self.links.append(href)
def listing(raw):
    text=raw.decode('utf8');parser=Links();parser.feed(text)
    if 'Index of' not in text or 'GC_2025_02/FINAL_ADCP_PRODUCTS' not in text:raise ValueError('Exact official directory body required')
    names=sorted(set(parser.links))
    if not names or len(names)>500:raise ValueError('Bounded product listing required')
    return names
def main():
    start=float(os.environ['OSW_WBTS2025_INDEX_START']);out=ROOT/'wbts2025-profile-index-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.wbts2025-native-depth-case-ledger.v1','status':'INDEX_RESERVED','original_provider_operation_cap':8,'attempted_provider_operations':0,'remaining_provider_operations':8,'maximum_case_raw_bytes':1600000,'maximum_case_numeric_tokens':250000,'maximum_selected_profiles':6,'minimum_selected_profiles_for_measurements':3,'maximum_selected_native_levels_per_profile':40,'maximum_case_decoded_cells':20000,'maximum_case_measurement_nodes':6000,'maximum_case_output_bytes':2400000,'maximum_cumulative_active_seconds':60,'automatic_retries':0,'redirects_followed':0,'native_array_values_decoded':0,'new_depth_references':0,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Source-case active deadline or SIGTERM')
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared cloud clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        ledger.update(status='INDEX_ATTEMPT_RESERVED_TARGET_CLOSED',attempted_provider_operations=1,remaining_provider_operations=7,source_url=URL);save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-directory-custody/1.0','Accept':'text/html','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(100001);(out/'primary-index.html').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>100000:raise ValueError('Directory HTTP or size gate')
        names=listing(raw)
        result={'schema':'osw.wbts2025-official-profile-file-index.v1','source_url':URL,'raw_sha256':ledger['raw_sha256'],'filenames':names,'profile_metadata_inspected':False,'native_values_decoded':0,'depth_measurements_emitted':0}
        encoded=(json.dumps(result,indent=2)+'\n').encode()
        if json.loads(encoded)!=result:raise ValueError('Index descriptor roundtrip')
        (out/'listing.json').write_bytes(encoded)
        charge=len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw+encoded))+2000
        if charge>250000:raise ValueError('Initial source-case numeric allowance')
        ledger.update(status='ORIGINAL_INDEX_RETAINED_PROFILE_SELECTION_PENDING',case_numeric_upper_bound=charge,index_target_closed=True,provider_case_closed=False)
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['cumulative_active_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
