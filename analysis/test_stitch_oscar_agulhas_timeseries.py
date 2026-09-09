import pathlib

from stitch_oscar_agulhas_timeseries import run


ROOT = pathlib.Path(__file__).parent.parent
WEST_SHA256 = "f3f359e03f7becf45932cf3e97658f870255caa72d1ff883b208f9fbaf43bd00"
EAST_SHA256 = "176cb2335a624b5245ee1a81ae1beac87086e7dd338dd63cfe86ace81c55cad9"
FIELD_SHA256 = "3106e0d767c24358c1adbfe5182a4898cea255830cfe679fe3280f270dc38cc4"


def test_stitch_preserves_axes_and_removes_archive_seam():
    payload = run(ROOT / "atlas/data/oscar-timeseries-agulhas-west-native-2018.js", ROOT / "atlas/data/oscar-timeseries-agulhas-east-native-2018.js")
    assert payload["shape"] == [71, 106, 151]
    assert payload["longitude_values"][0] == 5.0
    assert payload["longitude_values"][-1] == 55.0
    assert all(b > a for a, b in zip(payload["longitude_values"], payload["longitude_values"][1:]))
    assert len(payload["stitched_sources"]) == 2
    assert [source["sha256"] for source in payload["stitched_sources"]] == [WEST_SHA256, EAST_SHA256]
    assert payload["field_sha256"] == FIELD_SHA256


def test_stitch_preserves_every_source_cell_count():
    payload = run(ROOT / "atlas/data/oscar-timeseries-agulhas-west-native-2018.js", ROOT / "atlas/data/oscar-timeseries-agulhas-east-native-2018.js")
    rows, columns = payload["shape"][1:]
    assert all(len(frame["u_mm_s"]) == rows * columns for frame in payload["frames"])
    assert all(len(frame["v_mm_s"]) == rows * columns for frame in payload["frames"])
