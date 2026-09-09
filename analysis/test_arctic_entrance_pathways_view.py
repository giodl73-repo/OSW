import pathlib
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).parent.parent


class ArcticEntrancePathwaysViewTests(unittest.TestCase):
    def test_artifact_is_valid_and_preserves_pathway_boundary(self):
        svg = (ROOT / "figures/osw-motion-arctic-entrance-pathways-2018.svg").read_text(encoding="utf-8")
        ET.fromstring(svg)
        self.assertIn("EXPORT IS CLEANER THAN INFLOW", svg)
        self.assertIn("26/26 · 14/27 · 27/30", svg)
        self.assertIn("PATHWAYS · NOT HEAT TRANSPORT", svg)
        self.assertIn("Equal track counts are not transported volume", svg)


if __name__ == "__main__":
    unittest.main()
