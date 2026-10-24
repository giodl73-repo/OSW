"""Independent accepted IDs for current catalogue and atlas delivery checks.

Reads only small committed identity documents, never the query packet/index.
The historical catalogue remains unchanged; the checked coastal contract adds
four separate identities. Its unresolved East Gyral candidate is excluded.
"""
import json


def expected_current_ids(root):
    base = json.loads((root / 'research/ocean-current-effective-catalogue.json').read_bytes())
    coastal = json.loads((root / 'research/indian-current-identity-query-contract-v1.json').read_bytes())
    old = [row['id'] for row in base['entries']]
    new = [row['id'] for row in coastal['additions']['entities']]
    if (len(old) != base['current_count'] or len(old) != 102 or len(new) != 4
            or sorted(new) != sorted(coastal['proposed_entity_ids'])
            or len(set(old + new)) != len(old) + len(new)):
        raise ValueError('Changed or duplicate accepted catalogue identity inventory')
    return sorted(old + new)


def expected_proposal_ids(root):
    document = json.loads((root / 'research/ocean-current-inventory-expansion-candidates.json').read_bytes())
    ids = [row['proposed_id'] for row in document['entries']]
    if len(set(ids)) != len(ids):raise ValueError('Duplicate proposed current identity')
    accepted = {value.removeprefix('current:') for value in expected_current_ids(root)}
    return sorted(set(ids) - accepted)


def expected_reference_route_ids(root):
    """Historical cards plus the separately admitted NWASC source connection."""
    base=json.loads((root/'research/ocean-current-working-reference-routes.json').read_bytes())
    addition=json.loads((root/'research/nwasc-source-anchor-reference-route.json').read_bytes())
    old=[row['id'] for row in base['candidates']]
    route=addition['route_record']
    if (len(old)!=77 or base['counts']['route_candidates']!=77
            or len(set(old))!=len(old)
            or addition['current_id']!='norwegian-atlantic-slope'
            or route['id']!='norwegian-atlantic-slope-asar-regional-reference-route'
            or route['comparison_group']!='osw_source_anchor_connections'
            or route['id'] in old):
        raise ValueError('Changed or duplicate historical/admitted route inventory')
    return sorted([*old,route['id']])


def assert_route_planning_projection(root, actual, historical):
    """Check the complete declared identity extension without changing routes."""
    plans=json.loads((root/'research/indian-current-reference-route-planning-v1.json').read_bytes())['entries']
    revised={'counts','effective_accepted_current_count','remaining_current_decisions','planning_taxonomy'}
    assert set(actual)==set(historical)|{'planning_extension_version'}
    assert {k:v for k,v in actual.items() if k not in revised|{'planning_extension_version'}}=={
        k:v for k,v in historical.items() if k not in revised}
    assert actual['remaining_current_decisions']==historical['remaining_current_decisions']+plans
    assert {k:v for k,v in actual['planning_taxonomy'].items() if k!='strategies'}=={
        k:v for k,v in historical['planning_taxonomy'].items() if k!='strategies'}
    strategies=actual['planning_taxonomy']['strategies'];old=historical['planning_taxonomy']['strategies']
    assert strategies[:len(old)]==old
    assert strategies[len(old):]==[{'id':'source_axis_definition_required','label':plans[0]['route_strategy_label'],
                                   'description':plans[0]['planning_basis'],'current_count':4,'unbuilt_count':4}]
    assert actual['effective_accepted_current_count']==len(expected_current_ids(root))==106
    changed_counts={'accepted_current_names','currents_without_any_reference_card','currents_without_route_candidates',
                    'currents_without_published_ranked_estimate','route_decision_records'}
    assert {k:v for k,v in actual['counts'].items() if k not in changed_counts}=={
        k:v for k,v in historical['counts'].items() if k not in changed_counts}
    for key,value in {'accepted_current_names':106,'currents_without_any_reference_card':34,
                      'currents_without_route_candidates':23,'currents_without_published_ranked_estimate':93,
                      'route_decision_records':95}.items():
        assert actual['counts'][key]==value,key
    assert actual['planning_extension_version']=='indian-coastal-brazil-t24-v1'
