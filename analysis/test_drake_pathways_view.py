import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("build_drake_pathways_view.py")
SPEC = importlib.util.spec_from_file_location("build_drake_pathways_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class DrakePathwaysViewTests(unittest.TestCase):
    def test_longitude_normalization(self):
        self.assertEqual(-67, view.normalize_longitude(293))
        self.assertEqual(-40, view.normalize_longitude(320))

    def test_projection_domain_corners(self):
        panel = (60, 175)
        self.assertEqual((60, 520), view.project(-82, -72, panel))
        self.assertEqual((735, 175), view.project(-38, -43, panel))


if __name__ == "__main__":
    unittest.main()
