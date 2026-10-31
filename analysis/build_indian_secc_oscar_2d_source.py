"""Surrounding source fields with exact historical slices; no flow edges inferred."""
import json,hashlib
import numpy as np
from acquire_indian_secc_oscar_2d import ROOT,DIRECTORY,OLD,PROTOCOL,OPERATOR,load,baseline

REPORT='research/indian-secc-oscar-2d-monthly-source-fields.json'
BUILDER='analysis/build_indian_secc_oscar_2d_source.py'
FIGURE='figures/indian-secc-oscar-2d-source.svg'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,separators=(',',':'),allow_nan=False)+'\n').encode()
def monthly(arrays):
    frames=[];shape=arrays['u'].shape[1:]
    for month in range(1,13):
        ix=[i for i,t in enumerate(arrays['times']) if int(t[5:7])==month]
        paired=np.isfinite(arrays['u'][ix])&np.isfinite(arrays['v'][ix]);count=paired.sum(axis=0)
        u=np.full(shape,np.nan);v=np.full(shape,np.nan)
        for yi,xi in zip(*np.where(count>=5)):
            selected=[i for i in ix if np.isfinite(arrays['u'][i,yi,xi]) and np.isfinite(arrays['v'][i,yi,xi])]
            u[yi,xi]=sum(float(arrays['u'][i,yi,xi]) for i in selected)/len(selected)
            v[yi,xi]=sum(float(arrays['v'][i,yi,xi]) for i in selected)/len(selected)
        def nullable(a):return [[float(v) if np.isfinite(v) else None for v in row] for row in a]
        frames.append({'month':month,'source_time_indices':ix,'source_times':[arrays['times'][i] for i in ix],
            'available_source_times':len(ix),'paired_samples':count.tolist(),'eastward_m_s':nullable(u),'northward_m_s':nullable(v),
            'eligible_mean_cells':int((count>=5).sum()),'outside_fixed_color_scale_cells':int(((u<-.4)|(u>.4)).sum()),
            'viewport_eastward_component_min_m_s':float(np.nanmin(u)) if np.isfinite(u).any() else None,
            'viewport_eastward_component_max_m_s':float(np.nanmax(u)) if np.isfinite(u).any() else None})
    return frames

def check_monthly_overlap(arrays,frames):
    previous,clocks=baseline();checked=0
    for old in previous.values():
        longitude=next(iter(old.values()))[2];xi=np.where(arrays['longitude']==longitude)[0][0]
        for f in frames:
            times=f['source_times']
            for y in sorted({y for _,y in old}):
                yi=np.where(arrays['latitude']==y)[0][0]
                paired=[old[(t,y)] for t in times if np.isfinite(old[(t,y)][-2:]).all()]
                count=len(paired)
                if f['paired_samples'][yi][xi]!=count:raise ValueError('Changed historical monthly paired count')
                for key,i in [('eastward_m_s',-2),('northward_m_s',-1)]:
                    expected=sum(r[i] for r in paired)/count if count>=5 else None
                    value=f[key][yi][xi]
                    if (expected is None)!=(value is None) or expected is not None and np.float64(expected).view(np.uint64)!=np.float64(value).view(np.uint64):
                        raise ValueError('Changed historical monthly mean bits/mask')
                checked+=1
    return checked

