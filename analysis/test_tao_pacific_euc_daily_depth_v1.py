import csv
import io
import json
import signal
import tempfile
import time
import unittest
from pathlib import Path
import collect_tao_pacific_euc_daily_depth_v1 as source


def csv_bytes(fields,units,rows):
    out=io.StringIO();w=csv.writer(out);w.writerow(fields);w.writerow(units);w.writerows(rows)
    return out.getvalue().encode('iso8859-1')


def target():
    return source.targets([{'station':'site165','array':'TAO','longitude':165,'latitude':0}])[0]


def field_bytes(modify=None):
    t=target();rows=[]
    depths=list(range(30,171,10));velocity=[0,0,0,10,20,50,100,80,40,20,10,0,-10,-10,-10]
    for date in t['times_utc']:
        for z,u in zip(depths,velocity):rows.append(['TAO','site165',165,0,date,z,u,1])
    if modify is not None:rows=modify(rows)
    return csv_bytes(source.FIELDS,source.UNITS,rows)


def metadata_bytes(wrong_unit=False):
    attrs={('u_1205','units'):'m/s' if wrong_unit else 'cm/s',('u_1205','standard_name'):'eastward_sea_water_velocity',
           ('u_1205','_FillValue'):'1e35',('u_1205','missing_value'):'1e35',('depth','units'):'m',('depth','positive'):'down',
           ('longitude','units'):'degrees_east',('latitude','units'):'degrees_north',('longitude','long_name'):'Nominal Longitude',
           ('latitude','long_name'):'Nominal Latitude',('time','long_name'):'Centered Time',
           ('QU_5205','description'):'0=missing data, 1=highest, 2=standard, 3=lower',
           ('NC_GLOBAL','summary'):'Daily averages starting00:00Z labelled12:00Z',
           ('NC_GLOBAL','license'):'Data may be used and redistributed for free',('NC_GLOBAL','institution'):'NOAA PMEL'}
    return source.encoded({'table':{'columnNames':['Row Type','Variable Name','Attribute Name','Data Type','Value'],
                                   'rows':[['attribute',a,b,'String',v] for (a,b),v in attrs.items()]}})


