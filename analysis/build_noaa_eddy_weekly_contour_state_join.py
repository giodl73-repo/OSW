"""Join each available NOAA weekly trajectory contour to OSW states by date."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta

from netCDF4 import Dataset
from shapely.strtree import STRtree

from build_cartographic_current_state_join import load_states
from build_motion_state_join import ROOT
from build_noaa_eddy_state_snapshot import contour_shapes
from build_noaa_eddy_weekly_join import cache_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20230601", help="Start date YYYYMMDD with an existing weekly join")
    date = parser.parse_args().date
    end = (datetime.strptime(date, "%Y%m%d") + timedelta(days=6)).strftime("%Y%m%d")
    weekly_path = ROOT / "research" / f"noaa-munster-eddy-weekly-join-{date}-{end}.json"
    output_path = ROOT / "research" / f"noaa-munster-eddy-weekly-contour-state-join-{date}-{end}.json"
    weekly = json.loads(weekly_path.read_text(encoding="utf-8"))
    source = cache_file(date, end)
    if hashlib.sha256(source.read_bytes()).hexdigest() != weekly["source_sha256"]:
        raise ValueError("Cached NOAA weekly source differs from recorded SHA-256")
    states = load_states()
    codes = sorted(states)
    polygons = [states[code] for code in codes]
    tree = STRtree(polygons)
    state_index = {code: {"contained": {}, "intersected": {}} for code in codes}
    tracks = {}
    with Dataset(source) as nc:
        for track_id, track in weekly["tracks"].items():
            prefix = "anti" if "-anti-" in track_id else "cyclo"
            column = track["weekly_column_ordinal"] - 1
            contour_lon = nc.variables[f"{prefix}_lon_contour"]
            contour_lat = nc.variables[f"{prefix}_lat_contour"]
            records = []
            for day_index, position in enumerate(track["positions"]):
                # NOAA trajectories can end before day seven; their positions
                # occupy the leading time indices of this particular source.
                shapes = contour_shapes(contour_lon[day_index, column, :], contour_lat[day_index, column, :])
                touched = set()
                for shape in shapes:
                    touched.update(int(index) for index in tree.query(shape))
                contained = []
                intersected = []
                for index in sorted(touched):
                    state = polygons[index]
                    if not any(state.intersects(shape) for shape in shapes):
                        continue
                    (contained if all(state.covers(shape) for shape in shapes) else intersected).append(codes[index])
                date = position["date"]
                for code in contained:
                    state_index[code]["contained"].setdefault(track_id, []).append(date)
                for code in intersected:
                    state_index[code]["intersected"].setdefault(track_id, []).append(date)
                records.append({"date": date, "contained_states": contained, "intersected_states": intersected,
                                "contour_available": bool(shapes)})
            tracks[track_id] = records
    output = {
        "schema": "osw.almanac.noaa-munster-weekly-contour-state-join.v1",
        "start_date": weekly["start_date"],
        "end_date": weekly["end_date"],
        "weekly_source_sha256": weekly["source_sha256"],
        "weekly_join": str(weekly_path.relative_to(ROOT)).replace("\\", "/"),
        "method": "Project each available dated NOAA weekly trajectory contour onto the OSW map. A coast-masked state contains it if the state covers every visible contour piece; otherwise an overlapping contour intersects it.",
        "claim_limit": f"These are the NOAA weekly trajectories matched to {weekly['start_date']} daily eddies. Trajectories beginning later in the week are outside this join. Local IDs are not NASA ECCO eddies or named historical rings, and no relation implies passage outside the reported dates.",
        "track_count": len(tracks),
        "tracks": tracks,
        "states": state_index,
    }
    output_path.write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(tracks)} weekly contour tracks; {sum(len(v['contained']) + len(v['intersected']) for v in state_index.values())} track-state relations to {output_path}")


if __name__ == "__main__":
    main()
