"""Frozen source-stage report and inequality plot; no ocean fields or packet."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
from eacc_dekeyzer_width_constraint_v1 import validate

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json'
PREFLIGHT='research/eacc-dekeyzer-2012-cited-width-visual-preflight-v1.json'
REPORT='research/eacc-dekeyzer-2012-cited-width-prepared-v1.json'
FIGURE='figures/eacc-dekeyzer-2012-cited-width-lower-bound-v1.svg'
PREVIEW='.pytest_cache/eacc-dekeyzer-2012-cited-width-lower-bound-v1.png'
RECEIPT='research/eacc-dekeyzer-2012-cited-width-visual-preparation-review-v1.json'


def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def prepare(facts):
    validate(facts)
    return {'schema':'osw.review-cited-width-constraint-prepared.v1',
        'status':'PREPARED_CITED_LOWER_BOUND_NOT_INSTALLED','source_facts_file':FACTS,
        'source':copy.deepcopy(facts['source']),'source_kind':facts['source_kind'],
        'passage':copy.deepcopy(facts['passage']),
        'underlying_cited_work':copy.deepcopy(facts['underlying_cited_work']),
        'records':copy.deepcopy(facts['records']),'lineage_note':facts['lineage_note'],
        'excluded_inferences':copy.deepcopy(facts['excluded_inferences']),
        'visual_encoding':{'operator':'gt','exclusive_lower_bound_km':160,'marker':'open_circle',
            'direction':'right','arrow_endpoint_is_measurement':False,
            'upper_bound_km':None,'central_width_km':None,'annual_range_km':None},
        'prepared_cited_constraints':1,'installed_width_records_added':0,
        'new_independent_observations':0,'new_width_samples':0,'new_lengths':0,
        'new_geographic_footprints':0,'full_goal_complete':False}


def render(facts):
    validate(facts)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    plt.rcParams.update({'svg.hashsalt':'osw-eacc-cited-lower-bound-v1','svg.fonttype':'none','font.family':'DejaVu Sans'})
    fig,ax=plt.subplots(figsize=(10.5,4.8))
    fig.subplots_adjust(left=.09,right=.94,top=.70,bottom=.43)
    bound=facts['records'][0]['reported_bound_km']
    ax.add_patch(FancyArrowPatch((bound+2,0),(232,0),arrowstyle='-|>',mutation_scale=22,
                                linewidth=2.5,color='#176f79',zorder=3))
    ax.scatter([bound],[0],s=180,facecolors='white',edgecolors='#176f79',linewidths=2.5,zorder=4)
    ax.annotate('>160 km',(bound,0),xytext=(0,24),textcoords='offset points',
                ha='center',fontsize=14,fontweight='bold',color='#133c49')
    ax.set_xlim(0,240);ax.set_ylim(-.4,.6);ax.set_xticks([0,80,160]);ax.set_yticks([])
    ax.set_xlabel('Reported width constraint (km)',fontsize=11)
    ax.spines[['top','right','left']].set_visible(False);ax.grid(axis='x',alpha=.2)
    fig.suptitle('East African Coastal Current: cited width constraint',x=.055,y=.95,
                 ha='left',fontsize=17,fontweight='bold')
    fig.text(.055,.835,'Over 160 km; no central width or upper limit supplied.',fontsize=12)
    fig.text(.055,.34,'The open circle excludes 160 km. The right arrow is an inequality symbol, not a measured endpoint.',fontsize=10)
    fig.text(.055,.255,'One thesis-cited historical statement; not another independent width observation.',fontsize=10.5)
    fig.text(.055,.185,'Width dates, numerical depth, edge definition and uncertainty are unreported. No annual range inferred.',fontsize=10)
    fig.text(.055,.115,'The cited Bell (1972) original methods and edition remain unverified.',fontsize=10)
    citation=fig.text(.055,.045,'Dekeyzer (2012), thesis section 7.2, printed p. 56 / PDF p. 74, citing Bell (1972). Original OSW plot.',fontsize=9)
    citation.set_url(facts['source']['primary_repository_record'])
    svg=io.BytesIO();png=io.BytesIO()
    description='East African Coastal Current: cited width greater than 160 kilometres. Exclusive lower bound; no upper bound, central width, annual range or uncertainty supplied. Original Bell methods remain unverified.'
    fig.savefig(svg,format='svg',metadata={'Date':None,'Title':'EACC cited width lower bound','Description':description})
    fig.savefig(png,format='png',dpi=130);plt.close(fig)
    body=svg.getvalue().replace(b'<svg ',b'<svg role="img" aria-label="'+description.encode()+b'" ',1)
    return body,png.getvalue()


def build(verify_original=False):
    pref=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    outputs=[REPORT,FIGURE,PREVIEW,RECEIPT]
    if any((ROOT/path).exists() for path in outputs):raise ValueError('Refuse to overwrite executed source products')
    facts=json.loads((ROOT/FACTS).read_bytes());validate(facts)
    if verify_original:
        original=ROOT/facts['original_file']
        if original.stat().st_size!=facts['original_bytes'] or sha(facts['original_file'])!=facts['original_sha256']:
            raise ValueError('Retained complete thesis differs')
    report=prepare(facts);report['input_sha256']=dict(pref['input_sha256'])
    svg,png=render(facts)
    artifacts={REPORT:encoded(report),FIGURE:svg,PREVIEW:png}
    receipt={'schema':'osw.cited-width-constraint-visual-preparation-review.v1',
        'status':'PREPARED_RENDER_REVIEW_PENDING','input_sha256':dict(pref['input_sha256']),
        'files':{p:hashlib.sha256(raw).hexdigest() for p,raw in artifacts.items()},
        'complete_original_custody_checked':verify_original,'underlying_original_methods_verified':False,
        'prepared_review_cited_constraints':1,'installed_width_records_added':0,
        'new_independent_observations':0,'full_goal_complete':False}
    artifacts[RECEIPT]=encoded(receipt)
    for path,raw in artifacts.items():
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream:stream.write(raw)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-original',action='store_true');args=parser.parse_args()
    build(args.verify_original)
