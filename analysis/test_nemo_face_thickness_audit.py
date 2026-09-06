import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("audit_nemo_face_thickness_reconstruction.py")
SPEC = importlib.util.spec_from_file_location("audit_nemo_face_thickness_reconstruction", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class NemoFaceThicknessAuditTests(unittest.TestCase):
    def fixture(self):
        reference = np.array([10.0, 20.0])
        mbathy = np.array([[2, 1], [2, 0]])
        partial = np.array([[15.0, 7.0], [20.0, 0.0]])
        t, _ = module.reconstruct_t(reference, mbathy, partial)
        umask = np.zeros_like(t); vmask = np.zeros_like(t)
        umask[:, :, :-1] = np.minimum(t[:, :, :-1], t[:, :, 1:]) > 0
        vmask[:, :-1, :] = np.minimum(t[:, :-1, :], t[:, 1:, :]) > 0
        return reference, mbathy, partial, umask, vmask, np.ones((2, 2)) * 100, np.ones((2, 2)) * 120

    def test_consistent_native_masks_and_depths_pass(self):
        result = module.audit_arrays(*self.fixture())
        self.assertEqual("candidate_passes_native_geometry_consistency", result["status"])
        self.assertEqual({"u": 0, "v": 0}, result["mask_mismatch_count"])
        self.assertEqual(0, result["maximum_face_column_depth_residual_m"])
        self.assertTrue(result["wet_face_area_m2"]["all_finite_positive"])

    def test_mask_disagreement_fails(self):
        values = list(self.fixture())
        values[3][0, 0, 0] = 0
        result = module.audit_arrays(*values)
        self.assertEqual("candidate_fails_native_geometry_consistency", result["status"])
        self.assertEqual(1, result["mask_mismatch_count"]["u"])

    def test_invalid_bottom_level_is_rejected(self):
        values = list(self.fixture())
        values[1][0, 0] = 3
        with self.assertRaisesRegex(ValueError, "mbathy"):
            module.audit_arrays(*values)


if __name__ == "__main__":
    unittest.main()
