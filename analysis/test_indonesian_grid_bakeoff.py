import pathlib

from analyze_indonesian_grid_bakeoff import run, sha256_file


ROOT = pathlib.Path(__file__).parent.parent


def test_finer_grid_restores_surface_support_at_all_five_candidates():
    result = run(ROOT / "research/osw-m2-indonesian-gate-readiness-2018.json", ROOT / "atlas/data/hycom-indonesian-gates-20181116.json")
    for source in result["sources"]:
        assert source["sha256"] == sha256_file(ROOT / source["path"])
    gates = {gate["code"]: gate for gate in result["gates"]}
    assert {code: gate["hycom"]["surface_wet_points"] for code, gate in gates.items()} == {"MAK": 20, "LIF": 14, "LOM": 7, "OMB": 10, "TIM": 38}
    assert all(gate["hycom"]["surface_wet_points"] > gate["oscar"]["surface_wet_points"] for gate in gates.values())
    assert all(gate["verdict"] == "candidate_full_depth_section_supported" for gate in gates.values())


def test_profiles_keep_temperature_salinity_and_normal_motion_separate():
    result = run(ROOT / "research/osw-m2-indonesian-gate-readiness-2018.json", ROOT / "atlas/data/hycom-indonesian-gates-20181116.json")
    assert all(len(gate["profiles"]) == 33 for gate in result["gates"])
    assert all(gate["hycom"]["wet_standard_levels"] >= 10 for gate in result["gates"])
