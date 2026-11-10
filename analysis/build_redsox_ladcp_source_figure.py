"""Plot observed cast locations, never a current footprint or axis."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch,Rectangle

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'research/redsox-ladcp-source-inventory.json'
matplotlib.rcParams['svg.hashsalt']='osw-redsox-source-support-v1'


def coastline():
    svg=ET.parse(ROOT/'figures/ocean-motion-closeup-ground.svg').getroot()
    source=next(e.get('d') for e in svg if e.tag.endswith('path'))
    # Existing OSW coastline uses only absolute M/L/Z commands.
    if re.sub(r'[MLZ0-9.,\s-]','',source):raise ValueError('Changed OSW coastline path grammar')
    tokens=re.findall(r'[MLZ]|-?\d+(?:\.\d+)?',source)
    vertices=[];codes=[];i=0;start=None
    while i<len(tokens):
        command=tokens[i];i+=1
        if command=='Z':vertices.append(start);codes.append(PlotPath.CLOSEPOLY);continue
        x,y=map(float,tokens[i:i+2]);i+=2
        point=((x-60)/1480*360-180,90-(y-90)/740*180)
        if command=='M':start=point;code=PlotPath.MOVETO
        elif command=='L':code=PlotPath.LINETO
        else:raise ValueError('Unsupported coastline instruction')
        vertices.append(point);codes.append(code)
    return PlotPath(vertices,codes)


def main():
    data=json.loads(DATA.read_bytes());records=data['profiles']
    fig,axes=plt.subplots(2,2,figsize=(12.8,10.6),layout='constrained')
    detail=(43.1,44.5,11.8,12.9)
    for flat,ax in enumerate(axes.flat):
        row,index=divmod(flat,2)
        campaign,color=[('RSX1','#006a78'),('RSX2','#a95310')][row]
        if index==0:
            ax.add_patch(PathPatch(coastline(),facecolor='#e3e7e9',edgecolor='#8a969c',linewidth=.6))
        markers={'RSX1':[('nav','o'),('hr','^')],'RSX2':[('nav','s'),('hr','D')]}
        for family,marker in markers[campaign]:
            selected=[r for r in records if r['campaign']==campaign and r['file_reference_family']==family]
            ax.scatter([r['position_lon_lat'][0] for r in selected],[r['position_lon_lat'][1] for r in selected],
                color=color,marker=marker,s=20 if index==0 else 31,alpha=.72,
                linewidth=.3,edgecolor='white',label=f'{campaign} / {family} ({len(selected)})',zorder=3)
        if index==0:
            count=sum(r['campaign']==campaign for r in records)
            ax.set(xlim=(42,53.5),ylim=(4.8,16.5),title=f'{campaign}: all {count} distributed profiles')
            ax.add_patch(Rectangle((detail[0],detail[2]),detail[1]-detail[0],detail[3]-detail[2],
                fill=False,edgecolor='#505b62',linestyle='--',linewidth=1.2,zorder=4))
            ax.legend(fontsize=8,loc='lower left',title='Cruise / source reference family',title_fontsize=9)
        else:
            ax.set(xlim=detail[:2],ylim=detail[2:],title=f'{campaign}: near-field position detail')
        ax.set(xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)')
        ax.grid(alpha=.2)
    fig.suptitle('Red Sea outflow: direct-current survey sampling support\nNCEI accession 0146147 v1.2 / REDSOX 2001',fontsize=14)
    fig.supxlabel('RSX1: 14 Feb–11 Mar; RSX2: 21 Aug–10 Sep (distributed profile dates, not complete cruise dates).\n'
        'nav = navigation reference; hr = bottom-tracking family. Symbols identify each cruise/reference combination.\n'
        'Positions are observations, not plume membership or current boundaries. 310 nquan conflicts and 15 unclear reference headers remain.\n'
        'Overview: coarse OSW coastline and longitude/latitude display; unsuitable for coastal measurement. Detail panels omit coastline. No width admitted.',fontsize=9)
    target=ROOT/'figures/redsox-ladcp-source-support.svg'
    fig.savefig(target,metadata={'Date':None})
    fig.savefig(ROOT/'figures/redsox-ladcp-source-support.png',dpi=150)
    tree=ET.parse(target);root=tree.getroot();ET.register_namespace('','http://www.w3.org/2000/svg')
    root.set('role','img');root.set('aria-labelledby','redsox-title redsox-description')
    title=ET.Element('{http://www.w3.org/2000/svg}title',id='redsox-title')
    title.text='Locations of445 archived REDSOX current profiles in2001'
    desc=ET.Element('{http://www.w3.org/2000/svg}desc',id='redsox-description')
    desc.text=('Overview and near-field position detail for222 winter and223 summer profiles. '
        'Circles/triangles denote winter navigation/bottom reference; squares/diamonds denote summer navigation/bottom reference. '
        'The archive includes transit and far-field positions; not every point is a descending Red Sea plume. '
        'A dashed rectangle identifies the detail window, not a current extent. '
        'There are310 quantity-count conflicts and15 unclear reference headers. '
        'Current widths remain unknown. Complete coordinates, source times and per-profile issues appear in the companion JSON and plan.')
    root.insert(0,title);root.insert(1,desc);tree.write(target,encoding='utf-8',xml_declaration=True)
    target.write_bytes(b'\n'.join(line.rstrip() for line in target.read_bytes().splitlines())+b'\n')


if __name__=='__main__':main()
