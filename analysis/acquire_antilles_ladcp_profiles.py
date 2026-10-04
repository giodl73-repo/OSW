"""Pin NOAA AB0505 final LADCP ASCII products; default rebuild is offline.

Run with --acquire once to acquire provider bytes explicitly. Acquisition does
not admit current dimensions or equate ship tracks with current axes.
"""
import argparse
import hashlib
import json
import math
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.aoml.noaa.gov/ftp/phod/pub/WBTS/Global_Class/GC_2005_05/FINAL_ADCP_PRODUCTS/'
CACHE=ROOT/'research/source-data/noaa-wbts-ab0505'
MANIFEST=CACHE/'acquisition.json'
OUTPUT=ROOT/'research/antilles-ab0505-ladcp-profile-inventory.json'

def sha(data):return hashlib.sha256(data).hexdigest()

def parse_profile(data):
    text=data.decode('cp1252')
    metadata=dict(re.findall(r'^%\s*([\w/:]+)\s*=\s*(.*?)\s*$',text,re.M))
    required={'depth_units':'meters','velocity_units':'cm_per_sec','data_column_1':'z_depth',
              'data_column_2':'u_water_velocity_component','data_column_3':'v_water_velocity_component',
              'data_column_4':'error_velocity','data_status':'final','tides_removed_from_data':'no'}
    if any(metadata.get(k)!=v for k,v in required.items()):raise ValueError('Unsupported profile units, columns, final status or tide convention')
    lon=float(metadata['avg_position_longitude_decimal_deg']);lat=float(metadata['avg_position_latitude_decimal_deg'])
    if not math.isfinite(lon) or not -180<=lon<=180 or not math.isfinite(lat) or not -90<=lat<=90:raise ValueError('Invalid position')
    instant=datetime.strptime(metadata['avg_time_gmt_mm/dd/yy']+' '+metadata['avg_time_gmt_HH:MM:SS'],'%m/%d/%y %H:%M:%S').replace(tzinfo=timezone.utc)
    if instant.year!=2005 or instant.month!=5:raise ValueError('Unexpected cruise time')
    samples=[]
    for line in text.splitlines():
        if not line.strip() or line.startswith('%'):continue
        values=list(map(float,line.split()))
        if len(values)!=4 or not all(math.isfinite(x) for x in values):raise ValueError('Malformed sample')
        depth,u,v,error=values
        if depth<=0 or samples and depth<=samples[-1]['depth_m']:raise ValueError('Nonmonotonic depth')
        # This provider header declares no missing sentinel. Stop for review
        # rather than guessing how a newly encountered token should be masked.
        if any(abs(x)>=999 for x in [u,v,error]):raise ValueError('Undocumented velocity sentinel requires review')
        value=lambda x:x/100
        samples.append({'depth_m':depth,'eastward_m_s':value(u),'northward_m_s':value(v),'error_velocity_m_s':value(error)})
    if not samples:raise ValueError('Empty profile')
    return {'cast_id':metadata['ladcp_cast_number'],'coordinates_lon_lat':[lon,lat],
            'average_cast_time_utc':instant.isoformat().replace('+00:00','Z'),
            'depth_units':'m','velocity_units':'m s-1','metadata':metadata,'samples':samples}

def acquire():
    if MANIFEST.exists():raise ValueError('Pinned acquisition already exists; rebuild offline or use a new acquisition directory')
    CACHE.mkdir(parents=True,exist_ok=True)
    def get(relative):
        with urllib.request.urlopen(BASE+relative,timeout=30) as response:return response.read()
    index=get('ladcp_velfiles/')
    names=sorted(set(re.findall(r'href="(AB0505_\d{3}h\.vel)"',index.decode('utf-8'))))
    if not names:raise ValueError('No provider velocity filenames found')
    paths=['AB0505_ADCP_evaluation.readme']+['ladcp_velfiles/'+name for name in names]
    def save(relative):
        data=get(relative);name=relative.split('/')[-1]
        if name.endswith('.vel'):
            parsed=parse_profile(data)
            if parsed['metadata']['velocity_data_filename']!=name:raise ValueError('File identity mismatch')
        (CACHE/name).write_bytes(data)
        return {'url':BASE+relative,'file':(CACHE/name).relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':sha(data)}
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(save,paths))
    (CACHE/'provider-directory.html').write_bytes(index)
    files.append({'url':BASE+'ladcp_velfiles/','file':(CACHE/'provider-directory.html').relative_to(ROOT).as_posix(),'bytes':len(index),'sha256':sha(index)})
    manifest={'schema':'osw.source-acquisition.v1','provider':'NOAA/AOML/PhOD WBTS','product':'AB0505 final LADCP ASCII velocity profiles',
              'acquired_at_utc':datetime.now(timezone.utc).isoformat(),'encoding':'cp1252','files':files,
              'data_access_page':'https://www.aoml.noaa.gov/phod/wbts/data.php',
              'scope':'Entire published final LADCP directory, not all cruise casts. Quality cautions and absent casts are retained.'}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')

