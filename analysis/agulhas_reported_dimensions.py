"""Original-publication readback; scoped core description, no whole-length admission."""
from pathlib import Path
import copy,hashlib,json,re,xml.etree.ElementTree as ET
import current_measurement_admissions as prior

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='research/source-data/vinayachandran-indian-upwelling-2021/'
FILE='research/agulhas-vinayachandran-2021-reported-dimensions.json'
PROTOCOL='plans/agulhas-reported-dimensions-protocol-v1.md'
OPERATOR='analysis/agulhas_reported_dimensions.py'
FIGURE='figures/agulhas-vinayachandran-2021-reported-dimensions.svg'
EXPORT='research/ocean-current-effective-measurements.json'
ID='diagnostic:agulhas-vinayachandran-2021-reported-dimensions'
WIDTH_ID='agulhas-vinayachandran-2021-typical-core-description'
SOURCE_ID='source:ef2c46e173e203ae'
PINS={'article.pdf':'9ca5a0854eff936d32d5fd597cd94007ea3704ddba1ebeb1aeedede09967472d',
      'article.xml':'b0b6aaa4932ce5fcce1576c0cb389f106c96f56e983fc3773803a8ac53ed3f45'}
URL='https://bg.copernicus.org/articles/18/5967/2021/'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def read(path):return json.loads((ROOT/path).read_bytes())

def original():
    acquisition=read(DIRECTORY+'acquisition.json')
    if acquisition['doi']!='10.5194/bg-18-5967-2021' or acquisition['license']!='CC BY 4.0':
        raise ValueError('Changed publication identity/license')
    for name,pin in PINS.items():
        path=DIRECTORY+name;raw=(ROOT/path).read_bytes()
        matches=[r for r in acquisition['files'] if r['path']==path]
        if len(matches)!=1 or digest(path)!=pin or matches[0]['sha256']!=pin or matches[0]['bytes']!=len(raw):
            raise ValueError('Changed publisher original: '+name)
    tree=ET.fromstring((ROOT/(DIRECTORY+'article.xml')).read_bytes())
    paragraphs=[' '.join(''.join(p.itertext()).split()) for p in tree.iter('p')]
    length=[p for p in paragraphs if '1000 km long western boundary current' in p]
    width=[p for p in paragraphs if re.search(r'core\s*\([^)]*200\s*km wide',p)]
    if len(length)!=1 or len(width)!=1:raise ValueError('Changed source passages')
    return acquisition

def source_record():
    source=copy.deepcopy(next(r for r in prior.identity.read(prior.identity.BASE+'sources.json') if r['id']==SOURCE_ID))
    source.update(provider_asset_redistributed=True,repository_path=DIRECTORY+'article.pdf',
        rights_status='Original publication redistributed under publisher CC BY 4.0; attribution retained.',
        rights_policy_url='https://creativecommons.org/licenses/by/4.0/',rights_review_date='2026-10-21',
        source_file_sha256=PINS['article.pdf'],source_xml_sha256=PINS['article.xml'],license='CC BY 4.0',
        used_in_collections=list(dict.fromkeys(source['used_in_collections']+['widths','diagnostics'])),
        metadata_note='Original PDF/XML acquired 2026-10-21 and pages5970–5971 inspected. Length is an existing unranked coastal variant. Core width is a contextual description, with no width dates, fixed layer, numerical edges or error supplied.')
    return source

def width_record():
    return {'id':WIDTH_ID,'current_id':'agulhas','name':'Agulhas Current',
        'status':'editorial_source_extraction_not_historical_release','measurement_type':'published_regional_summary',
        'width_metric':'author_reported_typical_core_width','approximate_width_km':200,'width_range_km':None,
        'range_interpretation':'One typical core description; not a time mean, variability range or confidence interval.',
        'geographic_scope':'Southeast African coastal western-boundary-current description in section2.1.1; exact section and paired edges unspecified.',
        'vertical_scope':'Unspecified; adjacent surface/core speed is not a fixed width layer.',
        'layer':'Unspecified; no fixed width-layer bounds supplied.','fixed_layer_bounds_m':None,
        'boundary_rule':'Author-described typical core; numerical velocity cutoff and edge coordinates unspecified.',
        'boundary_sides':'author_reported_core_edges_not_supplied','source_id':SOURCE_ID,'source_url':URL,
        'source_citation':'Vinayachandran et al. (2021), Biogeosciences18,5967–6029, doi:10.5194/bg-18-5967-2021.',
        'source_locator':'Section2.1.1 paragraph2, printed5971/PDF5; width sentence cites Lutjeharms2006 and Beal et al.2015.',
        'source_access':'Original publisher PDF/XML retained; PDF pages4–5 visually inspected2026-10-21.',
        'extraction_method':'Direct prose readback; no velocity threshold, interpolation or figure digitization.',
        'source_precision':'approximately 200 km; typical core description','uncertainty_km':None,'observed_period':None,
        'time_precision':None,'calendar_months':None,'phase_label':'Undated typical core description',
        'phase_kind':'published_typical_core_description','time_convention':'Publication date is not an observation or averaging period.',
        'whole_current_representative':False,'width_rank_eligible':False,'full_width_inference_eligible':False,
        'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'is_confidence_interval':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None,
        'source_quality_note':'Contextual review description, not independent observations. ACT219km is a different time-mean section metric, not the other end of a200–219km range.',
        'source_report_file':FILE,'original_source_file':DIRECTORY+'article.pdf','source_pdf_sha256':PINS['article.pdf'],
        'independent_width_observation':False,'related_measurement_ids':['agulhas-act-eulerian-mean-section-width'],
        'physical_current_envelope_admitted':False,'historical_release_admitted':False,'is_annual_mean':False,'is_climatology':False}

