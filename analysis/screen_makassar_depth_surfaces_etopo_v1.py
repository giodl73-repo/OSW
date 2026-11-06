"""Bounded new terrain context; never clip a current contour to the bed."""
import copy,csv,hashlib,io,json,math,os,re,signal,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
import rasterio
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery,numeric_tokens

ROOT=Path(__file__).resolve().parents[1]
OP='research/makassar-etopo-terrain-screen-operator-v1.json'
SOURCE='research/barents-makassar-conditional-depth-surfaces-v1.json'
SOURCE_SHA='99c2c3007df7613950d77adbe611c2ab4f826579e086964590a76b0fb03ccdec'
SERVICE='https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_global_mosaic/ImageServer'
STEP=.04
OFFSETS=(-20,0,20)
RADIUS=6371008.8

def finite(v):return type(v) in (int,float) and math.isfinite(v)
def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def source_patches(source):
    if source['schema']!='osw.barents-makassar-conditional-regional-depth-surfaces.v1' or source['counts']['conditional_depth_surface_patches']!=59:raise ValueError('Exact frozen depth surface cohort')
    out=[]
    for si,s in enumerate(source['segments']):
        for ci,c in enumerate(s['cells']):
            for pi,p in enumerate(c['patches']):
                if s['entity_id']!='current:indonesian-throughflow' or s['physical_volume_km3'] is not None or s['whole_segment_volume_established'] is not False:raise ValueError('Only original partial Makassar scenarios')
                corners=p['corners_sw_se_ne_nw'];points=[a['lon_lat'] for a in corners]
                if len(points)!=4 or any(len(a)!=2 or not all(finite(x) for x in a) for a in points):raise ValueError('Original four corners required')
                w,e=points[0][0],points[1][0];south,north=points[0][1],points[2][1]
                if points!=[[w,south],[e,south],[e,north],[w,north]] or not 117<=w<e<=121 or not -5<=south<north<=0:raise ValueError('Original ordered regional rectangle')
                if any(not all(finite(a[k]) for k in ['upper_depth_m','lower_depth_m']) or not 0<=a['upper_depth_m']<a['lower_depth_m'] for a in corners):raise ValueError('Finite paired original surfaces')
                out.append({'id':s['id']+f':cell{ci}:patch{pi}','segment_id':s['id'],'snapshot_time_utc':s['snapshot_time_utc'],'source_pointer':f'/segments/{si}/cells/{ci}/patches/{pi}','bbox':[w,south,e,north],'corners':copy.deepcopy(corners),'original_conditional_volume_km3':p['conditional_partial_component_volume_km3'],'original_sampling_volume_scenarios_km3':copy.deepcopy(p['sampling_bracket_volume_scenarios_km3'])})
    if len(out)!=59:raise ValueError('All59 original patches must remain')
    return out

def plan_grid(patches):
    w=min(p['bbox'][0] for p in patches);s=min(p['bbox'][1] for p in patches);e=max(p['bbox'][2] for p in patches);n=max(p['bbox'][3] for p in patches)
    bounds=[(math.floor(w/STEP)-1)*STEP,(math.floor(s/STEP)-1)*STEP,(math.ceil(e/STEP)+1)*STEP,(math.ceil(n/STEP)+1)*STEP]
    nx=round((bounds[2]-bounds[0])/STEP);ny=round((bounds[3]-bounds[1])/STEP)
    if not 1<=nx*ny<=6000:raise ValueError('Prospective whole-case terrain cell cap; no grid retuning')
    nodes=[]
    for p in patches:
        indices=[(row,col) for row in range(ny) for col in range(nx) if p['bbox'][0]<=bounds[0]+(col+.5)*STEP<=p['bbox'][2] and p['bbox'][1]<=bounds[3]-(row+.5)*STEP<=p['bbox'][3]]
        nodes.append(indices)
    comparisons=sum(map(len,nodes))
    if comparisons>6000:raise ValueError('Prospective total comparison-node occurrence cap')
    return {'bbox':bounds,'width':nx,'height':ny,'step_degrees':STEP,'reserved_terrain_values':nx*ny,'comparison_node_occurrences':comparisons,'analysis_scalar_reservation':10*comparisons+40*len(patches)+5000},nodes

