"""Define measurement scope for family, system and ambiguous current records."""
from pathlib import Path
from collections import Counter
import hashlib,json,textwrap,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
INDEX='research/current-measurement-object-scope-index.json'
NOTES='research/ocean-current-scope-notes.json'
PROTOCOL='plans/current-measurement-object-scope-protocol-v1.md'
FROZEN_INPUTS={'research/ocean-current-almanac.json': '6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e', 'research/ocean-current-width-inventory.json': '929527ad7c4a500eca26d495c59e6eadd3d62e82b3bc9b9cd1ff57084b1aacb8', 'research/ocean-current-inventory-expansion-candidates.json': '0d0c4b707c70a50494151ca6c2d672eec7711bf7ea273d5f56df6849ee56893c', 'research/equatorial-basin-family-inventory-audit.json': 'dd053682b07525f818a0b5b9b6c03ecab717ff63926d2d273dfb0dae8ff4bac9', 'research/norwegian-naming-branch-scope-audit.json': 'b191cb19d5fe5d82b786fb8bdcd3f4b1ffd7c251add3430c10b6e09d4acf2d9f', 'research/spitsbergen-atlantic-naming-branch-scope-audit.json': 'f7a5c4a81ff9fb408097877b3cc0d2c85c8fd65618bccf3ac82bda09823158db', 'research/indonesian-throughflow-network-scope-audit.json': 'a857f6be29353bfb10f79fb91f51466049fc3324cd769d56de44af60e1506a0a', 'plans/ocean-current-width-measurement-protocol-v1.md': '1d4d577d8f3b422cf3252b973280cb7073bad7e3234bc40a2808bc16bda974bb', 'plans/current-measurement-object-scope-protocol-v1.md': 'df7611b56e14086f18c053ec0b20f95108717f80f72f0002c64f9eb5f5558842'}
GROUPS={
 'basin_family':['north-equatorial','south-equatorial','equatorial-countercurrent','north-equatorial-countercurrent','south-equatorial-countercurrent','equatorial-undercurrent','north-equatorial-undercurrent','south-equatorial-undercurrent'],
 'unresolved_name':['norwegian','spitsbergen-atlantic'],
 'continuity_hypothesis':['greenland-middle-atlantic-shelf-hypothesis'],
 'passage_network':['indonesian-throughflow'],
 'compound_current_system':['australian-west-south-boundary-flow'],
}
ACTIONS={
 'basin_family':'Measure basin members separately. Define layer, period and paired boundaries for each member; the family has no shared global width.',
 'unresolved_name':'Resolve the source-specific name and branch convention before attaching a width. Related records are not confirmed aliases or members.',
 'continuity_hypothesis':'Test continuity and define observed reaches before assigning a system-wide dimension. The proposed connection remains a hypothesis.',
 'passage_network':'Measure each passage with explicit depth, period and boundary rules. Channel and transport-integration spans are not current-width boundaries.',
 'compound_current_system':'Measure components separately with explicit season, layer and boundary rules. Do not pool their different widths into one system width.',
}
PRIOR={'norwegian':'research/norwegian-naming-branch-scope-audit.json',
       'spitsbergen-atlantic':'research/spitsbergen-atlantic-naming-branch-scope-audit.json',
       'indonesian-throughflow':'research/indonesian-throughflow-network-scope-audit.json'}

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def path_for(ident):return f'research/current-measurement-scopes/{ident}.json'
def figure_for(ident):return f'figures/current-measurement-scopes/{ident}.svg'

def diagram(report):
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    members=report['members'];height=max(310,160+len(members)*72)
    svg=ET.Element('svg',xmlns=ns,viewBox=f'0 0 800 {height}',role='img',attrib={'aria-labelledby':'title description'})
    ET.SubElement(svg,'title',id='title').text=report['name']+': measurement scope'
    ET.SubElement(svg,'desc',id='description').text=report['summary']+' Member evidence is not inherited by the parent. This is a relationship diagram, not a geographic map.'
    ET.SubElement(svg,'rect',width='800',height=str(height),fill='#f5f8fa')
    def text(x,y,value,size=15,color='#203747'):
        ET.SubElement(svg,'text',x=str(x),y=str(y),fill=color,attrib={'font-size':str(size),'font-family':'sans-serif'}).text=value
    for i,line in enumerate(textwrap.wrap(report['name'],65)):text(22,30+i*22,line,19)
    text(22,75,report['scope_kind'].replace('_',' '),14)
    ET.SubElement(svg,'rect',x='20',y='98',width='260',height='76',rx='6',fill='#e0edf2',stroke='#426579')
    for i,line in enumerate(textwrap.wrap('Define this object before measuring its width',30)):text(32,123+i*20,line,15)
    if not members:
        for i,line in enumerate(textwrap.wrap(report['summary'],63)):text(310,120+i*20,line,14)
    for i,member in enumerate(members):
        y=96+i*72;related=member['relationship']=='related_name_not_equated';proposed=member['record_status']=='proposed'
        ET.SubElement(svg,'line',x1='280',y1='136',x2='355',y2=str(y+25),stroke='#607d89',attrib={'stroke-dasharray':'3 4' if related or proposed else 'none'})
        ET.SubElement(svg,'rect',x='355',y=str(y),width='420',height='58',rx='5',fill='#fff',stroke='#607d89',attrib={'stroke-dasharray':'3 4' if proposed else 'none'})
        for j,line in enumerate(textwrap.wrap(member['label'],45)):text(367,y+19+j*17,line,14)
        suffix='proposal; not an admitted current' if proposed else ('related name; equivalence unresolved' if related else f"member owns {member['scoped_width_record_count']} scoped width records")
        text(367,y+48,suffix,11)
    text(22,height-45,'Relationships only. No current path, shared width or physical boundary is drawn.',13)
    text(22,height-23,'Member values and observation dates stay with their original records.',13)
    return ET.tostring(svg,encoding='utf-8',xml_declaration=True)+b'\n'