def build():
    receipt=json.loads((DIRECTORY/'acquisition.json').read_bytes())
    for p,pin in receipt['input_sha256'].items():
        if digest(p)!=pin:raise ValueError('Changed source intake contract:'+p)
    arrays,quality=load()
    if quality!=receipt['quality']:raise ValueError('Changed source quality receipt')
    frames=monthly(arrays);overlap=check_monthly_overlap(arrays,frames)
    paths=[PROTOCOL,OPERATOR,BUILDER,'research/indian-secc-winter-surface-frequency-scope-audit.json',
           (DIRECTORY/'source-responses.zip').relative_to(ROOT).as_posix(),(DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix(),
           *[(OLD/n).relative_to(ROOT).as_posix() for n in ['acquisition.json','indian-secc-80p333e.csv','indian-secc-80p667e.csv']]]
    return {'schema':'osw.indian-secc-oscar-2d-monthly-source.v1','status':'surrounding_source_context_not_current_geometry',
        'current_id':'indian-south-equatorial-countercurrent','entity_id':'current:indian-south-equatorial-countercurrent',
        'dataset_id':receipt['dataset_id'],'product_version':receipt['product_version'],'source_license':receipt['source_license'],
        'attribution':receipt['attribution'],'source_first_time':arrays['times'][0],'source_last_time':arrays['times'][-1],
        'nominal_depth_m':15,'layer_interpretation':'Mapped satellite-derived upper-ocean vectors; nominal15m is not a directly observed or depth-resolved layer.',
        'longitude_degrees_east':arrays['longitude'].tolist(),'latitude_degrees_north':arrays['latitude'].tolist(),
        'quality':quality,'monthly_mean_rule':'Chronological paired-vector sums with at least five finite pairs per calendar month/cell.',
        'comparison_longitudes_degrees_east':[80+1/3,80+2/3],'comparison_latitude_domain':[-10,0],
        'historical_monthly_overlap_cells':overlap,'historical_monthly_bits_masks_and_counts_exact':True,'months':frames,
        'monthly_summary':[{'id':f"source-month:2013-{f['month']:02d}",'month':f['month'],
            'available_source_times':f['available_source_times'],'first_source_time':f['source_times'][0],
            'last_source_time':f['source_times'][-1],'eligible_mean_cells':f['eligible_mean_cells'],
            'viewport_eastward_component_min_m_s':f['viewport_eastward_component_min_m_s'],
            'viewport_eastward_component_max_m_s':f['viewport_eastward_component_max_m_s'],
            'display_clipped_cells':f['outside_fixed_color_scale_cells'],
            'range_kind':'extrema_of_spatial_monthly_mean_component_field_not_current_dimensions'} for f in frames],
        'current_association_verified':False,'whole_current_length_km':None,'whole_current_width_km':None,
        'annual_physical_length_range_km':None,'annual_physical_width_range_km':None,
        'rank_eligible':False,'seasonal_current_footprint_admitted':False,'comparison_figure':FIGURE,
        'input_sha256':{p:digest(p) for p in paths},
        'limitations':['The source viewport is not a current boundary, origin, termination or complete named-current extent.',
            'Equatorial jets, SECC, westward SEC and regional eddies may coexist; current association requires separate review.',
            'A monthly mean field is not mean instantaneous width or an independently sampled seasonal climatology.',
            'No velocity axis, paired edges, flow-normal width, confidence interval, physical annual range or OSW state passage inferred.',
            'The previously acquired12S section tails are retained outside this viewport; no southern boundary is manufactured.',
            'All native cells have finite source vectors; fine islands/coast masks are not resolved by this coarse mapped product.']}

def verify():
    doc=json.loads((ROOT/REPORT).read_bytes())
    if doc!=build():raise ValueError('Changed surrounding SECC source report')
    manifest_path='research/indian-secc-oscar-2d-source-figure.json';manifest=json.loads((ROOT/manifest_path).read_bytes())
    if manifest['source_file']!=REPORT or manifest['source_sha256']!=digest(REPORT) or manifest['current_geometry_admitted'] is not False:
        raise ValueError('Changed surrounding SECC figure/source binding')
    pins={**doc['input_sha256'],REPORT:digest(REPORT),manifest_path:digest(manifest_path),manifest['generator_file']:manifest['generator_sha256']}
    pins.update({a['file']:a['sha256'] for a in manifest['figures'].values()})
    for p,pin in pins.items():
        if digest(p)!=pin:raise ValueError('Changed source context dependency:'+p)
    return doc,pins

if __name__=='__main__':
    d=build();(ROOT/REPORT).write_bytes(encoded(d))
    print(json.dumps({'quality':d['quality'],'monthly_cells':[m['eligible_mean_cells'] for m in d['months']],
        'historical_monthly_overlap_cells':d['historical_monthly_overlap_cells']}))