def selected_rasters(metadata):
    if 'error' in metadata or metadata.get('exceededTransferLimit'):raise ValueError('No service error or truncated metadata selection')
    features=metadata.get('features',[])
    if not 1<=len(features)<=16:raise ValueError('One bounded metadata result required; no alternate product query')
    rows=[]
    for feature in features:
        a=feature['attributes'];text=' '.join(str(a.get(k,'')) for k in ['Name','ProductName','DemName']).upper();clean=re.sub('[^A-Z0-9]','',text)
        if 'ETOPO2022' not in clean or not (a.get('CellsizeArcseconds')==15 or '15S' in clean):raise ValueError('Only identifiable15arcsecond ETOPO2022 elevations')
        if type(a['OBJECTID'])!=int:raise ValueError('Exact raster IDs required')
        rows.append(a)
    bed=[a for a in rows if 'BED' in ' '.join(str(a.get(k,'')) for k in ['Name','ProductName','DemName']).upper()]
    # Prefer explicitly named bed elevations; outside ice sheets surface and
    # bed versions share terrain, but neither may be replaced by another DEM.
    return sorted(bed or rows,key=lambda a:a['OBJECTID'])

def query_url(grid):
    params={'where':"Name LIKE '%ETOPO%2022%' OR ProductName LIKE '%ETOPO%2022%' OR DemName LIKE '%ETOPO%2022%'",'geometry':','.join(map(str,grid['bbox'])),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','returnGeometry':'false','outFields':'OBJECTID,Name,ProductName,DemName,VerticalDatum,CellsizeArcseconds','resultRecordCount':16,'f':'json'}
    return SERVICE+'/query?'+urllib.parse.urlencode(params)

def image_url(grid,rows):
    params={'bbox':','.join(map(str,grid['bbox'])),'bboxSR':4326,'imageSR':4326,'size':f"{grid['width']},{grid['height']}",'format':'tiff','pixelType':'F32','interpolation':'RSP_NearestNeighbor','compression':'LZW','renderingRule':json.dumps({'rasterFunction':'None'},separators=(',',':')),'mosaicRule':json.dumps({'mosaicMethod':'esriMosaicLockRaster','lockRasterIds':[a['OBJECTID'] for a in rows],'mosaicOperation':'MT_FIRST'},separators=(',',':')),'f':'image'}
    return SERVICE+'/exportImage?'+urllib.parse.urlencode(params)

def interpolated_depth(p,x,y,key):
    w,s,e,n=p['bbox'];u=(x-w)/(e-w);v=(y-s)/(n-s)
    if not 0<=u<=1 or not 0<=v<=1:raise ValueError('No extrapolation outside original surface')
    weights=[(1-u)*(1-v),u*(1-v),u*v,(1-u)*v]
    return sum(a[key]*t for a,t in zip(p['corners'],weights))

def assess(patches,grid,nodes,elevations,mask):
    results=[]
    for p,indices in zip(patches,nodes):
        points=[]
        for row,col in indices:
            x=grid['bbox'][0]+(col+.5)*STEP;y=grid['bbox'][3]-(row+.5)*STEP
            z=None if mask[row,col] else float(elevations[row,col])
            if z is not None and (not math.isfinite(z) or not -12000<=z<=9000):raise ValueError('Finite-or-missing plausible terrain elevation')
            points.append({'row':row,'column':col,'lon_lat':[x,y],'elevation_m':z,'interpolated_upper_depth_m':interpolated_depth(p,x,y,'upper_depth_m'),'interpolated_lower_depth_m':interpolated_depth(p,x,y,'lower_depth_m')})
        finite_points=[a for a in points if a['elevation_m'] is not None];scenarios=[]
        for offset in OFFSETS:
            differences=[a['interpolated_lower_depth_m']-(offset-a['elevation_m']) for a in finite_points]
            scenarios.append({'assumed_surface_above_nominal_etopo_reference_m':offset,'nonpositive_water_column_samples':sum(offset-a['elevation_m']<=0 for a in finite_points),'lower_surface_below_grid_bed_samples':sum(v>0 for v in differences),'maximum_lower_surface_minus_grid_water_depth_m':max(differences) if differences else None})
        conflicts=[a['lower_surface_below_grid_bed_samples']>0 for a in scenarios]
        status='NO_FINITE_TERRAIN_SAMPLES_UNKNOWN' if not finite_points else 'SAMPLED_CONFLICT_AT_ALL_TESTED_OFFSETS' if all(conflicts) else 'OFFSET_SENSITIVE_SAMPLED_CONFLICT' if any(conflicts) else 'NO_SAMPLED_CONFLICT_NOT_TERRAIN_VALIDATION'
        results.append({'id':p['id'],'segment_id':p['segment_id'],'snapshot_time_utc':p['snapshot_time_utc'],'source_pointer':p['source_pointer'],'status':status,'sample_count':len(points),'finite_sample_count':len(finite_points),'missing_sample_count':len(points)-len(finite_points),'nonnegative_elevation_samples':sum(a['elevation_m']>=0 for a in finite_points),'scenarios':scenarios,'sampled_points':points,'original_conditional_volume_km3':p['original_conditional_volume_km3'],'original_sampling_volume_scenarios_km3':p['original_sampling_volume_scenarios_km3'],'current_boundary_clipped_to_bed':False,'terrain_clearance_established':False,'physical_volume_eligible':False})
    return results

def csv_bytes(rows):
    fields=['id','segment_id','snapshot_time_utc','status','sample_count','finite_sample_count','missing_sample_count','nonnegative_elevation_samples','scenarios','original_conditional_volume_km3','original_sampling_volume_scenarios_km3','terrain_clearance_established','physical_volume_eligible','source_pointer']
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r in rows:w.writerow({k:json.dumps(r[k],separators=(',',':')) if isinstance(r[k],(dict,list,bool)) else '' if r[k] is None else r[k] for k in fields})
    return stream.getvalue().encode()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise RuntimeError('No source redirects or alternate targets')

def main():
    start=float(os.environ['OSW_TERRAIN_SCREEN_START']);out=ROOT/'makassar-etopo-terrain-screen-v1';out.mkdir(exist_ok=False)
    ledger={'schema':'osw.makassar-etopo-new-terrain-case-ledger.v1','scope':'new_environmental_terrain_context_not_velocity_case_renewal','maximum_provider_operations':2,'provider_operations_attempted':0,'provider_operations_remaining':2,'raw_byte_cap':7000000,'raw_bytes_retained':0,'numeric_scalar_cap':250000,'reserved_numeric_upper_bound':0,'native_terrain_values_decoded':0,'new_native_velocity_values_decoded':0,'targets':[],'status':'INITIALIZED','physical_current_depths_admitted':0,'physical_volumes_admitted':0,'full_goal_complete':False}
    def save():
        ledger['elapsed_seconds']=time.monotonic()-start;tmp=out/'case-ledger.tmp';tmp.write_bytes(encode(ledger));os.replace(tmp,out/'case-ledger.json')
    def stop(*args):ledger['status']='TERMINATED_AT_ABSOLUTE_DEADLINE_OR_SIGTERM';save();raise TimeoutError('Shared60second terrain case deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));save()
    def save_query(v):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save_query,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    def capture(url,name,cap):
        if not url.startswith(SERVICE+'/') or ledger['provider_operations_remaining']<=0:raise ValueError('Exact service and original operation budget')
        target={'url':url,'file':name,'reserved_raw_bytes':cap,'status':'RESERVED_BEFORE_REQUEST'};ledger['targets'].append(target);ledger['provider_operations_attempted']+=1;ledger['provider_operations_remaining']-=1;save()
        raw=b''
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'OSW-bounded-terrain-context/1.0','Accept':'application/json,image/tiff'})
            try:
                with urllib.request.build_opener(NoRedirect()).open(req,timeout=min(25,max(1,60-(time.monotonic()-start)))) as response:raw=response.read(cap+1);target['http_status']=response.status
            except urllib.error.HTTPError as error:raw=error.read(cap+1);target['http_status']=error.code;raise
        except BaseException as error:target['status']='FAILED_NO_RETRY';target['error_type']=type(error).__name__;raise
        finally:
            (out/name).write_bytes(raw);ledger['raw_bytes_retained']+=len(raw);target['bytes']=len(raw);target['sha256']=sha(raw);save()
        if len(raw)>cap or ledger['raw_bytes_retained']>7000000:raise ValueError('Raw bytes retained before cap rejection')
        target['status']='RETAINED_BEFORE_PARSE';save();return raw
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,pin in op['input_sha256'].items():
                if sha((ROOT/p).read_bytes())!=pin:raise ValueError('Frozen screen input changed:'+p)
            source_raw=reader(SOURCE)
            if sha(source_raw)!=SOURCE_SHA:raise ValueError('Exact prior surface bytes')
            source=json.loads(source_raw);original=copy.deepcopy(source);patches=source_patches(source);grid,nodes=plan_grid(patches)
            reserved=query.ledger['reserved_numeric_tokens']+2000+grid['reserved_terrain_values']+grid['analysis_scalar_reservation']
            if reserved>250000:raise ValueError('Prospective whole-case scalar cap before any provider request')
            ledger.update(reserved_numeric_upper_bound=reserved,descriptor_numeric_tokens_reserved=query.ledger['reserved_numeric_tokens'],metadata_numeric_token_reservation=2000,terrain_value_reservation=grid['reserved_terrain_values'],analysis_scalar_reservation=grid['analysis_scalar_reservation'],grid_plan=grid,status='SOURCE_PLAN_RESERVED');save()
            raw_metadata=capture(query_url(grid),'raster-metadata.json',100000)
            if numeric_tokens(raw_metadata)>2000:raise ValueError('Metadata scalar reservation before decode')
            metadata=json.loads(raw_metadata);rows=selected_rasters(metadata)
            raw_image=capture(image_url(grid,rows),'terrain.tif',1000000)
            if raw_image[:4] not in [b'II*\x00',b'MM\x00*']:raise ValueError('One ordinary GeoTIFF expected; no alternate response format')
            with rasterio.open(out/'terrain.tif') as raster:
                if raster.driver!='GTiff' or raster.count!=1 or (raster.width,raster.height)!=(grid['width'],grid['height']) or raster.crs!=rasterio.crs.CRS.from_epsg(4326) or raster.dtypes!=('float32',):raise ValueError('Exact bounded one-band F32 geographic raster before value decode')
                if any(abs(a-b)>1e-7 for a,b in zip(raster.bounds,grid['bbox'])) or any(abs(a-b)>1e-8 for a,b in zip(tuple(raster.transform)[:6],[STEP,0,grid['bbox'][0],0,-STEP,grid['bbox'][3]])):raise ValueError('Original planned pixel-center registration required')
                ledger['status']='TERRAIN_VALUES_RESERVED_BEFORE_DECODE';save();array=raster.read(1,masked=True);ledger['native_terrain_values_decoded']=int(array.size);save()
            results=assess(patches,grid,nodes,np.ma.getdata(array),np.ma.getmaskarray(array))
            if source!=original:raise ValueError('Original surfaces and volumes must remain exact')
            counts={'source_depth_surface_patches':59,'terrain_grid_cells_decoded':grid['reserved_terrain_values'],'comparison_node_occurrences':grid['comparison_node_occurrences'],'patch_status_counts':{s:sum(r['status']==s for r in results) for s in sorted({r['status'] for r in results})},'new_current_depth_measurements':0,'new_native_velocity_values_decoded':0,'physical_volumes_admitted':0}
            report={'schema':'osw.makassar-etopo-coarse-terrain-screen.v1','source_depth_surfaces':{'file':SOURCE,'sha256':SOURCE_SHA},'terrain_service':SERVICE,'selected_raster_metadata':rows,'grid':grid,'counts':counts,'patches':results,'vertical_reference':'ETOPO2022 nominal EGM2008 orthometric elevation in metres;provider current depths are positive down from their own sea-surface context. No datum/tide/model-grid reconciliation recovered.','offset_interpretation':'-20,0,+20m are explicit nominal surface/datum sensitivity scenarios,not uncertainty bounds or observed sea levels. Compare central bilinear lower surfaces only.','spatial_interpretation':'Nearest-neighbor export at0.04degree centers is a coarse sampled screen,not complete15arcsecond terrain inspection. Thin land,shoals and between-sample conflicts may be missed. No-conflict is not validation.','source_credit':'NOAA National Centers for Environmental Information ETOPO2022 Global Relief Model;doi:10.25921/fd45-gt74. Original HYCOM/NRL/COAPS-FSU attribution remains in the pinned current-source chain.','current_boundary_clipped_to_bed':False,'original_current_surfaces_unchanged':True,'physical_volume_eligibility_changed':False,'runtime_changed':False,'full_goal_complete':False}
            rr=encode(report);table=csv_bytes(results)
            if numeric_tokens(rr)>grid['analysis_scalar_reservation']:raise ValueError('Derived output scalar reservation')
            if json.loads(rr)!=report or csv_bytes(json.loads(rr)['patches'])!=table:raise ValueError('Complete terrain report/CSV roundtrip')
            if len(rr)+len(table)+sum(p.stat().st_size for p in out.iterdir() if p.is_file())>2400000:raise ValueError('Whole source/output cap')
            (out/'terrain-screen.json').write_bytes(rr);(out/'terrain-screen.csv').write_bytes(table);ledger['status']='COARSE_TERRAIN_SCREEN_COMPLETE_NO_PHYSICAL_PROMOTION';save();print(json.dumps({'counts':counts,'provider_operations':ledger['provider_operations_attempted'],'raw_bytes':ledger['raw_bytes_retained'],'numeric_upper_bound':ledger['reserved_numeric_upper_bound']}),flush=True)
    except BaseException as error:
        if ledger['status']!='TERMINATED_AT_ABSOLUTE_DEADLINE_OR_SIGTERM':ledger['status']='FAILED_OR_UNQUALIFIED_CASE_CLOSED_NO_RETRY';ledger['error_type']=type(error).__name__;save()
        raise
    finally:signal.alarm(0);save()

if __name__=='__main__':main()
