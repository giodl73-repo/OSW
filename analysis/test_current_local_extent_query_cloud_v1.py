"""Tiny fictional cloud controls; no compiler, original data or provider."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_current_local_extent_query_cloud_v1 as gate


class QueryCloudGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        def write(name,raw):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        self.write=write
        for name in gate.INPUTS:write(name,b'{}\n')
        original={f'executed/{i}.txt':gate.digest(b'original\n') for i in range(83)}
        for name in original:write(name,b'original\n')
        write(gate.EXECUTED,self.encode({'input_sha256':original}))
        self.pref={'schema':'osw.current-local-extent-query-check-preflight.v1','reviewed_parent':gate.PARENT,
            'python_exact':'3.14.8','rust_toolchain':'1.95.0',
            'input_sha256':{name:gate.digest((self.root/name).read_bytes()) for name in gate.INPUTS}}
        self.request={'schema':'osw.current-local-extent-query-check-request.v1','execution_permitted':True,
            'build_verification_only':True,'provider_requests_permitted':False,
            'original_source_processing_permitted':False,'measurement_admission_permitted':False,
            'installed_assets_change_permitted':False,'max_heavy_local_jobs':0,'max_cloud_jobs':1,
            'workflow':gate.WORKFLOW,'preflight':gate.PREFLIGHT}
        self.phase={'phase':'source-review-only-v1','heavy_work_permitted':False,
            'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}
        self.snapshots={};self.changes=set(gate.ALLOWED_CHANGES)
        self.commit()
        self.env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'giodl73-repo/OSW',
            'GITHUB_REF':'refs/heads/codex/current-measurement-gaps','RUNNER_OS':'Linux',
            'GITHUB_WORKSPACE':str(self.root),'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1',
            **{key:'1' for key in ('CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS',
                'OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}
        def git(root,*args):
            if args==('rev-parse','HEAD'):return b'a'*40+b'\n'
            if args[0]=='status':return b''
            if args[0]=='show':return self.snapshots[args[1].removeprefix('HEAD:')]
            if args[0]=='merge-base':return b''
            if args[0]=='diff':return ('\n'.join(sorted(self.changes))+'\n').encode()
            raise AssertionError(args)
        for patcher in (patch.object(gate,'git',git),
            patch.object(gate.os,'sched_getaffinity',lambda _:{3},create=True),
            patch.object(gate.platform,'python_version',lambda:'3.14.8'),
            patch.object(gate,'EXECUTED_SHA',gate.digest((self.root/gate.EXECUTED).read_bytes())),
            patch.object(gate,'DATA_SHA',gate.digest((self.root/gate.DATA).read_bytes()))):
            patcher.start();self.addCleanup(patcher.stop)

    @staticmethod
    def encode(value):return (json.dumps(value,sort_keys=True)+'\n').encode()

    def commit(self):
        self.write(gate.PREFLIGHT,self.encode(self.pref))
        self.request['preflight_sha256']=gate.digest((self.root/gate.PREFLIGHT).read_bytes())
        self.write(gate.REQUEST,self.encode(self.request));self.write(gate.PHASE,self.encode(self.phase))
        for path in self.root.rglob('*'):
            if path.is_file():self.snapshots[path.relative_to(self.root).as_posix()]=path.read_bytes()

    def test_valid_fictional_gate_permits_only_build_verification(self):
        report=gate.verify(self.root,self.env)
        self.assertEqual(report['executed_inputs_unchanged'],83)
        self.assertFalse(report['complete_atlas_load_permitted'])
        self.assertFalse(report['source_processing_permitted'])
        self.assertFalse((self.root/'.pytest_cache').exists())

    def test_local_invocation_refused_before_any_file_read(self):
        with patch.object(gate,'read',side_effect=AssertionError('Local file read')):
            with self.assertRaisesRegex(ValueError,'cloud working branch'):gate.verify(self.root,{})

    def test_changed_context_or_resources_refused(self):
        for key,value in (('GITHUB_REF','refs/heads/main'),('RUNNER_OS','Windows'),
            ('GITHUB_SHA','b'*40),('GITHUB_RUN_ID','0'),('CARGO_BUILD_JOBS','2'),('OMP_NUM_THREADS','2')):
            with self.subTest(key=key),self.assertRaises(ValueError):gate.verify(self.root,{**self.env,key:value})
        with patch.object(gate.os,'sched_getaffinity',lambda _:{1,2}),self.assertRaises(ValueError):gate.verify(self.root,self.env)

    def test_source_acquisition_installation_or_parallel_scope_cannot_be_enabled(self):
        for target,key,value in ((self.request,'execution_permitted',False),
            (self.request,'provider_requests_permitted',True),(self.request,'original_source_processing_permitted',True),
            (self.request,'measurement_admission_permitted',True),(self.request,'installed_assets_change_permitted',True),
            (self.request,'max_cloud_jobs',2),(self.phase,'heavy_work_permitted',True)):
            before=target[key];target[key]=value;self.commit()
            with self.subTest(key=key),self.assertRaises(ValueError):gate.verify(self.root,self.env)
            target[key]=before;self.commit()

    def test_edited_source_and_executed_inputs_are_refused(self):
        for name in ('rust/osw-query/src/lib.rs','executed/0.txt'):
            path=self.root/name;before=path.read_bytes();path.write_bytes(b'changed')
            with self.subTest(name=name),self.assertRaises(ValueError):gate.verify(self.root,self.env)
            path.write_bytes(before)

    def test_unexpected_parent_asset_change_is_refused(self):
        self.changes.add('almanac/query-data.json')
        with self.assertRaisesRegex(ValueError,'parent corpus'):gate.verify(self.root,self.env)


if __name__=='__main__':unittest.main()
