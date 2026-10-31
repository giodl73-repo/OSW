"""Verify source metadata agreement before exposing the complete atlas diagnostic."""
import json
from urllib.parse import quote

from redsox_provider_station_support import ROOT, REPORT, PREFLIGHT, METHODS, encoded, pin
from build_redsox_station_support_view import FOLDER, TEMPLATE

ID = 'diagnostic:redsox-provider-station-support'
AVAILABILITY = 'research/redsox-missing-cast74-archive-check.json'
ADAPTER = 'analysis/redsox_station_support_query.py'


def evidence():
    raw = (ROOT / REPORT).read_bytes()
    if raw != encoded():
        raise ValueError('Changed complete provider station-support report')
    doc = json.loads(raw)
    view_path = FOLDER + '/view.json'
    view = json.loads((ROOT / view_path).read_bytes())
    if view['report'] != REPORT or view['report_pin'] != pin(REPORT) or view['html_pin'] != pin(FOLDER + '/index.html'):
        raise ValueError('Changed source station-support view binding')
    for path, expected in view['dependencies'].items():
        if pin(path) != expected:
            raise ValueError('Changed station-support view input: ' + path)
    availability = json.loads((ROOT / AVAILABILITY).read_bytes())
    if (availability['missing_profile_imputed'] is not False
            or availability['not_found_is_global_absence_proof'] is not False
            or availability['new_width_record_admitted'] is not False
            or len(availability['directory_checks']) != 4
            or any(not r['positive_control_listed'] or r['missing_companion_listed'] for r in availability['directory_checks'])):
        raise ValueError('Changed missing-companion review scope')
    paths = set(doc['dependencies']) | set(view['dependencies']) | {
        REPORT, PREFLIGHT, METHODS, view_path, FOLDER + '/index.html', TEMPLATE,
        'analysis/build_redsox_station_support_view.py', ADAPTER, AVAILABILITY}
    inputs = {path: pin(path)['sha256'] for path in sorted(paths)}
    row = {'id': ID, 'current_id': doc['current_id'], 'entity_id': 'current:' + doc['current_id'],
           'kind': 'provider_station_record_consistency',
           'label': 'REDSOX provider metadata agreement and unresolved clock/processing gates',
           'document': doc, 'source_file': REPORT, 'source_file_sha256': inputs[REPORT],
           'missing_companion_review_file': AVAILABILITY,
           'missing_companion_review_sha256': inputs[AVAILABILITY],
           'figure': FOLDER + '/index.html', 'rank_eligible': False,
           'current_association_verified': False, 'physical_width_admitted': False,
           'sample_level_synchronization_verified': False}
    return doc, row, inputs


def source_link(label, pointer, limit, text=None):
    q = dict(document=REPORT, pointer=pointer, limit=limit, offset=0)
    if text is not None:
        q['text'] = text
    return {'label': label, 'url': 'query.html?source-q=' + quote(json.dumps(q, separators=(',', ':')), safe='') + '#source-query-title'}


def card_links():
    return [{'label': 'Inspect REDSOX velocity and CTD station metadata', 'url': '../' + FOLDER + '/'},
            source_link('Query all 445 provider station comparisons', '/profiles', 445),
            source_link('Query station records needing metadata review', '/profiles', 445, 'provider_metadata_review_required')]
