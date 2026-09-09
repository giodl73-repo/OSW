import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import sha256_file


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_nordic_surface_heat_receipt_matches_local_native_data() -> None:
    receipt = json.loads((ROOT / "research/osw-m4-oras5-nordic-surface-heat-source-2018.json").read_text(encoding="utf-8"))
    path = ROOT / receipt["output"]["path"]
    assert receipt["shape"] == [12, 256, 296]
    assert receipt["output"]["sha256"] == sha256_file(path)
    with netCDF4.Dataset(path) as dataset:
        assert dataset.variables["sohefldo"].shape == (12, 256, 296)
        assert np.asarray(dataset.variables["month"][:]).tolist() == list(range(201801, 201813))
        assert dataset.getncattr("sign_convention").startswith("positive downward")
