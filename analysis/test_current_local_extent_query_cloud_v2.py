"""Apply the existing tiny gate fixtures to the versioned small-target gate."""
from unittest.mock import patch
import unittest

import check_current_local_extent_query_cloud_v2 as small_gate
import test_current_local_extent_query_cloud_v1 as controls


class SmallTargetCloudGateTests(controls.QueryCloudGateTests):
    def commit(self):
        # Fixtures change only these three control documents after setup.
        # Keep the original source snapshots fixed instead of rereading them.
        first=not self.snapshots
        self.write(small_gate.PREFLIGHT,self.encode(self.pref))
        self.request['preflight_sha256']=small_gate.digest((self.root/small_gate.PREFLIGHT).read_bytes())
        self.write(small_gate.REQUEST,self.encode(self.request))
        self.write(small_gate.PHASE,self.encode(self.phase))
        names=([p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()]
            if first else [small_gate.PREFLIGHT,small_gate.REQUEST,small_gate.PHASE])
        for name in names:self.snapshots[name]=(self.root/name).read_bytes()

    def setUp(self):
        patcher=patch.object(controls,'gate',small_gate)
        patcher.start();self.addCleanup(patcher.stop)
        super().setUp()
        self.pref.update(schema='osw.current-local-extent-query-check-preflight.v2',
            max_dedicated_wasm_bytes=2097152,max_dedicated_memory_bytes=67108864,
            baseline_run_id=40131603572,baseline_artifact_id=12574929493)
        self.request['schema']='osw.current-local-extent-query-check-request.v2'
        self.commit()

    def test_delivery_budget_and_baseline_cannot_be_changed(self):
        for key,value in (('max_dedicated_wasm_bytes',59201757),
            ('max_dedicated_memory_bytes',134217728),('baseline_run_id',123),('baseline_artifact_id',123)):
            before=self.pref[key];self.pref[key]=value;self.commit()
            with self.subTest(key=key),self.assertRaises(ValueError):small_gate.verify(self.root,self.env)
            self.pref[key]=before;self.commit()


if __name__=='__main__':unittest.main()
