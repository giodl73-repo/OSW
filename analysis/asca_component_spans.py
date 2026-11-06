"""Verified diagnostic/source projection for the dated ASCA component experiment."""
from pathlib import Path
import json
from build_asca_component_spans import ROOT, REPORT, OPERATOR, digest, verify

ID = 'diagnostic:agulhas-asca100m-component-spans'
FIGURE = 'research/agulhas-asca-100m-dated-component-spans-figure.json'


def verify_inputs():
    document = verify(); figure = json.loads((ROOT/FIGURE).read_bytes())
    if figure['source_file'] != REPORT or figure['source_sha256'] != digest(REPORT):
        raise ValueError('Stale ASCA component figure source')
    if any(figure[k] is not False for k in ['physical_edges_rendered', 'source_uncertainty_inferred', 'annual_extrema_inferred']):
        raise ValueError('Promoted ASCA component figure')
    if figure['all_primary_outcomes_rendered'] != 931 or figure['prespecified_profile_indices'] != [0, 465, 930]:
        raise ValueError('Changed ASCA figure outcome coverage')
    helper = Path(__file__).relative_to(ROOT).as_posix()
    inputs = {**document['input_sha256'], REPORT: digest(REPORT), FIGURE: digest(FIGURE),
              helper: digest(helper), figure['generator_file']: figure['generator_sha256']}
    for asset in figure['figures'].values(): inputs[asset['file']] = asset['sha256']
    for path, pin in inputs.items():
        if digest(path) != pin: raise ValueError('Changed ASCA component dependency: '+path)
    return document, figure, inputs


def record(document):
    return {'id': ID, 'label': 'Agulhas ASCA100m dated component-span experiment',
            'entity_id': 'current:agulhas', 'current_id': 'agulhas', 'status': document['status'],
            'rank_eligible': False, 'source_file': REPORT, 'source_file_sha256': digest(REPORT),
            'source_json': (ROOT/REPORT).read_bytes().decode('utf8'), 'document': document}
