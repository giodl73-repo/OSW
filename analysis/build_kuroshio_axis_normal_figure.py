"""Standalone monthly ranges and actual model-normal sections; no ribbons."""
import io
import json
import math
import xml.etree.ElementTree as ET
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import shapefile
from shapely.geometry import box,shape
from shapely.geometry.polygon import orient

import kuroshio_axis_normal as k

ROOT=k.ROOT
OPERATOR='analysis/build_kuroshio_axis_normal_figure.py'
RECEIPT='research/kuroshio-wang-2024-axis-normal-figure.json'
COLORS=['#0072b2','#b34f00','#006f53','#884080','#454545']
MARKERS=['o','s','^','D','x']


def land_shapes():
    result=[]
    if k.base.digest(k.base.LAND)!='e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc':
        raise ValueError('Changed cartographic land source')
    with zipfile.ZipFile(ROOT/k.base.LAND) as archive:
        with shapefile.Reader(**{s:io.BytesIO(archive.read('ne_10m_land.'+s)) for s in ['shp','shx','dbf']}) as reader:
            for item in reader.iterShapes(bbox=(118,15,132,32)):
                clipped=shape(item.__geo_interface__).intersection(box(118,15,132,32)).simplify(.01,preserve_topology=True)
                if clipped.geom_type=='Polygon':result.append(clipped)
                elif clipped.geom_type=='MultiPolygon':result.extend(clipped.geoms)
    return result


def create_figure(doc):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none',
                         'svg.hashsalt':'osw-kuroshio-axis-normal-v1','axes.spines.top':False,'axes.spines.right':False})
    old=json.loads((ROOT/k.base.FILE).read_bytes());land=land_shapes()
    fig,axes=plt.subplots(2,3,figsize=(15,13),gridspec_kw={'height_ratios':[1,1.55]})
    fig.subplots_adjust(top=.84,bottom=.15,left=.06,right=.98,wspace=.24,hspace=.28)
    fig.suptitle('Kuroshio 2024 · model-axis-normal boundary spans',x=.06,y=.98,ha='left',fontsize=21,weight='bold')
    fig.text(.06,.948,'Primary tangent: ±14 km along the model axis. Three nominal depth levels; five fixed axis latitude gates.',fontsize=12)
    fig.text(.06,.925,'Bars: monthly min–max of available daily model values; markers: median. These are sample ranges, not error bars or climatology.',fontsize=10)
    fig.legend([Line2D([],[],color=c,marker=m,lw=1) for c,m in zip(COLORS,MARKERS)],
               [f'{lat:g}°N gate' for lat in k.base.SECTIONS],loc='upper left',bbox_to_anchor=(.055,.911),ncol=5,frameon=False)
    maximum=max(s['maximum_km'] for s in doc['summaries'] if s['tangent_half_window_km']==14 and s['maximum_km'] is not None)
    upper=math.ceil(maximum/50)*50
    when='2024-07-01'
    for col,(level,depth) in enumerate(k.base.LEVELS.items()):
        ax=axes[0,col]
        for index,(lat,color,marker) in enumerate(zip(k.base.SECTIONS,COLORS,MARKERS)):
            rows=[s for s in doc['summaries'] if s['source_level']==level and s['latitude']==lat
                  and s['tangent_half_window_km']==14 and s['month'] is not None]
            rows.sort(key=lambda s:s['month'])
            x=np.array([s['month'] for s in rows])+(index-2)*.13
            med=np.array([np.nan if s['median_km'] is None else s['median_km'] for s in rows])
            low=np.array([np.nan if s['minimum_km'] is None else s['minimum_km'] for s in rows])
            high=np.array([np.nan if s['maximum_km'] is None else s['maximum_km'] for s in rows])
            ax.vlines(x,low,high,color=color,lw=.8)
            ax.plot(x,med,color=color,marker=marker,ms=3,lw=.7)
        available=sum(r['status']=='resolved' for r in doc['cases'] if r['source_level']==level and r['tangent_half_window_km']==14)
        ax.set_title(f'{depth:g} m · {available:,}/1,830 resolved attempts',loc='left',fontsize=11)
        ax.set_xticks(range(1,13),list('JFMAMJJASOND'));ax.set_xlim(.4,12.6);ax.set_ylim(0,upper)
        ax.set_xlabel('2024 calendar month');ax.set_ylabel('Axis-normal span (km)');ax.grid(axis='y',alpha=.2)
        ax=axes[1,col];ax.set_facecolor('#e7f1f5')
        for polygon in land:
            polygon=orient(polygon,sign=1)
            rings=[Path(np.asarray(ring.coords),closed=True) for ring in [polygon.exterior,*polygon.interiors]]
            ax.add_patch(PathPatch(Path.make_compound_path(*rings),facecolor='#dddacd',edgecolor='#8b897f',lw=.35))
        frame=next(r for r in old['display_frames'] if r['date']==when and r['source_level']==level)
        for kind,color,style in [('axis','#153e75','-'),('left','#a03e9d','--'),('right','#008278',':')]:
            points=np.asarray([[np.nan,np.nan] if p is None else p for p in frame['curves_lon_lat'][kind]])
            ax.plot(points[:,0],points[:,1],color=color,ls=style,lw=1)
        previous=next(r for r in old['daily'] if r['date']==when and r['source_level']==level)
        for latitude,color,marker in zip(k.base.SECTIONS,COLORS,MARKERS):
            case=next(r for r in doc['cases'] if r['sample_date']==when and r['source_level']==level
                      and r['latitude']==latitude and r['tangent_half_window_km']==14)
            cut=next(r for r in previous['sections'] if r['latitude']==latitude)
            if cut['status']=='resolved':
                points=np.asarray(cut['section_lon_lat']);ax.plot(points[:,0],points[:,1],color='#777',ls='--',lw=.8,alpha=.7)
            if case['status']=='resolved':
                left,right=[case['edges'][name]['point'] for name in ('left','right')]
                points=np.asarray([left,*k.base.GEOD.npts(*left,*right,32),right])
                ax.plot(points[:,0],points[:,1],color=color,lw=1.6)
                gate=case['gate']['point'];ax.plot(*gate,marker=marker,ms=4,color=color)
                ax.annotate(f'{latitude:g}°N ≈{round(case["span_km"]/10)*10} km',gate,
                            xytext=(5,6),textcoords='offset points',fontsize=8,color=color)
            elif case['gate']:
                ax.plot(*case['gate']['point'],marker='x',color='#555',ms=5)
                ax.annotate(f'{latitude:g}°N unresolved',case['gate']['point'],xytext=(5,6),textcoords='offset points',fontsize=8)
        ax.set_xlim(118,132);ax.set_ylim(15,32);ax.set_aspect(1/math.cos(math.radians(24)))
        ax.set_title(f'{when} · {depth:g} m · dated snapshot',loc='left',fontsize=11)
        ax.set_xlabel('Longitude °E');ax.set_ylabel('Latitude °N');ax.grid(alpha=.16)
    fig.text(.06,.09,'Maps: coloured geodesic normals; grey dashed latitude cuts. Navy axis; purple dashed left edge; teal dotted right edge.',fontsize=10)
    fig.text(.06,.07,'Axis normal is a geometric convention, not a verified instantaneous velocity normal. Ocean connectivity is not established by these lines.',fontsize=10)
    fig.text(.06,.05,'Unflagged source fallback and 110 km smoothing remain. Tangent scales 7/14/28 km are method sensitivity; physical uncertainty stays unknown.',fontsize=10)
    fig.text(.06,.028,'Wang, Chen, Mao & Zhang (2026) · doi:10.1038/s41597-026-07275-3 · data:10.6084/m9.figshare.30267070.v1 · CC BY 4.0',fontsize=9)
    fig.text(.06,.01,'OSW derived geometry · WGS84 distances · equirectangular map display (24°N standard parallel) · Natural Earth land v5.1.1, public domain.',fontsize=9)
    return fig


