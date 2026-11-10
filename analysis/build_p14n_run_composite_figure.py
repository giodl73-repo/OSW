"""Plot conditional run links and every declared crossing outcome."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from build_p14n_run_composite import ROOT,OUTPUT,verify,encoded,eligibility

RECEIPT='research/aleutian-p14n-1993-run-composite-figure.json'

def generate():
 report=verify()
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-p14n-run-composite-v1'})
 fig=plt.figure(figsize=(15,10));grid=fig.add_gridspec(2,2,width_ratios=[1,1.2],left=.06,right=.985,top=.81,bottom=.27,hspace=.3,wspace=.36)
 styles=[('#8563aa','o'),('#126b7e','s'),('#b26324','^')]
 fig.suptitle('P14N run composite: every nominal half-peak case remains unresolved',x=.04,ha='left',fontsize=16,fontweight='bold')
 fig.text(.04,.93,'July 1993 | 100–300 m eastward component | 18 conditional cases resolve; 108 do not | no physical width admitted',fontsize=11)
 handles=[Line2D([],[],color=color,marker=marker,linestyle='none',label=f'≥{speed} m/s ship speed') for speed,(color,marker) in zip([1,2,3],styles)]
 handles.extend([Line2D([],[],color='#126b7e',linestyle='--',label='Conditional links: gaps ≤6 h'),Line2D([],[],color='#666',marker='x',linestyle='none',label='Short / ineligible summary'),
  Line2D([],[],color='#555',linestyle=':',label='Nominal 50% reference'),Line2D([],[],color='#777',linestyle='-.',label='60% conditional crossings')])
 fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.04,.905),ncol=4,frameon=False,fontsize=9)
 for ri,(name,window) in enumerate([('northern',[44,46]),('southern',[41,43])]):
  ax=fig.add_subplot(grid[ri,0])
  for experiment,(color,marker) in zip(report['experiments'],styles):
   rows=experiment['run_summaries'];primary=experiment['ship_speed_cutoff_m_s']==2
   for r in rows:
    latitude=r['mean']['latitude_degrees_north'];u=r['mean']['eastward_m_s']
    if not window[0]<=latitude<=window[1]:continue
    good=eligibility(r,window)=='eligible'
    ax.plot(latitude,u,marker=marker if good else 'x',color=color,alpha=1 if primary else .6,linestyle='none',markersize=6 if primary else 4)
    if primary:
     low,high=r['contributor_latitude_range']
     ax.hlines(u,low,high,color=color,alpha=.6,linewidth=1.5)
   if primary:
    for a,b,gap in zip(rows,rows[1:],experiment['adjacent_gaps']):
     if eligibility(a,window)==eligibility(b,window)=='eligible' and gap['status']=='eligible_subject_to_time_cap' and gap['unobserved_time_gap_hours']<=6:
      ax.plot([a['mean']['latitude_degrees_north'],b['mean']['latitude_degrees_north']],[a['mean']['eastward_m_s'],b['mean']['eastward_m_s']],linestyle='--',color=color,linewidth=1)
    case=next(c for c in experiment['cases'] if c['branch']==name and c['maximum_unobserved_time_gap_hours']==6)
    if case['selected_peak']:
     ax.axhline(case['selected_peak']['eastward_m_s']*.5,color='#555',linestyle=':',linewidth=1)
    higher=case['scenarios'][2]
    if higher['endpoint_separation_km'] is not None:
     for side in ['before_peak','after_peak']:ax.axvline(higher[side]['crossing']['latitude_degrees_north'],color='#777',linestyle='-.',linewidth=.8)
     hours=higher['full_bracketing_observation_period_utc']['hours']
     ax.text(.02,.05,f"60% case ≈{higher['rounded_endpoint_separation_km']:.0f} km; full bracket {hours:.1f} h",transform=ax.transAxes,fontsize=9,bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':2})
  ax.axhline(0,color='#aaa',linewidth=.7);ax.set_xlim(*window);ax.grid(alpha=.15)
  ax.set_title(name.capitalize()+': nominal 50% unresolved',loc='left',fontsize=12)
  ax.set_ylabel('Mean eastward u (m/s)');ax.set_xlabel('Run-summary latitude (degrees north)')
 matrix=[];labels=[];values=[]
 for experiment in report['experiments']:
  for case in experiment['cases']:
   outcomes=[s['rounded_endpoint_separation_km'] for s in case['scenarios']]
   values.append(outcomes);matrix.append([v is not None for v in outcomes])
   labels.append(f"{experiment['ship_speed_cutoff_m_s']:.0f} m/s · {case['maximum_unobserved_time_gap_hours']} h · {case['branch'][0].upper()}")
 ax=fig.add_subplot(grid[:,1]);ax.imshow(np.array(matrix,dtype=int),aspect='auto',cmap=ListedColormap(['#edf0f2','#c1e3eb']),vmin=0,vmax=1)
 for i,row in enumerate(values):
  for j,value in enumerate(row):ax.text(j,i,'—' if value is None else str(value),ha='center',va='center',fontsize=9)
 ax.set_yticks(range(len(labels)),labels,fontsize=9)
 ax.set_xticks(range(7),['40%','50%','60%','50%\n−0.06','50%\n−0.02','50%\n+0.02','50%\n+0.06'],fontsize=9)
 ax.tick_params(axis='x',top=True,labeltop=True,bottom=False,labelbottom=False)
 ax.set_title('Conditional separations (km)\n— unresolved / ineligible, never zero',fontsize=12,pad=38)
 ax.set_xlabel('Threshold offsets in m/s; N/S = northern/southern window',labelpad=8,fontsize=9)
 ax.axvline(.5,color='#555',linewidth=1);ax.axvline(1.5,color='#555',linewidth=1)
 notes=[
  'All 18 nominal 50% cases remain unresolved, including the declared 2 m/s / 6 h primary assumption. No successful threshold replaces them.',
  'Only northern 60% and positive threshold-displacement cases resolve at 6 h / 12 h caps. Their ≈80–140 km values are different assumptions, not a width range.',
  'These successful cases use bracketing observations spanning about 23 h. A 6 h inter-run cap does not establish synoptic or steady flow.',
  'Bars show contributor latitude footprints, not uncertainty. Dashed links assume temporal comparability; they are not observed velocities within gaps.',
  'Source gaps, unsupported profiles, short summaries and branch-window edges remain barriers. No latitude sorting or source-value filling.',
  'Source: UH/NOAA JASADCP 00016; OSW declared exploratory operator. No physical width, annual extrema or state intersection admitted.']
 for i,line in enumerate(notes):fig.text(.04,.205-i*.029,line,fontsize=9)
 assets={}
 for suffix in ['svg','png']:
  path=ROOT/f'figures/aleutian-p14n-1993-run-composite.{suffix}'
  fig.savefig(path,dpi=150,metadata={'Date':None} if suffix=='svg' else {'Software':'OSW'})
  if suffix=='svg':
   text=path.read_text(encoding='utf8')
   opening=text.index('>',text.index('<svg'))
   text=text[:opening+1]+'\n<title>P14N conditional run composite</title>\n<desc>All nominal half-peak cases remain unresolved. Eighteen sensitivity cases resolve under declared cross-run comparability assumptions, not physical current widths. Full bracketing observations span about 23 hours; all 126 outcomes are retained.</desc>'+text[opening+1:]
   text=text.replace('<svg ','<svg role="img" ',1);path.write_text(text,encoding='utf8',newline='\n')
  assets['.'+suffix]={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 plt.close(fig)
 receipt={'schema':'osw.source-figure.v1','generator_file':Path(__file__).relative_to(ROOT).as_posix(),
  'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_file':OUTPUT,
  'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),'figures':assets,
  'scenario_counts':report['scenario_counts'],'nominal_half_peak_resolved_cases':0,
  'physical_edges_rendered':False,'conditional_links_visualized':True,'footprints_are_uncertainty':False}
 (ROOT/RECEIPT).write_bytes(encoded(receipt));return receipt

if __name__=='__main__':print(json.dumps(generate()['scenario_counts']))
