"""Explicit, pinned acquisition of missing NECC meridional vectors and native neighbors."""
import argparse,datetime as dt,hashlib,json,urllib.parse,urllib.request
from pathlib import Path
from necc_paired_vectors import BASE,ROOT,declaration,metadata,parse,digest
DATASET='https://oceanwatch.pifsc.noaa.gov/erddap/griddap/yearly_336c_0b32_9cd3.csv?'
AXIS='longitude[(219.666667):1:(220.333333)]'
BOUNDS='[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(12):1:(0)][(219.666667):1:(220.333333)]'
QUERY='u'+BOUNDS+',v'+BOUNDS

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def save(data):
    tmp=BASE/'acquisition.json.tmp';tmp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');tmp.replace(BASE/'acquisition.json')
def acquire():
    declaration();metadata();path=BASE/'acquisition.json'
    sources=['analysis/acquire_necc_paired_vectors.py','analysis/necc_paired_vectors.py']
    code={p:digest(ROOT/p) for p in sources};preflight=digest(BASE/'preflight.json')
    receipt=json.loads(path.read_bytes()) if path.exists() else {'schema':'osw.necc-vector-acquisition.v1','dataset_id':'yearly_336c_0b32_9cd3','version':'2017.0','preflight_sha256':preflight,'collector_and_validator_sha256':code,'status':'PARTIAL','files':{}}
    if receipt['preflight_sha256']!=preflight or receipt['collector_and_validator_sha256']!=code:raise ValueError('Changed in-flight source declaration or acquisition code')
    for name,query,limit in [('longitude.csv',AXIS,20000),('vectors.csv',QUERY,3000000)]:
        url=DATASET+urllib.parse.quote(query,safe='');target=BASE/name
        if name in receipt['files']:
            r=receipt['files'][name]
            if r['url']!=url or digest(target)!=r['sha256']:raise ValueError('Changed retained original '+name)
            continue
        if target.exists():raise ValueError('Unreceipted original exists '+name)
        started=now()
        with urllib.request.urlopen(url,timeout=90) as response:
            data=response.read(limit+1);status=response.status;resolved=response.url
        if status!=200 or len(data)>limit:raise ValueError('Unexpected source response')
        target.write_bytes(data);receipt['files'][name]={'url':url,'resolved_url':resolved,'query':query,'started_utc':started,'completed_utc':now(),'status':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};save(receipt)
    if code!={p:digest(ROOT/p) for p in sources}:raise ValueError('Acquisition code changed while source request was live')
    d=parse(BASE/'vectors.csv',BASE/'longitude.csv');receipt.update(status='COMPLETE_VALIDATED',completed_utc=now(),vector_positions=d['vector_positions'],paired_finite_positions=d['paired_finite_positions'],old_target_u_float64_values_and_masks_exact=d['old_target_values_exact'],native_longitudes_degrees_east=d['longitudes'],native_glider_or_instrument_observations=False,new_width_record_admitted=False);save(receipt)
    print('COMPLETE',receipt['vector_positions'],'vectors;',receipt['old_target_u_float64_values_and_masks_exact'],'target u values/masks exact;',receipt['paired_finite_positions'],'finite pairs')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:acquire()
    else:
        d=parse(BASE/'vectors.csv',BASE/'longitude.csv');print('OFFLINE',d['vector_positions'],'retained vectors checked')
