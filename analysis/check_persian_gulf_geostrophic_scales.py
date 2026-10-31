"""GOGP99 velocity descriptions retain their operator and reference dependence."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/persian-gulf-gogp99-geostrophic-scales-scope-audit.json'
PIN = '6f4a7c211cb02fc5906c5d6e98279022bec688f446a1ba20aa7aa79a6c2d28d1'
OWNER = 'persian-gulf-saline-overflow'
IDS = ['persian-gulf-gogp99-r13-geostrophic-band', 'persian-gulf-gogp99-r13-geostrophic-peak']


def load():
    raw = (ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed GOGP99 geostrophic source audit')
    return json.loads(raw)


def records():
    rows = copy.deepcopy(load()['measurements'])
    for i, row in enumerate(rows):
        row['original_regional_context'].update(audit_file=AUDIT, audit_sha256=PIN, audit_pointer=f'/measurements/{i}')
    return rows


def validate_row(row, audit=None):
    document = load()
    if audit is not None and audit != document:
        raise ValueError('Changed GOGP99 geostrophic source definition')
    if row not in records():
        raise ValueError('GOGP99 geostrophic scale differs from source support or operator')
    for source in [document, *document['supporting_originals']]:
        for kind in ['source_document', 'acquisition']:
            if hashlib.sha256((ROOT/source[kind+'_file']).read_bytes()).hexdigest() != source[kind+'_sha256']:
                raise ValueError('Changed GOGP99 original or acquisition receipt')
    if hashlib.sha256((ROOT/document['protocol_file']).read_bytes()).hexdigest() != document['protocol_sha256']:
        raise ValueError('Changed GOGP99 measurement protocol')


def validate_inventory(document):
    selected = [r for r in document['measurements'] if r.get('id') in IDS]
    if len(selected) != 2 or {r['id'] for r in selected} != set(IDS):
        raise ValueError('Missing or duplicated GOGP99 geostrophic scales')
    for row in selected:
        validate_row(row)
    legacy = load()['existing_salinity_records']
    actual = [r for r in document['measurements'] if r.get('current_id') == OWNER and r.get('id') not in IDS]
    if actual != legacy:
        raise ValueError('Existing GOGP99 salinity core records changed or conflated')


def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.fonttype': 'none', 'svg.hashsalt': 'osw-gogp99-velocity-scales', 'font.size': 12})
    rows = records()
    for row in rows: validate_row(row)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(left=.25, right=.93, top=.78, bottom=.46)
    ax.scatter([30, 5], [1, 0], color='#08798b', s=65)
    for x, y in [(30, 1), (5, 0)]:
        ax.annotate(f'About {x} km', (x, y), xytext=(0, 12), textcoords='offset points', ha='center')
    ax.set_yticks([1, 0], ['Flow band near 0.1 m/s', 'Faster peak near 0.4 m/s'])
    ax.set_xlim(0, 40); ax.set_ylim(-.6, 1.7)
    ax.set_xlabel('Author-described geostrophic spatial scale (km)')
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.grid(axis='x', alpha=.2)
    fig.suptitle('Persian Gulf outflow · two descriptions at section R13', fontsize=16)
    caption = ('GOGP99 1999 context. Distinct spatial operators, not two occupations or a 5–30 km range.\n'
               'Stated speeds describe the flow/peak; no exact lateral velocity cutoff is supplied.\n'
               '30 m reference + 0.09 m/s mean offset; not contemporaneous R13 ADCP widths.\n'
               'Source: Pous, Carton & Lazure (2004), parts 1/2; part2 author-version p6 (PDF7).\n'
               'Fixed width layer, exact occupation, geographic edges and numerical width error unknown.\n'
               'Independent OSW graphic; original copyrighted figures not reproduced.')
    fig.text(.035, .03, caption, fontsize=11, linespacing=1.7)
    path = ROOT/'figures/persian-gulf-gogp99-geostrophic-scales.svg'
    fig.savefig(path, metadata={'Date': None, 'Creator': 'OSW independent source-scale comparison', 'Description': caption})
    path.write_bytes(('\n'.join(s.rstrip() for s in path.read_text(encoding='utf8').splitlines())+'\n').encode())
    plt.close(fig)


if __name__ == '__main__':
    figure()
    print('Verified GOGP99 source scales and wrote independent comparison')
