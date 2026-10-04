"""Fixed-depth observed section comparison; no full width or route admission."""
import hashlib,json,math
from pathlib import Path
from pyproj import Geod
from acquire_antilles_ladcp_profiles import build

ROOT=Path(__file__).resolve().parents[1]
GEOD=Geod(ellps='WGS84')
OUTPUT=ROOT/'research/antilles-ab0505-400m-section-diagnostic.json'
FIGURE=ROOT/'figures/antilles-ab0505-400m-section-diagnostic.svg'

def measure(samples,fraction=.5):
    if not 0<fraction<1 or not math.isfinite(fraction):raise ValueError('Invalid relative threshold')
    usable=[(i,r) for i,r in enumerate(samples) if r['northward_m_s'] is not None and r['quality_class']=='usable']
    if not usable:return {'status':'no_usable_samples','offshore_span_km':None,'full_width_km':None}
    index,peak=max(usable,key=lambda pair:pair[1]['northward_m_s'])
    if peak['northward_m_s']<=0:return {'status':'no_northward_peak','offshore_span_km':None,'full_width_km':None}
    threshold=peak['northward_m_s']*fraction
    result={'status':'offshore_boundary_unresolved','threshold_fraction':fraction,'threshold_m_s':threshold,
            'peak_cast_id':peak['cast_id'],'peak_coordinates_lon_lat':peak['coordinates_lon_lat'],
            'peak_northward_m_s':peak['northward_m_s'],'offshore_span_km':None,'full_width_km':None,
            'metric':'sampled_peak_to_offshore_half_peak_boundary_not_full_width',
            'nearshore_boundary_status':'not_diagnosed','is_confidence_interval':False}
    previous=peak
    # Samples ordered west to east. Never cross a missing or cautioned cast.
    for outer in samples[index+1:]:
        if outer['northward_m_s'] is None or outer['quality_class']!='usable':
            result['status']='offshore_boundary_blocked_by_missing_or_caution_cast';return result
        if outer['northward_m_s']<=threshold:
            ratio=(threshold-previous['northward_m_s'])/(outer['northward_m_s']-previous['northward_m_s'])
            coordinate=[a+ratio*(b-a) for a,b in zip(previous['coordinates_lon_lat'],outer['coordinates_lon_lat'])]
            distance=GEOD.inv(*peak['coordinates_lon_lat'],*coordinate)[2]/1000
            result.update({'status':'one_sided_offshore_span_candidate','offshore_span_km':round(distance,6),
                           'offshore_crossing_coordinates_lon_lat':coordinate,'bracketing_cast_ids':[previous['cast_id'],outer['cast_id']],
                           'station_bracket_span_km':sorted([GEOD.inv(*peak['coordinates_lon_lat'],*r['coordinates_lon_lat'])[2]/1000 for r in [previous,outer]])})
            return result
        previous=outer
    return result

def compute(inventory):
    sections=[]
    for group,label in [('abaco_first','4-8 May 2005'),('abaco_repeat','18-23 May 2005')]:
        casts=[r for r in inventory['profiles'] if r['section_group']==group]
        rows=[]
        for cast in sorted(casts,key=lambda r:r['coordinates_lon_lat'][0]):
            sample=next((r for r in cast['samples'] if r['depth_m']==400),None)
            rows.append({'cast_id':cast['cast_id'],'coordinates_lon_lat':cast['coordinates_lon_lat'],
                         'average_cast_time_utc':cast['average_cast_time_utc'],'quality_class':cast['provider_quality_class'],
                         'northward_m_s':sample['northward_m_s'] if sample else None,
                         'eastward_m_s':sample['eastward_m_s'] if sample else None,
                         'error_velocity_m_s':sample['error_velocity_m_s'] if sample else None,
                         'sample_status':'sample_at_400m' if sample else 'no_sample_at_400m'})
        sections.append({'id':group,'label':label,'samples':rows,'half_peak_diagnostic':measure(rows)})
    return {'schema':'osw.ladcp-section-diagnostic.v1','current_id':'antilles','status':'derived_local_diagnostic_requires_review',
            'depth_m':400,'depth_role':'fixed_instrument_depth_not_400_dbar','velocity_component':'northward',
            'threshold_rule':'0.5 times maximum positive northward sample among provider-usable casts, separately by occupation; walk eastward to first bracket without crossing missing/caution casts',
            'geographic_role':'transverse_observation_section_not_current_axis','tides_removed':False,'sections':sections,
            'whole_current_length_km':None,'whole_current_width_km':None,'annual_length_range_km':None,'annual_width_range_km':None,
            'width_rank_eligible':False,'seasonal_playback_eligible':False,
            'remaining_gates':['Independent review of section membership, tide/error-velocity impact, threshold and sampled-peak representativeness.',
                               'Diagnose both depth-compatible boundaries and sampling sufficiency before full-width measurement.',
                               'Recover along-current axes and repeated annual support; two May occupations are not a seasonal cycle.']}

