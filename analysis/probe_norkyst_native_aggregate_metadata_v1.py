"""Use one remaining metadata request on an observed aggregate resource."""
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
import discover_norkyst_native_metadata_v1 as prior

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/norkyst-native-aggregate-metadata-operator-v1.json'
FOLDER='research/source-data/norkyst-native-metadata-v1'


def plan(discovery, root_catalogue):
    receipts=discovery['transport_receipts']
    if len(receipts)!=5 or discovery['requests_attempted']!=5 or discovery['ocean_field_requests']!=0 or any(r['status']!='success' for r in receipts[:4]) or receipts[-1]['status']!='failed_no_retry':
        raise ValueError('Exactly five original requests and zero field reads required')
    parsed=prior.catalogue(root_catalogue,prior.CATALOG)
    candidates=[d for d in parsed['datasets'] if d['urlPath'].endswith('/norkyst_v3_sdepth_aggr.ncml')]
    bases={s['base'] for s in parsed['opendap_services']}
    if len(candidates)!=1 or len(bases)!=1: raise ValueError('One observed aggregate dataset/service required')
    url=next(iter(bases)).rstrip('/')+'/'+urllib.parse.quote(candidates[0]['urlPath'].lstrip('/'),safe='/')+'.dds'
    if url in {r['url'] for r in receipts}: raise ValueError('Never repeat a prior metadata request')
    return {'url':url,'resource_role':'observed_native_NcML_aggregate_metadata_not_daily_file_retry',
            'prior_requests':5,'new_requests_reserved':1,'cumulative_request_cap':6,'ocean_field_requests':0}


def main():
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin: raise ValueError('Pinned input changed:'+file)
    discovery=json.loads((ROOT/FOLDER/'discovery.json').read_bytes())
    p=plan(discovery,(ROOT/FOLDER/'catalogue-01.xml').read_bytes())
    out=ROOT/'norkyst-native-aggregate-metadata-v1';out.mkdir(exist_ok=True)
    report={'schema':'osw.norkyst-native-aggregate-metadata-probe.v1','plan':p,'transport_receipt':{},
            'ocean_field_requests':0,'decoded_ocean_values':0,'native_field_read_eligible':False,
            'daily_metadata_failure_preserved':True,'runtime_changed':False,'full_goal_complete':False}
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a,**k): return None
    failed=False
    try:
        raw=prior.read_metadata(p['url'],report['transport_receipt'],urllib.request.build_opener(NoRedirect()).open)
        (out/'aggregate.dds').write_bytes(raw)
        report.update(status='aggregate_DDS_captured_pending_attribute_and_vertical_transform_review',
                      captured_dds_file='aggregate.dds',captured_dds_sha256=hashlib.sha256(raw).hexdigest())
        print(raw.decode()[:12000])
    except Exception:
        failed=True;report['status']='aggregate_metadata_failed_no_retry_or_field_read'
    finally:
        report['cumulative_metadata_requests_attempted']=6
        (out/'probe.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
    if failed: raise SystemExit(1)


if __name__=='__main__':main()
