"""Rebuild a five-date Gulf Stream diagnostic movie from pinned local fields."""
import hashlib
import argparse
import math
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from shapely.geometry import LineString, box
from build_cartographic_current_state_join import load_states, project, PROVINCES
from build_gulf_stream_geostrophic_path import load_field, trace
from build_gulf_stream_navo_state_snapshot import geographic_line_length_km

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research/gulf-stream-geostrophic-repeat-20260918-20260927.json"
OUTPUT = ROOT / "research/ocean-current-dated-timeline.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sensitivity(source, fields):
    scenarios = []
    for latitude in [36.625, 36.875, 37.125]:
        for step in [5, 10, 20]:
            result = trace(source, fields, latitude, step)
            scenarios.append({"seed_latitude": latitude, "step_km": step,
                              "diagnostic_length_km": result['segment_length_km'],
                              "stop_reason": result['stop_reason'],
                              "last_lon_lat": result['last_lon_lat'],
                              "reaches_downstream_gate": result['stop_reason'] == 'downstream_longitude_gate'})
    successful = [r['diagnostic_length_km'] for r in scenarios if r['reaches_downstream_gate']]
    return {"range_kind": "finite_seed_and_step_sensitivity_of_gate_reaching_diagnostics",
            "is_confidence_interval": False, "is_width_estimate": False,
            "scenario_grid": {"seed_latitudes": [36.625,36.875,37.125], "steps_km": [5,10,20]},
            "scenarios": scenarios, "gate_reaching_count": len(successful),
            "rounded_successful_scenario_span_km": [math.floor(min(successful)/10)*10, math.ceil(max(successful)/10)*10] if successful else None,
            "rounding_rule": "Outward to 10 km; only gate-reaching traces enter the span; all failures retained."}

def build(audit_path=AUDIT):
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("sampling_year") == 2025 and audit["dates"] != [f"2025-{month:02d}-15" for month in range(1,13)]:
        raise ValueError("Annual sample must preserve all twelve predetermined dates")
    states = load_states()
    frames = []
    for observation in audit["observations"]:
        path = ROOT / observation["source_subset"]
        if digest(path) != observation["source_subset_sha256"]:
            raise ValueError("Changed pinned velocity subset")
        source = json.loads(path.read_text(encoding="utf-8"))
        if source["source_time_start"][:10] != observation["date"] or source["source_response_sha256"] != observation["source_response_sha256"]:
            raise ValueError("Source date or response mismatch")
        fields = load_field(source)
        result = trace(source, fields, 36.875, 10)
        scenario_sensitivity = sensitivity(source, fields)
        if "traces" in observation:
            receipt = next(row for row in observation["traces"] if row["seed_latitude"] == 36.875)
            if result["segment_length_km"] != receipt["partial_length_km"] or result["stop_reason"] != receipt["stop_reason"]:
                raise ValueError("Trace disagrees with previous repeat audit")
        line = LineString([project(*point) for point in result["coordinates_lon_lat"]])
        joins = []
        for code, shape in sorted(states.items()):
            intersection = line.intersection(shape)
            if intersection.length > 0:
                joins.append({"state_code": code, "predicate": "dated_geostrophic_streamline_segment_intersection", "intersection_length_km": round(geographic_line_length_km(intersection), 1)})
        figure = f"figures/gulf-stream-dated-{observation['date']}.svg"
        render_map(ROOT / figure, line, states, observation["date"], result["stop_reason"])
        frames.append({"date": observation["date"], "time_start": source["source_time_start"], "time_end_exclusive": source["source_time_end_exclusive"], "source_subset": observation["source_subset"], "source_subset_sha256": digest(path), "source_url": source["source_url"], "source_response_sha256": source["source_response_sha256"], "source_algorithm": source["source_algorithm"], "source_product_status": source["source_product_status"], "figure": figure, "figure_sha256": digest(ROOT / figure), "coordinates_lon_lat": result["coordinates_lon_lat"], "diagnostic_length_km": result["segment_length_km"], "reaches_downstream_gate": result["stop_reason"] == "downstream_longitude_gate", "stop_reason": result["stop_reason"], "width_km": None, "positional_uncertainty_km": None, "state_relations": joins})
        frames[-1]['diagnostic_sensitivity'] = scenario_sensitivity
    versions = sorted({json.loads((ROOT / row['source_subset']).read_text(encoding='utf-8'))['source_algorithm'] for row in audit['observations']})
    return {"schema": "osw.current-dated-timeline.v1", "status": "research_only_not_canonical_or_ranked", "current_id": "gulf-stream-system", "name": "Gulf Stream System", "layer": f"Altimetry-derived absolute surface geostrophic velocity, NOAA LSA experimental {', '.join(versions)}, 0.25-degree grid.", "method": "Frozen-time WGS84 midpoint integration, 10 km steps, fixed seed [-72.875,36.875], 0.15 m/s stop threshold, first -50-degree longitude crossing, speed/missing-data stop or hard 4000 km distance cap.", "geometry_role": "frozen_field_diagnostic_streamline_not_current_axis_or_parcel_track", "audit_file": str(audit_path.relative_to(ROOT)).replace("\\", "/"), "audit_sha256": digest(audit_path), "generator_sha256": digest(Path(__file__)), "trace_algorithm_sha256": digest(ROOT / "analysis/build_gulf_stream_geostrophic_path.py"), "state_map_sha256": digest(PROVINCES), "annual_extrema_eligible": False, "annual_length_range_km": None, "annual_width_range_km": None, "sampling_note": audit.get('sampling_note', "Five selected September 2026 dates; 19-23 September are unsampled here. Frames advance by observation, not elapsed time. No seasonal or annual cycle established."), "limitations": audit.get('limitations', 'Twelve selected daily fields do not establish monthly means, seasonal climatology, annual extrema, whole-current axis or width. Finite seed/step sensitivity is reported; positional uncertainty is not quantified.'), "attribution": "Altimetry data are provided by the NOAA Laboratory for Satellite Altimetry. Acknowledge NOAA CoastWatch.", "product_page": "https://coastwatch.noaa.gov/cwn/products/sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html", "frames": frames}

