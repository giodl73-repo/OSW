"""Cloud-only header audit of the paper-cited TR50 velocity product."""
import hashlib
import json
from pathlib import Path
import urllib.request
import netCDF4

URL='https://data.csiro.au/dap/ws/v2/collections/62713/data/75441556'
EXPECTED_BYTES=11898461
OUT=Path('leeuwin-depth-source-audit-v1')


def main():
    OUT.mkdir(exist_ok=True)
    path=OUT/'tr50-filled-adcp.nc'
    request=urllib.request.Request(URL,headers={'Accept':'application/x-netcdf'})
    with urllib.request.urlopen(request,timeout=90) as response:
        raw=response.read(EXPECTED_BYTES+1)
    if len(raw)!=EXPECTED_BYTES:raise ValueError('Source file size differs from cited collection v3')
    path.write_bytes(raw)
    with netCDF4.Dataset(path) as dataset:
        variables={}
        for name,var in dataset.variables.items():
            variables[name]={'dimensions':list(var.dimensions),'shape':list(var.shape),'dtype':str(var.dtype),'attributes':{k:str(var.getncattr(k)) for k in var.ncattrs()}}
            if name.upper() in ['DEPTH','LATITUDE','LONGITUDE']:
                variables[name]['coordinate_values']=var[:].tolist()
        result={'schema':'osw.leeuwin-depth-source-audit.v1','source_url':URL,'collection_version':3,'collection_id':62713,'file_id':75441556,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'source_licence':'CC-BY-4.0','source_citation':'Bui and Feng, doi:10.25919/myac-yx60, collection v3, cited by Feng et al.2025 doi:10.1029/2025JC022662','global_attributes':{k:str(dataset.getncattr(k)) for k in dataset.ncattrs()},'variables':variables,'depth_values_admitted':False,'full_goal_complete':False}
    (OUT/'source-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'source_sha256':result['source_sha256'],'bytes':len(raw),'variables':{k:{'shape':v['shape'],'units':v['attributes'].get('units'),'standard_name':v['attributes'].get('standard_name')} for k,v in variables.items()}},indent=2))


if __name__=='__main__':main()
