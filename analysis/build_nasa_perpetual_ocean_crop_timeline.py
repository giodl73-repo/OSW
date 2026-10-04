"""Build an explicitly inferred date seek index for NASA PO2 regional crops."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "nasa-perpetual-ocean-crop-timeline.json"
DATE_LIST = "https://svs.gsfc.nasa.gov/vis/a000000/a005400/a005479/dates_SOS.txt"


def main() -> None:
    request = urllib.request.Request(DATE_LIST, headers={"User-Agent": "OSW-Ocean-Motion-Almanac/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    lines = raw.decode("utf-8").splitlines()
    if len(lines) != 3601:
        raise ValueError(f"Expected 3601 NASA SOS date lines, got {len(lines)}")
    by_date = defaultdict(list)
    for frame_index, label in enumerate(lines):
        date = datetime.strptime(label.strip(), "%d %b %Y").strftime("%Y-%m-%d")
        by_date[date].append(frame_index)
    if list(by_date) != sorted(by_date) or lines[0] != "13 Nov 2022" or lines[-1] != "25 Dec 2023":
        raise ValueError("NASA date sequence has changed")
    dates = {}
    for date, frames in by_date.items():
        middle = frames[len(frames) // 2]
        dates[date] = {
            "sos_first_frame": frames[0],
            "sos_last_frame": frames[-1],
            "estimated_crop_frame": middle * 2,
            "estimated_crop_seconds": round(middle * 2 / 30, 2),
        }
    output = {
        "schema": "osw.almanac.nasa-po2-crop-timeline.v1",
        "date_list_source": DATE_LIST,
        "date_list_sha256": hashlib.sha256(raw).hexdigest(),
        "date_list_release": "https://svs.gsfc.nasa.gov/5479",
        "crop_release": "https://svs.gsfc.nasa.gov/5505",
        "crop_picker": "https://svs.gsfc.nasa.gov/vis/a000000/a005500/a005505/PCT_flow_map_ALL_noLabels_beauty.html",
        "date_start": next(iter(dates)),
        "date_end": next(reversed(dates)),
        "date_count": len(dates),
        "source_frame_count": 3601,
        "sampled_crop_video_evidence": {
            "sample_count": 4,
            "sample_tile_ids": ["level0_A_1", "level0_B_1", "level1_A_1", "level2_B_2"],
            "video_fps": 30,
            "video_frames": 7201,
            "video_duration_seconds": 240.033333,
            "tool": "ffprobe 9.0.1",
        },
        "alignment_status": "cross_release_inference",
        "method": "NASA's SOS date list has 3601 entries over the same declared ECCO2 model period as the regional beauty crops. Four sampled crop movies have 7201 frames at 30 fps. Estimate a crop seek time by doubling the middle SOS frame index for each date and dividing by 30 fps.",
        "limit": "NASA has not published an explicit frame-by-frame date list for these 70 crop movies in the reviewed page. These seek times are approximate cross-release navigation aids, not verified frame timestamps or evidence that a NASA particle pattern is the same object as a NOAA eddy.",
        "dates": dates,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(dates)} approximate NASA crop date seeks from {output['date_start']} to {output['date_end']}")


if __name__ == "__main__":
    main()
