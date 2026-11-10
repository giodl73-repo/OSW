"""Carry original1991 case budget into one ERDDAP variable-metadata request."""
import hashlib,json,os,re,signal,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://erddap.ogsl.ca/erddap/info/mpoCourantGaspeAdcp/index.json'
OP='research/gaspe1991-adcp-info-operator-v1.json'
PRIOR='research/gaspe1991-source-metadata-ledger-v1.json'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
def describe(payload):
    t=payload.get('table',{})
    if t.get('columnNames')!=['Row Type','Variable Name','Attribute Name','Data Type','Value'] or not isinstance(t.get('rows'),list) or len(t['rows'])>2000:raise ValueError('Bounded ERDDAP info table required')
    variables={};attributes={}
    for row in t['rows']:
        if not isinstance(row,list) or len(row)!=5:raise ValueError('Five metadata columns required')
        kind,name,attribute,datatype,value=row
        if kind=='variable':
            if name in variables:raise ValueError('Duplicate variable metadata')
            variables[name]={'data_type':datatype,'attributes':{}}
        elif kind=='attribute':attributes.setdefault(name,{})[attribute]=value
        else:raise ValueError('Unexpected ERDDAP metadata row type')
    for name,v in variables.items():v['attributes']=attributes.get(name,{})
    if not variables or len(variables)>100:raise ValueError('Bounded native variable definitions required')
    return {'variables':variables,'global_attributes':attributes.get('NC_GLOBAL',{}),'metadata_only':True,'native_data_rows_decoded':0,'depth_measurements_emitted':0}
def main():
    start=float(os.environ['OSW_GASPE1991_INFO_START']);out=ROOT/'gaspe1991-adcp-info-v1';out.mkdir(exist_ok=False)
    priorraw=(ROOT/PRIOR).read_bytes();prior=json.loads(priorraw)
    if prior['status']!='ORIGINAL_RESOURCE_METADATA_RETAINED_NATIVE_SELECTION_PENDING' or prior['attempted_provider_operations']!=1 or prior['remaining_provider_operations']!=7 or prior['provider_case_closed'] is not False:raise ValueError('Original open source case required')
    ledger=dict(prior,status='ERDDAP_INFO_RESERVED',prior_metadata_ledger_sha256=hashlib.sha256(priorraw).hexdigest(),prior_raw_bytes=prior['raw_bytes'],prior_numeric_upper_bound=prior['case_numeric_upper_bound'],prior_active_seconds=prior['cumulative_active_seconds'])
    def save():(out/'ledger.json').write_bytes((json.dumps(ledger,indent=2)+'\n').encode())
    def stopped(*a):raise TimeoutError('Cumulative source deadline or SIGTERM')
    elapsed=prior['cumulative_active_seconds']+time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Original source-case cumulative clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        ledger.update(status='ERDDAP_INFO_ATTEMPT_RESERVED_TARGET_CLOSED',attempted_provider_operations=2,remaining_provider_operations=6,source_url=URL);save()
        req=urllib.request.Request(URL,headers={'User-Agent':'OSW-primary-metadata-custody/1.0','Accept':'application/json','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(300001);(out/'primary-info.json').write_bytes(raw)
        ledger.update(http_status=response.code,info_raw_bytes=len(raw),info_raw_sha256=hashlib.sha256(raw).hexdigest());save()
        if response.code!=200 or len(raw)>300000 or prior['raw_bytes']+len(raw)>1600000:raise ValueError('ERDDAP metadata HTTP/byte gate')
        tokens=len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))
        if prior['case_numeric_upper_bound']+2*tokens+3000>250000:raise ValueError('Prospective source metadata token gate')
        report=describe(json.loads(raw));report.update(schema='osw.gaspe1991-original-adcp-variable-metadata.v1',source_url=URL,raw_sha256=ledger['info_raw_sha256'])
        encoded=(json.dumps(report,indent=2)+'\n').encode()
        if json.loads(encoded)!=report:raise ValueError('Actual variable metadata roundtrip')
        bound=prior['case_numeric_upper_bound']+2*tokens+2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',encoded))+3000
        if bound>250000 or prior['raw_bytes']+len(raw)+len(encoded)+100000>1600000:raise ValueError('Original cumulative case bound')
        (out/'variable-metadata.json').write_bytes(encoded)
        ledger.update(status='ERDDAP_VARIABLE_METADATA_RETAINED_NATIVE_SELECTION_PENDING',case_numeric_upper_bound=bound,raw_bytes=prior['raw_bytes']+len(raw),metadata_target_closed=True,provider_case_closed=False)
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['cumulative_active_seconds']=prior['cumulative_active_seconds']+time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)
if __name__=='__main__':main()
