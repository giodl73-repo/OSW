"""Derive transparent vertical-shape fingerprints for source-aligned provinces."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
OUTPUT = ROOT / "research" / "longhurst-2007-province-hypsometric-fingerprints.json"
BROWSER = ROOT / "column" / "province-fingerprints.js"
SUBSTANTIAL_AREA_FRACTION = 0.05
BANDS = ("epipelagic", "mesopelagic", "bathypelagic", "abyssopelagic", "hadalpelagic")
CHARACTERS = {
    "epipelagic": "shelf-led",
    "mesopelagic": "upper-depth-floor-led",
    "bathypelagic": "deep-floor-led",
    "abyssopelagic": "abyssal-floor-led",
    "hadalpelagic": "hadal-floor-led",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descending_ranks(provinces: dict, field: str) -> dict[str, int]:
    ordered = sorted(provinces.values(), key=lambda item: (-item[field], item["osw_code"]))
    return {item["osw_code"]: index + 1 for index, item in enumerate(ordered)}


def derive(source_path: Path = SOURCE, output_path: Path = OUTPUT, browser_path: Path = BROWSER) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    provinces = source["provinces"]
    ranks = {
        "area": descending_ranks(provinces, "sampled_wet_area_km2"),
        "volume": descending_ranks(provinces, "sampled_water_volume_km3"),
        "mean_depth": descending_ranks(provinces, "area_weighted_mean_water_depth_m"),
    }
    fingerprints = {}
    character_counts = Counter()
    breadth_counts = Counter()
    hadal_bearing_count = 0
    for code, province in provinces.items():
        fractions = province["wet_area_fraction_by_seafloor_band"]
        dominant = max(BANDS, key=lambda band: (fractions.get(band, 0), -BANDS.index(band)))
        substantial = [band for band in BANDS if fractions.get(band, 0) >= SUBSTANTIAL_AREA_FRACTION]
        hadal_bearing = province["counts_by_seafloor_band"].get("hadalpelagic", 0) > 0
        character = CHARACTERS[dominant]
        area_rank = ranks["area"][code]
        volume_rank = ranks["volume"][code]
        fingerprints[code] = {
            "osw_code": code,
            "floor_character": character,
            "dominant_seafloor_band": dominant,
            "dominant_seafloor_area_fraction": fractions[dominant],
            "substantial_band_threshold_area_fraction": SUBSTANTIAL_AREA_FRACTION,
            "substantial_seafloor_bands": substantial,
            "substantial_seafloor_band_count": len(substantial),
            "hadal_bearing": hadal_bearing,
            "hadal_seafloor_area_fraction": fractions.get("hadalpelagic", 0),
            "sampled_wet_area_rank": area_rank,
            "sampled_water_volume_rank": volume_rank,
            "mean_water_depth_rank": ranks["mean_depth"][code],
            "volume_rank_advantage_over_area": area_rank - volume_rank,
        }
        character_counts[character] += 1
        breadth_counts[str(len(substantial))] += 1
        hadal_bearing_count += int(hadal_bearing)

    payload = {
        "schema": "osw-longhurst-2007-hypsometric-fingerprints-v1",
        "source_path": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(source_path),
        "province_count": len(fingerprints),
        "method": {
            "floor_character": "Depth band containing the largest spherical-area-weighted share of wet GEBCO centers in the source-aligned province.",
            "substantial_band": f"Seafloor band containing at least {SUBSTANTIAL_AREA_FRACTION:.0%} of sampled wet area.",
            "hadal_bearing": "At least one wet sampled center has seabed depth of 6,000 m or greater.",
            "volume_rank_advantage_over_area": "sampled wet-area rank minus sampled water-volume rank; positive means the province ranks higher by volume than by area.",
        },
        "summary": {
            "counts_by_floor_character": dict(sorted(character_counts.items())),
            "counts_by_substantial_band_count": dict(sorted(breadth_counts.items())),
            "hadal_bearing_province_count": hadal_bearing_count,
        },
        "provinces": fingerprints,
        "boundary": "A deterministic bathymetric shape vocabulary derived from the 0.25-degree source-aligned screen. It does not diagnose slope, geomorphic feature identity, habitat, water mass, current, heat content, transport, or dynamical importance.",
    }
    encoded = json.dumps(payload, separators=(",", ":"))
    output_path.write_text(encoded + "\n", encoding="utf-8", newline="\n")
    browser_path.write_text("window.OSW_PROVINCE_FINGERPRINTS = " + encoded + ";\n", encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = derive()
    print(json.dumps(result["summary"], indent=2))
