import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_ocean_state_sant_density_boundary_year.py")
SPEC = importlib.util.spec_from_file_location("ocean_state_sant_density_boundary_year", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_compact_crop_covers_every_selected_box_face():
    selection = json.loads(MODULE.SELECTION.read_text(encoding="utf-8"))
    rectangle = MODULE.crop(selection)
    assert rectangle == {"y_start": 147, "y_stop_exclusive": 167, "x_start": 128, "x_stop_exclusive": 147}
    for box in [selection["primary"], *selection["one_cell_displaced_controls"]]:
        local = MODULE.local_box(box, rectangle)
        assert 0 < local["y_start"] < local["y_stop_exclusive"] < 20
        assert 0 < local["x_start"] < local["x_stop_exclusive"] < 19


def test_twelve_month_screen_reproduces_four_custodied_months():
    committed = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
    rebuilt = MODULE.build()
    assert rebuilt == committed
    MODULE.validate(committed)
    assert committed["status"] == "twelve_month_horizontal_density_bin_screen_not_transformation_or_budget"
    assert [month["valid_time"] for month in committed["months"]] == [f"2018-{month:02d}-01/P1M" for month in range(1, 13)]
    assert committed["baseline"]["reproduced_months"] == ["201802", "201805", "201808", "201811"]
    july = committed["months"][6]["outcomes"][0]
    mid = july["horizontal_density_boundary"]["strata"][2]
    upstream = july["collocation_sensitivity"]["strata"][2]
    assert mid["net_outward_volume_Sv"] > 1.5
    assert upstream["upstream_net_outward_Sv"] > 1.0
    august = committed["months"][7]["outcomes"][0]
    assert august["horizontal_density_boundary"]["strata"][2]["net_outward_volume_Sv"] > 0
    assert august["collocation_sensitivity"]["strata"][2]["upstream_net_outward_Sv"] < 0


def test_compact_source_archive_covers_all_months_and_reuses_four_bound_fields():
    source = json.loads(MODULE.SOURCE.read_text(encoding="utf-8"))
    assert source["output"]["sha256"] == MODULE.sha256(ROOT / source["output"]["path"])
    assert source["shape_month_z_y_x"] == [12, 75, 20, 19]
    assert [entry["month"] for entry in source["months"]] == list(MODULE.MONTHS)
    assert sum(entry["fields"]["votemper"]["archive"] is not None for entry in source["months"]) == 4
    for entry in source["months"]:
        assert all(entry["month"][:4] + "-" + entry["month"][4:] in field["time_units"] for field in entry["fields"].values())
