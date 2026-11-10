"""Typed v41 extension; frozen v3 handles every previously admitted packet."""
import copy,json
from compiled_depth_catalog_view_v3 import load_inventory as previous,append,check_counts,metadata_only
from load_current_depth_reference_inventory_v1 import checked_piece

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v41':return previous(manifest,reader)
    metadata_only(manifest)
    prior=json.loads(checked_piece(manifest['previous_inventory'],reader))
    if prior['schema']!='osw.current-depth-reference-inventory.v40':raise ValueError('Exact latest v40 predecessor required')
    view=previous(prior,reader)
    append(view,manifest['reference_addendum'],reader)
    check_counts(view,manifest);view.update(copy.deepcopy(manifest['view_metadata']));return view
