"""Diagnose a connected monthly eastward component from a pinned OSCAR section."""
import hashlib
import json
import math
from pathlib import Path
from pyproj import Geod
from acquire_pacific_necc_oscar_section import build as source_inventory

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'plans/pacific-necc-oscar-section-width-protocol-v1.md'
INVENTORY=ROOT/'research/pacific-necc-oscar-2013-section-inventory.json'
OUTPUT=ROOT/'research/pacific-necc-oscar-2013-section-diagnostic.json'
FIGURE=ROOT/'figures/pacific-necc-oscar-2013-monthly-profiles.svg'
GEOD=Geod(ellps='WGS84')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(profile,threshold=0):
    if type(threshold) not in (int,float) or not math.isfinite(threshold) or threshold<0:
        raise ValueError('Invalid eastward threshold')
    lats=[p['latitude'] for p in profile]
    if len(lats)<3 or any(not math.isfinite(lat) for lat in lats) or any(b<=a for a,b in zip(lats,lats[1:])):
        raise ValueError('Latitude grid must increase')
    if any(p['eastward_m_s'] is not None and not math.isfinite(p['eastward_m_s']) for p in profile):
        raise ValueError('Nonfinite velocity must be represented as missing')
    candidates=[(i,p) for i,p in enumerate(profile) if 2<=p['latitude']<=10 and p['eastward_m_s'] is not None]
    if not candidates:return {'threshold_m_s':threshold,'status':'missing_peak_support','span_km':None,'boundaries':{}}
    index,peak=max(candidates,key=lambda pair:pair[1]['eastward_m_s'])
    result={'threshold_m_s':threshold,'peak_latitude':peak['latitude'],'peak_eastward_m_s':peak['eastward_m_s'],'span_km':None,'boundaries':{}}
    if peak['eastward_m_s']<.1 or peak['eastward_m_s']<=threshold:
        return dict(result,status='weak_or_no_eligible_peak')
    for direction,label in [(-1,'south'),(1,'north')]:
        previous=index;current=index+direction
        boundary={'status':'domain_edge_without_crossing','latitude':None,'bracket':None}
        while 0<=current<len(profile):
            inner,outer=profile[previous],profile[current]
            if outer['eastward_m_s'] is None:
                boundary['status']='missing_before_crossing';break
            if outer['eastward_m_s']<=threshold:
                fraction=(threshold-inner['eastward_m_s'])/(outer['eastward_m_s']-inner['eastward_m_s'])
                boundary={'status':'resolved','latitude':inner['latitude']+fraction*(outer['latitude']-inner['latitude']),'bracket':[dict(inner),dict(outer)]}
                break
            previous=current;current+=direction
        result['boundaries'][label]=boundary
    if all(b['status']=='resolved' for b in result['boundaries'].values()):
        south=result['boundaries']['south']['latitude'];north=result['boundaries']['north']['latitude']
        result.update(status='resolved_connected_component',span_km=GEOD.inv(-140,south,-140,north)[2]/1000)
    else:result['status']='unresolved_full_span'
    return result


def monthly_profiles(frames):
    months=[]
    for month in range(1,13):
        selected=[f for f in frames if int(f['time'][5:7])==month]
        if len(selected)<5:raise ValueError('Insufficient monthly samples')
        lats=[s['latitude'] for s in selected[0]['samples']]
        if any([s['latitude'] for s in f['samples']]!=lats for f in selected):raise ValueError('Changed monthly grid')
        profile=[]
        for i,lat in enumerate(lats):
            values=[f['samples'][i]['eastward_m_s'] for f in selected]
            profile.append({'latitude':lat,'eastward_m_s':None if any(v is None for v in values) else sum(values)/len(values),'sample_count':len(values),'missing_count':sum(v is None for v in values)})
        measures=[measure(profile,t) for t in [0,.05,.1]]
        months.append({'id':f'oscar-necc-140w-2013-{month:02d}','month':month,'label':f'2013-{month:02d}','sample_times':[f['time'] for f in selected],'sample_count':len(selected),'profile':profile,'zero_crossing':measures[0],'threshold_sensitivity':measures[1:]})
    return months