def build():
    if len(FROZEN_INPUTS)!=9:raise ValueError('Missing object-scope inputs')
    for path,pin in FROZEN_INPUTS.items():
        if digest(path)!=pin:raise ValueError('Changed object-scope input: '+path)
    read=lambda p:json.loads((ROOT/p).read_bytes())
    ledger=read('research/ocean-current-almanac.json');owners={r['id']:r for r in ledger['entries']}
    widths=read('research/ocean-current-width-inventory.json')
    targets={r['current_id'] for r in widths['current_decisions'] if r['width_decision']=='width_not_assessed'}
    assignments={ident:group for group,ids in GROUPS.items() for ident in ids}
    if len(assignments)!=13 or set(assignments)!=targets:raise ValueError('Scope assessment does not match the unresolved worklist')
    counts=Counter(r['current_id'] for r in widths['measurements'])
    proposals=read('research/ocean-current-inventory-expansion-candidates.json')['entries']
    reports={};figures={};notes=[]
    for ident,kind in assignments.items():
        owner=owners[ident];prior=read(PRIOR[ident]) if ident in PRIOR else None
        member_ids=owner.get('component_current_ids',[])
        if kind=='unresolved_name':member_ids=prior['related_current_ids']
        if len(member_ids)!=len(set(member_ids)) or any(m not in owners or m==ident for m in member_ids):raise ValueError('Invalid explicit member/related identities')
        members=[{'id':m,'label':owners[m]['name'],'record_status':'released',
                  'relationship':'related_name_not_equated' if kind=='unresolved_name' else 'declared_component',
                  'scoped_width_record_count':counts[m],'width_values_inherited_by_parent':False} for m in member_ids]
        members += [{'id':p['proposed_id'],'label':p['name'],'record_status':'proposed','relationship':'proposed_basin_member',
                     'scoped_width_record_count':None,'width_values_inherited_by_parent':False}
                    for p in proposals if p.get('parent_current_id')==ident]
        source=prior['source_url'] if prior else ledger['sources'][owner['name_source']]
        report={'schema':'osw.current-measurement-object-scope.v1','current_id':ident,'name':owner['name'],
                'status':'editorial_measurement_scope_assessment_not_physical_taxonomy_admission','scope_kind':kind,
                'summary':ACTIONS[kind],'members':members,'source_registry_file':INDEX,
                'basis_object_sha256':hashlib.sha256(encoded({'owner':owner,'members':members,'prior_scope_audit':prior})).hexdigest(),
                'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_url':source,'source_locator':'Existing cited current ledger entry and explicit component links'+('; retained source-scope audit '+PRIOR[ident] if prior else ''),
                'source_access':'Existing cited ledger and retained scope evidence reviewed; no new field or original-page extraction claimed.',
                'prior_scope_audit_file':PRIOR.get(ident),'prior_width_decision':'width_not_assessed',
                'parent_width_km':None,'annual_width_range_km':None,'new_width_record_admitted':False,
                'member_measurements_inherited':False,'aliases_resolved':False,'physical_taxonomy_admitted':False,
                'physical_edge_geometry_admitted':False,'observation_date_inherited':False,
                'figure':figure_for(ident),'figure_alt':ACTIONS[kind]+' Relationships only; member measurements are not inherited.'}
        reports[path_for(ident)]=report;figures[figure_for(ident)]=diagram(report)
        note={'current_id':ident,'label':'Measurement object scope: '+kind.replace('_',' '),'audit_file':path_for(ident),
              'summary':ACTIONS[kind],'source_url':source,'source_locator':report['source_locator'],'observed_period':None,
              'measurement_scope_assessment':True,'related_current_ids':member_ids,
              'related_proposed_current_ids':[m['id'] for m in members if m['record_status']=='proposed']}
        notes.append(note)
    current=read(NOTES);base=[n for n in current['entries'] if not n.get('measurement_scope_assessment')]
    desired_notes=dict(current,entries=base+notes)
    index={'schema':'osw.current-measurement-object-scope-index.v1','status':'editorial_scope_assessments_not_measurement_admission',
           'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'protocol_file':PROTOCOL,'input_sha256':dict(FROZEN_INPUTS),'counts':dict(Counter(assignments.values())),
           'scope_notes_sha256':hashlib.sha256(encoded(desired_notes)).hexdigest(),
           'records':[{'current_id':r['current_id'],'source_file':p,'source_sha256':hashlib.sha256(encoded(r)).hexdigest(),
                       'document':r,'note':n,'figure_file':r['figure'],'figure_sha256':hashlib.sha256(figures[r['figure']]).hexdigest()}
                      for (p,r),n in zip(reports.items(),notes)]}
    return reports,figures,desired_notes,index

def verify():
    reports,figures,notes,index=build()
    expected={**{p:encoded(r) for p,r in reports.items()},**figures,NOTES:encoded(notes),INDEX:encoded(index)}
    for path,raw in expected.items():
        if (ROOT/path).read_bytes()!=raw:raise ValueError('Stale object-scope artifact: '+path)
    return index

if __name__=='__main__':
    reports,figures,notes,index=build()
    for path,raw in {**{p:encoded(r) for p,r in reports.items()},**figures,NOTES:encoded(notes),INDEX:encoded(index)}.items():
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    print(json.dumps({'assessments':len(reports),'categories':index['counts'],'widths_admitted':0}))
