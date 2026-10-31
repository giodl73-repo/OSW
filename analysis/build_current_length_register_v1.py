"""Assemble the length worklist from retained source records, without runtime I/O.

This register does not turn a sampled reach into a whole-current estimate.
It makes the existing numbers usable and identifies the routes still to finish.
"""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH='research/current-length-estimate-register-v1.json'
CSV_PATH='research/current-length-estimate-register-v1.csv'


def apply_family_conventions(rows, document):
    by_id={r['entity_id']:r for r in rows}
    seen=set()
    for definition in document['conventions']:
        owner=definition['entity_id'];ids=definition['members']
        if owner in seen or len(ids)!=len(set(ids)) or owner in ids:
            raise ValueError('Duplicate or recursive length components')
        seen.add(owner);target=by_id[owner]
        if target['length_estimate_km'] is not None:raise ValueError('Convention would overwrite an existing estimate')
        members=[by_id[i] for i in ids]
        if any(m['identity_level']=='family' or m['status'] in ['family_principal_member','system_segment_sum'] or not m['length_estimate_km'] for m in members):
            raise ValueError('Every component must have an existing non-aggregate reference extent')
        rule=definition['convention']
        selected=None
        if rule=='longest_catalogued_member':
            if target['identity_level']!='family':raise ValueError('Principal-member convention requires family owner')
            selected=sorted(members,key=lambda m:(-m['length_estimate_km'],m['entity_id']))[0]
            value=selected['length_estimate_km'];status='family_principal_member'
            scope=f"Principal catalogued member: {selected['name']} ({selected['entity_id']}). "+definition['scope_note']+' '+document['family_rule']
        elif rule=='distinct_segment_sum':
            if target['identity_level']!='system':raise ValueError('Segment sum requires a system owner')
            value=sum(m['length_estimate_km'] for m in members);status='system_segment_sum'
            scope=definition['scope_note']
        else:raise ValueError('Unknown family/system length convention')
        target.update(status=status,length_estimate_km=value,method=rule,scope=scope,
            length_convention=rule,selected_member_id=selected['entity_id'] if selected else None,
            record_file='research/current-length-family-conventions-v1.json',
            selected_route_id=selected['selected_route_id'] if selected else None,
            source_url=document['source_url'],source_locator=definition.get('source_locator','Declared member inventory and principal-member selection rule; every member source retained below.'),
            figure_file=selected.get('figure_file') if selected else None,
            conditional_extent=bool(selected and selected.get('conditional_extent')),
            geographic_screening=('Selected member only: '+selected['geographic_screening']) if selected and selected.get('geographic_screening') else None,
            source_time_convention='Member periods/phases differ; no simultaneous global axis or measured annual range. '+(selected.get('source_time_convention') or '') if selected else 'Combines segment descriptions/reference route with different source periods; not a simultaneous observed axis.',
            identity_interpretation=document['inventory_limits'],
            route_sensitivity_km=selected['route_sensitivity_km'] if selected else None,
            route_choice_rule=document['family_rule'] if selected else 'Sum only the three explicitly non-overlapping strict segments; source-reported numerical descriptions stay fixed. No annual range or statistical uncertainty inferred.',
            needs_full_extent_estimate=False,
            length_components=[{k:m.get(k) for k in ['entity_id','name','length_estimate_km','method','scope','record_file','source_url','source_locator','selected_route_id','source_time_convention','route_sensitivity_km','conditional_extent','figure_file','current_card_url']} for m in members])
    return rows


