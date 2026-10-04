"""Index NOAA seven-day eddy center positions against OSW ocean states."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta

from shapely.geometry import Point
from shapely.strtree import STRtree

from build_cartographic_current_state_join import load_states, project
from build_motion_state_join import ROOT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20230601", help="Start date YYYYMMDD with an existing weekly join")
    date = parser.parse_args().date
    end = (datetime.strptime(date, "%Y%m%d") + timedelta(days=6)).strftime("%Y%m%d")
    source = ROOT / "research" / f"noaa-munster-eddy-weekly-join-{date}-{end}.json"
    output_path = ROOT / "research" / f"noaa-munster-eddy-weekly-state-join-{date}-{end}.json"
    weekly = json.loads(source.read_text(encoding="utf-8"))
    states = load_states()
    codes = sorted(states)
    polygons = [states[code] for code in codes]
    tree = STRtree(polygons)
    by_state = defaultdict(dict)
    by_track = {}
    for track_id, track in weekly["tracks"].items():
        visits = []
        for position in track["positions"]:
            center = Point(project(*position["center"]))
            matched = [codes[int(index)] for index in tree.query(center)
                       if polygons[int(index)].covers(center)]
            matched.sort()
            visits.append({"date": position["date"], "state_codes": matched})
            for code in matched:
                by_state[code].setdefault(track_id, []).append(position["date"])
        by_track[track_id] = visits
    output = {
        "schema": "osw.almanac.noaa-munster-weekly-state-join.v1",
        "start_date": weekly["start_date"],
        "end_date": weekly["end_date"],
        "weekly_source_sha256": weekly["source_sha256"],
        "weekly_join": str(source.relative_to(ROOT)).replace("\\", "/"),
        "method": "Project each daily NOAA trajectory center into the OSW map and test which coast-masked state polygon covers the point, including boundaries.",
        "claim_limit": f"A center visit does not establish contour containment or intersection on that day. This join covers trajectories matched to {weekly['start_date']} daily eddies, not new trajectories appearing later in the week. Track IDs are scoped to these source files and have no NASA or named-ring identity.",
        "track_count": len(by_track),
        "tracks": by_track,
        "states": {code: {"track_dates": by_state[code]} for code in codes},
    }
    output_path.write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_track)} track visits across {sum(bool(by_state[code]) for code in codes)} states to {output_path}")


if __name__ == "__main__":
    main()
