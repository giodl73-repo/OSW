import unittest
from capture_gaspe1991_adcp_info_v1 import describe
class Tests(unittest.TestCase):
    def test_original_units_and_uncertainty_preserved(self):
        p={'table':{'columnNames':['Row Type','Variable Name','Attribute Name','Data Type','Value'],'rows':[['variable','u','','double',''],['attribute','u','units','String','mm s-1'],['attribute','NC_GLOBAL','processing','String','raw instrument velocity']]}}
        r=describe(p);self.assertEqual(r['variables']['u']['attributes']['units'],'mm s-1');self.assertEqual(r['global_attributes']['processing'],'raw instrument velocity');self.assertEqual(r['native_data_rows_decoded'],0)
    def test_wrong_layout_rejected(self):
        with self.assertRaises(ValueError):describe({'table':{'columnNames':['wrong'],'rows':[]}})
    def test_no_variables_rejected(self):
        with self.assertRaises(ValueError):describe({'table':{'columnNames':['Row Type','Variable Name','Attribute Name','Data Type','Value'],'rows':[]}})
if __name__=='__main__':unittest.main()
