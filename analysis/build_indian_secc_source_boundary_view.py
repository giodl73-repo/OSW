"""Build a standalone view from the frozen retained-source boundary audit."""
import hashlib
import json
from pathlib import Path

from indian_secc_source_boundary_audit import ROOT, REPORT, encoded, pin

FOLDER = 'figures/indian-secc-source-boundaries-2013'
TEMPLATE = 'analysis/indian_secc_source_boundary_view.html'


def build():
    raw = (ROOT / REPORT).read_bytes()
    if raw != encoded():
        raise ValueError('Audit is not an exact reconstruction')
    template = (ROOT / TEMPLATE).read_text(encoding='utf8')
    compact = json.dumps(json.loads(raw), ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    html = template.replace('__AUDIT_DATA__', compact).replace('__AUDIT_SHA256__', hashlib.sha256(raw).hexdigest())
    if '__AUDIT_' in html:
        raise ValueError('Unfilled view placeholder')
    output = ROOT / FOLDER
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(html, encoding='utf8', newline='\n')
    manifest = {'schema': 'osw.source-boundary-view.v1', 'source': REPORT,
                'source_pin': pin(REPORT), 'dependencies': {p: pin(p) for p in [TEMPLATE, 'analysis/build_indian_secc_source_boundary_view.py']},
                'html_pin': pin(FOLDER + '/index.html'), 'physical_width_admitted': False}
    (output / 'view.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    print('Built', FOLDER)


if __name__ == '__main__':
    build()
