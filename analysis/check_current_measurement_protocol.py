"""Audit reproducible editorial conformance to OSW measurement protocol v1."""
import hashlib
import json
import math
import itertools
from datetime import date
import re
from shapely.geometry import LinearRing
from pathlib import Path
from build_current_reference_path_candidate import length_km, PROVINCES, TILES

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "plans/ocean-current-measurement-protocol-v1.md"
REPORT = ROOT / "research/ocean-current-measurement-protocol-audit.json"

def validate_family_inventory(audit, proposals, ledger, input_hashes):
    """Keep basin naming proposals separate from admitted physical identities."""
    if audit.get('schema') != 'osw.equatorial-basin-family-inventory-audit.v1' or audit.get('status') != 'editorial_identity_proposals_not_canonical':
        raise ValueError('Invalid family inventory audit scope')
    if set(input_hashes) != {'research/ocean-current-almanac.json', 'research/ocean-current-reference-path-candidates.json', 'plans/ocean-current-measurement-protocol-v1.md'} or audit.get('inputs_sha256') != input_hashes:
        raise ValueError('Stale family inventory audit basis')
    existing = {row['id'] for row in ledger}
    additions = {row['proposed_id']: row for row in proposals['entries']}
    sources = {row['id'] for row in audit['sources']}
    members = audit['proposed_members']
    if len({row['proposed_id'] for row in members}) != len(members):
        raise ValueError('Duplicate basin member proposal')
    for row in members:
        proposal = additions.get(row['proposed_id'])
        if row['proposed_id'] in existing or row['parent_current_id'] not in existing or row['source_id'] not in sources:
            raise ValueError('Invalid basin member identity or provenance')
        if not proposal or any(proposal.get(key) != row[key] for key in ['parent_current_id', 'basin', 'whole_current_length_km', 'current_width_km', 'rank_eligible']) or proposal['name'] != row['proposed_label']:
            raise ValueError('Basin member differs from proposal inventory')
        if any(row[key] is not None for key in ['geometry', 'layer_scope', 'temporal_scope', 'whole_current_length_km', 'current_width_km']) or row['rank_eligible'] is not False:
            raise ValueError('Naming evidence used as physical measurement')
    for held in audit['held_source_conventions']:
        if held['parent_current_id'] not in existing or held['possible_existing_current_id'] not in existing or held['source_id'] not in sources or held['comparison_source_id'] not in sources:
            raise ValueError('Invalid held naming convention reference')
        calendar = held['reported_name_calendar']
        if held['distinct_current_admitted'] is not False or held['rank_eligible'] is not False or any(held[key] is not None for key in ['geometry', 'whole_current_length_km', 'current_width_km']):
            raise ValueError('Held naming convention admitted as measurement')
        months = calendar['months']
        if calendar['role'] != 'glossary_name_usage_only' or calendar['supports_annual_route_geometry'] is not False or not months or len(set(months)) != len(months) or any(type(month) is not int or not 1 <= month <= 12 for month in months):
            raise ValueError('Invalid naming calendar or annual geometry claim')
    expected = {'canonical_currents_at_audit': len(ledger), 'families_reviewed': len({row['parent_current_id'] for row in members}), 'proposed_basin_members': len(members), 'source_convention_cases_on_hold': len(audit['held_source_conventions'])}
    if audit['counts'] != expected:
        raise ValueError('Incorrect family inventory counts')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_route_topology(row):
    topology=row.get('route_topology')
    if topology is None:return
    if topology!='closed_circuit':raise ValueError('Unsupported route topology')
    if row.get('circuit_anchor_role')!='arbitrary_repeat_vertex_not_origin':
        raise ValueError('Closed circuit needs an arbitrary anchor convention')
    direction=row.get('circuit_direction')
    if direction not in {'counterclockwise','clockwise'}:
        raise ValueError('Closed circuit needs a circulation direction')
    if any(row.get(key,[0])!=[0] for key in ['endpoint_latitude_offsets_degrees','start_longitude_offsets_degrees','end_longitude_offsets_degrees']):
        raise ValueError('Independent endpoint offsets cannot preserve a closed circuit')
    paths=[row['coordinates_lon_lat']]+[v['coordinates_lon_lat'] for v in row.get('alternative_routes',[])]+[s['coordinates_lon_lat'] for s in row.get('scenarios',[])]
    for path in paths:
        if len(path)<4 or path[0]!=path[-1]:raise ValueError('Closed circuit has an open path')
        ring=LinearRing(path)
        if not ring.is_simple or not ring.is_valid:raise ValueError('Closed circuit must be simple')
        if ring.is_ccw!=(direction=='counterclockwise'):raise ValueError('Closed circuit direction mismatch')

