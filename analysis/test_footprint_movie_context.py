"""Exercise crop clipping, longitude wrapping and navigation-only semantics."""
import unittest
from build_footprint_movie_context import build

class CropContextTests(unittest.TestCase):
    def run_join(self, tiles, date="2013-05-29", ring=None):
        ring = ring or [[10,20],[12,20],[12,22],[10,22],[10,20]]
        candidate = dict(id="candidate", entity_id="eddy:test", geometry_id="g", geometry_sha256="hash", observation_date=date, source_id="paper", source_snapshot_id="figure")
        geometry = dict(id="g", geometry=dict(type="Polygon", coordinates=[ring]))
        return build([candidate], [geometry], tiles, "2021–2023", "ledger")

    def tile(self, name, west, east, south, north, zoom=0):
        return dict(tile_id=name, longitude_range_unwrapped=[west,east], latitude_range=[south,north], zoom=zoom, url="https://example.org/movie", source_id="nasa")

    def test_half_clip_and_opposite_hemisphere(self):
        rows=self.run_join([self.tile("half",10,11,20,22), self.tile("opposite",10,12,-22,-20)])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["nominal_angular_overlap_fraction"],0.5)
        self.assertFalse(rows[0]["recommended"])

    def test_periodic_crop_and_complete_recommendation(self):
        rows=self.run_join([self.tile("wrapped",370,372,20,22,1), self.tile("partial",10,11,20,22,2)])
        self.assertEqual([r["tile_id"] for r in rows if r["recommended"]],["wrapped"])
        self.assertEqual(next(r for r in rows if r["tile_id"]=="wrapped")["nominal_angular_overlap_fraction"],1)
        self.assertTrue(all(r["temporal_alignment_status"]=="outside_declared_model_years" for r in rows))

    def test_year_in_range_is_not_event_identity(self):
        row=self.run_join([self.tile("full",10,12,20,22)],"2022-05-29")[0]
        self.assertEqual(row["temporal_alignment_status"],"year_in_range_event_alignment_unresolved")
        self.assertEqual(row["event_identity_status"],"not_established")

    def test_equal_views_use_stable_tile_id(self):
        rows=self.run_join([self.tile("z",10,12,20,22),self.tile("a",10,12,20,22)])
        self.assertEqual([r["tile_id"] for r in rows if r["recommended"]],["a"])

    def test_ambiguous_seam_rejected(self):
        with self.assertRaises(ValueError):
            self.run_join([],ring=[[-179,20],[179,20],[179,22],[-179,22],[-179,20]])

if __name__=="__main__": unittest.main()