class DailyADCPDepth(unittest.TestCase):
    def test_units_flags_and_complete_daily_intervals(self):
        source.metadata(metadata_bytes())
        with self.assertRaises(ValueError):source.metadata(metadata_bytes(True))
        p,n=source.profiles(field_bytes(),target())
        self.assertEqual(n,45*6)
        self.assertEqual(p[0]['primary_lower_isotach_depth_m'],130)
        self.assertEqual(p[0]['primary_threshold_layer_span_m'],70)
        self.assertEqual(p[0]['accepted_eastward_velocity_m_s'][6],1)
        self.assertEqual(p[0]['provider_averaging_interval_utc'],{'start':'2005-03-14T00:00:00Z','end_exclusive':'2005-03-15T00:00:00Z'})
        for k in ['physical_current_thickness_m','annual_range_m','volume_m3']:self.assertIsNone(p[0][k])

    def test_flags_fill_and_nonfinite_are_not_zero(self):
        for value,flag in [('100',0),('100',3),('100',5),('1e35',1),('NaN',2),('100','NaN')]:
            self.assertIsNone(source.decode(value,flag))
        self.assertEqual(source.decode('-20',2),-.2)

    def test_quality_rejection_censors_instead_of_bridging(self):
        def modify(rows):
            for r in rows:
                if r[5]==120:r[-1]=3
            return rows
        p,_=source.profiles(field_bytes(modify),target())
        self.assertIsNone(p[0]['primary_lower_isotach_depth_m'])
        self.assertEqual(p[0]['threshold_contexts'][1]['lower_status'],'censored_before_missing_or_dry_level')

    def test_large_returned_depth_gap_censors_locked_core(self):
        p,_=source.profiles(field_bytes(lambda rows:[r for r in rows if r[5] not in [100,110,120]]),target())
        self.assertIsNone(p[0]['primary_lower_isotach_depth_m'])
        self.assertEqual(p[0]['threshold_contexts'][1]['core_depth_m'],90)
        self.assertEqual(p[0]['threshold_contexts'][1]['lower_status'],'censored_at_returned_depth_gap')

    def test_missing_days_retained_without_mean_or_substitution(self):
        p,_=source.profiles(field_bytes(lambda rows:[r for r in rows if '03-15' not in r[4]]),target())
        self.assertEqual(p[1]['status'],'no_source_rows_for_predeclared_day')
        self.assertEqual(p[1]['source_depths_m'],[])
        self.assertIsNone(p[1]['primary_lower_isotach_depth_m'])

    def test_duplicate_wrong_station_and_wrong_time_fail(self):
        for modify in [lambda rows:rows+[rows[0]],lambda rows:[r[:1]+['other']+r[2:] for r in rows],
                       lambda rows:[r[:4]+['2005-03-14T00:00:00Z']+r[5:] for r in rows]]:
            with self.assertRaises(ValueError):source.profiles(field_bytes(modify),target())

    def test_no_primary_promotion_at_core_window_edge(self):
        def modify(rows):
            for r in rows:r[6]=100 if r[5]==50 else 0
            return rows
        p,_=source.profiles(field_bytes(modify),target())
        self.assertTrue(p[0]['threshold_contexts'][1]['core_search_window_edge'])
        self.assertIsNone(p[0]['primary_lower_isotach_depth_m'])

    def test_separate_lobes_are_not_joined_or_reselected(self):
        z=list(range(30,201,10));u=[0.0]*len(z)
        for depth,speed in [(80,.5),(90,1),(100,.5),(160,.5),(170,1),(180,.5)]:u[z.index(depth)]=speed
        r=source.layer(z,u,.1)
        self.assertEqual(r['core_depth_m'],90)
        self.assertLess(r['lower_depth_m'],120)

    def test_global_request_scalar_budget_and_fixed_dates(self):
        chosen=[{'array':'TAO','station':'site'+str(lon),'longitude':lon,'latitude':0} for lon in [165,190,220,250]]
        plan=source.targets(chosen)
        self.assertEqual(len(plan),16);self.assertEqual(len({t['url'] for t in plan}),16)
        self.assertEqual(sum(t['reserved_numeric_scalars'] for t in plan),11520)
        for t in plan:
            self.assertEqual(len(t['times_utc']),3)
            self.assertIn('depth/10',t['url']);self.assertNotIn('QU_5205%3E',t['url'])

    def test_catalogue_station_ids_not_guessed(self):
        rows=[['TAO','actual_'+str(lon),lon,0] for lon in [165,190,220,250]]
        raw=csv_bytes(['array','station','longitude','latitude'],['','','degrees_east','degrees_north'],rows)
        self.assertEqual(source.stations(raw)[0]['station'],'actual_165')
        with self.assertRaises(ValueError):source.stations(csv_bytes(['array','station','longitude','latitude'],['','','degrees_east','degrees_north'],rows[:-1]))

    def test_pre_request_journal_and_archive_before_parser(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);j={'requests':[],'total_body_bytes':0};t={'target_id':'test','url':'https://example.invalid/raw','cap_bytes':100}
            class Response:
                status=200;url=t['url'];headers={}
                def __init__(self):self.body=io.BytesIO(b'not-valid-csv')
                def read(self,n):return self.body.read(n)
                def __enter__(self):return self
                def __exit__(self,*a):pass
            calls=[]
            def opener(req,timeout):
                calls.append(req.full_url)
                self.assertEqual(json.loads((folder/'journal.json').read_bytes())['requests'][0]['status'],'reserved_before_http')
                return Response()
            signal.signal(signal.SIGALRM,source.alarm)
            raw=source.acquire(t,folder,j,opener,time.monotonic()+100)
            with self.assertRaises(ValueError):source.profiles(raw,target())
            self.assertEqual((folder/'test.raw').read_bytes(),raw)
            with self.assertRaises(ValueError):source.acquire(t,folder,j,opener,time.monotonic()+100)
            self.assertEqual(len(calls),1)

    def test_absolute_deadline_stops_before_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            j={'requests':[],'total_body_bytes':0}
            self.assertIsNone(source.acquire({'target_id':'x','url':'https://invalid','cap_bytes':5},Path(tmp),j,None,time.monotonic()+20))
            self.assertEqual(j['requests'],[])
        with self.assertRaises(SystemExit):source.alarm(signal.SIGTERM,None)
        with self.assertRaises(source.SourceDeadline):source.alarm(signal.SIGALRM,None)

    def test_failed_transport_one_attempt_and_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            j={'requests':[],'total_body_bytes':0};calls=[];t={'target_id':'x','url':'https://invalid','cap_bytes':5}
            def opener(*a,**k):calls.append(1);raise TimeoutError('simulated')
            signal.signal(signal.SIGALRM,source.alarm)
            self.assertIsNone(source.acquire(t,Path(tmp),j,opener,time.monotonic()+100))
            self.assertEqual(j['requests'][0]['attempts'],1)
            with self.assertRaises(ValueError):source.acquire(t,Path(tmp),j,opener,time.monotonic()+100)
            self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
