import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import azcc_onken_cases_v1 as cases
import madagascar_dimensions_inventory_cases_v5 as madagascar
import check_azcc_onken_delivery_v1 as controller
import satellite_core_width_cases_v1 as satellite
import wicc_review_width_cases_v1 as wicc
import eacc_cited_width_cases_v1 as eacc
import wicc_winter_reference_cases_v1 as routes

class InventoryExpectation(unittest.TestCase):
    def test_exact_case_only_and_missing_duplicate_or_wrong_total_refused(self):
        width={'collection':'widths','limit':1};other={'collection':'objects','record_type':'named_current','limit':1}
        rows=[{'id':'preserved','metadata':{'keep':[1,2]}}];request={'collection':'sources','limit':100}
        original=[(width,177),(other,106),(request,rows)];before=copy.deepcopy(original)
        result=cases.adapt_legacy_cases(original);self.assertEqual(original,before)
        self.assertEqual(result[0],(width,178));self.assertEqual(result[1],original[1]);self.assertIs(result[2][1],rows)
        for wrong in [176,178,177.0,True]:
            with self.assertRaises(ValueError):cases.adapt_legacy_cases([(width,wrong)])
        with self.assertRaises(ValueError):cases.adapt_legacy_cases([(other,106)])
        with self.assertRaises(ValueError):cases.adapt_legacy_cases([(width,177),(width,177)])

    def test_complete_historical_adapter_chain_changes_only_declared_totals(self):
        width={'collection':'widths','limit':1};route={'collection':'reference_routes','limit':1}
        owner={'collection':'objects','record_type':'named_current','limit':1}
        unchanged=[{'id':'prior','value':42}];query={'collection':'sources','filters':[{'field':'id','op':'eq','value':'prior'}],'limit':100}
        original=[(width,172),(route,82),(owner,106),(query,unchanged)];before=copy.deepcopy(original)
        adapted=cases.adapt_legacy_cases(madagascar.adapt_legacy_cases(routes.adapt(eacc.adapt_legacy_cases(wicc.adapt_legacy_cases(satellite.adapt_legacy_cases(original))))))
        self.assertEqual(adapted,[(width,178),(route,83),(owner,106),(query,unchanged)])
        self.assertIs(adapted[-1][1],unchanged);self.assertEqual(original,before)

    def test_semantic_failure_saves_exact_request_expectation_and_response(self):
        request={'collection':'widths','limit':1};response={'ok':True,'total':177,'rows':[{'id':'prior'}]}
        with tempfile.TemporaryDirectory() as folder,patch.object(controller,'OUT',Path(folder)):
            with self.assertRaises(ValueError):controller.verify_legacy_response(request,178,response)
            saved=json.loads((Path(folder)/'semantic-failure.json').read_bytes())
            self.assertEqual(saved['request'],request);self.assertEqual(saved['expected'],178);self.assertEqual(saved['response'],response)
            self.assertFalse(saved['installed'])
        with tempfile.TemporaryDirectory() as folder,patch.object(controller,'OUT',Path(folder)):
            controller.verify_legacy_response(request,178,{**response,'total':178})
            self.assertEqual(list(Path(folder).iterdir()),[])

if __name__=='__main__':unittest.main()
