"""All twelve model-grid contexts, retaining source support and thresholds."""
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np

import build_south_australian_flow_context as context

ROOT=context.ROOT
GENERATOR='analysis/build_south_australian_flow_context_figure.py'
STEM='figures/south-australian-hycom-2d-flow-context'
RECEIPT='research/south-australian-hycom-2d-flow-context-figure.json'


def build():
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-sac-flow-context-v1'})
    saved=json.loads((ROOT/context.OUTPUT).read_bytes())
    if context.build()!=saved:raise ValueError('Flow-context report differs from current inputs')
    _,arrays,_=context.verify()
    original=json.loads((ROOT/context.ORIGINAL).read_bytes())
    lon,lat=np.meshgrid(arrays['lon'],arrays['lat'])
    fig,axes=plt.subplots(3,4,figsize=(15,16),layout='constrained')
    fig.get_layout_engine().set(rect=(0,.10,1,.90))
    colors=['#c5ccd3','#fafafa','#ffdb9c','#f4a340','#b54b09']
    cmap=ListedColormap(colors);norm=BoundaryNorm(np.arange(6)-.5,cmap.N)
    for ax,month,old in zip(axes.flat,saved['months'],original['months']):
        u,v,counts,supported=context.monthly_vectors(arrays,month['source_indices'],month['minimum_required_pairs'])
        classes=supported.astype(int)
        for level,case in enumerate(month['threshold_cases'],2):
            for y,x in case['cells']:classes[y,x]=level
        ax.pcolormesh(lon,lat,classes,cmap=cmap,norm=norm,shading='nearest',rasterized=True)
        speed=np.hypot(u,v);nonzero=supported&(speed>0)
        east=np.divide(u,speed,out=np.zeros_like(speed),where=nonzero)/np.cos(np.deg2rad(lat))
        north=np.divide(v,speed,out=np.zeros_like(speed),where=nonzero)
        sample=(slice(None,None,4),slice(None,None,4))
        ax.quiver(lon[sample],lat[sample],np.ma.masked_where(~nonzero,east)[sample],
                  np.ma.masked_where(~nonzero,north)[sample],angles='xy',scale_units='xy',scale=5,
                  width=.003,color='#334553',pivot='mid')
        ax.axvline(132,color='#51606c',linewidth=.65,linestyle='--')
        lo=old['nominal']['boundaries']['low_coordinate']['coordinate']
        hi=old['nominal']['boundaries']['high_coordinate']['coordinate']
        ax.plot([132,132],[lo,hi],color='#9d1976',linewidth=2.2)
        seed=month['seed'];ax.plot(seed['longitude'],seed['latitude'],'*',color='white',
                                markeredgecolor='black',markersize=9)
        half=month['threshold_cases'][1]
        sides=', '.join(half['touched_box_sides']) or 'none'
        ax.set_title(f"2012-{month['month']:02d} · seed angle {seed['angle_degrees_north_of_east']:+.1f}°\n"
                     f"50%: {half['cell_count']} cells; box sides: {sides}",fontsize=9)
        ax.set(xlim=(130,134),ylim=(-38,-32),xlabel='Longitude °E',ylabel='Latitude °N')
        ax.set_aspect(1/np.cos(np.deg2rad(-35)));ax.tick_params(labelsize=8)
    legend=[Patch(facecolor=color,label=label) for color,label in zip(colors,[
        'Unsupported (<80% paired days)','Supported, outside seed components',
        '40% seed-connected cells','50% seed-connected cells','60% seed-connected cells'])]
    legend.extend([Line2D([],[],color='#9d1976',linewidth=2,label='Existing 132°E half-peak span'),
                   Line2D([],[],marker='*',color='white',markeredgecolor='black',linestyle='',label='Original selected seed')])
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.005),ncol=3,fontsize=9)
    fig.suptitle('South Australian investigation · monthly model-grid flow context\n'
                 'GOFS 3.0 HYCOM+NCODA, 100 m, 2012; complete-pair means, four-neighbor threshold connectivity',fontsize=14)
    fig.text(.5,.073,'Thresholds are fractions of each original 132°E eastward-component peak; nested colors show source-cell membership, not current boundaries.\n'
                  'Arrows show mean direction every fourth cell; angles are north of east. Longitude/latitude axes, aspect at 35°S.\n'
                  'Missing support is not land. Box contact is not named-current continuity. No physical width, trajectory or annual extrema inferred.',fontsize=9,ha='center',va='center')
    paths=[]
    for extension in ['png','svg']:
        path=ROOT/(STEM+'.'+extension);fig.savefig(path,dpi=160,metadata={'Date':None} if extension=='svg' else {})
        if extension=='svg':
            ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(path);svg=tree.getroot()
            svg.set('role','img');svg.set('aria-labelledby','sac-context-title sac-context-desc')
            title=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'sac-context-title'});title.text='South Australian investigation: all twelve monthly model-grid contexts'
            desc=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'sac-context-desc'})
            desc.text='Twelve 2012 monthly paired-vector means at 100 m, at least 80 percent paired daily support per cell. Nested colors show four-neighbor components connected to the original 132 E seed at 40, 50 and 60 percent of that seed eastward peak. Gray is unsupported source data, white is supported outside these components, stars are original seeds, magenta marks unchanged section spans. Arrows show direction. These are grid-context diagnostics, not named-current identity or physical widths. Exact membership, support and directions are in south-australian-hycom-2d-flow-context.json.'
            svg.insert(0,title);svg.insert(1,desc);tree.write(path,encoding='utf8',xml_declaration=True)
        paths.append(path)
    plt.close(fig)
    receipt={'schema':'osw.south-australian-hycom-2d-flow-context-figure.v1',
             'generator_file':GENERATOR,'generator_sha256':context.sha(ROOT/GENERATOR),
             'context_file':context.OUTPUT,'context_sha256':context.sha(ROOT/context.OUTPUT),
             'months':12,'threshold_cases':36,'current_association_verified':False,
             'width_measurement_admitted':False,'figures':{p.relative_to(ROOT).as_posix():context.sha(p) for p in paths}}
    (ROOT/RECEIPT).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__=='__main__':print(json.dumps(build(),indent=2))
