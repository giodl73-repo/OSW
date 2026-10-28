"""Same frozen source values; inline SVG styling for portable export/rendering."""
import eac_kerry_2020_mean_core_v1 as base

ROOT=base.ROOT
FILE='analysis/eac_kerry_2020_mean_core_v2.py'
FACTS='research/eac-kerry-2020-mean-core-dimensions-source-facts-v2.json'
FIGURE='figures/eac-kerry-2020-mean-core-dimensions-v2.svg'
COMPACT='figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg'

def build():
    doc=base.build();doc.update(schema='osw.eac-published-mean-core-dimensions.v2',figure_file=FIGURE,compact_figure_file=COMPACT)
    doc['input_sha256'][FILE]=base.sha(FILE)
    doc['previous_source_facts_file']=base.FACTS
    doc['revision_scope']='Inline figure styling only; identical source values, definitions and eligibility.'
    return doc

def figure(doc,compact=False):
    raw=base.figure(doc,compact).decode()
    for name,attributes in {
        'title':'font-family="Arial,sans-serif" fill="#173b49" font-weight="700" font-size="24"',
        'label':'font-family="Arial,sans-serif" fill="#173b49" font-size="16"',
        'small':'font-family="Arial,sans-serif" fill="#173b49" font-size="14"',
        'value':'font-family="Arial,sans-serif" fill="#173b49" font-size="17" font-weight="700"',
        'grid':'stroke="#cbdcdd" stroke-width="1"'
    }.items():raw=raw.replace(f'class="{name}"',attributes)
    return raw.encode()

if __name__=='__main__':
    for p in [FACTS,FIGURE,COMPACT]:
        if (ROOT/p).exists():raise ValueError('Use a new version instead of overwriting preparation evidence')
    doc=build()
    for p,raw in [(FACTS,base.encoded(doc)),(FIGURE,figure(doc)),(COMPACT,figure(doc,True))]:(ROOT/p).write_bytes(raw)
    print('Prepared portable v2 SVGs; source records unchanged and not installed')
