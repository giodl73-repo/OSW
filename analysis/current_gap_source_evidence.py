"""Verified source-gap diagnostics and atlas links; no physical admissions."""
import hashlib
import json
from urllib.parse import quote

from indian_secc_source_boundary_audit import ROOT, REPORT, PREFLIGHT, encoded, pin
from build_indian_secc_source_boundary_view import FOLDER, TEMPLATE

BOUNDARY_ID = 'diagnostic:indian-secc-2013-source-boundaries'
REDSEA_ID = 'diagnostic:red-sea-ozgokmen-2003-width-scope'
REDSEA = 'research/ozgokmen-2003-red-sea-width-scope-review.json'
ACQUISITION = 'research/source-data/ozgokmen-redsea-2003/acquisition.json'
ADAPTER = 'analysis/current_gap_source_evidence.py'


def source_link(label, document, pointer, limit):
    query = {'document': document, 'pointer': pointer, 'limit': limit, 'offset': 0}
    return {'label': label, 'url': 'query.html?source-q=' + quote(json.dumps(query, separators=(',', ':')), safe='') + '#source-query-title'}


def evidence():
    raw = (ROOT / REPORT).read_bytes()
    if raw != encoded():
        raise ValueError('Changed complete source-boundary audit')
    audit = json.loads(raw)
    view_path = FOLDER + '/view.json'
    view = json.loads((ROOT / view_path).read_bytes())
    if view['source'] != REPORT or view['source_pin'] != pin(REPORT) or view['html_pin'] != pin(FOLDER + '/index.html'):
        raise ValueError('Changed source-boundary view binding')
    for path, expected in view['dependencies'].items():
        if pin(path) != expected:
            raise ValueError('Changed source-boundary view input: ' + path)
    review = json.loads((ROOT / REDSEA).read_bytes())
    receipt = json.loads((ROOT / ACQUISITION).read_bytes())
    if (review['current_id'] != 'red-sea-saline-overflow'
            or any(review[k] for k in ['physical_width_admitted', 'physical_axis_admitted', 'physical_length_admitted', 'annual_width_range_admitted'])
            or review['source_identity']['sha256'] != receipt['sha256']
            or review['source_identity']['bytes'] != receipt['bytes']
            or receipt['original_redistributed'] is not False):
        raise ValueError('Changed Red Sea source identity or admission scope')
    paths = set(audit['dependencies']) | set(view['dependencies']) | {
        REPORT, PREFLIGHT, view_path, FOLDER + '/index.html', TEMPLATE, ADAPTER,
        REDSEA, ACQUISITION}
    inputs = {path: pin(path)['sha256'] for path in sorted(paths)}
    rows = []
    for identifier, owner, kind, path, doc, label, figure in [
        (BOUNDARY_ID, audit['current_id'], 'serialized_source_boundary_audit', REPORT, audit,
         'Indian SECC 2013 source stops and unresolved threshold edges', FOLDER + '/index.html'),
        (REDSEA_ID, 'red-sea-saline-overflow', 'primary_source_channel_dimension_scope', REDSEA, review,
         'Red Sea 2003 channel dimensions are not measured plume widths', None)]:
        row = {'id': identifier, 'current_id': owner, 'entity_id': 'current:' + owner,
               'kind': kind, 'document': doc, 'source_file': path,
               'source_file_sha256': inputs[path], 'rank_eligible': False, 'label': label}
        if figure is not None:
            row['figure'] = figure
        rows.append(row)
    return audit, review, rows, inputs


def card_links(current_id):
    if current_id == 'indian-south-equatorial-countercurrent':
        return [{'label': 'Inspect every source stop and unresolved edge', 'url': '../' + FOLDER + '/'},
                source_link('Query all 144 source-boundary audit attempts', REPORT, '/attempt_inventory', 144),
                source_link('Query all retained terminal and threshold records', REPORT, '/terminal_rows', 156)]
    if current_id == 'red-sea-saline-overflow':
        return [source_link('Why the 2003 channel width is not a measured current width', REDSEA, '/findings', 4),
                source_link('Inspect the original-study acquisition receipt', ACQUISITION, '', 50)]
    return []