def render(document):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    matplotlib.rcParams['svg.hashsalt']='osw-antilles-ab0505-v1'
    fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True,sharey=True,layout='constrained')
    for ax,section in zip(axes,document['sections']):
        rows=section['samples']
        ax.axhline(0,color='#677880',lw=.7)
        ax.plot([r['coordinates_lon_lat'][0] for r in rows],[r['northward_m_s'] if r['quality_class']=='usable' and r['northward_m_s'] is not None else math.nan for r in rows],color='#137f87',marker='o',ms=3)
        caution=[r for r in rows if r['quality_class']=='caution' and r['northward_m_s'] is not None]
        ax.scatter([r['coordinates_lon_lat'][0] for r in caution],[r['northward_m_s'] for r in caution],color='#b16d13',marker='x',s=35)
        missing=[r for r in rows if r['northward_m_s'] is None]
        for row in missing:ax.axvline(row['coordinates_lon_lat'][0],color='#a6aeb1',ls=':',lw=1)
        result=section['half_peak_diagnostic']
        if result['offshore_span_km'] is not None:
            peak=result['peak_coordinates_lon_lat'][0];edge=result['offshore_crossing_coordinates_lon_lat'][0]
            ax.plot([peak,edge],[result['threshold_m_s']]*2,color='#4c537e',lw=2)
            ax.text((peak+edge)/2,result['threshold_m_s']+.06,f"{result['offshore_span_km']:.0f} km one-sided span",ha='center',fontsize=9)
        else:ax.text(.98,.88,'Offshore threshold blocked by caution/missing casts',transform=ax.transAxes,ha='right',fontsize=9)
        ax.set_title(section['label']+' | 400 m instrument depth',loc='left',fontsize=11)
        ax.set_ylabel('Northward velocity (m/s)');ax.grid(alpha=.2)
    axes[-1].set_xlabel('Longitude (degrees east; negative = west)')
    fig.suptitle('Antilles-region observed sections at 26.5 N\nTwo May 2005 occupations; no full width, route or annual cycle inferred',fontsize=13)
    handles=[Line2D([],[],color='#137f87',marker='o',label='Provider-usable samples'),Line2D([],[],color='#b16d13',marker='x',ls='',label='Provider caution; excluded from span'),Line2D([],[],color='#a6aeb1',ls=':',label='No sample at 400 m')]
    axes[-1].legend(handles=handles,loc='lower right',fontsize=8)
    fig.savefig(FIGURE,metadata={'Date':None});plt.close(fig)

if __name__=='__main__':
    inventory=build();document=compute(inventory)
    path=ROOT/'research/antilles-ab0505-ladcp-profile-inventory.json'
    document.update({'inventory_file':path.relative_to(ROOT).as_posix(),'inventory_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'figure':FIGURE.relative_to(ROOT).as_posix(),'source_url':'https://www.aoml.noaa.gov/phod/wbts/data.php'})
    render(document)
    OUTPUT.write_text(json.dumps(document,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps([{'id':r['id'],**r['half_peak_diagnostic']} for r in document['sections']]))
