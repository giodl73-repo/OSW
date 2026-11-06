"""Original data figure, with missing profiles and failed layers visible."""
import json
from xml.etree import ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from build_redsox_section3_spans import ROOT, REPORT, build, encoded, digest

MANIFEST = 'research/redsox-winter-section3-figure.json'
matplotlib.rcParams['svg.hashsalt'] = 'osw-redsox-section3-v1'


def main():
    data = build()
    if encoded(data) != (ROOT/REPORT).read_bytes():
        raise ValueError('Stale Section 3 calculation')
    fig, axes = plt.subplots(2,2,figsize=(13.5,9),layout='constrained')
    first = data['layers'][0]
    p = first['profiles']
    ax = axes[0,0]
    ax.plot([v['position_lon_lat'][0] for v in p], [v['position_lon_lat'][1] for v in p],
            color='#596974', marker='o', markersize=4)
    for v in p:
        x,y = v['position_lon_lat']
        ax.annotate(str(v['station']), (x,y), xytext=(5,4), textcoords='offset points', fontsize=8)
        if not v['usable']:
            ax.plot(x,y,'x',color='#ab3d24',markersize=9)
    ax.set(xlabel='Longitude (degrees east)', ylabel='Latitude (degrees north)',
           title='Source Figure 7(a) order: 12 casts, 22–23 February 2001')
    ax.set_aspect(1/np.cos(np.deg2rad(12.3)))
    ax.margins(.15)
    for layer, color, marker, style in zip(data['layers'], ['#00747c','#777777','#ae520c'], ['o','^','s'], ['-',':','--']):
        profiles = layer['profiles']
        x = [v['chainage_km'] for v in profiles]
        label = '–'.join(map(str,layer['height_layer_m']))+' m above bottom'
        y = [v['normal_component_m_s'] if v['usable'] else np.nan for v in profiles]
        salt = [(v['hydrography'] or {}).get('layer_mean_salinity_psu',np.nan) for v in profiles]
        axes[0,1].plot(x,y,color=color,marker=marker,linestyle=style,label=label,markersize=4)
        axes[1,0].plot(x,salt,color=color,marker=marker,linestyle=style,label=label,markersize=4)
        primary = layer['cases'][0]
        if primary['span_km'] is not None:
            edges = [primary[key]['chainage_km'] for key in ['left_edge','right_edge']]
            axes[0,1].hlines(primary['threshold_m_s'],*edges,color=color,linewidth=3)
        for case in layer['cases'][:5]:
            index = layer['cases'].index(case)
            if case['span_km'] is not None:
                axes[1,1].plot(index,case['span_km'],color=color,marker=marker,markersize=7)
    axes[0,1].axhline(0,color='#58636b',linewidth=.7)
    axes[0,1].axhline(.2,color='#58636b',linestyle=':',linewidth=.8)
    axes[0,1].set(ylabel='Local section-normal component (m/s)',title='Southern primary local span ≈5.0 km; northern unresolved')
    axes[1,0].axhline(38,color='#58636b',linestyle=':',linewidth=.8)
    axes[1,0].set(ylabel='Layer-mean practical salinity (source psu)',title='Same-cast hydrography; station 74 missing')
    for ax in [axes[0,1], axes[1,0]]:
        ax.set_xlabel('WGS84 chainage from station 76 along the bent section (km)')
        ax.legend(fontsize=8,loc='best')
        for v in p:
            ax.axvline(v['chainage_km'],color='#88949d',alpha=.15,linewidth=.5)
    axes[1,1].set(xticks=range(5),xticklabels=['50%','40%','60%','50%\n−0.03 m/s','50%\n+0.03 m/s'],
        ylabel='Southern section span (km)',ylim=(3.5,16),title='Fixed scenarios: layer and threshold dependence')
    axes[1,1].text(.03,.96,'10–50 m: all cases lack complete layer support\nNorthern branch: all 15 cases unresolved',
        transform=axes[1,1].transAxes,va='top',fontsize=9)
    for ax in axes.flat:
        ax.grid(alpha=.15)
    fig.suptitle('Red Sea outflow: an independent winter observed section\nDated local component spans; physical whole-current width and annual range remain unknown',fontsize=13)
    fig.supxlabel('20–60 m: ≈5.0 km; 40–80 m: ≈5.5 km. Sparse stations; neither is a verified flow-normal current width.\n'
        'Casts 61/63 excluded for unresolved reference/processing. Lines stop at missing values. Tides are not removed.\n'
        '40–60% thresholds and uniform ±0.03 m/s offsets are finite sensitivity scenarios, not confidence bounds or annual margins.',fontsize=9)
    assets={}
    for suffix in ['svg','png']:
        path='figures/redsox-winter-section3-component-spans.'+suffix
        fig.savefig(ROOT/path,metadata={'Date':None} if suffix=='svg' else {},**({'dpi':150} if suffix=='png' else {}))
        if suffix=='svg':
            tree=ET.parse(ROOT/path);root=tree.getroot();ns='http://www.w3.org/2000/svg'
            ET.register_namespace('',ns);root.set('role','img');root.set('aria-labelledby','section3-title section3-desc')
            title=ET.Element('{'+ns+'}title',id='section3-title');title.text='REDSOX winter Section 3 observed component spans'
            desc=ET.Element('{'+ns+'}desc',id='section3-desc');desc.text=('Twelve source-ordered stations on 22–23 February 2001. Southern half-peak local component spans are about 5.0 km at 20–60 m above bottom and 5.5 km at 40–80 m. The 40 percent threshold in the deeper layer extends to 12.6 km. Northern outcomes and all 10–50 m cases are unresolved. Missing casts, salinity support and all finite sensitivities are retained. These are not physical whole-current widths or annual ranges.')
            root.insert(0,title);root.insert(1,desc);tree.write(ROOT/path,encoding='utf8',xml_declaration=True)
            (ROOT/path).write_bytes(b'\n'.join(line.rstrip() for line in (ROOT/path).read_bytes().splitlines())+b'\n')
        assets[suffix]={'file':path,'sha256':digest(path),'bytes':(ROOT/path).stat().st_size}
    plt.close(fig)
    manifest={'schema':'osw.redsox-section3-figure.v1','source_file':REPORT,'source_sha256':digest(REPORT),
        'generator_file':'analysis/build_redsox_section3_figure.py','generator_sha256':digest('analysis/build_redsox_section3_figure.py'),
        'physical_width_admitted':False,'figures':assets}
    (ROOT/MANIFEST).write_bytes(encoded(manifest))


if __name__=='__main__':
    main()
