"""Acquire a small archived OSCAR section explicitly; default verification is offline."""
import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'research/source-data/oscar-necc-2013-140w'
BASE='https://oceanwatch.pifsc.noaa.gov/erddap'
DATASET='yearly_336c_0b32_9cd3'
QUERY='u[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(12):1:(0)][(220)]'
URLS={'metadata.json':f'{BASE}/info/{DATASET}/index.json','section.csv':f'{BASE}/griddap/{DATASET}.csv?'+quote(QUERY,safe='')}
OUTPUT=ROOT/'research/pacific-necc-oscar-2013-section-inventory.json'


def sha(data):return hashlib.sha256(data).hexdigest()


def parse(metadata_bytes,section_bytes):
    metadata=json.loads(metadata_bytes)
    attrs={(r[1],r[2]):r[4] for r in metadata['table']['rows'] if r[0]=='attribute'}
    for key,value in {('u','units'):'m s-1',('NC_GLOBAL','version'):'2017.0',('depth','actual_range'):'15.0, 15.0'}.items():
        if attrs.get(key)!=value:raise ValueError('OSCAR product/units/depth changed')
    lines=list(csv.reader(io.StringIO(section_bytes.decode('utf-8'))))
    if lines[0]!=['time','depth','latitude','longitude','u'] or lines[1]!=['UTC','m','degrees_north','degrees_east','m s-1']:
        raise ValueError('Unexpected section columns or units')
    frames={}
    for line in lines[2:]:
        if len(line)!=5:raise ValueError('Malformed section row')
        instant=datetime.fromisoformat(line[0].replace('Z','+00:00'))
        depth,lat,lon=map(float,line[1:4]);velocity=float(line[4])
        if instant.year!=2013 or instant.utcoffset().total_seconds()!=0 or depth!=15 or lon!=220 or not 0<=lat<=12:
            raise ValueError('Unexpected section coordinate or year')
        if math.isinf(velocity):raise ValueError('Infinite current value')
        value=None if math.isnan(velocity) else velocity
        frame=frames.setdefault(line[0],{})
        if lat in frame:raise ValueError('Duplicate time/latitude')
        frame[lat]=value
    result=[]
    for stamp,profile in sorted(frames.items()):
        lats=sorted(profile)
        if len(lats)!=37 or abs(lats[0])>1e-8 or abs(lats[-1]-12)>1e-8 or any(abs(b-a-1/3)>1e-8 for a,b in zip(lats,lats[1:])):
            raise ValueError('Incomplete section latitude grid')
        result.append({'time':stamp,'samples':[{'latitude':lat,'eastward_m_s':profile[lat]} for lat in lats]})
    times=[datetime.fromisoformat(r['time'].replace('Z','+00:00')) for r in result]
    if not times or (times[-1]-times[0]).days<350 or any((b-a).total_seconds()>6*86400 for a,b in zip(times,times[1:])):
        raise ValueError('Incomplete year or unsupported temporal gap')
    if any(sum(t.month==m for t in times)<5 for m in range(1,13)):
        raise ValueError('Insufficient monthly sampling')
    return attrs,result


def build():
    manifest=json.loads((CACHE/'acquisition.json').read_text(encoding='utf-8'))
    contents={}
    for name,url in URLS.items():
        contents[name]=(CACHE/name).read_bytes()
        if manifest['files'][name]['url']!=url or manifest['files'][name]['sha256']!=sha(contents[name]):
            raise ValueError('Changed acquisition query or provider bytes')
    attrs,frames=parse(contents['metadata.json'],contents['section.csv'])
    return {'schema':'osw.current-observed-section-inventory.v1','current_id':'pacific-north-equatorial-countercurrent','status':'acquired_surface_product_section_not_measurement_admission','provider':'Earth & Space Research / NOAA PIFSC ERDDAP mirror','dataset_id':DATASET,'product_version':attrs[('NC_GLOBAL','version')],'metadata_url':URLS['metadata.json'],'data_url':URLS['section.csv'],'acquisition_file':'research/source-data/oscar-necc-2013-140w/acquisition.json','acquisition_sha256':sha((CACHE/'acquisition.json').read_bytes()),'source_files':manifest['files'],'section_longitude_degrees_east':-140,'source_longitude_degrees_east':220,'nominal_depth_coordinate_m':15,'layer_interpretation':'Satellite-derived near-surface product with nominal 15 m coordinate; not a direct 15 m instrument section or depth-resolved current.','latitude_bounds':[0,12],'grid_spacing_degrees':1/3,'time_convention':'Five-day archive samples grouped by UTC timestamp; one 2013 year, not a seasonal climatology.','frames':frames,'counts':{'times':len(frames),'latitudes_per_time':37,'values':len(frames)*37,'missing_values':sum(s['eastward_m_s'] is None for f in frames for s in f['samples'])},'whole_current_width_km':None,'annual_width_range_km':None,'source_license':attrs[('NC_GLOBAL','license')]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:
        if CACHE.exists():raise ValueError('Acquisition directory exists; refusing source overwrite')
        responses={}
        for name,url in URLS.items():
            with urllib.request.urlopen(url,timeout=45) as response:responses[name]=response.read()
        parse(responses['metadata.json'],responses['section.csv'])
        CACHE.mkdir(parents=True)
        for name,data in responses.items():(CACHE/name).write_bytes(data)
        manifest={'schema':'osw.source-acquisition.v1','acquired_at':datetime.now(timezone.utc).isoformat(),'dataset_id':DATASET,'query':QUERY,'files':{name:{'url':URLS[name],'sha256':sha(data),'bytes':len(data)} for name,data in responses.items()}}
        (CACHE/'acquisition.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    result=build();OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Verified OSCAR section: '+json.dumps(result['counts']))


if __name__=='__main__':main()
