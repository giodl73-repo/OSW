"""Audit source-gated geographic floors separately from current lengths."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from pyproj import Geod


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research" / "ocean-current-almanac.json"
TARGET = ROOT / "research" / "ocean-current-gate-distances.json"
GEOD = Geod(ellps="WGS84")
GATE_PERTURBATION_DEGREES = 0.5


def sensitivity(gates: dict) -> dict:
    """Enumerate an editorial gate-location scenario, not measurement error."""
    shifts = (-GATE_PERTURBATION_DEGREES, 0, GATE_PERTURBATION_DEGREES)
    distances = []
    if gates["type"] == "source_latitude_span":
        for da, db in product(shifts, repeat=2):
            distances.append(GEOD.inv(0, gates["start"]["latitude"] + da,
                                      0, gates["end"]["latitude"] + db)[2] / 1000)
    else:
        a, b = gates["start"]["lon_lat"], gates["end"]["lon_lat"]
        for dx, dy, ex, ey in product(shifts, repeat=4):
            distances.append(GEOD.inv(a[0] + dx, a[1] + dy,
                                      b[0] + ex, b[1] + ey)[2] / 1000)
    return {
        "interpretation": "Finite gate-perturbation scenarios; not a statistical confidence interval, measured current path, or whole-current length range.",
        "perturbation_degrees": GATE_PERTURBATION_DEGREES,
        "perturbation_basis": "OSW editorial sensitivity choice; not source-reported positional uncertainty.",
        "scenario_count": len(distances),
        "scenario_min_km": round(min(distances), 1),
        "scenario_max_km": round(max(distances), 1),
    }

# Meridional gates deliberately have no longitude. Their distance is computed
# on the 0° meridian solely to quantify latitude separation, not to imply a
# measured flow position there. Other coordinates are approximate source gates.
GATES = {
    "benguela": {
        "type": "source_latitude_span",
        "start": {"name": "Benguela Current system southern section", "latitude": -30},
        "end": {"name": "Benguela Current system northern section", "latitude": -19},
        "scope": "Decadal inverse-model sections of the Benguela Current system; excludes a claimed measured centerline or a Benguela ecosystem extent.",
    },
    "brazil": {
        "type": "source_latitude_span",
        "start": {"name": "Brazil Current northern section", "latitude": -19},
        "end": {"name": "Brazil Current southern section", "latitude": -30},
        "scope": "Decadal inverse-model sections identifying the Brazil Current; no simultaneous centerline or confluence endpoint is inferred.",
    },
    "deep-western-boundary": {
        "type": "source_latitude_span",
        "start": {"name": "North Atlantic DWBC northern section", "latitude": 47},
        "end": {"name": "North Atlantic DWBC southern section", "latitude": 24.5},
        "scope": "North Atlantic segment of the deep western boundary current in decadal inverse-model sections; not a whole-Atlantic path.",
    },
    "agulhas": {
        "type": "source_latitude_span",
        "start": {"name": "northern Agulhas extent", "latitude": -27},
        "end": {"name": "southern Agulhas extent", "latitude": -40},
        "scope": "Broad 27–40°S research-description span; not the narrower approximately 1,000 km coastal usage.",
    },
    "agulhas-return": {
        "type": "approximate_source_gate_pair",
        "start": {"name": "21°E hydrographic section peak", "lon_lat": [21, -40.5], "coordinate_role": "study section center latitude"},
        "end": {"name": "60°E downstream mean latitude", "lon_lat": [60, -44.5], "coordinate_role": "study-described downstream latitude"},
        "scope": "Between two study-described sections; not the full return-current path to dissipation.",
    },
    "east-australian": {
        "type": "source_latitude_span",
        "start": {"name": "coherent shelf-break jet north", "latitude": -15},
        "end": {"name": "usual shelf separation", "latitude": -32},
        "scope": "Shelf-break jet before variable separation; excludes Tasman Front and downstream eddies.",
    },
    "east-greenland": {
        "type": "source_latitude_span",
        "start": {"name": "Fram Strait study section", "latitude": 78.5},
        "end": {"name": "Cape Farewell study boundary", "latitude": 59},
        "scope": "Study region covering the outer East Greenland Current and coastal branch; no claim of one measured core between gates. Supersedes an unsupported 81°N gate.",
    },
}


def build() -> dict:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    currents = {item["id"]: item for item in ledger["entries"]}
    entries = []
    for current_id, gates in GATES.items():
        item = currents[current_id]
        if gates["type"] == "source_latitude_span":
            a = [0, gates["start"]["latitude"]]
            b = [0, gates["end"]["latitude"]]
        else:
            a = gates["start"]["lon_lat"]
            b = gates["end"]["lon_lat"]
        distance_km = GEOD.inv(*a, *b)[2] / 1000
        floor_km = item["length_lower_bound_km"]
        assert floor_km <= distance_km and distance_km - floor_km < 250
        assert item["length_bound_basis"] and item["length_source"]
        entries.append({
            "current_id": current_id,
            "name": item["name"],
            "gate_type": gates["type"],
            "start": gates["start"],
            "end": gates["end"],
            "direct_gate_distance_km": round(distance_km, 1),
            "admitted_rounded_geographic_floor_km": floor_km,
            "scope": gates["scope"],
            "source_url": ledger["sources"][item["length_source"]],
            "gate_distance_sensitivity": sensitivity(gates),
        })
    for entry in entries:
        scenario = entry["gate_distance_sensitivity"]
        others = [other for other in entries if other is not entry]
        scenario["geographic_span_rank_best"] = 1 + sum(
            other["gate_distance_sensitivity"]["scenario_min_km"] > scenario["scenario_max_km"]
            for other in others)
        scenario["geographic_span_rank_worst"] = 1 + sum(
            other["gate_distance_sensitivity"]["scenario_max_km"] >= scenario["scenario_min_km"]
            for other in others)
        scenario["geographic_span_rank_count"] = len(entries)
        scenario["rank_interpretation"] = "Possible position by geographic gate separation within these seven source-gated spans; excludes along-current length and the published-length ranking. Overlap does not establish equal current length."
    return {
        "schema": "osw.almanac.current-gate-distances.v1",
        "as_of": "2026-10-02",
        "method": "WGS84 shortest geodesic between approximate gates; latitude-only spans use an abstract common meridian. Floors are conservatively rounded down from these gate distances.",
        "interpretation": "These are geographic separation floors conditional on the stated source gates, not measured along-current paths, whole-current estimates, or guaranteed physical minima when gates are approximate or a flow splits.",
        "sensitivity_method": "Independently perturb each source latitude gate by -0.5, 0, or +0.5 degrees; point gates also perturb longitude. Recompute WGS84 shortest distances for all 9 or 81 scenarios. Report the finite scenario envelope and possible ordinal positions among the seven geographic spans, reserving all tied positions. This is a declared editorial what-if analysis, not an empirical error model or a guarantee over every point in a continuous coordinate interval.",
        "count": len(entries),
        "entries": entries,
    }


if __name__ == "__main__":
    payload = build()
    TARGET.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {payload['count']} source-gated distance audits")
