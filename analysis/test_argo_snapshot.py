import gzip
import importlib.util
import json
import pathlib
import tempfile
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("fetch_argo_snapshot.py")
SPEC = importlib.util.spec_from_file_location("fetch_argo_snapshot", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ArgoSnapshotTests(unittest.TestCase):
    def make_fixture(self) -> bytes:
        try:
            import netCDF4
            import numpy
        except ImportError:
            self.skipTest("optional netCDF4 fixture dependencies are not installed")
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "rg.nc"
            with netCDF4.Dataset(path, "w", format="NETCDF3_CLASSIC") as dataset:
                dataset.createDimension("LONGITUDE", 4)
                dataset.createDimension("LATITUDE", 3)
                dataset.createDimension("PRESSURE", 2)
                dataset.createDimension("TIME", 1)
                dataset.createVariable("LONGITUDE", "f4", ("LONGITUDE",))[:] = [20.5, 21.5, 22.5, 23.5]
                dataset.createVariable("LATITUDE", "f4", ("LATITUDE",))[:] = [-64.5, -63.5, -62.5]
                dataset.createVariable("PRESSURE", "f4", ("PRESSURE",))[:] = [10, 700]
                dataset.createVariable("TIME", "f4", ("TIME",))[:] = [270.5]
                field = dataset.createVariable(
                    MODULE.VARIABLE,
                    "f4",
                    ("TIME", "PRESSURE", "LATITUDE", "LONGITUDE"),
                    fill_value=-999.0,
                )
                field[:] = numpy.ma.array(
                    [
                        [[[0] * 4] * 3, [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8], [0.9, 1.0, 1.1, 1.2]]]
                    ],
                    mask=[[[[False] * 4] * 3, [[False, True, False, False], [False] * 4, [False] * 4]]],
                )
            return gzip.compress(path.read_bytes(), mtime=0)

    def test_url_pins_month_and_product_version(self):
        self.assertEqual(
            "https://sio-argo.ucsd.edu/RG/RG_ArgoClim_202607_2019.nc.gz",
            MODULE.build_url("2026-07"),
        )

    def test_window_name_is_pressure_specific(self):
        self.assertEqual("OCEANLINES_ARGO_TEMPERATURE_ANOMALY_700DBAR", MODULE.window_name(700))
        with self.assertRaisesRegex(ValueError, "integer pressure"):
            MODULE.window_name(462.5)

    def test_fixture_selects_exact_pressure_stride_and_mask(self):
        result = MODULE.parse_layer(self.make_fixture(), 700, 2)
        self.assertEqual(700.0, result["pressure_dbar"])
        self.assertEqual([2, 2], result["shape"])
        self.assertEqual([-64.5, -62.5], [result["latitude"]["start"], result["latitude"]["start"] + result["latitude"]["step"]])
        self.assertEqual([10, 30, 90, 110], result["values_c_hundredths"])

    def test_missing_pressure_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unavailable"):
            MODULE.parse_layer(self.make_fixture(), 750, 1)

    def test_package_declares_baseline_and_boundaries(self):
        payload = MODULE.package(
            self.make_fixture(),
            "2026-07",
            700,
            2,
            "2026-08-28T19:02:31Z",
            MODULE.build_url("2026-07"),
        )
        self.assertEqual("oceanlines.argo.pressure-anomaly.v1", payload["schema"])
        self.assertIn("2004-2018", payload["baseline"])
        self.assertIn("not absolute temperature", payload["boundary"])
        self.assertIn("Antarctic shelf", payload["boundary"])
        self.assertIn("freely available", payload["source_data_terms"])
        self.assertIn("No per-cell uncertainty", payload["uncertainty"])

    def test_committed_layer_has_fixed_provenance(self):
        artifact = MODULE_PATH.parents[1] / "atlas" / "data" / "argo-temperature-anomaly-700dbar-2026-07.js"
        lines = artifact.read_text(encoding="utf-8").splitlines()
        payload = json.loads(lines[1].removeprefix(f"window.{MODULE.window_name(700)}=").removesuffix(";"))
        self.assertEqual("2026-07", payload["month"])
        self.assertEqual(700.0, payload["pressure_dbar"])
        self.assertEqual([73, 180], payload["shape"])
        self.assertEqual("5a19dc77aaccecfd7e6aec34e80e42e1cbd83642c3f08a94d98c7018f631bb5c", payload["source_sha256"])
        self.assertGreater(payload["summary"]["valid_ocean_cells"], 7000)

    def test_committed_depth_ladder_shares_one_source_contract(self):
        root = MODULE_PATH.parents[1] / "atlas" / "data"
        payloads = []
        for pressure in (10, 300, 700, 1000):
            artifact = root / f"argo-temperature-anomaly-{pressure}dbar-2026-07.js"
            line = artifact.read_text(encoding="utf-8").splitlines()[1]
            payloads.append(json.loads(line.removeprefix(f"window.{MODULE.window_name(pressure)}=").removesuffix(";")))
        self.assertEqual([10.0, 300.0, 700.0, 1000.0], [payload["pressure_dbar"] for payload in payloads])
        for field in ("month", "baseline", "source_sha256", "shape", "latitude", "longitude"):
            self.assertEqual(1, len({json.dumps(payload[field], sort_keys=True) for payload in payloads}), field)


if __name__ == "__main__":
    unittest.main()