def build():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    for row in manifest['files']:
        path=ROOT/row['file']
        if sha(path.read_bytes())!=row['sha256']:raise ValueError('Pinned file checksum mismatch: '+row['file'])
    assessment='\n'.join((CACHE/'AB0505_ADCP_evaluation.readme').read_bytes().decode('cp1252').splitlines())
    comments={name:comment.strip() for name,comment in re.findall(r'(AB0505_\d{3}h\.vel)\s+([^\r\n]+)',assessment)}
    absent=[int(x) for x in re.findall(r'^\s*(\d{3})[^\r\n]*No LADCP Data\.',assessment,re.M)]
    profiles=[]
    for source in manifest['files']:
        if not source['file'].endswith('.vel'):continue
        profile=parse_profile((ROOT/source['file']).read_bytes());name=Path(source['file']).name
        if name not in comments:raise ValueError('No provider assessment: '+name)
        comment=comments[name]
        if comment not in ['Profile looks good; use these data.','High error velocities, use these data with caution.']:raise ValueError('Unrecognized quality assessment')
        profile.update({'source_file':source['file'],'source_url':source['url'],'source_sha256':source['sha256'],
                        'provider_quality_comment':comment,'provider_quality_class':'caution' if 'caution' in comment else 'usable',
                        'automatic_measurement_eligible':False})
        number=int(profile['cast_id'].rsplit('_',1)[1])
        profile['section_group']='abaco_first' if 1<=number<=23 else 'abaco_repeat' if 37<=number<=63 else 'other_cruise_section'
        profiles.append(profile)
    summary={'profile_count':len(profiles),'sample_count':sum(len(r['samples']) for r in profiles),
             'provider_usable_count':sum(r['provider_quality_class']=='usable' for r in profiles),
             'provider_caution_count':sum(r['provider_quality_class']=='caution' for r in profiles),
             'provider_no_ladcp_cast_numbers':absent,
             'earliest_average_cast_time_utc':min(r['average_cast_time_utc'] for r in profiles),
             'latest_average_cast_time_utc':max(r['average_cast_time_utc'] for r in profiles)}
    output={'schema':'osw.ladcp-profile-inventory.v1','current_id':'antilles','status':'acquired_profiles_not_scientific_measurement_admission',
            'acquisition_file':MANIFEST.relative_to(ROOT).as_posix(),'acquisition_sha256':sha(MANIFEST.read_bytes()),
            'assessment_file':(CACHE/'AB0505_ADCP_evaluation.readme').relative_to(ROOT).as_posix(),
            'summary':summary,'profiles':profiles,'whole_current_length_km':None,'whole_current_width_km':None,
            'annual_length_range_km':None,'annual_width_range_km':None,
            'method_notes':['Provider reports final LADCP processing version 10.8; readme names IMF-GEOMAR, file metadata names LDEO. Labels preserved without claiming identical processing environments.',
                            'Depth is meters, not dbar. Velocities and error velocity converted from cm/s to m/s; tide removal is explicitly no.',
                            'Provider quality comments retained; caution profiles require review and are not silently treated as clean.',
                            'Cast positions are instrument sampling locations, not current edges or current axis endpoints.',
                            'The cruise includes Abaco and NWPC sections. Casts 1-23 match the first Abaco occupation on May 4-8; casts 37-63 match the repeat on May 18-23 by date and position. Casts 64-70 are other sections and excluded from the Antilles diagnostic.',
                            'No missing-value sentinel is declared in the profile header; unexpected sentinel-like velocity values stop parsing for review.']}
    OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(summary))
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:acquire()
    build()
