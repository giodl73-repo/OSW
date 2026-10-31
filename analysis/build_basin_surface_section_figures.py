"""Scientific profile panels for exact monthly component diagnostic readings."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from html import escape
from build_basin_surface_section_spans import ROOT, build
matplotlib.rcParams['svg.fonttype']='none'
matplotlib.rcParams['svg.hashsalt']='osw-basin-component-profiles-v1'


def main():
    for doc in build():
        saved=json.loads((ROOT/'research'/ (doc['section_id']+'-2013-monthly-component-spans.json')).read_bytes())
        if saved!=doc:
            raise ValueError('Stale monthly span report')
        fig, axes=plt.subplots(3,4,figsize=(13,9),sharex=True,sharey=True)
        for ax,month in zip(axes.flat,doc['months']):
            xs=[p['coordinate'] for p in month['profile']]
            ys=[p['component_m_s']*100 if p['component_m_s'] is not None else np.nan for p in month['profile']]
            ax.axvspan(*doc['section']['peak_search'],color='#e8edef',label='Peak-search context')
            ax.axhline(0,color='#657680',linewidth=.7)
            ax.plot(xs,ys,'o-',color='#087a91',markersize=2,linewidth=1)
            nominal=month['nominal']
            if nominal['span_km'] is not None:
                edges=[nominal['boundaries'][side]['coordinate'] for side in ['low_coordinate','high_coordinate']]
                ax.hlines(nominal['threshold_m_s']*100,*edges,color='#c47418',linewidth=2)
                ax.scatter(edges,[nominal['threshold_m_s']*100]*2,color='#c47418',s=16,zorder=3)
            label=str(month['approximate_section_span_km'])+' km' if month['approximate_section_span_km'] is not None else 'Unresolved span'
            if nominal['resolution_review_required']:
                label+='; <4 cells'
            if nominal.get('peak_at_search_edge'):
                label+='; search edge'
            ax.set_title(month['label']+' / '+label,fontsize=9)
            ax.grid(alpha=.2)
        for ax in axes[-1]:
            ax.set_xlabel('Longitude (degrees east)' if doc['section']['varying_axis']=='longitude' else 'Latitude (degrees north)')
        for ax in axes[:,0]:
            ax.set_ylabel(doc['section']['component'].title()+' component (cm/s)')
        fig.suptitle(doc['current_id'].replace('-',' ').title()+' context / 2013 local monthly component spans',fontsize=15)
        fig.text(.05,.055,'Grey: peak-search window, not current edges. Orange: nominal 50% peak boundary diagnostic.\n'
                 'Fixed section / OSCAR 2017.0 (ESR / NOAA PIFSC) near-surface model; association and resolution require review.\n'
                 'Peak changes do not establish tracked current evolution. Not flow-normal width, annual physical range or climatology.',fontsize=10)
        fig.tight_layout(rect=(0,.12,1,.95))
        target=ROOT/'figures'/ (doc['section_id']+'-2013-monthly-component-profiles.svg')
        fig.savefig(target,metadata={'Date':None},bbox_inches='tight')
        title=doc['current_id'].replace('-',' ').title()+' context: twelve 2013 monthly local component profiles'
        description='Each panel shows the full directional velocity profile, the peak-search context and nominal half-peak boundaries. Values narrower than four native grid spacings are flagged. Independent peaks do not establish tracked current evolution, current width or annual extrema. Exact values and source profiles are available in the corresponding query samples and diagnostic JSON.'
        # Keep Matplotlib's namespace prefixes and symbol references intact.
        svg=target.read_text(encoding='utf-8').replace('<svg ','<svg role="img" aria-labelledby="surface-span-title surface-span-desc" ',1)
        end=svg.index('>',svg.index('<svg '))+1
        svg=svg[:end]+'\n<title id="surface-span-title">'+escape(title)+'</title>\n<desc id="surface-span-desc">'+escape(description)+'</desc>'+svg[end:]
        target.write_bytes(('\n'.join(line.rstrip() for line in svg.splitlines())+'\n').encode('utf-8'))
        plt.close(fig)
        print('Built profile panels:',doc['section_id'])


if __name__=='__main__':
    main()
