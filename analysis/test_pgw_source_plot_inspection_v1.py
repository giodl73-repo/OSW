import copy,hashlib,io,unittest
import inspect_pgw_source_plot_v1 as p


class Response(io.BytesIO):
    status=200
    url='https://archimer.ifremer.fr/doc/00000/390/83.pdf'
    def __init__(self,raw):super().__init__(raw);self.headers={'Content-Length':str(len(raw))}


class InspectionTests(unittest.TestCase):
    def fixture(self):
        raw=b'%PDF-synthetic-only';op={'source_url':Response.url,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'maximum_http_requests':1,'maximum_response_body_bytes':18000000,'request_timeout_seconds':25,'maximum_drawings':100,'maximum_primitives':1000,'maximum_words':100}
        return raw,op
    def test_exact_bounded_document_receipt_no_retries(self):
        raw,op=self.fixture();receipt={};calls=[]
        def opener(request,timeout):calls.append(timeout);return Response(raw)
        self.assertEqual(p.read_original(op,receipt,opener),raw);self.assertEqual(calls,[25]);self.assertEqual(receipt['status'],'success');self.assertEqual(receipt['response_body_bytes'],len(raw));self.assertEqual(receipt['automatic_retries'],0)
    def test_changed_original_hash_length_or_signature_rejected(self):
        raw,op=self.fixture()
        for changed in [raw+b'x',raw.replace(b'PDF',b'BAD'),b'not_a_pdf']:
            with self.assertRaises(ValueError):p.validate_original(changed,op)
    def test_wrong_status_encoding_declared_length_or_source_rejected_before_body(self):
        raw,op=self.fixture()
        for kind in ['status','encoding','length','url']:
            response=Response(raw)
            if kind=='status':response.status=206
            if kind=='encoding':response.headers['Content-Encoding']='gzip'
            if kind=='length':response.headers['Content-Length']='999999999'
            if kind=='url':response.url='https://other.example/paper.pdf'
            receipt={}
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.read_original(op,receipt,lambda *a,**k:response)
            self.assertEqual(receipt['response_body_bytes'],0);self.assertEqual(receipt['status'],'failed_no_retry')
    def test_unknown_length_still_bounded_and_hash_verified(self):
        raw,op=self.fixture();response=Response(raw);response.headers={};receipt={}
        self.assertEqual(p.read_original(op,receipt,lambda *a,**k:response),raw)
        response=Response(raw+b'excess');response.headers={};receipt={};bad={**op,'maximum_response_body_bytes':len(raw)}
        with self.assertRaises(ValueError):p.read_original(bad,receipt,lambda *a,**k:response)
        self.assertEqual(receipt['response_body_bytes'],len(raw)+1)
    def test_page_inspection_exports_only_bounded_metadata_not_curve_vertices(self):
        raw,op=self.fixture()
        class Page:
            rect=[0.,0.,600.,800.]
            def get_drawings(self):return [{'items':[('l','private_start','private_end')],'rect':[10.,20.,30.,40.],'type':'s','dashes':'[] 0','width':.5}]
            def get_text(self,kind):return [(1.,2.,3.,4.,"'Hpgw'"),(2.,3.,4.,5.,'100'),(1.,2.,3.,4.,'unrelated_article_text')]
            def get_images(self):return []
        result=p.inspect_page(Page(),op);self.assertEqual(result['drawing_count'],1);self.assertEqual([r['text'] for r in result['selected_axis_and_legend_labels']],['Hpgw','100']);self.assertNotIn('private_start',str(result));self.assertFalse(result['curve_vertices_exported']);self.assertEqual(result['new_measurement_values_extracted'],0)
        with self.assertRaises(ValueError):p.inspect_page(Page(),{**op,'maximum_primitives':0})
    def test_neuc_screen_keeps_original_rejected_maxima_without_weaker_replacement(self):
        sections=[]
        for inside in [False,False,False,True]:sections.append({'diagnostic':{'selected_column_index':47,'horizontal_interior_selection':True,'selected_node_in_independent_latitude_context':inside,'primary_layer_detached_from_surface':True,'selected_column_threshold_layers':[{'threshold_m_s':.02,'lower_depth_m':900.}]}})
        result=p.screen_neuc(sections);self.assertEqual([r['regional_axis_proxy_anchor_eligible'] for r in result['source_section_screen']],[False,False,False,True]);self.assertEqual(result['adjacent_eligible_anchor_pairs'],0);self.assertFalse(result['weaker_replacement_selected']);self.assertFalse(result['new_route_created'])


if __name__=='__main__':unittest.main()
