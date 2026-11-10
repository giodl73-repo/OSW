"""First raw CIOOS record capture for a bounded, new1991 Gaspé source case."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IDENTITY='ca-cioos_9acdc006-20cb-4c7e-8aae-ca1007cf9b63'
URL='https://catalogue.cioos.ca/api/3/action/package_show?id='+IDENTITY
OP='research/gaspe1991-observed-depth-source-case-operator-v1.json'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
def inventory(payload):
    if payload.get('success') is not True or not isinstance(payload.get('result'),dict):raise ValueError('Successful original CKAN record required')
    record=payload['result']
    if record.get('name')!=IDENTITY:raise ValueError('Exact original dataset identity required')
    resources=record.get('resources',[])
    if not isinstance(resources,list) or len(resources)>80:raise ValueError('Bounded resource metadata required')
    rows=[]
    for r in resources:
        if not isinstance(r,dict) or not isinstance(r.get('url'),str):raise ValueError('Explicit original resource URL required')
        rows.append({k:r.get(k) for k in ['id','name','description','format','url','size','hash','last_modified']})
    extras=record.get('extras',[])
    if not isinstance(extras,list) or len(extras)>150:raise ValueError('Bounded dataset extras required')
    origin=[]
    for e in extras:
        if isinstance(e,dict) and isinstance(e.get('value'),str) and re.search(r'(?:source|url|doi|identifier)',str(e.get('key')),re.I):origin.append({'key':e.get('key'),'value':e['value']})
    return {'dataset_name':record['name'],'dataset_title':record.get('title'),'license_id':record.get('license_id'),'resources':rows,'origin_metadata':origin,'metadata_only':True,'native_fields_inspected':False,'depth_measurements_emitted':0}
def main():
    start=float(os.environ['OSW_GASPE1991_METADATA_START']);out=ROOT/'gaspe1991-resource-metadata-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.gaspe1991-observed-depth-case-ledger.v1','status':'METADATA_RESERVED','original_provider_operation_cap':8,'attempted_provider_operations':0,'remaining_provider_operations':8,'maximum_case_raw_bytes':1600000,'maximum_case_numeric_tokens':250000,'maximum_selected_profiles':150,'minimum_selected_profiles_for_measurements':3,'maximum_selected_native_levels_per_profile':40,'maximum_case_decoded_cells':20000,'maximum_measurement_nodes':6000,'maximum_case_output_bytes':2400000,'maximum_cumulative_active_seconds':60,'automatic_retries':0,'redirects_followed':0,'native_array_values_decoded':0,'new_depth_references':0,'full_goal_complete':False}
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Source-case active deadline or SIGTERM')
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        ledger.update(status='METADATA_ATTEMPT_RESERVED_TARGET_CLOSED',attempted_provider_operations=1,remaining_provider_operations=7,source_url=URL);save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-metadata-custody/1.0','Accept':'application/json','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(1000001);(out/'primary-response.json').write_bytes(raw)
        ledger.update(http_status=response.code,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>1000000:raise ValueError('Metadata HTTP or size gate')
        tokens=len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))
        if tokens>10000:raise ValueError('Metadata numeric allowance before JSON decoding')
        ledger['reserved_metadata_numeric_upper_bound']=tokens+3000;save()
        report=inventory(json.loads(raw));report.update(schema='osw.gaspe1991-original-resource-metadata.v1',source_url=URL,raw_sha256=ledger['raw_sha256'])
        encoded=(json.dumps(report,indent=2)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual metadata roundtrip')
        bound=2*tokens+2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',encoded))+3000
        if bound>250000 or len(raw)+len(encoded)+20000>1600000:raise ValueError('Cumulative source-case metadata budget')
        (out/'resource-inventory.json').write_bytes(encoded)
        ledger.update(status='ORIGINAL_RESOURCE_METADATA_RETAINED_NATIVE_SELECTION_PENDING',case_numeric_upper_bound=bound,metadata_target_closed=True,provider_case_closed=False,resource_entries=len(report['resources']))
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['cumulative_active_seconds']=time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
