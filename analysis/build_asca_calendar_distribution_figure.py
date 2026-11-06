"""Plot conditional ASCA sample ranges with finite/attempted counts."""
from pathlib import Path
import calendar,hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from build_asca_calendar_distributions import ROOT,REPORT,PROTOCOL,digest,verify,encoded

MANIFEST='research/asca-component-calendar-distributions-figure.json'
OPERATOR='analysis/build_asca_calendar_distribution_figure.py'
BASE='figures/asca-component-calendar-distributions'

def build():
    doc=verify();rows=[r for r in doc['records'] if r['primary_convention']]
    years=[r for r in rows if r['cohort_kind']=='calendar_year']
    whole=[r for r in rows if r['cohort_kind']=='source_period']
    months=[r for r in rows if r['cohort_kind']=='calendar_month']
    plt.rcParams.update({'svg.hashsalt':'osw-asca-calendar-v1','font.family':'DejaVu Sans','font.size':12})
    fig,(annual,monthly)=plt.subplots(2,1,figsize=(12,13),gridspec_kw={'height_ratios':[4,10]})
    xmax=max(r['statistics']['maximum_km'] or 0 for r in rows)*1.12
    def draw(ax,items,labels):
        for y,r in enumerate(items):
            s=r['statistics']
            if s['count']:
                ax.hlines(y,s['minimum_km'],s['maximum_km'],color='#73838a',linewidth=2)
                ax.plot([s['minimum_km'],s['maximum_km']],[y,y],linestyle='none',marker='|',color='#536a74',markersize=11)
                ax.barh(y,s['q75_km']-s['q25_km'],left=s['q25_km'],height=.33,color='#267b92')
                ax.plot(s['median_km'],y,marker='|',color='#102f3b',markersize=18,markeredgewidth=2)
            else:ax.text(5,y,'No resolved spans',va='center')
            ax.text(1.02,y,f"{r['resolved_samples']} / {r['attempted_samples']} resolved",transform=ax.get_yaxis_transform(),va='center',fontsize=11)
        ax.set_yticks(range(len(items)),labels);ax.set_ylim(len(items)-.4,-.7)
        ax.set_xlim(0,xmax);ax.set_xlabel('Conditional recorded component span (km)')
        ax.grid(axis='x',color='#dce4e7');ax.set_axisbelow(True)
        for side in ['top','right','left']:ax.spines[side].set_visible(False)
        ax.tick_params(axis='y',length=0)
    draw(annual,whole+years,['All source dates']+[str(r['year'])+(' · full nominal year' if r['complete_nominal_calendar_year_support'] else ' · partial year') for r in years])
    annual.set_title('Source period and calendar years',loc='left',fontweight='bold')
    labels=[]
    for r in months:
        partial=sum(not m['complete_calendar_time_support'] for m in r['source_month_bins'])
        labels.append(calendar.month_abbr[r['month']]+(' · partial source bin' if partial else ''))
    draw(monthly,months,labels)
    monthly.set_title('Pooled UTC calendar months · uneven source support, not climatology',loc='left',fontweight='bold')
    fig.suptitle('Agulhas ASCA: recorded component-span distributions\n100 m fixed-array −v · source-declared 50% peak convention',fontsize=17,y=.985)
    fig.legend(handles=[Line2D([0],[0],color='#73838a',label='Finite min–max'),Patch(color='#267b92',label='25th–75th percentiles'),Line2D([0],[0],color='#102f3b',marker='|',linestyle='none',markersize=14,label='Median')],loc='upper center',bbox_to_anchor=(.5,.935),ncol=3,frameon=False)
    fig.text(.02,.015,'Each mapped source timestamp has one vote; 40 h filtering means samples are not independent.\nStatistics condition on resolved boundaries. Failed attempts remain counted.\nFull nominal calendar support does not establish physical annual extrema or a flow-normal width.\nOSW summaries from Beal, McMonigal, Gunn & Novelli / ASCA 2.0; doi:10.5281/zenodo.20515068 (CC BY 4.0).',fontsize=10)
    fig.subplots_adjust(left=.26,right=.77,top=.875,bottom=.105,hspace=.45)
    assets={}
    for suffix in ['svg','png']:
        path=BASE+'.'+suffix
        kwargs={'metadata':{'Date':None}} if suffix=='svg' else {'dpi':150}
        fig.savefig(ROOT/path,**kwargs)
        if suffix=='svg':
            svg=(ROOT/path).read_text(encoding='utf-8')
            (ROOT/path).write_bytes(('\n'.join(line.rstrip() for line in svg.splitlines())+'\n').encode('utf-8'))
        assets[suffix]={'file':path,'sha256':digest(path)}
    plt.close(fig)
    report={'schema':'osw.asca-calendar-distribution-figure.v1','source_file':REPORT,'source_sha256':digest(REPORT),
        'protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),'generator_file':OPERATOR,'generator_sha256':digest(OPERATOR),
        'matplotlib_version':matplotlib.__version__,'figures':assets,'primary_fraction':.5,'plotted_groups':len(rows),
        'source_profiles':931,'partial_years_labeled':True,'failed_attempt_counts_rendered':True,
        'physical_edges_rendered':False,'confidence_intervals_rendered':False,'climatology_inferred':False,
        'figure_alt':'Agulhas ASCA 100 m conditional component spans: finite min/max, interquartile span and median for all source dates, three calendar years and twelve pooled months. Finite/attempted counts remain visible. Partial 2016 and 2018 are labeled; 2017 has full nominal support but many unresolved cases. Not physical annual extrema or independent observations.'}
    (ROOT/MANIFEST).write_bytes(encoded(report));return report

if __name__=='__main__':
    report=build();print(json.dumps({'plotted_groups':report['plotted_groups'],'assets':list(report['figures'])}))
