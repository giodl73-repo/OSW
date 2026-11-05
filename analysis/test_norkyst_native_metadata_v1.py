import io
import unittest
import discover_norkyst_native_metadata_v1 as m


class NativeMetadata(unittest.TestCase):
    def test_only_same_provider_observed_catalogue_refs(self):
        raw=b'<catalog xmlns:xlink="http://www.w3.org/1999/xlink"><catalogRef name="native" xlink:href="native/catalog.xml"/><catalogRef name="bad" xlink:href="https://example.com/catalog.xml"/><dataset name="data" urlPath="romshindcast/norkyst_v3/native/norkyst20240315.nc"/><service name="odap" serviceType="OPENDAP" base="/thredds/dodsC/"/></catalog>'
        result=m.catalogue(raw,m.CATALOG)
        self.assertEqual(len(result['references']),1)
        self.assertEqual(result['opendap_services'][0]['base'],'https://thredds.met.no/thredds/dodsC/')

    def test_no_fixed_depth_or_wrong_year_month(self):
        for name,path in [('zdepth','zdepth/catalog.xml'),('2023','native/2023/catalog.xml'),('02','native/2024/02/catalog.xml')]:
            self.assertIsNone(m.priority({'name':name,'url':m.CATALOG.rsplit('/',1)[0]+'/'+path},1))
        self.assertIsNotNone(m.priority({'name':'native','url':m.CATALOG.rsplit('/',1)[0]+'/native/catalog.xml'},0))

    def test_never_request_field_or_guessed_external_endpoints(self):
        for url in ['https://thredds.met.no/file.nc','https://thredds.met.no/file.nc.ascii?u','https://example.com/catalog.xml']:
            with self.assertRaises(ValueError): m.read_metadata(url,{},lambda *a,**k:self.fail('No network call'))

    def test_transport_failure_is_one_attempt(self):
        calls=[]
        def fail(*a,**k): calls.append(1); raise TimeoutError('synthetic')
        receipt={}
        with self.assertRaises(TimeoutError): m.read_metadata(m.CATALOG,receipt,fail)
        self.assertEqual(calls,[1]); self.assertEqual(receipt['status'],'failed_no_retry')

    def test_metadata_byte_cap(self):
        class Response(io.BytesIO):
            status=200; url=m.CATALOG; headers={}
        receipt={}
        with self.assertRaises(ValueError): m.read_metadata(m.CATALOG,receipt,lambda *a,**k:Response(b'0'*250001))
        self.assertEqual(receipt['bytes_received'],250001)


if __name__=='__main__': unittest.main()
