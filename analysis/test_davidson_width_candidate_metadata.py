"""Small delivery fixtures; no original, full packet/index, build or browser."""
import copy
import json
import unittest
from pathlib import Path

import davidson_wallace_width_admission as admission
import davidson_width_candidate_metadata as candidate
from test_davidson_wallace_width_admission import baseline


def fixture(document):
    rows = baseline(document)
    rows['objects'][1]['type'] = 'named_current'
    dashboard = {'schema':'osw.motion-dashboard.v1', 'fingerprint_version':2,
                 'entries':copy.deepcopy(rows['objects']), 'counts':{'named_current':2},
                 'snapshot_fingerprint':candidate.fingerprint(rows['objects']),
                 'built_at_utc':'2026-10-24T00:00:00Z',
                 'candidate_delivery':{'version':candidate.PARENT_VERSION,'published':False}}
    raw = candidate.encoded(dashboard)
    manifest = {'current_gap_admission_version':candidate.PARENT_VERSION,
                'input_sha256':{candidate.DASHBOARD:candidate.digest(raw)},
                'dashboard_receipt':{'source_file':candidate.DASHBOARD,
                                     'source_sha256':candidate.digest(raw),
                                     'source_json':raw.decode('utf-8')},
                'taxonomy':{'node_count':2}, 'historical_receipt':{'sentinel':'unchanged'}}
    return manifest, rows, raw


def installed():
    return {'schema':'osw.current-gap-installed-delivery.v1',
            'status':'verified_cloud_delivery', 'cohort_version':candidate.PARENT_VERSION,
            'packet_logical_sha256':candidate.PARENT_SHA,
            'native_verified':True, 'browser_verified':True, 'working_dataset_delivery_verified':True,
            'candidate':{'logical_sha256':candidate.PARENT_SHA,'logical_bytes':candidate.PARENT_BYTES,
                         'objects':246,'rows':108524,'named_currents':106}}


class CandidateChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = admission.build_contract()
        raw = (Path(__file__).resolve().parents[1] / candidate.PARENT_PACKET).read_bytes()
        assert candidate.digest(raw) == candidate.PARENT_PACKET_SHA
        cls.packet = json.loads(raw)

    def prepare(self, manifest, rows, raw):
        return candidate.prepare(manifest, rows, raw, self.document,
                                 prepared_at_utc='2026-10-24T04:00:00Z')

    def test_exact_installed_parent_and_no_future_or_unverified_packet(self):
        candidate.validate_parent(self.packet, installed())
        for field in ['native_verified','browser_verified','working_dataset_delivery_verified']:
            proof = installed(); proof[field] = False
            with self.subTest(field=field), self.assertRaises(ValueError):
                candidate.validate_parent(self.packet, proof)
        for change in [{'logical_sha256':'a'*64}, {'logical_byte_length':123}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                candidate.validate_parent({**self.packet, **change}, installed())
        proof = installed(); proof['candidate']['named_currents'] = 107
        with self.assertRaises(ValueError):candidate.validate_parent(self.packet, proof)

    def test_coherent_append_and_owner_projection_without_input_mutation(self):
        manifest, rows, raw = fixture(self.document)
        before = copy.deepcopy((manifest,rows,raw))
        metadata, staged, dashboard_raw, receipt = self.prepare(manifest, rows, raw)
        self.assertEqual((manifest,rows,raw),before)
        self.assertEqual(metadata['historical_receipt'],manifest['historical_receipt'])
        self.assertEqual(metadata['current_gap_admission_version'],candidate.PARENT_VERSION)
        self.assertEqual(metadata[admission.VERSION_KEY],admission.VERSION)
        dashboard = json.loads(dashboard_raw)
        self.assertEqual(dashboard['entries'],staged['objects'])
        self.assertEqual(dashboard['counts'],{'named_current':2})
        self.assertEqual(dashboard['parent_candidate_delivery'],json.loads(raw)['candidate_delivery'])
        self.assertEqual(dashboard['built_at_utc'],'2026-10-24T04:00:00Z')
        self.assertEqual(metadata['dashboard_receipt']['source_sha256'],candidate.digest(dashboard_raw))
        self.assertEqual(metadata['dashboard_receipt']['source_json'],dashboard_raw.decode('utf-8'))
        self.assertEqual(metadata['input_sha256'][candidate.DASHBOARD],candidate.digest(dashboard_raw))
        self.assertEqual(receipt['preservation']['unchanged_objects_verified'],1)
        self.assertEqual(receipt['raw_samples_added'],0)
        self.assertEqual(receipt['annual_ranges_added'],0)
        self.assertFalse(metadata['davidson_candidate_delivery']['scientific_release_published'])

    def test_changed_dashboard_and_owner_projection_rejected(self):
        for changed in ['bytes','fingerprint','counts','entries']:
            manifest, rows, raw = fixture(self.document)
            dashboard = json.loads(raw)
            if changed == 'bytes': raw += b' '
            else:
                dashboard[changed if changed != 'fingerprint' else 'snapshot_fingerprint'] = []
                raw = candidate.encoded(dashboard)
                manifest['dashboard_receipt'].update(source_sha256=candidate.digest(raw),source_json=raw.decode())
                manifest['input_sha256'][candidate.DASHBOARD] = candidate.digest(raw)
            with self.subTest(changed=changed), self.assertRaises(ValueError):self.prepare(manifest,rows,raw)

    def test_no_reapplication_changed_parent_or_observation_time_inference(self):
        manifest, rows, raw = fixture(self.document)
        for change in [{admission.VERSION_KEY:admission.VERSION}, {'current_gap_admission_version':'future'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.prepare({**manifest, **change}, rows, raw)
        with self.assertRaises(ValueError):
            candidate.prepare(manifest,rows,raw,self.document,prepared_at_utc=None)

    def test_preservation_guard_rejects_erasure_reordering_and_physical_changes(self):
        manifest, rows, raw = fixture(self.document)
        _, stage, _, receipt = self.prepare(manifest,rows,raw)
        mutations = [
            lambda s:s['widths'].pop(0),
            lambda s:s['objects'].reverse(),
            lambda s:s['objects'][1].update(fingerprint='unrelated change'),
            lambda s:s['objects'][0].update(latest_observation_date='2008-01-30'),
            lambda s:s['objects'][0]['capabilities'].update(width_samples=4),
            lambda s:s['objects'][0]['width_ids'].pop(0),
            lambda s:s.update(new_unexpected_collection=[]),
        ]
        for index, mutate in enumerate(mutations):
            changed = copy.deepcopy(stage); mutate(changed)
            with self.subTest(index=index), self.assertRaises(ValueError):
                candidate.verify_preservation(rows,changed,receipt)


if __name__ == '__main__':unittest.main()
