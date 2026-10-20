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
ALEUTIAN='research/aleutian-p14n-1993-observed-vector-section.json'
ALEUTIAN_BASE='research/source-data/jasadcp-p14n-1993/'
ALEUTIAN_INPUTS={'research/aleutian-p14n-1993-observed-vector-section.json': 'c454ed7a8d1de2a83956d74b25dceeb88d2098b2ff339daeb46ea4c9d2415426', 'research/source-data/jasadcp-p14n-1993/acquisition.json': '1aac36510a4857b02f3adcebaf47fc0d97366b33e48943ae6fc16212ac921ae3', 'research/source-data/jasadcp-p14n-1993/figure.json': '6fcafc536355b9efbda6140624b840c3dca40c00529b2bb629b5768bdb5464ae'}
FROZEN_INPUTS.update(ALEUTIAN_INPUTS)
HYDRO='research/aleutian-p14n-1993-hydrography-correspondence.json'
HYDRO_BASE='research/source-data/cchdo-p14n-1993/'
HYDRO_INPUTS={'research/aleutian-p14n-1993-hydrography-correspondence.json': '6342f35f1a9f9affe71244eabd8e1dfe0bb7f46046bccf30eb564274cf202c04', 'research/source-data/cchdo-p14n-1993/acquisition.json': '6d9d9aad7a5e5fbe222bbdd00ca00b5d415aa0e75ed8a7def8aa19020e8d1b38', 'research/source-data/cchdo-p14n-1993/figure.json': 'eebdcea754f4b55098ce02022e183edb8db111e2f01834fd34282364e1e3cc78'}
FROZEN_INPUTS.update(HYDRO_INPUTS)
SPANS='research/aleutian-p14n-1993-component-spans.json'
SPAN_FIGURE='research/aleutian-p14n-1993-component-spans-figure.json'
SPAN_INPUTS={'research/aleutian-p14n-1993-component-spans.json': '9355c3dbc5ee86b6e50da63305e6498fbb8e3224bc67e08c097a5767efe10ebe', 'research/aleutian-p14n-1993-component-spans-figure.json': '240bfe1705d78af82d658bc279b10856a3a80cbe6055ff3c84e46849d321e895'}
FROZEN_INPUTS.update(SPAN_INPUTS)
NATIVE='research/aleutian-p14n-1993-native-vector-support.json'
NATIVE_META='research/aleutian-p14n-1993-native-product-metadata.json'
NATIVE_FIGURE='research/aleutian-p14n-1993-native-vector-support-figure.json'
NATIVE_BASE='research/source-data/jasadcp-p14n-1993-native/'
NATIVE_INPUTS={'research/aleutian-p14n-1993-native-vector-support.json': 'b41d6f82bc60475de67c3bfb6e596dad0f72a726034126ae67bbed29cfd82962', 'research/aleutian-p14n-1993-native-product-metadata.json': '6b5050ba8c1aeaf08667df95ad432c1ab5faa63b563b8161f40dbb3d3906c859', 'research/aleutian-p14n-1993-native-vector-support-figure.json': 'ed75dd87a5d508c54bad75dd23ff04f0203bd349e791ef7b06dc05e9a4231df6', 'research/source-data/jasadcp-p14n-1993-native/acquisition.json': 'be53aa8de06de0355ce4fa597a0a6250873f955ed863bdc408c883364c704bc1'}
FROZEN_INPUTS.update(NATIVE_INPUTS)
AVERAGES='research/aleutian-p14n-1993-underway-averages.json'
AVERAGE_FIGURE='research/aleutian-p14n-1993-underway-averages-figure.json'
AVERAGE_INPUTS={AVERAGES:'92d6d3fc8717b010051b0fbbd96fe3b3955f7a86b2e0cf87cd6b5ed74783d626',
    AVERAGE_FIGURE:'6a7aed03a752123e5eb1841c68ab5a92cac42b80b5426b81e104b03d4b470bd1'}
