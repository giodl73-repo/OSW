import unittest
from project_wsc_f3_time_window_brackets_v3 import reconstruct,source_time

def row(stamp,gear,z,v,temp='3'):
    return [{'text':s,'attributes':[]} for s in [stamp,str(gear),str(z),str(z+1),temp,'35','20','0','0',str(v)]]

class TimeWindowSelection(unittest.TestCase):
    def test_nearest_time_does_not_select_more_favorable_velocity(self):
        rows=[row('2004-07-20T23:00',1,70,5),row('2004-07-21T01:00',1,70,90),row('2004-07-21T00:30',2,250,20)]
        p=reconstruct(rows)[0][0]
        self.assertEqual(p['levels'][0]['provider_v_cm_s'],5)
        self.assertEqual(p['levels'][0]['source_time_offset_seconds'],-3600)
        self.assertEqual(p['actual_source_time_span_seconds'],5400)
    def test_window_boundary_is_inclusive_and_missing_is_not_extrapolated(self):
        rows=[row('2004-07-21T02:00',1,70,20),row('2004-07-21T02:01',2,250,20)]
        profiles,_=reconstruct(rows);self.assertEqual(len(profiles[0]['levels']),1);self.assertEqual(profiles[1]['levels'],[])
    def test_flagged_values_stay_missing_and_non_utc_offsets_are_not_discarded(self):
        p=reconstruct([row('2004-07-21T00:00',1,70,'?20')])[0][0]
        self.assertIsNone(p['levels'][0]['provider_v_cm_s'])
        with self.assertRaises(ValueError):source_time('2004-07-21T00:00+02:00')

if __name__=='__main__':unittest.main()
