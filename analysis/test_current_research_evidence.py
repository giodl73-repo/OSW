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
