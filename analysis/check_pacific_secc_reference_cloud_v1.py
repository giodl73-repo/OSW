"""One source-scoped cloud geography case; no installed packet or ocean fields."""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/pacific-secc-reference-cloud-request-v1.json'
PREFLIGHT = 'research/pacific-secc-reference-cloud-preflight-v1.json'
INPUT = 'research/pacific-secc-western-mean-reference-path-v2-input.json'
PREVIEW = 'research/pacific-secc-western-mean-geodesic-preview-v1.json'
LAND_RECEIPT = 'research/source-data/natural-earth-land-10m-5.1.1/acquisition.json'
OUTPUT = ROOT/'.pytest_cache/pacific-secc-reference-cloud-v1'


def read(path): return json.loads((ROOT/path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value): Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')


def controls():
    if (os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('RUNNER_OS')!='Linux'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Explicit cloud working-branch case required before geography or files')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:
        raise ValueError('One low-priority CPU required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1': raise ValueError('Worker limit missing: '+key)
    request=read(REQUEST)
    if request.get('execute') is not True or request.get('max_cloud_jobs')!=1 or request.get('max_local_heavy_jobs')!=0:
        raise ValueError('Case not requested')
    for key in ['packet_load','index_load','native_build','wasm_build','browser_automation','original_ocean_field_processing','installation','main_merge']:
        if request.get(key) is not False: raise ValueError('Forbidden operation: '+key)
    if sha(ROOT/PREFLIGHT)!=request['preflight_sha256']: raise ValueError('Changed preflight')
    for p,h in read(PREFLIGHT)['input_sha256'].items():
        if sha(ROOT/p)!=h: raise ValueError('Changed frozen source: '+p)
    phase=read('research/current-gap-delivery-phase.json')
    if phase['phase']!='source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Keep the global phase disabled')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():
        raise ValueError('Clean exact source checkout required')
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))
    if remote['object']['sha']!=head: raise ValueError('Stale source case refused')
    return head


def dense(points,geod):
    result=[list(points[0])]
    for a,b in zip(points,points[1:]):
        count=max(1,math.ceil(geod.inv(*a,*b)[2]/1000))
        if count>1: result.extend([list(p) for p in geod.npts(*a,*b,count-1)])
        result.append(list(b))
    unwrapped=[result[0]]
    for lon,lat in result[1:]:
        lon+=360*round((unwrapped[-1][0]-lon)/360)
        unwrapped.append([lon,lat])
    if max(geod.inv(*a,*b)[2] for a,b in zip(unwrapped,unwrapped[1:]))>1000.00001:
        raise ValueError('Geodesic sampling exceeds1km')
    return unwrapped


