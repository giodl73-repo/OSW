"""Plot a published width statistic and its discontinuous source sampling windows."""
from pathlib import Path
import json,hashlib,datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from check_west_spitsbergen_selected_core import validate,AUDIT,ROOT

def build():
    d=validate();plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-wsc-selected-core-v1'})
    fig,(width,time)=plt.subplots(2,1,figsize=(10,6.5),gridspec_kw={'height_ratios':[1,1.15]})
    fig.subplots_adjust(left=.12,right=.96,top=.83,bottom=.24,hspace=.85)
    fig.suptitle('West Spitsbergen Current: a selected core-width statistic',x=.05,ha='left',fontsize=16,fontweight='bold')
    fig.text(.05,.90,'Published estimate at 77.25 N | Dundas & Fer (2026) | 2020-2023 missions',fontsize=10)
    width.barh([0],[28],height=.25,color='#1b7279',alpha=.28)
    width.errorbar([28],[0],xerr=[7],fmt='o',color='#12474d',capsize=8,markersize=8,lw=2)
    width.text(28,.29,'28 km',ha='center',fontsize=14,fontweight='bold')
    width.set(xlim=(0,45),ylim=(-.45,.65),yticks=[],xlabel='Local zonal core-width statistic (km); whisker = reported standard deviation of 7 km')
    width.spines[['left','top','right']].set_visible(False);width.grid(axis='x',alpha=.2)
    width.set_title('Selected high-transport sections; not a whole-current width',loc='left',fontsize=11,pad=12)
    for i,w in enumerate(d['section_windows']):
        start=mdates.date2num(dt.date.fromisoformat(w['start']));end=mdates.date2num(dt.date.fromisoformat(w['end']))
        time.barh([2-i],[end-start+1],left=start,height=.45,color='#1b7279')
        time.text(start,2-i+.3,f"{w['sections']} sections",fontsize=9)
    time.set_yticks([2,1,0],['Mission 1','Mission 2','Mission 3']);time.xaxis_date();time.xaxis.set_major_locator(mdates.MonthLocator(interval=6));time.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    time.set_xlim(dt.date(2020,8,1),dt.date(2023,4,1));time.set_ylim(-.55,2.8);time.spines[['top','right']].set_visible(False);time.grid(axis='x',alpha=.2)
    time.set_title('Target-section observation windows (Table 1); gaps are unsampled',loc='left',fontsize=11,pad=10)
    fig.text(.05,.16,'The 7 km standard deviation describes western-boundary variability. It is not a confidence interval,',fontsize=10)
    fig.text(.05,.13,'observed minimum/maximum, annual range or physical-boundary error. Selected-section membership is unextracted.',fontsize=10)
    fig.text(.05,.09,'Geostrophic shear + satellite surface reference; 2 km grid, 40 km horizontal objective-mapping scale.',fontsize=9)
    fig.text(.05,.06,'Source: Dundas & Fer, Ocean Science 22, 1003-1021 (2026), doi:10.5194/os-22-1003-2026, CC BY 4.0.',fontsize=9)
    fig.text(.05,.03,'OSW source extraction and new graphic. No geographic width edges or seasonal widths inferred.',fontsize=9)
    prefix=ROOT/'figures/west-spitsbergen-selected-core-width'
    fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':'Published WSC selected-core width and source sampling windows','Description':'A published local zonal core width of 28 km with a separately identified standard deviation of 7 km, and three discontinuous target-section observation windows. These are not annual extrema, confidence limits or physical geographic edges.'})
    fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW selected-core figure v1'});plt.close(fig)
    svg=prefix.with_suffix('.svg');raw=svg.read_text(encoding='utf8');raw=raw.replace('<svg ','<svg role="img" aria-label="Published WSC core width and discontinuous sampling windows" ',1);svg.write_bytes(('\n'.join(line.rstrip() for line in raw.splitlines())+'\n').encode())
    files=[prefix.with_suffix(s).relative_to(ROOT).as_posix() for s in ['.svg','.png']]
    return {'schema':'osw.selected-core-width-figure.v1','audit_file':AUDIT,'audit_sha256':hashlib.sha256((ROOT/AUDIT).read_bytes()).hexdigest(),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},'no_geographic_width_edges_inferred':True,'standard_deviation_is_annual_range':False}

if __name__=='__main__':
    receipt=build();(ROOT/'research/source-data/dundas-fer-wsc-2026/figure.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print('Built published width and sampling-window graphic')
