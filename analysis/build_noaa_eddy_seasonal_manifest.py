"""Index four reproducible NOAA daily eddy snapshots per NASA model year."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = RESEARCH / "noaa-munster-eddy-seasonal-manifest-2021-2023.json"
DATES = [f"{year}{month}01" for year in (2021, 2022, 2023) for month in ("03", "06", "09", "12")]


def build():
    snapshots = []
    for date in DATES:
        path = RESEARCH / f"noaa-munster-eddy-state-{date}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["date"] != f"{date[:4]}-{date[4:6]}-{date[6:]}":
            raise ValueError(f"Snapshot date mismatch: {path}")
        if len(data["states"]) != 56:
            raise ValueError(f"Expected 56 state records in {path}")
        snapshots.append({
            "date": data["date"],
            "path": f"../research/{path.name}",
            "source_url": data["source"],
            "source_sha256": data["source_sha256"],
            "detection_count": len(data["entries"]),
            "contained_relation_count": sum(len(state["contained"]) for state in data["states"].values()),
            "intersected_relation_count": sum(len(state["intersected"]) for state in data["states"].values()),
            "weekly_track_join": date[4:6] == "06",
        })
    return {
        "schema": "osw.almanac.noaa-munster-seasonal-manifest.v1",
        "period": "2021–2023",
        "sampling": "One source-dated NOAA daily eddy-identification file on 1 March, 1 June, 1 September, and 1 December of each year. This is twelve sampled days, not a continuous eddy census or NASA ECCO object identity.",
        "state_relation_method": "Each referenced snapshot retains daily contour containment and intersection against the 56 approximate OSW states.",
        "weekly_track_limit": "Seven-day NOAA tracks and dated contour joins are available only for the three June snapshots.",
        "snapshot_count": len(snapshots),
        "detection_count_sum": sum(item["detection_count"] for item in snapshots),
        "snapshots": snapshots,
    }


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {result['snapshot_count']} dates and {result['detection_count_sum']} dated detections")
