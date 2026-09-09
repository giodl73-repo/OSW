import json
import pathlib


ROOT = pathlib.Path(__file__).parent.parent


def test_committed_hycom_gate_sample_is_complete_and_multivariate():
    payload = json.loads((ROOT / "atlas/data/hycom-indonesian-gates-20181116.json").read_text(encoding="utf-8"))
    assert payload["date"] == "20181116"
    assert len(payload["depth_m"]) == 33
    assert {gate["code"] for gate in payload["gates"]} == {"MAK", "LIF", "LOM", "OMB", "TIM"}
    for gate in payload["gates"]:
        point_count = len(gate["points"])
        for variable in ("temperature", "salinity", "u", "v"):
            assert len(gate["values"][variable]) == 33
            assert all(len(level) == point_count for level in gate["values"][variable])