def calculate(head):
    # Geographic libraries and source masks are opened only after controls().
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pyproj
    import shapefile
    import shapely
    from shapely.geometry import LineString,box,shape
    from shapely.ops import unary_union
    import xml.etree.ElementTree as ET
    from build_motion_state_join import PROVINCES,polygon_parts
    from build_cartographic_current_state_join import project
    from build_current_reference_path_candidate import periodic_geometry
    if (pyproj.__version__!='3.7.2' or shapely.__version__!='2.1.2'
            or shapefile.__version__!='2.3.1' or matplotlib.__version__!='3.10.8'):
        raise ValueError('Use pinned geographic versions')
    result={'schema':'osw.pacific-secc-reference-cloud.result.v1','status':'RUNNING','source_commit':head,
            'run_id':os.environ['GITHUB_RUN_ID'],'new_physical_measurements':0,'installed':False,
            'packet_or_wasm_loaded':False,'source_curves_digitized':False}
    OUTPUT.mkdir(parents=True,exist_ok=True);write(OUTPUT/'result.json',result)
    # The regular generator checks the coarse atlas and retains its standard outputs.
    subprocess.run([sys.executable,'analysis/build_current_reference_path_candidate.py','--input',INPUT],cwd=ROOT,check=True)
    stem=Path(INPUT).name.removesuffix('-input.json')
    candidate_path=ROOT/'research'/f'{stem}-candidate.json'
    figure_path=ROOT/'figures'/f'{stem}-candidate.svg'
    candidate=json.loads(candidate_path.read_bytes());preview=read(PREVIEW)
    if (candidate['scenario_count']!=27 or abs(candidate['nominal_reference_path_km']-preview['nominal_polyline_km'])>0.001
            or candidate['reported_approximate_reference_path_km']!=1800
            or candidate['rank_eligible_published_estimates'] is not False):
        raise ValueError('Changed route/scenario meaning or arithmetic')
    receipt=read(LAND_RECEIPT)
    if receipt['sha256']!='e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc':
        raise ValueError('Wrong retained coastline identity')
    archive_path=OUTPUT.parent/'pacific-secc-coast-source-v1'/'ne_10m_land.zip'
    archive_path.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(receipt['source_url'],timeout=45) as response:
        data=response.read(receipt['bytes']+1)
    if len(data)!=receipt['bytes'] or hashlib.sha256(data).hexdigest()!=receipt['sha256']:
        raise ValueError('Coastline provider bytes changed')
    # Retain the public package in the cloud only; never include it in compact output.
    archive_path.write_bytes(data)
    region=box(160,-14,180,-6)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if set(z.namelist())!=set(receipt['members']): raise ValueError('Wrong coastline members')
        for name,expected in receipt['members'].items():
            raw=z.read(name)
            if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
                raise ValueError('Changed coastline member: '+name)
        if z.read('ne_10m_land.VERSION.txt').decode().strip()!='5.1.1' or 'GCS_WGS_1984' not in z.read('ne_10m_land.prj').decode():
            raise ValueError('Coastline edition or CRS changed')
        pieces=[]
        with shapefile.Reader(**{k:io.BytesIO(z.read('ne_10m_land.'+k)) for k in ['shp','shx','dbf']}) as reader:
            for item in reader.iterShapes(bbox=region.bounds):
                geom=shape(item.__geo_interface__)
                if not geom.is_valid: raise ValueError('Do not repair source coast geometry')
                clipped=geom.intersection(region)
                if not clipped.is_empty: pieces.append(clipped)
    fine=unary_union(pieces)
    if fine.is_empty or not fine.is_valid: raise ValueError('Missing regional coastline')
    svg=ET.parse(PROVINCES).getroot()
    coarse=periodic_geometry(unary_union(polygon_parts(next(n.get('d') for n in svg.iter() if n.get('class')=='land-context'))))
    geod=pyproj.Geod(ellps='WGS84');checks=[];lines=[]
    for i,row in enumerate(candidate['scenarios']):
        pts=dense(row['coordinates_lon_lat'],geod);line=LineString(pts)
        if not region.covers(line):raise ValueError('Scenario left declared land-check region')
        lines.append(pts)
        checks.append({'scenario_index':i,'variant':row['route_variant_id'],'fine_land_contact':line.intersects(fine),
                       'coarse_land_contact_1km':LineString([project(*p) for p in pts]).intersects(coarse),
                       'sample_count':len(pts),'length_km':row['length_km']})
    geography={'schema':'osw.pacific-secc-reference-geography.v1','source_commit':head,'region_lon_lat':[160,-14,180,-6],
               'coast_source':LAND_RECEIPT,'coast_package_sha256':receipt['sha256'],'sample_spacing_max_km':1,
               'scenarios':checks,'all_27_clear':not any(r['fine_land_contact'] or r['coarse_land_contact_1km'] for r in checks),
               'interpretation':'Geographic screening only; no velocity continuity, current edges, physical passage or navigational clearance established.'}
    write(OUTPUT/'geography.json',geography)
    fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
    for piece in pieces:
        for polygon in ([piece] if piece.geom_type=='Polygon' else piece.geoms):
            if polygon.geom_type=='Polygon':
                x,y=polygon.exterior.xy;ax.fill(x,y,color='#c7c9bd',edgecolor='#66756e',linewidth=.35)
    for pts in lines:ax.plot([p[0] for p in pts],[p[1] for p in pts],color='#6c98ac',alpha=.3,linewidth=.7)
    nominal=dense(candidate['coordinates_lon_lat'],geod)
    ax.plot([p[0] for p in nominal],[p[1] for p in nominal],color='#a14613',linestyle='--',linewidth=1.8)
    for x,y,label in [(164,-9,'164E editorial gate'),(180,-9.5,'180E editorial gate')]:
        ax.scatter([x],[y],s=22,color='#a14613');ax.annotate(label,(x,y),xytext=(5,12) if x<180 else (-5,-22),textcoords='offset points',ha='left' if x<180 else 'right',fontsize=9)
    ax.set(xlim=(160,180.5),ylim=(-14,-6),xlabel='Longitude (degrees east; unwrapped at dateline)',ylabel='Latitude (degrees north)')
    ax.set_facecolor('#e7f2f7');ax.grid(alpha=.2)
    ax.set_title('Pacific SECC western reference reach | about1800km |27 editorial drawings\nNatural Earth5.1.1 land at1:10 million; source context: Chen and Qiu2004 Fig1b',fontsize=12)
    fig.text(.5,.005,'Schematic reference reach, not a measured current axis, whole-current length, seasonal range or source uncertainty.',ha='center',fontsize=9)
    fig.savefig(OUTPUT/'fine-geography.png',dpi=130);plt.close(fig)
    shutil.copyfile(candidate_path,OUTPUT/'candidate.json');shutil.copyfile(figure_path,OUTPUT/'candidate.svg')
    import pymupdf
    with pymupdf.open(figure_path) as doc:doc[0].get_pixmap().save(OUTPUT/'candidate.png')
    if not geography['all_27_clear']:raise ValueError('Retain every failed land scenario; do not admit this route')
    result.update(status='PASS',scenario_count=27,nominal_reference_path_km=candidate['nominal_reference_path_km'],
                  reported_reference_path_km=1800,reported_scenario_range_km=candidate['reported_scenario_range_km'],
                  both_masks_clear=True,display_state_ids=candidate['nominal_atlas_state_crossings'],
                  recommended_nasa_tile_id=candidate['recommended_nasa_tile_id'],map_visually_reviewed=False,
                  outputs={p.name:sha(p) for p in OUTPUT.iterdir() if p.name!='result.json' and p.suffix!='.zip'})
    write(OUTPUT/'result.json',result)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    head=controls()
    if not args.preflight_only:
        try:calculate(head)
        except Exception as error:
            if OUTPUT.exists():
                result_path=OUTPUT/'result.json'
                result=json.loads(result_path.read_bytes()) if result_path.exists() else {}
                result.update(status='FAIL',error=str(error),installed=False)
                write(result_path,result)
            raise
    print('PASS Pacific SECC source case'+(' preflight' if args.preflight_only else ''))


if __name__=='__main__':main()
