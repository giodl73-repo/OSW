"""Invert declared editorial route crossings into a state-first inventory."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/ocean-current-reference-route-state-join.json'


def crossing_summary(record, state_ids, apply_exclusions=True):
    """Counts describe a declared sensitivity grid, never probability or occupancy."""
    nominal = set(record['nominal_atlas_state_crossings'])
    scenarios = record['scenarios']
    if not scenarios or len(scenarios) != record['scenario_count']:
        raise ValueError('Incomplete route scenario inventory')
    counts = Counter()
    for scenario in scenarios:
        codes = scenario['atlas_state_crossings']
        if len(codes) != len(set(codes)):
            raise ValueError('Duplicate state crossing within a scenario')
        counts.update(codes)
    if not nominal <= set(counts) or not (nominal | set(counts)) <= state_ids:
        raise ValueError('Unknown state or nominal crossing absent from scenarios')
    exclusions=record.get('state_semantic_exclusions',[])
    excluded={row['state_code'] for row in exclusions}
    if len(excluded)!=len(exclusions) or not excluded<=state_ids or any(not isinstance(row.get('reason'),str) or not row['reason'].strip() for row in exclusions):
        raise ValueError('Invalid declared state semantic exclusions')
    return {code: {'nominal_crossing': code in nominal,
                   'crossing_scenario_count': count,
                   'scenario_count': len(scenarios),
                   'crosses_in_all_declared_scenarios': count == len(scenarios)}
            for code, count in sorted(counts.items()) if not apply_exclusions or code not in excluded}


def main():
    inputs = {}
    def read(relative):
        raw = (ROOT / relative).read_bytes()
        inputs[relative] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    catalog = read('research/ocean-current-reference-path-candidates.json')
    atlas = read('research/ocean-motion-state-join.json')
    states = {code: {'name': state['name'], 'route_candidates': []}
              for code, state in atlas['states'].items()}
    excluded_contacts=[]
    for row in catalog['candidates']:
        record = read(row['candidate_file'])
        if inputs[row['candidate_file']] != row['candidate_sha256']:
            raise ValueError('Stale reference route catalog')
        raw=crossing_summary(record,set(states),apply_exclusions=False)
        for exclusion in record.get('state_semantic_exclusions',[]):
            code=exclusion['state_code']
            if code in raw:excluded_contacts.append({'candidate_id':row['id'],**exclusion,**raw[code]})
        for code, summary in crossing_summary(record, set(states)).items():
            states[code]['route_candidates'].append({
                'candidate_id': row['id'], 'current_id': row['current_id'],
                'name': row['name'], 'scope': row['scope'],
                'layer': record['layer'], 'time_convention': record['time_convention'],
                'comparison_group': row['comparison_group'],
                'route_extent_kind': row['route_extent_kind'],
                'route_url': 'reference-routes.html#' + row['id'],
                'source_url': row['source_url'], **summary,
            })
    for state in states.values():
        state['route_candidates'].sort(key=lambda row: (row['name'].casefold(), row['candidate_id']))
        state['current_count'] = len({row['current_id'] for row in state['route_candidates']})
        state['nominal_current_count'] = len({row['current_id'] for row in state['route_candidates'] if row['nominal_crossing']})
    result = {'schema': 'osw.current-reference-route-state-join.v1',
              'status': 'editorial_route_display_crossings_not_physical_passage',
              'method': 'Invert stored nominal and all declared scenario crossings of the approximate OSW display-state shapes. No velocity, width, footprint, residence or transport is diagnosed.',
              'scenario_count_meaning': 'Counts within an editorial sensitivity grid; not probabilities, dated frequency, confidence or seasonal occupancy.',
              'absence_meaning': 'No candidate crossing recorded; physical current passage remains unresolved.',
              'counts': {'states': len(states), 'route_candidates': len(catalog['candidates']),
                         'currents_with_route_candidates': catalog['counts']['currents_with_route_candidates'],
                         'states_with_candidate_crossings': sum(bool(s['route_candidates']) for s in states.values()),
                         'candidate_state_pairs': sum(len(s['route_candidates']) for s in states.values())},
              'excluded_display_contacts':excluded_contacts,
              'input_sha256': inputs, 'states': states}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Built route/state inventory: {result['counts']}")
    return result


if __name__ == '__main__':
    main()
