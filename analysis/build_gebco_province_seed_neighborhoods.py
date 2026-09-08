"""Build compact browser and summary products from raw GEBCO neighborhoods."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from build_gebco_province_seed_depths import deepest_band, tid_class


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "gebco-2026-province-seed-neighborhoods-source.json"
OUTPUT = ROOT / "research" / "gebco-2026-province-seed-neighborhoods.json"
SUMMARY = ROOT / "research" / "gebco-2026-province-seed-neighborhoods-summary.json"
BROWSER = ROOT / "column" / "neighborhoods.js"


def parse_grid(text: str, variable: str, size: int) -> tuple[list[int], list[float], list[float]]:
    array_match = re.search(
        rf"^{variable}\.{variable}\[{size}\]\[{size}\]\n(.*?)\n\n{variable}\.lat\[{size}\]\n([^\n]+)\n\n{variable}\.lon\[{size}\]\n([^\n]+)",
        text, flags=re.MULTILINE | re.DOTALL,
    )
    if not array_match:
        raise ValueError(f"cannot parse {variable} grid")
    values = []
    for expected, line in enumerate(array_match.group(1).splitlines()):
        prefix, payload = line.split("]", 1)
        if int(prefix[1:]) != expected:
            raise ValueError(f"nonsequential {variable} row")
        values.extend(int(value.strip()) for value in payload.lstrip(", ").split(","))
    latitudes = [float(value.strip()) for value in array_match.group(2).split(",")]
    longitudes = [float(value.strip()) for value in array_match.group(3).split(",")]
    if len(values) != size * size or len(latitudes) != size or len(longitudes) != size:
        raise ValueError(f"wrong {variable} dimensions")
    return values, latitudes, longitudes


def build(source: Path = SOURCE, output: Path = OUTPUT, summary_output: Path = SUMMARY, browser_output: Path = BROWSER) -> dict:
    receipt = json.loads(source.read_text(encoding="utf-8"))
    size = receipt["sampling"]["shape"][0]
    neighborhoods, summaries = {}, []
    for record in receipt["records"]:
        elevation_raw = record["elevation_response_ascii"].encode("utf-8")
        tid_raw = record["tid_response_ascii"].encode("utf-8")
        if hashlib.sha256(elevation_raw).hexdigest() != record["elevation_response_sha256"]:
            raise ValueError(f"elevation checksum mismatch for {record['code']}")
        if hashlib.sha256(tid_raw).hexdigest() != record["tid_response_sha256"]:
            raise ValueError(f"TID checksum mismatch for {record['code']}")
        elevations, latitudes, longitudes = parse_grid(record["elevation_response_ascii"], "elevation", size)
        tids, tid_latitudes, tid_longitudes = parse_grid(record["tid_response_ascii"], "tid", size)
        if latitudes != tid_latitudes or longitudes != tid_longitudes:
            raise ValueError(f"elevation/TID coordinates disagree for {record['code']}")
        wet_depths = [-value for value in elevations if value < 0]
        tid_counts = Counter(tid_class(value) for value in tids)
        band_counts = Counter(deepest_band(-value) if value < 0 else "land" for value in elevations)
        summary = {
            "code": record["code"], "sample_count": len(elevations),
            "latitude_bounds": [latitudes[0], latitudes[-1]],
            "longitude_bounds": [longitudes[0], longitudes[-1]],
            "wet_sample_count": len(wet_depths), "land_sample_count": len(elevations) - len(wet_depths),
            "minimum_wet_depth_m": min(wet_depths) if wet_depths else None,
            "maximum_wet_depth_m": max(wet_depths) if wet_depths else None,
            "counts_by_seafloor_band": dict(sorted(band_counts.items())),
            "counts_by_tid_class": dict(sorted(tid_counts.items())),
        }
        summaries.append(summary)
        neighborhoods[record["code"]] = {
            "latitudes": latitudes, "longitudes": longitudes,
            "elevation_m": elevations, "tid": tids, "summary": summary,
        }
    payload = {
        "schema": "osw-gebco-province-seed-neighborhood-v1",
        "source_release": receipt["source"]["release"],
        "source_doi": receipt["source"]["doi"],
        "source_receipt_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "shape": receipt["sampling"]["shape"],
        "spacing_degrees": receipt["sampling"]["spacing_degrees"],
        "nominal_width_degrees": receipt["sampling"]["nominal_width_degrees"],
        "neighborhoods": neighborhoods,
        "boundary": receipt["boundary"],
    }
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    browser_output.write_text("window.OSW_BATHY_NEIGHBORHOODS = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    aggregate_tid = Counter()
    aggregate_bands = Counter()
    for summary in summaries:
        aggregate_tid.update(summary["counts_by_tid_class"])
        aggregate_bands.update(summary["counts_by_seafloor_band"])
    summary_payload = {
        "schema": "osw-gebco-province-seed-neighborhood-summary-v1",
        "source_release": receipt["source"]["release"],
        "neighborhood_count": len(neighborhoods),
        "samples_per_neighborhood": size * size,
        "total_samples": len(neighborhoods) * size * size,
        "fully_wet_neighborhood_count": sum(summary["land_sample_count"] == 0 for summary in summaries),
        "mixed_land_water_neighborhood_count": sum(summary["land_sample_count"] > 0 and summary["wet_sample_count"] > 0 for summary in summaries),
        "counts_by_tid_class": dict(sorted(aggregate_tid.items())),
        "counts_by_seafloor_band": dict(sorted(aggregate_bands.items())),
        "neighborhoods": summaries,
        "boundary": receipt["boundary"],
    }
    summary_output.write_text(json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"wrote {len(result['neighborhoods'])} neighborhoods")
