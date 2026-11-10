"""Small standalone SVG of known synthetic examples; never reads ocean data."""
import argparse
import hashlib
from html import escape
import json
import math
from pathlib import Path

from coastal_reference_extent_v1 import analyse,FRAME,COORDINATE

ROOT=Path(__file__).resolve().parents[1]
SVG='figures/coastal-reference-extent-v1-synthetic.svg'
MANIFEST='research/coastal-reference-extent-v1-synthetic-figure.json'


def fixture(detached=False):
    offsets=range(-100,105,5) if detached else range(-10,125,5)
    rows=[]
    for s in offsets:
        status='missing_paired_corner' if s==min(offsets) else 'ok'
        q=(math.exp(-(s/40)**2) if detached else .95 if s<0 else math.exp(-s/40)) if status=='ok' else None
        rows.append({'s_km':s,'q_m_s':q,'status':status})
    return {'case_id':'synthetic:detached' if detached else 'synthetic:near_support_boundary',
        'source':{'fixture':'analytic Gaussian' if detached else 'analytic seaward exponential with constructed inshore sample'},
        'legacy_regional_gate':{'status':'synthetic_only_not_a_real_current'},
        'frame':FRAME,'coordinate':COORDINATE,'normal_sample_step_km':5,
        'q_representation_bound_m_s':0,'offset_representation_bound_km':0,
        'rows':rows,'segments':[{'supported':a['status']==b['status']=='ok','native_cell_scale_km':2}
            for a,b in zip(rows,rows[1:])],
        'peak':{'index':next(i for i,r in enumerate(rows) if r['s_km']==0),
            'unique_verified':True,'local_support_verified':True,'source_fingerprint':'synthetic:known_function'}}


def half(result,name):
    return next(m for v in result['variants'] if v['fraction']==.5 for m in v['metrics'] if m['quantity']==name)


