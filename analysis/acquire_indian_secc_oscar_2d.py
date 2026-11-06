"""Preserve surrounding vectors and prove two historical native slices exact."""
import argparse,csv,hashlib,io,json,tempfile,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/oscar-indian-secc-2d-2013'
OLD=ROOT/'research/source-data/oscar-indian-secc-1995-2016'
PROTOCOL='plans/indian-secc-oscar-2d-source-protocol-v1.md'
OPERATOR='analysis/acquire_indian_secc_oscar_2d.py'
BASE='https://oceanwatch.pifsc.noaa.gov/erddap'
DATASET='yearly_336c_0b32_9cd3'
LIMIT=50_000_000
NY,NX=37,121

def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(d):return (json.dumps(d,indent=2,allow_nan=False)+'\n').encode()
def urls():
    bounds='[(2013-01-01T00:00:00Z):1:(2013-12-28T00:00:00Z)][(15)][(2):1:(-10)][(50):1:(90)]'
    return {'metadata.json':BASE+'/info/'+DATASET+'/index.json',
            'vectors.csv':BASE+'/griddap/'+DATASET+'.csv?'+quote(','.join(c+bounds for c in ['u','v']),safe='')}

def baseline():
    receipt=json.loads((OLD/'acquisition.json').read_bytes());result={}
    for name in ['indian-secc-80p333e.csv','indian-secc-80p667e.csv']:
        raw=(OLD/name).read_bytes()
        if digest(raw)!=receipt['files'][name]['sha256']:raise ValueError('Changed historical source slice')
        reader=csv.reader(io.StringIO(raw.decode()));next(reader);next(reader)
        rows={}
        for r in reader:
            if r[0].startswith('2013-') and -10<=float(r[2])<=0:
                key=(r[0],float(r[2]));value=tuple(map(float,r[1:]))
                if key in rows:raise ValueError('Duplicate historical vector')
                rows[key]=value
        if len(rows)!=72*31:raise ValueError('Changed historical overlap support')
        result[name]=rows
    clocks=sorted({t for t,_ in result['indian-secc-80p333e.csv']})
    if len(clocks)!=72 or {t for t,_ in result['indian-secc-80p667e.csv']}!=set(clocks):raise ValueError('Historical clocks disagree')
    return result,clocks

def parse(metadata,raw,previous=None):
    attrs={(r[1],r[2]):r[4] for r in json.loads(metadata)['table']['rows'] if r[0]=='attribute'}
    for k,wanted in {('u','units'):'m s-1',('v','units'):'m s-1',('NC_GLOBAL','version'):'2017.0',('depth','actual_range'):'15.0, 15.0'}.items():
        if attrs.get(k)!=wanted:raise ValueError('Changed OSCAR version/units/depth')
    if 'may be used and redistributed for free' not in attrs.get(('NC_GLOBAL','license'),''):raise ValueError('Missing source license')
    previous,clocks=baseline() if previous is None else previous
    reader=csv.reader(io.StringIO(raw.decode('utf-8')))
    if next(reader,None)!=['time','depth','latitude','longitude','u','v'] or next(reader,None)!=['UTC','m','degrees_north','degrees_east','m s-1','m s-1']:raise ValueError('Changed vector columns/units')
    u=np.full((len(clocks),NY,NX),np.nan);v=np.full_like(u,np.nan)
    lat=np.full(NY,np.nan);lon=np.full(NX,np.nan);count=0
    for count,r in enumerate(reader,1):
        if len(r)!=6 or count>u.size:raise ValueError('Malformed or extra source row')
        ti,rest=divmod(count-1,NY*NX);yi,xi=divmod(rest,NX)
        depth,y,x,e,n=map(float,r[1:])
        if r[0]!=clocks[ti] or depth!=15 or abs(y-(2-yi/3))>1e-7 or abs(x-(50+xi/3))>1e-7:raise ValueError('Changed source grid/order/clock/depth')
        if np.isinf(e) or np.isinf(n):raise ValueError('Infinite source velocity')
        if ti==0 and xi==0:lat[yi]=y
        if ti==0 and yi==0:lon[xi]=x
        if y!=lat[yi] or x!=lon[xi]:raise ValueError('Inconsistent coordinate across rows')
        u[ti,yi,xi]=e;v[ti,yi,xi]=n
    if count!=u.size:raise ValueError('Incomplete rectangular source cube')
    comparison=0
    for name,old in previous.items():
        x=next(iter(old.values()))[2];xi=np.where(lon==x)[0]
        if len(xi)!=1:raise ValueError('Missing historical longitude')
        for (t,y),values in old.items():
            yi=np.where(lat==y)[0]
            if len(yi)!=1:raise ValueError('Missing historical latitude')
            ti=clocks.index(t);a=np.array([u[ti,yi[0],xi[0]],v[ti,yi[0],xi[0]]],dtype='<f8');b=np.array(values[-2:],dtype='<f8')
            if not np.array_equal(np.isnan(a),np.isnan(b)):raise ValueError('Changed historical masks')
            finite=np.isfinite(b)
            if not np.array_equal(a[finite].view('<u8'),b[finite].view('<u8')):raise ValueError('Changed historical finite vector bits')
            comparison+=1
    paired=np.isfinite(u)&np.isfinite(v)
    quality={'source_times':len(clocks),'latitude_positions':NY,'longitude_positions':NX,'vector_positions':int(u.size),
             'finite_pairs':int(paired.sum()),'both_missing':int((np.isnan(u)&np.isnan(v)).sum()),
             'one_component_missing':int((np.isnan(u)^np.isnan(v)).sum()),'historical_overlap_vectors':comparison,
             'historical_finite_bits_masks_coordinates_and_clocks_exact':True}
    return {'times':clocks,'latitude':lat,'longitude':lon,'u':u,'v':v},quality

