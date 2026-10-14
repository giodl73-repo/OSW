"""Plot full declared offshore profiles without implying a tracked current."""
from html import escape
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_west_australian_oscar_spans import ROOT,OUTPUT,build
from build_basin_surface_section_spans import diagnostic_matches

def main():
    doc=build()
    if not diagnostic_matches(json.loads(OUTPUT.read_bytes()),doc):raise ValueError('Stale offshore diagnostic')
    plt.rcParams['svg.fonttype']='none';plt.rcParams['svg.hashsalt']='osw-west-australian-offshore-v1'
    fig,axes=plt.subplots(3,4,figsize=(14,9),sharex=True,sharey=True)
    for ax,month in zip(axes.flat,doc['months']):
        rows=month['profile'];xs=[r['coordinate'] for r in rows]
        ys=[r['component_m_s']*100 if r['component_m_s'] is not None else np.nan for r in rows]
        ax.axvspan(*doc['section']['peak_search'],color='#e8edef')
        for r in rows:
            if r['component_m_s'] is None:ax.axvspan(r['coordinate']-1/6,r['coordinate']+1/6,color='#eee8de',hatch='///',alpha=.8)
        ax.axhline(0,color='#657680',linewidth=.7)
        ax.plot(xs,ys,color='#087a91',linewidth=1,marker='.',markersize=2)
        n=month['nominal']
        if n['span_km'] is not None:
            edges=[n['boundaries'][s]['coordinate'] for s in ['low_coordinate','high_coordinate']]
            ax.hlines(n['threshold_m_s']*100,*edges,color='#c47418',linewidth=2)
            ax.scatter(edges,[n['threshold_m_s']*100]*2,color='#c47418',s=13,zorder=3)
        label=str(month['approximate_section_span_km'])+' km' if month['approximate_section_span_km'] is not None else 'Unresolved'
        if n['resolution_review_required']:label+='; <4 cells'
        if n.get('peak_at_search_edge'):label+='; search edge'
        ax.set_title(month['label']+' / '+label,fontsize=9);ax.set_xlim(*doc['section']['domain']);ax.grid(alpha=.2)
    for ax in axes[-1]:ax.set_xlabel('Longitude (degrees east)')
    for ax in axes[:,0]:ax.set_ylabel('Northward component (cm/s)')
    fig.suptitle('West Australian offshore context / 32 S / 2013 monthly component profiles',fontsize=15)
    fig.text(.05,.045,'Grey: editorial peak-search window. Orange: connected 50% peak crossings. Hatching: insufficient complete u/v support, not a land mask.\n'
        'OSCAR 2017.0 / ESR and NOAA PIFSC, nominal 15 m coordinate. Ten monthly spans are narrower than four native grid spacings.\n'
        'Independent peaks shift between 80.7 and 103 E; no tracked current identity, current width, seasonal footprint or annual physical range.',fontsize=10)
    fig.tight_layout(rect=(0,.12,1,.95))
    target=ROOT/'figures/west-australian-32s-2013-monthly-component-profiles.svg'
    fig.savefig(target,metadata={'Date':None},bbox_inches='tight')
    svg=target.read_text(encoding='utf-8').replace('<svg ','<svg role="img" aria-labelledby="wac-profile-title wac-profile-desc" ',1)
    pos=svg.index('>',svg.index('<svg '))+1
    title='West Australian offshore context: twelve full-domain monthly northward profiles, 2013'
    desc='Full 60 to 116 E section at 32 S, with editorial peak search and half-peak crossings. Ten spans require resolution review. The peak changes location; neither continuity nor named-current identity is established. Missing support is hatched and is not interpreted as land. These are local diagnostic spans, not seasonal current widths.'
    svg=svg[:pos]+'\n<title id="wac-profile-title">'+escape(title)+'</title>\n<desc id="wac-profile-desc">'+escape(desc)+'</desc>'+svg[pos:]
    target.write_bytes(('\n'.join(line.rstrip() for line in svg.splitlines())+'\n').encode())
    scratch=ROOT/'.pytest_cache/west-australian-review';scratch.mkdir(parents=True,exist_ok=True)
    fig.savefig(scratch/'profiles.png',dpi=110,bbox_inches='tight');plt.close(fig)
    print(target.relative_to(ROOT))

if __name__=='__main__':main()
