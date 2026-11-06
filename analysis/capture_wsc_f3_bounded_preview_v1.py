"""Original published bounded PANGAEA preview; no full-file or field decode."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from capture_gaspe1991_adcp_info_v1 import NoRedirect
ROOT=Path(__file__).resolve().parents[1]
URL='https://doi.pangaea.de/10.1594/PANGAEA.800346'
OP='research/wsc-f3-observed-depth-case-operator-v1.json'

class Metadata(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.anchor=None;self.headers=[];self.header=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.anchor=[a.get('href',''),[]]
        if tag=='th':self.header=[]
    def handle_data(self,data):
        if self.anchor is not None:self.anchor[1].append(data)
        if self.header is not None:self.header.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.anchor is not None:
            self.links.append([self.anchor[0],' '.join(' '.join(self.anchor[1]).split())]);self.anchor=None
        if tag=='th' and self.header is not None:self.headers.append(' '.join(' '.join(self.header).split()));self.header=None

def preview_link(raw):
    page=Metadata();page.feed(raw.decode('utf8'))
    choices=[]
    for href,label in page.links:
        target=urllib.parse.urljoin(URL,href);u=urllib.parse.urlparse(target)
        if 'View dataset as HTML' in label:
            if u.scheme!='https' or u.netloc!='doi.pangaea.de' or u.path!='/10.1594/PANGAEA.800346' or urllib.parse.parse_qs(u.query)!={'format':['html']}:raise ValueError('Exact original bounded preview link required')
            choices.append(target)
    if len(choices)!=1:raise ValueError('One publisher-linked HTML preview required')
    return choices[0]

def main():
    start=float(os.environ['OSW_F3_CAPTURE_START']);out=ROOT/'wsc-f3-bounded-preview-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.wsc-f3-observed-depth-original-case-ledger.v1','status':'CASE_RESERVED','maximum_provider_operations':8,'attempted_provider_operations':0,'remaining_provider_operations':8,'maximum_case_raw_bytes':2000000,'maximum_case_numeric_tokens':250000,'maximum_cumulative_active_seconds':60,'minimum_selected_profiles':3,'maximum_selected_profiles':150,'maximum_selected_native_levels_per_profile':40,'maximum_case_decoded_cells':20000,'maximum_measurement_nodes':6000,'maximum_case_output_bytes':2400000,'automatic_retries':0,'redirects_followed':0,'source_responses':[],'raw_bytes':0,'case_numeric_upper_bound':5000,'native_numeric_values_decoded':0,'provider_case_closed':False,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Shared original-case deadline or SIGTERM')
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save()
    def acquire(url,name,cap):
        ledger['attempted_provider_operations']+=1;ledger['remaining_provider_operations']-=1
        row={'source_url':url,'file':name,'status':'RESERVED_TARGET_CLOSED_BEFORE_REQUEST'};ledger['source_responses'].append(row);save();response=None
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'OSW-published-preview-custody/1.0','Accept':'text/html','Accept-Encoding':'identity'})
            try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
            except urllib.error.HTTPError as error:response=error
            raw=response.read(cap+1);(out/name).write_bytes(raw)
            row.update(http_status=response.code,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());ledger['raw_bytes']+=len(raw);save()
            if response.code!=200 or len(raw)>cap or ledger['raw_bytes']>2000000:raise ValueError('Original response HTTP/byte gate')
            charge=2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))+5000
            if ledger['case_numeric_upper_bound']+charge>250000:raise ValueError('Prospective cumulative source scalar cap')
            ledger['case_numeric_upper_bound']+=charge;row['status']='ORIGINAL_RAW_RETAINED_TARGET_CLOSED';save();return raw
        finally:
            if response is not None:response.close()
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        landing=acquire(URL,'landing.html',150000)
        if b'Physical oceanography and current meter data from mooring F3-7' not in landing:raise ValueError('Exact original mooring dataset required')
        target=preview_link(landing);preview=acquire(target,'preview.html',1500000)
        page=Metadata();page.feed(preview.decode('utf8'))
        report={'schema':'osw.wsc-f3-original-bounded-preview-metadata.v1','dataset_doi':'10.1594/PANGAEA.800346','landing_url':URL,'preview_url':target,'published_preview_scope':'publisher_initial_HTML_view_first_2000_rows_not_complete_year','column_headers':page.headers,'source_responses':ledger['source_responses'],'native_numeric_values_decoded':0,'current_depth_references_admitted':0,'full_goal_complete':False}
        encoded=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual source metadata JSON roundtrip')
        (out/'preview-metadata.json').write_bytes(encoded)
        ledger.update(status='ORIGINAL_BOUNDED_PREVIEW_RETAINED_NATIVE_ANALYSIS_PENDING',targets_closed=True,whole_year_download_attempted=False)
        save()
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole output cap')
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        ledger['cumulative_active_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
