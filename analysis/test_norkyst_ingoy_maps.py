import copy
import json
import unittest
from pathlib import Path
import numpy as np
from build_norkyst_ingoy_maps import rotated_vectors
from build_norkyst_ingoy_timeline import TRANSFORM
from check_norkyst_ingoy_maps import validate

ROOT=Path(__file__).resolve().parents[1]


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'research/norkyst-ingoy-2024-map-frames.json').read_text(encoding='utf-8'))
        cls.timeline=json.loads((ROOT/'research/norkyst-ingoy-2024-section-timeline.json').read_text(encoding='utf-8'))

    def test_source_and_profile_synchronization(self):validate(self.doc,self.timeline)

    def test_cardinal_directions_follow_projection(self):
        lon=np.array([24.0]);lat=np.array([72.0]);x,y=TRANSFORM.transform(lon,lat)
        for east,north in [(1,0),(0,1),(-1,0),(0,-1)]:
            u,v=rotated_vectors(lon,lat,np.array([east]),np.array([north]))
            x2,y2=TRANSFORM.transform(lon+east*.00001,lat+north*.00001)
            norm=np.hypot(x2-x,y2-y)
            self.assertAlmostEqual(float(u[0]),float(((x2-x)/norm)[0]),places=3)
            self.assertAlmostEqual(float(v[0]),float(((y2-y)/norm)[0]),places=3)
            self.assertAlmostEqual(float(np.hypot(u,v)[0]),1.0,places=10)

    def test_reject_changed_support_or_scope(self):
        for change in ['date','receipt','scale','footprint','colors']:
            doc=copy.deepcopy(self.doc)
            if change=='date':doc['frames'][0]['sample_time_utc']='2024-01-15T00:00:00Z'
            if change=='receipt':doc['frames'][0]['receipt_sha256']='0'*64
            if change=='scale':doc['rules']['velocity_arrow_scale']=.02
            if change=='footprint':doc['state_footprint_join_eligible']=True
            if change=='colors':doc['frames'][0]['salinity_cells_outside_color_limits']=999
            with self.assertRaises(ValueError):validate(doc,self.timeline)


if __name__=='__main__':unittest.main()
