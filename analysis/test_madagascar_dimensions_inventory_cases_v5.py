import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import madagascar_dimensions_inventory_cases_v5 as cases
import check_madagascar_dimensions_delivery_v5 as controller
import satellite_core_width_cases_v1 as satellite
import wicc_review_width_cases_v1 as wicc
import eacc_cited_width_cases_v1 as eacc
import wicc_winter_reference_cases_v1 as routes

class InventoryExpectation(unittest.TestCase):
    def test_exact_case_only_and_missing_duplicate_or_wrong_total_refused(self):
        width={'collection':'widths','limit':1};other={'collection':'objects','record_type':'named_current','limit':1}
        source_rows=[{'id':'preserved','metadata':{'keep':[1,2]}}]
        source_query={'collection':'sources','limit':100};original=[(width,176),(other,106),(source_query,source_rows)]
        before=copy.deepcopy(original);result=cases.adapt_legacy_cases(original)
        self.assertEqual(original,before);self.assertEqual(result[0],(width,177));self.assertEqual(result[1],original[1])
        self.assertIs(result[0][0],width);self.assertIs(result[2][1],source_rows)
        for wrong in [175,177,176.0,True]:
            with self.assertRaises(ValueError):cases.adapt_legacy_cases([(width,wrong)])
        with self.assertRaises(ValueError):cases.adapt_legacy_cases([(other,106)])
        with self.assertRaises(ValueError):cases.adapt_legacy_cases([(width,176),(width,176)])

    def test_complete_historical_adapter_chain_changes_only_declared_totals(self):
        width={'collection':'widths','limit':1};route={'collection':'reference_routes','limit':1}
        owner={'collection':'objects','record_type':'named_current','limit':1}
        unchanged=[{'id':'prior','value':42}];query={'collection':'sources','filters':[{'field':'id','op':'eq','value':'prior'}],'limit':100}
        original=[(width,172),(route,82),(owner,106),(query,unchanged)];before=copy.deepcopy(original)
        adapted=cases.adapt_legacy_cases(routes.adapt(eacc.adapt_legacy_cases(wicc.adapt_legacy_cases(satellite.adapt_legacy_cases(original)))))
        self.assertEqual(adapted,[(width,177),(route,83),(owner,106),(query,unchanged)])
        self.assertIs(adapted[-1][1],unchanged);self.assertEqual(original,before)

    def test_semantic_failure_saves_exact_request_expectation_and_response(self):
        request={'collection':'widths','limit':1};response={'ok':True,'total':176,'rows':[{'id':'prior'}]}
        with tempfile.TemporaryDirectory() as folder,patch.object(controller,'OUT',Path(folder)):
            with self.assertRaises(ValueError):controller.verify_legacy_response(request,177,response)
            saved=json.loads((Path(folder)/'semantic-failure.json').read_bytes())
            self.assertEqual(saved['request'],request);self.assertEqual(saved['expected'],177);self.assertEqual(saved['response'],response)
            self.assertFalse(saved['installed'])
        with tempfile.TemporaryDirectory() as folder,patch.object(controller,'OUT',Path(folder)):
            controller.verify_legacy_response(request,177,{**response,'total':177})
            self.assertEqual(list(Path(folder).iterdir()),[])

if __name__=='__main__':unittest.main()
