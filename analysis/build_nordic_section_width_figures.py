"""Independent source-width figures: no invented midpoint, errors or seasonality."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_nordic_section_widths import ROOT, NOR, WSC, records, validate_row, visual

def build():
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-nordic-section-widths-v1','font.size':11})
    for owner,filename in [(NOR,'norwegian-fer-2020-section-width.svg'),
                           (WSC,'spitsbergen-kolas-2018-section-widths.svg')]:
        rows=records(owner)
        for row in rows:validate_row(row)
        rows=[visual(r) for r in rows]
        wsc=owner==WSC
        fig,ax=plt.subplots(figsize=(11,6 if wsc else 4))
        fig.subplots_adjust(left=.23,right=.92,top=.82,bottom=.32 if wsc else .43)
        for i,row in enumerate(rows):
            y=len(rows)-1-i
            span=row['width_range_km'];point=row['approximate_width_km']
            if span:
                ax.hlines(y,*span,color='#08798b',linestyles='dashed',linewidth=2)
                ax.plot(span,[y,y],'|',color='#08798b',markersize=12)
            if point is not None:
                tube=row['original_regional_context'].get('tube',1)
                ax.plot(point,y,'o' if tube==1 else 's',color='#08798b' if tube==1 else '#8c5e20',markersize=7)
            label=f'{point} km [{span[0]}–{span[1]}]' if point is not None and span else f'{span[0]}–{span[1]} km' if span else f'{point} km'
            ax.annotate(label,(span[1] if span else point,y),xytext=(10,0),textcoords='offset points',va='center')
        labels=[r['original_regional_context']['section']+' · '+('threshold tube 1' if r['original_regional_context']['tube']==1 else 'transport tube 2') for r in reversed(rows)] if wsc else ['Gimsøy · four occupations']
        ax.set_yticks(range(len(rows)),labels)
        ax.set_xlim(0,80 if wsc else 40);ax.set_ylim(-.6,len(rows)-.4)
        ax.set_xlabel('Source-defined section span (km)');ax.grid(axis='x',alpha=.2)
        ax.spines[['top','right','left']].set_visible(False)
        fig.suptitle('West Spitsbergen Current · three sections, two methods' if wsc else 'Proposed Norwegian Atlantic Slope Current · Gimsøy section span',fontsize=16)
        if wsc:
            caption=('August 2015 cruise snapshot; section order is geographic, not a time series.\n'
                     'Circles: primary 0.04 m/s threshold. Dashed spans: 0.02/0.04/0.08 m/s sensitivity, not errors.\n'
                     'Squares: alternate ~1.3 Sv transport-conserving tube; 10% flux tolerance is not width uncertainty.\n'
                     'Source: Kolås & Fer (2018), doi:10.5194/os-14-1603-2018, Table 2, p1611 · CC BY 4.0.\n'
                     'No annual extrema, fixed depth layer or mapped width edges inferred. Independent OSW graphic.')
        else:
            caption=('Four occupations: 30 Jul / 19 Nov 2016; 8 Mar / 7 Jun 2017. No per-date widths assigned.\n'
                     '20% of maximum depth-integrated relative geostrophic current; surface-pressure reference.\n'
                     'Exact width integration depths unspecified. No midpoint, annual extrema or width error inferred.\n'
                     'Source: Fer et al. (2020), doi:10.5194/os-16-685-2020, p692 · CC BY 4.0.\n'
                     'Norwegian Current catalog-name ambiguity retained. Independent OSW graphic.')
        fig.text(.04,.025,caption,fontsize=10,linespacing=1.7)
        fig.savefig(ROOT/'figures'/filename,format='svg',metadata={'Date':None,'Creator':'OSW; source-defined Nordic section width comparison','Title':'Source-defined Nordic section widths','Description':caption})
        target=ROOT/'figures'/filename
        target.write_text('\n'.join(line.rstrip() for line in target.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
        plt.close(fig)
        print('Built',filename)

if __name__=='__main__':build()
