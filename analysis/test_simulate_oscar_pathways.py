import datetime as dt
import importlib.util
import json
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("simulate_oscar_pathways.py")
SPEC = importlib.util.spec_from_file_location("simulate_oscar_pathways", MODULE_PATH)
pathways = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(pathways)


def constant_payload(u_mm_s=1000, v_mm_s=0):
    frames = []
    for time in ("2018-01-01T00:00:00Z", "2018-01-06T00:00:00Z", "2018-01-11T00:00:00Z"):
        frames.append({"time": time, "u_mm_s": [u_mm_s] * 4, "v_mm_s": [v_mm_s] * 4})
    return {
        "shape": [3, 2, 2], "latitude_values": [1.0, -1.0],
        "longitude_values": [0.0, 2.0], "frames": frames,
    }


class VelocityFieldTests(unittest.TestCase):
    def test_bilinear_temporal_sample_of_constant_field(self):
        field = pathways.VelocityField(constant_payload())
        self.assertEqual((1.0, 0.0), field.sample(pathways.parse_time("2018-01-03T12:00:00Z"), 0, 1))

    def test_one_day_constant_eastward_displacement(self):
        field = pathways.VelocityField(constant_payload())
        result = pathways.integrate(field, pathways.parse_time("2018-01-02T00:00:00Z"), 0, 0.5, 1, 6, 24)
        expected_degrees = 86400 / pathways.EARTH_RADIUS_M * 180 / 3.141592653589793
        self.assertEqual("completed", result["status"])
        self.assertAlmostEqual(0.5 + expected_degrees, result["points"][-1]["longitude"], places=5)
        self.assertAlmostEqual(86.4, result["travelled_km"], places=2)

    def test_joint_mask_terminates_track(self):
        payload = constant_payload()
        payload["frames"][1]["u_mm_s"][0] = None
        field = pathways.VelocityField(payload)
        result = pathways.integrate(field, pathways.parse_time("2018-01-02T00:00:00Z"), 0, 0.5, 1, 6, 24)
        self.assertEqual("terminated_invalid_wet_stencil_or_domain", result["status"])
        self.assertEqual(0, result["integrated_hours"])


class HistoricalPathwayArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((MODULE_PATH.parents[1] / "research/osw-m2-drake-pathways-2018.json").read_text(encoding="utf-8"))

    def test_declared_run_and_losses_are_preserved(self):
        self.assertEqual({"released": 40, "completed": 35, "terminated": 5, "completion_fraction": 35 / 40}, self.data["summary"])
        self.assertEqual(6, self.data["solver_contract"]["timestep_hours"])
        self.assertEqual("none", self.data["solver_contract"]["diffusion"])
        self.assertEqual(10, self.data["release_contract"]["count_per_time"])

    def test_completed_and_terminated_durations_are_consistent(self):
        for track in self.data["tracks"]:
            if track["status"] == "completed":
                self.assertEqual(720, track["integrated_hours"])
                self.assertEqual(31, len(track["points"]))
            else:
                self.assertLess(track["integrated_hours"], 720)


if __name__ == "__main__":
    unittest.main()
