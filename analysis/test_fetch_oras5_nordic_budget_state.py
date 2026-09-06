import json
import pathlib

import netCDF4

import fetch_oras5_nordic_budget_state as state
from fetch_oras5_arctic_state_subset import sha256_file


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_required_windows_cover_every_storage_cell_and_boundary_neighbor() -> None:
    control = json.loads((ROOT / "research/osw-m4-oras5-nordic-control-volume.json").read_text(encoding="utf-8"))
    windows = state.required_windows(control)
    assert windows["votemper"] == windows["vosaline"]
    for y, x in control["inside_t_cells"]:
        window = windows["votemper"]
        assert window["y_start"] <= y < window["y_stop_exclusive"]
        assert window["x_start"] <= x < window["x_stop_exclusive"]
    for section in control["sections"]:
        for face in section["faces"]:
            window = windows["vozocrtx" if face["face"] == "U" else "vomecrty"]
            assert window["y_start"] <= face["y"] < window["y_stop_exclusive"]
            assert window["x_start"] <= face["x"] < window["x_stop_exclusive"]


def test_global_window_preserves_extent() -> None:
    local = {"y_start": 3, "y_stop_exclusive": 8, "x_start": 7, "x_stop_exclusive": 11}
    box = {"y_start": 100, "x_start": 200}
    assert state.global_window(local, box) == {"y_start": 103, "y_stop_exclusive": 108, "x_start": 207, "x_stop_exclusive": 211}


def test_all_twelve_committed_states_match_receipts() -> None:
    for month_number in range(1, 13):
        month = f"2018{month_number:02d}"
        receipt = json.loads((ROOT / f"research/osw-m4-oras5-nordic-budget-state-{month}.json").read_text(encoding="utf-8"))
        path = ROOT / receipt["output"]["path"]
        assert receipt["month"] == month
        assert receipt["output"]["sha256"] == sha256_file(path)
        with netCDF4.Dataset(path) as dataset:
            assert dataset.getncattr("month") == month
            assert set(("votemper", "vosaline", "vozocrtx", "vomecrty")).issubset(dataset.variables)