def text(x,y,value,size=16,**attributes):
    attrs=' '.join(f'{key.replace("_","-")}="{escape(str(value))}"' for key,value in attributes.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" {attrs}>{escape(str(value))}</text>'


def render():
    near=fixture();far=fixture(True)
    shore={'kind':'geographic_shoreline','status':'declared_shore_reference','offset_bracket_km':[-15,-10],
        'source_fingerprint':'synthetic:declared_shore_interval','geometry_reviewed':True,
        'inshore_flow_connectivity_verified':False}
    answers=[analyse(near,shore),analyse(far)]
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1050" viewBox="0 0 1000 1050" role="img" aria-labelledby="title desc">',
        '<title id="title">Synthetic coastal extent definitions</title>',
        '<desc id="desc">Two synthetic scalar profiles, not ocean measurements. The first has a missing inshore velocity region: one-sided, supported-domain and conditional shore-referenced extents differ. The second has two velocity crossings and a disconnected inshore support reference. Text below each panel gives the bounds and unresolved outcomes.</desc>',
        '<style>text{font-family:system-ui,sans-serif;fill:#172d3a} .grid{stroke:#d8dee2;stroke-width:1} .axis{stroke:#607583;stroke-width:1.3}</style>',
        '<defs><pattern id="missing" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="#a5adb3" stroke-width="1"/></pattern></defs>',
        '<rect width="1000" height="1050" fill="white"/>',
        text(35,38,'Boundary choice changes the reported quantity',26,font_weight=650),
        text(35,67,'Constructed profiles only · 5 km sampling · 2 km native-scale fixture · no measurement admission',15)]
    for index,(profile,result) in enumerate(zip((near,far),answers)):
        top=110+index*450;low,high=(-25,100) if index==0 else (-105,105)
        x=lambda s:95+(s-low)/(high-low)*800
        y=lambda q:top+205-q/1.1*170
        out += [text(35,top,'A · Core reaches the inshore support limit' if index==0 else 'B · Detached offshore core',21,font_weight=650),
                text(35,top+25,'Projected velocity q (m/s); signed normal distance s (km).',14)]
        ref=half(result,'finite_paired_support_to_positive_threshold_extent')['reference']
        if ref and ref.get('offset_bracket_km'):
            left,right=ref['offset_bracket_km']
            out += [f'<rect x="{x(low):.2f}" y="{top+35}" width="{x(left)-x(low):.2f}" height="170" fill="#eef1f3"/>',
                    f'<rect x="{x(left):.2f}" y="{top+35}" width="{x(right)-x(left):.2f}" height="170" fill="#dce4e9" stroke="#647785" stroke-dasharray="3 3"/>']
            width=x(left)-x(low)
            for d in range(-170,math.ceil(width),8):
                a,b=max(0,-d),min(170,width-d)
                if b>a:out.append(f'<line x1="{x(low)+d+a:.2f}" y1="{top+35+a:.2f}" x2="{x(low)+d+b:.2f}" y2="{top+35+b:.2f}" stroke="#a5adb3" stroke-width="1"/>')
        for q in (0,.5,1):
            out += [f'<line x1="95" y1="{y(q):.2f}" x2="895" y2="{y(q):.2f}" class="grid"/>',text(85,y(q)+5,f'{q:g}',14,text_anchor='end')]
        out += [f'<line x1="95" y1="{y(.5):.2f}" x2="895" y2="{y(.5):.2f}" stroke="#92631d" stroke-dasharray="5 4"/>',text(905,y(.5)+5,'50%',14)]
        positive=half(result,'core_to_positive_normal_threshold_extent')['positive_edge']['offset_bracket_km']
        left,right=positive
        out.append(f'<rect x="{x(left):.2f}" y="{top+35}" width="{x(right)-x(left):.2f}" height="170" fill="#f2d499" fill-opacity=".55" stroke="#92631d" stroke-dasharray="4 3"/>')
        paired=half(result,'local_two_sided_threshold_span')
        if paired['reference'] and paired['reference'].get('offset_bracket_km'):
            left,right=paired['reference']['offset_bracket_km']
            out.append(f'<rect x="{x(left):.2f}" y="{top+35}" width="{x(right)-x(left):.2f}" height="170" fill="#f2d499" fill-opacity=".55"/>')
        for i,row in enumerate(profile['rows']):
            if row['status']!='ok':continue
            if i and profile['segments'][i-1]['supported'] and low<=profile['rows'][i-1]['s_km'] and row['s_km']<=high:
                prior=profile['rows'][i-1]
                out.append(f'<line x1="{x(prior["s_km"]):.2f}" y1="{y(prior["q_m_s"]):.2f}" x2="{x(row["s_km"]):.2f}" y2="{y(row["q_m_s"]):.2f}" stroke="#244e69" stroke-width="2.2"/>')
            if low<=row['s_km']<=high:
                out.append(f'<circle cx="{x(row["s_km"]):.2f}" cy="{y(row["q_m_s"]):.2f}" r="2.4" fill="white" stroke="#244e69"/>')
        for tick in ((-25,0,25,50,75,100) if index==0 else (-100,-50,0,50,100)):
            out += [f'<line x1="{x(tick):.2f}" y1="{top+205}" x2="{x(tick):.2f}" y2="{top+211}" class="axis"/>',text(x(tick),top+231,str(tick),14,text_anchor='middle')]
        labels=[('Core → positive threshold','core_to_positive_normal_threshold_extent'),
                ('Two-sided local threshold span','local_two_sided_threshold_span'),
                ('Finite-support boundary → threshold','finite_paired_support_to_positive_threshold_extent'),
                ('Independent shore interval → threshold','shore_reference_to_positive_threshold_extent')]
        for n,(label,quantity) in enumerate(labels):
            answer=half(result,quantity);bounds=answer['extent_bracket_km']
            value=f'{bounds[0]:g}–{bounds[1]:g} km' if bounds else 'unresolved'
            out.append(text(45,top+270+n*27,label+': '+value,15))
        note=('Shore extent is conditional: the 5–10 km inshore model gap remains unsupported.' if index==0 else
              'The inshore support reference lies outside the connected half-peak core.')
        out.append(text(45,top+385,note,15,font_weight=600))
    out += [text(35,981,'Hatching: missing velocities · outlined band: support transition · amber bands: threshold brackets',14),
        text(35,1010,'Bands mark sampling/reference brackets. They are not physical uncertainty or annual ranges.',15),'</svg>']
    return ''.join(out),answers


def write(refresh=False):
    svg,results=render();raw=svg.encode()
    manifest={'schema':'osw.coastal-reference-extent.synthetic-figure.v1','original_ocean_data_used':False,
        'source':'Constructed scalar profiles, not an ocean model or observations','figure':SVG,
        'figure_sha256':hashlib.sha256(raw).hexdigest(),
        'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'operator_sha256':hashlib.sha256((ROOT/'analysis/coastal_reference_extent_v1.py').read_bytes()).hexdigest(),
        'examples':results,'measurement_admission':False}
    for name,data in ((SVG,raw),(MANIFEST,(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode())):
        path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():
            if path.read_bytes()!=data:
                if not refresh or json.loads((ROOT/MANIFEST).read_bytes()).get('original_ocean_data_used') is not False:
                    raise ValueError('Changed existing synthetic artifact: '+name)
                path.write_bytes(data)
        else:
            with path.open('xb') as stream:stream.write(data)
    print(json.dumps({'figure':SVG,'bytes':len(raw),'original_ocean_data_used':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-synthetic',action='store_true')
    parser.add_argument('--refresh-synthetic',action='store_true')
    args=parser.parse_args()
    if not args.write_synthetic:parser.error('Use --write-synthetic for constructed examples only')
    write(args.refresh_synthetic)