def render_map(path, line, states, day, stop):
    left, top = project(-77, 44)
    right, bottom = project(-48, 34)
    clip = box(left, top, right, bottom)
    root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", viewBox=f"{left} {top} {right-left} {bottom-top}", role="img", **{"aria-labelledby": "title desc"})
    ET.SubElement(root, "title", id="title").text = f"Gulf Stream surface geostrophic diagnostic, {day}"
    ET.SubElement(root, "desc", id="desc").text = f"Equirectangular regional map, 77-48 W and 34-44 N. Fixed-seed diagnostic over OSW state context; stop: {stop}. No measured footprint or width."
    ET.SubElement(root, "rect", x=str(left), y=str(top), width=str(right-left), height=str(bottom-top), fill="#dbecef")
    land_path = next(item.get("d") for item in ET.parse(PROVINCES).getroot().iter() if item.get("class") == "land-context")
    ET.SubElement(root, "path", d=land_path, fill="#d0d1c8", stroke="none")
    for code, shape in states.items():
        clipped = shape.intersection(clip)
        if not clipped.is_empty:
            group = ET.SubElement(root, "g", fill="#dbecef", stroke="#829aa2", **{"stroke-width":"0.12"})
            ET.SubElement(group, "title").text = code
            # Shapely SVG supplies explicit styling; replace it for consistent state context.
            element = ET.fromstring(clipped.svg())
            for part in element.iter():
                if part.tag.endswith("path"):
                    part.set("fill", "#dbecef"); part.set("stroke", "#829aa2"); part.set("stroke-width", "0.12")
            group.append(element)
    for lon in [-75, -70, -65, -60, -55, -50]:
        x, y = project(lon, 34.5)
        ET.SubElement(root, "line", x1=str(x), x2=str(x), y1=str(top), y2=str(bottom), stroke="#b7c8cd", **{"stroke-width":"0.1"})
        ET.SubElement(root, "text", x=str(x), y=str(y), fill="#183e4b", **{"font-size":"1.5", "text-anchor":"middle"}).text = f"{abs(lon)} W"
    for lat in [35, 40, 43]:
        x, y = project(-76.5, lat)
        ET.SubElement(root, "text", x=str(x), y=str(y), fill="#183e4b", **{"font-size":"1.5"}).text = f"{lat} N"
    x, _ = project(-50, 40)
    ET.SubElement(root, "line", x1=str(x), x2=str(x), y1=str(top), y2=str(bottom), stroke="#183e4b", **{"stroke-width":"0.2", "stroke-dasharray":"0.8 0.5"})
    ET.SubElement(root, "polyline", points=" ".join(f"{x:.5f},{y:.5f}" for x,y in line.coords), fill="none", stroke="#b84a21", **{"stroke-width":"0.5", "stroke-linejoin":"round"})
    for index, color in [(0,"#163e4b"),(-1,"#b84a21")]:
        x,y=line.coords[index]
        ET.SubElement(root,"circle",cx=str(x),cy=str(y),r="0.7",fill=color)
    path.write_text(ET.tostring(root,encoding="unicode")+"\n",encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annual', action='store_true')
    args = parser.parse_args()
    output = build(ROOT / 'research/gulf-stream-2025-monthly-sample-receipts.json' if args.annual else AUDIT)
    path = ROOT / 'research/ocean-current-dated-timeline-2025.json' if args.annual else OUTPUT
    path.write_text(json.dumps(output, indent=2)+"\n", encoding="utf-8")
    print(f"Built {len(output['frames'])} dated diagnostic frames; annual ranges remain unknown")

if __name__ == "__main__":
    main()
