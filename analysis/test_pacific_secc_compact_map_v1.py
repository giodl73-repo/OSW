"""Exact-vector, responsive markup and inherited engine preservation checks."""
import copy
from html.parser import HTMLParser
import json
import unittest
import xml.etree.ElementTree as ET

import pacific_secc_compact_map_v1 as compact


class Markup(HTMLParser):
    def __init__(self): super().__init__(); self.tags = []
    def handle_starttag(self, tag, attrs): self.tags.append((tag, dict(attrs)))


class CompactMap(unittest.TestCase):
    def parent(self):
        result = json.loads((compact.ROOT / 'research/eacc-connection-presentation-saved-engine-manifest-v4.json').read_bytes())
        result['sha256'][compact.PAGE] = compact.BASE_PAGE_SHA
        result['sha256']['almanac/query-engine.wasm'] = compact.WASM_SHA
        result['pacific_secc_reference_engine_delivery_v1'] = {'logical_sha256': compact.LOGICAL,
            'matching_binary_sha256': compact.WASM_SHA, 'preserve_compiler_receipt': True}
        return result

    def test_every_original_land_route_endpoint_and_dateline_vector_is_retained_exactly(self):
        original = ET.fromstring((compact.ROOT / compact.SOURCE).read_bytes())
        derived = ET.fromstring(compact.compact_svg())
        nested = derived.find(compact.tag('svg'))
        tags = {compact.tag(k) for k in ['path', 'polyline', 'circle', 'line']}
        self.assertEqual([(r.tag, r.attrib) for r in nested], [(r.tag, r.attrib) for r in original if r.tag in tags])
        self.assertEqual(derived.attrib['viewBox'], '0 0 320 190')
        labels = [r.text for r in derived.findall(compact.tag('text'))]
        self.assertIn('164°E', labels); self.assertIn('180°E', labels)
        self.assertIn('≈ 1,800 km · editorial reach', labels)
        self.assertEqual((compact.ROOT / compact.FIGURE).read_bytes(), compact.compact_svg())

    def test_media_source_wraps_one_image_and_keeps_full_map_link_and_all_other_page_bytes(self):
        text = compact.support_page().decode()
        parsed = Markup(); parsed.feed(text)
        sources = [attrs for tag, attrs in parsed.tags if tag == 'source']
        self.assertEqual(sources, [{'media': '(max-width:480px)', 'srcset': '../' + compact.FIGURE}])
        self.assertTrue(any(tag == 'a' and attrs.get('href') == '../' + compact.SOURCE for tag, attrs in parsed.tags))
        unwrapped = text.replace('<picture><source media="(max-width:480px)" srcset="../' + compact.FIGURE + '">', '').replace('</picture>', '')
        self.assertEqual(unwrapped.encode(), compact.presentation.support_page())

    def test_atlas_ui_only_adds_the_target_figure_picture_branch(self):
        raw = compact.atlas_ui()
        original = (compact.ROOT / compact.UI_ARCHIVE).read_bytes()
        text = raw.decode()
        start = text.index("      if(row.figure==='" + compact.SOURCE + "'){")
        end = text.index('      }\n', start) + len('      }\n')
        self.assertEqual((text[:start] + text[end:]).encode(), original)
        self.assertIn("mobile.media='(max-width:480px)'", text[start:end])
        self.assertIn(compact.FIGURE, text[start:end])

    def test_engine_overlay_preserves_all_scientific_and_historical_namespaces_and_pins(self):
        parent = self.parent(); before = copy.deepcopy(parent)
        result = compact.overlay(parent, parent_manifest_sha=compact.BASE_ENGINE_SHA, control_commit='a' * 40)
        self.assertEqual(parent, before)
        changed = {p for p, sha in parent['sha256'].items() if result['sha256'][p] != sha}
        self.assertEqual(changed, {compact.PAGE, compact.UI})
        self.assertEqual(set(result['sha256']) - set(parent['sha256']), {compact.FIGURE, compact.MODULE, compact.PROTOCOL})
        for key in set(parent) - {'sha256'}: self.assertEqual(result[key], parent[key])
        self.assertEqual(result['sha256']['almanac/query-engine.wasm'], compact.WASM_SHA)
        self.assertFalse(result[compact.KEY]['native_wasm_rebuilt'])

    def test_changed_parent_and_repeat_are_refused(self):
        parent = self.parent()
        parent['sha256'][compact.UI] = 'wrong'
        with self.assertRaises(ValueError): compact.overlay(parent, parent_manifest_sha=compact.BASE_ENGINE_SHA, control_commit='a' * 40)
        result = compact.overlay(self.parent(), parent_manifest_sha=compact.BASE_ENGINE_SHA, control_commit='a' * 40)
        with self.assertRaises(ValueError): compact.overlay(result, parent_manifest_sha=compact.BASE_ENGINE_SHA, control_commit='a' * 40)


if __name__ == '__main__': unittest.main()