def build():
    pins={}
    def read(path):
        raw=(ROOT/path).read_bytes();pins[path]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    baseline=read('research/current-measurement-coverage-baseline-v1.json')
    identities={r['id']:r for r in baseline['records']}
    basin=read('research/equatorial-basin-identity-query-contract-v3.json')
    for row in basin['additions']['objects']:
        if row['id'] in identities:raise ValueError('Duplicate current identity')
        identities[row['id']]=row
    if len(identities)!=111:raise ValueError('The complete111-current inventory is required')
    lengths=read('research/ocean-current-live-measurements.json')
    reported={r['entity_id']:r for r in lengths['length_assessments'] if r.get('published_length_km') is not None}
    if len(reported)!=13:raise ValueError('All13 existing reported-length owners required')
    hypotheses={r['entity_id']:r for r in lengths['length_assessments'] if r.get('proposed_system_length_km') is not None}
    if set(hypotheses)!={'current:greenland-middle-atlantic-shelf-hypothesis'}:raise ValueError('Review proposed-system inventory before changing its length convention')
    routes={}
    def add(row,path):
        row=dict(row);owner=row.get('current_id')
        if not owner:return
        if not owner.startswith('current:'):owner='current:'+owner
        if owner not in identities:raise ValueError('Unknown route owner: '+owner)
        identifier=row.get('id',row.get('route_id'))
        if not identifier:raise ValueError('Missing route identity')
        if identifier in routes:raise ValueError('Duplicate reference route: '+identifier)
        value=row.get('approximate_reference_path_km',row.get('reported_approximate_reference_path_km'))
        if not isinstance(value,(int,float)) or value<=0:raise ValueError('Missing positive route calculation')
        routes[identifier]={'id':identifier,'entity_id':owner,'length_km':value,
            'extent_class':'reference_extent' if row.get('comparison_group')=='osw_approximate_reference_routes' else 'regional_reach',
            'scope':row.get('scope',''),'scenario_range_km':row.get('scenario_range_km',row.get('reported_scenario_range_km')),
            'source_url':row.get('source_url'),'source_locator':row.get('source_locator'),
            'record_file':path,'route_card_url':'reference-routes.html#'+identifier}
    path='research/ocean-current-reference-path-candidates.json'
    for row in read(path)['candidates']:add(row,path)
    for path in ['research/south-java-reference-query-contract-v1.json','research/pacific-secc-reference-query-contract-v1.json','research/wicc-winter-reference-query-contract-v1.json']:
        add(read(path)['route'],path)
    for path in ['research/atlantic-nsec-reference-query-contract-v2.json','research/current-reference-profile-batch-query-contract-v1.json']:
        for row in read(path)['routes']:add(row,path)
    path='research/eicc-reference-query-contract-v1.json'
    for row in read(path)['collections']['reference_routes']:add(row,path)
    for path,identifier in [('research/nwasc-source-anchor-reference-route.json',None),('research/southern-east-madagascar-coastal-reference-curve.json','southern-east-madagascar-coastal-reference-curve')]:
        row=read(path)
        if identifier:row['id']=identifier
        add(row,path)
    if len(routes)!=87:raise ValueError('All87 prepared reference routes required')
    provisional={}
    for version in [1,2,3,4,5,7]:
        extent_path=f'research/current-length-reference-extents-v{version}.json'
        extents=read(extent_path);geography=read(f'research/current-length-reference-extents-geography-v{version}.json')
        if geography['estimate_file_sha256']!=pins[extent_path] or not all(r['all_clear'] and r['scenarios']==r['coarse_land_clear']==36 for r in geography['records']):raise ValueError('Exact geographic screening required')
        if {r['entity_id'] for r in extents['records']}!={r['entity_id'] for r in geography['records']}:raise ValueError('Incomplete screening owners')
        for item in extents['records']:
            if item['entity_id'] in provisional:raise ValueError('Duplicate new estimate')
            provisional[item['entity_id']]={**item,'record_file':extent_path,'figure_file':'figures/atlantic-basin-current-length-estimates-v1.svg' if version==1 else f'figures/{item["map_group"]}-current-length-estimates-v{version}.svg'}
    rows=[]
    for identifier,current in sorted(identities.items()):
        options=sorted([r for r in routes.values() if r['entity_id']==identifier],key=lambda r:(r['extent_class']!='reference_extent',-r['length_km'],r['id']))
        full=[r for r in options if r['extent_class']=='reference_extent']
        publication=reported.get(identifier) or hypotheses.get(identifier)
        is_hypothesis=identifier in hypotheses
        chosen=full[0] if full else None
        draft=provisional.get(identifier) if not publication and not chosen else None
        status='reported' if publication else 'reference_estimate' if chosen else 'regional_only' if options else 'needs_route'
        value=(publication['proposed_system_length_km'] if is_hypothesis else publication['published_length_km']) if publication else chosen['length_km'] if chosen else None
        if is_hypothesis:status='reported_hypothesis'
        if draft:status='provisional_estimate';value=draft['length_estimate_km']
        rows.append({'entity_id':identifier,'name':current['label'],'basin':current.get('basin'),
            'identity_level':current.get('identity_level','current'),'status':status,'length_estimate_km':value,
            'method':'source_reported_hypothesis' if is_hypothesis else 'source_reported_extent' if publication else 'WGS84_editorial_reference_route' if chosen or draft else None,
            'scope':publication['scope'] if publication else chosen['scope'] if chosen else draft['scope'] if draft else None,
            'selected_route_id':chosen['id'] if chosen and not publication else draft['id'] if draft else None,
            'reported_length_source_id':publication.get('length_source_id') if publication else None,
            'reported_length_source_locator':publication.get('length_source_locator') if publication else None,
            'record_file':'research/ocean-current-live-measurements.json' if publication else chosen['record_file'] if chosen else draft['record_file'] if draft else None,
            'source_url':'https://doi.org/10.1175/1520-0485(1989)019<0384:OTOOSW>2.0.CO;2' if is_hypothesis else chosen['source_url'] if chosen and not publication else draft['source_url'] if draft else None,
            'source_locator':chosen['source_locator'] if chosen and not publication else draft.get('source_locator') if draft else None,
            'figure_file':draft['figure_file'] if draft else None,
            'geographic_screening':'All36 variants clear coarse OSW land; fine coast not checked.' if draft else None,
            'source_time_convention':draft['source_time_convention'] if draft else None,
            'gate_rationale':draft.get('gate_rationale') if draft else None,
            'drawing_constraint':draft.get('fixed_drawing_vertex_rationale') if draft else None,
            'source_typography_note':draft.get('source_typography_note') if draft else None,
            'identity_interpretation':draft.get('identity_interpretation') if draft else None,
            'conditional_extent':is_hypothesis or bool(draft and draft.get('conditional_extent')),
            'route_sensitivity_km':draft['scenario_range_km'] if draft else chosen['scenario_range_km'] if chosen else None,
            'route_choice_rule':'Longest declared reference-extent route; all phase/definition alternatives retained. This is not a maximum annual length.' if chosen and not publication else None,
            'route_options':options,'available_regional_reach_km':max((r['length_km'] for r in options if r['extent_class']=='regional_reach'),default=None),
            'scenario_range_is_physical_uncertainty':False,'annual_length_range_km':None,
            'needs_full_extent_estimate':value is None,
            'current_card_url':'object.html?id='+identifier.replace(':','%3A')})
    rows=apply_family_conventions(rows,read('research/current-length-family-conventions-v1.json'))
    counts=Counter(r['status'] for r in rows)
    return {'schema':'osw.current-length-estimate-register.v1','status':'ALL_LENGTH_ENTRIES_AVAILABLE_REVIEW_PENDING' if all(r['length_estimate_km'] is not None for r in rows) else 'LENGTH_FIRST_WORKING_REGISTER_INCOMPLETE',
        'target':'A declared, reproducible length estimate for every catalogued current.',
        'counts':{'currents':len(rows),'with_length_estimate':sum(r['length_estimate_km'] is not None for r in rows),'remaining_full_extent_estimates':sum(r['needs_full_extent_estimate'] for r in rows),**dict(counts)},
        'rules_file':'plans/current-length-estimates-v1.md','rules_sha256':hashlib.sha256((ROOT/'plans/current-length-estimates-v1.md').read_bytes()).hexdigest(),
        'generator_file':'analysis/build_current_length_register_v1.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':pins,
        'interpretation':['Reported values and editorial reference estimates retain different methods and extents.','Regional reaches remain visible as supporting calculations but do not fill a whole-current estimate.','Endpoint/route sensitivity is not annual variation or statistical uncertainty.','Family/system estimates require an explicit principal-route or aggregate convention before they are filled.'],
        'full_goal_complete':False,'records':rows}


def main():
    value=build();(ROOT/JSON_PATH).write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode())
    output=io.StringIO(newline='');fields=['entity_id','name','basin','identity_level','status','length_estimate_km','method','scope','length_convention','selected_member_id','selected_route_id','available_regional_reach_km','needs_full_extent_estimate']
    writer=csv.DictWriter(output,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(value['records'])
    (ROOT/CSV_PATH).write_bytes(output.getvalue().encode('utf8'))
    print(json.dumps(value['counts']))


if __name__=='__main__':main()
