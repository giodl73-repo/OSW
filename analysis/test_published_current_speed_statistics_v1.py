import copy
import unittest
import published_current_speed_statistics_v1 as m


class ProjectionTests(unittest.TestCase):
    def parent(self):
        return {"schema": "osw.query-bundle.v1", "manifest": {"historical": "preserve"},
                "collections": {"objects": [{"id": m.OWNER, "label": "EACC"}, {"id": "current:other"}],
                                "widths": [{"id": "old", "value": 7}], "measurements": []}}

    def test_lossless_scientific_collections_and_original_input(self):
        parent = self.parent()
        original = copy.deepcopy(parent)
        out = m.prepare(parent, logical_parent_sha256=m.PARENT)
        self.assertEqual(parent, original)
        for name in ["widths", "measurements"]:
            self.assertEqual(out["collections"][name], original["collections"][name])
        self.assertEqual(out["collections"]["objects"][1], original["collections"]["objects"][1])
        self.assertEqual(len(out["collections"][m.COLLECTION]), 15)
        self.assertEqual(out["manifest"]["historical"], "preserve")

    def test_monthly_and_seasonal_are_same_observations(self):
        rows = m.records()
        for kind in ["monthly", "seasonal"]:
            self.assertEqual(sum(r["observation_count"] for r in rows if r["statistic_period"] == kind), 328)
        self.assertTrue(all(r["confidence_interval"] is None and r["geometry"] is None for r in rows))

    def test_reject_wrong_parent_missing_owner_and_repeated_admission(self):
        with self.assertRaises(ValueError):
            m.prepare(self.parent(), logical_parent_sha256="other")
        parent = self.parent()
        parent["collections"]["objects"] = []
        with self.assertRaises(ValueError):
            m.prepare(parent, logical_parent_sha256=m.PARENT)
        out = m.prepare(self.parent(), logical_parent_sha256=m.PARENT)
        with self.assertRaises(ValueError):
            m.prepare(out, logical_parent_sha256=m.PARENT)

    def test_reject_inconsistent_monthly_counts_and_overlapping_seasons(self):
        for change in [lambda d: d["monthly_records"][0].update(observation_count=13),
                       lambda d: d["records"][0]["months"].append(1)]:
            doc, pin = m.document()
            change(doc)
            with self.assertRaises(ValueError):
                m.records(doc, pin)

    def test_preserve_source_conflict_and_exact_table_value(self):
        row = next(r for r in m.records() if r.get("season") == "NE")
        self.assertEqual(row["minimum"], 0.05)
        self.assertTrue(row["source_conflicts"])
        self.assertEqual(row["source_pointer"], "/records/2")


if __name__ == "__main__":
    unittest.main()