def load():
    receipt=json.loads((DIRECTORY/'acquisition.json').read_bytes());archive=(DIRECTORY/'source-responses.zip').read_bytes()
    if digest(archive)!=receipt['archive_sha256']:raise ValueError('Changed surrounding source archive')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        if z.namelist()!=['metadata.json','vectors.csv']:raise ValueError('Changed source archive members')
        members={n:z.read(n) for n in z.namelist()}
    for n,b in members.items():
        r=receipt['files'][n]
        if r['url']!=urls()[n] or r['bytes']!=len(b) or r['sha256']!=digest(b):raise ValueError('Changed archived source response')
    return parse(members['metadata.json'],members['vectors.csv'])

def acquire():
    if DIRECTORY.exists():raise ValueError('Source directory exists; refusing overwrite')
    paths=[PROTOCOL,OPERATOR,(OLD/'acquisition.json').relative_to(ROOT).as_posix()]
    pins={p:digest((ROOT/p).read_bytes()) for p in paths};received={};receipts={}
    cache=ROOT/'.pytest_cache/indian-secc-2d-downloads';cache.mkdir(parents=True,exist_ok=True)
    for name,url in urls().items():
        saved=cache/(name+'.receipt.json')
        if saved.exists():
            r=json.loads(saved.read_bytes());b=(cache/name).read_bytes()
            if r['url']!=url or r['sha256']!=digest(b) or r['bytes']!=len(b):raise ValueError('Changed cached response; refusing replacement')
            received[name]=b;receipts[name]=r;continue
        started=datetime.now(timezone.utc).isoformat()
        with urllib.request.urlopen(url,timeout=90) as response:
            b=response.read(LIMIT+1)
            if response.status!=200 or len(b)>LIMIT:raise ValueError('Unexpected source HTTP status/size')
            r={'url':url,'resolved_url':response.url,'http_status':response.status,'started_utc':started,
               'completed_utc':datetime.now(timezone.utc).isoformat(),'bytes':len(b),'sha256':digest(b),
               'download_collector_sha256':pins[OPERATOR]}
        (cache/name).write_bytes(b);saved.write_bytes(encoded(r));received[name]=b;receipts[name]=r
    arrays,quality=parse(received['metadata.json'],received['vectors.csv'])
    if pins!={p:digest((ROOT/p).read_bytes()) for p in pins}:raise ValueError('Selection/collector changed during acquisition')
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in ['metadata.json','vectors.csv']:
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,received[name])
    archive=buffer.getvalue()
    receipt={'schema':'osw.indian-secc-oscar-2d-acquisition.v1','status':'COMPLETE_VALIDATED','dataset_id':DATASET,
        'product_version':'2017.0','input_sha256':pins,'files':receipts,'archive_sha256':digest(archive),'archive_bytes':len(archive),
        'quality':quality,'new_current_dimension_admitted':False,
        'attribution':'OSCAR third-degree surface currents2017.0, Earth & Space Research / NOAA OceanWatch ERDDAP. Original metadata retained.',
        'source_license':'Provider metadata permits free use and redistribution with accuracy/use disclaimers; see archived NC_GLOBAL license.'}
    DIRECTORY.parent.mkdir(exist_ok=True,parents=True)
    with tempfile.TemporaryDirectory(dir=DIRECTORY.parent) as temporary:
        staging=Path(temporary)/DIRECTORY.name;staging.mkdir();(staging/'source-responses.zip').write_bytes(archive)
        (staging/'acquisition.json').write_bytes(encoded(receipt));staging.rename(DIRECTORY)
    print(json.dumps(quality),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--acquire',action='store_true');a=p.parse_args()
    if a.acquire:acquire()
    else:print(json.dumps(load()[1]))
