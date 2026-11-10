import copy
import unittest
import pacific_nec_nominal_width_cases_v1 as m


class QuerySemantics(unittest.TestCase):
    def cases(self):
        c=m.query.build_contract()
        return m.main_cases({'widths':[c['width_record']],'objects':[c['final_owner']],'sources':c['new_sources'],'reference_routes':[]})

    def response(self,request,expected):
        sort=request.get('sort',{'field':'id','direction':'asc'});ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc');offset=request.get('offset',0)
        return {'ok':True,'total':len(expected),'rows':ordered[offset:offset+request['limit']],
            'chart_scene':m.runtime.width_scene(ordered) if request['collection']=='widths' else None,'map_scene':None}

    def test_exact20_semantic_cases(self):
        cases=self.cases();self.assertEqual(len(cases),20)
        for request,expected in cases:m.verify(request,expected,self.response(request,expected))

    def test_pagination_does_not_remove_matching_scene(self):
        request,expected=next((r,e) for r,e in self.cases() if r.get('offset')==1 and r['collection']=='widths')
        response=self.response(request,expected);self.assertEqual(response['rows'],[]);self.assertEqual(len(response['chart_scene']['width_records']),1)
        bad=copy.deepcopy(response);bad['chart_scene']=None
        with self.assertRaises(ValueError):m.verify(request,expected,bad)

    def test_false_annual_range_scene_extra_row_or_map_is_refused(self):
        request,expected=self.cases()[0]
        for mutation in ['row','total','scope','map']:
            response=self.response(request,expected)
            if mutation=='row':response['rows']=[]
            elif mutation=='total':response['total']=2
            elif mutation=='scope':response['chart_scene']['width_records'][0]['annual_width_range_km']=[900,1100]
            else:response['map_scene']={'features':[{}]}
            with self.assertRaises(ValueError,msg=mutation):m.verify(request,expected,response)

    def test_exact_one178_to179_inventory_migration(self):
        request={'collection':'widths','limit':1};other=({'collection':'objects','limit':1},111)
        self.assertEqual(m.adapt_legacy_cases([(request,178),other]),[(request,179),other])
        for cases in [[],[(request,177)],[(request,178),(request,178)]]:
            with self.assertRaises(ValueError):m.adapt_legacy_cases(cases)


if __name__=='__main__':unittest.main()
