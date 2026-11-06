import copy,hashlib,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import netCDF4,numpy as np
import collect_act2011_observed_pair_v1 as source


def fixture(depth=100.,south=.4,lat=-34.,units='m/s',missing=False,shift_last=False,n=3):
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'point.nc'
        with netCDF4.Dataset(path,'w',format='NETCDF3_CLASSIC') as ds:
            ds.createDimension('time',n);ds.latitude=lat;ds.longitude=28.
            t=ds.createVariable('time','f8',('time',));t.units='days since 1970-01-01 00:00:00';t.calendar='standard';t.standard_name='time'
            z=ds.createVariable('depth','f8',('time',));z.units='m';z.positive='down';z.reference_datum='sea_surface';z.standard_name='depth'
            u=ds.createVariable('u','f8',('time',),fill_value=1e35);u.units=units;u.standard_name='eastward_sea_water_velocity'
            v=ds.createVariable('v','f8',('time',),fill_value=1e35);v.units=units;v.standard_name='northward_sea_water_velocity'
            if n==3:
                dates=[source.datetime.fromisoformat(s.replace('Z','')) for s in source.DATES]
                if shift_last:dates[-1]+=source.timedelta(hours=1)
                t[:]=netCDF4.date2num(dates,t.units);z[:]=depth
                f=100 if units=='cm/s' else 1
                u[:]=.2*f;v[:]=-south*f
                if missing:v[1]=v._FillValue
        return path.read_bytes()


def prior():return {'operations':[{'target_id':'old'+str(i),'command':'LIST','path':'/old/'+str(i)} for i in range(6)],'total_body_bytes':73839}


def plan(payloads):return [{'target_id':['readme','instrument-01','instrument-02'][i],'path':source.BASE+source.PATHS[i],
 'provider_size_bytes':len(raw),'provider_asserted_sha256':source.sha(raw)} for i,raw in enumerate(payloads)]


class Client:
    def __init__(self,payloads):self.payloads=dict(zip([source.BASE+p for p in source.PATHS],payloads));self.commands=[];self.closed=False
    def connect(self,*a,**k):pass
    def login(self,*a):assert a==('anonymous','anonymous@')
    def close(self):self.closed=True
    def retrbinary(self,command,callback,blocksize):self.commands.append(command);callback(self.payloads[command.removeprefix('RETR ')])


class ObservedPair(unittest.TestCase):
    def test_exact_native_values_and_conditional_scenario_not_thickness(self):
        report={'profiles':[]};source.decode([fixture(),fixture(300,0)],report)
        self.assertTrue(report['native_decode_completed']);self.assertEqual(len(report['profiles']),3)
        p=report['profiles'][0];self.assertTrue(p['provider_depth_and_frame_supported'])
        self.assertAlmostEqual(p['threshold_contexts'][1]['lower_isotach_scenario_m'],250)
        self.assertEqual(p['threshold_contexts'][1]['interpolation_bracket_m'],[100,300])
        self.assertIsNone(p['physical_thickness_m']);self.assertIsNone(p['annual_range_m']);self.assertIsNone(p['volume_m3'])
        self.assertFalse(p['physical_current_identity_independently_verified'])

    def test_centimetre_conversion_and_CF_missing_mask_not_zero(self):
        report={'profiles':[]};source.decode([fixture(units='cm/s'),fixture(300,0,units='cm/s',missing=True)],report)
        self.assertAlmostEqual(report['instrument_observations'][0][0]['northward_m_s'],-.4)
        self.assertIsNone(report['instrument_observations'][1][1]['northward_m_s'])
        self.assertIsNone(report['profiles'][1]['threshold_contexts'][1]['lower_isotach_scenario_m'])

    def test_missing_timestamp_and_different_site_cannot_be_joined(self):
        for raw in [fixture(300,0,lat=-34.2),fixture(300,0,shift_last=True)]:
            report={'profiles':[]};source.decode([fixture(),raw],report)
            self.assertFalse(report['profiles'][-1]['provider_depth_and_frame_supported'])
            self.assertEqual(report['profiles'][-1]['threshold_contexts'],[])

    def test_gap_reverse_and_deep_above_threshold_keep_censoring(self):
        self.assertEqual(source.pair_diagnostic([100,700],[.4,0],.1)['status'],'censored_at_predeclared_500m_sample_gap')
        self.assertIsNone(source.pair_diagnostic([100,300],[-.4,0],.1)['lower_isotach_scenario_m'])
        r=source.pair_diagnostic([100,300],[.4,.2],.1)
        self.assertEqual(r['deeper_observed_sample_depth_m'],300);self.assertIsNone(r['lower_isotach_scenario_m']);self.assertIsNone(r['physical_current_bottom_m'])

    def test_global_native_reserve_checked_before_arrays_not_per_instrument(self):
        report={'profiles':[]}
        with self.assertRaisesRegex(ValueError,'Whole-cohort'):source.decode([fixture(n=30000),fixture(n=30000)],report)
        self.assertEqual(len(report['native_headers']),2);self.assertNotIn('instrument_observations',report)
        report={'profiles':[]}
        with self.assertRaises(ValueError):source.decode([fixture(units='knots'),fixture(300,0)],report)

    def test_actual_transfer_preserves_old_receipts_and_four_op_allowance(self):
        payloads=[b'Public archive. Credit the investigators.',fixture(),fixture(300,0)];p=prior();before=copy.deepcopy(p['operations']);c=Client(payloads)
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            report,j,failed=source.collect(Path(temp)/'out',c,p,plan(payloads),time.monotonic()+158)
            self.assertFalse(failed);self.assertEqual(j['operations'][:6],before);self.assertEqual(len(j['operations']),10)
            self.assertEqual(j['unused_independent_case_remote_operations'],8);self.assertTrue(j['producer_finalized_before_artifact_upload'])
            self.assertTrue(c.closed);self.assertEqual(len(c.commands),3);self.assertEqual(report['new_depth_references_admitted'],0)
            self.assertEqual(j['metadata_stage_operations_used_unchanged'],6)

    def test_restrictive_document_stops_before_native_fields(self):
        payloads=[b'Access is restricted. Not for public release.',fixture(),fixture(300,0)];c=Client(payloads)
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            report,j,failed=source.collect(Path(temp)/'out',c,prior(),plan(payloads),time.monotonic()+158)
            self.assertTrue(failed);self.assertEqual(len(c.commands),1);self.assertEqual(len(j['operations']),8);self.assertFalse(report['native_decode_completed'])

    def test_exact_provider_hash_and_partial_custody_no_retry(self):
        raw=b'Exact raw provider bytes';t=plan([raw,raw,raw])[0];t['provider_asserted_sha256']='0'*64
        c=Client([raw,raw,raw]);j=prior();j['field_phase_body_bytes']=0
        with tempfile.TemporaryDirectory() as temp,patch.object(source.signal,'setitimer'):
            folder=Path(temp)
            with self.assertRaises(ValueError):source.acquire(c,folder,j,t,time.monotonic()+158)
            self.assertEqual((folder/'readme.raw').read_bytes(),raw)
            with self.assertRaises(ValueError):source.acquire(c,folder,j,t,time.monotonic()+158)
            self.assertEqual(len(c.commands),1)

    def test_body_reservation_and_budget_denial_precede_source_call(self):
        j=prior();j['field_phase_body_bytes']=1699999
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):source.reserve(j,Path(temp),'new','RETR','/new',1)
            self.assertEqual(len(j['operations']),6)

if __name__=='__main__':unittest.main()
