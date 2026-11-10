"""Independent monthly profiles and interannual tables; missing spans stay missing."""
import json
from html import escape
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_indian_secc_oscar_climatology import ROOT, OUTPUT, diagnostics

plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-indian-secc-climatology-v1'})


def save(fig,path,title,description):
    fig.savefig(ROOT/path,metadata={'Date':None,'Creator':'OSW independent diagnostic graphics','Description':description})
    p=ROOT/path
    text=p.read_text(encoding='utf8').replace('<svg ','<svg role="img" aria-labelledby="source-title source-desc" ',1)
    i=text.index('>',text.index('<svg '))+1
    text=text[:i]+f'\n<title id="source-title">{escape(title)}</title>\n<desc id="source-desc">{escape(description)}</desc>'+text[i:]
    p.write_bytes(('\n'.join(s.rstrip() for s in text.splitlines())+'\n').encode())
    plt.close(fig)


def main():
    data=json.loads((ROOT/OUTPUT).read_bytes())
    docs=diagnostics(data)
    for doc in docs:
        fig,axes=plt.subplots(3,4,figsize=(13,9),sharex=True,sharey=True)
        for ax,m in zip(axes.flat,doc['months']):
            ax.axvspan(-6,-2.5,color='#e8edef')
            ax.axhline(0,color='#657680',linewidth=.7)
            ax.plot([p['coordinate'] for p in m['profile']],[p['component_m_s']*100 if p['component_m_s'] is not None else np.nan for p in m['profile']],'o-',color='#087a91',markersize=2,linewidth=1)
            nominal=m['nominal']
            if nominal['span_km'] is not None:
                edges=[nominal['boundaries'][side]['coordinate'] for side in ['low_coordinate','high_coordinate']]
                ax.hlines(nominal['threshold_m_s']*100,*edges,color='#b36616',linewidth=2)
                ax.scatter(edges,[nominal['threshold_m_s']*100]*2,color='#b36616',s=16,zorder=3)
            label=f"{m['approximate_section_span_km']} km" if m['approximate_section_span_km'] is not None else 'Unresolved span'
            if m['crossing_outside_frequency_window']:label+=' / outside context'
            ax.set_title(m['label']+' / '+label,fontsize=9)
            ax.grid(alpha=.2)
        for ax in axes[-1]:ax.set_xlabel('Latitude (degrees north)')
        for ax in axes[:,0]:ax.set_ylabel('Eastward component (cm/s)')
        title=f"Indian SECC region / {doc['section_longitude_degrees_east']:.3f} E / 1995–2016 monthly climatology"
        fig.suptitle(title,fontsize=14)
        caption=('Equal-year mean of paired yearly monthly vectors; not mean yearly width. Grey: peak-search context, not current edges.\n'
                 'Orange: paired 50% crossings. Missing/weak/domain-edge cases remain unresolved. Outside-context crossings do not identify current modes.\n'
                 'OSCAR2017.0 / ESR / NOAA PIFSC. Nominal15 m coordinate, near-surface diagnostic; not depth-resolved observations.\n'
                 'Local component spans, not flow-normal current widths, annual physical ranges or seasonal current footprints.')
        fig.text(.05,.035,caption,fontsize=10,linespacing=1.6)
        fig.tight_layout(rect=(0,.15,1,.95))
        save(fig,doc['profile_figure'],title,caption)
    matrices=[]
    for section in data['sections']:
        matrices.append(np.array([[m['approximate_section_span_km'] if m['approximate_section_span_km'] is not None else np.nan for m in section['yearly'][str(y)]['months']] for y in range(1995,2017)]))
    vmax=max(float(np.nanmax(m)) for m in matrices)
    vmax=np.ceil(vmax/100)*100
    cmap=plt.colormaps['viridis'].copy();cmap.set_bad('#dedede')
    fig,axes=plt.subplots(1,2,figsize=(14,12),sharey=True)
    fig.subplots_adjust(left=.07,right=.88,top=.91,bottom=.15,wspace=.08)
    for ax,matrix,s in zip(axes,matrices,data['sections']):
        graph=ax.imshow(matrix,aspect='auto',vmin=0,vmax=vmax,cmap=cmap)
        ax.set_title(f"{s['longitude_degrees_east']:.3f} E / separate native column")
        ax.set_xticks(range(12),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],rotation=45,ha='right')
        ax.set_yticks(range(22),range(1995,2017))
        for y in range(22):
            for x in range(12):
                value=matrix[y,x]
                ax.text(x,y,'—' if np.isnan(value) else str(int(value)),ha='center',va='center',fontsize=8,color='#333333' if np.isnan(value) or value>vmax*.55 else 'white')
    fig.colorbar(graph,cax=fig.add_axes([.9,.23,.018,.6]),label='Local monthly-mean half-peak span (km)')
    title='Indian SECC study region / yearly monthly component spans / 1995–2016'
    fig.suptitle(title,fontsize=16)
    count=sum(int(np.isfinite(m).sum()) for m in matrices)
    caption=(f'{count}/528 monthly profiles have paired nominal boundaries. Grey/dash: weak or unresolved, never zero width.\n'
             'Columns remain separate. Finite year-to-year spread is conditional on resolved sections, not measurement error or annual extrema.\n'
             'OSCAR2017.0 / ESR / NOAA PIFSC, near-surface diagnostic. Current association and physical boundary validation remain unresolved.')
    fig.text(.04,.035,caption,fontsize=11,linespacing=1.7)
    save(fig,docs[0]['interannual_figure'],title,caption)
    print('Built two monthly profile figures and yearly table:',count,'of528 resolved')


if __name__=='__main__':main()
