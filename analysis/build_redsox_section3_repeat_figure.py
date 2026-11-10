"""Two dated source sections; no interpolation through time or failed casts."""
from xml.etree import ElementTree as ET
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_redsox_section3_repeat import ROOT, REPORT, build, digest, encoded, winter

MANIFEST='research/redsox-section3-repeat-figure.json'
matplotlib.rcParams['svg.hashsalt']='osw-redsox-section3-repeat-v1'


def main():
    repeat=build()
    if encoded(repeat)!=(ROOT/REPORT).read_bytes():raise ValueError('Stale repeat-survey data')
    old=json.loads((ROOT/winter.REPORT).read_bytes())
    fig,axes=plt.subplots(2,2,figsize=(13.6,8.8),layout='constrained')
    columns=[old['layers'],repeat['summer_layers']]
    max_x=math.ceil(max(p['chainage_km'] for layers in columns for p in layers[0]['profiles']))+1
    q_values=[p['normal_component_m_s'] for layers in columns for layer in layers
        for p in layer['profiles'] if p['normal_component_m_s'] is not None]
    q_limits=(math.floor(min(q_values)*10)/10-.02,math.ceil(max(q_values)*10)/10+.02)
    for col,layers in enumerate(columns):
        excluded_label=False
        for layer,color,marker,style in zip(layers,['#00747c','#777777','#ae520c'],['o','^','s'],['-',':','--']):
            label='–'.join(map(str,layer['height_layer_m']))+' m above bottom'
            p=layer['profiles'];x=[v['chainage_km'] for v in p]
            q=[v['normal_component_m_s'] if v['usable'] else np.nan for v in p]
            s=[(v['hydrography'] or {}).get('layer_mean_salinity_psu',np.nan) for v in p]
            axes[0,col].plot(x,q,color=color,marker=marker,linestyle=style,label=label,markersize=4)
            axes[1,col].plot(x,s,color=color,marker=marker,linestyle=style,label=label,markersize=4)
            for v in p:
                if v['layer'] and not v['usable']:
                    axes[0,col].plot(v['chainage_km'],v['normal_component_m_s'],marker='x',color=color,
                        markersize=8,linestyle='none',label='Excluded reference/processing' if not excluded_label else None)
                    excluded_label=True
            for case in layer['cases']:
                if case['fraction']==.5 and case['uniform_component_offset_m_s']==0 and case['span_km'] is not None:
                    edges=[case[key]['chainage_km'] for key in ['left_edge','right_edge']]
                    axes[0,col].hlines(case['threshold_m_s'],*edges,color=color,linewidth=3,
                        linestyles='solid' if case['saline_outflow_screen'] else 'dotted')
        axes[0,col].axhline(0,color='#57636c',linewidth=.6)
        axes[0,col].axhline(.2,color='#57636c',linewidth=.8,linestyle=':',label='0.2 m/s peak screen')
        axes[1,col].axhline(38,color='#57636c',linewidth=.8,linestyle=':',label='Unchanged 38 psu screen')
        for row in range(2):
            axes[row,col].set_xlim(-.8,max_x)
            axes[row,col].set_xlabel('WGS84 chainage along each observed section (km)')
            axes[row,col].grid(alpha=.16)
            if row==1:axes[row,col].legend(fontsize=8,loc='best')
            elif col==1:axes[row,col].legend(fontsize=8,loc='upper left')
        axes[0,col].set_ylabel('Local section-normal component (m/s)')
        axes[1,col].set_ylabel('Layer-mean practical salinity (source psu)')
        axes[0,col].set_ylim(*q_limits)
        axes[1,col].set_ylim(35.4,39.7)
    axes[0,0].set_title('22–23 February 2001: southern ≈5.0 / 5.5 km\n20–60 / 40–80 m; northern branch unresolved',fontsize=11)
    axes[0,1].set_title('23 August 2001: northern component candidate ≈3.1 km\n20–60 m; saline screen fails, southern branch unresolved',fontsize=11)
    axes[1,0].set_title('Winter same-cast hydrography; cast 74 missing',fontsize=11)
    axes[1,1].set_title('Summer candidate peak: ≈37.41 psu, below 38 psu screen',fontsize=11)
    fig.suptitle('Red Sea outflow Section 3: two dated observed surveys\nNo supported same-branch width difference or annual range',fontsize=13)
    fig.supxlabel('Lines stop at excluded or missing velocities; crosses show retained excluded layer values. Profiles are not interpolated across time.\n'
        'Summer cast 22 has unresolved bad-upcast treatment. A −0.04 m/s offset puts the northern candidate below the speed floor.\n'
        'Local component spans along a bent section are not verified physical current widths. Tides remain; two surveys are not a seasonal climatology.',fontsize=9)
    assets={}
    for suffix in ['svg','png']:
        path='figures/redsox-section3-repeat-surveys.'+suffix
        fig.savefig(ROOT/path,metadata={'Date':None} if suffix=='svg' else {},**({'dpi':150} if suffix=='png' else {}))
        if suffix=='svg':
            tree=ET.parse(ROOT/path);root=tree.getroot();ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
            root.set('role','img');root.set('aria-labelledby','repeat-title repeat-description')
            title=ET.Element('{'+ns+'}title',id='repeat-title');title.text='REDSOX repeated Section 3: two dated velocity and salinity surveys'
            desc=ET.Element('{'+ns+'}desc',id='repeat-description');desc.text=('Winter southern component spans about 5.0 and 5.5 km in two layers. Summer northern component candidate about 3.1 km at 20–60 m above bottom fails the unchanged 38 psu screen; a negative velocity-offset case fails the speed floor. Summer southern peak search is blocked by cast22 quality uncertainty. Northern winter support remains incomplete. All six same-branch dated width comparisons are unresolved; no annual width range or physical current width is admitted.')
            root.insert(0,title);root.insert(1,desc);tree.write(ROOT/path,encoding='utf8',xml_declaration=True)
            (ROOT/path).write_bytes(b'\n'.join(line.rstrip() for line in (ROOT/path).read_bytes().splitlines())+b'\n')
        assets[suffix]={'file':path,'sha256':digest(path),'bytes':(ROOT/path).stat().st_size}
    plt.close(fig)
    manifest={'schema':'osw.redsox-section3-repeat-figure.v1','source_file':REPORT,'source_sha256':digest(REPORT),
        'winter_file':winter.REPORT,'winter_sha256':digest(winter.REPORT),
        'generator_file':'analysis/build_redsox_section3_repeat_figure.py',
        'generator_sha256':digest('analysis/build_redsox_section3_repeat_figure.py'),
        'physical_width_admitted':False,'seasonal_climatology':False,'figures':assets}
    (ROOT/MANIFEST).write_bytes(encoded(manifest))


if __name__=='__main__':main()
