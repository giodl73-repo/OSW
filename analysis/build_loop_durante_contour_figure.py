"""Plot all fixed contour levels/gateway shifts without implying annual ranges."""
import json,math
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from acquire_loop_durante_2026 import ROOT,verify as verify_source,sha,write
from loop_durante_composite_contours import build,OUTPUT,LEVELS

GENERATOR='analysis/build_loop_durante_contour_figure.py'
REPORT='research/loop-durante-2026-composite-contour-figure.json'
STEM='figures/loop-durante-2026-composite-contours'


def figure():
    data=build()
    if data!=json.loads((ROOT/OUTPUT).read_bytes()):raise ValueError('Stale composite contour report')
    _,_,arrays=verify_source();x,y=arrays['xduf'],arrays['yduf']
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-loop-durante-contours-v1'})
    fig,axes=plt.subplots(2,3,figsize=(16,11),layout='constrained')
    fig.get_layout_engine().set(rect=(0,.10,1,.81))
    maximum=max(float(np.nanmax(arrays[n])) for n in ['Cmax','Cmin']);cmap=plt.colormaps['viridis'].copy();cmap.set_bad('#d5d9de')
    cases_drawn=[]
    for row,(phase,suffix) in enumerate([('Positive','max'),('Negative','min')]):
        for col,level in enumerate(LEVELS):
            ax=axes[row,col];group=[c for c in data['cases'] if c['phase']==phase and c['adt_level_m']==level]
            image=ax.pcolormesh(x,y,np.ma.masked_invalid(arrays['C'+suffix]),shading='nearest',cmap=cmap,vmin=0,vmax=maximum,rasterized=True)
            for c in sorted(group,key=lambda c:c['south_offset_degrees']==c['east_offset_degrees']==0):
                central=c['south_offset_degrees']==c['east_offset_degrees']==0
                cases_drawn.append(c['id'])
                for p in c['components']:
                    points=np.asarray(p['coordinates_lon_lat'])
                    if p['supported']:
                        if central:
                            ax.plot(points[:,0],points[:,1],color='white',lw=3)
                            ax.plot(points[:,0],points[:,1],color='#111111',lw=1.5)
                        else:ax.plot(points[:,0],points[:,1],color='white',lw=.65,alpha=.7)
                    elif central:
                        ax.plot(points[:,0],points[:,1],color='#b03040',lw=1,ls='--')
                south,east=c['gates']['entry_latitude'],c['gates']['exit_longitude']
                ax.plot([-86.875,-85.125],[south,south],color='#bb5d00',lw=1.5 if central else .5)
                ax.plot([east,east],[23,25],color='#bb5d00',lw=1.5 if central else .5)
            nominal=next(c for c in group if c['south_offset_degrees']==c['east_offset_degrees']==0)
            number=nominal['rounded_supported_contour_path_km']
            label=f'About {number:,} km' if number is not None else 'Unresolved'
            ax.set_title(f'{phase} composite · ADT {level:.2f} m\nCentral gates: {label}; {sum(c["status"]=="unique_supported_path" for c in group)}/9 supported cases',fontsize=11)
            ax.set(xlim=(-90,-80.9),ylim=(21.3,29.5),xlabel='Longitude °E',ylabel='Latitude °N')
            ax.set_aspect(1/math.cos(math.radians(25)));ax.grid(alpha=.15)
    colorbar=fig.colorbar(image,ax=axes,location='bottom',fraction=.045,shrink=.75,pad=.02)
    colorbar.set_label('Original author composite speed (m/s); common scale; gray = missing source values, not coastline')
    fig.suptitle('Loop Current · measured composite contour paths\nFixed author guide 0.55 m, neighbouring levels and all gateway shifts; not dated or seasonal current lengths',fontsize=16)
    handles=[Line2D([],[],color='#111',lw=2,label='Central-gate supported contour'),Line2D([],[],color='#888',lw=.8,label='Other gateway shifts (white on maps)'),
             Line2D([],[],color='#b03040',ls='--',label='Rejected components at central gates'),Line2D([],[],color='#bb5d00',label='Editorial gates and shifts')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.93),ncol=4,fontsize=9)
    fig.text(.5,.052,'54/54 declared cases have one supported open contour arc. Disconnected closed rings remain rejected; none is appended.\n'
             'WGS84 distances use retained vertices. Support requires complete velocity sampling, forward flow and coarse OSW land clearance.\n'
             '0.50–0.60 m and ±0.125° gate shifts are editorial sensitivity, not confidence, annual extrema or effective-resolution error.\n'
             'Durante2026, Zenodo10.5281/zenodo.22652650 v0; author-processed surface composites. No ranked length, physical width or footprint admission.',
             ha='center',va='center',fontsize=9)
    assets={}
    for extension in ['png','svg']:
        path=ROOT/(STEM+'.'+extension);fig.savefig(path,dpi=160,metadata={'Date':None} if extension=='svg' else {})
        if extension=='svg':
            ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(path);svg=tree.getroot();svg.set('role','img');svg.set('aria-labelledby','loop-contour-title loop-contour-desc')
            title=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'loop-contour-title'});title.text='All54 Loop Current composite contour and gateway cases'
            desc=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'loop-contour-desc'});desc.text='Two rows show positive and negative surface composites; three columns show absolute ADT levels0.50,0.55,0.60m. Each panel retains all nine editorial gateway shifts. Black central-gate contours over white outlines, white sensitivity paths, dashed red rejected components and orange gateways. All54cases have one supported open arc. Nominal0.55m paths are about1400km positive and600km negative. These are geometry of conditional composites, not mean daily lengths, annual extrema, ranked whole-current lengths or physical widths. Exact paths, rejected components and every velocity sample are in the checked composite-contour report.'
            svg.insert(0,title);svg.insert(1,desc);tree.write(path,encoding='utf8',xml_declaration=True)
        assets[path.relative_to(ROOT).as_posix()]=sha(path)
    plt.close(fig)
    result={'schema':'osw.loop-durante-composite-contour-figure.v1','generator_file':GENERATOR,'generator_sha256':sha(ROOT/GENERATOR),
            'source_report_file':OUTPUT,'source_report_sha256':sha(ROOT/OUTPUT),'figures':assets,'all_drawn_case_ids':cases_drawn,
            'whole_current_length_admitted':False,'width_measurement_admitted':False,'annual_range_admitted':False}
    write(ROOT/REPORT,result);return result


if __name__=='__main__':print(json.dumps(figure(),indent=2))
