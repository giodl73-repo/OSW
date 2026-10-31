"""Browser counts follow the verified working inventory, including unlocated names."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalogue = json.loads((ROOT / 'research/ocean-current-effective-catalogue.json').read_bytes())
measurements = json.loads((ROOT / 'research/ocean-current-measurements-aleutian-edition.json').read_bytes())
admission = json.loads((ROOT / 'research/norwegian-atlantic-slope-working-admission.json').read_bytes())
base = json.loads((ROOT / 'almanac/release/v0.1.0/entities.json').read_bytes())
CURRENT_IDS = {r['id'] for r in catalogue['entries']}
CURRENT_COUNT = len(CURRENT_IDS)
assert CURRENT_COUNT == len(catalogue['entries']) == catalogue['current_count']
MOTION_COUNT = CURRENT_COUNT + sum(r['type'] in ['named_eddy', 'operational_eddy_detection'] for r in base)
CURRENT_SELECT_OPTIONS = CURRENT_COUNT + 1  # Blank/all-currents option.
PENDING_PROPOSALS = admission['pending_current_proposals']
SCOPED_WIDTH_COUNT = len(measurements['widths'])
RANKED_LENGTH_COUNT = sum(r['rank_eligible'] for r in measurements['length_assessments'])

# Geographic gateway labels are a source-role subset, not all named eddies.
dashboard = json.loads((ROOT / 'research/ocean-motion-dashboard.json').read_bytes())
SHARED_GATEWAY_EDDY_IDS = {r['id'] for r in dashboard['entries'] if r['type'] != 'named_current'
                           and any(f['role'] == 'shared_regional_gateway' for f in r['map_features'])}

# Expected geographic marks derive from the checked source inventory.
MAPPED_MOTION_IDS={r['id'] for r in dashboard['entries'] if r['map_features']}
MAPPED_CURRENT_IDS=MAPPED_MOTION_IDS & CURRENT_IDS
MAPPED_MOTION_COUNT=len(MAPPED_MOTION_IDS)
MAPPED_CURRENT_COUNT=len(MAPPED_CURRENT_IDS)
REFERENCE_ROUTE_COUNT=sum(r['capabilities']['reference_route'] for r in dashboard['entries'])
REFERENCE_ROUTE_OWNERS=sum(r['capabilities']['reference_route']>0 for r in dashboard['entries'])
