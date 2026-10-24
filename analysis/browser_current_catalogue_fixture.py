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
