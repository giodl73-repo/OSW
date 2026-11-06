import unittest
import xml.etree.ElementTree as ET
import eac_kerry_2020_mean_core_v2 as m

class PortableFigures(unittest.TestCase):
    def test_all_source_records_and_scientific_rules_preserved(self):
        before=m.base.build();after=m.build()
        self.assertEqual(before['records'],after['records'])
        self.assertEqual(before['method'],after['method'])
        self.assertEqual(before['source'],after['source'])
        self.assertEqual(before['source_labeling_discrepancy'],after['source_labeling_discrepancy'])

    def test_svg_text_and_scales_have_inline_styling(self):
        for compact in [False,True]:
            svg=ET.fromstring(m.figure(m.build(),compact))
            for text in svg.findall('{http://www.w3.org/2000/svg}text'):
                self.assertIsNotNone(text.get('font-size'))
                self.assertIsNotNone(text.get('font-family'))
            lines=svg.findall('{http://www.w3.org/2000/svg}line');self.assertTrue(lines)
            for line in lines:self.assertEqual(line.get('stroke'),'#cbdcdd')

if __name__=='__main__':unittest.main()
