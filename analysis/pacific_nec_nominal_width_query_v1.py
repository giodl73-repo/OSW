"""One audited nominal width; no inherited family measurements or seasonal bounds."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import check_pacific_nec_nominal_width_parent_v1 as parent
import pacific_nec_nominal_width_v1 as nominal

ROOT=Path(__file__).resolve().parents[1]
PARENT=parent.LOGICAL
OWNER=parent.OWNER
CURRENT='pacific-north-equatorial'
KEY='published_pacific_nec_nominal_width_v1'
FILE='research/pacific-nec-nominal-width-query-contract-v1.json'
MODULE='analysis/pacific_nec_nominal_width_query_v1.py'
PROTOCOL='plans/pacific-nec-nominal-width-query-contract-v1.md'
SELECTED='research/pacific-nec-nominal-width-parent-run-v1/selected-records.json'
REVIEW='research/pacific-nec-nominal-width-parent-execution-review-v1.json'
RESULT='research/pacific-nec-nominal-width-parent-run-v1/result.json'
SOURCE_IDS=['source:qiu-pacific-nec-okmc-2015','source:qiu-paradigm-2015']
WIDTH_ID='pacific-nec-qiu2015-nominal-surface-span'


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def fingerprint(value):return hashlib.sha256(encoded(value)).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def query_url():
    return 'query.html?q='+quote(json.dumps({'collection':'widths','filters':[{'field':'current_id','op':'eq','value':CURRENT}],'limit':100},separators=(',',':')))+'#query-chart-section'


def build_contract():
    review=read(REVIEW);selected=read(SELECTED);result=read(RESULT);request=read(parent.REQUEST)
    facts=read(nominal.FACTS);prepared=read(nominal.FILE);source_review=read('research/pacific-nec-nominal-width-preparation-review-v1.json')
    if (review['status']!='PASS_NO_EXISTING_MEMBER_OR_FAMILY_WIDTH_AND_REVIEWED_PUBLICATIONS_MISSING'
            or review['request_disabled'] is not True or request['execute'] is not False
            or request['cloud_parent_packet_read_permitted'] is not False or request['completed_run_id']!=40809019002
            or result['logical_sha256']!=PARENT or result['logical_byte_length']!=190678008
            or sha(SELECTED)!=result['selected_records_sha256'] or sha(SELECTED)!=review['selected_records_sha256']
            or selected['candidate_width_id_matches'] or selected['publication_linked_width_records']
            or any(r['status']!='MISSING' for r in result['publication_resolutions'].values())
            or any(selected['publications'].values()) or source_review['compact_figure_individually_viewed'] is not True):
        raise ValueError('Exact installed audit and original-source review required')
    for path,pin in source_review['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Changed reviewed source input: '+path)
    expected=nominal.prepare(facts)
    if {k:v for k,v in prepared.items() if k!='input_sha256'}!=expected:
        raise ValueError('Prepared nominal width differs from reviewed source calculation')
    for owner in [OWNER,'current:north-equatorial']:
        if selected['identities'][owner]['widths']:raise ValueError('Existing member/family widths require reconciliation')
    width=copy.deepcopy(expected)
    for key in ['installed','full_goal_complete']:width.pop(key)
    width.update(schema='osw.scoped-width-evidence.v1',status='derived_published_nominal_regional_summary',
        name='Pacific North Equatorial Current',display='about 1,000 km',width_range_km=None,
        phase_kind='nominal_regional_summary',phase_label='Nominal near-surface span, Qiu et al. (2015)',
        edge_operator=None,source_id=SOURCE_IDS[0],source_ids=list(SOURCE_IDS),
        source_file_sha256=sha(nominal.FACTS),source_citation=facts['citation'],
        source_evidence_kind='project_synthesis_nominal_surface_band',
        extraction_method='Convert the source nominal8-17N separation with WGS84 and round to100km. No figure edges digitized or physical longitude supplied.',
        source_retrieved_date='2026-10-28',is_annual_mean=False,is_climatology=False,
        related_source_context={'source_id':SOURCE_IDS[1],'source_file':nominal.FACTS,
            'source_pointer':'/underlying_study_context','latitude_band_deg_north':[7,17],
            'is_second_width_record':False,'is_annual_or_uncertainty_range':False})
    papers=[('qiu_okmc_2015',['Bo Qiu','Daniel L. Rudnick','Ivana Cerovecki','Bruce D. Cornuelle','Shuiming Chen','Martha C. Schonau','Julie L. McClean','Ganesh Gopalakrishnan']),
        ('qiu_paradigm_2015',['Bo Qiu','Shuiming Chen','Daniel L. Rudnick','Yuji Kashino'])]
    sources=[]
    for (key,authors),source_id in zip(papers,SOURCE_IDS):
        p=parent.PAPERS[key]
        sources.append({'id':source_id,'kind':'publication','title':p['title'],'label':p['title'],
            'authors':authors,'year':2015,'doi':p['doi'],'url':p['urls'][0],
            'source_facts_file':nominal.FACTS,'source_facts_sha256':sha(nominal.FACTS),
            'source_pointer':'/nominal_surface_width' if key=='qiu_okmc_2015' else '/underlying_study_context',
            'provider_asset_redistributed':False,'used_in_collections':['objects','widths'],
            'access_scope':'Relevant original pages individually reviewed from public author deposits; originals not redistributed.',
            'scope_note':'Nominal regional surface span.' if key=='qiu_okmc_2015' else 'Related methods and separately preserved7-17N context; not a second width or independent observation.'})
    prior=selected['identities'][OWNER];old=prior['object'];owner=copy.deepcopy(old)
    owner['width_ids'].append(WIDTH_ID);owner['capabilities']['scoped_width']+=1
    owner['source_ids']=sorted(set(owner['source_ids'])|set(SOURCE_IDS));owner['linked_source_count']=len(owner['source_ids'])
    owner['section_fingerprints']['measurements']=fingerprint({'prior_fingerprint':old['section_fingerprints']['measurements'],'added_width':width})
    owner['section_fingerprints']['sources']=fingerprint({'prior_fingerprint':old['section_fingerprints']['sources'],'added_sources':sources})
    owner['evidence_links'] += [{'label':'Inspect nominal near-surface width and source scope','url':query_url()},
        {'label':'Nominal regional width diagram','url':'../'+nominal.FIGURE}]
    owner['fingerprint']=fingerprint({k:v for k,v in owner.items() if k!='fingerprint'})
    pins=[MODULE,PROTOCOL,SELECTED,REVIEW,RESULT,parent.REQUEST,'research/pacific-nec-nominal-width-parent-run-v1/run-receipt.json',
        nominal.FACTS,nominal.FILE,nominal.PROTOCOL,'analysis/pacific_nec_nominal_width_v1.py',nominal.FIGURE,
        'research/pacific-nec-nominal-width-preparation-review-v1.json',
        'research/source-data/qiu-pacific-nec-2015/acquisition-v1.json','research/source-data/qiu-pacific-nec-2015/selected-render-review-v1.json',
        'research/source-data/qiu-paradigm-2015/acquisition-v1.json','research/source-data/qiu-paradigm-2015/selected-render-review-v1.json']
    return {'schema':'osw.pacific-nec-nominal-width-query-contract.v1','status':'PREPARED_NOT_COMPILED_OR_INSTALLED',
        'parent_logical_sha256':PARENT,'prior_records':selected,'parent_collection_counts':result['collection_counts'],
        'width_record':width,'new_sources':sources,'final_owner':owner,'dashboard_before':old,'dashboard_after':copy.deepcopy(owner),
        'input_sha256':{p:sha(p) for p in pins},'new_width_records':1,'new_publication_sources':2,
        'new_length_records':0,'new_width_samples':0,'new_independent_observations':0,'new_physical_footprints':0,
        'expected_totals':{'widths':179,'sources':219,'owners_with_scoped_width_capability':90,'accepted_current_identities':111},
        'width_query_after_installation':query_url()}


def marker(contract):
    return {'schema':'osw.pacific-nec-nominal-width-runtime-receipt.v1','parent_logical_sha256':PARENT,
        'contract_file':FILE,'contract_sha256':fingerprint(contract),'width_records_added':1,'publication_sources_added':2,
        'new_width_samples':0,'new_independent_observations':0,'new_length_records':0,'physical_geometry_added':False}


def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied contract and audited parent required')
    prior=contract['prior_records'];identities=prior['identities']
    for name in ['sources','objects','entities','widths','reference_routes']:
        rows=collections.get(name)
        if not isinstance(rows,list) or len(rows)!=contract['parent_collection_counts'][name]:raise ValueError('Parent inventory differs: '+name)
        ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique IDs required: '+name)
    for owner,audited in identities.items():
        for name,key in [('objects','object'),('entities','entity')]:
            if [r for r in collections[name] if r.get('id')==owner]!=[audited[key]]:raise ValueError('Changed audited identity: '+owner)
        for name in ['widths','reference_routes']:
            if [r for r in collections[name] if r.get('current_id')==owner.removeprefix('current:') or r.get('entity_id')==owner]!=audited[name]:raise ValueError('Changed audited evidence: '+owner)
    sources=collections['sources'];matches,resolutions=parent.publications(sources)
    if any(matches.values()) or any(r['status']!='MISSING' for r in resolutions.values()) or any(r['id'] in SOURCE_IDS for r in sources):
        raise ValueError('Existing publication identity requires reconciliation')
    by_id={r['id']:r for r in sources}
    for owner,audited in identities.items():
        if any(by_id.get(r['id'])!=r for r in audited['owner_sources']):raise ValueError('Changed prior source: '+owner)
    if any(r.get('id')==WIDTH_ID for r in collections['widths']):raise ValueError('Existing width ID')
    for path,pin in {**contract['input_sha256'],FILE:fingerprint(contract)}.items():
        if path in manifest.get('input_sha256',{}) and manifest['input_sha256'][path]!=pin:raise ValueError('Historical input pin would change: '+path)
    after=dict(collections)
    after['widths']=[*collections['widths'],copy.deepcopy(contract['width_record'])]
    after['sources']=[*sources,*copy.deepcopy(contract['new_sources'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==OWNER else r for r in collections['objects']]
    updated=dict(manifest);updated['input_sha256']=dict(manifest.get('input_sha256',{}))
    updated['input_sha256'].update(contract['input_sha256']);updated['input_sha256'][FILE]=fingerprint(contract);updated[KEY]=marker(contract)
    collections.clear();collections.update(after);manifest.clear();manifest.update(updated)


if __name__=='__main__':
    path=ROOT/FILE
    if path.exists():raise ValueError('Use a new contract version')
    path.write_bytes(encoded(build_contract()))
    print('Frozen one nominal regional width and two publication sources; runtime integration and installation pending.')
