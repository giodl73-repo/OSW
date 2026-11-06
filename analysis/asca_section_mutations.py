"""Coherent source/projection alterations for native and WASM admission checks."""
import copy
import hashlib
import json

SOURCE = 'research/agulhas-asca-100m-monthly-sections.json'
CONTRACT = 'research/agulhas-asca-100m-query-contract.json'
MODES = ('mean', 'mask', 'paired_support', 'year', 'owner', 'geographic_edges',
         'annual_width', 'deleted_frame', 'owner_join', 'owner_count', 'changed_contract')


def corrupt(bundle, mode):
    if mode not in MODES:
        raise ValueError('Unknown ASCA alteration: '+mode)
    changed = copy.deepcopy(bundle)
    rows = changed['collections']['current_sections']
    row = rows[0]
    owner = next(o for o in changed['collections']['objects'] if o['id']=='current:agulhas')
    if mode == 'mean': row['field_statistics']['v']['mean'][100] += 1
    elif mode == 'mask': row['field_statistics']['v']['valid_count'][100] = 0
    elif mode == 'paired_support': row['paired_vector_statistics']['U']['valid_count'][100] = 0
    elif mode == 'year': row['year'] = 2017
    elif mode == 'owner': row['entity_id'] = 'current:loop'
    elif mode == 'geographic_edges': row['geographic_edges'] = [[28,-34],[30,-35]]
    elif mode == 'annual_width': row['annual_width_range_km'] = [50,200]
    elif mode == 'deleted_frame':
        removed = rows.pop()
        owner['current_section_ids'].remove(removed['id'])
        owner['capabilities']['current_sections'] -= 1
    elif mode == 'owner_join': owner['current_section_ids'].pop()
    elif mode == 'owner_count': owner['capabilities']['current_sections'] = 26
    elif mode == 'changed_contract': changed['manifest']['input_sha256'][CONTRACT] = '0'*64
    if mode not in ('owner_join', 'owner_count', 'changed_contract'):
        receipt = changed['manifest']['current_section_receipts'][SOURCE]
        document = json.loads(receipt['source_json'])
        document['frames'] = rows
        receipt['source_json'] = json.dumps(document)
        receipt['source_sha256'] = hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        changed['manifest']['input_sha256'][SOURCE] = receipt['source_sha256']
    return changed