def figure_bytes(doc):
    fig=create_figure(doc);buffer=io.BytesIO()
    fig.savefig(buffer,format='svg',metadata={'Date':None,'Creator':'OSW source-derived scientific figure'})
    plt.close(fig)
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    root=ET.fromstring(buffer.getvalue());root.set('role','img')
    root.set('aria-labelledby','normal-title');root.set('aria-describedby','normal-description')
    for text in root.iter('{'+ns+'}text'):
        text.set('style',text.get('style','').replace("font-family: 'DejaVu Sans'","font-family: 'DejaVu Sans', Arial, sans-serif"))
    title=ET.Element('{'+ns+'}title',{'id':'normal-title'});title.text='Kuroshio 2024: model-axis-normal spans, monthly sample ranges and dated section maps'
    desc=ET.Element('{'+ns+'}desc',{'id':'normal-description'});desc.text='Three depth levels. All primary attempts retained, including unresolved cases. Monthly markers are median and bars the available daily sample range. Dated July maps show independently intersected normals and separate latitude cuts. Source fallback, velocity normal and ocean connectivity are not verified; these are not physical uncertainty intervals or footprints.'
    root.insert(0,title);root.insert(1,desc)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)


if __name__=='__main__':
    doc=k.verify_inputs();(ROOT/k.FIGURE).write_bytes(figure_bytes(doc))
    paths=[k.FILE,k.PROTOCOL,OPERATOR,'requirements-test.txt',k.base.LAND,k.base.FILE]
    receipt={'schema':'osw.kuroshio-axis-normal-figure.v1','figure':k.FIGURE,
             'figure_sha256':k.base.digest(k.FIGURE),'input_sha256':{p:k.base.digest(p) for p in paths},
             'display_snapshot_date':'2024-07-01','display_tangent_half_window_km':14,
             'source_original_images_redistributed':False,'physical_inventory_admission':False}
    (ROOT/RECEIPT).write_bytes(k.encoded(receipt))
    print(json.dumps({'figure':k.FIGURE,'bytes':(ROOT/k.FIGURE).stat().st_size}))