def figure():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" role="img" aria-labelledby="title desc">
<title id="title">Agulhas: two separately scoped source descriptions</title>
<desc id="desc">A reported one thousand kilometre coastal extent and an approximately two hundred kilometre typical core width. Separate scalar descriptions; no geographic edges, area, observation date or annual range. The existing ACT two hundred nineteen kilometre time-mean section result is a different metric.</desc>
<rect width="900" height="410" fill="#eef6f8"/><g fill="#123c4b" font-family="Arial, sans-serif">
<text x="28" y="40" font-size="25" font-weight="bold">Agulhas · reported dimension context</text>
<text x="28" y="82" font-size="18">Coastal western-boundary extent · existing unranked source variant</text>
<text x="28" y="127" font-size="34" font-weight="bold">≈ 1,000 km</text>
<text x="28" y="160" font-size="17">Different scope from the broader 27–40°S geographic floor and reference route.</text>
<path d="M28 182H872" stroke="#587681"/>
<text x="28" y="216" font-size="18">Typical core-width description · contextual literature summary</text>
<text x="28" y="260" font-size="34" font-weight="bold">≈ 200 km</text>
<text x="28" y="294" font-size="17">Dates, layer, edge cutoff and uncertainty unspecified. No annual range.</text>
<text x="28" y="326" font-size="17">ACT 219 km is a different time-mean section metric; do not combine as a range.</text>
<text x="28" y="369" font-size="16">Vinayachandran et al. (2021), §2.1.1 · doi:10.5194/bg-18-5967-2021</text>
<text x="28" y="394" font-size="15">Original CC BY 4.0 article · OSW scalar summary, not a geographic diagram.</text>
</g></svg>'''.encode()

def build():
    original()
    if (ROOT/FIGURE).read_bytes()!=figure():raise ValueError('Changed dimension summary figure')
    paths=[DIRECTORY+n for n in ['article.pdf','article.xml','acquisition.json']]+[PROTOCOL,OPERATOR,FIGURE,'analysis/acquire_indian_upwelling_review.py',prior.identity.BASE+'sources.json']
    return {'schema':'osw.agulhas-reported-dimension-context.v1','version':'1','current_id':'agulhas','entity_id':'current:agulhas',
        'status':'scoped_core_description_admitted_length_variant_unranked','source_url':URL,'source_doi':'10.5194/bg-18-5967-2021',
        'source_record':source_record(),'width_record':width_record(),'figure_file':FIGURE,
        'length_variant':{'value_km':1000,'quantity':'reported_coastal_extent','source_locator':'Section2.1.1 paragraph1, printed5970/PDF4.',
            'rank_eligible':False,'new_length_measurement_admitted':False,'scope':'Existing narrow coastal western-boundary description, not the broader27–40S floor or whole current system.',
            'endpoint_coordinates_lon_lat':None,'fixed_layer_bounds_m':None,'observed_period':None,'uncertainty_km':None},
        'original_pdf_pages_visually_reviewed':[4,5],'original_source_figures_digitized':False,
        'source_report_type':'contextual_review_description_citing_earlier_literature',
        'physical_current_edges_admitted':False,'annual_extrema_admitted':False,'external_scientific_review_claimed':False,
        'input_sha256':{p:digest(p) for p in paths}}

def verify():
    doc=build()
    if (ROOT/FILE).read_bytes()!=encoded(doc):raise ValueError('Stale Agulhas dimension context')
    return doc

def effective_export(doc=None):
    doc=verify() if doc is None else doc
    base=copy.deepcopy(prior.working_export())
    base.update(schema='osw.effective-current-measurements.v1',version='0.2.0-draft-core-description-1',
        base_working_export=prior.EXPORT,additional_admission_files=[FILE],scoped_width_count=158)
    base['widths'].append(doc['width_record'])
    base['sources']=[doc['source_record'] if r['id']==SOURCE_ID else r for r in base['sources']]
    base['input_sha256'].update({prior.EXPORT:digest(prior.EXPORT),FILE:digest(FILE),OPERATOR:digest(OPERATOR)})
    return base

def verify_inputs():
    doc=verify()
    if (ROOT/EXPORT).read_bytes()!=encoded(effective_export(doc)):raise ValueError('Stale effective measurements')
    return doc,{**doc['input_sha256'],FILE:digest(FILE),EXPORT:digest(EXPORT),prior.EXPORT:digest(prior.EXPORT)}

def diagnostic(doc):
    return {'id':ID,'label':'Agulhas source-reported coastal extent and typical core description',
        'entity_id':'current:agulhas','current_id':'agulhas','rank_eligible':False,'source_file':FILE,
        'source_file_sha256':digest(FILE),'source_json':(ROOT/FILE).read_text(encoding='utf-8'),
        'summary':{'reported_coastal_extent_km':1000,'reported_typical_core_width_km':200,'independent_observation':False,
            'annual_range_km':None,'geographic_edges':None,'whole_current_length_rank_admitted':False}}

if __name__=='__main__':
    (ROOT/FIGURE).write_bytes(figure())
    doc=build();(ROOT/FILE).write_bytes(encoded(doc));(ROOT/EXPORT).write_bytes(encoded(effective_export(doc)))
    print('Built Agulhas scoped200km core description;1000km variant remains unranked;158 scoped widths/83 owners.')
