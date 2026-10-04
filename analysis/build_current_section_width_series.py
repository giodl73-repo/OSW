"""Compute explicitly scoped section-span candidates from pinned daily fields."""
import hashlib
import json
import math
from pathlib import Path
from pyproj import Geod
from build_gulf_stream_geostrophic_path import load_field, sample_velocity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/gulf-stream-section-width-series.json'
PROTOCOL = ROOT / 'plans/gulf-stream-section-width-protocol-v1.md'
GEOD = Geod(ellps='WGS84')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def distance(south,north): return GEOD.inv(-70,south,-70,north)[2]/1000

def measure(profile, fraction):
    if not math.isfinite(fraction) or not 0 < fraction < 1:
        raise ValueError('Invalid relative boundary threshold')
    eligible = [(index,row) for index,row in enumerate(profile) if row['eastward_m_s'] is not None]
    if not eligible: return {'fraction':fraction,'status':'missing_profile','span_km':None}
    index,peak = max(eligible,key=lambda pair:pair[1]['eastward_m_s'])
    if peak['eastward_m_s'] < .15: return {'fraction':fraction,'status':'weak_or_no_eastward_peak','span_km':None}
    threshold = peak['eastward_m_s']*fraction
    crossings=[]
    for direction in [-1,1]:
        previous=index
        current=index+direction
        crossing=None
        while 0 <= current < len(profile):
            inner,outer=profile[previous],profile[current]
            if outer['eastward_m_s'] is None:break
            if outer['eastward_m_s'] <= threshold:
                ratio=(threshold-inner['eastward_m_s'])/(outer['eastward_m_s']-inner['eastward_m_s'])
                crossing={'latitude':inner['latitude']+ratio*(outer['latitude']-inner['latitude']), 'bracket_latitudes':[inner['latitude'],outer['latitude']]}
                break
            previous=current; current+=direction
        crossings.append(crossing)
    if any(row is None for row in crossings):
        return {'fraction':fraction,'status':'unbracketed_boundary','span_km':None,'peak_latitude':peak['latitude'],'peak_eastward_m_s':peak['eastward_m_s']}
    south,north=crossings
    span=distance(south['latitude'],north['latitude'])
    inner=distance(max(south['bracket_latitudes']),min(north['bracket_latitudes']))
    outer=distance(min(south['bracket_latitudes']),max(north['bracket_latitudes']))
    spacing=distance(peak['latitude'],peak['latitude']+.25)
    return {'fraction':fraction,'status':'paired_boundaries','span_km':round(span,6),'peak_latitude':peak['latitude'],'peak_eastward_m_s':peak['eastward_m_s'],'south_boundary':south,'north_boundary':north,'grid_bracket_span_km':[round(inner,6),round(outer,6)],'native_cell_spacings':round(span/spacing,3),'resolution_review_required':span/spacing<4}

def compute(source):
    fields=load_field(source)
    profile=[]
    for index in range(source['subset_shape'][0]):
        latitude=source['grid_origin_lon_lat'][1]+index*source['grid_step_degrees'][1]
        if not 35<=latitude<=41:continue
        velocity=sample_velocity(source,fields,-70,latitude)
        profile.append({'latitude':latitude,'eastward_m_s':velocity[0] if velocity else None})
    scenarios=[measure(profile,fraction) for fraction in [.4,.5,.6]]
    nominal=scenarios[1]
    complete=[r['span_km'] for r in scenarios if r['span_km'] is not None]
    return {'profile':profile,'nominal':nominal,'threshold_scenarios':scenarios,'approximate_section_span_km':int(math.floor(nominal['span_km']/10+.5)*10) if nominal['span_km'] is not None else None,'threshold_sensitivity_span_km':[math.floor(min(complete)/10)*10,math.ceil(max(complete)/10)*10] if complete else None,'range_kind':'finite_boundary_threshold_sensitivity_not_confidence_or_annual_range'}

def build():
    frames=[]
    for series in ['ocean-current-dated-timeline.json','ocean-current-dated-timeline-2025.json']:
        timeline=json.loads((ROOT/'research'/series).read_text(encoding='utf-8'))
        for frame in timeline['frames']:
            path=ROOT/frame['source_subset']
            if digest(path)!=frame['source_subset_sha256']:raise ValueError('Changed source subset')
            source=json.loads(path.read_text(encoding='utf-8'))
            frames.append({'date':frame['date'],'source_subset':frame['source_subset'],'source_subset_sha256':digest(path),'source_url':source['source_url'],'source_algorithm':source['source_algorithm'],**compute(source)})
    spans=[]
    for year in sorted({r['date'][:4] for r in frames}):
        selected=[r for r in frames if r['date'].startswith(year) and r['approximate_section_span_km'] is not None]
        values=[r['approximate_section_span_km'] for r in selected]
        spans.append({'year':int(year),'sample_count':len(selected),'rounded_sample_value_span_km':[min(values),max(values)] if values else None,'range_kind':'span_of_sampled_rounded_section_candidate_values_not_annual_extrema','source_algorithms':sorted({r['source_algorithm'] for r in selected})})
    return {'schema':'osw.current-section-width-series.v1','status':'derived_width_candidate_requires_scientific_review','current_id':'gulf-stream-system','metric':'meridional_half_peak_eastward_velocity_section_span','section_longitude':-70,'latitude_window':[35,41],'layer':'NOAA LSA altimetry-derived absolute surface geostrophic velocity','whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,'annual_width_range_km':None,'is_confidence_interval':False,'protocol_file':str(PROTOCOL.relative_to(ROOT)).replace('\\','/'),'protocol_sha256':digest(PROTOCOL),'general_protocol_sha256':digest(ROOT/'plans/ocean-current-width-measurement-protocol-v1.md'),'generator_sha256':digest(Path(__file__)),'velocity_sampler_sha256':digest(ROOT/'analysis/build_gulf_stream_geostrophic_path.py'),'sample_value_spans':spans,'frames':sorted(frames,key=lambda r:r['date'])}

if __name__=='__main__':
    document=build();OUTPUT.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    print(f"Built {len(document['frames'])} fixed-section width candidates")
