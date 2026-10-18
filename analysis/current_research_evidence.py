"""Bind reviewed studies to shared evidence scenes without width admission."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
PATH='research/current-research-evidence-registry.json'
FROZEN_INPUTS = {
    "research/indian-secc-eof-classification-feasibility.json": "1ec87c83802445c8685a091fc1b8d9a7d70755bc203dd3c09e14baafa0e2d144",
    "research/redsox-cruise-log-metadata-reconciliation.json": "c20b965126a62925b35cf61c8d7b61cd887d236e478dba57714cbc1b7bba252b",
    "research/redsox-ctd-companion-inventory.json": "b411184a90164368a75f36eba32c1e24c48a386c725859ab0e530bc5582ca7ee",
    "research/redsox-ladcp-source-inventory.json": "0c67399b66991f0160f09c21ce6a6966b4426fe7a434cd0126fd13a7f368a254",
    "research/redsox-lower-nc-dated-section-diagnostic.json": "fc247b8090793bdcc62e6073d51522fa21e756759fde4caab6383dba84e0f3c5",
    "research/source-data/ncei-redsox-2001/acquisition.json": "f6453064d837cefa689fa274e72c5d5b84bcae85d119910a48f1092d7f11236c",
    "research/source-data/ncei-redsox-2001/ctd-acquisition.json": "56f7c5bb42a7db5f891b47b7c53eb19501d7deb7fa0c2fa4612d0270945dc498",
    "research/source-data/ncei-redsox-2001/ctd-preflight.json": "1230ece2b9c4869d76d94b9f2e751273f10cb9ddd2d3bdbe466408ae7c02a326",
    "research/source-data/ncei-redsox-2001/documentation.json": "12c56f526f1054643cdc72848bf791f6780cdb5aa2615c92a330079cc022bcd2",
    "research/source-data/ncei-redsox-2001/preflight.json": "334a989a2b2f5205d345584f8c471641bac3eea7be4a44ab360cb1881a855b41",
    "research/source-data/oscar-indian-eof-1995-2016/acquisition.json": "dc684f969378f2ada64a6174fa23810ade8bbe8db2f86ea77e849384b7d95fae",
    "research/source-data/oscar-indian-eof-1995-2016/preflight.json": "b9c19d3c1abd87bf9b1c03910d383905a07de73ba2a957f597f83ab1224587a9",
    "research/source-data/redsox-lower-nc-2001/alternate-format-acquisition.json": "f0cc0d599b9ae5262ec05183211611ffa1b483eeef313ad845ba3d035d6e11ac",
    "research/source-data/redsox-lower-nc-2001/declaration-history-note.json": "23f5f47e82136efe661cb35422b7d2bc7447648048965d1f44a75bb6c6fb9123",
    "research/source-data/redsox-lower-nc-2001/implementation-clarifications.json": "2fbf9636562ee5e22e420e1355220bded6368ab05aee82fe92f9949cc8e8a81b",
    "research/source-data/redsox-lower-nc-2001/lower-northern-channel-section-preflight.json": "c9aa43ff540a180e606b984400aaa29d20f525e91dfee12b17791ece53c98660",
    "research/source-data/redsox-lower-nc-2001/matched-section-followup-preflight.json": "cfced47f8fc78bb1fc37b1e6033f499e687afab5239388f104d330a6e0dd410a"
}
YEAR='research/source-data/norkyst-ingoy-months-2024/section-diagnostic-year.json'
YEAR_ROOT='research/source-data/norkyst-ingoy-months-2024/'
FROZEN_INPUTS.update({
    'research/source-data/norkyst-ingoy-months-2024/preflight.json': '64e2513c69d554e30d2cda61ccb4c26f47711163d12dcefbe98c720c3b2ee42d',
    'research/source-data/norkyst-ingoy-months-2024/acquisition-pilot.json': 'a3b45fbd4d1bae694e23533cb6387c65d97e7f56f6c57852aab9340c9ebd0e35',
    'research/source-data/norkyst-ingoy-months-2024/regional-monthly-means-year.json': 'a165a29e8c5f24fb88020194707d692c2f597cd3b65c55119f0a84486042bec5',
    YEAR: '390c9457c116abadbd3c5efb79bd1899f1a98d5cae6c7a916610b909947002bf',
    YEAR_ROOT+'figure-year.json': 'fd253485672fe34da50531046fb3145f7af738266679bc00e2bf4f9bde812d62',
    YEAR_ROOT+'acquisition-year.json': '763ed97ac94fa7c220baa9333d4ab5b74d7f86fa296606a8c022c126e0fe01fc',
})
NECC='research/pacific-necc-paired-vector-direction-evidence.json'
NECC_BASE='research/source-data/oscar-necc-vectors-2013/'
FROZEN_INPUTS.update({'research/pacific-necc-paired-vector-direction-evidence.json': '14c556b982c387a199fcddafce319843451e438739ee14b09ffb0a135c0216f6', 'research/pacific-necc-paired-vector-source-inventory.json': '549e5f09d5489133e498f50b886df0cf1b2cb56610874a17d7192d155e74b580', 'research/source-data/oscar-necc-vectors-2013/preflight.json': 'b65a57a268075c1e3efc6ebc6c1c319c3b6e7462c23ad7dedbbb2731e3427294', 'research/source-data/oscar-necc-vectors-2013/metadata.json': '8c1f41c4e7a0f91492482345e7038c47e461c46c56852dbe57f217e40b9ec2ba', 'research/source-data/oscar-necc-vectors-2013/metadata-acquisition.json': 'f9261037ca1d2bfc92ed91894736f8d29a05bb3e3c0ab6d49414a97fac110203', 'research/source-data/oscar-necc-vectors-2013/acquisition.json': 'e0f5c86892b9c7a73e3efef41a456cd46672238e08dc72c6927e12e9c25b0a05', 'research/source-data/oscar-necc-vectors-2013/figure.json': '5f547d1d2e9887d9668c958e4f82a8a4903965c955412498e7416aa8773a3d09'})
EOF='research/indian-secc-eof-classification-feasibility.json'
SECTION='research/redsox-lower-nc-dated-section-diagnostic.json'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    if len(FROZEN_INPUTS)!=30:raise ValueError('Missing reviewed research source registry')
    documents={}
    for path,pin in FROZEN_INPUTS.items():
        if digest(path)!=pin:raise ValueError('Changed reviewed current research source '+path)
        documents[path]=json.loads((ROOT/path).read_bytes())
    dependencies=dict(FROZEN_INPUTS)
    for path,doc in documents.items():
        for source,pin in doc.get('input_sha256',{}).items():
            dependencies[source]=pin
        for field in ['source_ladcp_inputs','source_ctd_inputs']:
            dependencies.update(doc.get(field,{}))
        for original in doc.get('existing_southern_files',[]):dependencies[original['file']]=original['sha256']
        parent=Path(path).parent
        if 'bundle' in doc:dependencies[(parent/doc['bundle']['file']).as_posix()]=doc['bundle']['sha256']
        for name,record in doc.get('files',{}).items():
            if name.endswith('.csv'):dependencies[(parent/name).as_posix()]=record['sha256']
        for name,record in doc.items():
            if name.endswith('.mat') and isinstance(record,dict):dependencies[(parent/name).as_posix()]=record['sha256']
    for source in ['analysis/build_indian_secc_eof_feasibility.py','analysis/build_redsox_lower_nc_section.py',
        'analysis/build_redsox_ladcp_source_inventory.py','analysis/build_redsox_ctd_companion_inventory.py',
        'analysis/build_indian_secc_eof_feasibility_figure.py','analysis/build_redsox_lower_nc_figure.py',
        'figures/indian-secc-eof-feasibility.svg','figures/redsox-ladcp-source-support.svg',
        'figures/redsox-lower-nc-section-diagnostic.svg']:
        dependencies[source]=digest(source)
    year=documents[YEAR]
    if (year['calendar_hours']!=8784 or year['completed_months']!=list(range(1,13))
        or not year['complete_annual_section_support'] or year['new_width_record_admitted']):
        raise ValueError('Changed complete-year model scope')
    dependencies['analysis/build_norkyst_continuous_year.py']=year['generator_sha256']
    dependencies['analysis/build_norkyst_continuous_year_figures.py']=documents[YEAR_ROOT+'figure-year.json']['generator_sha256']
    for asset in year['monthly_assets']:dependencies[asset['file']]=asset['sha256']
    for figure in documents[YEAR_ROOT+'figure-year.json']['figures'].values():
        dependencies[figure['svg_file']]=figure['svg_sha256']
        dependencies[figure['png_file']]=figure['png_sha256']
    necc=documents[NECC]
    if necc['source_vector_positions']!=7992 or necc['target_u_values_and_masks_exact']!=2664 or necc['summary']['target_monthly_means_equal_old']!=12 or necc['new_width_record_admitted'] or necc['component_spans_are_flow_normal_widths']:
        raise ValueError('Changed paired-vector source scope')
    dependencies['analysis/build_necc_paired_vector_evidence.py']=necc['generator_sha256']
    figure=documents[NECC_BASE+'figure.json']
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for group in figure['figures'].values():
        for asset in group.values():dependencies[asset['file']]=asset['sha256']
    for source,pin in dependencies.items():
        if digest(source)!=pin:raise ValueError('Changed current research dependency '+source)
    eof=documents[EOF];section=documents[SECTION]
    local=section['cases'][2]['supported_local_core_diagnostics'][0]
    if local['span_km'] is None or section['cases'][0]['primary']['span_km'] is not None:
        raise ValueError('Changed Red Sea primary/follow-up meaning')
    if eof['current_association_verified'] or section['current_association_verified'] or section['fully_blinded_before_any_selected_velocity_exposure']:
        raise ValueError('Promoted current research interpretation')
    def link(label,document,pointer=''):return {'label':label,'document':document,'pointer':pointer}
    scenes=[{
        'current_id':'indian-south-equatorial-countercurrent',
        'label':'Indian South Equatorial Countercurrent',
        'diagnostic_id':'diagnostic:current-research:indian-south-equatorial-countercurrent',
        'title':'Seasonal patterns: classification evidence',
        'finding':'Two neighboring OSCAR columns over 1995–2016 show similar leading statistical patterns. The southern pattern peaks near 5°S, with an April maximum in its monthly coefficient climatology. This does not verify a named current or its physical edges.',
        'facts':[{'label':'Pattern-current association','value':'Not independently verified'},
            {'label':'Current width','value':'Unknown'},{'label':'Annual width range','value':'Unknown'},
            {'label':'Source coverage','value':'Two native columns · 1995–2016'}],
        'notes':['Five northern latitudes fail complete monthly support. Missing observations are not land or zero flow; the northern pattern peaks at the retained data edge.',
            'Latitude bands are paper classification context, not current boundaries. Principal-component coefficients are not local current speeds.',
            'Three latitude windows and both native columns remain separate. Similarity within one product is not independent validation or a confidence interval.',
            'Exact author domain/weighting/code were unavailable; this experiment is not an exact reproduction.'],
        'next_evidence':'Independent flow association and comparable transverse velocity sections before physical-width admission.',
        'figure_file':'figures/indian-secc-eof-feasibility.svg',
        'figure_alt':'Three statistical loading patterns and monthly coefficients at two native longitudes. Northern support is incomplete; no current width is admitted.',
        'source_file':EOF,'source_pointer':'','source_links':[
            link('Inspect all fits and comparisons',EOF),
            link('Inspect acquisition receipt','research/source-data/oscar-indian-eof-1995-2016/acquisition.json'),
            link('Inspect declared calculation','research/source-data/oscar-indian-eof-1995-2016/preflight.json')],
        'original_url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022JC019147',
        'table':{'caption':'Primary-window variance by native column; statistical patterns, not named-current widths.',
            'headers':['Native longitude','Mode 1','Mode 2','Mode 3'],
            'rows':[[f"{fit['longitude']:.3f}°E",*[f"{100*m['variance_fraction']:.1f}%" for m in fit['modes'][:3]]]
                for fit in eof['fits'] if fit['domain']==[-8,6]]}
    },{
        'current_id':'red-sea-saline-overflow','label':'Red Sea saline overflow',
        'diagnostic_id':'diagnostic:current-research:red-sea-saline-overflow',
        'title':'Observed section: a local core estimate',
        'finding':'Winter casts 7, 8 and 9 support a roughly 6 km half-peak southward-component section span in the layer 40–80 m above bottom. This local-core follow-up is separate from the unresolved primary calculation at 20–60 m. It does not establish a whole-current or flow-normal width.',
        'facts':[{'label':'Local section span','value':f"About {local['span_km']:.0f} km · 40–80 m above bottom"},
            {'label':'Primary 20–60 m result','value':'Unresolved'},
            {'label':'Whole-current width','value':'Unknown'},{'label':'Annual width range','value':'Unknown'}],
        'notes':['The local span covers only 1.67 native station spacings. The core vector is about 15.7° from the section normal; no cosine correction or precise physical-boundary claim is made.',
            'The 40% threshold remains unresolved. Finite velocity, boundary and layer scenarios are not combined into a confidence interval.',
            'A conditional value near 7.3 km in the 20–60 m layer uses excluded winter cast 10 and does not replace the primary unknown. Summer lacks comparable usable layer/reference support; it is not zero width or proof of an absent current.',
            'Original headers, reviewed metadata and filename-only cast joins remain distinct. The declaration-history note records prior incidental exposure to three cast 10 rows; no fully blinded preregistration is claimed.'],
        'next_evidence':'Resolve source processing, reference/tidal treatment, flow association and transverse resolution before physical-width admission; recover comparable repeated sections for seasonal ranges.',
        'figure_file':'figures/redsox-lower-nc-section-diagnostic.svg',
        'figure_alt':'Winter and summer layer velocity and salinity. A roughly 6 km secondary-layer local span is distinguished from unknown primary and summer outcomes.',
        'source_file':SECTION,'source_pointer':'','source_links':[
            link('Inspect all layers and null scenarios',SECTION),
            link('Inspect direct-current source inventory','research/redsox-ladcp-source-inventory.json'),
            link('Inspect hydrography and filename joins','research/redsox-ctd-companion-inventory.json'),
            link('Inspect reviewed source metadata','research/redsox-cruise-log-metadata-reconciliation.json'),
            link('Inspect declaration-history qualification','research/source-data/redsox-lower-nc-2001/declaration-history-note.json')],
        'original_url':'https://www.ncei.noaa.gov/archive/accession/0146147',
        'table':{'caption':'Two non-synoptic 2001 surveys; outcomes are section diagnostics, not annual current widths.',
            'headers':['Survey','Layer above bottom','Supported local half-peak span'],
            'rows':[[('18 Feb 2001' if case['campaign']=='RSX1' else '24 Aug 2001'),
                '–'.join(map(str,case['height_layer_m']))+' m',
                (f"About {case['supported_local_core_diagnostics'][0]['span_km']:.0f} km · follow-up" if case['supported_local_core_diagnostics'][0]['span_km'] is not None else 'Unresolved')]
                for case in section['cases']]}
    }]
    scenes.append({
        'current_id':'norwegian-coastal','label':'Norwegian Coastal Current',
        'diagnostic_id':'diagnostic:current-research:norwegian-coastal',
        'title':'Complete 2024 model year: monthly maps and sections',
        'finding':'All twelve months retain 8,784 hourly model fields at 10 m, with complete support at the 191 fixed section positions. This improves seasonal sampling in the offshore Ingoy region; the section is not a verified current axis or a current-width measurement.',
        'facts':[{'label':'Calendar coverage','value':'12 months · 8,784 hours'},
            {'label':'Model layer','value':'10 m · 2024'},
            {'label':'Current width','value':'Unknown'},{'label':'Annual width range','value':'Unknown'}],
        'notes':['Monthly means use all calendar hours, including leap day. Source spacing is 800 m; retained spacing is 3.2 km. Interpolated section positions add no native resolution.',
            'The 24/24/25-hour low-pass convolution attenuates tides and other high-frequency variability. It is not a harmonic tidal solution.',
            'Temporal standard deviations and sample quantiles describe model variability, not confidence intervals or current-width uncertainty. Serial dependence remains.',
            'This is a single model year at one layer, not observations, a climatology or a depth average. The offshore region does not establish coastal extent or physical current edges.',
            'The declaration records prior exposure to twelve isolated snapshots; no fully blinded preregistration is claimed. Modified Norkyst data: MET Norway / Institute of Marine Research, CC BY 4.0.'],
        'next_evidence':'Establish flow association and comparable paired physical boundaries before admitting a current width or annual width range.',
        'figure_file':'figures/norkyst-ingoy-complete-year-maps.svg',
        'figure_alt':'Twelve monthly low-pass model salinity maps at 10 m with mean velocity arrows and the fixed 24 degrees east section. These are regional model fields, not current boundaries.',
        'additional_figures':[
            {'file':'figures/norkyst-ingoy-complete-year-sections.svg','alt':'Monthly raw and low-pass mean salinity and velocity sections for all twelve months.'},
            {'file':'figures/norkyst-ingoy-complete-year-variability.svg','alt':'Monthly temporal model standard deviations, raw and low-pass. These are not uncertainty intervals.'}],
        'source_file':YEAR,'source_pointer':'','source_links':[
            link('Inspect monthly means, quantiles and support',YEAR,'/months'),
            link('Inspect complete-year acquisition',YEAR_ROOT+'acquisition-year.json'),
            link('Inspect figure provenance',YEAR_ROOT+'figure-year.json'),
            link('Inspect declared source and filtering rules',YEAR_ROOT+'preflight.json'),
            link('Inspect monthly regional means',YEAR_ROOT+'regional-monthly-means-year.json','/months')],
        'original_url':'https://thredds.met.no/thredds/catalog/romshindcast/norkyst_v3/zdepth/catalog.html',
        'table':{'caption':'Complete hourly section support in each calendar month of 2024; current width remains unknown.',
            'headers':['Month','Calendar hours','Current width'],
            'rows':[[f"2024-{month['month']:02d}",str(month['expected_month_hours']),'Unknown'] for month in year['months']]}
    })
    scenes.append({
        'current_id':'pacific-north-equatorial-countercurrent','label':'Pacific North Equatorial Countercurrent',
        'diagnostic_id':'diagnostic:current-research:pacific-north-equatorial-countercurrent',
        'title':'Paired surface-product vectors: direction and nearby columns',
        'finding':'Both velocity components are retained at 140 W and its two native neighbors. All twelve central monthly means and component spans reproduce the earlier calculation. Nine of 36 selected monthly peaks depart more than 15 degrees from east, reaching about 46 degrees. These are product diagnostics, not physical current widths.',
        'facts':[{'label':'Paired source support','value':'7,992 vectors · 3 native columns'},
            {'label':'Archive sampling','value':'72 timestamps · 2013'},
            {'label':'Physical current width','value':'Unknown'},{'label':'Annual width range','value':'Unknown'}],
        'notes':['This is archived satellite-derived OSCAR 2017.0 near-surface velocity, not direct instrument sections. Nominal depth coordinate 15 m is product context.',
            'Actual source times run from 1 January to 26 December 2013, including four six-day gaps. Equal-sample monthly means are not daily/time-weighted means or a climatology.',
            'Directions are derived from paired monthly-mean vectors, not averaged source-frame headings. No cosine correction turns the component spans into flow-normal widths.',
            'The 15-degree and two-native-cell attention guides are OSW choices, not admission limits or confidence intervals. Three months show larger peak-latitude separation between columns; same-product neighbors are not independent validation or measurement-error bounds.',
            'The 1/3-degree grid does not establish independent effective resolution. Cells outside the selected component, including westward flow, are not assigned to the named NECC.',
            'Target u was viewed before the new declaration. New v and neighboring velocity acquisition followed the declaration commit; no fully blinded or externally timestamped preregistration is claimed.'],
        'next_evidence':'Compatible independent velocity sections, verified named-flow association, source-error assessment and transverse physical edges before current width, annual ranges or mapped width admission.',
        'figure_file':'figures/necc-paired-2013-monthly-vector-sections.svg',
        'figure_label':'Monthly paired components',
        'figure_alt':'Monthly eastward and northward near-surface OSCAR fields at three native longitudes in 2013. Dots are selected component peaks, not a current axis or physical edges.',
        'additional_figures':[{'file':'figures/necc-paired-2013-direction-column-context.svg','label':'Direction and native-column context','alt':'Monthly peak directions and connected eastward-component spans across three native columns. Attention guides are not error bounds, annual ranges or flow-normal widths.'}],
        'source_file':NECC,'source_pointer':'','source_links':[
            link('Inspect paired source vectors','research/pacific-necc-paired-vector-source-inventory.json','/samples'),
            link('Inspect monthly paired profiles',NECC,'/rows'),
            link('Inspect vector acquisition',NECC_BASE+'acquisition.json'),
            link('Inspect declared paired-vector rules',NECC_BASE+'preflight.json')],
        'original_url':'https://oceanwatch.pifsc.noaa.gov/erddap/info/yearly_336c_0b32_9cd3/index.html',
        'table':{'caption':'140 W monthly product summaries. Component spans are not physical current widths; direction is from east, positive toward north.',
            'headers':['Month','Peak latitude','Direction from east','u=0 component span'],
            'rows':[[f"2013-{r['month']:02d}",f"{r['selected_peak_vector']['latitude']:.2f} N",f"{r['selected_peak_vector']['direction_degrees_from_east']:+.1f} degrees",f"{r['zero_crossing_component_span']['span_km']:.0f} km" if r['zero_crossing_component_span']['span_km'] is not None else 'Unresolved'] for r in necc['rows'] if r['source_longitude_degrees_east']==220]}
    })
    for scene in scenes:
        scene.update(kind='current_research_evidence',rank_eligible=False,new_width_record_admitted=False,
            whole_current_width_km=None,annual_width_range_km=None,
            geometry_role='research_evidence_no_current_axis_or_physical_width_geometry',
            figure_sha256=dependencies[scene['figure_file']])
    return {'schema':'osw.current-research-evidence-registry.v1',
        'status':'reviewed_research_evidence_pending_physical_measurement_admission',
        'documents':dict(sorted(FROZEN_INPUTS.items())),
        'input_sha256':dict(sorted(dependencies.items())),'scenes':scenes}


def verify():
    calculated=build();saved=json.loads((ROOT/PATH).read_bytes())
    if saved!=calculated:raise ValueError('Stale shared current research evidence registry')
    return saved


def record(scene,registry):
    path=scene['source_file'];raw=(ROOT/path).read_bytes()
    return {'id':scene['diagnostic_id'],'label':scene['label']+' research evidence',
        'entity_id':'current:'+scene['current_id'],'current_id':scene['current_id'],
        'status':registry['status'],'rank_eligible':False,'source_file':path,
        'source_file_sha256':digest(path),'source_json':raw.decode('utf8'),
        'document':json.loads(raw),'research_evidence':scene}


if __name__=='__main__':
    data=build();(ROOT/PATH).write_bytes((json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode())
    print(len(data['documents']),'source documents;',len(data['scenes']),'shared evidence scenes')