def build():
    source=source_inventory()
    saved=json.loads(INVENTORY.read_text(encoding='utf-8'))
    if source!=saved:raise ValueError('Saved section inventory differs from provider bytes')
    months=monthly_profiles(source['frames'])
    spans=[m['zero_crossing']['span_km'] for m in months if m['zero_crossing']['span_km'] is not None]
    return {'schema':'osw.current-monthly-section-diagnostic.v1','current_id':source['current_id'],'status':'derived_width_candidate_requires_scientific_review','source_inventory_file':str(INVENTORY.relative_to(ROOT)).replace('\\','/'),'source_inventory_sha256':digest(INVENTORY),'protocol_file':str(PROTOCOL.relative_to(ROOT)).replace('\\','/'),'protocol_sha256':digest(PROTOCOL),'section_longitude_degrees_east':-140,'nominal_depth_coordinate_m':15,'layer':source['layer_interpretation'],'year':2013,'width_metric':'connected_positive_zonal_component_of_equal_sample_monthly_mean','boundary_rule':'first_zero_crossing_on_each_side_of_largest_eligible_peak_in_2_to_10N','peak_eligibility_m_s':.1,'sensitivity_thresholds_m_s':[.05,.1],'whole_current_representative':False,'width_rank_eligible':False,'seasonal_playback_eligible':False,'whole_current_width_km':None,'whole_current_length_km':None,'annual_width_range_km':None,'annual_length_range_km':None,'is_confidence_interval':False,'is_climatology':False,'monthly_width_is_mean_of_instantaneous_widths':False,'months':months,'summary':{'resolved_months':len(spans),'unresolved_months':12-len(spans),'local_monthly_mean_span_km':None if not spans else [min(spans),max(spans)],'range_role':'resolved_2013_local_monthly_mean_diagnostic_not_annual_whole_current_extrema'},'remaining_gates':['Independent boundary, branch and product-error review.','Repeat years/sections and compatible products before representative seasonal ranges.','No route or canonical measurement admission from this section alone.']}


def plot(document):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt']='osw-necc-2013-section-v1'
    fig,axes=plt.subplots(3,4,figsize=(13,9),sharex=True,sharey=True)
    for ax,month in zip(axes.flat,document['months']):
        profile=month['profile'];ax.plot([p['latitude'] for p in profile],[p['eastward_m_s'] for p in profile],color='#087f88')
        ax.axhline(0,color='#485b65',linewidth=.8)
        for b in month['zero_crossing']['boundaries'].values():
            if b['latitude'] is not None:ax.axvline(b['latitude'],color='#b37612',linestyle='--',linewidth=1)
        width=month['zero_crossing']['span_km']
        label='width unresolved' if width is None else f'~{round(width/10)*10} km'
        ax.set_title(f"{month['label']} | {month['sample_count']} samples | {label}",fontsize=10)
        ax.set_xlim(0,12);ax.set_ylim(-.9,.9);ax.grid(alpha=.2)
    fig.suptitle('Pacific NECC | 140 W | 2013 monthly-mean OSCAR section diagnostics',fontsize=15)
    fig.supxlabel('Latitude (degrees north)',y=.045);fig.supylabel('Eastward zonal velocity (m/s)')
    fig.text(.5,.014,'Dashed boundaries: connected u > 0 component. Nominal 15 m surface product; one year, not climatology or whole-current width.',ha='center',fontsize=9)
    fig.tight_layout(rect=[.025,.09,1,.95]);fig.savefig(FIGURE,metadata={'Date':None});plt.close(fig)


def main():
    document=build();OUTPUT.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8');plot(document)
    print(json.dumps(document['summary']))


if __name__=='__main__':main()
