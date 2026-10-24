"""Render paired component fields and direction/column context as source evidence."""
from pathlib import Path
import hashlib,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_necc_paired_vector_evidence import ROOT,REPORT,INVENTORY,build,encoded

def generate():
    inventory,report=build()
    if (ROOT/REPORT).read_bytes()!=encoded(report) or (ROOT/INVENTORY).read_bytes()!=encoded(inventory):raise ValueError('Stale paired-vector evidence')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-necc-paired-2013-v1'})
    lons=report['native_longitudes_degrees_east'];lats=report['native_latitudes_degrees_north'];months=np.arange(1,13);edges=np.arange(.5,13.5);lat_edges=np.r_[lats[0]-1/6,(np.asarray(lats[:-1])+lats[1:])/2,lats[-1]+1/6]
    figures={}
    def save(fig,name,title,description):
        prefix=ROOT/'figures'/name
        fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':title,'Description':description});fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW paired vector evidence v1'});plt.close(fig)
        path=prefix.with_suffix('.svg');s=path.read_text(encoding='utf8').replace('<svg ','<svg role="img" aria-label="'+title+'" ',1);path.write_bytes(('\n'.join(line.rstrip() for line in s.splitlines())+'\n').encode())
        figures[name]={suffix:{'file':prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in ['.svg','.png']}
    fig,axes=plt.subplots(2,3,figsize=(12,8.5),sharex=True,sharey=True)
    fig.subplots_adjust(left=.07,right=.91,top=.84,bottom=.24,hspace=.24,wspace=.12)
    fig.suptitle('Pacific NECC region: paired monthly surface-product vectors',x=.05,ha='left',fontsize=16,fontweight='bold')
    fig.text(.05,.92,'2013 OSCAR 2017.0 | target 140 W and two adjacent native columns | not instrument sections',fontsize=10)
    cmap=plt.get_cmap('RdBu_r').copy();cmap.set_bad('#d2d2d2')
    for i,(field,label,step) in enumerate([('eastward_m_s','Eastward component (m/s)',.1),('northward_m_s','Northward component (m/s)',.05)]):
        arrays=[]
        for lon in lons:
            rows=sorted([r for r in report['rows'] if r['source_longitude_degrees_east']==lon],key=lambda r:r['month'])
            arrays.append(np.array([[cell[field] if cell[field] is not None else np.nan for cell in r['profile']] for r in rows]).T)
        limit=max(step,math.ceil(max(np.nanmax(np.abs(a)) for a in arrays)/step)*step)
        for j,(lon,array) in enumerate(zip(lons,arrays)):
            ax=axes[i,j];mesh=ax.pcolormesh(edges,lat_edges,np.ma.masked_invalid(array),cmap=cmap,vmin=-limit,vmax=limit,shading='flat')
            rows=sorted([r for r in report['rows'] if r['source_longitude_degrees_east']==lon],key=lambda r:r['month'])
            ax.scatter([r['month'] for r in rows if r['selected_peak_vector']],[r['selected_peak_vector']['latitude'] for r in rows if r['selected_peak_vector']],s=12,c='black',marker='o')
            ax.set(ylim=(0,12),xticks=months,yticks=np.arange(0,13,2))
            if i==0:ax.set_title(f'{360-lon:.3f} W',fontsize=11)
            if i==1:ax.set_xlabel('Month in 2013')
            if j==0:ax.set_ylabel('Latitude (degrees N)')
        fig.colorbar(mesh,ax=axes[i,:],fraction=.025,pad=.02).set_label(label)
    fig.text(.05,.12,'Dots locate the selected eastward-component peak, not a current axis. Gray cells would indicate missing pairs.',fontsize=10)
    fig.text(.05,.085,'Equal-sample monthly means; 1/3 degree native grid. Nominal depth coordinate 15 m is not a direct instrument depth.',fontsize=9)
    fig.text(.05,.05,'Source: ESR OSCAR / NOAA PIFSC mirror, version 2017.0. OSW derives paired means; current width remains unknown.',fontsize=9)
    save(fig,'necc-paired-2013-monthly-vector-sections','Paired 2013 OSCAR velocity components at three native longitudes','Monthly eastward and northward near-surface product fields. Dots identify selected eastward peaks, not a current axis or physical edges. Source periods and units are explicit.')
    fig,axes=plt.subplots(2,1,figsize=(11,8))
    fig.subplots_adjust(left=.10,right=.96,top=.79,bottom=.28,hspace=.42)
    fig.suptitle('Pacific NECC region: direction and native-column context',x=.05,ha='left',fontsize=16,fontweight='bold')
    fig.text(.05,.91,'Same product and one year | neighboring-column agreement is not independent validation',fontsize=10)
    colors=['#8d411a','#155c83','#5a427a'];markers=['s','o','^']
    for lon,color,marker in zip(lons,colors,markers):
        rows=sorted([r for r in report['rows'] if r['source_longitude_degrees_east']==lon],key=lambda r:r['month']);label=f'{360-lon:.3f} W'
        angles=[r['selected_peak_vector']['direction_degrees_from_east'] if r['selected_peak_vector'] else np.nan for r in rows]
        spans=[r['zero_crossing_component_span']['span_km'] if r['zero_crossing_component_span']['span_km'] is not None else np.nan for r in rows]
        axes[0].plot(months,angles,color=color,marker=marker,label=label,markersize=5)
        axes[1].plot(months,spans,color=color,marker=marker,label=label,markersize=5)
    axes[0].axhline(15,color='#555',ls='--',lw=1);axes[0].axhline(-15,color='#555',ls='--',lw=1);axes[0].axhline(0,color='#aaa',lw=.7)
    axes[0].set(ylim=(-90,90),ylabel='Peak direction from east (degrees)',title='OSW attention guides at +/-15 degrees; not admission or error thresholds')
    fig.legend(*axes[0].get_legend_handles_labels(),ncol=3,loc='center',bbox_to_anchor=(.55,.86),frameon=False)
    axes[1].set(ylabel='Meridional component span (km)',xlabel='Month in 2013',title='First connected u=0 crossings; these are not flow-normal current widths')
    for ax in axes:ax.set(xticks=months,xlim=(.7,12.3));ax.grid(alpha=.2)
    axes[1].set_ylim(bottom=0)
    fig.text(.05,.15,'Lines connect monthly source summaries, not parcel trajectories. Missing full spans stay missing, never zero.',fontsize=10)
    fig.text(.05,.11,'The target reproduces all 12 earlier u-only monthly means. Added v reveals direction; no cosine width correction is made.',fontsize=9)
    fig.text(.05,.075,'Spatial differences are product context, not uncertainty intervals or annual physical width extrema.',fontsize=9)
    fig.text(.05,.04,'Source: ESR OSCAR / NOAA PIFSC mirror (2017.0). OSW paired-vector diagnostics; physical current association unresolved.',fontsize=9)
    save(fig,'necc-paired-2013-direction-column-context','Direction and component-span context across three OSCAR columns','Three native longitude columns show monthly peak direction and source component zero-crossing spans. Attention guides are OSW choices, not measurement errors. No annual or flow-normal current width is inferred.')
    return {'schema':'osw.necc-paired-vector-figures.v1','report_file':REPORT,'report_sha256':hashlib.sha256((ROOT/REPORT).read_bytes()).hexdigest(),'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figures':figures,'physical_geometry_admitted':False,'new_width_record_admitted':False}

if __name__=='__main__':
    receipt=generate();(ROOT/'research/source-data/oscar-necc-vectors-2013/figure.json').write_bytes(encoded(receipt));print('Rendered two paired-vector evidence figures')
