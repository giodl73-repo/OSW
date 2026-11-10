"""New extent evidence, preserving old map input bytes and all original outcomes."""
import calendar
from copy import deepcopy
import hashlib
from html import escape
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from indian_secc_local_normals import normal_point

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
REGION=[38.,-13.,44.,-5.]
QUANTITY_LABELS={
    'core_to_positive_normal_threshold_extent':'Core to + threshold',
    'local_two_sided_threshold_span':'Local paired span',
    'finite_paired_support_to_positive_threshold_extent':'Paired support boundary to + threshold',
    'shore_reference_to_positive_threshold_extent':'Independent shore to + threshold'}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def text(x,y,value,size=14):
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="#172d3a">{escape(str(value))}</text>'
def project(lon,lat):return 100+(lon-38)*80,150+(-5-lat)*80
def number(value):return 'unresolved' if value is None else f'{value:.3f}'
def span(value):
    return 'unresolved' if value is None else f'{math.floor(value[0]*10)/10:.1f} to {math.ceil(value[1]*10)/10:.1f} km'


def explicit_missing_hatching(raw):
    """Display-only derivative: avoid SVG-pattern black fill in raster backends.

    Geometry/data/arrows/candidate paths remain the old producer's output.
    Original bytes are never overwritten; raw input SHA is retained in manifest.
    """
    if len(raw)>2*1024*1024:raise ValueError('Base SVG exceeds map input cap')
    root=ET.fromstring(raw)
    if root.tag!=f'{{{NS}}}svg' or root.get('viewBox')!='0 0 820 920':
        raise ValueError('Unexpected frozen source map frame')
    changed=0
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag!=f'{{{NS}}}rect' or child.get('fill')!='url(#missing)':continue
            x,y,w,h=(float(child.get(key)) for key in ('x','y','width','height'))
            if not all(math.isfinite(v) for v in (x,y,w,h)) or not 0<w<=1000 or not 0<h<=1000:
                raise ValueError('Invalid source missing-cell geometry')
            group=ET.Element(f'{{{NS}}}g')
            rectangle=deepcopy(child);rectangle.set('fill','#eef1f3');group.append(rectangle)
            for d in range(-math.ceil(h),math.ceil(w),6):
                a,b=max(0,-d),min(h,w-d)
                if b>a:ET.SubElement(group,f'{{{NS}}}line',{
                    'x1':f'{x+d+a:.6f}','y1':f'{y+a:.6f}','x2':f'{x+d+b:.6f}',
                    'y2':f'{y+b:.6f}','stroke':'#87949c','stroke-width':'.8'})
            index=list(parent).index(child);parent.remove(child);parent.insert(index,group);changed+=1
    children=''.join(ET.tostring(child,encoding='unicode') for child in root
                     if child.tag not in (f'{{{NS}}}title',f'{{{NS}}}desc'))
    return children,changed


