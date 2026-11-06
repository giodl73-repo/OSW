"""Selected visible model-front extent; never reconstruct clipped source geometry."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
from eddy_map_spans_v1 import axis_value
from eddy_scale_bar_spans_v1 import ink


def read_source_pixels(samples,width,height):
    ticks=[]
    for value,y in [(29.5,25),(29,151),(28.5,277),(28,402),(27.5,526),(27,650),(26.5,774),(26,897)]:
        roi=[48,y-5,54,y+5];p=ink(samples,width,height,roi,100)
        ticks.append({'latitude_north_degrees':value,'window_xyxy':roi,'coordinate_y':statistics.median(y for x,y in p),'ink_pixels':len(p),'pixels_sha256':hashlib.sha256(json.dumps(sorted(p),separators=(',',':')).encode()).hexdigest()})
    readings=[]
    for gate in [75,100]:
        row={'maximum_rgb_channel':gate,'extrema':{}}
        for side,roi,choose in [('north',[390,312,515,335],min),('south',[420,868,585,885],max)]:
            p=ink(samples,width,height,roi,gate);y=choose(y for x,y in p)
            assert roi[1]<y<roi[3]
            row['extrema'][side]={'window_xyxy':roi,'coordinate_y':y,'ink_pixels':len(p),'pixels_sha256':hashlib.sha256(json.dumps(sorted(p),separators=(',',':')).encode()).hexdigest(),'extreme_x_range':[min(x for x,yy in p if yy==y),max(x for x,yy in p if yy==y)]}
        readings.append(row)
    return {'ticks':ticks,'readings':readings}


def span(c):
    anchors=[[t['coordinate_y'],t['latitude_north_degrees']] for t in c['ticks']]
    assert [r[1] for r in anchors]==[29.5,29,28.5,28,27.5,27,26.5,26]
    km_per_degree=6371*math.pi/180;intervals=[]
    for row in c['readings']:
        n,s=[row['extrema'][side]['coordinate_y'] for side in ['north','south']]
        for shifts in itertools.product([-2,2],repeat=8):
            a=[[y+d,value] for (y,value),d in zip(anchors,shifts)]
            intervals.append([(axis_value(n+6,a)-axis_value(s-6,a))*km_per_degree,(axis_value(n-6,a)-axis_value(s+6,a))*km_per_degree])
    nominal=next(r for r in c['readings'] if r['maximum_rgb_channel']==100)
    n,s=[nominal['extrema'][side]['coordinate_y'] for side in ['north','south']]
    lo,hi=min(r[0] for r in intervals),max(r[1] for r in intervals)
    return {'audit_visible_meridional_span_km':round((axis_value(n,anchors)-axis_value(s,anchors))*km_per_degree,6),'audit_reading_interval_km':[round(lo,6),round(hi,6)],'range_km':[math.floor(lo/25)*25,math.ceil(hi/25)*25],'total_scenarios':len(intervals),'full_front_extent_inferred':False}


def validate_case(c):
    assert c['method']=='source_visible_model_front_meridional_span_v1'
    assert c['owner_id']=='eddy:horizon:loop-66-primary' and c['source_name']=='Quantum / northern Quantum I' and c['date']=='2018-03-26'
    assert c['pdf_page']==7 and c['figure']==2 and c['front_basis']=='model_inferred_per_source_caption' and c['east_side_clipped'] is True
    assert c['earth_radius_km']==6371 and c['reading_allowance_pixels']==6 and c['axis_sensitivity_pixels']==2 and c['round_outward_km']==25
    assert all(c[k] is False for k in ['east_west_span_admitted','full_front_extent_inferred','observed_front_inferred','front_threshold_known','missing_geometry_reconstructed','physical_footprint_admitted','physical_state_join_eligible','association_is_verified','rights_screened_release_eligible','quantum_ii_values_inherited'])
    assert c['source_raster']=={'xref':235,'width':835,'height':1014,'components':3,'samples_sha256':'754bc0de08c33d14d740b71f6da563f8ef6192d63d1bc76159ac1502ebbcac95'}
    assert len(c['ticks'])==8 and len(c['readings'])==2 and {r['maximum_rgb_channel'] for r in c['readings']}=={75,100}
    for row in c['readings']:
        for side,roi in [('north',[390,312,515,335]),('south',[420,868,585,885])]:
            v=row['extrema'][side];assert v['window_xyxy']==roi and roi[1]<v['coordinate_y']<roi[3]
            assert roi[0]<v['extreme_x_range'][0]<=v['extreme_x_range'][1]<roi[2] and v['ink_pixels']>300
    span(c)


def verify_source(pdf,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    b=json.loads(batch_path.read_bytes());c=b['visible_model_front_cases'][0];validate_case(c);original=b['sources']['rodriguez-2020']['original']
    raw=pdf.read_bytes();assert len(raw)==original['bytes']==12313659 and hashlib.sha256(raw).hexdigest()==original['sha256']
    with pymupdf.open(stream=raw,filetype='pdf') as doc:
        assert len(doc)==original['pages']==38 and 235 in [r[0] for r in doc[6].get_images(full=True)]
        pix=pymupdf.Pixmap(doc,235);samples=pix.samples;assert (pix.width,pix.height,pix.n)==(835,1014,3)
        assert hashlib.sha256(samples).hexdigest()==c['source_raster']['samples_sha256']
        actual=read_source_pixels(samples,pix.width,pix.height);assert actual=={key:c[key] for key in ['ticks','readings']}
        text=doc[6].get_text();assert '2018-03-26' in text and 'black line inferred from models' in text
    return {'schema':'osw.eddy-visible-model-front-source-verification.v1','status':'PASS','original_pdf_sha256':original['sha256'],'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'axis_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),'ink_reader_sha256':hashlib.sha256((Path(__file__).parent/'eddy_scale_bar_spans_v1.py').read_bytes()).hexdigest(),'source_pixels_verified':True,'manual_name_component_and_extremum_selection_required':True,'tick_windows_verified':8,'extremum_windows_verified':4,'east_side_clipped':True,'missing_geometry_reconstructed':False,'full_front_extent_inferred':False,'physical_footprint_admitted':False,'meridional_span':span(c),'runtime_changed':False}
