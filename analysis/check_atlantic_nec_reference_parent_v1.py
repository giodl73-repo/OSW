"""One cloud job: installed duplicate audit and 1 km coastal screening, no builds."""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/atlantic-nec-reference-parent-request-v1.json'
PREFLIGHT='research/atlantic-nec-reference-parent-preflight-v1.json'
WORKFLOW='.github/workflows/atlantic-nec-reference-parent-v1.yml'
OUT=ROOT/'.pytest_cache/atlantic-nec-reference-parent-v1'
ENGINE='4f52f914fa8b434731c6f6ac342040a21a92c132a8078bf66f069b64ad05541a'
LOGICAL='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'
TARGET='current:atlantic-north-equatorial'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW'+path],timeout=55))


def controls():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('RUNNER_OS')!='Linux' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('GITHUB_EVENT_NAME')!='push':
        raise ValueError('Cloud-only parent and geography audit required')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One low-priority CPU required')
    for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(name)!='1':raise ValueError('Single worker required')
    request=read(REQUEST)
    for key,value in {'schema':'osw.atlantic-nec-reference-parent-request.v1','workflow':WORKFLOW,'execute':True,'cloud_parent_packet_read_permitted':True,'coast_geography_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        if type(request.get(key)) is not type(value) or request[key]!=value:raise ValueError('Disabled or changed request: '+key)
    for key in ['index_load_permitted','native_wasm_build_permitted','browser_permitted','ocean_field_processing_permitted','working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated work enabled: '+key)
    if sha(ROOT/PREFLIGHT)!=request['preflight_sha256']:raise ValueError('Changed preflight')
    pref=read(PREFLIGHT)
    for p,pin in pref['input_sha256'].items():
        if sha(ROOT/p)!=pin:raise ValueError('Changed source: '+p)
    for p,row in pref['installed_files'].items():
        if sha(ROOT/p)!=row['sha256'] or (ROOT/p).stat().st_size!=row['bytes']:raise ValueError('Installed bytes differ: '+p)
    for p in pref['disabled_requests']:
        old=read(p)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+p)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad processing enabled')
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or api('/git/ref/heads/codex/current-measurement-gaps')['object']['sha']!=head or api('/git/ref/heads/main')['object']['sha']!=MAIN:raise ValueError('Source or main moved')
    headers=subprocess.check_output(['git','-c','core.fsmonitor=false','cat-file','-p','HEAD']).decode().split('\n\n',1)[0].splitlines()
    if [s[7:] for s in headers if s.startswith('parent ')]!=[pref['source_parent_commit']]:raise ValueError('Exact source parent required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact checkout required')
    return head


def publication_matches(rows):
    from check_current_core_gap_followup_parent_v1 import doi,title
    return [r for r in rows if any(doi(r.get(k))=='10.1016/s0967-0645(98)00109-x' for k in ['doi','url']) or any(title(r.get(k))=='themeanflowfieldofthetropicalatlanticocean' for k in ['title','label']) or 'stramma99a.pdf' in str(r.get('url','')).lower()]


def select(bundle,candidate_ids):
    from check_current_core_gap_followup_parent_v1 import projection,owns
    c=bundle['collections']
    if len(c)!=78 or sum(map(len,c.values()))!=110328 or len(c['reference_routes'])!=85 or len(c['widths'])!=190 or len(c['sources'])!=233:raise ValueError('Exact installed collection inventory differs')
    out={}
    for name in ['objects','entities','route_decisions','length_assessments','reference_routes','current_basin_memberships','widths']:
        out[name]=[projection(r) for r in c[name] if r.get('id')==TARGET or owns(r,TARGET)]
    if len(out['objects'])!=1 or len(out['entities'])!=1 or len(out['route_decisions'])!=1:raise ValueError('Unique installed owner and planning decision required')
    out['publication_candidates']=publication_matches(c['sources'])
    out['candidate_id_matches']=[{'collection':name,'record':projection(r)} for name,rows in c.items() for r in rows if r.get('id') in candidate_ids]
    owner=next(r for r in c['objects'] if r['id']==TARGET)
    out['owner_sources']=[r for r in c['sources'] if r['id'] in owner.get('source_ids',[])]
    return out


