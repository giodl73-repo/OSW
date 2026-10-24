"""Platform tolerance is confined to unrounded geodesic outputs, never data."""
import copy
import json
import math
import unittest
from build_antilles_sadcp_layer_spans import ROOT, OUTPUT
from compare_shipboard_reconstruction import matches


class ShipboardRoundoffTests(unittest.TestCase):
    def setUp(self):
        self.document=json.loads((ROOT/OUTPUT).read_bytes())

    def test_one_ulp_geodesic_roundoff_is_accepted_but_larger_change_is_not(self):
        bad=copy.deepcopy(self.document)
        case=next(c for r in bad['rows'] for c in r['threshold_cases'] if c['survey_span_km'] is not None)
        value=case['survey_span_km']
        case['survey_span_km']=math.nextafter(value,math.inf)
        self.assertTrue(matches(self.document,bad))
        case['survey_span_km']=value+1e-8
        self.assertFalse(matches(self.document,bad))

    def test_coordinates_velocities_rounding_and_admission_stay_exact(self):
        for mode in ['coordinate','velocity','rounded','fraction','source','admission','nonfinite']:
            bad=copy.deepcopy(self.document)
            row=bad['rows'][0];case=next(c for c in row['threshold_cases'] if c['survey_span_km'] is not None)
            if mode=='coordinate':
                point=case['shoreward_boundary']['coordinates_lon_lat'];point[0]=math.nextafter(point[0],math.inf)
            if mode=='velocity':
                cell=next(p for p in row['profile_bins'] if p['northward_m_s'] is not None);cell['northward_m_s']=math.nextafter(cell['northward_m_s'],math.inf)
            if mode=='rounded':case['approximate_span_km']+=1
            if mode=='fraction':case['threshold_fraction']=math.nextafter(case['threshold_fraction'],math.inf)
            if mode=='source':bad['subset_sha256']='0'*64
            if mode=='admission':row['current_association_verified']=True
            if mode=='nonfinite':case['survey_span_km']=float('inf')
            with self.subTest(mode=mode):self.assertFalse(matches(self.document,bad))

    def test_missing_distance_cannot_be_replaced_by_zero(self):
        bad=copy.deepcopy(self.document)
        case=next(c for r in bad['rows'] for c in r['threshold_cases'] if c['survey_span_km'] is None)
        case['survey_span_km']=0.0
        self.assertFalse(matches(self.document,bad))


if __name__=='__main__':unittest.main()
