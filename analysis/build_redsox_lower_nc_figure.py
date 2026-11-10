"""Static scientific figure: layer/quality distinctions survive without color."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[1]
matplotlib.rcParams['svg.hashsalt']='osw-redsox-lower-nc-section-v1'


def main():
    data=json.loads((ROOT/'research/redsox-lower-nc-dated-section-diagnostic.json').read_bytes())
    fig,axes=plt.subplots(2,2,figsize=(12.8,8.2),layout='constrained');g=Geod(ellps='WGS84')
    for column,campaign in enumerate(['RSX1','RSX2']):
        cases=[c for c in data['cases'] if c['campaign']==campaign and c['height_layer_m'] in [[20,60],[40,80]]]
        reference=min(cases[0]['profiles'],key=lambda p:p['position_lon_lat'][0])['position_lon_lat']
        for case,color,marker,style in zip(cases,['#00747c','#ac500c'],['o','s'],['-','--']):
            p=sorted(case['profiles'],key=lambda p:p['position_lon_lat'][0])
            x=[g.inv(*reference,*r['position_lon_lat'])[2]/1000 for r in p]
            label='–'.join(map(str,case['height_layer_m']))+' m above bottom'
            y=[r['layer']['southward_m_s'] if r['layer'] and r['primary_available'] else np.nan for r in p]
            axes[0,column].plot(x,y,color=color,marker=marker,linestyle=style,label=label)
            salt=[(r.get('hydrography') or {}).get('layer_mean_salinity_psu',np.nan) for r in p]
            axes[1,column].plot(x,salt,color=color,marker=marker,linestyle=style,label=label)
            for xx,r in zip(x,p):
                if r['layer'] and not r['primary_available']:
                    axes[0,column].plot(xx,r['layer']['southward_m_s'],marker='x',color=color,markersize=8)
            if campaign=='RSX1' and case['height_layer_m']==[40,80]:
                span=case['supported_local_core_diagnostics'][0]
                edge_x=[g.inv(*reference,*span[side]['position_lon_lat'])[2]/1000 for side in ['left_edge','right_edge']]
                axes[0,column].hlines(span['threshold_m_s'],*edge_x,color=color,linewidth=3)
                axes[0,column].vlines(edge_x,-.18,span['threshold_m_s'],color=color,linestyle=':',linewidth=1)
        axes[0,column].axhline(.2,color='#6d7880',linewidth=.8,linestyle=':',label='0.2 m/s peak screening floor')
        axes[1,column].axhline(38,color='#6d7880',linewidth=.8,linestyle=':',label='38 psu plume screening context')
        axes[0,column].axhline(0,color='#6d7880',linewidth=.6)
        for row in [0,1]:
            axes[row,column].set(xlim=(-.6,15.6),xlabel='Distance east from western cast (km; WGS84 assumption)')
            axes[row,column].grid(alpha=.18);axes[row,column].legend(fontsize=8,loc='best')
        axes[0,column].set(ylabel='Layer-mean southward component (m/s)',ylim=(-.2,.6))
        axes[1,column].set(ylabel='Layer-mean practical salinity (source psu)',ylim=(36.3,39.7))
    axes[0,0].set_title('18 February 2001: supported local-core follow-up ≈6 km\n40–80 m layer only; primary 20–60 m result unresolved',fontsize=11)
    axes[0,1].set_title('24 August 2001: comparable span unresolved\nMissing western layer/reference support; no zero-width inference',fontsize=11)
    axes[0,1].annotate('Cast34 lacks the selected layer',xy=(0,.93),xycoords=('data','axes fraction'),fontsize=8,ha='left')
    fig.suptitle('Red Sea lower Northern Channel: direct observations and unresolved edges\nTwo non-synoptic surveys; flow/salinity screening does not confirm current identity',fontsize=13)
    fig.supxlabel('Crosses: distributed winter cast10 values, excluded for unresolved component-quality treatment. Velocity lines do not bridge unavailable profiles.\n'
        '≈6 km is a fixed-component local section span, only1.67 station spacings; 40% threshold remains unresolved.\n'
        '10–50 m layer lacks near-bottom support. No whole-current width, annual range, physical footprint or scientific width admission.',fontsize=9)
    target=ROOT/'figures/redsox-lower-nc-section-diagnostic.svg'
    fig.savefig(target,metadata={'Date':None});fig.savefig(ROOT/'figures/redsox-lower-nc-section-diagnostic.png',dpi=150)
    tree=ET.parse(target);root=tree.getroot();ET.register_namespace('','http://www.w3.org/2000/svg')
    root.set('role','img');root.set('aria-labelledby','nc-title nc-description')
    title=ET.Element('{http://www.w3.org/2000/svg}title',id='nc-title');title.text='Red Sea winter and summer local section feasibility'
    desc=ET.Element('{http://www.w3.org/2000/svg}desc',id='nc-description')
    desc.text=('Winter40–80m-above-bottom observations support a local half-peak southward component span near6km using casts7,8,9. '
        'The primary20–60m layer needs quality-questioned cast10 and remains unresolved. '
        'Summer lacks comparable usable support. Circles/solid lines identify20–60m, squares/dashed lines40–80m. '
        'Salinity panels show independent water-property context. Neither a physical full-current width nor an annual range is admitted. '
        'All scenarios, missing profiles and numerical values are available in the companion JSON and plan.')
    root.insert(0,title);root.insert(1,desc);tree.write(target,encoding='utf-8',xml_declaration=True)
    target.write_bytes(b'\n'.join(line.rstrip() for line in target.read_bytes().splitlines())+b'\n')


if __name__=='__main__':main()
