"""One source-stage review-cited width report; no ocean fields or original curves."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/wicc-vinayachandran-2021-surface-width-source-facts-v1.json'
PROTOCOL='plans/wicc-vinayachandran-2021-surface-width-protocol-v1.md'
PREFLIGHT='research/wicc-vinayachandran-2021-surface-width-preflight-v1.json'
REPORT='research/wicc-vinayachandran-2021-surface-width-prepared-v1.json'
FIGURE='figures/wicc-vinayachandran-2021-surface-width-v1.svg'
PREVIEW='.pytest_cache/wicc-vinayachandran-2021-surface-width-v1.png'
RECEIPT='research/wicc-vinayachandran-2021-surface-width-preparation-review-v1.json'

def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def validate(facts):
    if facts.get('schema')!='osw.published-review-current-width-facts.v1' or facts.get('entity_id')!='current:west-india-coastal' or facts.get('current_id')!='west-india-coastal':raise ValueError('Review current identity differs')
    source=facts['source'];underlying=facts['underlying_cited_work']
    if source['doi']!='10.5194/bg-18-5967-2021' or source['original_pdf_sha256']!='9ca5a0854eff936d32d5fd597cd94007ea3704ddba1ebeb1aeedede09967472d' or source['selected_pdf_page_text_and_visually_reviewed']!=25 or source['printed_page']!=5991:raise ValueError('Review source or passage differs')
    if underlying['doi']!='10.1357/002224090784988809' or underlying['original_full_text_reviewed'] is not False or underlying['original_file_sha256'] is not None:raise ValueError('Unavailable original promoted or lineage changed')
    if len(facts['records'])!=1:raise ValueError('Exactly one review-cited report required')
    row=facts['records'][0]
    if row['id']!='wicc-vinayachandran-2021-review-surface-width' or row['current_id']!=facts['current_id'] or row['entity_id']!=facts['entity_id'] or row['quantity']!='published_review_reported_regional_surface_current_width' or row['unit']!='km' or type(row['reported_width_km']) is not int or row['reported_width_km']!=150 or row['approximate'] is not True:raise ValueError('Review-cited value, owner or quantity differs')
    for key in ['observed_period','calendar_months','section_latitude','fixed_depth_level_m','fixed_layer_bounds_m','geographic_edge_coordinates','geometry','sample_count','individual_observations','reported_width_uncertainty_km','confidence_interval_km','annual_width_range_km']:
        if row[key] is not None:raise ValueError('Unreported review support promoted: '+key)
    for key in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_observational_sample','underlying_original_measurement_methods_verified']:
        if row[key] is not False:raise ValueError('Unsupported review eligibility: '+key)
    for key in ['geographic_scope','time_description','layer_description','boundary_rule','source_locator']:
        if not isinstance(row[key],str) or not row[key].strip():raise ValueError('Missing review context: '+key)
    if facts['physical_measurement_reproduction_verified'] is not False or facts['installed_width_records_added']!=0 or facts['installed_width_samples_added']!=0:raise ValueError('Source preparation promoted to observation or installation')

def prepare(facts):
    validate(facts)
    return {'schema':'osw.prepared-review-current-width.v1','status':'SOURCE_STAGE_REVIEW_CITED_WIDTH_NOT_INSTALLED','source_facts_file':FACTS,'source':copy.deepcopy(facts['source']),'underlying_cited_work':copy.deepcopy(facts['underlying_cited_work']),'records':copy.deepcopy(facts['records']),'excluded_inferences':copy.deepcopy(facts['excluded_inferences']),'observational_independence_note':facts['observational_independence_note'],'independent_observations_added':0,'new_width_samples':0,'installed_width_records_added':0,'full_goal_complete':False}

def plot(facts):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt':'osw-wicc-review-width-v1','svg.fonttype':'none','font.family':'DejaVu Sans'})
    fig,ax=plt.subplots(figsize=(10,4.5));fig.subplots_adjust(left=.22,right=.94,top=.72,bottom=.39)
    ax.scatter([facts['records'][0]['reported_width_km']],[0],s=180,color='#176f79',zorder=3)
    ax.annotate('about 150 km',(150,0),xytext=(0,17),textcoords='offset points',ha='center',fontsize=13,fontweight='bold')
    ax.set_xlim(0,200);ax.set_ylim(-.5,.5);ax.set_yticks([0],['Review-cited\nsurface width']);ax.set_xlabel('Reported regional width (km)',fontsize=11)
    ax.grid(axis='x',alpha=.2);ax.spines[['top','right','left']].set_visible(False)
    fig.suptitle('West India Coastal Current',x=.06,y=.94,ha='left',fontsize=17,fontweight='bold')
    fig.text(.06,.83,'One published review statement; not a new independent observation.',fontsize=11)
    fig.text(.06,.24,'Summer-monsoon discussion; exact dates, numerical width depth and edge coordinates unspecified.',fontsize=10)
    fig.text(.06,.16,'No width error or annual range supplied. The cited 1990 original methods remain unverified.',fontsize=10)
    fig.text(.06,.06,'Vinayachandran et al. (2021), section 2.7.1, p. 5991. DOI: 10.5194/bg-18-5967-2021. Original OSW plot.',fontsize=9)
    fig.savefig(ROOT/FIGURE,metadata={'Date':None});fig.savefig(ROOT/PREVIEW,dpi=130);plt.close(fig)

def build(verify_original=False):
    pref=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    if any((ROOT/path).exists() for path in [REPORT,FIGURE,PREVIEW,RECEIPT]):raise ValueError('Refuse to overwrite executed source products')
    facts=json.loads((ROOT/FACTS).read_bytes());validate(facts)
    if verify_original:
        source=facts['source']
        if (ROOT/source['original_pdf_file']).stat().st_size!=source['original_pdf_bytes'] or sha(source['original_pdf_file'])!=source['original_pdf_sha256'] or sha(source['original_xml_file'])!=source['original_xml_sha256']:raise ValueError('Retained review original differs')
    report=prepare(facts);report['input_sha256']=dict(pref['input_sha256']);(ROOT/REPORT).write_bytes(encoded(report));plot(facts)
    receipt={'schema':'osw.review-current-width-preparation-review.v1','status':'PREPARED_RENDER_REVIEW_PENDING','input_sha256':dict(pref['input_sha256']),'files':{p:sha(p) for p in [REPORT,FIGURE,PREVIEW]},'exact_review_original_custody_checked':verify_original,'original1990_methods_verified':False,'prepared_review_cited_records':1,'installed_width_records_added':0,'new_independent_observations':0,'full_goal_complete':False}
    (ROOT/RECEIPT).write_bytes(encoded(receipt))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-original',action='store_true');args=parser.parse_args();build(args.verify_original)
