"""Verified conditional property supports for read-only atlas investigation."""
import json

from acquire_indian_secc_hycom_2013 import pin
from south_indian_front_property_windows_v2 import ROOT, REPORT, PREFLIGHT, build

ID = 'diagnostic:south-indian-2013-front-properties'
FOLDER = 'figures/south-indian-front-properties-2013/'
TEMPLATE = 'analysis/south_indian_front_property_view.html'


def evidence():
    report = build()
    if (ROOT/REPORT).read_bytes() != (json.dumps(report, indent=2, allow_nan=False)+'\n').encode():
        raise ValueError('Changed complete property-support report')
    if len(report['cases']) != 36 or any(len(c['property_windows']) != 4 for c in report['cases']):
        raise ValueError('Incomplete property assessment')
    inputs = {p: v['sha256'] for p, v in report['dependencies'].items()}
    inputs[REPORT] = pin(ROOT/REPORT)['sha256']
    inputs['analysis/south_indian_front_property_query.py'] = pin(ROOT/'analysis/south_indian_front_property_query.py')['sha256']
    row = {'id': ID, 'current_id': 'south-indian', 'entity_id': 'current:south-indian',
           'kind': 'conditional_native_property_supports', 'document': report,
           'source_file': REPORT, 'source_file_sha256': inputs[REPORT], 'figure': FOLDER+'index.html',
           'rank_eligible': False, 'label': 'South Indian 2013 conditional property windows and surface peaks'}
    return report, row, inputs


def view_evidence():
    report, row, inputs = evidence()
    view = json.loads((ROOT/FOLDER/'view.json').read_bytes())
    for key, path in [('report', REPORT), ('template', TEMPLATE), ('html', FOLDER+'index.html'),
                      ('query_adapter', 'analysis/south_indian_front_property_query.py')]:
        if view[key] != pin(ROOT/path):
            raise ValueError('Changed property view dependency: '+key)
    if view['source_input_sha256'] != inputs or view['cases'] != 36 or view['criteria_per_case'] != 4:
        raise ValueError('Changed property-view source or case matrix')
    for p in [FOLDER+'view.json', FOLDER+'index.html', TEMPLATE, 'analysis/build_south_indian_front_property_view.py']:
        inputs[p] = pin(ROOT/p)['sha256']
    return report, row, inputs


def card_links():
    from urllib.parse import quote
    q = {'document': REPORT, 'pointer': '/cases', 'limit': 36, 'offset': 0}
    return [{'label': 'Compare conditional property windows with every surface flow peak', 'url': '../'+FOLDER},
            {'label': 'Query all 36 property-support cases',
             'url': 'query.html?source-q='+quote(json.dumps(q, separators=(',', ':')), safe='')+'#source-query-title'}]
