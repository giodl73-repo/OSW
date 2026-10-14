"""An explicit core width does not supply a whole-current or annual width."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/atlantic-seuc-molinari-1981-core-width-scope-audit.json'
PIN='577cccac98a3970272e7e2ab7a11bceba86138fec881adad570ba18d58c8ca1c'
ID='atlantic-seuc-molinari-1981-core-width'
OWNER='atlantic-south-equatorial-undercurrent'

def load():
    raw=(ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Changed Atlantic SEUC core audit')
    return json.loads(raw)

def record():
    row=copy.deepcopy(load()['measurement'])
    row['original_regional_context'].update(audit_file=AUDIT,audit_sha256=PIN)
    return row

def validate_row(row,audit=None):
    expected=load()
    if audit is not None and audit!=expected:raise ValueError('Changed Atlantic SEUC source definition')
    if row!=record():raise ValueError('Atlantic SEUC core width differs from source definition or support')
    for kind in ['source_document','acquisition','protocol']:
        if hashlib.sha256((ROOT/expected[kind+'_file']).read_bytes()).hexdigest()!=expected[kind+'_sha256']:
            raise ValueError('Changed Atlantic SEUC original source or provenance')

def validate_inventory(document):
    rows=[r for r in document['measurements'] if r.get('id')==ID or r.get('current_id')==OWNER]
    if len(rows)!=1:raise ValueError('Missing or duplicated Atlantic SEUC core width')
    validate_row(rows[0])

def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    validate_row(record())
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-atlantic-seuc-1981','font.size':12})
    fig,ax=plt.subplots(figsize=(11,5))
    fig.subplots_adjust(left=.17,right=.91,top=.77,bottom=.45)
    ax.plot(120,0,'o',color='#08798b',markersize=10)
    ax.annotate('About 120 km core',(120,0),xytext=(0,22),textcoords='offset points',ha='center')
    ax.set_xlim(0,160);ax.set_ylim(-.7,.7);ax.set_yticks([]);ax.set_xlabel('Author-reported core width (km)')
    ax.grid(axis='x',alpha=.2);ax.spines[['top','right','left']].set_visible(False)
    fig.suptitle('Atlantic South Equatorial Undercurrent · 20 cm/s core',fontsize=16)
    caption=('1978–1980 regional study; body reports ~120 km within the 20 cm/s isotach.\n'
             'Abstract separately reports ~100 km. No 100–120 km range, 110 km midpoint or error inferred.\n'
             'No fixed width-layer bounds, per-cruise values, annual extrema or geographic edges extracted.\n'
             'Source: Molinari, Voituriez & Duncan (1981), Oceanologica Acta 4(4), 451–456, p453.\n'
             'Independent OSW graphic; source PDF/figures not reproduced.')
    fig.text(.04,.035,caption,fontsize=11,linespacing=1.7)
    path=ROOT/'figures/atlantic-seuc-molinari-1981-core-width.svg'
    fig.savefig(path,format='svg',metadata={'Date':None,'Creator':'OSW independent core-width graphic','Title':'Atlantic SEUC contour core width','Description':caption})
    path.write_bytes(('\n'.join(s.rstrip() for s in path.read_text(encoding='utf8').splitlines())+'\n').encode())
    plt.close(fig)

if __name__=='__main__':figure();print('Verified Atlantic SEUC source and wrote independent core-width figure')
