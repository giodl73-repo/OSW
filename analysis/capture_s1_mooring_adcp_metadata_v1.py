"""One original ERDDAP info capture; preserve the entire S1 case budget."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.request
from pathlib import Path
from capture_gaspe1991_adcp_info_v1 import describe,NoRedirect
ROOT=Path(__file__).resolve().parents[1]
URL='https://data.iadc.cnr.it/erddap/info/8e2f4c44-d784-40ed-94aa-ef5fa505761a/index.json'
OP='research/s1-mooring-observed-depth-case-operator-v1.json'

def main():
    start=float(os.environ['OSW_S1_METADATA_START']);out=ROOT/'s1-mooring-adcp-metadata-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.s1-mooring-observed-depth-case-ledger.v1','status':'RESERVED',
        'maximum_provider_operations':8,'attempted_provider_operations':0,'remaining_provider_operations':8,
        'maximum_case_raw_bytes':1600000,'maximum_case_numeric_tokens':250000,
        'minimum_selected_profiles_for_measurements':3,'maximum_selected_profiles':150,
        'maximum_selected_native_levels_per_profile':40,'maximum_case_decoded_cells':20000,
        'maximum_measurement_nodes':6000,'maximum_case_output_bytes':2400000,
        'maximum_cumulative_active_seconds':60,'native_array_values_decoded':0,'new_depth_references':0,
        'automatic_retries':0,'redirects_followed':0,'provider_case_closed':False,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Original S1 case deadline or SIGTERM')
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared producer clock required')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source input changed:'+p)
        ledger.update(status='METADATA_ATTEMPT_RESERVED_TARGET_CLOSED',source_url=URL,attempted_provider_operations=1,remaining_provider_operations=7);save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-metadata-custody/1.0','Accept':'application/json','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(300001);(out/'primary-info.json').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>300000:raise ValueError('Original metadata HTTP/byte gate')
        tokens=len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))
        if tokens+3000>250000:raise ValueError('Predecode numeric allowance')
        ledger['case_numeric_upper_bound']=tokens+3000;save()
        report=describe(json.loads(raw));title=report['global_attributes'].get('title','')
        if title!='S1 Mooring ADCP data @ 420m looking upward':raise ValueError('Exact original upward-looking dataset required')
        report.update(schema='osw.s1-mooring-adcp-variable-metadata.v1',source_url=URL,raw_sha256=ledger['raw_sha256'],source_dataset_id='8e2f4c44-d784-40ed-94aa-ef5fa505761a',current_identity_assignment_performed=False)
        encoded=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual metadata roundtrip')
        bound=2*tokens+2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',encoded))+3000
        if bound>250000 or len(raw)+len(encoded)+20000>1600000:raise ValueError('Cumulative original source-case cap')
        (out/'variable-metadata.json').write_bytes(encoded)
        ledger.update(status='ORIGINAL_METADATA_RETAINED_NATIVE_SELECTION_PENDING',case_numeric_upper_bound=bound,metadata_target_closed=True)
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['cumulative_active_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
