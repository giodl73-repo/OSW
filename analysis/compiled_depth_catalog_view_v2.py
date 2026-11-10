"""Read admitted v33 entries without following native science provenance."""
import copy,json
import compiled_depth_catalog_view_v1 as previous
from load_current_depth_reference_inventory_v1 import checked_piece

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v33':return previous.load_inventory(manifest,reader)
    view=load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    previous.append(view,manifest['reference_addendum'],reader)
    missing=json.loads(checked_piece(manifest['unresolved_contexts'],reader))
    if len(missing['contexts'])!=3 or any(c['lower_depth_m'] is not None or c['canonical_reference_admitted'] is not False for c in missing['contexts']):
        raise ValueError('Three unresolved contexts must remain outside canonical entries')
    previous.check_counts(view,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    view.update(copy.deepcopy(manifest['view_metadata']));return view
