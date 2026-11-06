"""Plot retained observations without interpolating a current edge or missing data."""
import hashlib,json
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from build_aleutian_p14n_vector_section import ROOT,OUTPUT,verify,encoded

RECEIPT='research/source-data/jasadcp-p14n-1993/figure.json'
def build():
 report=verify();rows=report['profiles']
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'osw-aleutian-p14n-1993-vector-v1'})
 fig,axes=plt.subplots(2,2,figsize=(12,9));fig.subplots_adjust(left=.08,right=.94,top=.84,bottom=.24,hspace=.52,wspace=.28)
 fig.suptitle('Subarctic region: directly measured July 1993 velocities',x=.05,ha='left',fontsize=17,fontweight='bold')
 fig.text(.05,.925,'P14N / JASADCP 00016 | 13–18 July 1993 | hourly reduced product | no physical current width admitted',fontsize=10)
 lat=np.array([r['latitude_degrees_north'] for r in rows]);lon=np.array([r['longitude_degrees_east'] for r in rows])
 ax=axes[0,0];ax.scatter(lon,lat,s=10,color='#243f58');ax.set(xlim=(178,180),ylim=(40,48),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)',title='Sampling locations: coordinate context')
 ax.set_xticks([178,179,180]);ax.grid(alpha=.2)
 ax=axes[0,1]
 for key,label,color in [('eastward_m_s','Eastward u','#176b82'),('northward_m_s','Northward v','#a84c28')]:
  x=[];y=[]
  for i,row in enumerate(rows):
   if i and (datetime.fromisoformat(row['observed_at'])-datetime.fromisoformat(rows[i-1]['observed_at'])).total_seconds()>5400:x.append(np.nan);y.append(np.nan)
   x.append(row['latitude_degrees_north']);y.append(np.nan if row['layer_mean'][key] is None else row['layer_mean'][key])
  ax.plot(x,y,marker='.',markersize=3,lw=1,label=label,color=color)
 ax.axhline(0,color='#666',lw=.6);ax.set(xlim=(40,48),xlabel='Latitude (degrees north)',ylabel='Layer mean velocity (m/s)',title='100–300 m jointly supported layer means');ax.legend(fontsize=9);ax.grid(alpha=.2)
 norm=Normalize(-.6,.6);cmap=plt.get_cmap('RdBu_r');image=None
 for ax,key,label in [(axes[1,0],'eastward_m_s','Eastward u'),(axes[1,1],'northward_m_s','Northward v')]:
  xs=[];ys=[];values=[];mx=[];my=[]
  for row in rows:
   for cell in row['profile']:
    if cell[key] is None:mx.append(row['latitude_degrees_north']);my.append(cell['depth_m'])
    else:xs.append(row['latitude_degrees_north']);ys.append(cell['depth_m']);values.append(cell[key])
  image=ax.scatter(xs,ys,c=values,s=9,marker='s',cmap=cmap,norm=norm,linewidths=0)
  ax.scatter(mx,my,s=8,marker='x',color='#666',linewidths=.5)
  ax.set(xlim=(40,48),ylim=(340,20),xlabel='Latitude (degrees north)',ylabel='Depth (m)',title=label+' at actual hourly positions')
  ax.axhline(100,color='#333',ls='--',lw=.6);ax.axhline(300,color='#333',ls='--',lw=.6)
 cax=fig.add_axes([.29,.165,.43,.019]);fig.colorbar(image,cax=cax,orientation='horizontal',label='Earth-coordinate velocity (m/s); grey crosses = missing')
 fig.text(.05,.105,'132 profiles · 31 levels · 4,030 / 4,092 valid vectors. Unconnected locations; no missing-data interpolation.',fontsize=10)
 fig.text(.05,.077,'Depth means require ≥160 m joint u/v support. Acquisition order retained; 16 northward steps and one 2-hour gap.',fontsize=10)
 fig.text(.05,.049,'Branch association needs matching water-mass evidence. Latitude windows do not define edges or seasonal ranges.',fontsize=10)
 fig.text(.05,.022,'Source: UH / NOAA JASADCP; G. Roden; E. Kestenare / E. Firing. Context: Chen & Firing (2006), doi:10.1029/2005JC003064.',fontsize=9)
 prefix=ROOT/'figures/aleutian-p14n-1993-observed-vectors'
 fig.savefig(prefix.with_suffix('.svg'),metadata={'Date':None,'Title':'Observed Subarctic-region vector section, July1993','Description':'Measured east/north velocities, missing samples, layer means and unconnected source positions. No physical current width.'})
 fig.savefig(prefix.with_suffix('.png'),dpi=150,metadata={'Software':'OSW P14N observed vector section v1'});plt.close(fig)
 assets={suffix:{'file':prefix.with_suffix(suffix).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(prefix.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in ['.svg','.png']}
 result={'schema':'osw.source-figure.v1','generator_file':__file__ and 'analysis/build_aleutian_p14n_vector_figure.py','generator_sha256':hashlib.sha256((ROOT/'analysis/build_aleutian_p14n_vector_figure.py').read_bytes()).hexdigest(),'source_file':OUTPUT,'source_sha256':hashlib.sha256((ROOT/OUTPUT).read_bytes()).hexdigest(),'figures':assets,'source_panel_copied':False,'physical_edges_rendered':False,'gap_interpolation_applied':False}
 (ROOT/RECEIPT).write_bytes(encoded(result));return result

if __name__=='__main__':print(json.dumps(build()))