def validate_record(row):
    validate_route_topology(row)
    anchors = row.get('source_anchor_observations')
    if anchors is not None:
        if not isinstance(anchors, list) or not anchors:
            raise ValueError('Source anchor observations must be a nonempty list')
        ids = set()
        for anchor in anchors:
            if not isinstance(anchor, dict) or not isinstance(anchor.get('id'), str) or not anchor['id'].strip() or anchor['id'] in ids:
                raise ValueError('Source anchors need distinct identifiers')
            ids.add(anchor['id'])
            if anchor.get('geometry_role') != 'observed_front_crossing_not_current_axis' or anchor.get('time_precision') != 'month' or not isinstance(anchor.get('source_locator'), str) or not anchor['source_locator'].strip():
                raise ValueError('Frontal anchor role, precision or locator changed')
            point = anchor.get('longitude_latitude')
            if not isinstance(point, list) or len(point) != 2 or any(type(v) not in (int, float) or not math.isfinite(v) for v in point) or not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90) or point not in row['coordinates_lon_lat']:
                raise ValueError('Source anchor must be a declared nominal vertex')
            period = anchor.get('observed_period')
            if not isinstance(period, dict) or any(not isinstance(period.get(k), str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', period[k]) for k in ['start','end']):
                raise ValueError('Frontal anchor periods need month precision')
            if period['start'] > period['end']:
                raise ValueError('Frontal anchor period reversed')
            for value in (period['start'], period['end']):
                date.fromisoformat(value + '-01')
    convention=row.get('source_season_convention')
    if convention is not None:
        if not isinstance(convention,dict) or convention.get('label_basis') not in {'boreal','austral','source_defined'} or convention.get('role')!='source_observation_labels_only' or convention.get('supports_annual_route_geometry') is not False or not isinstance(convention.get('source_locator'),str) or not convention['source_locator'].strip():
            raise ValueError('Invalid source-season convention receipt')
        windows=convention.get('months_by_label')
        if not isinstance(windows,dict) or not windows:
            raise ValueError('Source seasons need explicit month windows')
        for label,months in windows.items():
            if not isinstance(label,str) or not label.strip() or not isinstance(months,list) or not months or any(type(month) is not int or not 1<=month<=12 for month in months) or len(set(months))!=len(months):
                raise ValueError('Invalid source-season month window')
    for key in ("current_id", "name", "scope", "layer", "time_convention", "coordinate_selection", "source_url", "source_locator", "source_citation", "source_retrieved_date", "scenario_rule", "geometry_role", "method"):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"Missing protocol metadata: {key}")
    try:
        date.fromisoformat(row["source_retrieved_date"])
    except ValueError as error:
        raise ValueError("Retrieval date must be an ISO calendar date") from error
    if row.get("crs") != "OGC:CRS84" or row.get("geometry_role") != "osw_editorial_reference_route":
        raise ValueError("Unexpected geometry definition")
    if row.get("status") != "editorial_reference_path_candidate_not_scientifically_reviewed" or row.get("rank_eligible_published_estimates") is not False:
        raise ValueError("Editorial admission boundary changed")
    if not row.get("remaining_gates"):
        raise ValueError("Missing independent review gates")
    if not row.get("scenarios") or len(row["scenarios"]) != row["scenario_count"]:
        raise ValueError("Incomplete scenario inventory")
    allow_seam = row.get("longitude_seam_policy") == "shortest_geodesic_periodic_display"
    nominal = length_km(row["coordinates_lon_lat"], allow_seam=allow_seam)
    if not math.isfinite(row["nominal_reference_path_km"]) or abs(nominal - row["nominal_reference_path_km"]) > .0011:
        raise ValueError("Nominal geodesic mismatch")
    variants = [{"id": "nominal", "coordinates_lon_lat": row["coordinates_lon_lat"]}] + row.get("alternative_routes", [])
    if len({v["id"] for v in variants}) != len(variants):
        raise ValueError("Duplicate route variant")
    offsets = [row["longitude_offsets_degrees"], row["endpoint_latitude_offsets_degrees"], row["endpoint_latitude_offsets_degrees"], row.get("start_longitude_offsets_degrees", [0]), row.get("end_longitude_offsets_degrees", [0])]
    if any(not values or 0 not in values or len(set(values)) != len(values) or any(not math.isfinite(v) for v in values) for values in offsets):
        raise ValueError("Invalid scenario grid")
    expected_paths = {}
    for variant, lon, start, end, start_lon, end_lon in itertools.product(variants, *offsets):
        path = [[x + lon, y] for x, y in variant["coordinates_lon_lat"]]
        path[0][1] += start
        path[-1][1] += end
        path[0][0] += start_lon
        path[-1][0] += end_lon
        if allow_seam:
            path = [[(x + 180) % 360 - 180, y] for x, y in path]
        expected_paths[(variant["id"], lon, start, end, start_lon, end_lon)] = path
    seen = set()
    lengths = []
    for scenario in row["scenarios"]:
        key = tuple(scenario[k] for k in ["route_variant_id", "longitude_offset_degrees", "start_latitude_offset_degrees", "end_latitude_offset_degrees", "start_longitude_offset_degrees", "end_longitude_offset_degrees"])
        if key in seen or key not in expected_paths or expected_paths[key] != scenario["coordinates_lon_lat"]:
            raise ValueError("Scenario differs from declared grid")
        seen.add(key)
        measured = length_km(scenario["coordinates_lon_lat"], allow_seam=allow_seam)
        if not math.isfinite(scenario["length_km"]) or abs(measured - scenario["length_km"]) > .00051:
            raise ValueError("Scenario geodesic mismatch")
        lengths.append(scenario["length_km"])
    if seen != set(expected_paths):
        raise ValueError("Scenario grid was truncated")
    if row["scenario_range_km"] != [min(lengths), max(lengths)]:
        raise ValueError("Raw scenario envelope mismatch")
    if not any(s["coordinates_lon_lat"] == row["coordinates_lon_lat"] for s in row["scenarios"]):
        raise ValueError("Nominal route absent from scenarios")
    increment = row["report_rounding_km"]
    if not math.isfinite(increment) or increment <= 0:
        raise ValueError("Invalid rounding increment")
    expected = [math.floor(min(lengths) / increment) * increment, math.ceil(max(lengths) / increment) * increment]
    if expected != row["reported_scenario_range_km"] or round(nominal / increment) * increment != row["reported_approximate_reference_path_km"]:
        raise ValueError("Rounding rule mismatch")
    if "avoid the coarse OSW atlas land mask" not in row.get("map_land_check", ""):
        raise ValueError("Missing land-check outcome")

def main():
    records = []
    for path in sorted((ROOT / "research").glob("*-reference-path-candidate.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        validate_record(row)
        for file_key, hash_key in (("input_file", "input_sha256"), ("generator_file", "generator_sha256")):
            if digest(ROOT / row[file_key]) != row[hash_key]:
                raise ValueError(f"Stale {file_key}: {path.name}")
        source = json.loads((ROOT / row["input_file"]).read_text(encoding="utf-8"))
        if any(row.get(key) != value for key, value in source.items()):
            raise ValueError(f"Report metadata differs from input: {path.name}")
        if digest(PROVINCES) != row["atlas_map_sha256"] or digest(TILES) != row["nasa_tiles_sha256"]:
            raise ValueError(f"Stale navigation geometry: {path.name}")
        records.append({"candidate_file": path.relative_to(ROOT).as_posix(), "candidate_sha256": digest(path), "scenario_count": row["scenario_count"]})
    if not records:
        raise ValueError("No candidates to audit")
    ledger_path = ROOT / "research/ocean-current-almanac.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))["entries"]
    proposals = json.loads((ROOT / "research/ocean-current-inventory-expansion-candidates.json").read_text(encoding="utf-8"))
    if proposals["current_ledger_sha256"] != digest(ledger_path):
        raise ValueError("Stale proposal inventory basis")
    ids = {r["id"] for r in ledger}
    names = {r["name"].casefold().replace(" ", "") for r in ledger}
    additions = proposals["entries"]
    family_audit = json.loads((ROOT / 'research/equatorial-basin-family-inventory-audit.json').read_bytes())
    validate_family_inventory(family_audit, proposals, ledger, {path: digest(ROOT / path) for path in family_audit['inputs_sha256']})
    if len({r["proposed_id"] for r in additions}) != len(additions) or len({r["name"].casefold().replace(" ", "") for r in additions}) != len(additions):
        raise ValueError("Duplicate proposed identity")
    for row in additions:
        if row["proposed_id"] in ids or row["name"].casefold().replace(" ", "") in names or row["whole_current_length_km"] is not None or row["rank_eligible"] is not False:
            raise ValueError("Proposal admitted or borrowed length")
    result = {"schema": "osw.current-measurement-protocol-audit.v1", "protocol_version": "1.2", "protocol_file": PROTOCOL.relative_to(ROOT).as_posix(), "protocol_sha256": digest(PROTOCOL), "status": "editorial_conformance_checks_passed_not_scientific_approval", "candidate_count": len(records), "scenario_count": sum(r["scenario_count"] for r in records), "proposed_identity_count": len(additions), "candidate_checks": records, "review_required": ["Source support and endpoint identity", "Layer/time and continuity", "Physical axis/bathymetric correspondence", "Sensitivity choice justification", "Comparability and canonical/publication admission"]}
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"OK: protocol v1.2; {len(records)} candidates; {result['scenario_count']} scenarios; {len(additions)} proposed identities")

    return result

if __name__ == "__main__":
    main()