def svg_start(width,height,title,description):
    return [f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="white"/>']


def half(case,quantity):
    return next(m for v in case['variants'] if v['fraction']==.5 for m in v['metrics'] if m['quantity']==quantity)


def map_layer_svg(month,base_raw,adapted,calculated):
    base,changed=explicit_missing_hatching(base_raw)
    title=f'{calendar.month_name[month]} 2013: local signed-normal extent evidence'
    out=svg_start(1080,1100,title,
        'Original regional source map with explicit missing-data hatching and new local normal markers. Blue is the retained candidate peak and path to the positive side; orange is the50% crossing bracket; dashed gray marks the model support-transition bracket. These are not whole-current boundaries or physical uncertainty. Equivalent coordinates, q samples and all outcomes are in the monthly HTML.')
    out += [text(25,30,title,22),text(25,56,'Method development at 15 m · daily 00Z monthly sample means · original regional gate unchanged',15),
        '<g transform="translate(0 80)">'+base+'</g>',
        '<defs><clipPath id="extent-overlay-clip"><rect x="100" y="150" width="480" height="640"/></clipPath></defs>',
        '<g transform="translate(0 80)" clip-path="url(#extent-overlay-clip)">']
    profile=adapted.get('profile')
    if profile is not None:
        origin=tuple(profile['source']['original_seed_lon_lat']);bearing=adapted['adapter_audit']['seed_bearing_degrees_true']
        def at(offset):return project(*normal_point(origin,bearing,offset)[0])
        peak=profile['rows'][profile['peak']['index']]['s_km'];x,y=at(peak)
        positive=half(calculated,'core_to_positive_normal_threshold_extent')['positive_edge']
        if positive and positive['offset_bracket_km'] is not None:
            left,right=positive['offset_bracket_km']
            points=[at(peak+(left-peak)*i/30) for i in range(31)]
            coords=' '.join(f'{a:.4f},{b:.4f}' for a,b in points)
            out += [f'<polyline points="{coords}" fill="none" stroke="white" stroke-width="5"/>',
                f'<polyline points="{coords}" fill="none" stroke="#164e80" stroke-width="2.2"/>']
            a,b=at(left),at(right)
            out += [f'<line x1="{a[0]:.4f}" y1="{a[1]:.4f}" x2="{b[0]:.4f}" y2="{b[1]:.4f}" stroke="white" stroke-width="10"/>',
                f'<line x1="{a[0]:.4f}" y1="{a[1]:.4f}" x2="{b[0]:.4f}" y2="{b[1]:.4f}" stroke="#9c4b00" stroke-width="7"/>']
        reference=half(calculated,'finite_paired_support_to_positive_threshold_extent')['reference']
        if reference and reference.get('offset_bracket_km') is not None:
            a,b=(at(s) for s in reference['offset_bracket_km'])
            out.append(f'<line x1="{a[0]:.4f}" y1="{a[1]:.4f}" x2="{b[0]:.4f}" y2="{b[1]:.4f}" stroke="#475a68" stroke-width="7" stroke-dasharray="2 2"/>')
        out.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="4.5" fill="#164e80" stroke="white" stroke-width="2"/>')
    out.append('</g>')
    labels=['New local markers','Blue dot: retained peak','Blue line: core to + side','Orange: 50% crossing bracket',
        'Dashed gray: support bracket','Positive side is not verified','as geographic offshore.','No physical shoreline inferred.',
        'No whole-current width admitted.','Original map frame/data retained.',
        f'Explicit missing-cell hatches: {changed}', 'All six profiles and metrics', 'are retained in the report.']
    for i,label in enumerate(labels):out.append(text(830,140+29*i,label,13))
    out += [text(25,1040,'New markers use the offset0/step5 initial normal. Old source-map paths/edges remain visible and unchanged.',14),
        text(25,1068,'Missing velocity hatching is not a surveyed land mask. Current association, physical ranges and uncertainty remain unverified.',13),'</svg>']
    return ''.join(out),changed


def profiles_svg(month,adapted,calculated):
    out=svg_start(1000,110+260*len(adapted),f'{calendar.month_name[month]} 2013 retained initial profiles',
        'All six initial profiles, including unsupported cases, on signed WGS84 normal distance in km and projected q in m/s. Gaps are not connected; bands are sampling brackets, not confidence intervals. Every stored sample and outcome is in the monthly HTML.')
    out += [text(25,32,f'{calendar.month_name[month]} 2013 · all retained initial normal profiles',23),
        text(25,61,'Fixed original seeds/peaks · 40/50/60% definitions · sample/reference brackets are not physical uncertainty',14)]
    for n,(case,result) in enumerate(zip(adapted,calculated)):
        top=100+n*260
        out += [text(30,top,case['id']+' · original: '+case['source_status'].replace('_',' '),14)]
        profile=case.get('profile')
        if profile is None:
            out.append(text(45,top+60,'No supported original candidate profile; all metric slots remain unresolved.',15));continue
        rows=profile['rows'];valid=[r for r in rows if r['status']=='ok']
        left,right=rows[0]['s_km'],rows[-1]['s_km'];low=min(0,min(r['q_m_s'] for r in valid));high=max(r['q_m_s'] for r in valid)
        high=max(high+.1*(high-low),low+.02)
        x=lambda s:80+(s-left)/(right-left)*800
        y=lambda q:top+180-(q-low)/(high-low)*125
        out.append(text(80,top+35,'Projected q (m/s)',12))
        out.append(f'<rect x="80" y="{top+55}" width="800" height="125" fill="#f4f6f7" stroke="#a7b3bc"/>')
        for variant in result['variants']:
            edge=next(m for m in variant['metrics'] if m['quantity']=='core_to_positive_normal_threshold_extent')['positive_edge']
            if edge is None:continue
            level=sum(edge['threshold_component_interval_m_s'])/2
            out += [f'<line x1="80" y1="{y(level):.4f}" x2="880" y2="{y(level):.4f}" stroke="#9b6a27" stroke-dasharray="4 4"/>',text(888,y(level)+4,f'{variant["fraction"]:.0%}',12)]
        for i,row in enumerate(rows):
            if row['status']!='ok':continue
            if i and rows[i-1]['status']=='ok' and profile['segments'][i-1]['supported']:
                prior=rows[i-1]
                out.append(f'<line x1="{x(prior["s_km"]):.4f}" y1="{y(prior["q_m_s"]):.4f}" x2="{x(row["s_km"]):.4f}" y2="{y(row["q_m_s"]):.4f}" stroke="#244e69" stroke-width="1.8"/>')
            out.append(f'<circle cx="{x(row["s_km"]):.4f}" cy="{y(row["q_m_s"]):.4f}" r="1.5" fill="#244e69"/>')
        answer=half(result,'finite_paired_support_to_positive_threshold_extent')
        out += [text(80,top+203,f'{left:g} km',12),text(785,top+203,f'{right:g} km',12),
            text(330,top+203,'Signed normal distance (km)',12),
            text(30,top+67,number(high),11),text(30,top+180,number(low),11),
            text(45,top+230,'Support→+ threshold: '+span(answer['extent_bracket_km'])+' · '+answer['status'],12)]
    return ''.join(out+['</svg>'])


STYLE='body{font:16px/1.5 system-ui,sans-serif;color:#172d3a;max-width:78rem;margin:auto;padding:1rem}img{display:block;width:100%;height:auto}a{color:#13558a}a:focus-visible,summary:focus-visible{outline:3px solid #974b00;outline-offset:3px}nav a,summary{display:inline-block;padding:.6rem}table{border-collapse:collapse}th,td{padding:.35rem;border:1px solid #a7b3bc;vertical-align:top;text-align:left}code{overflow-wrap:anywhere}.scroll{overflow:auto;max-width:100%}caption{text-align:left;font-weight:bold}'
def page(title,body):
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{STYLE}</style><body><main><h1>{escape(title)}</h1>{body}</main></body></html>'


def monthly_html(month,adapted,calculated):
    name=f'm{month:02d}'
    body='<nav aria-label="Evidence months"><a href="index.html">All months</a>'
    body+=''.join(f'<a href="m{m:02d}.html">{calendar.month_abbr[m]}</a>' for m in range(1,13))+'</nav>'
    body+='<p>Local method development on 2013 HYCOM daily 00Z monthly sample means at 15 m. Current association and physical uncertainty remain unverified. Positive normal is not automatically offshore. A width of a monthly mean is not mean instantaneous width. No annual physical range or whole-current width is admitted.</p>'
    body+=f'<figure><img src="{name}-map-layer.svg" alt="Original regional model source map with explicit missing-data hatching and new retained-peak, support-transition and crossing-bracket markers."><figcaption>Original map geometry, values, arrows and old candidate paths are retained; missing-cell hatches are expanded for reliable raster display. New markers show the primary initial normal only. These are not current polygons.</figcaption></figure>'
    body+=f'<figure><img src="{name}-profiles.svg" alt="All six retained initial q profiles; every outcome and sample follows in tables."><figcaption>Signed geodesic normal offset in km; Earth-frame projected q in m/s. Missing samples are not zero or joined.</figcaption></figure>'
    primary=next(c for c in adapted if c['native_latitude_offset']==0 and c['normal_sample_step_km']==5)
    profile=primary.get('profile')
    if profile is not None:
        result=next(c for c in calculated if c['case_id']==primary['id'])
        origin=tuple(profile['source']['original_seed_lon_lat']);bearing=primary['adapter_audit']['seed_bearing_degrees_true']
        positions=[('Retained candidate peak',profile['rows'][profile['peak']['index']]['s_km'])]
        edge=half(result,'core_to_positive_normal_threshold_extent')['positive_edge']
        if edge and edge.get('offset_bracket_km'):
            positions.extend(zip(('Positive crossing bracket start','Positive crossing bracket end'),edge['offset_bracket_km']))
        reference=half(result,'finite_paired_support_to_positive_threshold_extent')['reference']
        if reference and reference.get('offset_bracket_km'):
            positions.extend(zip(('Support reference bracket start','Support reference bracket end'),reference['offset_bracket_km']))
        body+='<table><caption>Primary map-marker geometry from geodesic offsets; not a current footprint.</caption><thead><tr><th scope="col">Marker</th><th scope="col">Offset km</th><th scope="col">Longitude E</th><th scope="col">Latitude N</th></tr></thead><tbody>'
        for label,offset in positions:
            point,_=normal_point(origin,bearing,offset)
            body+=f'<tr><th scope="row">{escape(label)}</th><td>{offset:.6f}</td><td>{point[0]:.8f}</td><td>{point[1]:.8f}</td></tr>'
        body+='</tbody></table>'
    body+='<div class="scroll" tabindex="0" role="region" aria-label="All metric outcomes"><table><caption>All 6 cases × 3 fractions × 4 quantities; unresolved outcomes are retained.</caption><thead><tr>'
    body+=''.join(f'<th scope="col">{t}</th>' for t in ('Case / original status','Fraction','Quantity','Bracket','Outcome','Native scale km','Source grid scale check'))+'</tr></thead><tbody>'
    for case in calculated:
        for variant in case['variants']:
            for metric in variant['metrics']:
                values=[f'{variant["fraction"]:.0%}',QUANTITY_LABELS[metric['quantity']],span(metric['extent_bracket_km']),metric['status'].replace('_',' '),number(metric['maximum_native_cell_scale_km']),str(metric['source_scale_gate_passed'])]
                body+=f'<tr><th scope="row">{escape(case["case_id"])}<br>{escape(case["source_status"].replace("_"," "))}</th>'+''.join(f'<td>{escape(v)}</td>' for v in values)+'</tr>'
    body+='</tbody></table></div><details><summary>Every retained signed-offset / projected-q sample</summary><div class="scroll" tabindex="0" role="region" aria-label="Stored scalar profile samples"><table><caption>Source-rounded samples; source support statuses are preserved.</caption><thead><tr><th scope="col">Case</th><th scope="col">Offset km</th><th scope="col">q m/s</th><th scope="col">Support</th></tr></thead><tbody>'
    for case in adapted:
        for row in (case.get('profile') or {}).get('rows',[]):
            body+=f'<tr><th scope="row">{escape(case["id"])}</th><td>{row["s_km"]}</td><td>{escape(str(row["q_m_s"]))}</td><td>{escape(row["status"])}</td></tr>'
    body+='</tbody></table></div></details><p>Displayed brackets are rounded outward to 0.1 km; reporting precision is not physical uncertainty. Sampling/position brackets are not confidence intervals. Source cell spacing is not effective model resolution. The complete original source and source-grid alternatives remain in the linked source run.</p>'
    body+='<p><a href="https://github.com/giodl73-repo/OSW/actions/runs/40117999392">Original source case, semantic source-grid pages and frozen artifact</a> · <a href="../extents.json">Unrounded new extent report</a></p>'
    return page(f'{calendar.month_name[month]} 2013: coastal reference extent evidence',body)


def render_evidence(adapted,report,base_maps,base_manifest,directory,rasterize=False):
    if base_manifest['region_lon_lat']!=REGION or base_manifest['projection']!='equirectangular longitude/latitude':
        raise ValueError('Unknown source projection/region')
    if len(adapted)!=72 or len(report['cases'])!=72 or set(base_maps)!=set(range(1,13)):
        raise ValueError('All72 cases and12 source maps required')
    lookup={c['case_id']:c for c in report['cases']}
    if len(lookup)!=72 or {c['id'] for c in adapted}!=set(lookup):raise ValueError('Evidence case identity mismatch')
    out=Path(directory);out.mkdir(parents=True,exist_ok=False);files={};hatches={};source_maps={}
    def save(name,raw):
        with (out/name).open('xb') as stream:stream.write(raw)
        files[name]={'bytes':len(raw),'sha256':sha(raw)}
    for month in range(1,13):
        cases=[c for c in adapted if c['month']==month]
        if len(cases)!=6:raise ValueError('All six source cases required for every month')
        original=base_maps[month];expected=base_manifest['files'][f'm{month:02d}-map.svg']
        if len(original)!=expected['bytes'] or sha(original)!=expected['sha256']:raise ValueError('Source map fingerprint changed')
        source_maps[f'm{month:02d}-map.svg']=deepcopy(expected)
        primary=next(c for c in cases if c['native_latitude_offset']==0 and c['normal_sample_step_km']==5)
        mapped,count=map_layer_svg(month,original,primary,lookup[primary['id']]);hatches[month]=count
        curve=profiles_svg(month,cases,[lookup[c['id']] for c in cases])
        for suffix,content in (('map-layer.svg',mapped),('profiles.svg',curve)):
            name=f'm{month:02d}-{suffix}';save(name,content.encode())
            if rasterize:
                import pymupdf
                with pymupdf.open(stream=content.encode(),filetype='svg') as document:
                    save(name.removesuffix('.svg')+'.png',document[0].get_pixmap().tobytes('png'))
        save(f'm{month:02d}.html',monthly_html(month,cases,[lookup[c['id']] for c in cases]).encode())
    body='<p>Method development following the 2013 diagnostic. All 12 months and 72 attempts remain visible. No animation starts automatically, no source grid is replaced and no whole-current dimension is admitted.</p><ul>'
    body+=''.join(f'<li><a href="m{m:02d}.html">{calendar.month_name[m]}: map, all profiles, outcomes and sample table</a></li>' for m in range(1,13))+'</ul>'
    save('index.html',page('EACC coastal reference extent evidence · 2013',body).encode())
    manifest={'schema':'osw.eacc-coastal-reference-extent.figures.v1','months':12,'cases':72,
        'files':files,'source_map_inputs':source_maps,'source_map_frame_px':[100,150,480,640],
        'source_projection':'equirectangular longitude/latitude','source_region_lon_lat':REGION,
        'display_only_missing_hatch_expansion_count_by_month':hatches,'original_map_inputs_unchanged':True,
        'old_figure_producer_rerun':False,'all_metric_outcomes_and_q_samples_in_html':True,
        'independent_shore_reference_supplied':False,'current_association_verified':False,
        'new_current_measurements_admitted':0,'raster_pngs':rasterize}
    with (out/'manifest.json').open('w',encoding='utf8',newline='\n') as stream:json.dump(manifest,stream,indent=2);stream.write('\n')
    return manifest
