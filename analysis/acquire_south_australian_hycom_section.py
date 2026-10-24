"""Acquire exact predeclared HYCOM u/v section responses; no width admission."""
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
from urllib.parse import quote
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'research/south-australian-hycom-section-input.json'
CACHE=ROOT/'research/source-data/hycom-south-australian-2012'
BASE='https://tds.hycom.org/thredds/dodsC/GLBu0.08/reanalysis'

def sha(data):return hashlib.sha256(data).hexdigest()

def source_urls():
    cfg=json.loads(CONFIG.read_bytes())
    expected={'current_id':'south-australian','section_id':'south-australian-132e-100m','dataset':'GLBu0.08/reanalysis','component':'eastward','latitude_bounds':[-38,-32],'scope_audit':'research/south-australian-reference-path-input.json','year':2012,'time_indices':[6990,7355],'depth_index':19,'depth_m':100,'latitude_indices':[525,600],'longitude_index':3900,'longitude_east':132,'variables':['water_u','water_v']}
    if any(cfg[k]!=v for k,v in expected.items()):raise ValueError('Changed predeclared HYCOM section')
    expression=','.join(v+'[6990:1:7355][19][525:1:600][3900]' for v in cfg['variables'])
    return {'section.ascii':BASE+'.ascii?'+quote(expression,safe=''),'metadata.das':BASE+'.das','metadata.dds':BASE+'.dds'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    urls=source_urls()
    if args.acquire:
        if CACHE.exists():raise ValueError('Source cache exists; refusing overwrite')
        responses={}
        for name,url in urls.items():
            with urllib.request.urlopen(url,timeout=60) as response:responses[name]=response.read()
        if not responses['section.ascii'].startswith(b'Dataset {'):raise ValueError('Not a HYCOM ASCII response')
        CACHE.mkdir(parents=True)
        for name,data in responses.items():(CACHE/name).write_bytes(data)
        receipt={'schema':'osw.source-acquisition.v1','acquired_at':datetime.now(timezone.utc).isoformat(),'config_sha256':sha(CONFIG.read_bytes()),'product':'GOFS 3.0 HYCOM+NCODA GLBu0.08 reanalysis','provider':'Naval Oceanographic Office / Naval Research Laboratory / HYCOM.org','rights':'Freely available per official HYCOM catalog; original NC_GLOBAL distribution_statement: Approved for public release. Distribution unlimited.','catalog_url':'https://tds.hycom.org/thredds/catalogs/GLBu0.08/reanalysis.html?dataset=GLBu0.08-reanalysis','files':{name:{'url':urls[name],'bytes':len(data),'sha256':sha(data)} for name,data in responses.items()}}
        (CACHE/'acquisition.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    receipt=json.loads((CACHE/'acquisition.json').read_bytes())
    if receipt['config_sha256']!=sha(CONFIG.read_bytes()):raise ValueError('Changed HYCOM acquisition config')
    for name,url in urls.items():
        raw=(CACHE/name).read_bytes();r=receipt['files'][name]
        if r['url']!=url or r['sha256']!=sha(raw) or r['bytes']!=len(raw):raise ValueError('Changed provider response '+name)
    print(json.dumps({name:r['bytes'] for name,r in receipt['files'].items()}))

if __name__=='__main__':main()
