"""Typed v55 extension over the frozen v54 reader."""
import copy,json
from compiled_depth_catalog_view_v17 import load_inventory as previous
from compiled_depth_catalog_view_v3 import append,check_counts,metadata_only
from load_current_depth_reference_inventory_v1 import checked_piece

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v55':return previous(manifest,reader)
    metadata_only(manifest);prior=json.loads(checked_piece(manifest['previous_inventory'],reader))
    if prior['schema']!='osw.current-depth-reference-inventory.v54':raise ValueError('Exact v54 predecessor required')
    view=previous(prior,reader);append(view,manifest['reference_addendum'],reader)
    check_counts(view,manifest);view.update(copy.deepcopy(manifest['view_metadata']));return view
