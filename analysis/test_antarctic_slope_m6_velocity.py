"""Check actual coverage and distinguish equal-year means from pooled samples."""
import json
import unittest
import subprocess
from datetime import datetime
from build_antarctic_slope_m6_velocity import ROOT, OUTPUT, build, aggregate


class M6VelocityTests(unittest.TestCase):
    def test_reconstruction_and_source_support(self):
        data=build()
        self.assertEqual(data,json.loads(OUTPUT.read_bytes()))
        monthly=[r for r in data['samples'] if r['series_kind']=='monthly']
        seasonal=[r for r in data['samples'] if r['series_kind']=='seasonal_composite']
        self.assertEqual(len(monthly),49)
        self.assertEqual(sum(r['available_pairs'] for r in monthly),16393)
        self.assertEqual([r['label'] for r in monthly if r['partial_month']],['M6 228 m · 2017-02','M6 228 m · 2021-02'])
        self.assertEqual(seasonal[1]['contributing_years'],[2018,2019,2020])
        self.assertTrue(all(0<r['hourly_coverage_fraction']<1 for r in monthly))
        self.assertTrue(all(r['measurement_uncertainty_cm_s'] is None for r in data['samples']))

    def test_sparse_hours_are_not_zero_and_years_are_equal_weighted(self):
        readings={datetime(2018,1,1):(10.,-2.),datetime(2019,1,1):(20.,-4.),datetime(2019,1,1,1):(20.,-4.)}
        rows=aggregate(readings)
        self.assertEqual(rows[0]['eastward_mean_cm_s'],10.)
        self.assertEqual(rows[0]['available_pairs'],1)
        composite=next(r for r in rows if r['series_kind']=='seasonal_composite')
        self.assertEqual(composite['eastward_mean_cm_s'],15.)
        self.assertEqual(composite['northward_mean_cm_s'],-3.)
        self.assertEqual(composite['eastward_interannual_span_cm_s'],[10.,20.])


if __name__=='__main__':unittest.main()


def test_native_velocity_guard_rejects_coherent_mutation(tmp_path):
    from test_rust_query_browser import CLI
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    packet['collections']['current_velocity_samples'][0]['eastward_mean_cm_s']=0
    packet['manifest']['input_sha256']['research/antarctic-slope-m6-velocity-series.json']='0'*64
    target=tmp_path/'changed-velocity.json'
    target.write_text(json.dumps(packet),encoding='utf8')
    result=subprocess.run([str(CLI),str(target)],capture_output=True,text=True,encoding='utf8')
    assert result.returncode==2 and 'M6 velocity' in result.stderr,result.stderr
