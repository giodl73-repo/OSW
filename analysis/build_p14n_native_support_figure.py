"""Show actual sampling, motion and unaveraged native vector support."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from build_p14n_native_field_audit import ROOT,OUTPUT,verify,encoded

RECEIPT='research/aleutian-p14n-1993-native-vector-support-figure.json'
def generate():
    r=verify();rows=r['profiles'];dates=[datetime.fromisoformat(p['ensemble_end_utc']) for p in rows]
    hydro=json.loads((ROOT/'research/aleutian-p14n-1993-hydrography-correspondence.json').read_bytes())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-p14n-native-support-v1'})
    fig,axes=plt.subplots(2,2,figsize=(12,9.8));fig.subplots_adjust(left=.08,right=.97,top=.84,bottom=.25,wspace=.28,hspace=.5)
    fig.suptitle('P14N: underway support beside station occupations',x=.05,ha='left',fontsize=17,fontweight='bold')
    fig.text(.05,.925,'13–18 July 1993 | 1,585 native profiles | 100–300 m joint means | no current width admitted',fontsize=11)
    for ax in axes.flat:
        for event in r['ctd_event_intervals']:ax.axvspan(datetime.fromisoformat(event['begin_utc']),datetime.fromisoformat(event['end_utc']),color='#ddd',alpha=.5,lw=0)
        ax.xaxis.set_major_locator(mdates.DayLocator(tz=timezone.utc));ax.xaxis.set_major_formatter(mdates.DateFormatter('%d Jul',tz=timezone.utc))
        ax.set_xlim(dates[0],dates[-1]);ax.set_xlabel('UTC ensemble-end date');ax.grid(alpha=.15)
    ax=axes[0,0]
    for motion,label,color,marker in [('slow','Slow ≤0.5 m/s','#777','.'),('intermediate','Intermediate','#ae682b','x'),('underway_eligible','Underway-eligible ≥2 m/s','#176b82','^')]:
        keep=[i for i,row in enumerate(rows) if row['ship_motion_class']==motion]
        ax.scatter([dates[i] for i in keep],[rows[i]['latitude_degrees_north'] for i in keep],color=color,marker=marker,s=7,linewidths=.5,label=label)
    ax.set(ylabel='Source latitude (degrees north)',title='Native observations remain in acquisition order');ax.legend(fontsize=8,loc='upper right')
    ax=axes[0,1];ship_x=[];ship_y=[]
    for i,row in enumerate(rows):
        if i and (row['source_time_index']!=rows[i-1]['source_time_index']+1 or (dates[i]-dates[i-1]).total_seconds()>450):
            ship_x.append(dates[i]);ship_y.append(float('nan'))
        ship_x.append(dates[i]);ship_y.append(row['ship_speed_m_s'])
    ax.plot(ship_x,ship_y,color='#243f58',lw=.8)
    for cutoff,style in [(1,':'),(2,'--'),(3,':')]:ax.axhline(cutoff,color='#a84c28',ls=style,lw=.7)
    ax.set(ylabel='Source ship-speed magnitude (m/s)',title='Fixed 1 / 2 / 3 m/s eligibility sensitivity')
    hourly=hydro['velocity_section']['profiles']
    for ax,key,title in [(axes[1,0],'eastward_m_s','Ocean eastward u'),(axes[1,1],'northward_m_s','Ocean northward v')]:
        available=[i for i,p in enumerate(rows) if p['layer_mean'][key] is not None]
        underway=[i for i in available if rows[i]['ship_motion_class']=='underway_eligible']
        ax.scatter([dates[i] for i in available],[rows[i]['layer_mean'][key] for i in available],s=6,color='#999',alpha=.45,label='All supported native means')
        ax.scatter([dates[i] for i in underway],[rows[i]['layer_mean'][key] for i in underway],s=10,marker='^',color='#176b82',alpha=.8,label='Underway-eligible native means')
        xs=[];ys=[]
        for i,p in enumerate(hourly):
            t=datetime.fromisoformat(p['observed_at'])
            if i and (t-datetime.fromisoformat(hourly[i-1]['observed_at'])).total_seconds()>5400:xs.append(t);ys.append(float('nan'))
            xs.append(t);ys.append(p['layer_mean'][key])
        ax.plot(xs,ys,color='#111',lw=1.1,label='Original hourly product')
        ax.axhline(0,color='#888',lw=.5);ax.set(ylabel='100–300 m mean velocity (m/s)',title=title);ax.legend(fontsize=7,loc='upper right')
    fig.text(.05,.185,'Grey bands: nominal CTD BE–EN intervals. 685 native profiles overlap; none of the 568 ≥2 m/s profiles does.',fontsize=10)
    fig.text(.05,.15,'All 1 / 2 / 3 m/s scenarios retained: 623 / 568 / 532 eligible profiles in 42 / 19 / 19 contiguous runs.',fontsize=10)
    fig.text(.05,.115,'No further OSW time averaging; paper GPS-related five-minute two-SD 0.47 m/s is not a width error interval.',fontsize=10)
    fig.text(.05,.08,'Editing flags and joint support retained. Short/long velocity-frame correspondence checked; no second ship correction.',fontsize=10)
    fig.text(.05,.045,'Source: UH/NOAA JASADCP 00016; CCHDO / original station log; Chen & Firing (2006), doi:10.1029/2005JC003064.',fontsize=9)
    prefix=ROOT/'figures/aleutian-p14n-1993-native-vector-support'
    fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':'P14N native vectors, ship motion and nominal CTD-event intervals'})
    fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW P14N native vector support v1'});plt.close(fig)
    svg=prefix.with_suffix('.svg');svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n').encode())
    receipt={'schema':'osw.source-figure.v1','generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_file':OUTPUT,'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),
             'figures':{suffix:{'file':prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in ['.svg','.png']},'osw_temporal_ocean_velocity_averaging_applied':False,'physical_edges_rendered':False}
    (ROOT/RECEIPT).write_bytes(encoded(receipt));return receipt

if __name__=='__main__':print(json.dumps(generate()))
