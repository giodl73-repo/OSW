"""Prepare two source-reported means and an original plot; no source curves read."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FACTS='research/agulhas-krug-2012-core-widths-source-facts-v1.json'
PROTOCOL='plans/agulhas-krug-2012-core-widths-protocol-v1.md'
PREFLIGHT='research/agulhas-krug-2012-core-widths-preflight-v1.json'
REPORT='research/agulhas-krug-2012-core-widths-prepared-v1.json'
FIGURE='figures/agulhas-krug-2012-core-widths-v1.svg'
PREVIEW='.pytest_cache/agulhas-krug-2012-core-widths-v1.png'
REVIEW='research/agulhas-krug-2012-core-widths-preparation-review-v1.json'


def sha(path):
    with (ROOT/path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def validate(facts):
    if facts.get('schema')!='osw.published-satellite-core-width-facts.v1' or facts.get('current_id')!='agulhas' or facts.get('entity_id')!='current:agulhas':
        raise ValueError('Source identity differs')
    source=facts['source']
    if source['doi']!='10.1029/2012GL052335' or source['original_sha256']!='4345cbf32003a2effe9b6041ff742e69c931caec610a3addf435291f13ac59dc':raise ValueError('Source custody differs')
    rows=facts['records']
    expected=[('agulhas-krug-2012-altimetry-gaussian-core-mean-width',64,113,81,145),('agulhas-krug-2012-sst-core-mean-width',80,124,85,165)]
    if len(rows)!=2:raise ValueError('Exactly two source means required')
    for row,(identity,width,core,inshore,offshore) in zip(rows,expected):
        if row['id']!=identity or row['current_id']!='agulhas' or row['quantity']!='author_reported_regional_mean_core_width' or row['unit']!='km':raise ValueError('Width identity or quantity changed')
        for key,value in [('reported_mean_width_km',width),('mean_core_distance_from_coast_km',core),('mean_landward_edge_distance_from_coast_km',inshore),('mean_seaward_edge_distance_from_coast_km',offshore)]:
            if type(row[key]) is not int or row[key]!=value:raise ValueError('Reported value differs: '+key)
        for key in ['exact_mean_estimation_start','exact_mean_estimation_end','reported_width_uncertainty_km','reported_width_standard_deviation_km','annual_width_range_km','calendar_months','individual_width_observations']:
            if row[key] is not None:raise ValueError('Unreported support promoted: '+key)
        for key in ['operator','dataset','source_locator','source_time_description']:
            if not isinstance(row[key],str) or not row[key].strip():raise ValueError('Source support missing: '+key)
    ambiguity=facts['source_ambiguities']
    if len(ambiguity)!=1 or ambiguity[0]['id']!='krug-2012-gaussian-sigma-versus-half-maximum' or ambiguity[0]['resolved'] is not False:raise ValueError('Unresolved Gaussian definition must remain explicit')
    if rows[0]['operator_ambiguity_id']!=ambiguity[0]['id'] or rows[1]['operator_ambiguity_id'] is not None:raise ValueError('Operator ambiguity reassigned')
    finding=facts['seasonality_finding']
    if finding['claim_kind']!='source_reported_non_detection_in_regional_analysis' or any(finding[k] is not False for k in ['zero_seasonal_amplitude_claimed','width_constant_claimed','annual_range_known']):raise ValueError('Non-detection promoted to zero variability')
    for key in ['geographic_section_coordinates','geographic_edge_coordinates','fixed_depth_level_m','fixed_depth_interval_m','sample_counts']:
        if facts['regional_support'][key] is not None:raise ValueError('Unsupported geometry, layer or count')
    expected_eligibility={'prepared_scoped_width_summaries':2,'installed_width_records_added':0,'independent_width_observations_added':0,'whole_current_width':False,'width_rank_eligible':False,'seasonal_playback_eligible':False,'confidence_interval_km':None,'geometry':None,'state_intersections':None,'length_km':None,'annual_width_range_km':None}
    if facts['eligibility']!=expected_eligibility or any(type(facts['eligibility'][k]) is not type(v) for k,v in expected_eligibility.items()):raise ValueError('Unsupported installation or dimensional promotion')
    exclusions=facts['excluded_context']
    for key in ['position_standard_deviations_are_width_errors','gradient_test_period_assigned_to_width_mean','merged_altimetry_third_width_record','mean_core_positions_are_width_midpoints']:
        if exclusions[key] is not False:raise ValueError('Unrelated position/time support promoted')


def prepare(facts):
    validate(facts)
    result=copy.deepcopy(facts)
    result['schema']='osw.published-satellite-core-width-preparation.v1'
    result['source_file']=FACTS
    for index,row in enumerate(result['records']):row.update(source_file=FACTS,source_pointer=f'/records/{index}')
    result['visualization']={'figure_file':FIGURE,'quantity':'Two method-specific regional mean core widths; no annual or uncertainty range','geographic_geometry':None}
    result['full_goal_complete']=False
    return result


def plot(facts):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.hashsalt':'osw-krug-2012-core-widths-v1'})
    fig,ax=plt.subplots(figsize=(10,5.2),layout=None)
    fig.subplots_adjust(left=.30,right=.95,top=.77,bottom=.35)
    values=[r['reported_mean_width_km'] for r in facts['records']]
    ax.barh([1,0],values,height=.38,color=['#246b77','#527fb4'])
    ax.set_yticks([1,0],['Along-track altimetry\nGaussian-core mean','Sea-surface temperature\nThermal-core mean'])
    for y,value in zip([1,0],values):ax.text(value+1.5,y,f'{value} km',va='center',weight='bold',color='#173c4b')
    ax.set_xlim(0,100);ax.set_ylim(-.65,1.65);ax.set_xlabel('Reported mean core width (km)')
    ax.xaxis.grid(True,color='#dce4e8',linewidth=.7);ax.set_axisbelow(True)
    for side in ['top','right','left']:ax.spines[side].set_visible(False)
    ax.tick_params(axis='y',length=0,pad=12)
    fig.suptitle('Agulhas core widths at Track 020',x=.06,ha='left',y=.96,fontsize=19,weight='bold',color='#173c4b')
    fig.text(.06,.85,'Offshore Port Elizabeth | two published method-specific means',fontsize=11,color='#385769')
    fig.text(.06,.20,'These are not seasonal limits or uncertainty bounds. No numerical width uncertainty is reported.',fontsize=10)
    fig.text(.06,.15,'The study did not detect an annual width cycle; that does not mean width is constant.',fontsize=10)
    fig.text(.06,.10,'Altimetry edge definition has an unresolved sigma / half-maximum wording ambiguity.',fontsize=10)
    fig.text(.06,.035,'Source: Krug & Tournadre (2012), doi:10.1029/2012GL052335, sections 2-3. Original OSW plot.',fontsize=9,color='#385769')
    fig.savefig(ROOT/FIGURE,metadata={'Date':None});fig.savefig(ROOT/PREVIEW,dpi=130);plt.close(fig)


def build(verify_original=False):
    preflight=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in preflight['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    facts=json.loads((ROOT/FACTS).read_bytes());validate(facts)
    if verify_original:
        source=facts['source'];original=ROOT/source['original_file']
        if original.stat().st_size!=source['original_bytes'] or sha(source['original_file'])!=source['original_sha256']:raise ValueError('Retained original differs')
    report=prepare(facts);report['input_sha256']=dict(preflight['input_sha256'])
    (ROOT/REPORT).write_bytes(encoded(report));plot(facts)
    receipt={'schema':'osw.published-satellite-core-width-preparation-review.v1','status':'PREPARED_RENDER_REVIEW_PENDING','source_file':FACTS,'source_sha256':sha(FACTS),'protocol_file':PROTOCOL,'protocol_sha256':sha(PROTOCOL),'input_sha256':dict(preflight['input_sha256']),'files':{p:sha(p) for p in [REPORT,FIGURE,PREVIEW]},'exact_original_custody_checked':verify_original,'source_figures_digitized':False,'prepared_width_summaries':2,'installed_width_records_added':0,'new_length_records':0,'seasonal_geometry_added':False,'full_goal_complete':False}
    (ROOT/REVIEW).write_bytes(encoded(receipt));print(json.dumps(receipt))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-original',action='store_true');args=parser.parse_args();build(args.verify_original)
