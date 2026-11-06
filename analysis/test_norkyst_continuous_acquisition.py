"""A year extension must preserve the two-month originals and avoid redundant I/O."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

import numpy as np

import fetch_norkyst_ingoy_continuous as fetch


class ContinuousAcquisitionTests(unittest.TestCase):
    def test_conflicting_original_or_daily_metadata_pins_reject(self):
        row={'key':'20240629_12-23','date':'2024-06-29','field_sha256':'field','metadata_sha256':'meta'}
        self.assertEqual(fetch.retained_responses([row],[row]),{row['key']:row})
        for changed in [{**row,'field_sha256':'different'},
                        {**row,'key':'20240629_00-23','metadata_sha256':'different'}]:
            with self.subTest(changed=changed),self.assertRaises(ValueError):fetch.retained_responses([row],[changed])

    def test_existing_archive_keeps_exact_container_bytes_and_rejects_mutations(self):
        with TemporaryDirectory() as temporary:
            folder=Path(temporary);path=folder/'originals.zip';members={'test.ascii':b'original source'}
            with patch.object(fetch,'ROOT',folder):
                receipt=fetch.archive(path,members);before=path.read_bytes()
                with patch.object(zipfile.ZipFile,'writestr',side_effect=AssertionError('Retained archive must not be rewritten')):
                    self.assertEqual(fetch.archive(path,members,receipt['sha256']),receipt)
                self.assertEqual(path.read_bytes(),before)
                with self.assertRaises(ValueError):fetch.archive(path,{'test.ascii':b'different'},receipt['sha256'])
                path.write_bytes(before+b'changed container')
                with self.assertRaises(ValueError):fetch.archive(path,members,receipt['sha256'])

    def test_retained_originals_hydrate_without_network_and_reject_corrupt_cache(self):
        with TemporaryDirectory() as temporary:
            folder=Path(temporary);cache=folder/'cache';cache.mkdir()
            with patch.object(fetch,'ROOT',folder),patch.object(fetch,'CACHE',cache):
                receipt=fetch.archive(folder/'originals.zip',{'original.ascii':b'original'})
                with patch.object(fetch,'urlopen',side_effect=AssertionError('No source refresh during hydration')):
                    fetch.hydrate_originals({'archives':[receipt]})
                self.assertEqual((cache/'original.ascii').read_bytes(),b'original')
                (cache/'original.ascii').write_bytes(b'changed')
                with self.assertRaises(ValueError):fetch.hydrate_originals({'archives':[receipt]})

    def test_new_hour_interval_reuses_daily_metadata_pin_without_rebinding_old_field_pin(self):
        row={'key':'20240629_12-23','date':'2024-06-29','field_sha256':'old interval field pin',
             'metadata_sha256':'known daily metadata pin','metadata_retrieved_utc':'2026-10-18T00:00:00+00:00'}
        calls=[]
        def retrieve(url,path,pin=None):
            calls.append((url,pin));return (b'metadata' if url.endswith('.das') else b'new interval'),'2026-10-18T01:00:00+00:00'
        arrays={name:np.zeros((24,48,50),dtype=np.int16) for name in fetch.source.VARIABLES}
        arrays['sea_mask']=np.ones((48,50),dtype=np.int16)
        with patch.object(fetch,'retrieve',retrieve),patch.object(fetch.source,'metadata',return_value={}),\
             patch.object(fetch.source,'parse_fields',return_value=(list(range(24)),arrays)):
            result=fetch.day_job(('2024-06-29',0,23),{row['key']:row})
        self.assertEqual(calls[0][1],'known daily metadata pin')
        self.assertIsNone(calls[1][1])
        self.assertEqual(result['metadata_retrieved_utc'],row['metadata_retrieved_utc'])
        self.assertEqual(result['complete_wet_paired_positions'],24*48*50)


if __name__=='__main__':unittest.main()
