"""Package audited JSON imports for the shared native/WASM Rust record store."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'almanac/query-data.json'
CANONICAL=['entities', 'sources', 'claims', 'relations', 'measurements', 'geometries', 'names', 'length_assessments', 'classification_vocabularies', 'named_eddy_footprint_candidates', 'footprint_movie_context', 'media', 'tiles', 'tile_state_relations', 'named_eddy_state_assessments', 'named_eddy_source_observations', 'named_current_source_observations', 'operational_eddy_state_observations', 'diagnosed_current_path_observations', 'observation_sets']

def build():
    inputs={}
    def read(path):
        raw=(ROOT/path).read_bytes();inputs[path]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    base='almanac/release/v0.1.0/'
    collections={name:read(base+name+'.json') for name in CANONICAL}
    read(base+'manifest.json')
    preview='almanac/release/v0.1.0-rights-screened-preview/'
    preview_manifest=read(preview+'manifest.json')
    if preview_manifest['source_manifest_sha256']!=inputs[base+'manifest.json']:raise ValueError('Stale screened preview parent')
    movies_receipts={}
    for name in ['manifest','tiles','tile_state_relations','media','entities']:
        path=preview+name+'.json';document=read(path)
        if name!='manifest':
            digest=next(r['sha256'] for r in preview_manifest['files'] if r['path']==name+'.json')
            if digest!=inputs[path]:raise ValueError('Changed screened movie input: '+path)
        movies_receipts[name]={'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')}
    dashboard=read('research/ocean-motion-dashboard.json')
    widths=read('research/ocean-current-width-inventory.json')
    from build_necc_chen_spread_scale import validate_inventory as validate_model_scale, OUTPUT as MODEL_SCALE
    validate_model_scale(widths)
    model_scale=read(MODEL_SCALE);read(model_scale['acquisition_file'])
    for path,pin in model_scale['input_sha256'].items():
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if actual!=pin:raise ValueError('Changed model axis-distance dependency: '+path)
        inputs[path]=actual
    inputs[model_scale['generator_file']]=hashlib.sha256((ROOT/model_scale['generator_file']).read_bytes()).hexdigest()
    gogp=read('research/persian-gulf-gogp99-geostrophic-scales-scope-audit.json')
    for source in [gogp,*gogp['supporting_originals']]:
        read(source['acquisition_file'])
        inputs[source['source_document_file']]=hashlib.sha256((ROOT/source['source_document_file']).read_bytes()).hexdigest()
    for path in [gogp['protocol_file'],'analysis/check_persian_gulf_geostrophic_scales.py','figures/persian-gulf-gogp99-geostrophic-scales.svg']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

    from check_loop_uhlhorn_core_width import validate_inventory as validate_loop_core, AUDIT as LOOP_CORE_AUDIT
    validate_loop_core(widths)
    loop_core_audit=read(LOOP_CORE_AUDIT)
    read(loop_core_audit['acquisition_file']);read(loop_core_audit['integrity_contract_file'])
    for path in [loop_core_audit['protocol_file'],'analysis/check_loop_uhlhorn_core_width.py','analysis/uhlhorn_thesis_source.py','analysis/melet_hal_source.py','figures/loop-uhlhorn-2008-core-width.svg']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_gulf_stream_published_widths import validate_inventory as validate_gulf, AUDIT as GULF_AUDIT
    validate_gulf(widths)
    gulf_audit=read(GULF_AUDIT)
    for source in gulf_audit['sources']:
        read(source['acquisition_file'])
        inputs[source['source_document_file']]=hashlib.sha256((ROOT/source['source_document_file']).read_bytes()).hexdigest()
    for path in [gulf_audit['protocol_file'],'analysis/check_gulf_stream_published_widths.py','figures/gulf-stream-published-width-definitions.svg']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    core=read('research/atlantic-seuc-molinari-1981-core-width-scope-audit.json');read(core['acquisition_file'])
    for path in [core['source_document_file'],core['protocol_file'],'analysis/check_atlantic_seuc_core_width.py','figures/atlantic-seuc-molinari-1981-core-width.svg']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    jet_audit = read('research/antarctic-slope-chavanne-2010-dated-width-constraint-scope-audit.json')
    for path in [jet_audit['protocol_file'], 'analysis/check_antarctic_slope_jet_constraint.py']:
        inputs[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    socib_audit = read('research/balearic-socib-2023-regional-width-scope-audit.json')
    read(socib_audit['acquisition_file'])
    for path in [socib_audit['source_document_file'], socib_audit['protocol_file'], 'analysis/check_balearic_socib_width.py']:
        inputs[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    coordinate_audit=read('research/azores-countercurrent-posaf-coordinate-meaning-audit.json')
    from build_azcc_coordinate_meaning_figure import validate as validate_coordinate_meaning
    validate_coordinate_meaning(coordinate_audit)
    read('research/source-data/carracedo-caibox-2012/acquisition.json')
    path='analysis/build_azcc_coordinate_meaning_figure.py'
    inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['research/azores-carracedo-2014-model-core-width-scope-audit.json','research/azores-carracedo-2014-climatological-core-width-record.json','research/source-data/carracedo-azores-2014/acquisition.json','research/source-data/woa09-season-definition/acquisition.json']:
        read(path)
    for path in ['analysis/check_azores_model_core_widths.py','analysis/build_azores_climatological_core_width_figure.py','plans/azores-model-core-width-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/somali-schott-2001-premonsoon-width-scope-audit.json');read('research/source-data/schott-mccreary-2001/acquisition.json')
    for path in ['research/source-data/schott-mccreary-2001/journal-article.pdf','plans/somali-seasonal-width-protocol-v1.md','analysis/check_somali_seasonal_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['research/california-2011-abstract-width-scope-audit.json','research/oyashio-2005-abstract-width-scope-audit.json']:
        read(path)
    inputs['analysis/check_abstract_regional_widths.py']=hashlib.sha256((ROOT/'analysis/check_abstract_regional_widths.py').read_bytes()).hexdigest()
    for path in ['research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json','research/source-data/kolas-fer-wsc-2018/acquisition.json']:
        read(path)
    for path in ['research/source-data/kolas-fer-wsc-2018/journal-article.pdf','plans/west-spitsbergen-stream-tube-width-protocol-v1.md','analysis/check_west_spitsbergen_stream_tubes.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_west_spitsbergen_selected_core import AUDIT as SELECTED_CORE_AUDIT, validate as validate_selected_core
    selected_core=validate_selected_core();read(SELECTED_CORE_AUDIT)
    for path in ['research/source-data/dundas-fer-wsc-2026/acquisition.json','research/source-data/dundas-fer-wsc-2026/figure.json','research/source-data/dundas-fer-wsc-2026/dataset-acquisition.json']:
        read(path)
    inputs.update(selected_core['input_sha256'])
    inputs[selected_core['protocol_file']]=selected_core['protocol_sha256']
    for path in ['analysis/check_west_spitsbergen_selected_core.py','analysis/build_west_spitsbergen_selected_core_figure.py','figures/west-spitsbergen-selected-core-width.svg','figures/west-spitsbergen-selected-core-width.png']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/ngcc-radenac-2016-seasonal-vein-width-scope-audit.json');read('research/source-data/radenac-ngcc-2016/acquisition.json')
    from check_southern_current_width_source_limits import AUDIT as SOURCE_LIMITS_AUDIT, verify as verify_source_limits
    source_limits=verify_source_limits();read(SOURCE_LIMITS_AUDIT)
    from current_research_evidence import PATH as RESEARCH_EVIDENCE_PATH, verify as verify_research_evidence
    research_evidence=verify_research_evidence();read(RESEARCH_EVIDENCE_PATH)
    for path in research_evidence['documents']:read(path)
    inputs.update(research_evidence['input_sha256'])
    inputs['analysis/current_research_evidence.py']=hashlib.sha256((ROOT/'analysis/current_research_evidence.py').read_bytes()).hexdigest()
    for source in source_limits['sources']:
        read(source['acquisition_file'])
        inputs[source['source_document_file']]=hashlib.sha256((ROOT/source['source_document_file']).read_bytes()).hexdigest()
    inputs['analysis/check_southern_current_width_source_limits.py']=hashlib.sha256((ROOT/'analysis/check_southern_current_width_source_limits.py').read_bytes()).hexdigest()
    from check_portugal_orca_section_span import AUDIT as PORTUGAL_AUDIT
    portugal_audit=read(PORTUGAL_AUDIT)
    read(portugal_audit['source_event_file'])
    for path in [portugal_audit['protocol_file'],portugal_audit['figure_file'],'analysis/check_portugal_orca_section_span.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_south_atlantic_secondary_band import AUDIT as SAC_AUDIT
    sac_audit=read(SAC_AUDIT);read(sac_audit['acquisition_file'])
    for path in [sac_audit['source_document_file'],sac_audit['protocol_file'],sac_audit['figure_file'],'analysis/check_south_atlantic_secondary_band.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_south_pacific_band_constraint import AUDIT as SPC_AUDIT
    spc_audit=read(SPC_AUDIT);read(spc_audit['acquisition_file'])
    for path in [spc_audit['source_document_file'],spc_audit['protocol_file'],spc_audit['figure_file'],'analysis/check_south_pacific_band_constraint.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from radenac_hal_source import integrity_inputs as radenac_inputs
    for path in radenac_inputs()+['plans/ngcc-seasonal-vein-width-protocol-v1.md','analysis/check_ngcc_seasonal_vein_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/pacific-secc-rotschi-1972-width-range-scope-audit.json');read('research/source-data/rotschi-secc-1972/acquisition.json')
    for path in ['research/source-data/rotschi-secc-1972/journal-article.pdf','plans/pacific-secc-historical-width-protocol-v1.md','analysis/check_pacific_secc_historical_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_current_width_inventory import validate
    from check_nordic_section_widths import SOURCES as NORDIC_SOURCES, NOR, WSC, proposed_records, validate_proposal, validate_inventory as validate_nordic_inventory
    for owner,(path,pin) in NORDIC_SOURCES.items():
        audit=read(path);read(audit['acquisition_file'])
        for dependency in [audit['source_document_file'],audit['protocol_file'],'analysis/check_nordic_section_widths.py',
                           'analysis/build_nordic_section_width_figures.py',
                           'figures/norwegian-fer-2020-section-width.svg' if owner==NOR else 'figures/spitsbergen-kolas-2018-section-widths.svg']:
            inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
    validate(widths,read('research/ocean-current-almanac.json'))
    validate_nordic_inventory(widths)
    validate_proposal(read('research/ocean-current-inventory-expansion-candidates.json'))
    collections['proposed_widths']=proposed_records()
    read('research/guinea-djakoure-2017-model-width-source-review.json');read('research/source-data/djakoure-guinea-2017/acquisition.json')
    for path in ['research/source-data/djakoure-guinea-2017/journal-article.pdf','plans/guinea-model-regional-width-protocol-v1.md','analysis/check_guinea_model_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_hiri_east_adriatic_local_widths import AUDITS as LOCAL_AUDITS
    for audit_file, _ in LOCAL_AUDITS.values():
        audit = read(audit_file)
        read(audit['acquisition_file'])
        for kind in ['source_document', 'protocol']:
            path = audit[kind+'_file']; inputs[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['analysis/check_hiri_east_adriatic_local_widths.py','analysis/build_hiri_east_adriatic_local_widths.py']:
        inputs[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/caribbean-duncan-1982-dated-width-scope-audit.json');read('research/source-data/duncan-caribbean-1982/acquisition.json')
    for path in ['research/source-data/duncan-caribbean-1982/journal-article.pdf','plans/caribbean-dated-width-protocol-v1.md','analysis/check_caribbean_dated_width.py','analysis/build_caribbean_dated_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/algerian-cotroneo-2019-regional-width-scope-audit.json');read('research/source-data/cotroneo-algerian-2019/acquisition.json')
    for path in ['research/source-data/cotroneo-algerian-2019/journal-article.pdf','plans/algerian-regional-width-protocol-v1.md','analysis/check_original_regional_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/alaska-weingartner-2002-regional-width-scope-audit.json');read('research/source-data/weingartner-alaska-2002/acquisition.json')
    for path in ['research/source-data/weingartner-alaska-2002/journal-article.pdf','plans/alaska-regional-width-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/pacific-euc-wang-2022-background-width-scope-audit.json');read('research/source-data/wang-pacific-euc-2022/acquisition.json')
    for path in ['research/source-data/wang-pacific-euc-2022/journal-article.pdf','plans/pacific-euc-background-width-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/atlantic-euc-gouriou-1988-background-width-scope-audit.json');read('research/source-data/gouriou-atlantic-1988/acquisition.json')
    for path in ['research/source-data/gouriou-atlantic-1988/source-book.pdf','plans/atlantic-euc-background-width-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json');read('research/source-data/sasaki-kuroshio-extension-2013/acquisition.json')
    for path in ['research/source-data/sasaki-kuroshio-extension-2013/journal-article.pdf','plans/kuroshio-extension-width-averaging-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    zeehan_width_audit=read('research/zeehan-cresswell-2000-width-section-scope-audit.json');read('research/source-data/cresswell-zeehan-2000/acquisition.json')
    for path in ['research/source-data/cresswell-zeehan-2000/journal-article.pdf','plans/zeehan-width-source-separation-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_pacific_neuc_isopycnal_breadths import document as neuc_document, AUDIT as NEUC_AUDIT
    neuc=neuc_document();read(NEUC_AUDIT)
    for kind in ['source_document','acquisition','protocol','source_figure_receipt']:
        path=neuc[kind+'_file'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for figure in neuc['source_figures']:
        path=figure['asset_file'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    inputs['analysis/check_pacific_neuc_isopycnal_breadths.py']=hashlib.sha256((ROOT/'analysis/check_pacific_neuc_isopycnal_breadths.py').read_bytes()).hexdigest()
    read('research/dwbc-richardson-1993-upper-core-width-scope-audit.json');read('research/source-data/richardson-dwbc-1993/acquisition.json')
    for path in ['research/source-data/richardson-dwbc-1993/journal-article.pdf','plans/dwbc-richardson-float-composite-width-protocol-v1.md','analysis/check_dwbc_float_composite.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json');read('research/source-data/schubert-aacc-2021/acquisition.json');read('research/source-data/schubert-aacc-2021/source-figure.json')
    for path in ['research/source-data/schubert-aacc-2021/journal-article.pdf','plans/antarctic-coastal-composite-width-protocol-v1.md','analysis/check_antarctic_coastal_composites.py','figures/schubert-aacc-2021-source-sections.png']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/tasman-front-nilsson-1980-meander-band-scope-audit.json');read('research/source-data/nilsson-tasman-1980/acquisition.json')
    for path in ['research/source-data/nilsson-tasman-1980/journal-article.pdf','plans/tasman-front-meander-band-protocol-v1.md','analysis/check_tasman_front_band.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/monsoon-webber-2018-distinct-widths-scope-audit.json');read('research/source-data/webber-monsoon-2018/acquisition.json')
    for path in ['research/source-data/webber-monsoon-2018/journal-article.pdf','plans/monsoon-webber-2018-width-protocol-v1.md','analysis/check_monsoon_webber_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/acc-park-2019-udintsev-breadths-scope-audit.json');read('research/source-data/park-acc-2019/acquisition.json')
    for path in ['research/source-data/park-acc-2019/journal-article.pdf','plans/acc-udintsev-breadths-protocol-v1.md','analysis/check_acc_udintsev_breadths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/north-pacific-tomczak-2005-broad-band-scope-audit.json');read('research/source-data/tomczak-regional-2005/acquisition.json')
    for path in ['research/source-data/tomczak-regional-2005/journal-article.pdf','plans/north-pacific-broad-band-protocol-v1.md','analysis/check_north_pacific_broad_band.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/solomon-melet-2010-coastal-confinement-scope-audit.json');read('research/source-data/melet-solomon-2010/acquisition.json')
    from melet_hal_source import integrity_inputs as melet_inputs
    for path in melet_inputs()+['plans/solomon-coastal-confinement-protocol-v1.md','analysis/check_solomon_coastal_confinement.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/jutland-nielsen-2000-cited-satellite-width-scope-audit.json');read('research/source-data/nielsen-jutland-2000/acquisition.json')
    for path in ['research/source-data/nielsen-jutland-2000/journal-article.pdf','plans/jutland-satellite-width-support-protocol-v1.md','analysis/check_jutland_satellite_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/jutland-skov-2019-water-mass-breadth-scope-audit.json');read('research/source-data/skov-jutland-2019/acquisition.json')
    for path in ['research/source-data/skov-jutland-2019/journal-article.pdf','plans/jutland-water-mass-breadth-protocol-v1.md','analysis/check_jutland_water_mass_breadth.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/western-adriatic-chavanne-2007-mean-width-scope-audit.json');read('research/source-data/chavanne-adriatic-2007/acquisition.json')
    for path in ['research/source-data/chavanne-adriatic-2007/journal-article.pdf','plans/western-adriatic-radar-width-support-protocol-v1.md','analysis/check_western_adriatic_mean_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/baffin-fissel-1982-regional-width-scope-audit.json');read('research/source-data/fissel-baffin-1982/acquisition.json')
    for path in ['research/source-data/fissel-baffin-1982/journal-article.pdf','plans/baffin-regional-width-support-protocol-v1.md','analysis/check_baffin_regional_widths.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/humboldt-fuenzalida-2008-regional-width-scope-audit.json');read('research/source-data/fuenzalida-humboldt-2008/text-review.json')
    for path in ['plans/humboldt-regional-width-support-protocol-v1.md','analysis/check_humboldt_width_descriptions.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    tsushima_modal_audit=read('research/tsushima-matsuyama-1990-modal-width-scope-audit.json');read('research/source-data/matsuyama-tsushima-1990/acquisition.json')
    read('research/west-australian-glenn-2008-breadth-scope-audit.json');read('research/source-data/glenn-wac-2008/acquisition.json')
    for path in ['research/source-data/glenn-wac-2008/journal-article.pdf','plans/west-australian-breadth-constraint-protocol-v1.md','analysis/check_west_australian_breadth.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['research/source-data/matsuyama-tsushima-1990/journal-article.pdf','plans/campaign-modal-decay-width-protocol-v1.md','analysis/check_tsushima_modal_width.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    read('research/ngcu-zenk-1999-width-constraint-scope-audit.json');read('research/source-data/zenk-ngcu-1999/acquisition.json');read('research/source-data/siedler-sonne-1997/acquisition.json')
    for path in ['research/source-data/zenk-ngcu-1999/journal-article.pdf','research/source-data/siedler-sonne-1997/journal-article.pdf','plans/ngcu-reported-width-constraint-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from build_current_measurement_scopes import verify as verify_measurement_scopes
    scope_index=verify_measurement_scopes()
    read('research/current-measurement-object-scope-index.json')
    read('research/ocean-current-scope-notes.json')
    for record in scope_index['records']:read(record['source_file'])
    inputs.update(scope_index['input_sha256'])
    inputs[scope_index['generator_file']]=scope_index['generator_sha256']
    inputs.update({r['figure_file']:r['figure_sha256'] for r in scope_index['records']})
    routes=read('research/ocean-current-reference-path-candidates.json')
    from build_current_reference_path_catalog import validate_source_receipt
    for route in routes['candidates']:
        inputs.update(validate_source_receipt(read(route['candidate_file'])))
    for record in widths['measurements']:
        if record.get('extraction_file'):
            extraction = read(record['extraction_file'])
            for dependency,pin in extraction.get('input_sha256',{}).items():
                actual=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
                if actual!=pin:raise ValueError('Changed cruise extraction dependency: '+dependency)
                inputs[dependency]=actual
            read(extraction['acquisition_file'])
            for dependency in [extraction['protocol_file'], extraction['generator_file'], *[s['file'] for s in json.loads((ROOT / extraction['acquisition_file']).read_bytes())['files']]]:
                inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            extra = extraction.get('additional_source_receipts')
            if extra:
                read(extra['acquisition_file'])
                for key in ['source_file', 'parser_file']:
                    inputs[extra[key]]=hashlib.sha256((ROOT/extra[key]).read_bytes()).hexdigest()
        context=record.get('eulerian_section_context') or record.get('width_statistics_context') or record.get('regional_range_context') or record.get('regional_scalar_context') or record.get('mean_offshore_context') or record.get('adcp_threshold_context')
        if context:
            audit=read(context['audit_file'])
            if audit.get('source_document_file'):
                path=audit['source_document_file']
                inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from published_section_transports import document as transport_document, build as transport_records, SOURCE as TRANSPORT_SOURCE
    transports=transport_document();read(TRANSPORT_SOURCE);read(transports['acquisition_file'])
    for path in [transports['source_document_file'],transports['protocol_file'],'analysis/published_section_transports.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    collections.update(transport_records(transports))
    collections['widths']=widths['measurements']
    collections['reference_routes']=routes['candidates']
    objects=copy.deepcopy(dashboard['entries'])
    for row in objects:row['dashboard_search']=row['label']+' '+row['basin']
    entity_index={e['id']:e for e in collections['entities']}
    sources={s['id'] for s in collections['sources']}
    from build_query_taxonomy import build as build_taxonomy
    collections['taxonomy_links'],taxonomy=build_taxonomy(objects,collections['entities'],read)
    inputs['analysis/build_query_taxonomy.py']=hashlib.sha256((ROOT/'analysis/build_query_taxonomy.py').read_bytes()).hexdigest()
    state_links=[]
    for row in objects:
        current=row['id'].removeprefix('current:')
        row['width_ids']=[w['id'] for w in collections['widths'] if w['current_id']==current]
        measures=[m for m in collections['measurements'] if m['entity_id']==row['id']]
        row['measurement_ids']=[m['id'] for m in measures]
        row['route_ids']=[r['id'] for r in collections['reference_routes'] if r['current_id']==current]
        source_ids={entity_index[row['id']].get('source_id')}
        source_ids.update(m.get('source_id') for m in measures)
        source_ids.update(c.get('source_id') for c in collections['claims'] if row['id'] in [c.get('subject_id'),c.get('object_id')])
        row['source_ids']=sorted(s for s in source_ids if s in sources)
        row['state_codes']=sorted({r['state_code'] for r in row['state_evidence']})
        lengths=[m['value'] for m in measures if m.get('rank_eligible') is True and m['quantity']=='reported_length']
        if len(lengths)>1:raise ValueError('Multiple ranked source lengths require explicit variant selection')
        row['published_length_km']=lengths[0] if lengths else None
        for i,relation in enumerate(row['state_evidence']):
            state_links.append({'id':f"query-state:{row['id']}:{i}",'entity_id':row['id'],'entity_label':row['label'],**relation})
    collections['objects']=objects
    recurrence_path='research/black-sea-eddy-recurrence.json'
    recurrence=read(recurrence_path)
    from build_black_sea_eddy_recurrence import validate as validate_recurrence
    validate_recurrence(recurrence)
    collections['eddy_recurrence']=recurrence['entries']
    for key in ['source_document_file','protocol_file','generator_file']:
        path=recurrence[key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    collections['state_links']=state_links
    collections['states']=[{**e,'code':e['id'].removeprefix('state:')} for e in collections['entities'] if e['type']=='osw_state']
    # Import the same coarse, land-masked OSW polygons as the existing state joins.
    from build_cartographic_current_state_join import load_states
    from shapely.geometry import mapping
    from shapely.ops import transform
    import shapely
    for path in ['figures/osw-province-atlas-interactive.svg', 'analysis/build_cartographic_current_state_join.py', 'analysis/build_motion_state_join.py', 'analysis/build_current_reference_path_candidate.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    state_shapes=load_states()
    for state in collections['states']:
        shape=state_shapes[state['code']]
        if not shape.is_valid or shape.is_empty:raise ValueError('Invalid masked state geometry')
        geographic=transform(lambda x,y,z=None:((x-60)*360/1480-180,90-(y-90)*180/740),shape)
        state['display_geometry']=json.loads(json.dumps(mapping(geographic)))
        state['geometry_scope']='Approximate OSW display-state polygons with coarse atlas land removed; not a physical ocean boundary.'
    # Source semantic exclusions remain attached to each route geometry.
    route_shapes={}
    from build_current_reference_path_candidate import display_coordinates
    for route in collections['reference_routes']:
        candidate=read(route['candidate_file'])
        if inputs[route['candidate_file']]!=route['candidate_sha256']:raise ValueError('Stale route candidate')
        route_shapes[route['id']]=candidate
    for row in objects:
        for feature in row['map_features']:
            matches=[g for g in collections['geometries'] if g['entity_id']==row['id'] and g['role']==feature['role'] and g['geometry']==feature['geometry']]
            if len(matches)==1:
                geometry=matches[0]
                feature['geometry_id']=geometry['id']
                for key in ['observation_date','coordinate_reference_system','coordinate_reference_status','positional_uncertainty','source_id','source_snapshot_id']:
                    if key in geometry:feature[key]=geometry[key]
            if feature.get('role')=='editorial_reference_route':
                matches=[route for route in collections['reference_routes'] if route['id'] in row['route_ids'] and route_shapes[route['id']]['coordinates_lon_lat']==feature['geometry']['coordinates']]
                if len(matches)!=1:raise ValueError('Ambiguous route geometry identity')
                route=matches[0];candidate=route_shapes[route['id']]
                feature['candidate_id']=route['id']
                feature['state_semantic_exclusions']=candidate.get('state_semantic_exclusions',[])
                points=display_coordinates(candidate['coordinates_lon_lat'],allow_seam=candidate.get('longitude_seam_policy')=='shortest_geodesic_periodic_display')
                feature['spatial_geometry']={'type':'LineString','coordinates':[[((x-60)*360/1480)%360-180,90-(y-90)*180/740] for x,y in points]}
                feature['spatial_geometry_method']='WGS84 geodesic legs densified at <=10 km as in the existing reference-route state join; planar relation to coarse masked OSW display polygons.'
    collections['series']=[{'id':f"query-series:{row['id']}:{i}",'entity_id':row['id'],**series} for row in objects for i,series in enumerate(row['series'])]
    # Seasonal source conventions are distinct from exact observation dates.
    seasonal_path='research/ocean-current-seasonal-route-frames.json'
    seasonal=read(seasonal_path)
    if inputs[seasonal['width_inventory_file']]!=seasonal['width_inventory_sha256']:raise ValueError('Stale seasonal width inventory')
    reports={}
    for phase in seasonal['frames']:
        reports[phase['route_candidate_file']]=read(phase['route_candidate_file'])
        if inputs[phase['route_candidate_file']]!=phase['route_candidate_sha256']:raise ValueError('Stale seasonal route')
    from check_current_seasonal_route_frames import validate as validate_seasonal
    validate_seasonal(seasonal,reports,widths)
    inputs['analysis/check_current_seasonal_route_frames.py']=hashlib.sha256((ROOT/'analysis/check_current_seasonal_route_frames.py').read_bytes()).hexdigest()
    collections['seasonal_routes']=[]
    for phase in seasonal['frames']:
        candidate=reports[phase['route_candidate_file']]
        entity_id='current:'+phase['current_id'];row=next(r for r in objects if r['id']==entity_id)
        comparison=next(c for c in seasonal['comparability'] if c['current_id']==phase['current_id'])
        record={**copy.deepcopy(phase),'entity_id':entity_id,'label':row['label']+' — '+phase['phase_label'],
                'status':seasonal['status'],'seasonal_inventory_file':seasonal_path,'seasonal_inventory_sha256':inputs[seasonal_path],
                'coordinates_lon_lat':copy.deepcopy(candidate['coordinates_lon_lat']),'comparability':copy.deepcopy(comparison)}
        collections['seasonal_routes'].append(record);row.setdefault('seasonal_route_ids',[]).append(record['id'])
        points=display_coordinates(candidate['coordinates_lon_lat'],allow_seam=candidate.get('longitude_seam_policy')=='shortest_geodesic_periodic_display')
        row['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(candidate['coordinates_lon_lat'])},
            'role':phase['geometry_role'],'phase_id':phase['id'],
            **{key:copy.deepcopy(record[key]) for key in ['phase_label','calendar_months','flow_direction','source_url','source_locator','time_convention','layer','route_candidate_sha256','seasonal_inventory_sha256','comparability']},
            'spatial_geometry':{'type':'LineString','coordinates':[[((x-60)*360/1480)%360-180,90-(y-90)*180/740] for x,y in points]},
            'state_semantic_exclusions':candidate.get('state_semantic_exclusions',[]),
            'spatial_geometry_method':'WGS84 geodesic legs densified at <=10 km; planar relation to coarse land-masked OSW display polygons. Source-defined seasonal regional editorial route, not an occupied footprint.',
            'note':phase['time_convention']+' '+comparison['reason']})
    # Import existing checked diagnostic frames without admitting them as current axes.
    from check_current_dated_timeline import validate as validate_timeline
    collections['geometry_frames']=[]
    for path in ['research/ocean-current-dated-timeline-2025.json','research/ocean-current-dated-timeline.json']:
        timeline=read(path)
        validate_timeline(timeline)
        for dependency in [timeline['audit_file'],'analysis/build_current_dated_timeline.py','analysis/check_current_dated_timeline.py','analysis/build_gulf_stream_geostrophic_path.py','analysis/build_loop_current_recorded_dates.py']:
            inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
        entity_id='current:'+timeline['current_id']
        row=next(r for r in objects if r['id']==entity_id)
        series=next(s for s in collections['series'] if s['entity_id']==entity_id and s['url']=='dated-current.html')
        for frame in timeline['frames']:
            frame_id=f"query-frame:{entity_id}:{frame['date']}:fixed-seed-geostrophic"
            for dependency in [frame['source_subset'],frame['figure']]:
                inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            record={'id':frame_id,'entity_id':entity_id,'series_id':series['id'],
                'label':f"{timeline['name']} — {frame['date']} frozen-field diagnostic",'status':timeline['status'],
                'timeline_file':path,'timeline_sha256':inputs[path],
                **{key:copy.deepcopy(timeline[key]) for key in ['layer','method','geometry_role','sampling_note','limitations','attribution','product_page','annual_extrema_eligible','annual_length_range_km','annual_width_range_km']},
                **copy.deepcopy(frame)}
            collections['geometry_frames'].append(record)
            row.setdefault('frame_ids',[]).append(frame_id)
            series.setdefault('frame_ids',[]).append(frame_id)
            row['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(frame['coordinates_lon_lat'])},
                'role':timeline['geometry_role'],'observation_date':frame['date'],'frame_id':frame_id,'series_id':series['id'],
                'source_url':frame['source_url'],'source_subset_sha256':frame['source_subset_sha256'],
                'source_response_sha256':frame['source_response_sha256'],'timeline_sha256':inputs[path],
                'source_algorithm':frame['source_algorithm'],'source_product_status':frame['source_product_status'],
                'coordinate_reference_system':'longitude_latitude_source_grid_with_WGS84_trace_integration',
                'coordinate_reference_status':'Trace integration uses WGS84; source grid datum is not independently resolved here.',
                'positional_uncertainty':None,
                'note':f"{timeline['sampling_note']} {timeline['limitations']} Stop: {frame['stop_reason']}. {timeline['attribution']}"})
    for series in collections['series']:
        if series.get('frame_ids') and len(series['frame_ids'])!=series['frames']:raise ValueError('Incomplete geometry frame series')
    collections['diagnostics']=[{'id':id,'document':read(path)} for id,path in [
        ('diagnostic:florida-monthly-width','research/florida-monthly-width-plot-extraction.json'),
        ('diagnostic:leeuwin-monthly-width','research/leeuwin-a101-monthly-plot-extraction.json'),
        ('diagnostic:kuroshio-seasonal-width','research/kuroshio-ecs-seasonal-width-profile-extraction.json'),
        ('diagnostic:necc-monthly-section','research/pacific-necc-oscar-2013-section-diagnostic.json'),
        ('diagnostic:antilles-observed-sections','research/antilles-ab0505-400m-section-diagnostic.json'),
        ('diagnostic:gulf-stream-widths','research/gulf-stream-section-width-series.json')]]
    collections['diagnostics'].append({'id':'diagnostic:gulf-stream-published-width-definitions',
        'label':'Gulf Stream transport-float occupations and historical isopycnal width',
        'entity_id':'current:gulf-stream','current_id':'gulf-stream','status':gulf_audit['status'],'rank_eligible':False,
        'source_file':GULF_AUDIT,'source_file_sha256':inputs[GULF_AUDIT],
        'source_json':(ROOT/GULF_AUDIT).read_bytes().decode('utf8'),'document':gulf_audit})
    collections['diagnostics'].append({'id':'diagnostic:uhlhorn-loop-core-width','label':'Loop Current prestorm fixed-speed geostrophic core',
        'entity_id':'current:loop','current_id':'loop','status':loop_core_audit['status'],'rank_eligible':False,
        'source_file':LOOP_CORE_AUDIT,'source_file_sha256':inputs[LOOP_CORE_AUDIT],
        'source_json':(ROOT/LOOP_CORE_AUDIT).read_bytes().decode('utf8'),'document':loop_core_audit})
    collections['diagnostics'].append({'id':'diagnostic:south-pacific-dated-band-constraint',
        'label':'South Pacific March 1990 relative-geostrophic band constraint',
        'entity_id':'current:south-pacific','current_id':'south-pacific','status':spc_audit['status'],'rank_eligible':False,
        'source_file':SPC_AUDIT,'source_file_sha256':inputs[SPC_AUDIT],
        'source_json':(ROOT/SPC_AUDIT).read_bytes().decode('utf8'),'document':spc_audit})
    collections['diagnostics'].append({'id':'diagnostic:south-atlantic-secondary-band',
        'label':'South Atlantic October 1983 southern component breadth',
        'entity_id':'current:south-atlantic','current_id':'south-atlantic','status':sac_audit['status'],'rank_eligible':False,
        'source_file':SAC_AUDIT,'source_file_sha256':inputs[SAC_AUDIT],
        'source_json':(ROOT/SAC_AUDIT).read_bytes().decode('utf8'),'document':sac_audit})
    collections['diagnostics'].append({'id':'diagnostic:portugal-orca-section-span',
        'label':'Portugal ORCA 2009 published-coordinate section span',
        'entity_id':'current:portugal','current_id':'portugal','status':portugal_audit['status'],'rank_eligible':False,
        'source_file':PORTUGAL_AUDIT,'source_file_sha256':inputs[PORTUGAL_AUDIT],
        'source_json':(ROOT/PORTUGAL_AUDIT).read_bytes().decode('utf8'),'document':portugal_audit})
    for review in source_limits['reviews']:
        owner=review['current_id']
        collections['diagnostics'].append({'id':'diagnostic:current-width-source-limits:'+owner,
            'label':owner+' current width source limitations','entity_id':'current:'+owner,'current_id':owner,
            'status':source_limits['status'],'rank_eligible':False,'source_file':SOURCE_LIMITS_AUDIT,
            'source_file_sha256':inputs[SOURCE_LIMITS_AUDIT],
            'source_json':(ROOT/SOURCE_LIMITS_AUDIT).read_bytes().decode('utf8'),'document':source_limits})
    from current_research_evidence import record as research_evidence_record
    for scene in research_evidence['scenes']:
        collections['diagnostics'].append(research_evidence_record(scene,research_evidence))
        owner=next(r for r in objects if r['id']=='current:'+scene['current_id'])
        owner['research_evidence_ids']=[scene['diagnostic_id']]
    florida_diagnostic=next(d for d in collections['diagnostics'] if d['id']=='diagnostic:florida-monthly-width')
    florida_path='research/florida-monthly-width-plot-extraction.json'
    florida_diagnostic.update(source_file=florida_path,source_file_sha256=inputs[florida_path],source_json=(ROOT/florida_path).read_bytes().decode('utf-8'))
    # Two same-day Loop experiments remain separate methods and unranked.
    from build_loop_current_dated_streamline import build as rebuild_loop_noaa
    from build_loop_current_adt_contours import build as rebuild_loop_adt
    loop_owner=next(r for r in objects if r['id']=='current:loop')
    loop_owner['diagnostic_ids']=[]
    loop_specs=[
        ('diagnostic:loop-noaa-20260925','research/loop-current-dated-streamline-20260925.json','Loop Current — NOAA velocity integration, 25 September 2026',rebuild_loop_noaa,'nominal','source_subset'),
        ('diagnostic:loop-adt-20260925','research/loop-current-adt-contours-20260925.json','Loop Current — DUACS ADT contour search, 25 September 2026',rebuild_loop_adt,'selected','source_file')]
    from build_loop_current_recorded_dates import build as rebuild_loop_series, source_rows, rebuild_noaa, rebuild_adt, path_for, OUTPUT as LOOP_SERIES
    from functools import partial
    series=read(LOOP_SERIES.relative_to(ROOT).as_posix())
    if series!=rebuild_loop_series():raise ValueError('Stale Loop repeat series')
    read(series['source_manifest'])
    for row in source_rows():
        for method,fn,key,source_key in [('noaa',rebuild_noaa,'nominal','source_subset'),('adt',rebuild_adt,'selected','source_file')]:
            stamp=row['date'].replace('-','')
            loop_specs.append((f'diagnostic:loop-{method}-{stamp}',path_for(method,row['date']).relative_to(ROOT).as_posix(),
                'Loop Current — '+('NOAA velocity integration' if method=='noaa' else 'DUACS ADT contour search')+', '+row['date'],partial(fn,row),key,source_key))
    for ident,path,label,rebuild,coordinates_key,source_key in loop_specs:
        document=read(path)
        if document!=rebuild():raise ValueError('Stale Loop diagnostic: '+ident)
        for key in [source_key,'protocol_file']:
            dependency=document[key];raw_hash=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
            expected=document['source_subset_sha256' if key=='source_subset' else 'source_sha256' if key=='source_file' else 'protocol_sha256']
            if raw_hash!=expected:raise ValueError('Stale Loop dependency: '+dependency)
            inputs[dependency]=raw_hash
        snapshot=read(document[source_key])
        record={'id':ident,'label':label,'entity_id':'current:loop','current_id':'loop',
            'observation_date':document['observation_date'],'status':document['status'],
            'rank_eligible':False,'source_file':path,'source_file_sha256':inputs[path],
            'diagnostic_page':'almanac/loop-current-experiment.html' if document['observation_date']=='2026-09-25' else 'almanac/loop-current-recorded-dates.html','source_url':document['source_url'],
            'scope':'Dated surface diagnostic between editorial gates. No whole-current length, width, annual range or independent observational confirmation.',
            'document':document,'source_json':(ROOT/path).read_bytes().decode('utf-8')}
        collections['diagnostics'].append(record);loop_owner['diagnostic_ids'].append(ident)
        selected=document[coordinates_key]
        if selected is not None and (coordinates_key=='selected' or selected['gate_connected']):
            frame_id='geometry-frame:'+ident.removeprefix('diagnostic:')
            role='frozen_field_diagnostic_streamline_not_current_axis_or_parcel_track' if coordinates_key=='nominal' else 'finite_ADT_contour_diagnostic_not_admitted_current_axis'
            frame={'id':frame_id,'entity_id':'current:loop','label':label,'date':document['observation_date'],
                'observation_date':document['observation_date'],'geometry_role':role,'diagnostic_id':ident,
                'coordinates_lon_lat':copy.deepcopy(selected['coordinates_lon_lat']),
                'rank_eligible':False,'source_url':document['source_url'],'status':document['status'],
                'scope':record['scope'],'diagnostic_page':record['diagnostic_page']}
            collections['geometry_frames'].append(frame);loop_owner.setdefault('frame_ids',[]).append(frame_id)
            loop_owner['map_features'].append({'geometry':{'type':'LineString','coordinates':copy.deepcopy(frame['coordinates_lon_lat'])},
                'role':role,'observation_date':frame['date'],'frame_id':frame_id,'diagnostic_id':ident,
                'source_url':document['source_url'],'source_subset_sha256':inputs[document[source_key]],
                'source_response_sha256':snapshot['source_response_sha256'],
                'source_algorithm':snapshot.get('source_algorithm',snapshot.get('source_metadata',{}).get('subset_datasetId')),
                'layer':document['layer'],'note':record['scope']+' '+document['interpretation']})
    for path in ['analysis/build_loop_current_dated_streamline.py','analysis/build_loop_current_adt_contours.py','analysis/build_gulf_stream_geostrophic_path.py','analysis/build_loop_current_recorded_dates.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_current_section_width_series import validate as validate_dated_widths
    dated_widths=next(d['document'] for d in collections['diagnostics'] if d['id']=='diagnostic:gulf-stream-widths')
    validate_dated_widths(dated_widths)
    for path in ['analysis/build_current_section_width_series.py','analysis/check_current_section_width_series.py','plans/gulf-stream-section-width-protocol-v1.md','plans/ocean-current-width-measurement-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for frame in dated_widths['frames']:
        path=frame['source_subset'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=frame['source_subset_sha256']:raise ValueError('Changed dated width source')
    from build_loop_current_section_spans import build as rebuild_loop_sections, output as loop_section_output
    for method in ['noaa','adt']:
        path=loop_section_output(method).relative_to(ROOT).as_posix();document=read(path)
        if document!=rebuild_loop_sections(method):raise ValueError('Stale Loop section span diagnostic')
        collections['diagnostics'].append({'id':f'diagnostic:yucatan-{method}-sections','label':f'Loop inflow — {method.upper()} fixed-section spans',
            'entity_id':'current:loop','current_id':'loop','status':document['status'],'rank_eligible':False,
            'source_file':path,'source_file_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8'),'document':document})
        for dependency in ['analysis/build_loop_current_section_spans.py',document['protocol_file']]:
            inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
    from build_basin_surface_section_spans import build as rebuild_basin, diagnostic_matches as basin_matches
    basin_inventory=read('research/basin-surface-section-inventory.json')
    for document in rebuild_basin():
        path='research/'+document['section_id']+'-2013-monthly-component-spans.json'
        original=read(path)
        if not basin_matches(original,document):raise ValueError('Stale basin section diagnostic')
        collections['diagnostics'].append({'id':'diagnostic:basin-'+document['section_id'],
            'label':document['current_id'].replace('-',' ').title()+' local monthly component spans (width unresolved)',
            'entity_id':'current:'+document['current_id'],'current_id':document['current_id'],'status':document['status'],'rank_eligible':False,
            'source_file':path,'source_file_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8'),'document':original})
        for key,value in original.items():
            if key.endswith('_file') and key.removesuffix('_file')+'_sha256' in original:
                inputs[value]=hashlib.sha256((ROOT/value).read_bytes()).hexdigest()
                if inputs[value]!=original[key.removesuffix('_file')+'_sha256']:raise ValueError('Stale basin source dependency')
    for path in ['analysis/build_basin_surface_section_spans.py','analysis/acquire_basin_surface_sections.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for name,receipt in basin_inventory['source_files'].items():
        path='research/source-data/oscar-basin-sections-2013/'+name
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=receipt['sha256']:raise ValueError('Changed basin original bytes')
    from build_south_australian_hycom_spans import build as rebuild_hycom
    path='research/south-australian-132e-100m-2012-monthly-component-spans.json'
    original=read(path);calculated=rebuild_hycom()
    if not basin_matches(original,calculated):raise ValueError('Stale HYCOM section diagnostic')
    collections['diagnostics'].append({'id':'diagnostic:basin-'+original['section_id'],
        'label':'South Australian local monthly component spans (width unresolved)',
        'entity_id':'current:south-australian','current_id':'south-australian','status':original['status'],'rank_eligible':False,
        'source_file':path,'source_file_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8'),'document':original})
    for key,value in original.items():
        if key.endswith('_file') and key.removesuffix('_file')+'_sha256' in original:
            inputs[value]=hashlib.sha256((ROOT/value).read_bytes()).hexdigest()
            if inputs[value]!=original[key.removesuffix('_file')+'_sha256']:raise ValueError('Stale HYCOM source dependency')
    for key,path in {'generator':'analysis/build_south_australian_hycom_spans.py','acquirer':'analysis/acquire_south_australian_hycom_section.py','operator':'analysis/build_basin_surface_section_spans.py'}.items():
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=original[key+'_sha256']:raise ValueError('Changed HYCOM operator')
    hycom_inventory=read(original['source_inventory_file']);read(hycom_inventory['acquisition_file'])
    for name,receipt in hycom_inventory['source_files'].items():
        path='research/source-data/hycom-south-australian-2012/'+name
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=receipt['sha256']:raise ValueError('Changed HYCOM original bytes')
    from build_west_australian_oscar_spans import build as rebuild_offshore
    path='research/west-australian-32s-2013-monthly-component-spans.json'
    original=read(path)
    if not basin_matches(original,rebuild_offshore()):raise ValueError('Stale offshore northward diagnostic')
    collections['diagnostics'].append({'id':'diagnostic:basin-'+original['section_id'],
        'label':'West Australian offshore monthly component spans (width unresolved)',
        'entity_id':'current:west-australian','current_id':'west-australian','status':original['status'],'rank_eligible':False,
        'source_file':path,'source_file_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8'),'document':original})
    for path,pin in original['input_sha256'].items():
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=pin:raise ValueError('Changed offshore source dependency')
    from check_indian_secc_oscar_climatology import saved as indian_saved, DOCUMENTS as INDIAN_DOCS, DATA as INDIAN_DATA
    from build_indian_secc_oscar_climatology import build as rebuild_indian
    indian_sections=indian_saved()
    if not basin_matches(read(INDIAN_DATA),rebuild_indian()):raise ValueError('Changed Indian SECC yearly/climatology reconstruction')
    for file,doc in zip(INDIAN_DOCS,indian_sections):
        original=read(file)
        collections['diagnostics'].append({'id':'diagnostic:basin-'+doc['section_id'],
            'label':doc['period_label']+' (current width unresolved)',
            'entity_id':'current:'+doc['current_id'],'current_id':doc['current_id'],'status':doc['status'],'rank_eligible':False,
            'source_file':file,'source_file_sha256':inputs[file],'source_json':(ROOT/file).read_bytes().decode('utf8'),'document':original})
        for path,pin in doc['input_sha256'].items():
            inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            if inputs[path]!=pin:raise ValueError('Changed Indian SECC source dependency')
        for path in [doc['profile_figure'],doc['interannual_figure']]:inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['analysis/check_indian_secc_oscar_climatology.py','analysis/build_indian_secc_climatology_figures.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_southern_basin_oscar_climatology import saved as southern_saved, DOCUMENTS as SOUTHERN_DOCS, DATA as SOUTHERN_DATA
    from build_southern_basin_oscar_climatology import build as rebuild_southern
    southern_sections=southern_saved()
    if not basin_matches(read(SOUTHERN_DATA),rebuild_southern()):raise ValueError('Changed southern-basin yearly/climatology reconstruction')
    for file,doc in zip(SOUTHERN_DOCS,southern_sections):
        original=read(file)
        collections['diagnostics'].append({'id':doc['diagnostic_id'],
            'label':doc['period_label']+' (current width unresolved)',
            'entity_id':'current:'+doc['current_id'],'current_id':doc['current_id'],'status':doc['status'],'rank_eligible':False,
            'source_file':file,'source_file_sha256':inputs[file],'source_json':(ROOT/file).read_bytes().decode('utf8'),'document':original})
        for path,pin in doc['input_sha256'].items():
            inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            if inputs[path]!=pin:raise ValueError('Changed southern-basin source dependency')
        for path in [doc['profile_figure'],doc['interannual_figure']]:inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for path in ['analysis/check_southern_basin_oscar_climatology.py','analysis/build_southern_basin_climatology_figures.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from build_query_width_samples import build as build_width_samples
    from build_antilles_sadcp_layer_spans import build as rebuild_shipboard, OUTPUT as SHIPBOARD, INPUT as SHIPBOARD_INPUT, SUBSET as SHIPBOARD_SUBSET
    shipboard=read(SHIPBOARD)
    from compare_shipboard_reconstruction import matches as shipboard_matches
    if not shipboard_matches(shipboard,rebuild_shipboard()):raise ValueError('Changed shipboard component-span reconstruction')
    for path in [SHIPBOARD,SHIPBOARD_INPUT,SHIPBOARD_SUBSET,'research/source-data/noaa-wbts-ab0505-sadcp/acquisition.json','analysis/build_antilles_sadcp_layer_spans.py','analysis/compare_shipboard_reconstruction.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    collections['observed_section_spans']=copy.deepcopy(shipboard['rows'])
    collections['diagnostics'].append({'id':'diagnostic:antilles-shipboard-layer-spans','label':'Antilles-region shipboard component spans','entity_id':'current:antilles','current_id':'antilles','status':shipboard['status'],'rank_eligible':False,'source_file':SHIPBOARD,'source_file_sha256':inputs[SHIPBOARD],'source_json':(ROOT/SHIPBOARD).read_bytes().decode('utf8'),'document':shipboard})
    next(r for r in objects if r['id']=='current:antilles')['observed_section_span_ids']=[r['id'] for r in shipboard['rows']]
    from build_leeuwin_monthly_plot import build as rebuild_leeuwin
    from build_kuroshio_seasonal_width_profiles import build as rebuild_kuroshio
    from build_pacific_necc_oscar_section_diagnostic import build as rebuild_necc, diagnostic_matches
    from build_florida_monthly_plot import build as rebuild_florida
    rebuilds={'diagnostic:florida-monthly-width':rebuild_florida,'diagnostic:leeuwin-monthly-width':rebuild_leeuwin,'diagnostic:kuroshio-seasonal-width':rebuild_kuroshio,'diagnostic:necc-monthly-section':rebuild_necc}
    for diagnostic in collections['diagnostics']:
        if diagnostic['id'] not in rebuilds:continue
        original=diagnostic['document'];calculated=rebuilds[diagnostic['id']]()
        matches=diagnostic_matches(original,calculated) if diagnostic['id']=='diagnostic:necc-monthly-section' else original==calculated
        if not matches:raise ValueError('Width diagnostic differs from pinned source reconstruction: '+diagnostic['id'])
        for key,path in original.items():
            if key.endswith('_file') and key.removesuffix('_file')+'_sha256' in original:
                actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                if actual!=original[key.removesuffix('_file')+'_sha256']:raise ValueError('Stale width diagnostic dependency: '+path)
                inputs[path]=actual
    for path in ['analysis/build_florida_monthly_plot.py','analysis/build_leeuwin_monthly_plot.py','analysis/build_kuroshio_seasonal_width_profiles.py','analysis/build_pacific_necc_oscar_section_diagnostic.py','analysis/acquire_pacific_necc_oscar_section.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    inputs['analysis/build_query_width_samples.py']=hashlib.sha256((ROOT/'analysis/build_query_width_samples.py').read_bytes()).hexdigest()
    from kuroshio_filtered_width import verify_inputs as verify_filtered_width, record as filtered_width_record, ID as FILTERED_WIDTH_ID
    filtered_document,filtered_figure,filtered_inputs=verify_filtered_width()
    inputs.update(filtered_inputs)
    collections['diagnostics'].append(filtered_width_record(filtered_document))
    filtered_owner=next(r for r in objects if r['id']=='current:kuroshio')
    filtered_owner.setdefault('diagnostic_ids',[]).append(FILTERED_WIDTH_ID)
    collections['width_samples']=build_width_samples(collections['diagnostics'])
    for row in objects:
        row['width_sample_ids']=[sample['id'] for sample in collections['width_samples'] if sample['entity_id']==row['id']]
        row['capabilities']['width_samples']=len(row['width_sample_ids'])
    # Keep the complete remaining-length worklist queryable without assigning
    # dimensions to unresolved names, families or continuity hypotheses.
    collections['route_decisions']=[]
    for original in routes['remaining_current_decisions']:
        entity_id='current:'+original['current_id']
        owner=next(row for row in objects if row['id']==entity_id)
        if sorted(original['candidate_ids'])!=sorted(owner['route_ids']):
            raise ValueError('Planning candidate IDs disagree with imported routes')
        reviews=[]
        for note in owner['scope_notes']:
            document=read(note['audit_file'])
            if document['current_id']!=original['current_id']:raise ValueError('Scope review owner mismatch')
            reviews.append({'note':copy.deepcopy(note),'document':document,'source_sha256':inputs[note['audit_file']]})
        record={'id':'route-decision:'+original['current_id'],'entity_id':entity_id,
                'label':original['name'],'current_id':original['current_id'],
                'strategy_id':original['route_strategy_id'],'strategy_label':original['route_strategy_label'],
                'construction_status':original['reference_path_decision'],
                'candidate_count':len(original['candidate_ids']),'route_ids':copy.deepcopy(original['candidate_ids']),
                'next_action':original['next_action'],'scope':original['existing_scope'],
                'status':original['planning_status'],'rank_eligible':False,
                'source_url':original['name_source_url'],'source_decision':copy.deepcopy(original),
                'source_catalog_file':'research/ocean-current-reference-path-candidates.json',
                'source_catalog_sha256':inputs['research/ocean-current-reference-path-candidates.json'],
                'scope_reviews':reviews}
        collections['route_decisions'].append(record)
        owner['route_decision_ids']=[record['id']]
    from build_flow_network import build as build_network, INPUT as NETWORK_INPUT
    read(NETWORK_INPUT.relative_to(ROOT).as_posix())
    network_collections=build_network();collections.update(network_collections)
    inputs['analysis/build_flow_network.py']=hashlib.sha256((ROOT/'analysis/build_flow_network.py').read_bytes()).hexdigest()
    network_owner=next(row for row in objects if row['id']=='current:indonesian-throughflow')
    network_owner['flow_network_ids']=[r['id'] for r in collections['flow_networks']]
    network_owner['passage_sample_ids']=[r['id'] for r in collections['passage_samples']]
    model_timeline=read('research/norkyst-ingoy-2024-section-timeline.json')
    model_maps=read('research/norkyst-ingoy-2024-map-frames.json')
    from check_norkyst_ingoy_timeline import validate as validate_model_timeline
    from check_norkyst_ingoy_maps import validate as validate_model_maps
    validate_model_timeline(model_timeline);validate_model_maps(model_maps,model_timeline)
    for document in [model_timeline,model_maps]:
        for kind in ['acquisition','generator','protocol','projection_helper']:
            if kind+'_file' not in document:continue
            path=document[kind+'_file'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            if inputs[path]!=document[kind+'_sha256']:raise ValueError('Stale model source provenance: '+path)
        for frame in document['frames']:
            for file_key,hash_key in [('receipt_file','receipt_sha256'),('figure','figure_sha256')]:
                if file_key not in frame:continue
                path=frame[file_key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                if inputs[path]!=frame[hash_key]:raise ValueError('Stale model frame support: '+path)
    from build_query_model_sections import build as build_model_sections, UNITS as MODEL_UNITS
    for frame in model_timeline['frames']:
        receipt=read(frame['receipt_file'])
        if {key:receipt['packing'][key]['units'] for key in MODEL_UNITS}!=MODEL_UNITS:
            raise ValueError('Changed model field units: '+frame['receipt_file'])
    collections.update(build_model_sections(model_timeline,model_maps,inputs))
    inputs['analysis/build_query_model_sections.py']=hashlib.sha256((ROOT/'analysis/build_query_model_sections.py').read_bytes()).hexdigest()
    model_owner=next(row for row in objects if row['id']=='current:norwegian-coastal')
    model_owner['model_frame_ids']=[row['id'] for row in collections['model_frames']]
    model_owner['capabilities']['model_frames']=len(collections['model_frames'])
    model_owner['capabilities']['model_samples']=len(collections['model_samples'])
    from build_antarctic_slope_m6_velocity import build as rebuild_velocity
    velocity_path='research/antarctic-slope-m6-velocity-series.json'
    velocity=read(velocity_path)
    from check_antarctic_slope_scope import validate as validate_slope, AUDIT as SLOPE_AUDIT, PAPER as SLOPE_PAPER
    slope_audit=read(SLOPE_AUDIT);validate_slope(slope_audit,widths)
    read('research/source-data/darelius-asc-2024/acquisition.json')
    inputs[SLOPE_PAPER]=hashlib.sha256((ROOT/SLOPE_PAPER).read_bytes()).hexdigest()
    inputs['analysis/check_antarctic_slope_scope.py']=hashlib.sha256((ROOT/'analysis/check_antarctic_slope_scope.py').read_bytes()).hexdigest()
    if velocity!=rebuild_velocity():raise ValueError('Stale M6 observed velocity aggregation')
    for key in ['source','protocol','generator']:
        path=velocity[key+'_file'];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=velocity[key+'_sha256']:raise ValueError('Changed M6 dependency: '+path)
    from build_asca_100m_sections import checked_packets as checked_asca
    _, asca_sections, asca_contract = checked_asca()
    del _
    asca_path=asca_contract['monthly_section_file']
    read('research/agulhas-asca-100m-query-contract.json')
    for file_key,hash_key in [('raw_profile_file','raw_profile_sha256'),('monthly_section_file','monthly_section_sha256'),('source_acquisition_file','source_acquisition_sha256'),('protocol_file','protocol_sha256'),('builder_file','builder_sha256')]:
        path=asca_contract[file_key];inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if inputs[path]!=asca_contract[hash_key]:raise ValueError('Changed ASCA section dependency: '+path)
    collections['current_sections']=asca_sections['frames']
    for row in objects:
        row['current_section_ids']=[r['id'] for r in asca_sections['frames'] if r['entity_id']==row['id']]
    collections['current_velocity_samples']=velocity['samples']
    for row in objects:
        row['velocity_sample_ids']=[r['id'] for r in velocity['samples'] if r['entity_id']==row['id']]
    for row in objects:
        for collection in ['section_transports','transport_validations']:
            owned=[r['id'] for r in collections[collection] if r['entity_id']==row['id']]
            if owned:row[collection+'_ids']=owned
    for name,rows in collections.items():
        if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate ID in '+name)
    from check_norwegian_atlantic_branch_widths import validate as validate_proposed_widths, AUDIT, ACQUISITION, SOURCE
    validate_proposed_widths(read('research/ocean-current-inventory-expansion-candidates.json'))
    read(AUDIT);read(ACQUISITION)
    inputs[SOURCE]=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
    inputs['analysis/check_norwegian_atlantic_branch_widths.py']=hashlib.sha256((ROOT/'analysis/check_norwegian_atlantic_branch_widths.py').read_bytes()).hexdigest()
    from check_astrid_radial_scales import validate as validate_astrid
    validate_astrid(read('research/astrid-2000-radial-scale-scope-audit.json'),read('research/named-eddy-geography.json'))
    read('research/source-data/van-aken-astrid-2003/acquisition.json')
    for path in ['research/source-data/van-aken-astrid-2003/journal-article.pdf','analysis/check_astrid_radial_scales.py']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from build_agulhas_ring_radius_audit import validate as validate_ring_radii
    validate_ring_radii(read('research/agulhas-guerra-2022-ring-radius-scope-audit.json'),read('research/named-eddy-geography.json'))
    read('research/source-data/guerra-agulhas-2022/acquisition.json')
    for path in ['research/source-data/guerra-agulhas-2022/journal-article.pdf','analysis/build_agulhas_ring_radius_audit.py','plans/agulhas-ring-radius-protocol-v1.md']:
        inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    from check_atlantic_euc_section_properties import validate as validate_atlantic_sections
    atlantic_path='research/atlantic-euc-layer-island-scope-audit.json'
    atlantic_audit=read(atlantic_path);validate_atlantic_sections(atlantic_audit)
    read(atlantic_audit['section_properties']['acquisition_file'])
    protocol=atlantic_audit['section_properties']['protocol_file']
    inputs[protocol]=hashlib.sha256((ROOT/protocol).read_bytes()).hexdigest()
    from check_zeehan_seasonal_calendar import PATH as calendar_path, validate as validate_calendar
    calendar_audit=validate_calendar(read(calendar_path))
    protocol=calendar_audit['protocol_file']
    inputs[protocol]=hashlib.sha256((ROOT/protocol).read_bytes()).hexdigest()
    from build_thor_ursa_source_panels import PATH as panel_path, validate as validate_panels
    panel_audit=validate_panels(read(panel_path));read(panel_audit['acquisition_file'])
    for dependency in [panel_audit['source_document_file'],panel_audit['protocol_file'],*[e['source_image_file'] for e in panel_audit['events']],'analysis/build_thor_ursa_source_panels.py']:
        inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
    from build_ursa_contour_candidate import PATH as contour_path, validate as validate_contour
    contour=validate_contour(read(contour_path))
    for stem in ['source_document','source_image','source_panel_audit','acquisition','state_geometry','protocol']:
        dependency=contour[stem+'_file']
        inputs[dependency]=hashlib.sha256((ROOT/dependency).read_bytes()).hexdigest()
    atlas_paths=[contour_path,panel_path,calendar_path,atlantic_path,'research/agulhas-guerra-2022-ring-radius-scope-audit.json','research/astrid-2000-radial-scale-scope-audit.json','research/ocean-current-inventory-expansion-candidates.json',
                 'research/ocean-current-reference-route-state-join.json',
                 'research/ocean-current-dated-timeline-2025.json',
                 'research/ocean-current-dated-timeline.json',
                 'research/antilles-ab0505-400m-section-diagnostic.json',
                 'research/leeuwin-a101-monthly-plot-extraction.json',
                 'research/kuroshio-ecs-seasonal-width-profile-extraction.json',
                 'research/pacific-necc-oscar-2013-section-diagnostic.json',
                 'research/gulf-stream-section-width-series.json',
                 'research/norkyst-ingoy-2024-section-timeline.json',
                 'research/norkyst-ingoy-2024-map-frames.json',
                 *[r['candidate_file'] for r in routes['candidates']]]
    atlas_receipts={}
    for path in atlas_paths:
        document=read(path)
        atlas_receipts[path]={'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')}
        if path.endswith('reference-route-state-join.json'):
            for dependency,digest in document['input_sha256'].items():
                read(dependency)
                if inputs[dependency]!=digest:raise ValueError('Stale atlas state join: '+dependency)
        if path.endswith('antilles-ab0505-400m-section-diagnostic.json'):
            read(document['inventory_file'])
            if inputs[document['inventory_file']]!=document['inventory_sha256']:raise ValueError('Stale observed-section inventory')
    return {'schema':'osw.query-bundle.v1','manifest':{'status':'local_editorial_and_canonical_snapshot_not_new_scientific_admission',
            'canonical_release':'v0.1.0','canonical_collections':CANONICAL,
            'eddy_recurrence_receipt':{'source_file':recurrence_path,'source_sha256':inputs[recurrence_path],'source_json':(ROOT/recurrence_path).read_bytes().decode('utf-8')},
            'atlas_receipts':atlas_receipts,
            'current_section_receipts':{asca_path:{'source_file':asca_path,'source_sha256':inputs[asca_path],'source_json':(ROOT/asca_path).read_bytes().decode('utf-8')}},
            'movies_receipts':movies_receipts,
            'loop_recorded_receipts':{path:{'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')} for path in ['research/loop-current-recorded-date-comparison.json','research/loop-current-recorded-date-sources.json']},
            'taxonomy':taxonomy,'editorial_collections':['proposed_widths','observed_section_spans','eddy_recurrence','taxonomy_links','objects','widths','reference_routes','state_links','states','series','geometry_frames','seasonal_routes','diagnostics','width_samples','route_decisions','flow_networks','flow_network_nodes','flow_network_edges','passage_samples','model_frames','model_samples','current_velocity_samples','current_sections','section_transports','transport_validations'],
            'seasons_receipts':{key:{'source_file':path,'source_sha256':inputs[path],'source_json':(ROOT/path).read_bytes().decode('utf-8')} for key,path in [('widths','research/ocean-current-width-inventory.json'),('routes','research/ocean-current-reference-path-candidates.json'),('frames','research/ocean-current-seasonal-route-frames.json'),('directions','research/new-guinea-coastal-current-seasonal-direction-scope-audit.json')]},
            'dashboard_receipt':{'source_file':'research/ocean-motion-dashboard.json','source_sha256':inputs['research/ocean-motion-dashboard.json'],'source_json':(ROOT/'research/ocean-motion-dashboard.json').read_bytes().decode('utf-8')},
            'input_sha256':inputs,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'state_geometry_runtime':{'shapely':shapely.__version__,'pyproj':__import__('pyproj').__version__},
            'scope':'State joins retain relation kinds; gateways are not containment. Widths retain scope. Published lengths and editorial route lengths are separate collections.'},
            'collections':collections}

def main():
    data=build();OUTPUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print('Built Rust query bundle:',{name:len(rows) for name,rows in data['collections'].items()})

if __name__=='__main__':main()
