"""Show actual water properties and candidate offsets without interpolated edges."""
from pathlib import Path
from datetime import datetime
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_p14n_hydrography_companion import ROOT,OUTPUT,verify,encoded
from build_aleutian_p14n_vector_section import verify as verify_vectors

RECEIPT='research/source-data/cchdo-p14n-1993/figure.json'

def generate():
 report=verify();vector=verify_vectors()
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-p14n-hydrography-v1'})
 fig,axes=plt.subplots(2,2,figsize=(12,9.5));fig.subplots_adjust(left=.08,right=.92,top=.84,bottom=.25,hspace=.52,wspace=.38)
 fig.suptitle('P14N: hydrography beside nearby velocity observations',x=.05,ha='left',fontsize=17,fontweight='bold')
 fig.text(.05,.92,'13–18 July 1993 | 17 CTD casts | 84 candidate CTD–hourly-profile pairs | no physical current width admitted',fontsize=10)
 for ax,key,title,label,cmap in [(axes[0,0],'practical_salinity_pss78','Practical salinity: PSS-78','Practical salinity (dimensionless)','viridis'),(axes[0,1],'in_situ_temperature_its90_degC','In-situ temperature: ITS-90','Temperature (degrees C)','plasma')]:
  xs=[];ys=[];values=[];ox=[];oy=[]
  for cast in report['casts']:
   for cell in cast['cells']:
    if cell['joint_acceptable']:
     xs.append(cast['latitude_degrees_north']);ys.append(cell['depth_m']);values.append(cell[key])
    else:ox.append(cast['latitude_degrees_north']);oy.append(cell['depth_m'])
  image=ax.scatter(xs,ys,c=values,cmap=cmap,s=10,marker='s',linewidths=0)
  ax.scatter(ox,oy,color='#777',marker='x',s=8,linewidths=.5)
  ax.axhline(100,color='#222',ls='--',lw=.6);ax.axhline(300,color='#222',ls='--',lw=.6)
  ax.set(xlim=(40,48),ylim=(350,0),xlabel='Cast latitude (degrees north)',ylabel='Converted depth (m)',title=title)
  fig.colorbar(image,ax=ax,pad=.02,fraction=.045,label=label)
 ax=axes[1,0];matched={r['adcp_source_time_index'] for r in report['candidate_pairs']}
 for key,label,color in [('eastward_m_s','Eastward u','#176b82'),('northward_m_s','Northward v','#a84c28')]:
  xs=[];ys=[];mx=[];my=[]
  for i,row in enumerate(vector['profiles']):
   if i and (datetime.fromisoformat(row['observed_at'])-datetime.fromisoformat(vector['profiles'][i-1]['observed_at'])).total_seconds()>5400:xs.append(np.nan);ys.append(np.nan)
   value=row['layer_mean'][key];xs.append(row['latitude_degrees_north']);ys.append(value if value is not None else np.nan)
   if key=='eastward_m_s' and row['source_time_index'] in matched and value is not None:mx.append(row['latitude_degrees_north']);my.append(value)
  ax.plot(xs,ys,color=color,marker='.',markersize=2.5,lw=1,label=label)
  if key=='eastward_m_s':ax.scatter(mx,my,facecolors='none',edgecolors='#243f58',s=22,linewidths=.6,label='Candidate-paired hour')
 ax.axhline(0,color='#777',lw=.6);ax.set(xlim=(40,48),xlabel='Latitude (degrees north)',ylabel='100–300 m mean velocity (m/s)',title='Original layer means; candidate-paired hours marked');ax.legend(fontsize=8);ax.grid(alpha=.2)
 ax=axes[1,1];pairs=report['candidate_pairs']
 ax.scatter([r['adcp_minus_nominal_bottom_hours'] for r in pairs],[r['position_separation_km'] for r in pairs],s=18,color='#176b82')
 ax.axvline(-3,ls='--',color='#666',lw=.8);ax.axvline(3,ls='--',color='#666',lw=.8);ax.axhline(15,ls='--',color='#666',lw=.8)
 ax.set(xlim=(-3.3,3.3),ylim=(-.3,16),xlabel='ADCP time minus CTD bottom time (hours)',ylabel='Separation between source positions (km)',title='All 84 qualifying pairs; no nearest-only selection');ax.grid(alpha=.2)
 fig.text(.05,.18,'Filled property cells: joint WOCE QC2. Grey crosses: other source codes, including 7 (despiked); raw values retained.',fontsize=10)
 fig.text(.05,.145,'2,525 / 3,009 upper-ocean cells meet QC2. No hydrography interpolation. Depth = -GSW z_from_p; original pressure retained.',fontsize=10)
 fig.text(.05,.11,'Pairing uses nominal BO (cast-bottom) time ±3 hours and distance ≤15 km. Dashed limits are selection rules, not errors.',fontsize=10)
 fig.text(.05,.075,'Bottom time is not sampling time at 100–300 m. The historical temperature-correction notice remains unresolved.',fontsize=10)
 fig.text(.05,.04,'Source: CCHDO 325023_1 CTD / original station log; UH/NOAA JASADCP 00016. Gunnar Roden; E. Kestenare / E. Firing.',fontsize=9)
 prefix=ROOT/'figures/aleutian-p14n-1993-hydrography-correspondence'
 fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':'P14N hydrography and candidate observation correspondence','Description':'Actual CTD water properties and source QC; original ADCP layer means and qualifying time/distance offsets. No current edges or width inferred.'})
 fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW P14N hydrography correspondence v1'});plt.close(fig)
 svg=prefix.with_suffix('.svg');svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n').encode())
 record={'schema':'osw.source-figure.v1','generator_file':'analysis/build_p14n_hydrography_figure.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_file':OUTPUT,'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),'figures':{suffix:{'file':prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in ['.svg','.png']},'source_panel_copied':False,'hydrography_interpolated_to_adcp':False,'physical_edges_rendered':False}
 (ROOT/RECEIPT).write_bytes(encoded(record));return record

if __name__=='__main__':print(json.dumps(generate()))
