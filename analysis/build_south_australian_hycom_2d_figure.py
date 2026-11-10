"""Fixed source examples and all-date availability; no derived current edges."""
import json
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from acquire_south_australian_hycom_2d import ROOT, DIRECTORY, verify, sha

GENERATOR='analysis/build_south_australian_hycom_2d_figure.py'
STEM='figures/south-australian-hycom-2d-source'
RECEIPT='research/south-australian-hycom-2d-source-figure.json'
# Fixed before viewing the acquired cube: first, midpoint and last source day.
EXAMPLES=(0,182,365)


def build():
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-sac-source-v1'})
    receipt,arrays,report=verify()
    u=arrays['water_u'].astype(float)*.001
    v=arrays['water_v'].astype(float)*.001
    valid=(arrays['water_u']!=-30000)&(arrays['water_v']!=-30000)
    speed=np.where(valid,np.hypot(u,v),np.nan)
    lon,lat=np.meshgrid(arrays['lon'],arrays['lat'])
    fig,axes=plt.subplots(1,4,figsize=(16,7),layout='constrained')
    cmap=plt.colormaps['viridis'].copy();cmap.set_bad('#d3d8de')
    for ax,index in zip(axes[:3],EXAMPLES):
        image=ax.pcolormesh(lon,lat,np.ma.masked_invalid(speed[index]),shading='nearest',
                            cmap=cmap,vmin=0,vmax=float(np.nanmax(speed)),rasterized=True)
        # Glyphs are direction-only, not displacement predictions. Longitude
        # adjustment and map aspect keep local east/north directions consistent.
        norm=np.hypot(u[index],v[index])
        usable=valid[index]&(norm>0)
        du=np.divide(u[index],norm,out=np.zeros_like(norm),where=usable)/np.cos(np.deg2rad(lat))
        dv=np.divide(v[index],norm,out=np.zeros_like(norm),where=usable)
        sample=(slice(None,None,4),slice(None,None,4))
        ax.quiver(lon[sample],lat[sample],np.ma.masked_where(~usable,du)[sample],
                  np.ma.masked_where(~usable,dv)[sample],angles='xy',scale_units='xy',
                  scale=5,width=.004,color='white',pivot='mid')
        date=datetime(2000,1,1,tzinfo=timezone.utc)+timedelta(hours=float(arrays['time'][index]))
        ax.set_title(date.strftime('%Y-%m-%d · %H:%M UTC')+'\n'+
                     str(report['paired_counts_by_date'][index])+' / 3,876 paired cells')
    fig.colorbar(image,ax=list(axes[:3]),location='bottom',label='Native paired-vector speed (m/s); common all-date scale',shrink=.85)
    availability=axes[3].pcolormesh(lon,lat,valid.sum(axis=0),shading='nearest',vmin=0,vmax=366,cmap='cividis',rasterized=True)
    axes[3].set_title('All 366 source dates\nPaired-vector availability')
    fig.colorbar(availability,ax=axes[3],location='bottom',label='Paired dates per source cell')
    for ax in axes:
        ax.axvline(132,color='#f18b3b',linewidth=1.2,linestyle='--')
        ax.set(xlim=(130,134),ylim=(-38,-32),xlabel='Longitude °E',ylabel='Latitude °N')
        ax.set_aspect(1/np.cos(np.deg2rad(-35)))
        ax.grid(alpha=.15)
    fig.suptitle('Surrounding HYCOM model vectors · 100 m · 2012\n'
                 'Fixed source days 1, 183, 366; direction glyph every fourth cell; dashed line = retained 132°E section',fontsize=13)
    fig.supxlabel('GOFS 3.0 HYCOM+NCODA reanalysis. Longitude/latitude axes; local map aspect at 35°S. Direction-only arrows; zero vectors have no arrow.\n'
                  'Gray = missing paired values, not a coastline. No named-current identity, physical width, or annual physical extrema established.',fontsize=9)
    paths=[]
    for extension in ['png','svg']:
        path=ROOT/(STEM+'.'+extension);fig.savefig(path,dpi=160,metadata={'Date':None} if extension=='svg' else {})
        if extension=='svg':
            ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(path);svg=tree.getroot()
            svg.set('role','img');svg.set('aria-labelledby','sac-source-title sac-source-desc')
            title=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'sac-source-title'});title.text='South Australian investigation: surrounding model source vectors'
            desc=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'sac-source-desc'})
            desc.text='GOFS 3.0 HYCOM+NCODA 100 m daily source vectors for fixed 2012 days 1, 183 and 366, and all-date paired availability. Common speed scale; direction glyphs every fourth cell. Gray is missing paired source data, not a coastline. Dashed line is the original 132 E section. Named-current association and physical width remain unresolved. Numerical source masks, coordinates and availability are retained in source-vectors.npz and quality.json.'
            svg.insert(0,title);svg.insert(1,desc);tree.write(path,encoding='utf8',xml_declaration=True)
        paths.append(path)
    plt.close(fig)
    document={'schema':'osw.south-australian-hycom-2d-source-figure.v1',
              'generator_file':GENERATOR,'generator_sha256':sha(ROOT/GENERATOR),
              'acquisition_file':(DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix(),
              'acquisition_sha256':sha(DIRECTORY/'acquisition.json'),
              'source_indices':list(EXAMPLES),'direction_glyph_stride':4,
              'all_date_speed_scale_m_s':[0,float(np.nanmax(speed))],
              'current_association_verified':False,'width_measurement_admitted':False,
              'figures':{p.relative_to(ROOT).as_posix():sha(p) for p in paths}}
    (ROOT/RECEIPT).write_text(json.dumps(document,indent=2)+'\n',encoding='utf8')
    return document


if __name__=='__main__':print(json.dumps(build(),indent=2))
