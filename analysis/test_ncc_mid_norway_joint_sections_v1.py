import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
import acquire_ncc_mid_norway_joint_sections_v1 as p
from test_ncc_north_joint_sections_v1 import Dataset,Variable


class MidNorwayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def make(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);return p.JournalReads(120,Path(tmp.name)/'transport-ledger.json',lambda _:None)
    def datasets(self):
        uv,ts=Dataset(),Dataset()
        for ds in [uv,ts]:ds['lat'].data=np.asarray([62.98,63.02,63.74,63.78]);ds['lon'].data=np.arange(4.5,11.6,.08)
        return uv,ts
    def test_new_declared_gates_and_frozen_rules(self):
        self.assertEqual(self.op['sections'],p.SECTIONS);self.assertEqual([s['latitude_degrees_north'] for s in p.SECTIONS],[63,63.75]);self.assertTrue({s['id'] for s in p.SECTIONS}.isdisjoint(s['id'] for s in p.frozen.SECTIONS))
        with p.configured():p.frozen.validate_operator(self.op)
        self.assertEqual(self.op['practical_salinity_exclusive_upper_threshold'],35);self.assertEqual(self.op['selection_depth_interval_m'],[0,100]);self.assertFalse(any(self.op['eligibility'].values()))
    def test_scoped_configuration_restores_old_collector_after_success_and_error(self):
        old=(p.frozen.OPERATOR,p.frozen.SECTIONS,p.frozen.JointReads)
        for fail in [False,True]:
            try:
                with p.configured():
                    self.assertEqual(p.frozen.OPERATOR,p.OPERATOR);self.assertIs(p.frozen.JointReads,p.JournalReads)
                    if fail:raise RuntimeError('deliberate')
            except RuntimeError:pass
            self.assertEqual((p.frozen.OPERATOR,p.frozen.SECTIONS,p.frozen.JointReads),old)
    def test_success_saved_exactly_before_next_field_without_extra_read(self):
        r=self.make();v=Variable('water_u');a=r.read(v,0,0,0,2);files=list(r.journal.glob('*.json'));self.assertEqual(len(files),1);record=json.loads(files[0].read_bytes());self.assertEqual(record['native_flat_depth_major_values'],p.frozen.clean(a.ravel()));self.assertEqual(record['native_shape'],[40,3]);self.assertEqual(len(v.calls),1);self.assertFalse(record['wire_hash_claimed'])
        intent=json.loads((r.path.parent/'inflight-read.json').read_bytes());self.assertEqual(intent['status'],'SUCCESSFUL_NATIVE_VALUES_JOURNALED');self.assertEqual(intent['journal_sha256'],p.frozen.digest(files[0].read_bytes()))
    def test_failed_read_keeps_prior_success_journal_and_pending_intent(self):
        r=self.make();r.read(Variable('water_u'),0,0,0,2);bad=Variable('water_v',failures=[RuntimeError('permission denied')])
        with self.assertRaises(RuntimeError):r.read(bad,0,0,0,2)
        self.assertEqual(len(list(r.journal.glob('*.json'))),1);self.assertEqual(len(bad.calls),1);intent=json.loads((r.path.parent/'inflight-read.json').read_bytes());self.assertEqual(intent['variable'],'water_v');self.assertEqual(intent['status'],'ENTERING_VALIDATED_READER_NOT_A_SUCCESS_CLAIM');self.assertEqual(r.returned,120)
    def test_successful_archive_never_overwritten_or_replayed(self):
        r=self.make();v=Variable('salinity');r.read(v,0,0,0,2);file=next(r.journal.glob('*.json'));before=file.read_bytes()
        with self.assertRaises(ValueError):r.read(v,0,0,0,2)
        self.assertEqual(file.read_bytes(),before);self.assertEqual(len(v.calls),1)
    def test_journal_preserves_missing_values_without_zero_fill(self):
        r=self.make();v=Variable('salinity',np.ma.array(np.full((1,40,1,3),34.),mask=True));r.read(v,0,0,0,2);record=json.loads(next(r.journal.glob('*.json')).read_bytes());self.assertEqual(record['native_flat_depth_major_values'],[None]*120)
    def test_invalid_field_never_enters_reader_or_journal(self):
        r=self.make();v=Variable('temperature')
        with self.assertRaises(ValueError):r.read(v,0,0,0,2)
        self.assertEqual(v.calls,[]);self.assertEqual(list(r.journal.glob('*.json')),[])
    def test_all8_new_cases24_success_journals_and_caps_end_to_end(self):
        uv,ts=self.datasets()
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);p.collect(out=out,factory=lambda url:uv if url==p.frozen.UV else ts);report=json.loads((out/'source-report.json').read_bytes());manifest=json.loads((out/'journal-manifest.json').read_bytes());self.assertEqual(len(report['records']),8);self.assertEqual(len(manifest['successful_patches']),24);self.assertEqual(report['operator_file'],p.OPERATOR);self.assertLess(sum(f.stat().st_size for f in out.rglob('*') if f.is_file()),2400000)
            for piece in manifest['successful_patches']:
                raw=(out/piece['file']).read_bytes();self.assertEqual(len(raw),piece['bytes']);self.assertEqual(p.frozen.digest(raw),piece['sha256']);patch=json.loads(raw)
                matches=[json.loads((out/v['file']).read_bytes()) for v in report['profiles'] if json.loads((out/v['file']).read_bytes())['source_time_index']==patch['time_index'] and json.loads((out/v['file']).read_bytes())['native_latitude_index']==patch['latitude_index']];self.assertEqual(len(matches),1);s=matches[0]
                if patch['variable']=='salinity':array=np.asarray(s['practical_salinity_columns'],dtype=float).T
                else:array=np.asarray([c['eastward_velocity_m_s' if patch['variable']=='water_u' else 'northward_velocity_m_s'] for c in s['columns']],dtype=float).T
                self.assertEqual(patch['native_flat_depth_major_values'],p.frozen.clean(array.ravel()))
            self.assertTrue(manifest['all_successful_field_reads_retained']);self.assertFalse(manifest['successful_field_reads_replayed']);self.assertEqual(manifest['last_field_intent_sha256'],p.frozen.digest((out/'inflight-read.json').read_bytes()));self.assertTrue(uv.closed and ts.closed)
    def test_partial_collection_upload_material_preserves_completed_field(self):
        uv,ts=self.datasets();uv['water_v'].failures=[RuntimeError('permission denied')]
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            with self.assertRaises(RuntimeError):p.collect(out=out,factory=lambda url:uv if url==p.frozen.UV else ts)
            self.assertEqual(len(list((out/'field-journal').glob('*.json'))),1);ledger=json.loads((out/'transport-ledger.json').read_bytes());self.assertEqual([v['status'] for v in ledger['requests']],['success','non_transport_error_not_retried']);self.assertFalse((out/'source-report.json').exists());self.assertFalse((out/'journal-manifest.json').exists());self.assertTrue(uv.closed and ts.closed)
    def test_public_pins_and_unchanged_underlying_numerics(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.frozen.digest((p.ROOT/file).read_bytes()),pin,file)
        self.assertTrue(issubclass(p.JournalReads,p.BASE_READS));self.assertEqual(self.op['maximum_total_cell_pairs'],250000);self.assertEqual(self.op['maximum_total_decoded_velocity_bytes'],7000000)


if __name__=='__main__':unittest.main()
