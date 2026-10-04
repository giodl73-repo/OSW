"""Index route candidates against all currents lacking published ranked lengths."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "ocean-current-reference-path-candidates.json"
STRATEGIES = ROOT / "research" / "ocean-current-route-strategy-input.json"


def validate_generator(record: dict, expected_sha256: str) -> None:
    if record.get('generator_file') != 'analysis/build_current_reference_path_candidate.py' or record.get('generator_sha256') != expected_sha256:
        raise ValueError('Stale or missing candidate generator fingerprint; rebuild the route')


def validate_parent_scope(record: dict, ledger: dict) -> None:
    parent=record.get('parent_current_id')
    if parent is None:
        return
    current_id=record['current_id']
    if parent not in ledger or parent==current_id or ledger[current_id].get('part_of_current_id')!=parent or not isinstance(record.get('parent_scope_note'),str) or not record['parent_scope_note'].strip():
        raise ValueError('Candidate parent scope disagrees with current ledger')


def validate_strategies(document: dict, current_ids: set[str], basis_sha256: str) -> dict[str, str]:
    if document['basis_sha256'] != basis_sha256:
        raise ValueError('Stale route strategy evidence basis; review the planning assignments')
    strategy_ids = [row['id'] for row in document['strategies']]
    if len(strategy_ids) != len(set(strategy_ids)):
        raise ValueError('Duplicate route strategy definitions')
    assignments = document['assignments']
    counts = Counter(row['current_id'] for row in assignments)
    if set(counts) != current_ids or any(value != 1 for value in counts.values()):
        raise ValueError('Route strategies must cover every remaining current exactly once')
    if any(row['strategy_id'] not in strategy_ids for row in assignments):
        raise ValueError('Undefined route strategy assignment')
    if any('next_action' in row and (not isinstance(row['next_action'], str) or not row['next_action'].strip()) for row in assignments):
        raise ValueError('Per-current next action must be nonempty text')
    return {row['current_id']: row['strategy_id'] for row in assignments}


def ordering_sensitivity(candidates: list[dict]) -> dict[str, dict]:
    """Conservative positions using independent, rounded scenario envelopes.

    Touching intervals count as overlapping. These bounds describe the retained
    envelopes, not probabilities, uniform current scopes or an empirical rank.
    """
    comparable = [row for row in candidates if row['comparison_group'] == 'osw_approximate_reference_routes']
    result = {}
    for row in comparable:
        low, high = row['scenario_range_km']
        others = [other for other in comparable if other['id'] != row['id']]
        overlap = [other['id'] for other in others if other['scenario_range_km'][0] <= high and other['scenario_range_km'][1] >= low]
        result[row['id']] = {
            'overlapping_candidate_ids': overlap,
            'envelope_position_bounds': [
                1 + sum(other['scenario_range_km'][0] > high for other in others),
                1 + sum(other['scenario_range_km'][1] >= low for other in others),
            ],
            'interpretation': 'Conservative positions within retained rounded route envelopes, treating choices independently; touching envelopes overlap. Not a statistical rank interval or a uniform whole-current comparison.',
        }
    return result


def main() -> None:
    evidence_path = ROOT / "research" / "ocean-current-length-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    remaining = {row['current_id']: row for row in evidence['entries'] if not row['rank_eligible']}
    strategy_raw = STRATEGIES.read_bytes()
    planning = json.loads(strategy_raw)
    evidence_sha256 = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    assignments = validate_strategies(planning, set(remaining), evidence_sha256)
    ledger_path = ROOT / 'research' / 'ocean-current-almanac.json'
    ledger_raw = ledger_path.read_bytes()
    if planning['current_ledger_sha256'] != hashlib.sha256(ledger_raw).hexdigest():
        raise ValueError('Stale route strategy current ledger; review identity and scope assignments')
    ledger = {row['id']: row for row in json.loads(ledger_raw)['entries']}
    if not set(remaining) <= set(ledger):
        raise ValueError('Length evidence contains names absent from the current ledger')
    if {current_id for current_id in remaining if 'family' in ledger[current_id]['kind']} != {current_id for current_id, strategy in assignments.items() if strategy == 'split_basin_family'}:
        raise ValueError('Planning family assignments disagree with ledger identity kinds')
    strategies = {row['id']: row for row in planning['strategies']}
    candidates = []
    by_current = {}
    generator_sha256 = hashlib.sha256((ROOT / 'analysis/build_current_reference_path_candidate.py').read_bytes()).hexdigest()
    for path in sorted((ROOT / 'research').glob('*-reference-path-candidate.json')):
        raw = path.read_bytes()
        record = json.loads(raw)
        validate_generator(record, generator_sha256)
        current_id = record['current_id']
        if current_id not in remaining:
            raise ValueError(f'Candidate does not belong to remaining-current inventory: {current_id}')
        validate_parent_scope(record,ledger)
        if assignments[current_id] == 'split_basin_family':
            raise ValueError('A cross-basin family needs member routes, not a single family length')
        if record['rank_eligible_published_estimates'] is not False:
            raise ValueError('Editorial route cannot enter the published estimate ranking')
        if hashlib.sha256((ROOT / record['input_file']).read_bytes()).hexdigest() != record['input_sha256']:
            raise ValueError(f'Stale candidate input: {path.name}')
        row = {
            'id': path.stem,
            'current_id': current_id,
            'name': record['name'],
            'status': record['status'],
            'comparison_group': record['candidate_comparison_group'],
            'scope': record['scope'],
            'route_extent_kind': record['route_extent_kind'],
            'approximate_reference_path_km': record['reported_approximate_reference_path_km'],
            'scenario_range_km': record['reported_scenario_range_km'],
            'scenario_count': record['scenario_count'],
            'source_url': record['source_url'],
            'source_locator': record['source_locator'],
            'supporting_sources': record.get('supporting_sources', []),
            'candidate_file': path.relative_to(ROOT).as_posix(),
            'candidate_sha256': hashlib.sha256(raw).hexdigest(),
            'generator_sha256': record['generator_sha256'],
            'figure': record['figure'],
            'nominal_atlas_state_crossings': record['nominal_atlas_state_crossings'],
            'recommended_nasa_tile_id': record['recommended_nasa_tile_id'],
            'remaining_gates': record['remaining_gates'],
            'parent_current_id': record.get('parent_current_id'),
            'parent_scope_note': record.get('parent_scope_note'),
        }
        candidates.append(row)
        by_current.setdefault(current_id, []).append(row['id'])
    candidates.sort(key=lambda row: (-row['approximate_reference_path_km'], row['id']))
    sensitivity = ordering_sensitivity(candidates)
    for row in candidates:
        row['ordering_sensitivity'] = sensitivity.get(row['id'])
    reference_order = [row['id'] for row in candidates if row['comparison_group'] == 'osw_approximate_reference_routes']
    assignment_details = {item['current_id']: item for item in planning['assignments']}
    decisions = []
    for current_id, row in sorted(remaining.items(), key=lambda pair: pair[1]['name']):
        strategy_id = assignments[current_id]
        current = ledger[current_id]
        component_ids = current.get('component_current_ids', [])
        if any(component_id not in ledger for component_id in component_ids):
            raise ValueError('Planning navigation refers to an unknown component current')
        decisions.append({
            'current_id': current_id,
            'name': row['name'],
            'existing_length_evidence_status': row['status'],
            'existing_scope': row['scope'],
            'name_source_url': row['name_source_url'],
            'candidate_ids': by_current.get(current_id, []),
            'reference_path_decision': 'editorial_candidate_present_scientific_review_pending' if current_id in by_current else 'reference_path_not_constructed',
            'published_length_rank_eligible': False,
            'ledger_kind': current['kind'],
            'route_strategy_id': strategy_id,
            'route_strategy_label': strategies[strategy_id]['label'],
            'planning_status': planning['status'],
            'planning_basis': row['scope'],
            'next_action': 'Review the existing editorial route against scientific gates; broader/system/family scope remains governed by the planning strategy.' if current_id in by_current else assignment_details[current_id].get('next_action', strategies[strategy_id]['next_action']),
            'strategy_next_action': strategies[strategy_id]['next_action'],
            'known_component_currents': [{'current_id': component_id, 'name': ledger[component_id]['name']} for component_id in component_ids],
            'component_inventory_status': 'known_component_records_not_complete_census' if component_ids else ('no_component_records_in_current_ledger' if strategy_id == 'split_basin_family' else 'not_assessed_by_this_planning_crosswalk'),
        })
    strategy_counts = Counter(row['route_strategy_id'] for row in decisions)
    unbuilt_counts = Counter(row['route_strategy_id'] for row in decisions if not row['candidate_ids'])
    result = {
        'schema': 'osw.current-reference-path-candidates.v1',
        'status': 'editorial_candidates_not_canonical_length_admissions',
        'counts': {'currents_without_published_ranked_estimate': len(remaining), 'currents_with_route_candidates': len(by_current), 'currents_without_route_candidates': len(remaining) - len(by_current), 'route_candidates': len(candidates), 'studied_reach_candidates': sum(row['comparison_group'] == 'osw_studied_reach_routes' for row in candidates)},
        'comparison_rule': 'Descending length of declared OSW reference routes only. Coherent jets, specified branches and source/region-defined extents differ in scope; their order is provisional and is not a uniform whole-current ranking. Studied reaches are excluded from the reference-route order. No number replaces the existing length evidence or published ranking.',
        'reference_route_length_order': reference_order,
        'length_evidence_sha256': evidence_sha256,
        'planning_taxonomy': {
            'status': planning['status'], 'author': planning['author'], 'scope': planning['scope'],
            'input_file': STRATEGIES.relative_to(ROOT).as_posix(), 'input_sha256': hashlib.sha256(strategy_raw).hexdigest(),
            'current_ledger_sha256': hashlib.sha256(ledger_raw).hexdigest(), 'parent_taxonomy': planning['parent_taxonomy'],
            'strategies': [{**strategy, 'current_count': strategy_counts[strategy['id']], 'unbuilt_count': unbuilt_counts[strategy['id']]} for strategy in planning['strategies']],
        },
        'candidates': candidates,
        'remaining_current_decisions': decisions,
    }
    # Audit before writing the catalog: rejected candidates cannot replace it.
    from check_current_measurement_protocol import main as audit_protocol
    audit = audit_protocol()
    result['measurement_protocol'] = {
        'version': audit['protocol_version'],
        'file': audit['protocol_file'],
        'sha256': audit['protocol_sha256'],
        'audit_file': 'research/ocean-current-measurement-protocol-audit.json',
        'audit_sha256': hashlib.sha256((ROOT / 'research/ocean-current-measurement-protocol-audit.json').read_bytes()).hexdigest(),
        'status': audit['status'],
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Indexed {len(candidates)} route candidates for {len(by_current)} of {len(remaining)} currents; {len(remaining) - len(by_current)} awaiting routes")
    from build_reference_route_state_join import main as refresh_state_routes
    refresh_state_routes()
    from build_motion_dashboard import main as refresh_dashboard
    refresh_dashboard()


if __name__ == '__main__':
    main()
