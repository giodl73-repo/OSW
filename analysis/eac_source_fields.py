"""Bind EAC source quality and lazy source-query records to the Rust UI."""
from pathlib import Path
import json
from acquire_eac_100m_source import ROOT,sha
from check_eac_100m_source import REPORT,build as quality
from build_eac_source_profiles import OUTPUT,CONTRACT,verify

ID='diagnostic:eac-csiro100m-source-fields'
FIGURE='research/eac-csiro-v23-100m-source-fields-figure.json'


def verify_inputs():
    document=json.loads((ROOT/REPORT).read_bytes())
    if document!=quality():raise ValueError('Stale EAC source quality')
    _,contract=verify();figure=json.loads((ROOT/FIGURE).read_bytes())
    if figure['source_file']!=REPORT or figure['source_sha256']!=sha(ROOT/REPORT):raise ValueError('Stale EAC source figure')
    if figure['physical_width_admitted'] is not False or figure['provider_uncertainty_reinterpreted_as_confidence_interval'] is not False:
        raise ValueError('Promoted EAC source figure')
    helper=Path(__file__).relative_to(ROOT).as_posix()
    inputs={**contract['input_sha256'],OUTPUT:contract['raw_profile_sha256'],CONTRACT:sha(ROOT/CONTRACT),
        FIGURE:sha(ROOT/FIGURE),figure['generator_file']:figure['generator_sha256'],helper:sha(ROOT/helper)}
    for asset in figure['figures'].values():inputs[asset['file']]=asset['sha256']
    for path,pin in inputs.items():
        if sha(ROOT/path)!=pin:raise ValueError('Changed EAC source-view input: '+path)
    return document,contract,figure,inputs


def record(document):
    return {'id':ID,'label':'East Australian Current daily100m source fields','entity_id':'current:east-australian',
        'current_id':'east-australian','status':document['status'],'rank_eligible':False,'source_file':REPORT,
        'source_file_sha256':sha(ROOT/REPORT),'source_json':(ROOT/REPORT).read_bytes().decode('utf8'),'document':document}
