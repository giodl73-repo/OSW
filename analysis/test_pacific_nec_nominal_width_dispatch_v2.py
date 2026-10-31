import json
from pathlib import Path
import unittest
from unittest.mock import patch
import check_pacific_nec_nominal_width_delivery_v2 as delivery
import check_pacific_nec_nominal_width_browser_v1 as browser


class CloudDispatch(unittest.TestCase):
    def test_local_engine_and_browser_refuse_before_payload_or_process_access(self):
        for action in [delivery.controls, delivery.engine, delivery.browser]:
            with patch.dict(delivery.os.environ, {}, clear=True), \
                 patch.object(delivery, 'read', side_effect=AssertionError('File opened')), \
                 patch.object(delivery.subprocess, 'run', side_effect=AssertionError('Process launched')):
                with self.assertRaisesRegex(ValueError, 'Exact scoped cloud delivery required'):
                    action()

    def test_standalone_browser_refuses_before_playwright_or_file_access(self):
        with patch.dict(browser.os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'Exact scoped cloud browser required'):
                browser.browser_review(Path('unavailable'), Path('unavailable'))

    def test_request_does_not_permit_installation_or_field_processing(self):
        request=json.loads((delivery.ROOT/delivery.REQUEST).read_bytes())
        self.assertIs(type(request['execute']),bool)
        self.assertEqual(request['max_cloud_jobs'],1)
        self.assertEqual(request['max_heavy_local_jobs'],0)
        for key in ['installation_permitted','source_field_processing_permitted',
                    'main_merge_permitted','local_bulk_sync_permitted']:
            self.assertIs(request[key],False)


if __name__=='__main__':unittest.main()
