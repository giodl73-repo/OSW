"""Prospective Baffin latitude floor; actual-source execution requires a Git freeze."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess

from north_atlantic_gate_bound import calculation as established_gate_operator

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/baffin_latitude_gate_bound_v1.py'
TEST = 'analysis/test_baffin_latitude_gate_bound_v1.py'
FACTS = 'research/baffin-fissel-1982-length-source-review-v1.json'
PROTOCOL = 'plans/baffin-latitude-gate-bound-protocol-v1.md'
PREFLIGHT = 'research/baffin-latitude-gate-bound-preflight-v1.json'
REPORT = 'research/baffin-latitude-gate-bound-v1.json'
FIGURE = 'figures/baffin-latitude-gate-bound-v1.svg'
REVIEW = 'signals/roles/check/baffin-latitude-gate-bound-v1-roles-check-2026-10-23.md'
INPUTS = [OPERATOR, TEST, FACTS, PROTOCOL,
          'analysis/north_atlantic_gate_bound.py',
          'analysis/build_ocean_motion_claims.py', 'requirements-test.txt',
          'research/source-data/fissel-baffin-1982/acquisition.json', REVIEW]


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def input_pins():
    return {path: digest(path) for path in INPUTS}


def source_facts(document):
    expected = {
        'schema': 'osw.current-length-source-review.v1', 'current_id': 'baffin',
        'source_doi': '10.14430/arctic2318',
        'original_sha256': '23347326454aa485a98444d98ccd141fe73bc75bbcf9c6b6943f66e2d4e8e266',
        'original_bytes': 2154964, 'original_pages': 21,
        'reported_regional_latitudes_degrees_north': [67, 76],
        'southern_named_gate': 'Cape Dyer', 'northern_named_gate': 'Lady Ann Strait',
        'selected_pdf_pages_visually_reviewed_for_this_question': [1, 4],
        'study_years': [1978, 1979], 'study_season': 'summer',
    }
    for key, value in expected.items():
        if type(document.get(key)) is not type(value) or document[key] != value:
            raise ValueError('Changed selected original-source support: ' + key)
    for key in ('exact_gate_occupation_dates', 'fixed_layer_bounds_m',
                'whole_current_length_km', 'source_reported_length_km',
                'endpoint_coordinates_lon_lat', 'source_position_uncertainty_degrees'):
        if key not in document or document[key] is not None:
            raise ValueError('Undeclared physical quantity: ' + key)
    for key in ('original_redistributed', 'single_simultaneous_connected_axis_established',
                'along_current_length_calculated', 'new_numeric_calculation_performed',
                'rank_eligible', 'annual_extrema_eligible', 'seasonal_playback_eligible',
                'mapped_axis_eligible', 'independent_scientific_review_completed',
                'working_dataset_admitted'):
        if document.get(key) is not False:
            raise ValueError('Unsupported source-stage capability: ' + key)
    return copy.deepcopy(document)


def calculate_gates(lower, upper):
    if (any(type(v) not in (int, float) or not math.isfinite(v) for v in (lower, upper))
            or not (-89.5 <= lower < upper <= 89.5) or upper - lower <= 1):
        raise ValueError('Finite ordered gates and nine non-crossing scenarios required')
    return established_gate_operator(lower, upper)


def independent_meridian(lower, upper):
    """Simpson integration of WGS84 curvature, independent of PROJ inverse geodesics."""
    e2 = 0.0066943799901413165
    lo, hi = math.radians(lower), math.radians(upper)
    n = 2000
    step = (hi - lo) / n
    def radius(phi):
        return 6378137 * (1 - e2) / (1 - e2 * math.sin(phi)**2)**1.5
    total = radius(lo) + radius(hi)
    total += sum((4 if i % 2 else 2) * radius(lo + i * step) for i in range(1, n))
    return total * step / 3 / 1000


def verify_arithmetic(calc):
    rows = [(calc['nominal_latitudes_degrees_north'], calc['direct_gate_distance_km'])]
    scenarios = calc['scenarios']
    if (len(scenarios) != 9 or calc['scenario_count'] != 9
            or {(r['start_shift_degrees'], r['end_shift_degrees']) for r in scenarios}
            != {(a, b) for a in (-0.5, 0, 0.5) for b in (-0.5, 0, 0.5)}):
        raise ValueError('All nine independent scenarios required')
    for row in scenarios:
        a, b = calc['nominal_latitudes_degrees_north']
        if row['nominal_latitudes_degrees_north'] != [a + row['start_shift_degrees'], b + row['end_shift_degrees']]:
            raise ValueError('Changed shifted gates')
        rows.append((row['nominal_latitudes_degrees_north'], row['geographic_separation_km']))
    for (a, b), distance in rows:
        if not math.isfinite(distance) or abs(independent_meridian(a, b) - distance) > 0.000001:
            raise ValueError('Independent WGS84 arithmetic mismatch')
    distances = [r['geographic_separation_km'] for r in scenarios]
    if (calc['rounded_conditional_geographic_floor_km'] != math.floor(calc['direct_gate_distance_km'] / 100) * 100
            or calc['scenario_min_km'] != min(distances) or calc['scenario_max_km'] != max(distances)):
        raise ValueError('Changed rounding or scenario extrema')


def inspect_frozen_inputs(freeze_commit):
    if len(freeze_commit) != 40 or any(c not in '0123456789abcdef' for c in freeze_commit):
        raise ValueError('An exact pre-execution Git commit is required')
    subprocess.run(['git', '-c', 'core.fsmonitor=false', 'merge-base', '--is-ancestor', freeze_commit, 'HEAD'],
                   cwd=ROOT, check=True, capture_output=True)
    declaration = json.loads((ROOT / PREFLIGHT).read_bytes())
    if (declaration.get('schema') != 'osw.baffin-latitude-bound-preflight.v1'
            or declaration.get('phase') != 'prospective_declaration'
            or declaration.get('actual_baffin_gate_distance_calculated') is not False
            or declaration.get('input_sha256') != input_pins()):
        raise ValueError('Changed prospective inputs')
    for path in [*INPUTS, PREFLIGHT]:
        frozen = subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', freeze_commit + ':' + path],
                                cwd=ROOT, check=True, capture_output=True).stdout
        if frozen != (ROOT / path).read_bytes():
            raise ValueError('Input differs from pre-execution freeze: ' + path)
    return declaration


def figure(calc):
    floor = calc['rounded_conditional_geographic_floor_km']
    lower, upper = calc['nominal_latitudes_degrees_north']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-labelledby="title desc">
<title id="title">Baffin Current: conditional regional geographic floor</title>
<desc id="desc">Conditional geographic floor {floor:,.0f} km from nominal {lower:g} to {upper:g} degrees north. Not a mapped current route or whole-current length. Source summer near-surface extent uses a historical northern naming extension. Nine editorial scenarios span {calc['scenario_min_km']:,.1f} to {calc['scenario_max_km']:,.1f} km; these are not physical uncertainty or seasonal variability.</desc>
<rect width="960" height="490" rx="12" fill="#102733"/>
<g font-family="system-ui,sans-serif" fill="#e8f4f5">
<text x="28" y="44" font-size="27">Baffin Current · described latitude span</text>
<text x="28" y="90" font-size="32">{floor:,.0f} km · conditional geographic floor · unranked</text>
<text x="28" y="124" font-size="17">Rounded down to 100 km. No measured axis or guaranteed physical minimum.</text>
<path d="M110 181H850" stroke="#71cbdc" stroke-width="12"/>
<path d="M110 164V198 M850 164V198" stroke="#e8f4f5" stroke-width="3"/>
<text x="45" y="230" font-size="17">Southern latitude: {lower:g}°N</text>
<text x="654" y="230" font-size="17">Northern latitude: {upper:g}°N</text>
<text x="28" y="274" font-size="17">Nominal WGS84 meridional separation: {calc['direct_gate_distance_km']:,.1f} km.</text>
<text x="28" y="307" font-size="17">Nine ±0.5° editorial scenarios: {calc['scenario_min_km']:,.1f}–{calc['scenario_max_km']:,.1f} km.</text>
<text x="28" y="340" font-size="17">Not source position error, a confidence interval or a seasonal range.</text>
<text x="28" y="373" font-size="17">Summer 1978/1979 context; exact gate dates and a common fixed layer unknown.</text>
<text x="28" y="406" font-size="17">Fissel et al. (1982), pp180,183: author extends the name north to Lady Ann Strait.</text>
<text x="28" y="439" font-size="17">Lancaster excursion and meanders are not reconstructed. Calculation longitude is abstract.</text>
<text x="28" y="472" font-size="16">Scalar diagram only · doi:10.14430/arctic2318 · no new ranked whole-current length</text>
</g></svg>'''.encode('utf8')


def build(freeze_commit):
    inspect_frozen_inputs(freeze_commit)
    facts = source_facts(json.loads((ROOT / FACTS).read_bytes()))
    calc = calculate_gates(*facts['reported_regional_latitudes_degrees_north'])
    verify_arithmetic(calc)
    return {
        'schema': 'osw.baffin-latitude-bound-report.v1',
        'status': 'source_stage_calculation_not_working_dataset_admission',
        'current_id': 'baffin', 'entity_id': 'current:baffin',
        'freeze_commit': freeze_commit, 'source_review_file': FACTS,
        'source_url': facts['source_url'], 'source_doi': facts['source_doi'],
        'original_sha256': facts['original_sha256'], 'original_redistributed': False,
        'source_locator': facts['source_locator'], 'naming_scope': facts['naming_scope'],
        'study_years': facts['study_years'], 'study_season': facts['study_season'],
        'calculation': calc, 'independent_wgs84_integration_verified': True,
        'arithmetic_tolerance_km': 0.000001,
        'arithmetic_tolerance_is_physical_uncertainty': False,
        'sensitivity_interpretation': 'Nine editorial gate scenarios, not source position errors, physical uncertainty, confidence intervals or seasonal variability.',
        'conditional_on_nominal_gates': True, 'guaranteed_physical_minimum': False,
        'whole_current_length_km': None, 'source_reported_length_km': None,
        'annual_length_range_km': None, 'uncertainty_km': None,
        'fixed_layer_bounds_m': None, 'exact_gate_occupation_dates': None,
        'endpoint_coordinates_lon_lat': None, 'geometry_id': None,
        'rank_eligible': False, 'physical_state_join_eligible': False,
        'seasonal_playback_eligible': False, 'working_dataset_admitted': False,
        'independent_scientific_review_completed': False,
        'figure_file': FIGURE,
        'input_sha256': {**input_pins(), PREFLIGHT: digest(PREFLIGHT)},
        'figure_sha256': hashlib.sha256(figure(calc)).hexdigest(),
    }


def declare():
    if any((ROOT / p).exists() for p in (PREFLIGHT, REPORT, FIGURE)):
        raise ValueError('Retain prior declarations and products; use a new version')
    source_facts(json.loads((ROOT / FACTS).read_bytes()))
    doc = {'schema': 'osw.baffin-latitude-bound-preflight.v1',
           'phase': 'prospective_declaration', 'input_sha256': input_pins(),
           'actual_baffin_gate_distance_calculated': False,
           'selected_original_pages_previously_inspected': True,
           'whole_current_length_admitted': False}
    (ROOT / PREFLIGHT).write_bytes(encoded(doc))


def verify_original(path):
    facts = source_facts(json.loads((ROOT / FACTS).read_bytes()))
    raw = Path(path).read_bytes()
    if len(raw) != facts['original_bytes'] or hashlib.sha256(raw).hexdigest() != facts['original_sha256']:
        raise ValueError('Changed institutional original PDF')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['declare', 'build', 'check', 'original'])
    parser.add_argument('--freeze-commit')
    parser.add_argument('--original-path')
    args = parser.parse_args()
    if args.action == 'declare':
        declare()
    elif args.action == 'original':
        verify_original(args.original_path)
    else:
        if not args.freeze_commit:
            parser.error('--freeze-commit is required for actual-source execution')
        if args.action == 'build' and any((ROOT / p).exists() for p in (REPORT, FIGURE)):
            raise ValueError('Retain products; use check or a new version')
        result = build(args.freeze_commit)
        svg = figure(result['calculation'])
        if args.action == 'check':
            if (ROOT / REPORT).read_bytes() != encoded(result) or (ROOT / FIGURE).read_bytes() != svg:
                raise ValueError('Changed complete report or scalar figure')
        else:
            with (ROOT / REPORT).open('xb') as stream:
                stream.write(encoded(result))
            with (ROOT / FIGURE).open('xb') as stream:
                stream.write(svg)
        print(json.dumps({'status': 'PASS', 'calculation': result['calculation'], 'working_dataset_admitted': False}))
