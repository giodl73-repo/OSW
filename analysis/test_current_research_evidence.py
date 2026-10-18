"""Scientific input and figure changes invalidate the shared research registry."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import current_research_evidence as evidence


class ResearchEvidenceTests(unittest.TestCase):
    def test_registry_and_index_cover_the_retained_research_documents(self):
        registry = evidence.verify()
        source_index = json.loads((evidence.ROOT / 'almanac/index-sources.json').read_bytes())
        serialized = json.dumps(source_index)
        for path in [evidence.PATH, *registry['documents']]:
            self.assertIn(path, serialized)
        owner=next(scene for scene in registry['scenes'] if scene['current_id']=='aleutian')
        self.assertEqual(set(owner['support_source_sha256']),set(evidence.NATIVE_INPUTS))
        self.assertEqual(owner['support_source_sha256'],{path:registry['documents'][path] for path in evidence.NATIVE_INPUTS})

    def test_changed_scientific_source_is_rejected(self):
        original = Path.read_bytes
        target = evidence.ROOT / 'research/redsox-lower-nc-dated-section-diagnostic.json'
        def altered(path):
            raw = original(path)
            if path == target:
                doc = json.loads(raw)
                doc['fully_blinded_before_any_selected_velocity_exposure'] = True
                return json.dumps(doc).encode()
            return raw
        with patch.object(Path, 'read_bytes', altered), self.assertRaises(ValueError):
            evidence.verify()

    def test_underway_negative_result_stays_distinct_from_hourly_spans(self):
        registry=evidence.verify()
        owner=next(s for s in registry['scenes'] if s['current_id']=='aleutian')
        self.assertEqual(owner['source_file'],evidence.SPANS)
        self.assertIn(evidence.AVERAGES,[s['document'] for s in owner['source_links']])
        self.assertEqual(len(owner['additional_figures']),5)
        table=owner['additional_tables'][0]
        self.assertEqual([r[2:4] for r in table['rows']],
            [['128','95'],['81','41'],['53','16'],['103','92'],['57','39'],['29','16'],['96','85'],['54','37'],['27','15']])
        self.assertTrue(all(r[-1]=='0 / 14' for r in table['rows']))
        self.assertIsNone(owner['whole_current_width_km'])
        self.assertIsNone(owner['annual_width_range_km'])
        self.assertIs(owner['new_width_record_admitted'],False)

    def test_changed_underway_result_or_figure_invalidates_registration(self):
        original=Path.read_bytes
        for name in [evidence.AVERAGES,'figures/aleutian-p14n-1993-underway-averages.svg']:
            target=evidence.ROOT/name
            def altered(path):
                raw=original(path)
                return raw+b' ' if path==target else raw
            with self.subTest(source=name),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):
                evidence.verify()

    def test_composite_cannot_replace_unresolved_nominal_or_no_bridge_result(self):
        registry=evidence.verify()
        owner=next(s for s in registry['scenes'] if s['current_id']=='aleutian')
        self.assertEqual(len(owner['additional_tables']),2)
        rows=owner['additional_tables'][1]['rows']
        self.assertEqual(len(rows),9)
        self.assertTrue(all(r[2:4]==['Unresolved','Unresolved'] for r in rows))
        self.assertEqual(sum(int(r[-1].split('/')[0]) for r in rows),18)
        self.assertIn(evidence.AVERAGES,[s['document'] for s in owner['source_links']])
        self.assertIn(evidence.COMPOSITE,[s['document'] for s in owner['source_links']])
        self.assertIs(owner['new_width_record_admitted'],False)

    def test_changed_source_archive_invalidates_the_registry(self):
        original = Path.read_bytes
        target = evidence.ROOT / 'research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip'
        def altered(path):
            raw = original(path)
            return raw + b'changed' if path == target else raw
        with patch.object(Path, 'read_bytes', altered), self.assertRaises(ValueError):
            evidence.verify()

    def test_changed_figure_cannot_silently_replace_reviewed_visualization(self):
        original = Path.read_bytes
        target = evidence.ROOT / 'figures/redsox-lower-nc-section-diagnostic.svg'
        def altered(path):
            raw = original(path)
            return raw + b'<!--changed-->' if path == target else raw
        with patch.object(Path, 'read_bytes', altered), self.assertRaises(ValueError):
            evidence.verify()


if __name__ == '__main__':
    unittest.main()
