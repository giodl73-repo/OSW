"""Display component crossings and separate finite sensitivities."""
from pathlib import Path
import hashlib,json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_p14n_component_spans import ROOT,OUTPUT,verify,encoded

RECEIPT='research/aleutian-p14n-1993-component-spans-figure.json'

def generate():
    report=verify()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-p14n-component-spans-v1'})
    fig,axes=plt.subplots(2,2,figsize=(12,10))
    fig.subplots_adjust(left=.13,right=.97,top=.85,bottom=.25,hspace=.65,wspace=.35)
    fig.suptitle('P14N: measured component spans, with sensitivity',x=.05,ha='left',fontsize=17,fontweight='bold')
    fig.text(.05,.925,'July 1993 | 100–300 m paired velocity means | fixed northern and southern branch windows',fontsize=11)
    for col,branch in enumerate(report['branches']):
        ax=axes[0,col];low,high=branch['latitude_search_window_degrees_north']
        source=[r for r in report['retained_samples'] if low<=r['latitude_degrees_north']<=high]
        # Source acquisition order, no latitude sorting or missing-value bridge.
        for key,label,color,ls in [('eastward_m_s','Eastward u','#176b82','-'),('northward_m_s','Northward v','#a84c28','--')]:
            xs=[];ys=[]
            for i,row in enumerate(source):
                if i and (datetime.fromisoformat(row['observed_at'])-datetime.fromisoformat(source[i-1]['observed_at'])).total_seconds()>5400:xs.append(float('nan'));ys.append(float('nan'))
                xs.append(row['latitude_degrees_north']);ys.append(row['layer_mean'][key])
            ax.plot(xs,ys,color=color,ls=ls,marker='.',markersize=3,lw=1,label=label)
        nominal=branch['boundary_choice_scenarios'][1]
        ax.axhline(nominal['comparison_threshold_m_s'],color='#777',lw=.8,label='50% of selected u peak')
        for side in ['before_peak','after_peak']:
            cross=nominal[side]
            if cross['status']=='resolved':
                ax.plot([cross['inside']['latitude_degrees_north'],cross['outside']['latitude_degrees_north']],[cross['inside']['layer_mean']['eastward_m_s'],cross['outside']['layer_mean']['eastward_m_s']],lw=3,color='#58b8ac')
                ax.scatter(cross['crossing']['latitude_degrees_north'],nominal['comparison_threshold_m_s'],marker='x',s=65,color='#111',zorder=5)
        ax.axhline(0,color='#aaa',lw=.5)
        ax.set(xlim=(low,high),xlabel='Latitude (degrees north); lines follow observation order',ylabel='Layer mean velocity (m/s)',title=branch['branch'].capitalize()+' branch window')
        ax.legend(fontsize=8,loc='best');ax.grid(alpha=.15)
        ax=axes[1,col]
        choices=branch['boundary_choice_scenarios'];sensitivity=branch['velocity_sensitivity_scenarios']
        labels=['40% boundary','50% boundary','60% boundary','50% − 0.06 m/s','50% − 0.02 m/s','50% + 0.02 m/s','50% + 0.06 m/s']
        for i,(row,label) in enumerate(zip(choices+sensitivity,labels)):
            value=row['endpoint_separation_km']
            if value is not None:
                ax.scatter(value,i,color='#176b82' if i<3 else '#a84c28',marker='o' if i<3 else 's',s=40)
                ax.text(value+3,i,f'{value:.1f}',va='center',fontsize=9)
            else:ax.text(2,i,row['status'],va='center')
        ax.axhline(2.5,color='#bbb',lw=.8)
        ax.set(yticks=list(range(7)),yticklabels=labels,ylim=(6.7,-.7),xlim=(0,175),xlabel='WGS84 crossing endpoint separation (km)')
        ax.tick_params(axis='y',labelsize=8);ax.grid(axis='x',alpha=.2)
        ax.set_title(f"50% span ≈{nominal['display_endpoint_separation_km']} km; threshold envelope {branch['complete_boundary_choice_envelope_km'][0]}–{branch['complete_boundary_choice_envelope_km'][1]} km",fontsize=10)
    fig.text(.05,.185,'Crosses and teal segments: 50% crossing and its native bracket. All 14 declared scenarios resolve.',fontsize=10)
    fig.text(.05,.15,'Northern first bracket moves only 0.34 km in one hour: a temporal crossing near a CTD occupation, not a verified edge.',fontsize=10)
    fig.text(.05,.115,'Velocity comparators are separate finite scenarios (m/s), motivated by GPS-related hourly uncertainty; no width CI.',fontsize=10)
    fig.text(.05,.08,'Neither span is a flow-normal or whole-current width. No annual range, inventory width, map ribbon or ranking admitted.',fontsize=10)
    fig.text(.05,.045,'Source: UH/NOAA JASADCP 00016 / P14N; Chen & Firing (2006), doi:10.1029/2005JC003064. OSW calculation.',fontsize=9)
    prefix=ROOT/'figures/aleutian-p14n-1993-component-spans'
    fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':'P14N branch component spans and separate finite sensitivities'})
    fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW P14N component spans v1'});plt.close(fig)
    svg=prefix.with_suffix('.svg');svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n').encode())
    receipt={'schema':'osw.source-figure.v1','generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'source_file':OUTPUT,'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),
             'figures':{suffix:{'file':prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in ['.svg','.png']},
             'physical_edges_rendered':False,'sensitivity_is_confidence_interval':False}
    (ROOT/RECEIPT).write_bytes(encoded(receipt));return receipt

if __name__=='__main__':print(json.dumps(generate()))
