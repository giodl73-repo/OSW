"""Typed projection of the frozen axis-normal model source; no physical admission."""
import json
import kuroshio_axis_normal as source
import kuroshio_wang_query as prior

ROOT=source.ROOT
FILE='research/kuroshio-wang-2024-axis-normal-query-contract.json'
PROTOCOL='plans/kuroshio-axis-normal-query-atlas-protocol-v1.md'
OPERATOR='analysis/kuroshio_axis_normal_query.py'
FIGURE_RECEIPT='research/kuroshio-wang-2024-axis-normal-figure.json'
COLLECTION='current_axis_normal_samples'
ID='diagnostic:kuroshio-wang-2024-axis-normal-spans'
SOURCE_ID=prior.SOURCE_ID


def samples(doc):
    return [{'id':r['id'],'entity_id':'current:kuroshio','current_id':'kuroshio',
        'sample_date':r['sample_date'],'source_level':r['source_level'],'nominal_depth_m':r['nominal_depth_m'],
        'section_latitude':r['latitude'],'tangent_half_window_km':r['tangent_half_window_km'],
        'is_primary_convention':r['tangent_half_window_km']==14,'quantity':'axis_normal_model_boundary_span',
        'status':r['status'],'value_km':r['span_km'],'report_case_index':i,
        'source_id':SOURCE_ID,'diagnostic_id':ID,'evidence_class':'model_derived',
        'rank_eligible':False,'physical_width_inventory_admitted':False,'velocity_normal_verified':False,
        'ocean_connectivity_verified':False,'uncertainty_km':None,'boundary_fallback_occurred':None,
        'threshold_attained':None,'exceeds_source_nominal_140km_transect':r.get('exceeds_source_nominal_140km_transect')}
        for i,r in enumerate(doc['cases'])]


def record(doc):
    return {'id':ID,'label':'Kuroshio2024 axis-normal model spans and sample ranges',
        'entity_id':'current:kuroshio','current_id':'kuroshio','rank_eligible':False,
        'source_file':source.FILE,'source_file_sha256':source.base.digest(source.FILE),
        'source_json':(ROOT/source.FILE).read_text(encoding='utf-8'),
        'summary':{key:doc[key] for key in ['counts','status_counts','primary_status_counts','metric','numerical_readback']}}


def build():
    doc=source.verify_inputs();figure=json.loads((ROOT/FIGURE_RECEIPT).read_bytes())
    for path,pin in figure['input_sha256'].items():
        if source.base.digest(path)!=pin:raise ValueError('Changed normal figure input: '+path)
    if source.base.digest(source.FIGURE)!=figure['figure_sha256']:raise ValueError('Changed normal figure')
    old=json.loads((ROOT/prior.FILE).read_bytes())
    paths=[source.FILE,source.FIGURE,FIGURE_RECEIPT,PROTOCOL,OPERATOR,prior.FILE]
    return {'schema':'osw.kuroshio-axis-normal-query-contract.v1','version':'1',
        'source_report_file':source.FILE,'source_report_sha256':source.base.digest(source.FILE),
        'sample_collection':COLLECTION,'sample_count':16470,'diagnostic_id':ID,
        'source_record':old['source_record'],'manifest_flag':'kuroshio_axis_normal_version',
        'input_sha256':{**doc['input_sha256'],**figure['input_sha256'],**{p:source.base.digest(p) for p in paths}},
        'scope':'Regional model-axis-normal geometry; velocity normal, ocean connectivity, fallback and physical uncertainty unverified. Sample ranges are not physical annual bounds or climatology.',
        'sample_id_rule':'Scientific source edition/date/depth/gate/tangent-window/operator ID; row ordinal is only a snapshot-scoped report pointer.'}


def verify_inputs():
    contract=json.loads((ROOT/FILE).read_bytes())
    if contract!=build():raise ValueError('Stale normal query contract')
    return contract,source.verify_inputs()


if __name__=='__main__':
    (ROOT/FILE).write_bytes(source.encoded(build()))
    print('Built axis-normal query contract:16470 attempts; no inventory promotion.')
