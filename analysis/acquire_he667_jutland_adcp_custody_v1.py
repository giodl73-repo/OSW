"""One bounded HE667 source screen, retaining raw bytes before header inspection."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/he667-jutland-adcp-custody-operator-v1.json'
LANDING='https://doi.pangaea.de/10.1594/PANGAEA.988085'
BASENAME='HE667_OceanSurveyor_150kHz_ADCP.nc'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.extend(v for k,v in attrs if k=='href' and v)
def observed_link(raw):
    if len(raw)>250000:raise ValueError('Metadata response byte cap')
    p=Links();p.feed(raw.decode('utf8'))
    matches={x for x in p.links if x.startswith('https://download.pangaea.de/') and x.endswith('/'+BASENAME)}
    if len(matches)!=1:raise ValueError('One exact observed NetCDF link required')
    return matches.pop()
def size_gate(headers):
    value=next((v for k,v in headers.items() if k.lower()=='content-length'),None)
    if not value or not value.isdigit():return 'SOURCE_SIZE_UNRESOLVED_NO_FIELDS',None
    size=int(value)
    return ('SOURCE_WITHIN_OUTPUT_CUSTODY_CAP' if 0<size<=1900000 else 'SOURCE_EXCEEDS_OUTPUT_CUSTODY_CAP_NO_FIELDS'),size
def header_only(dataset):
    return {'dimensions':{n:{'length':len(d),'unlimited':d.isunlimited()} for n,d in dataset.dimensions.items()},
        'variables':{n:{'dimensions':list(v.dimensions),'shape':list(v.shape),'dtype':str(v.dtype),'units':str(getattr(v,'units',''))[:200],'long_name':str(getattr(v,'long_name',''))[:250]} for n,v in dataset.variables.items()},
        'attributes':{k:str(dataset.getncattr(k))[:500] for k in dataset.ncattrs() if k.lower() in ['title','source','history','institution','references','comment','conventions']},'native_array_values_decoded':0,'measurement_profiles_selected':0}
def main():
    import netCDF4
    out=ROOT/'he667-jutland-adcp-custody-v1';out.mkdir(exist_ok=False)
    start=float(os.environ['OSW_HE667_CUSTODY_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared cloud phase clock')
    ledger={'schema':'osw.he667-adcp-source-custody-ledger.v1','status':'RESERVED','provider_operation_cap':3,'operations':[],'raw_response_bytes':0,'native_array_values_decoded':0,'selected_native_levels':0,'measurement_profiles_selected':0,'new_depth_references':0,'runtime_changed':False,'full_goal_complete':False}
    def save():
        p=out/'ledger.json';t=p.with_suffix('.tmp');t.write_bytes((json.dumps(ledger,indent=2)+'\n').encode());os.replace(t,p)
    def stopped(*a):raise TimeoutError('Absolute HE667 source deadline or SIGTERM')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(90);save()
    opener=urllib.request.build_opener(NoRedirect())
    def request(url,method,name,cap):
        if len(ledger['operations'])>=3:raise ValueError('Shared provider-operation cap')
        row={'url':url,'method':method,'status':'RESERVED_TARGET_CLOSED','body_bytes':0};ledger['operations'].append(row);save()
        req=urllib.request.Request(url,method=method,headers={'User-Agent':'OSW-bounded-source-custody/1.0','Accept-Encoding':'identity'})
        try:response=opener.open(req,timeout=25)
        except urllib.error.HTTPError as error:response=error
        with response:
            row.update(http_status=response.code,headers=dict(response.headers.items()));save()
            if method=='HEAD':row['status']='METADATA_HEADERS_RETAINED';save();return response.code,row['headers'],None
            path=out/name
            with path.open('xb') as f:
                while True:
                    chunk=response.read(min(65536,cap+1-row['body_bytes']))
                    if not chunk:break
                    f.write(chunk);row['body_bytes']+=len(chunk);ledger['raw_response_bytes']+=len(chunk)
                    if row['body_bytes']>cap or ledger['raw_response_bytes']>7000000:raise ValueError('Cumulative response/body byte cap')
            raw=path.read_bytes();row.update(status='RAW_BYTES_RETAINED',sha256=hashlib.sha256(raw).hexdigest());save()
            return response.code,row['headers'],raw
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        code,headers,raw=request(LANDING,'GET','landing-response.html',250000)
        if code!=200:raise ValueError('Original landing metadata not available')
        url=observed_link(raw);ledger['observed_native_file_url']=url;save()
        code,headers,_=request(url,'HEAD',None,0)
        if code!=200:ledger['status']='NATIVE_METADATA_HTTP_FAILURE_NO_FIELD_GET';return
        status,size=size_gate(headers);ledger.update(status=status,declared_native_file_bytes=size);save()
        if status!='SOURCE_WITHIN_OUTPUT_CUSTODY_CAP':return
        code,headers,raw=request(url,'GET','source.nc',1900000)
        if code!=200 or len(raw)!=size or not (raw.startswith(b'CDF') or raw.startswith(b'\x89HDF')):raise ValueError('Complete exact original NetCDF required')
        with netCDF4.Dataset(out/'source.nc') as ds:report=header_only(ds)
        metadata=(json.dumps(report,indent=2)+'\n').encode()
        metadata_numbers=len(re.findall(rb'(?<![A-Za-z])\d+(?:\.\d+)?',metadata))
        if metadata_numbers>10000 or len(metadata)>100000:raise ValueError('Header-only metadata bounds')
        (out/'native-header.json').write_bytes(metadata);ledger.update(status='RAW_NATIVE_FILE_RETAINED_HEADER_ONLY_NO_ARRAYS',native_header_numeric_tokens_conservative=metadata_numbers)
        if sum(p.stat().st_size for p in out.iterdir() if p.is_file())>2350000:raise ValueError('Whole custody output chunk cap')
    except BaseException as error:
        ledger.update(status='FAILED_NO_RETRY',error_type=type(error).__name__,error=str(error)[:400]);raise
    finally:
        ledger['elapsed_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
