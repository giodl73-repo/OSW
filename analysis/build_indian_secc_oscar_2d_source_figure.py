"""Independent monthly geographic source maps, not a current footprint."""
import calendar,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from build_indian_secc_oscar_2d_source import ROOT,REPORT,build,digest

OPERATOR='analysis/build_indian_secc_oscar_2d_source_figure.py'
MANIFEST='research/indian-secc-oscar-2d-source-figure.json'
STEM='figures/indian-secc-oscar-2d-source'

def main():
    d=json.loads((ROOT/REPORT).read_bytes())
    if d!=build():raise ValueError('Changed source report')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-indian-secc-source-v1'})
    fig,axes=plt.subplots(6,2,figsize=(18,14));fig.subplots_adjust(left=.055,right=.98,top=.90,bottom=.17,hspace=.6,wspace=.14)
    fig.suptitle('Indian Ocean SECC investigation · surrounding OSCAR source fields',x=.055,y=.98,ha='left',fontsize=19)
    fig.text(.055,.95,'2013 paired-vector monthly means · 50–90°E / 2°N–10°S · nominal 15 m · at least five finite pairs per cell',fontsize=12)
    lon,lat=np.meshgrid(d['longitude_degrees_east'],d['latitude_degrees_north']);stride=(slice(None,None,2),slice(None,None,4))
    cmap=plt.colormaps['RdBu_r'].copy();cmap.set_bad('#d7dadd')
    for ax,f in zip(axes.flat,d['months']):
        u=np.array(f['eastward_m_s'],dtype=float);v=np.array(f['northward_m_s'],dtype=float)
        image=ax.pcolormesh(lon,lat,u,cmap=cmap,norm=Normalize(-.4,.4),shading='nearest',rasterized=True)
        q=ax.quiver(lon[stride],lat[stride],u[stride],v[stride],angles='uv',scale_units='inches',scale=4,color='#162b35',width=.0023)
        for x in d['comparison_longitudes_degrees_east']:ax.axvline(x,color='#2b3134',linewidth=.7,linestyle='--')
        if f['month']==1:ax.quiverkey(q,.75,1.32,.2,'0.2 m/s',labelpos='E',coordinates='axes',fontproperties={'size':9})
        ax.set_xlim(50,90);ax.set_ylim(-10,2);ax.set_aspect('equal')
        ax.set_xticks([50,60,70,80,90]);ax.set_yticks([-10,-6,-2,2]);ax.tick_params(labelsize=8)
        ax.set_title(f"{calendar.month_name[f['month']]} · {f['available_source_times']} source times · {f['eligible_mean_cells']}/4477 cells · {f['outside_fixed_color_scale_cells']} clipped",loc='left',fontsize=10,pad=5)
    cax=fig.add_axes([.27,.092,.46,.014]);fig.colorbar(image,cax=cax,orientation='horizontal',extend='both')
    fig.text(.5,.116,'Monthly mean eastward component (m/s) · fixed shared scale; extremes clipped',ha='center',fontsize=11)
    fig.text(.055,.059,'Dashed: existing 80⅓E/80⅔E slices. Gray: insufficient paired support (none here). Arrows: east/north; display stride 4 columns / 2 rows.',fontsize=10)
    fig.text(.055,.037,'Equirectangular degree viewport, not equal-distance measurements. No named-current axis, edges, length, width or physical seasonal range.',fontsize=10)
    fig.text(.055,.015,'Source: OSCAR 2017.0 / Earth & Space Research / NOAA OceanWatch. Original numerical responses retained with exact hashes and source license.',fontsize=9)
    assets={}
    for suffix in ['svg','png']:
        path=STEM+'.'+suffix;metadata={'Date':None,'Creator':'OSW'} if suffix=='svg' else {'Software':'OSW'}
        fig.savefig(ROOT/path,dpi=140,metadata=metadata,facecolor='white');assets[suffix]={'file':path,'sha256':digest(path),'bytes':(ROOT/path).stat().st_size}
    plt.close(fig)
    m={'schema':'osw.indian-secc-oscar-2d-source-figure.v1','source_file':REPORT,'source_sha256':digest(REPORT),
        'generator_file':OPERATOR,'generator_sha256':digest(OPERATOR),'figures':assets,
        'alt':'Twelve2013 monthly maps of surrounding Indian Ocean source velocities, with a common signed eastward-component color scale, east/north vectors and two existing comparison meridians. Viewport and monthly patterns do not establish named-current edges or dimensions.',
        'current_geometry_admitted':False,'source_image_redistributed':False}
    (ROOT/MANIFEST).write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(json.dumps(assets))

if __name__=='__main__':main()
