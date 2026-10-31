"""Two reported mean-core spans; proposed branch, no canonical transfer."""
from pathlib import Path
import copy,hashlib,json,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='research/source-data/baumann-nwasc-2026/'
FILE='research/norwegian-baumann-2026-mean-core-widths.json'
FIGURE='figures/norwegian-baumann-2026-mean-core-widths.svg'
PROTOCOL='plans/nwasc-mean-core-width-protocol-v1.md'
OPERATOR='analysis/nwasc_mean_core_widths.py'
OWNER='norwegian-atlantic-slope'
URL='https://os.copernicus.org/articles/22/17/2026/'
PINS={'article.pdf':'b7a49fcc9ff6f2f487381d9736996fd07e5cd0d2310743a88fb168e1587bae49',
      'article.xml':'81be4c2d2e437e1375c7063cd6f58cde79b66ea593437d6425346d0d1086b96d'}

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(doc):return (json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()

def original():
    receipt=read(DIRECTORY+'acquisition.json')
    if receipt['doi']!='10.5194/os-22-17-2026' or receipt['license']!='CC BY 4.0':raise ValueError('Changed mean-core publication identity/license')
    for name,pin in PINS.items():
        path=DIRECTORY+name;raw=(ROOT/path).read_bytes();entry,=[r for r in receipt['files'] if r['path']==path]
        if digest(path)!=pin or entry['sha256']!=pin or entry['bytes']!=len(raw):raise ValueError('Changed mean-core publisher original')
    text=' '.join(''.join(ET.fromstring((ROOT/(DIRECTORY+'article.xml')).read_bytes()).itertext()).split())
    for passage in ['lateral extent of about 50', 'extending about 50', '35.16', 'static over time', '2500', '1993–2022']:
        if passage not in text:raise ValueError('Changed mean-core source passage: '+passage)
    return receipt

def measurements():
    rows=[]
    for section,plane,depth,isobath,casts in [('svinoy',50,460,1500,4),('gimsoy',None,530,2500,None)]:
        name='Svinøy' if section=='svinoy' else 'Gimsøy'
        rows.append({'id':f'norwegian-atlantic-slope-baumann-2026-{section}-mean-core-span',
            'proposed_current_id':OWNER,'name':'Norwegian Atlantic Slope Current',
            'status':'editorial_width_evidence_for_proposed_identity_not_canonical',
            'measurement_type':'published_mean_field_transport_core_extent',
            'width_metric':'mean_core_lateral_extent_at_50m' if plane else 'mean_core_horizontal_projection_extent',
            'approximate_width_km':50,'width_range_km':None,'range_kind':None,'unit':'km',
            'source_precision':'about 50 km','uncertainty_km':None,
            'geographic_scope':name+' repeat section across the Norwegian continental slope; source-defined slope branch.',
            'layer':('Lateral extent at 50 m; variable core shape reaches about 460 m.' if plane else 'Horizontal extent of a variable-depth mean core from 50 m to about 530 m maximum depth; no single width plane specified.'),
            'width_plane_depth_m':plane,'fixed_layer_bounds_m':None,'core_upper_boundary_m':50,
            'reported_maximum_core_depth_m':depth,'scope_isobath_m':isobath,'isobath_is_width_layer':False,
            'core_salinity_minimum_g_kg':35.16,'mean_transport_fraction':0.5,
            'boundary_rule':'Fastest mean absolute-geostrophic-velocity cells supplying 50% of mean Atlantic-Water transport, within salinity and shoreward-isobath domain; no paired geographic edges transcribed.',
            'observed_period':'1993–2022','time_precision':'year_range','calendar_months':None,
            'temporal_interpretation':'Static core defined from 30-year mean fields, not a mean of instantaneous widths. Uneven seasonal sampling retained; no monthly width series.',
            'is_mean_field_geometry':True,'is_mean_of_widths':False,'is_uniformly_sampled_climatology':False,
            'section_geometry':None,'geographic_current_edges':None,'core_connectivity_verified':False,
            'width_support_cast_count':casts,'source_publication_year':2026,
            'source_url':URL,'source_citation':'Baumann et al. (2026), Ocean Science22,17–29, doi:10.5194/os-22-17-2026.',
            'source_locator':'Section2.1.2, printed19–21/PDF3–5; '+('Svinøy paragraph and Figure3a.' if plane else 'Gimsøy paragraph and Figure3b.'),
            'source_access':'Original publisher PDF/XML retained; methods and Figure3 visually inspected2026-10-21.',
            'source_license':'CC BY 4.0','original_pdf':DIRECTORY+'article.pdf',
            'extraction_method':'Direct reported prose quantities, independently checked against original pages; no image digitization or velocity reconstruction.',
            'phase_label':name+' · 1993–2022 static mean-core extent',
            'whole_current_representative':False,'full_width_inference_eligible':False,'rank_eligible':False,
            'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'is_confidence_interval':False,
            'whole_current_width_km':None,'annual_width_range_km':None,
            'source_quality_note':'50 km box-model width is a separate modeling choice. Core areas at different sections and previous width operators cannot be combined into an area, trend or seasonal range.'})
    return rows

def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" role="img" aria-label="Norwegian Atlantic Slope Current: two approximately 50 km static mean-core spans, with different vertical support. Proposed branch only; no seasonal range.">
<rect width="900" height="410" fill="#f7faf9"/><g font-family="sans-serif" fill="#123541">
<text x="24" y="35" font-size="24">Norwegian Atlantic Slope Current · mean-core spans</text>
<text x="24" y="66" font-size="18">1993–2022 mean fields · proposed identity · separate section supports</text>
<text x="24" y="108" font-size="21">Svinøy: ≈ 50 km at 50 m depth</text>
<text x="24" y="139" font-size="17">Four CTD casts; variable core reaches about 460 m maximum depth.</text>
<path d="M24 164H876" stroke="#8ca4ab"/>
<text x="24" y="204" font-size="21">Gimsøy: ≈ 50 km horizontal core extent</text>
<text x="24" y="235" font-size="17">Variable-depth shape, 50 m top to about 530 m deepest point; no fixed width plane.</text>
<text x="24" y="282" font-size="17">50% of mean AW transport; salinity ≥ 35.16 g/kg; section-specific isobath limits.</text>
<text x="24" y="313" font-size="17">Static mean-core geometry, not mean widths, annual extrema or seasonal samples.</text>
<text x="24" y="350" font-size="16">No paired geographic edges, uncertainty, whole-current width or area inferred.</text>
<text x="24" y="384" font-size="15">Baumann et al. (2026), §2.1.2, Fig.3 · CC BY4.0 · independent OSW scalar diagram</text>
</g></svg>'''.encode()

def build():
    original()
    if (ROOT/FIGURE).read_bytes()!=figure():raise ValueError('Changed mean-core scalar diagram')
    paths=[DIRECTORY+n for n in ['article.pdf','article.xml','acquisition.json']]+[PROTOCOL,OPERATOR,FIGURE]
    return {'schema':'osw.nwasc-mean-core-widths.v1','version':'1','proposed_current_id':OWNER,
        'status':'source_reported_section_core_extents_proposed_identity_only','source_url':URL,
        'source_doi':'10.5194/os-22-17-2026','measurements':measurements(),'figure_file':FIGURE,
        'original_pdf':DIRECTORY+'article.pdf','source_license':'CC BY 4.0','pages_visually_reviewed':[3,4,5,6],
        'raw_curated_sections_acquired':False,'raw_data_reproduction_claimed':False,
        'raw_data_availability':'Public IMR CTD data: doi:10.48670/moi-00031. Curated study sections require contacting the corresponding author; no contact made.',
        'full_current_width_admitted':False,'physical_current_edges_admitted':False,'annual_extrema_admitted':False,
        'canonical_name_equivalence_admitted':False,'input_sha256':{p:digest(p) for p in paths}}

def verify_inputs():
    doc=build()
    if (ROOT/FILE).read_bytes()!=encoded(doc):raise ValueError('Stale mean-core width report')
    return doc,{**doc['input_sha256'],FILE:digest(FILE)}

def records():
    doc,_=verify_inputs();rows=copy.deepcopy(doc['measurements'])
    for i,r in enumerate(rows):r.update(source_file=FILE,source_pointer=f'/measurements/{i}')
    return rows

if __name__=='__main__':
    (ROOT/FIGURE).write_bytes(figure());doc=build();(ROOT/FILE).write_bytes(encoded(doc))
    print('Built two mean-core spans on proposed Norwegian Atlantic Slope branch; canonical widths unchanged.')
