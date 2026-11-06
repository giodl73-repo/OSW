"""Local descriptors cannot acquire full-width, seasonal or new naming scope."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS = {
    'hiri-current': ('research/hiri-hughes-1993-local-decay-scales-scope-audit.json', 'a4db684cf25734a0519e902115cd9197e1c6f41e0d0097c4a0e7073dc0698084'),
    'east-adriatic': ('research/east-adriatic-pasaric-2019-inflow-extent-scope-audit.json', 'd5e5d83fb84cd1243a5a4dd44b4dd3104ed2dd6c61276d29146b2bfda60e4993'),
}

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def validate_row(row, audit=None):
    ident = str(row.get('id', ''))
    owner = next((key for key, prefix in [('hiri-current', 'hiri-hughes-1993-'),
                                         ('east-adriatic', 'east-adriatic-pasaric-2019-')]
                  if ident.startswith(prefix)), row.get('current_id'))
    if owner not in AUDITS or row.get('current_id') != owner:
        raise ValueError('Local current descriptor owner reassigned')
    file, pinned = AUDITS[owner]
    reviewed = json.loads((ROOT / file).read_bytes())
    if digest(file) != pinned or audit is not None and audit != reviewed:
        raise ValueError('Changed reviewed local descriptor audit')
    for kind in ['source_document', 'acquisition', 'protocol']:
        if digest(reviewed[kind+'_file']) != reviewed[kind+'_sha256']:
            raise ValueError('Changed local descriptor original or method support')
    matches = [(i, r) for i, r in enumerate(reviewed['measurements']) if r['id'] == ident]
    if len(matches) != 1:
        raise ValueError('Unknown reviewed local descriptor')
    index, source = matches[0]
    expected = copy.deepcopy(source)
    expected['original_regional_context'].update(audit_file=file, audit_sha256=pinned,
                                                audit_pointer=f'/measurements/{index}')
    if row != expected:
        raise ValueError('Local current descriptor metric, naming or temporal scope promoted')

if __name__ == '__main__':
    inventory = json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes())
    rows = [r for r in inventory['measurements'] if r['current_id'] in AUDITS]
    if len(rows) != 3:
        raise ValueError('Missing or duplicated local descriptors')
    for row in rows:
        validate_row(row)
    print('PASS: local EAC extent and historical Hiri e-folding scales retain distinct supports')
