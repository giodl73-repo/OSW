"""Project registered object provenance without counting supporting metadata."""
import copy


def project(owner, source_registry, evidence_rows):
    """Return a new owner; callers supply every owned evidence row before admission.

    Registered references are counted, not independent datasets or observations.
    This prepares a consistent projection; it does not infer source completeness.
    """
    identity = owner['id']
    if not isinstance(identity, str):
        raise ValueError('Object identity must be a string')
    registry = list(source_registry)
    if any(not isinstance(ref, str) for ref in registry) or len(registry) != len(set(registry)):
        raise ValueError('Invalid or duplicate registered source identities')
    registered = set(registry)
    refs = set()
    for row in [owner, *evidence_rows]:
        if row is not owner:
            owned = identity in [row.get('id'), row.get('entity_id'), row.get('subject_id'), row.get('object_id')]
            if identity.startswith('current:'):
                owned = owned or row.get('current_id') == identity.removeprefix('current:')
            if not owned:
                raise ValueError('Evidence row is not associated with this object')
        multiple = row.get('source_ids', [])
        if (not isinstance(multiple, list) or any(not isinstance(ref, str) for ref in multiple)
                or len(multiple) != len(set(multiple))):
            raise ValueError('Invalid or duplicate source reference list')
        refs.update(multiple)
        for key in ['source_id', 'source_snapshot_id', 'method_source_id']:
            ref = row.get(key)
            if ref is not None:
                if not isinstance(ref, str):
                    raise ValueError('Invalid source reference identity')
                refs.add(ref)
    if refs-registered:
        raise ValueError('Unresolved source references: '+', '.join(sorted(refs-registered)))
    result = copy.deepcopy(owner)
    result['source_ids'] = sorted(refs)
    result['linked_source_count'] = len(refs)
    return result
