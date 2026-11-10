import copy
import unittest
import os
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import patch
import install_equatorial_basin_saved_v1 as m

class Installation(unittest.TestCase):
    def test_all_four_complete_parity_receipts(self):
        m.verify_parities()

    def test_changed_object_response_or_short_main_receipt_refused(self):
        original=m.read
        for name in ['main','object']:
            def changed(path):
                d=copy.deepcopy(original(path))
                if path.endswith(name+'-parity.json'):
                    if name=='main':d['checks'].pop()
                    else:d['checks'][0]['entire_response_equal']=False
                return d
            with patch.object(m,'read',side_effect=changed),self.assertRaises(AssertionError):m.verify_parities()

    def test_actual_workflow_selector_reads_actual_request(self):
        workflow=(m.ROOT/m.WORKFLOW).read_text()
        start=workflow.index("          python - <<'PY'\n")+len("          python - <<'PY'\n")
        program=textwrap.dedent(workflow[start:workflow.index('\n          PY',start)])
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'output'
            with patch.dict(os.environ,{'GITHUB_OUTPUT':str(output)}):exec(compile(program,m.WORKFLOW,'exec'),{})
            self.assertEqual(output.read_text(),'execute=true\n')

    def evidence(self):
        return [m.read(m.EVIDENCE+'engine.json'),m.read(m.BROWSER+'result.json'),m.read(m.REVIEW),m.read(m.BROWSER+'browser.json')]

    def test_exact_saved_engine_final_manifest_and_visual_review(self):
        hashes=m.verify_evidence(*self.evidence())
        self.assertEqual(len(hashes),18)
        self.assertEqual(hashes[m.delivery.MANIFEST],m.FINAL_MANIFEST)

    def test_changed_science_custody_browser_or_review_refused(self):
        for mutation in ['tests','binary','artifact','browser','source','manifest','review','clipping','observations','sections']:
            values=copy.deepcopy(self.evidence())
            if mutation=='tests':values[0]['rust_tests_passed']=0
            elif mutation=='binary':values[1]['generated_sha256'][m.delivery.WASM]='0'*64
            elif mutation=='artifact':values[1]['saved_artifact']['id']=0
            elif mutation=='browser':values[1]['browser_verified']=False
            elif mutation=='source':values[1]['browser_source_commit']='0'*40
            elif mutation=='manifest':values[1]['generated_sha256'][m.delivery.MANIFEST]='0'*64
            elif mutation=='review':values[2]['images']=[]
            elif mutation=='observations':values[0]['new_independent_observations']=5
            elif mutation=='sections':values[0]['new_identity_records']=6
            else:values[3]['captures'][0]['geometry']['clipped_axes']=['x']
            with self.assertRaises((AssertionError,ValueError),msg=mutation):m.verify_evidence(*values)

    def test_local_execution_refused_before_file_read(self):
        with patch.dict(m.os.environ,{},clear=True),patch.object(m,'read',side_effect=ValueError('early read')):
            with self.assertRaises(AssertionError):m.controls()

    def test_request_cannot_expand_to_build_or_main(self):
        request={'schema':'osw.equatorial-basin-installation-request.v1','workflow':m.WORKFLOW,
            'execution_permitted':True,'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
            'max_cloud_jobs':1,'max_heavy_local_jobs':0,**{k:False for k in ['native_build_permitted','wasm_build_permitted',
            'browser_automation_permitted','scientific_source_processing_permitted','source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']}}
        m.verify_request(request)
        for key in ['native_build_permitted','main_merge_permitted','local_bulk_sync_permitted']:
            changed=dict(request);changed[key]=True
            with self.assertRaises(AssertionError):m.verify_request(changed)

if __name__=='__main__':unittest.main()
