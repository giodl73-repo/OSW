"""Measure reproducible monthly local component spans, preserving unresolved edges."""
import calendar
import hashlib
import json
import math
from pathlib import Path
from pyproj import Geod
from acquire_basin_surface_sections import build as source_inventory

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'plans/basin-surface-section-width-protocol-v1.md'
INVENTORY = ROOT/'research/basin-surface-section-inventory.json'
GEOD = Geod(ellps='WGS84')


def diagnostic_matches(saved, calculated, path=()):
    """Only geodesic arithmetic roundoff may differ, by at most 1e-10 km."""
    if type(saved) is not type(calculated):
        return False
    if isinstance(saved,dict):
        return saved.keys()==calculated.keys() and all(diagnostic_matches(saved[k],calculated[k],path+(k,)) for k in saved)
    if isinstance(saved,list):
        return len(saved)==len(calculated) and all(diagnostic_matches(a,b,path+(i,)) for i,(a,b) in enumerate(zip(saved,calculated)))
    derived=bool(path) and (path[-1]=='span_km' or len(path)>1 and path[-2]=='grid_bracket_span_km')
    if isinstance(saved,float) and derived:
        return math.isfinite(saved) and math.isfinite(calculated) and math.isclose(saved,calculated,rel_tol=0,abs_tol=1e-10)
    return saved==calculated


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point(section, coordinate):
    return [coordinate,section['fixed_coordinate']] if section['varying_axis']=='longitude' else [section['fixed_coordinate'],coordinate]


def distance(section, low, high):
    return GEOD.inv(*point(section,low),*point(section,high))[2]/1000


def measure(profile, section, fraction, minimum_peak=.02):
    if fraction not in [.4,.5,.6] or not math.isfinite(minimum_peak) or minimum_peak<=0:
        raise ValueError('Invalid component boundary rule')
    coordinates = [r['coordinate'] for r in profile]
    if len(profile)<3 or any(not math.isfinite(x) for x in coordinates) or any(b<=a for a,b in zip(coordinates,coordinates[1:])):
        raise ValueError('Section grid must increase')
    if any(r['component_m_s'] is not None and not math.isfinite(r['component_m_s']) for r in profile):
        raise ValueError('Nonfinite component must remain missing')
    eligible = [(i,r) for i,r in enumerate(profile) if section['peak_search'][0]-1e-8<=r['coordinate']<=section['peak_search'][1]+1e-8 and r['component_m_s'] is not None]
    result = {'fraction':fraction,'span_km':None,'boundaries':{},'grid_bracket_span_km':None,'native_cell_spacings':None,'resolution_review_required':None}
    if not eligible:
        return {**result,'status':'missing_peak_support'}
    index, peak = max(eligible,key=lambda item:item[1]['component_m_s'])
    result.update(peak_coordinate=peak['coordinate'], peak_component_m_s=peak['component_m_s'],
                  peak_at_search_edge=index in [eligible[0][0],eligible[-1][0]])
    if peak['component_m_s']<minimum_peak:
        return {**result,'status':'weak_or_no_eligible_peak'}
    threshold = peak['component_m_s']*fraction
    result['threshold_m_s'] = threshold
    for direction,label in [(-1,'low_coordinate'),(1,'high_coordinate')]:
        previous=index; current=index+direction
        boundary={'status':'domain_edge_without_crossing','coordinate':None,'bracket':None}
        while 0<=current<len(profile):
            inner, outer = profile[previous],profile[current]
            if outer['component_m_s'] is None:
                boundary['status']='missing_before_crossing';break
            if outer['component_m_s']<=threshold:
                ratio=(threshold-inner['component_m_s'])/(outer['component_m_s']-inner['component_m_s'])
                coordinate=inner['coordinate']+ratio*(outer['coordinate']-inner['coordinate'])
                boundary={'status':'resolved','coordinate':coordinate,'longitude_latitude':point(section,coordinate),'bracket':[dict(inner),dict(outer)]}
                break
            previous=current;current+=direction
        result['boundaries'][label]=boundary
    if not all(b['status']=='resolved' for b in result['boundaries'].values()):
        return {**result,'status':'unresolved_full_span'}
    low,high=(result['boundaries'][k] for k in ['low_coordinate','high_coordinate'])
    span=distance(section,low['coordinate'],high['coordinate'])
    inner_low=max(r['coordinate'] for r in low['bracket']);inner_high=min(r['coordinate'] for r in high['bracket'])
    outer_low=min(r['coordinate'] for r in low['bracket']);outer_high=max(r['coordinate'] for r in high['bracket'])
    native_spacings=(high['coordinate']-low['coordinate'])/(1/3)
    result.update(status='paired_boundaries',span_km=span,grid_bracket_span_km=[distance(section,inner_low,inner_high),distance(section,outer_low,outer_high)],
                  native_cell_spacings=native_spacings,resolution_review_required=native_spacings<4)
    return result