FROZEN_INPUTS.update(AVERAGE_INPUTS)
COMPOSITE='research/aleutian-p14n-1993-run-composite.json'
COMPOSITE_FIGURE='research/aleutian-p14n-1993-run-composite-figure.json'
COMPOSITE_INPUTS={COMPOSITE:'2438e75f6714d44352422727cdd6653cd3a316210b439485702a7654497e965b',
 COMPOSITE_FIGURE:'87a42f35d1db2470b73a4a75edae3afe8acf58b4a7dc6afc864c6c73739cb4b1'}
FROZEN_INPUTS.update(COMPOSITE_INPUTS)


LOOP_SOURCE='research/source-data/loop-durante-2026-v0/quality.json'
LOOP_VIEW='research/loop-durante-2026-source-view.json'
LOOP_FIGURE='research/loop-durante-2026-source-view-figure.json'
LOOP_ACQUISITION='research/source-data/loop-durante-2026-v0/acquisition.json'
FROZEN_INPUTS.update({LOOP_SOURCE:'af7ff4bc05a909aa84e5dab0125504f14affa0ecad369bbfda27ce00fd435959',
    LOOP_VIEW:'c7e2625677c6125138540ecc3d21cdf26756cc899603c358254be47dd4b8a7bc',
    LOOP_FIGURE:'0023a293a59149d0098ec732a8eeff1b32af3c1f80e56f8056e287b59e6b9889',
    LOOP_ACQUISITION:'2b01220d7880461e898a16b041ec749a9e2797d3611ac6122075bb6bd7bfc698'})

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    if len(FROZEN_INPUTS)!=50:raise ValueError('Missing reviewed research source registry')
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
    loop_figure=documents[LOOP_FIGURE]
    if loop_figure['source_view_sha256']!=digest(LOOP_VIEW):raise ValueError('Changed Loop source view/figure binding')
    dependencies.update(loop_figure['figures'])
    from acquire_loop_durante_2026 import verify as verify_loop_source
    _,loop_quality,_=verify_loop_source()
    if loop_quality!=documents[LOOP_SOURCE]:raise ValueError('Changed processed Loop source quality')
    if loop_quality['current_length_admitted'] or loop_quality['width_measurement_admitted']:
        raise ValueError('Promoted Loop source intake')
    for source,pin in dependencies.items():
        if digest(source)!=pin:raise ValueError('Changed current research dependency '+source)
    observed=documents[ALEUTIAN]
    from build_aleutian_p14n_vector_section import verify as verify_observed
    if observed!=verify_observed():raise ValueError('Changed observed vector section')
    dependencies[observed['generator_file']]=observed['generator_sha256']
    figure=documents[ALEUTIAN_BASE+'figure.json']
    if figure['source_file']!=ALEUTIAN or figure['source_sha256']!=digest(ALEUTIAN):raise ValueError('Changed observed figure source binding')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
    hydro=documents[HYDRO]
    from build_p14n_hydrography_companion import verify as verify_hydro
    if hydro!=verify_hydro() or hydro['velocity_section']!=observed:raise ValueError('Changed observed hydrography join')
    dependencies[hydro['generator_file']]=hydro['generator_sha256']
    figure=documents[HYDRO_BASE+'figure.json']
    if figure['source_file']!=HYDRO or figure['source_sha256']!=digest(HYDRO):raise ValueError('Changed hydrography figure source')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
    spans=documents[SPANS]
    from build_p14n_component_spans import verify as verify_spans
    if spans!=verify_spans() or spans['hydrography_context']!=hydro:raise ValueError('Changed measured component spans or original context')
    dependencies[spans['generator_file']]=spans['generator_sha256']
    figure=documents[SPAN_FIGURE]
    if figure['source_file']!=SPANS or figure['source_sha256']!=digest(SPANS):raise ValueError('Changed component-span figure source')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
    native=documents[NATIVE]
    from build_p14n_native_field_audit import verify as verify_native
    from build_p14n_native_metadata import verify as verify_native_metadata
    if native!=verify_native() or documents[NATIVE_META]!=verify_native_metadata():raise ValueError('Changed native source/field support')
    if native['new_width_record_admitted'] or native['current_association_verified'] or native['osw_temporal_ocean_velocity_averaging_applied']:raise ValueError('Promoted native support audit')
    native_observation_times=[row['ensemble_end_utc'] for row in native['profiles'] if row['layer_mean']['eastward_m_s'] is not None]
    dependencies[native['generator_file']]=native['generator_sha256']
    dependencies[documents[NATIVE_META]['generator_file']]=documents[NATIVE_META]['generator_sha256']
    figure=documents[NATIVE_FIGURE]
    if figure['source_file']!=NATIVE or figure['source_sha256']!=digest(NATIVE):raise ValueError('Changed native figure source')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
    from build_p14n_underway_averages import verify as verify_averages
    averages=documents[AVERAGES]
    if averages!=verify_averages():raise ValueError('Changed native underway averaging evidence')
    relative=[s for e in averages['experiments'] for b in e['branches'] for s in b['boundary_choice_scenarios']]
    velocity=[s for e in averages['experiments'] for b in e['branches'] for s in b['velocity_sensitivity_scenarios']]
    if len(relative)!=54 or len(velocity)!=72 or any(s['endpoint_separation_km'] is not None for s in relative+velocity):
        raise ValueError('Changed unresolved underway boundary result')
    if (not averages['osw_temporal_ocean_velocity_averaging_applied'] or averages['station_gaps_bridged']
        or averages['new_width_record_admitted'] or averages['seasonal_playback_supported']):
        raise ValueError('Promoted underway averages')
    dependencies[averages['generator_file']]=averages['generator_sha256']
    figure=documents[AVERAGE_FIGURE]
    if figure['source_file']!=AVERAGES or figure['source_sha256']!=digest(AVERAGES):raise ValueError('Changed averaging figure source')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
    from build_p14n_run_composite import verify as verify_composite
    composite=documents[COMPOSITE]
    if composite!=verify_composite():raise ValueError('Changed conditional run-composite evidence')
    if composite['temporal_comparability_verified'] or composite['new_width_record_admitted'] or composite['existing_no_bridge_result_replaced']:
        raise ValueError('Promoted conditional run composite')
    dependencies[composite['generator_file']]=composite['generator_sha256']
    figure=documents[COMPOSITE_FIGURE]
    if figure['source_file']!=COMPOSITE or figure['source_sha256']!=digest(COMPOSITE):raise ValueError('Changed composite figure source')
    dependencies[figure['generator_file']]=figure['generator_sha256']
    for asset in figure['figures'].values():dependencies[asset['file']]=asset['sha256']
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
    scenes.append({
        'current_id':'aleutian','label':'Aleutian / Subarctic Current',
        'diagnostic_id':'diagnostic:current-research:aleutian',
        'title':'July 1993 observed section: paired current velocities',
        'finding':'The July 1993 observations resolve local eastward-component spans of about 100 km in the northern branch window and 80 km in the southern window. Threshold-choice envelopes are 90–110 km and 60–90 km. Temporal crossings, velocity sensitivity and nearby eddy flow prevent treating these as verified physical current widths.',
        'facts':[{'label':'Observed sampling','value':'132 profiles · 13–18 July 1993'},
            {'label':'Joint vector support','value':'4,030 / 4,092 positions'},
            {'label':'Primary depth layer','value':'100–300 m'},
            {'label':'Supported layer means','value':'131 / 132 profiles'},
            {'label':'Companion hydrography','value':'17 casts · 84 candidate profile pairs'},
            {'label':'Local 50% component spans','value':'North ≈100 km · south ≈80 km'},
            {'label':'Complete declared scenarios','value':'14 / 14 resolved'},
            {'label':'Native regional support','value':'1,585 profiles · 1,582 layer means'},
            {'label':'Native underway eligibility','value':'568 profiles · 19 runs at ≥2 m/s'},
            {'label':'Native averaging boundary tests','value':'126 / 126 unresolved'},
            {'label':'Conditional run-composite tests','value':'18 / 126 sensitivity cases resolve; all nominal 50% cases unresolved'},
            {'label':'Physical current width','value':'Unknown'}],
        'notes':['Hourly archive means at 10 m depth levels are reduced products, not the native five-minute ensembles or four-metre acquisition bins.',
            'Layer means use midpoint cell thickness clipped to 100–300 m, joint u/v validity and at least 160 m valid support. Missing velocities remain missing; no vertical interpolation or component-to-speed substitution.',
            'The source track has 16 northward latitude steps and one two-hour gap. Points remain in acquisition order. The plot breaks the mean curve at the long gap; it does not silently fit a monotone current crossing.',
            'The paper places Subarctic branches near 42 N and 45 N. Fixed 41–43 N and 44–46 N windows are search context, not physical edges. The westward Alaskan Stream and Bering-side Aleutian North Slope Current are distinct.',
            'Provider metadata describe GPS selective availability, heading correction and CTD wire interference editing. Per-cell native editing history is not included in this reduced archive.',
            'One July 1993 transect is not a seasonal climatology or annual width range. No current-edge geometry, full width, uncertainty interval or seasonal playback is admitted. The separate 2013 OSCAR component diagnostic is retained.'],
        'next_evidence':'The separate declared run composite does not recover nominal half-peak boundaries under any tested gap cap. Eighteen other threshold cases resolve only under temporal-comparability assumptions and about 23 hours of bracketing observations. Independent repeated sections, branch/eddy attribution and transverse boundary support remain required; do not tune thresholds to replace the unresolved nominal result.',
        'figure_file':'figures/aleutian-p14n-1993-observed-vectors.svg',
        'figure_label':'Observed velocity section',
        'additional_figures':[{'file':'figures/aleutian-p14n-1993-hydrography-correspondence.svg','label':'CTD properties and pairing offsets','alt':'Measured in-situ ITS-90 temperature and PSS-78 salinity at 17 casts; QC2 cells and other quality codes distinguished; original velocity profiles and 84 candidate timing/distance offsets. No interpolated physical current edges.'},
            {'file':'figures/aleutian-p14n-1993-component-spans.svg','label':'Component spans and sensitivity','alt':'Both branch windows show actual vector means, half-peak crossings and native brackets; fourteen finite threshold and velocity scenarios remain separate. North about 100 km and south about 80 km are local component spans, not physical widths or annual ranges.'},
            {'file':'figures/aleutian-p14n-1993-native-vector-support.svg','label':'Native vectors and ship-motion support','alt':'Actual native observation latitude, ship-speed magnitude and both 100–300 m ocean velocity components against UTC ensemble end. Recorded CTD begin/end intervals and fixed ship-speed scenarios remain distinct. Source editing flags, gaps and uncertainty do not define physical current edges.'},
            {'file':'figures/aleutian-p14n-1993-underway-averages.svg','label':'Native averages: unresolved boundaries','alt':'Six panels compare northern and southern 100–300 m eastward means for fixed 30, 60 and 150 minute windows and all three ship-speed cutoffs. Horizontal bars are contributor latitude footprints, not uncertainty or edges. Hollow markers have less than 80% time coverage. All 54 relative-peak and 72 velocity-sensitivity scenarios remain unresolved. Station gaps are not bridged; no physical width or annual range is admitted.'},
            {'file':'figures/aleutian-p14n-1993-run-composite.svg','label':'Conditional run composite: gap assumptions','alt':'Whole-run eastward means and spatial footprints remain in source order. Dashed links assume temporal comparability across eligible gaps, not measured velocities inside them. The complete 126-case matrix retains all 18 unresolved nominal half-peak cases and 18 successful sensitivity cases under other thresholds. Successful northern spans of about 80–140 km use roughly 23 hours of bracketing observations; these are separate assumptions, not a physical width range or uncertainty interval.'}],
        'figure_alt':'Unconnected P14N sampling locations; observed eastward and northward velocity by latitude and depth; 100–300 m layer means with a gap break. Missing values are marked and no physical current boundaries are drawn.',
        'source_file':SPANS,'source_pointer':'',
        'observation_kind':'direct_shipboard_adcp_velocity',
        'observation_source_file':NATIVE,
        'observation_times_utc':[native_observation_times[0],native_observation_times[-1]] if native_observation_times else [],
        'support_source_sha256':{name:dependencies[name] for name in sorted(NATIVE_INPUTS)},
        'source_links':[
            link('Inspect conditional run-composite means and all assumptions',COMPOSITE),
            link('Inspect all run summaries, gap barriers and crossing cases',COMPOSITE,'/experiments'),
            link('Inspect conditional run-composite figure provenance',COMPOSITE_FIGURE),
            link('Inspect the unresolved native-averaging result',AVERAGES),
            link('Inspect all nine averaging experiments and boundary cases',AVERAGES,'/experiments'),
            link('Inspect native-averaging figure provenance',AVERAGE_FIGURE),
            link('Inspect native vector means and ship motion',NATIVE,'/profiles'),
            link('Inspect all three underway-run scenarios',NATIVE,'/run_sensitivity'),
            link('Inspect recorded CTD-event intervals',NATIVE,'/ctd_event_intervals'),
            link('Inspect native velocity-frame correspondence',NATIVE,'/frame_correspondence'),
            link('Inspect original native-product metadata',NATIVE_META),
            link('Inspect original native-product acquisition',NATIVE_BASE+'acquisition.json'),
            link('Inspect native-support figure provenance',NATIVE_FIGURE),
            link('Inspect component spans and all crossing brackets',SPANS,'/branches'),
            link('Inspect component-span figure provenance',SPAN_FIGURE),
            link('Inspect the joined hydrography and velocity record',HYDRO),
            link('Inspect all CTD casts and quality codes',HYDRO,'/casts'),
            link('Inspect candidate timing and position offsets',HYDRO,'/candidate_pairs'),
            link('Inspect original CTD acquisition',HYDRO_BASE+'acquisition.json'),
            link('Inspect all observed profiles',ALEUTIAN,'/profiles'),
            link('Inspect fixed branch windows and unresolved widths',ALEUTIAN,'/branches'),
            link('Inspect sampling gaps, spacing and bearings',ALEUTIAN,'/track_legs'),
            link('Inspect original archive acquisition',ALEUTIAN_BASE+'acquisition.json'),
            link('Inspect figure provenance',ALEUTIAN_BASE+'figure.json')],
        'original_url':'https://uhslc.soest.hawaii.edu/sadcp/DATABASE/00016.html',
        'table':{'caption':'Hourly-track eastward-component spans in fixed search windows. Sensitivity is boundary choice, not a confidence interval or annual range.',
            'headers':['Branch context','Search latitude','50% component span','40/50/60% envelope','Physical width'],
            'rows':[[row['branch'].title(),'–'.join(map(str,row['latitude_search_window_degrees_north']))+' N','≈'+str(row['boundary_choice_scenarios'][1]['display_endpoint_separation_km'])+' km','–'.join(map(str,row['complete_boundary_choice_envelope_km']))+' km','Unknown'] for row in spans['branches']]}
    })
    scenes[-1]['additional_tables']=[{
        'caption':'Native averaging support across the full 40–48 N reach. Counts are retained bins, not boundary support inside either branch. Every experiment has 6 relative-peak and 8 velocity-sensitivity cases across both branches; none resolve two crossings.',
        'headers':['Minimum ship speed (m/s)','Window (minutes)','All retained bins','Bins with ≥80% coverage','Resolved boundary cases'],
        'rows':[[str(e['ship_speed_cutoff_m_s']),str(e['averaging_minutes']),
            str(sum(len(r['bins']) for r in e['runs'])),
            str(sum(b['boundary_eligible_coverage'] for r in e['runs'] for b in r['bins'])),'0 / 14'] for e in averages['experiments']]}]
    scenes[-1]['notes'].extend([
        'A separate whole-run composite explicitly tests interpolation between summary positions under 3/6/12 hour gap caps, a 25 km unobserved-distance cap and unchanged source-order/quality barriers. All 18 nominal half-peak cases remain unresolved. Only northern 60% and positive threshold-offset cases resolve with 6/12 hour caps: 18 of 126 cases. Their about 80–140 km separations are different assumptions, not a width range. Their full bracketing observations span about 23 hours; temporal comparability and physical branch identity remain unverified. This does not replace the earlier no-bridge negative result.',
        'A separate exploratory OSW operator averages native supported layer means within each contiguous underway run, using fixed 30/60/150 minute windows and 1/2/3 m/s ship-speed cutoffs. Overlapping ensemble time is counted once and boundary analysis requires at least 80% of the full window duration. All 54 relative-peak and 72 velocity-sensitivity cases lack two resolved crossings. No station gap is bridged; run ends and incomplete windows cannot substitute for boundaries.',
        'The separate native products retain 1,585 regional ensemble profiles and 190,200 depth cells in their original files. There are 1,582 supported 100–300 m means and 182,081 jointly finite unflagged vectors. CODAS editing bits are distinct from CTD WOCE quality codes.',
        'Fixed ship-speed eligibility at 1/2/3 m/s gives 623/568/532 profiles in 42/19/19 contiguous runs. Every run remains available, including short ones. Source gaps, missing support and ineligible profiles break runs; no latitude sorting or station-gap bridge is applied.',
        'All 685 profiles whose nominal ensemble intervals overlap recorded CTD BE–EN events fall outside the ≥2 m/s eligibility class. This event/speed agreement is context, not proof of depth-specific simultaneity or a new CTD-wire interference flag.',
        'Short-product ocean velocities already include ship motion; numerical correspondence with the long relative-water/absolute-ship fields is checked. Actual ensemble durations are 300 seconds; timestamps and positions refer to ensemble end, and depths are nominal bin centres. OSW applies no further temporal ocean-velocity averaging in this audit.',
        'All 14 declared component scenarios resolve within the original fixed windows. Nominal half-peak endpoint separations are about 100 km north and 80 km south; 40/50/60% envelopes are 90–110 km and 60–90 km, not error bounds or annual ranges.',
        'The northern first crossing bracket spans only 0.34 km in one hour near a CTD occupation. Nominal bracketing observations span about 13 hours north and 14 hours south. Temporal change can masquerade as a spatial edge.',
        'Separate ±0.02 and ±0.06 m/s threshold-comparator scenarios yield roughly 43–152 km north and 56–90 km south. They explore GPS-related hourly velocity sensitivity; they are not a total error budget or a confidence interval. No rotation to a flow-normal width is applied.',
        'Companion CCHDO hydrography retains 17 casts and all 84 qualifying cast-to-hourly-profile pairs within three hours of nominal cast-bottom time and 15 km. No nearest-only selection or interpolation is applied. Forty-eight hourly velocity profiles have no qualifying pair.',
        'All 17 nominal timestamps agree with unique BO (bottom) events in the original station log. This does not establish simultaneous sampling at 100–300 m. Cast beginning/end events and actual offsets remain inspectable.',
        'Of 3,009 upper-ocean property cells, 2,525 meet joint WOCE QC2. Raw edited/despiked code7 and questionable code3 values remain available; other codes are not silently relabeled missing or acceptable.',
        'Temperature is in-situ ITS-90; salinity is practical PSS-78. Pressure is retained in dbar beside depth converted with GSW3.6.23. The source-history temperature-correction notice remains unresolved and is not reapplied.'])
    composite_rows=[]
    for experiment in composite['experiments']:
        for cap in [3,6,12]:
            cases=[c for c in experiment['cases'] if c['maximum_unobserved_time_gap_hours']==cap]
            values=[c['scenarios'][1]['rounded_endpoint_separation_km'] for c in cases]
            resolved=sum(s['endpoint_separation_km'] is not None for c in cases for s in c['scenarios'])
            composite_rows.append([str(experiment['ship_speed_cutoff_m_s']),str(cap),
                *['Unresolved' if v is None else f'{v} km, conditional' for v in values],f'{resolved} / 14'])
    scenes[-1]['additional_tables'].append({
        'caption':'Conditional run composite: all northern and southern nominal 50% spans remain unresolved. The resolved-case count includes other thresholds under explicit gap assumptions; cases are not independent observations and their separations are not a physical width range.',
        'headers':['Minimum ship speed (m/s)','Maximum unobserved gap (h)','North nominal 50%','South nominal 50%','Resolved sensitivity cases'],
        'rows':composite_rows})
    scenes.append({
        'current_id':'loop','label':'Loop Current','diagnostic_id':'diagnostic:current-research:loop',
        'title':'Author surface composites and source coverage',
        'finding':'Two processed surface-flow configurations are available. The supplied coordinate means extend through the Caribbean toward Yucatan; they are not complete Loop Current paths. No length or width is admitted.',
        'facts':[{'label':'Processed surface configurations','value':'2 conditional composites'},
                 {'label':'Source clocks','value':'4,111 / 4,111 / 11,902 entries'},
                 {'label':'Coordinate points','value':'248 per composite; unjoined'},
                 {'label':'Complete Loop path','value':'Not supplied'}],
        'notes':['These are author-processed MCA phase composites, not dated snapshots, seasons or forecasts. Original daily Canek/CMEMS observations are not supplied in this compact archive.',
                 'The two coordinate means were formed with omitnan. Daily member coordinates and per-point support counts are unavailable; no full Loop axis or length is inferred.',
                 'The three source clocks are distinct. One tisp entry is missing at zero-based OSW position3462 (MATLAB index3463); it is not filled from tid. Original phase/grid selection indices remain one-based MATLAB indices. Calendar timezone is unspecified, and dates are source clocks rather than new current observations.',
                 'The area_loop and AMR_loop scalars remain unscaled under their original names. No width, length or occupied-current polygon is inferred from enclosed-area metrics.',
                 'The source API declares CC BY4.0 and version0. README retains a license-selection TODO, CITATION.cff says1.0.0, and the associated manuscript DOI is a placeholder; these documentary disagreements remain visible.'],
        'next_evidence':'Recover complete daily Loop axes or a validated gateway-connected algorithm before route/length admission; establish exact composite-member support before physical interpretation.',
        'figure_file':'figures/loop-durante-2026-source-view.svg',
        'figure_alt':'Two native-grid geostrophic-speed composites with direction arrows and all248unjoined coordinate means each, plus three separate source-clock coverage rows. Gray means missing source data. Coordinate means end below23.2N and do not form a complete Loop Current. No dimensions are admitted.',
        'source_file':LOOP_SOURCE,'original_url':'https://zenodo.org/records/22652650',
        'source_links':[link('Exact source schema and quality',LOOP_SOURCE),link('Exact composite fields and masks',LOOP_VIEW,'/phases'),
                        link('All original clocks',LOOP_VIEW,'/clocks'),link('Unscaled source area scalars',LOOP_VIEW,'/source_scalar_series'),
                        link('Source custody and release notes',LOOP_ACQUISITION)],
        'table':{'caption':'Source clocks are not dates of complete current paths. Missing clocks remain missing; no timezone is inferred.',
                 'headers':['Original clock','Source entries','Finite calendar support','Missing times'],
                 'rows':[[name,str(clock['records']),clock['first_finite_calendar'][:10]+' to '+clock['last_finite_calendar'][:10],str(clock['nonfinite'])] for name,clock in loop_quality['times'].items()]},
        'additional_tables':[{'caption':'Supplied coordinate means are incomplete for a full Loop path. Bounds describe source points, not current extent or uncertainty.',
                 'headers':['Original field','Paired finite points','Northernmost point','Full Loop path'],
                 'rows':[[name,str(axis['paired_finite_rows']),f"{axis['latitude_bounds'][1]:.2f} N",'Not supplied'] for name,axis in loop_quality['source_composite_axes'].items()]}]
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
