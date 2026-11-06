"""Keep transport-float occupations and isopycnal climatology distinct."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/gulf-stream-published-width-definitions-scope-audit.json'
PIN='4e94e8b7f7a29deca11f3005b045d81966de99e967c82fd90f3ba2e4fac2060f'
OWNER='gulf-stream'


def load():
    raw=(ROOT/AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Changed frozen Gulf Stream width source definitions')
    return json.loads(raw)


def records():
    rows=copy.deepcopy(load()['measurements'])
    for i,row in enumerate(rows):row['original_regional_context'].update(audit_file=AUDIT,audit_sha256=PIN,audit_pointer=f'/measurements/{i}')
    return rows


def validate_row(row,audit=None):
    expected=load()
    if audit is not None and audit!=expected:raise ValueError('Changed Gulf Stream source support')
    wanted=next((r for r in records() if r['id']==row.get('id')),None)
    if wanted is None or row!=wanted:raise ValueError('Gulf Stream width differs from original definition, occupation or scope')
    inputs={expected['protocol_file']:expected['protocol_sha256']}
    for source in expected['sources']:
        inputs[source['source_document_file']]=source['source_document_sha256']
        inputs[source['acquisition_file']]=source['acquisition_sha256']
        if (ROOT/source['source_document_file']).stat().st_size!=source['source_document_bytes']:raise ValueError('Changed Gulf Stream source size')
    for path,pin in inputs.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=pin:raise ValueError('Changed Gulf Stream original or provenance')


def validate_inventory(inventory):
    for expected in load()['existing_current_records']:
        if [r for r in inventory['measurements'] if r.get('id')==expected['id']]!=[expected]:raise ValueError('Changed existing Gulf Stream inverse-model section')
    for expected in records():
        matches=[r for r in inventory['measurements'] if r.get('id')==expected['id']]
        if len(matches)!=1:raise ValueError('Missing or duplicated Gulf Stream published width')
        validate_row(matches[0])


def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from html import escape
    rows=records()
    for r in rows:validate_row(r)
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-gulf-stream-published-widths-v1','font.size':11})
    fig,axes=plt.subplots(1,2,figsize=(14,7))
    fig.subplots_adjust(left=.14,right=.95,top=.78,bottom=.42,wspace=.38)
    ax=axes[0];occupations=rows[0]['original_regional_context']['complete_crossing_occupations']
    for index,o in enumerate(occupations):
        ax.plot(o['width_km'],index,'o',color='#08798b',markersize=9)
        ax.annotate(str(o['width_km'])+' km',(o['width_km'],index),xytext=(8,0),textcoords='offset points',va='center')
    ax.axvline(135,color='#b36616',linestyle='--',label='Author mean135 km')
    ax.set_yticks(range(3),['30 Jun–5 Jul1967','11–15 Jul1967','16–18 Jul1967'])
    ax.invert_yaxis();ax.set_xlim(0,200);ax.set_xlabel('Fixed-baseline zero-transport span (km)')
    ax.set_title('Transport floats off Cape Hatteras\nThree complete, multi-day occupations')
    ax.legend(loc='upper left',bbox_to_anchor=(0,-.25),frameon=False)
    ax=axes[1];ax.plot(300,0,'o',color='#6c5596',markersize=10)
    ax.annotate('About300 km',(300,0),xytext=(0,18),textcoords='offset points',ha='center')
    ax.set_yticks([]);ax.set_xlim(0,350);ax.set_ylim(-1,1)
    ax.set_xlabel('Mean isopycnal contour separation (km)')
    ax.set_title('Historical climatology near70 W\nsigma-theta26.50;100/400 dbar contours')
    for ax in axes:
        ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
    title='Gulf Stream / published regional width definitions'
    fig.suptitle(title,fontsize=17)
    caption=('Left:145,140,120 km; author mean135 km. Finite occupation span120–145 km; no annual extrema or error inferred.\n'
             'Authors extend transport curves to zero, including all inshore edges. Width follows a fixed135-degree baseline, not a rotated jet frame.\n'
             'Right:100/400 dbar pressure contours on a density surface are not fixed100–400 m depth bounds or velocity edges.\n'
             'Historical archive cutoffApril1990; exact local averaging dates unresolved. Meandering/smoothing context stays separate.\n'
             'Different locations, periods, layers and boundary operators. No pooled135–300 km range or whole-current/system width.\n'
             'Sources: Richardson & Knauss1971, pp1094–1095/1107; Lozier, Owens & Curry1995, p17. Independent OSW graphic.')
    fig.text(.035,.025,caption,fontsize=10.5,linespacing=1.65)
    path=ROOT/'figures/gulf-stream-published-width-definitions.svg'
    fig.savefig(path,metadata={'Date':None,'Creator':'OSW independent scientific graphic','Description':caption})
    text=path.read_text(encoding='utf8').replace('<svg ','<svg role="img" aria-labelledby="source-title source-desc" ',1)
    i=text.index('>',text.index('<svg '))+1
    text=text[:i]+'\n<title id="source-title">'+escape(title)+'</title>\n<desc id="source-desc">'+escape(caption)+'</desc>'+text[i:]
    path.write_bytes(('\n'.join(s.rstrip() for s in text.splitlines())+'\n').encode())
    plt.close(fig)


if __name__=='__main__':figure();print('Verified two original Gulf Stream width definitions and drew independent comparison')
