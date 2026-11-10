"""Stage complete owner-source projections after all provider adapters append."""
import copy

from object_source_links import project

REQUIRED = ('entities', 'measurements', 'claims', 'geometries', 'media', 'reference_routes')


def prepare(collections):
    """Return replacement objects and an audit; never mutate any input.

    Root source_id/source_ids/source_snapshot_id/method_source_id references
    are collected across all supplied owned rows. Nested prose metadata is
    not a registered source. The caller must supply the final collections.
    """
    if any(name not in collections for name in ('objects', 'sources', *REQUIRED)):
        raise ValueError('Incomplete inventory source-projection inputs')
    if any(not isinstance(rows, list) for rows in collections.values()):
        raise ValueError('Inventory collections must be record lists')
    if any(not isinstance(row, dict) for rows in collections.values() for row in rows):
        raise ValueError('Inventory rows must be records')
    owners = collections['objects']
    identities = [row['id'] for row in owners]
    if any(not isinstance(i, str) for i in identities) or len(identities) != len(set(identities)):
        raise ValueError('Invalid or duplicate object identities')
    registry = [row['id'] for row in collections['sources']]
    if any(not isinstance(i, str) for i in registry) or len(registry) != len(set(registry)):
        raise ValueError('Invalid or duplicate source registry')
    owned = {identity: [] for identity in identities}
    for name, rows in collections.items():
        if name in ('objects', 'sources'):
            continue
        for row in rows:
            refs = {value for key in ('id', 'entity_id', 'subject_id', 'object_id')
                    if isinstance(value := row.get(key), str) and value in owned}
            current = row.get('current_id')
            if isinstance(current, str) and 'current:' + current in owned:
                refs.add('current:' + current)
            for identity in refs:
                owned[identity].append(row)
    replacements = []
    changes = []
    for owner in owners:
        result = project(owner, registry, owned[owner['id']])
        if (owner.get('source_ids') != result['source_ids']
                or owner.get('linked_source_count') != result['linked_source_count']):
            changes.append({
                'entity_id': owner['id'],
                'previous_source_ids': copy.deepcopy(owner.get('source_ids')),
                'previous_linked_source_count': owner.get('linked_source_count'),
                'source_ids': result['source_ids'].copy(),
                'linked_source_count': result['linked_source_count'],
                'owned_evidence_rows_inspected': len(owned[owner['id']]),
            })
        replacements.append(result)
    return replacements, {
        'schema': 'osw.inventory-source-projection-audit.v1',
        'objects_checked': len(owners), 'registered_source_references': len(registry),
        'changed_objects': changes, 'changed_object_count': len(changes),
        'independent_document_or_observation_count_inferred': False,
        'scope': 'Explicit registered references across supplied final collections; unchanged physical quantities, rights and source assets. Not a proof that all external evidence has been discovered.',
    }


def append(collections):
    """Replace objects only after the entire projection succeeds."""
    objects, audit = prepare(collections)
    collections['objects'] = objects
    return audit
