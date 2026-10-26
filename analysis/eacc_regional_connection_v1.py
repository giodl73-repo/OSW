"""Prepare one scoped published regional connection without inferred geometry."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/eacc-painter-2020-regional-reach-source-facts-v1.json'
PROTOCOL = 'plans/eacc-published-regional-connection-protocol-v1.md'
RECEIPT = 'research/source-data/painter-eacc-2020/acquisition.json'
PREFLIGHT = 'research/eacc-regional-connection-preflight-v1.json'
REPORT = 'research/eacc-regional-connection-candidate-v1.json'
FIGURE = 'figures/eacc-regional-connection-v1.svg'
INPUTS = [FACTS, PROTOCOL, RECEIPT, 'analysis/eacc_regional_connection_v1.py',
          'analysis/test_eacc_regional_connection_v1.py']


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf8')


def sha(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def project(facts):
    if (facts['entity_id'] != 'current:east-african-coastal'
            or facts['quantity'] != 'source_reported_approximate_regional_connection_distance'
            or facts['reported_distance_km'] != 1000
            or isinstance(facts['reported_distance_km'], bool)
            or facts['approximate'] is not True
            or facts['reported_latitude_context_degrees'] != [-11, -3]):
        raise ValueError('Changed source identity, quantity, precision or context')
    for key in ['longitude_coordinates', 'exact_observation_dates', 'fixed_depth_layer_m',
                'source_numeric_length_uncertainty_km', 'whole_current_length_km',
                'annual_length_range_km']:
        if facts[key] is not None:
            raise ValueError('Unreported support must remain null: '+key)
    for key in ['source_gate_coordinates_extracted', 'geodesic_path_computed',
                'whole_current_rank_eligible', 'seasonal_geometry_eligible',
                'working_dataset_admitted']:
        if facts[key] is not False:
            raise ValueError('Unsupported promotion: '+key)
    if facts['new_physical_geometry_or_state_joins'] != 0:
        raise ValueError('No new physical geometry or state joins')
    return {
        'id': 'regional-reach:east-african-coastal:painter-2020-connection',
        'entity_id': facts['entity_id'], 'current_id': 'east-african-coastal',
        'quantity': facts['quantity'], 'reported_value_km': facts['reported_distance_km'],
        'approximate': True, 'relation': 'source_reported_value', 'unit': 'km',
        'latitude_context_degrees_north': copy.deepcopy(facts['reported_latitude_context_degrees']),
        'longitude_coordinates': None, 'observation_window': None, 'fixed_depth_layer_m': None,
        'reported_uncertainty_km': None, 'whole_current_length_km': None,
        'physical_length_lower_bound_km': None, 'annual_length_range_km': None,
        'physical_width_km': None, 'current_geometry': None, 'state_intersections': None,
        'rank_eligible': False, 'seasonal_playback_eligible': False,
        'evidence_class': 'review_reported_regional_connection_theoretical_transit_context',
        'source': copy.deepcopy(facts['source']),
        'status': 'prepared_pending_query_and_runtime_integration',
        'protocol_file': PROTOCOL,
    }


def build():
    pins = json.loads((ROOT/PREFLIGHT).read_bytes())
    if pins['input_sha256'] != {p: sha(p) for p in INPUTS}:
        raise ValueError('Frozen source-stage inputs changed')
    facts = json.loads((ROOT/FACTS).read_bytes())
    report = project(facts)
    source = facts['source']
    receipt = json.loads((ROOT/RECEIPT).read_bytes())
    if (source['doi'] != '10.1016/j.pocean.2020.102374'
            or sha(source['original_file']) != source['original_sha256']
            or receipt['sha256'] != source['original_sha256']
            or (ROOT/source['original_file']).stat().st_size != source['original_bytes']
            or receipt['bytes'] != source['original_bytes']):
        raise ValueError('Original source identity or custody changed')
    import pymupdf
    with pymupdf.open(ROOT/source['original_file']) as doc:
        text = ' '.join(doc[26].get_text().split())
        for phrase in ['EACC', '11°S', '~1000 km', 'Somali Current at ~3°S', 'could in theory travel']:
            if phrase not in text:
                raise ValueError('Missing registered page-27 passage: '+phrase)
    report['input_sha256'] = pins['input_sha256']
    return report


def figure(report):
    if report['reported_value_km'] != 1000 or report['approximate'] is not True:
        raise ValueError('Changed visual quantity')
    return b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 360" role="img" aria-labelledby="title desc">
<title id="title">EACC: published regional connection</title>
<desc id="desc">Approximately 1000 km from coastal contact near 11 degrees south to the Somali Current confluence near 3 degrees south. Review context, not an observed transit or measured current axis. Observation dates, fixed layer, uncertainty and annual ranges unknown.</desc>
<rect width="860" height="360" rx="14" fill="#f3f8fa"/>
<g font-family="Arial,sans-serif" fill="#173342">
<text x="32" y="43" font-size="25">East African Coastal Current</text>
<text x="32" y="76" font-size="18">Published regional connection - approximately 1000 km</text>
<path d="M70 130H775M70 120V140M775 120V140" stroke="#0c6b82" stroke-width="4"/>
<text x="32" y="173" font-size="16">Coastal contact near 11 S</text>
<text x="440" y="173" font-size="16">Somali Current confluence near 3 S</text>
<text x="32" y="217" font-size="16">Schematic only; longitudes and geographic axis unspecified.</text>
<text x="32" y="247" font-size="16">Dates, fixed layer, numerical uncertainty and annual ranges unknown.</text>
<text x="32" y="277" font-size="16">Whole-current length unmeasured; excluded from length ranking.</text>
<text x="32" y="318" font-size="14">Painter (2020), p27 - review's theoretical-transit context, not a tracked transit.</text>
</g></svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    report = build()
    outputs = {REPORT: encoded(report), FIGURE: figure(report)}
    for path, raw in outputs.items():
        target = ROOT/path
        if target.exists() and target.read_bytes() != raw:
            raise ValueError('Refusing changed product: '+path)
        if args.command == 'check' and not target.exists():
            raise ValueError('Missing product: '+path)
    if args.command == 'build':
        for path, raw in outputs.items():
            (ROOT/path).write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'products': {p: hashlib.sha256(b).hexdigest() for p,b in outputs.items()}}))


if __name__ == '__main__':
    main()
