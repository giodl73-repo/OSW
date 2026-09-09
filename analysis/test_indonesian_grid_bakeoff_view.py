import pathlib


ROOT = pathlib.Path(__file__).parent.parent


def test_committed_grid_bakeoff_keeps_resolution_and_transport_separate():
    svg = (ROOT / "figures/osw-m3-indonesian-grid-bakeoff-2018.svg").read_text(encoding="utf-8")
    assert "THE FINER GRID OPENS ALL FIVE." in svg
    assert "RESOLUTION PASSES. TRANSPORT HAS NOT STARTED." in svg
    for count in ("20/32", "14/16", "7/17", "10/15", "38/38"):
        assert count in svg
    assert "ONE DAILY FIELD · NOT A MEAN" in svg
