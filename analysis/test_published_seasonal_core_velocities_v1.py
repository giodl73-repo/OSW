import copy
import gzip
import json
import unittest
import published_seasonal_core_velocities_v1 as core
import published_seasonal_core_velocity_index_v1 as index


class CoreProjectionTests(unittest.TestCase):
    def parent(self):
        ids = sorted({r["entity_id"] for r in core.records()})
        return {"schema": "osw.query-bundle.v1", "manifest": {"old": {"keep": True}},
                "collections": {"objects": [{"id": owner, "old": 1} for owner in ids] + [{"id": "current:other"}],
                                "widths": [{"id": "old-width", "width": 7}],
                                "current_speed_statistics": [{"id": "existing-pooled-speed", "count": 328}]}}

    def test_preserve_parent_previous_collections_and_owner_fields(self):
        parent = self.parent()
        before = copy.deepcopy(parent)
        result = core.prepare(parent, logical_parent_sha256=core.PARENT)
        self.assertEqual(parent, before)
        for key in ["widths", "current_speed_statistics"]:
            self.assertEqual(result["collections"][key], parent["collections"][key])
        for old, new in zip(parent["collections"]["objects"], result["collections"]["objects"]):
            self.assertEqual({k: v for k, v in new.items() if k != core.JOIN}, old)
        self.assertEqual(result["manifest"]["old"], parent["manifest"]["old"])
        self.assertEqual(len(result["collections"][core.COLLECTION]), 6)

    def test_source_qualifiers_pointers_and_shared_support(self):
        source, _ = core.document()
        for row in core.records():
            target = source["records"][int(row["source_pointer"].split("/")[-1])]
            self.assertEqual(target["id"], row["id"])
            for key, value in target.items():
                self.assertEqual(row[key], value)
            self.assertEqual(row["common_support"]["selected_section_count"], 31)
            self.assertIsNone(row["observation_count"])
            self.assertIsNone(row["geometry"])
            self.assertIsNone(row["confidence_interval"])
        interval = next(r for r in core.records() if r["estimate_kind"] == "approximate_prose_interval")
        self.assertEqual(interval["interval_m_s"], [0.4, 0.5])
        self.assertIsNone(interval["value_m_s"])
        threshold = next(r for r in core.records() if r["estimate_kind"] == "reported_greater_than")
        self.assertEqual(threshold["lower_threshold_m_s"], 0.3)
        self.assertIsNone(threshold["interval_m_s"])

    def test_refuse_wrong_parent_missing_duplicate_or_repeated_owner(self):
        with self.assertRaises(ValueError):
            core.prepare(self.parent(), logical_parent_sha256="wrong")
        for change in [lambda p: p["collections"]["objects"].pop(0),
                       lambda p: p["collections"]["objects"].append(copy.deepcopy(p["collections"]["objects"][0])),
                       lambda p: p["collections"]["objects"][0].update({core.JOIN: []}),
                       lambda p: p["manifest"].update(input_sha256={core.SOURCE: "old"})]:
            parent = self.parent()
            change(parent)
            with self.assertRaises(ValueError):
                core.prepare(parent, logical_parent_sha256=core.PARENT)
        prepared = core.prepare(self.parent(), logical_parent_sha256=core.PARENT)
        with self.assertRaises(ValueError):
            core.prepare(prepared, logical_parent_sha256=core.PARENT)


class IndexPreservationTests(unittest.TestCase):
    def fixture(self):
        text = '{ "schema": "old", "original spacing": true }\n'
        raw = index.encode({"schema": "osw.almanac-index-bundle.v1", "documents": {"research/old.json": text}})
        packed = gzip.compress(raw, mtime=0)
        catalog = {"schema": "osw.almanac-index-catalog.v1", "source_count": 1,
                   "source_bytes": len(text.encode()), "bundle_sha256": index.sha(raw), "bundle_bytes": len(raw),
                   "compressed_sha256": index.sha(packed), "compressed_bytes": len(packed),
                   "documents": [{"path": "research/old.json", "source_sha256": index.sha(text.encode()), "source_bytes": len(text.encode())}]}
        return catalog, packed, {"schema": "osw.almanac-index-sources.v1", "documents": ["research/old.json"]}, text

    def test_preserve_old_strings_and_all_six_new_record_pointers(self):
        catalog, packed, registry, text = self.fixture()
        source = (core.ROOT / core.SOURCE).read_bytes()
        files, audit = index._extend_verified(catalog, packed, registry, source)
        docs = json.loads(gzip.decompress(files["almanac/index-data.json.gz"]))["documents"]
        self.assertEqual(docs["research/old.json"], text)
        self.assertEqual(docs[core.SOURCE].encode(), source)
        self.assertEqual(len(json.loads(docs[core.SOURCE])["records"]), 6)
        self.assertEqual(audit["original_source_strings_preserved"], 1)
        self.assertEqual(audit["replaced_source_paths"], [])
        with self.assertRaises(ValueError):
            index._extend_verified(json.loads(files["almanac/index-catalog.json"]), files["almanac/index-data.json.gz"], json.loads(files["almanac/index-sources.json"]), source)

    def test_refuse_bad_compressed_or_installed_catalog_before_loading(self):
        catalog, packed, registry, _ = self.fixture()
        with self.assertRaises(ValueError):
            index._extend_verified(catalog, packed+b"changed", registry, b"{}")
        with self.assertRaises(ValueError):
            index.source_index(b"{}", b"not-opened", b"not-opened")


if __name__ == "__main__":
    unittest.main()
