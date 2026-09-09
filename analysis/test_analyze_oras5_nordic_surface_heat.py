import json
import pathlib

import analyze_oras5_nordic_surface_heat as surface


ROOT = pathlib.Path(__file__).resolve().parents[1]


def derive_repository_analysis():
    return surface.analyze(
        ROOT / "research/osw-m4-oras5-nordic-control-volume.json",
        ROOT / "atlas/data/oras5-nordic-t-metrics.nc",
        ROOT / "atlas/data/oras5-nordic-surface-heat-2018.nc",
    )


def test_surface_flux_covers_the_exact_room_for_twelve_months() -> None:
    payload = derive_repository_analysis()
    assert payload["checks"]["month_count"] == 12
    assert payload["checks"]["all_months_cover_complete_room"]
    assert payload["checks"]["control_cell_count_matches"]
    assert payload["inside_wet_t_cell_count"] == 12550
    assert payload["time_weighted_2018"]["warming_month_count"] > 0
    assert payload["time_weighted_2018"]["cooling_month_count"] > 0


def test_committed_analysis_matches_derivation() -> None:
    expected = derive_repository_analysis()
    committed = json.loads((ROOT / "research/osw-m4-oras5-nordic-surface-heat-2018.json").read_text(encoding="utf-8"))
    assert committed == expected
