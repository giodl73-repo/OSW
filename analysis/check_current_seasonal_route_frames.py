"""Check seasonal associations against existing scoped route candidates."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def validate(document, reports, widths):
    frames = document["frames"]
    width_by_id = {row['id']: row for row in widths['measurements']}
    if len({row["id"] for row in frames}) != len(frames):
        raise ValueError("Duplicate seasonal frame")
    for frame in frames:
        report = reports[frame["route_candidate_file"]]
        if frame["current_id"] != report["current_id"] or frame["geometry_role"] != report["geometry_role"]:
            raise ValueError("Frame identity/geometry mismatch")
        for key in ["time_convention", "layer", "source_url", "source_locator"]:
            if frame[key] != report[key]:
                raise ValueError("Seasonal evidence differs from pinned route")
        if not frame["phase_label"] or frame["flow_direction"] not in ["northward", "southward", "eastward", "westward"]:
            raise ValueError("Unsupported pilot frame attributes")
        start, end = report['coordinates_lon_lat'][0], report['coordinates_lon_lat'][-1]
        delta_lon = (end[0] - start[0] + 180) % 360 - 180
        delta_lat = end[1] - start[1]
        progress = {'northward': delta_lat, 'southward': -delta_lat,
                    'eastward': delta_lon, 'westward': -delta_lon}
        if progress[frame['flow_direction']] <= 0:
            raise ValueError('Seasonal direction disagrees with oriented regional route')
        if 'source_season_label' in frame:
            convention = report.get('source_season_convention', {})
            if convention.get('months_by_label', {}).get(frame['source_season_label']) != frame['calendar_months']:
                raise ValueError('Seasonal calendar differs from source convention')
        width_ids = frame['width_measurement_ids']
        if len(set(width_ids)) != len(width_ids) or len(width_ids) > 1:
            raise ValueError('Duplicate or unaggregated frame widths')
        for identifier in width_ids:
            width = width_by_id.get(identifier)
            if width is None or width['current_id'] != frame['current_id'] or width['source_url'] != frame['source_url'] or width.get('calendar_months') != frame['calendar_months'] or width['phase_label'] != frame['phase_label'] or width['phase_kind'] != 'seasonal_summary' or width['whole_current_representative'] is not False or width['width_rank_eligible'] is not False:
                raise ValueError('Incompatible frame width context')
            if frame.get('width_support_role') != 'regional_source_context_not_uniform_route_width' or not frame.get('width_scope_note', '').strip():
                raise ValueError('Uniform route width inference forbidden')
        months = frame["calendar_months"]
        if months is not None and (not months or len(set(months)) != len(months) or any(type(m) is not int or not 1 <= m <= 12 for m in months)):
            raise ValueError("Invalid seasonal calendar")
    ids = {row["current_id"] for row in frames}
    if document["counts"] != {"currents": len(ids), "frames": len(frames)}:
        raise ValueError("Frame count mismatch")
    comparisons = document["comparability"]
    if len(comparisons) != len(ids) or {r["current_id"] for r in comparisons} != ids:
        raise ValueError("Missing comparability decision")
    for row in comparisons:
        if row["annual_extrema_eligible"] is not False or row["annual_length_range_km"] is not None or row["annual_width_range_km"] is not None or not row["reason"]:
            raise ValueError("Different scoped components cannot define annual extrema")

def main():
    document = json.loads((ROOT / "research/ocean-current-seasonal-route-frames.json").read_text(encoding="utf-8"))
    width_path = ROOT / document['width_inventory_file']
    if hashlib.sha256(width_path.read_bytes()).hexdigest() != document['width_inventory_sha256']:
        raise ValueError('Stale seasonal width context')
    widths = json.loads(width_path.read_text(encoding='utf-8'))
    reports = {}
    for frame in document["frames"]:
        path = ROOT / frame["route_candidate_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != frame["route_candidate_sha256"]:
            raise ValueError("Stale seasonal route association")
        reports[frame["route_candidate_file"]] = json.loads(path.read_text(encoding="utf-8"))
    validate(document, reports, widths)
    print(f"OK: {len(document['frames'])} scoped seasonal route frames; no annual extrema inferred")

if __name__ == "__main__":
    main()