def parent_audit():
    from query_packet import descriptors,read_bundle_bytes
    if sha(ROOT/'almanac/query-engine.manifest.json')!=ENGINE:raise ValueError('Wrong installed manifest')
    manifest=read('almanac/query-engine.manifest.json');descriptor=read('almanac/query-data.json')
    if descriptor['logical_sha256']!=LOGICAL or descriptor['logical_byte_length']!=195361434 or sha(ROOT/'almanac/query-data.json')!=manifest['sha256']['almanac/query-data.json']:raise ValueError('Wrong installed packet')
    parts=descriptors(descriptor)
    if len(parts)!=12 or any(manifest['sha256'].get('almanac/'+p['path'])!=p['sha256'] for p in parts):raise ValueError('Changed part inventory')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if len(raw)!=195361434 or hashlib.sha256(raw).hexdigest()!=LOGICAL:raise ValueError('Changed logical bytes')
    bundle=json.loads(raw);del raw
    prepared=read('research/atlantic-nec-schematic-reference-reaches-prepared-v1.json')
    profile=read('research/pacific-sec-sun-2025-core-migration-profile-prepared-v1.json')
    candidate_ids={r['id'] for r in prepared['routes']}|{r['id'] for r in profile['rows']}
    if len(candidate_ids)!=26:raise ValueError('Both prepared sub-batches required')
    selected=select(bundle,candidate_ids)
    from check_current_core_gap_followup_parent_v1 import projection,owns
    selected['sun_2025_source_candidates']=[projection(r) for r in bundle['collections']['sources'] if 's40562-025-00393-7' in str(r).lower()]
    selected['pacific_sec_existing_records']={name:[projection(r) for r in bundle['collections'][name] if r.get('id')=='current:pacific-south-equatorial' or owns(r,'current:pacific-south-equatorial')] for name in ['objects','entities','reference_routes','widths','length_assessments']}
    selected['prepared_profile_ids_checked']=24
    encoded=(json.dumps(selected,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    if len(encoded)>400000:raise ValueError('Selected metadata exceeds bound')
    (OUT/'selected-records.json').write_bytes(encoded)
    return {'collections':len(bundle['collections']),'records':sum(map(len,bundle['collections'].values())),
        'selected_records_sha256':hashlib.sha256(encoded).hexdigest(),'selected_records_bytes':len(encoded),
        'publication_candidate_count':len(selected['publication_candidates']),'existing_owner_reference_routes':len(selected['reference_routes']),
        'candidate_id_matches':len(selected['candidate_id_matches']),'packet_parts_verified':12,
        'prepared_core_migration_ids_checked':24,'core_migration_publication_candidates':len(selected['sun_2025_source_candidates'])}


def geography():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pyproj,shapefile,shapely
    from shapely.geometry import LineString,box,shape
    from shapely.ops import unary_union
    import xml.etree.ElementTree as ET
    from build_motion_state_join import PROVINCES,polygon_parts
    from build_cartographic_current_state_join import project
    from check_pacific_secc_reference_cloud_v1 import dense
    import atlantic_nec_reference_reaches_v1 as reaches
    if pyproj.__version__!='3.7.2' or shapely.__version__!='2.1.2' or shapefile.__version__!='2.3.1' or matplotlib.__version__!='3.10.8':raise ValueError('Pinned geographic versions required')
    source=read(reaches.INPUT);prepared=read(reaches.OUTPUT);fresh=reaches.prepare(source)
    if any(prepared.get(k)!=v for k,v in fresh.items()):raise ValueError('Prepared arithmetic differs')
    if prepared['input_sha256']!=sha(ROOT/reaches.INPUT):raise ValueError('Prepared source differs')
    receipt=read('research/source-data/natural-earth-land-10m-5.1.1/acquisition.json')
    if receipt['sha256']!='e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc':raise ValueError('Wrong coast source')
    with urllib.request.urlopen(receipt['source_url'],timeout=45) as response:raw=response.read(receipt['bytes']+1)
    if len(raw)!=receipt['bytes'] or hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Coast package changed')
    region=box(-66,8,-20,24);pieces=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(receipt['members']):raise ValueError('Coast members differ')
        for name,pin in receipt['members'].items():
            data=z.read(name)
            if len(data)!=pin['bytes'] or hashlib.sha256(data).hexdigest()!=pin['sha256']:raise ValueError('Coast member changed')
        if z.read('ne_10m_land.VERSION.txt').decode().strip()!='5.1.1' or 'GCS_WGS_1984' not in z.read('ne_10m_land.prj').decode():raise ValueError('Wrong coast edition or CRS')
        with shapefile.Reader(**{k:io.BytesIO(z.read('ne_10m_land.'+k)) for k in ['shp','shx','dbf']}) as reader:
            for item in reader.iterShapes(bbox=region.bounds):
                geom=shape(item.__geo_interface__)
                if not geom.is_valid:raise ValueError('Invalid original land geometry; no repair permitted')
                clipped=geom.intersection(region)
                if not clipped.is_empty:pieces.append(clipped)
    fine=unary_union(pieces)
    if fine.is_empty or not fine.is_valid:raise ValueError('Missing regional land')
    svg=ET.parse(PROVINCES).getroot()
    coarse=unary_union(polygon_parts(next(n.get('d') for n in svg.iter() if n.get('class')=='land-context')))
    checks=[];lines=[]
    for i,case in enumerate(prepared['editorial_sensitivity_cases']):
        route=next(r for r in source['routes'] if r['id']==case['route_id'])
        coords=reaches.truncate(route['support_waypoints_lon_lat'],case['west_gate'])
        coords=[[lon,lat+case['uniform_shift_degrees']+(case['interior_shift_degrees'] if 0<j<len(coords)-1 else 0)] for j,(lon,lat) in enumerate(coords)]
        points=dense(coords,reaches.GEOD);line=LineString(points)
        if not region.covers(line):raise ValueError('Scenario left coast region')
        if abs(reaches.length_km(coords)-case['reference_length_km'])>.000501:raise ValueError('Changed scenario length')
        checks.append({'scenario_index':i,'route_id':case['route_id'],'fine_land_contact':line.intersects(fine),
            'coarse_land_contact':LineString([project(*p) for p in points]).intersects(coarse),'sample_count':len(points)})
        lines.append(points)
    result={'status':'PASS' if not any(r['fine_land_contact'] or r['coarse_land_contact'] for r in checks) else 'FAIL',
        'scenarios':checks,'scenario_count':len(checks),'region_lon_lat':[-66,8,-20,24],'sample_spacing_max_km':1,
        'coast_package_sha256':receipt['sha256'],'nominal_reference_lengths_km':[r['calculated_reference_length_km'] for r in prepared['routes']],
        'interpretation':'Geographic screening of editorial drawings only; no physical current axis, boundaries, uncertainty or state membership established.'}
    write(OUT/'geography.json',result)
    fig,ax=plt.subplots(figsize=(11,4.5));fig.subplots_adjust(bottom=.23,top=.86)
    for piece in pieces:
        for poly in ([piece] if piece.geom_type=='Polygon' else piece.geoms):
            if poly.geom_type=='Polygon':x,y=poly.exterior.xy;ax.fill(x,y,color='#c7c9bd',edgecolor='#66756e',linewidth=.3)
    for points in lines:ax.plot([p[0] for p in points],[p[1] for p in points],color='#6c98ac',alpha=.2,linewidth=.6)
    for route,color in zip(prepared['routes'],['#006e80','#a14613']):
        points=dense(route['coordinates_lon_lat'],reaches.GEOD)
        ax.plot([p[0] for p in points],[p[1] for p in points],color=color,label=route['phase'].replace('_',' '),linewidth=1.8)
    ax.set(xlim=(-66,-20),ylim=(8,24),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)')
    ax.set_facecolor('#e7f2f7');ax.grid(alpha=.2);ax.legend();ax.set_title('Atlantic NEC interior reach | 36 editorial drawings and gate choices')
    fig.text(.5,.035,'Nominal gates:0Â°â€“35Â°W. About3900km per reach. Geographic screening only; whole-current length remains unresolved.',ha='center',fontsize=9)
    fig.savefig(OUT/'geography.png',dpi=120);plt.close(fig)
    if result['status']!='PASS' or len(checks)!=36:raise ValueError('Retain failed scenarios; no partial geography admission')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    head=controls()
    if args.preflight_only:print('PASS_FROZEN_PARENT_GEOGRAPHY_PREFLIGHT');return
    OUT.mkdir(parents=True,exist_ok=False)
    parent=parent_audit();coast=geography()
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Tracked files changed')
    write(OUT/'result.json',{'schema':'osw.atlantic-nec-reference-parent-result.v1','status':'PASS_READ_ONLY_PARENT_AND_GEOGRAPHY',
        'source_commit':head,'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'logical_sha256':LOGICAL,'engine_manifest_sha256':ENGINE,'parent_audit':parent,'all_36_scenarios_clear_both_masks':coast['status']=='PASS',
        'packet_loaded_only_in_cloud':True,'index_loaded':False,'native_wasm_built':False,'ocean_fields_acquired':False,
        'installed':False,'full_goal_complete':False})


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:2000],'source_commit':os.environ.get('GITHUB_SHA'),'installed':False})
        raise
