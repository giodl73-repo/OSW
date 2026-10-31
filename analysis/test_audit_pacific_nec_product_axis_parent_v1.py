import unittest
from unittest.mock import patch
import audit_pacific_nec_product_axis_parent_v1 as audit


class ParentAudit(unittest.TestCase):
    def test_local_refusal_precedes_installed_file_reads(self):
        with patch.dict(audit.os.environ,{},clear=True),patch.object(audit,'read',side_effect=AssertionError('No reads')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):audit.guard()

    def test_source_aliases_and_doi_citations_are_retained_without_automatic_merge(self):
        rows=[{'id':'a','url':'https://oceanwatch.pifsc.noaa.gov/erddap/info/yearly_336c_0b32_9cd3/index.html'},
              {'id':'b','url':'https://oceanwatch.pifsc.noaa.gov/erddap/info/yearly_336c_0b32_9cd3/index.json'},
              {'id':'c','doi':'https://doi.org/10.1029/2019JC015895'},
              {'id':'d','label':'OSCAR different version, unresolved'}]
        found=audit.publications(rows)
        self.assertEqual(found['resolutions']['exact_oscar_mirror_dataset']['status'],'RECONCILIATION_REQUIRED')
        self.assertEqual(found['resolutions']['liu_zhou_2020_context']['source_ids'],['c'])
        self.assertEqual(found['possible_oscar_aliases'],[rows[3]])
        self.assertEqual(rows[0]['id'],'a')


if __name__=='__main__':unittest.main()
