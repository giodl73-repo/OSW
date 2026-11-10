import unittest
from derive_wsc_f3_warm_flow_brackets_v1 import bracket,value,selected_profiles

def profile():
    return {'time_utc':'2004-07-21T00:00:00Z','levels':[{'gear_id':str(i),'water_depth_m':z,'temperature_degrees_C':t,'provider_u_cm_s':0.,'provider_v_cm_s':v} for i,(z,t,v) in enumerate([(70,4,20),(250,3,30),(750,1,15),(1000,0,5)])]}

class ConditionalBracket(unittest.TestCase):
    def test_native_table_units_and_timestamp_representations_select_the_same_dates(self):
        headers=['Date/Time','Gear ID','Depth water [m]','Press [dbar]','Temp [°C]','Sal','Cur vel hor [cm/s]','DIR [deg]','Cur vel U [cm/s]','Cur vel V [cm/s]']
        html='<table><tr>'+''.join(f'<th>{i+1} {h}</th>' for i,h in enumerate(headers))+'</tr>'
        for stamp in ['2004-07-21T00:00','2004-07-22T00:00:00','2004-07-23T00:00:00Z']:
            for gear,z,t,v in [(1,250,3,20),(2,750,1,10)]:
                cells=[stamp,str(gear),str(z),str(z+1),str(t),'35','20','0','0',str(v)]
                html+='<tr>'+''.join(f'<td>{c}</td>' for c in cells)+'</tr>'
        profiles,nrows,gears=selected_profiles((html+'</table>').encode('utf8'))
        self.assertEqual([len(p['levels']) for p in profiles],[2,2,2]);self.assertEqual(nrows,6)
        self.assertEqual([bracket(p,10)['range_m'] for p in profiles],[[250,750]]*3)
    def test_component_bracket_does_not_become_point_depth_or_current_thickness(self):
        r=bracket(profile(),10);self.assertEqual(r['range_m'],[250,750]);self.assertIsNone(r['approximate_value_m']);self.assertIsNone(r['thickness_m']);self.assertIsNone(r['annual_range_m']);self.assertFalse(r['physical_current_bottom_established'])
    def test_native_pressure_censoring_and_flags_are_not_numeric_points(self):
        for text in ['?3.1','/3.1','*3.1','#3.1','>3.1','<3.1','ø3.1','3.1±0.1','']:
            self.assertIsNone(value({'text':text,'attributes':[]}))
        self.assertEqual(value({'text':'-0.3','attributes':[]}),-.3)
        self.assertIsNone(value({'text':'3.1','attributes':[{'class':'questionable'}]}))
    def test_missing_below_censors_support_instead_of_bridging_gap(self):
        p=profile();p['levels'][2]['temperature_degrees_C']=None;r=bracket(p,10)
        self.assertIsNone(r['range_m']);self.assertEqual(r['lower_bound_m'],250);self.assertFalse(r['lower_bound_exclusive'])
        p=profile();p['levels'][2]['water_depth_m']=900;self.assertIsNone(bracket(p,10)['range_m'])
    def test_disconnected_deep_warm_flow_is_not_inherited_by_a_shallow_core(self):
        p=profile();p['levels'][3].update(temperature_degrees_C=3,provider_v_cm_s=20)
        self.assertEqual(bracket(p,10)['range_m'],[250,750])
        p=profile()
        for r in p['levels']:r['provider_v_cm_s']=-20
        self.assertIsNone(bracket(p,10)['range_m']);self.assertIsNone(bracket(p,10)['lower_bound_m'])

if __name__=='__main__':unittest.main()
