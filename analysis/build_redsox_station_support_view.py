"""Render metadata agreement separately from physical-cast and width admission."""
import json

from redsox_provider_station_support import ROOT, REPORT, encoded, pin

FOLDER = 'figures/redsox-station-support-2001'
TEMPLATE = 'analysis/redsox_station_support_view.html'


def build():
    raw = (ROOT / REPORT).read_bytes()
    if raw != encoded():
        raise ValueError('Changed complete station-support source')
    compact = json.dumps(json.loads(raw), ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    html = (ROOT / TEMPLATE).read_text(encoding='utf8').replace('__REPORT__', compact).replace('__SHA256__', pin(REPORT)['sha256'])
    if '__REPORT__' in html or '__SHA256__' in html:
        raise ValueError('Unfilled station-support view')
    output = ROOT / FOLDER; output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(html, encoding='utf8', newline='\n')
    doc = {'schema': 'osw.redsox-station-support-view.v1', 'report': REPORT,
           'report_pin': pin(REPORT), 'html_pin': pin(FOLDER + '/index.html'),
           'dependencies': {p: pin(p) for p in [TEMPLATE, 'analysis/build_redsox_station_support_view.py']},
           'physical_cast_identity_verified': False, 'sample_level_synchronization_verified': False,
           'physical_width_admitted': False}
    (output / 'view.json').write_text(json.dumps(doc, indent=2) + '\n', encoding='utf8')
    print('Built', FOLDER)


if __name__ == '__main__':
    build()