def monthly_profiles(section, minimum_pairs=5):
    result=[]
    for month in range(1,13):
        frames=[f for f in section['frames'] if int(f['time'][5:7])==month]
        if len(frames)<minimum_pairs:
            raise ValueError('Insufficient monthly archive sampling')
        profile=[]
        for i, grid in enumerate(frames[0]['samples']):
            cells=[f['samples'][i] for f in frames]
            if any([c[k] for k in ['coordinate','longitude','latitude']] != [grid[k] for k in ['coordinate','longitude','latitude']] for c in cells):
                raise ValueError('Changed vector-section coordinates')
            complete=[c for c in cells if c['eastward_m_s'] is not None and c['northward_m_s'] is not None]
            u=sum(c['eastward_m_s'] for c in complete)/len(complete) if len(complete)>=minimum_pairs else None
            v=sum(c['northward_m_s'] for c in complete)/len(complete) if len(complete)>=minimum_pairs else None
            component=u if section['component']=='eastward' else -v if v is not None else None
            profile.append({k:grid[k] for k in ['coordinate','longitude','latitude']}|{'eastward_m_s':u,'northward_m_s':v,'component_m_s':component,'paired_source_samples':len(complete)})
        result.append({'month':month,'label':calendar.month_abbr[month],'source_times':[f['time'] for f in frames],'profile':profile})
    return result


def build():
    inventory=source_inventory()
    if json.loads(INVENTORY.read_bytes())!=inventory:
        raise ValueError('Changed acquired section inventory')
    config=json.loads((ROOT/inventory['config_file']).read_bytes())
    if config['fractions']!=[.4,.5,.6] or config['minimum_eligible_component_m_s']!=.02 or config['monthly_cell_minimum_pairs']!=5 or config['rounding_km']!=10 or config['minimum_resolved_cells_for_no_resolution_flag']!=4:
        raise ValueError('Changed declared diagnostic operator')
    documents=[]
    for section in inventory['sections']:
        months=monthly_profiles(section)
        for month in months:
            scenarios=[measure(month['profile'],section,f) for f in config['fractions']]
            nominal=scenarios[1];values=[s['span_km'] for s in scenarios if s['span_km'] is not None]
            month.update(nominal=nominal,threshold_scenarios=scenarios,
                         approximate_section_span_km=math.floor(nominal['span_km']/10+.5)*10 if nominal['span_km'] is not None else None,
                         threshold_sensitivity_span_km=[math.floor(min(values)/10)*10,math.ceil(max(values)/10)*10] if len(values)==3 else None,
                         all_thresholds_resolved=len(values)==3)
        values=[m['approximate_section_span_km'] for m in months if m['approximate_section_span_km'] is not None]
        documents.append({'schema':'osw.basin-monthly-component-span.v1','status':'local_component_section_diagnostic_requires_scientific_review','current_id':section['current_id'],
                          'section_id':section['section_id'],'year':2013,'width_metric':'fixed_orientation_half_peak_'+section['component']+'_component_span',
                          'section_latitude':section['fixed_coordinate'] if section['fixed_axis']=='latitude' else None,
                          'section_longitude_degrees_east':section['fixed_coordinate'] if section['fixed_axis']=='longitude' else None,
                          'source_url':inventory['source_files'][section['section_id']+'.csv']['url'],
                          'section':{k:section[k] for k in ['fixed_axis','fixed_coordinate','varying_axis','domain','peak_search','component']},
                          'scope_note':section['source_scope']+' Local monthly-mean component spans, not flow-normal widths, whole-current dimensions or a seasonal footprint.',
                          'layer':inventory['layer_interpretation'],'time_convention':inventory['time_convention'],
                          'monthly_width_is_mean_of_instantaneous_widths':False,'is_climatology':False,'current_association_verified':False,
                          'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
                          'chart_playback_eligible':True,'whole_current_length_km':None,'whole_current_width_km':None,'annual_length_range_km':None,'annual_width_range_km':None,
                          'measurement_uncertainty_interval_km':None,'is_confidence_interval':False,
                          'source_inventory_file':INVENTORY.relative_to(ROOT).as_posix(),'source_inventory_sha256':digest(INVENTORY),
                          'config_file':inventory['config_file'],'config_sha256':inventory['config_sha256'],
                          'scope_audit_file':section['scope_audit'],'scope_audit_sha256':digest(ROOT/section['scope_audit']),
                          'protocol_file':PROTOCOL.relative_to(ROOT).as_posix(),'protocol_sha256':digest(PROTOCOL),
                          'general_protocol_sha256':digest(ROOT/'plans/ocean-current-width-measurement-protocol-v1.md'),
                          'generator_sha256':digest(Path(__file__)),'acquirer_sha256':digest(ROOT/'analysis/acquire_basin_surface_sections.py'),
                          'range_kind':'finite_boundary_threshold_sensitivity_not_confidence_or_annual_range','months':months,
                          'summary':{'resolved_nominal_months':len(values),'sample_monthly_mean_span_range_km':[min(values),max(values)] if values else None,
                                     'range_kind':'span_of_local_monthly_mean_component_values_not_annual_physical_range'}})
    return documents


def main():
    for document in build():
        path=ROOT/'research'/ (document['section_id']+'-2013-monthly-component-spans.json')
        path.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
        print(document['current_id'],document['summary'])


if __name__=='__main__':
    main()
