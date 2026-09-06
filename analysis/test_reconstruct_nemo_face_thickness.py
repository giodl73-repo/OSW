import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("reconstruct_nemo_face_thickness.py")
SPEC = importlib.util.spec_from_file_location("reconstruct_nemo_face_thickness", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
FIXTURE = json.loads((PATH.parent / "fixtures/nemo-partial-step-synthetic.json").read_text(encoding="utf-8"))


class NemoFaceThicknessTests(unittest.TestCase):
    def test_reconstructs_expected_interior_faces(self):
        result = module.reconstruct(FIXTURE)
        self.assertEqual([3, 2, 2], result["u_shape"])
        self.assertEqual([3, 1, 3], result["v_shape"])
        self.assertEqual(
            [10, 0, 10, 6, 12, 0, 20, 0, 0, 0, 35, 0],
            result["u_face_thickness_m"],
        )
        self.assertEqual(
            [10, 10, 0, 20, 12, 0, 25, 0, 0],
            result["v_face_thickness_m"],
        )

    def test_zero_partial_bottom_uses_reference_thickness(self):
        result = module.reconstruct(FIXTURE)
        self.assertEqual(1, result["fallback_bottom_cell_count"])

    def test_face_column_depth_cannot_exceed_either_adjacent_column(self):
        result = module.reconstruct(FIXTURE)
        # U face between the first two cells in the top row: min(55 m, 22 m).
        first_u_column = sum(result["u_face_thickness_m"][offset] for offset in (0, 4, 8))
        self.assertEqual(22, first_u_column)
        self.assertLessEqual(first_u_column, 55)
        self.assertLessEqual(first_u_column, 22)

    def test_rejects_invalid_bottom_level(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["mbathy_1_based"][0] = 4
        with self.assertRaisesRegex(ValueError, "mbathy"):
            module.reconstruct(payload)

    def test_does_not_manufacture_terminal_faces(self):
        result = module.reconstruct(FIXTURE)
        self.assertFalse(result["checks"]["terminal_face_copying"])
        self.assertEqual(12, len(result["u_face_thickness_m"]))
        self.assertEqual(9, len(result["v_face_thickness_m"]))


if __name__ == "__main__":
    unittest.main()
