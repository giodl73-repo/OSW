"""Bound ordinary reads of already compiled catalog descriptors, not acquisition."""
import contextlib,copy,hashlib,json,re

STRINGS=re.compile(rb'"(?:[^"\\]|\\.)*"')
NUMBERS=re.compile(rb'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')

def numeric_tokens(raw):
    return len(NUMBERS.findall(STRINGS.sub(b'""',raw)))

class DescriptorQuery:
    def __init__(self,save,numeric_cap=250000,byte_cap=32000000,prior_numeric=23444,prior_bytes=6635876):
        self.save=save;self.numeric_cap=numeric_cap;self.byte_cap=byte_cap;self.cache={}
        self.ledger={'schema':'osw.compiled-depth-descriptor-query-ledger.v3',
            'scope':'already_compiled_derived_catalog_query_not_native_acquisition_or_case_budget_renewal',
            'numeric_token_cap':numeric_cap,'unique_json_byte_cap':byte_cap,
            'maximum_json_packet_bytes':2500000,'reserved_numeric_tokens':prior_numeric,'unique_json_bytes':prior_bytes,'new_numeric_tokens':0,'new_json_bytes':0,
            'prior_failed_numeric_upper_bound':prior_numeric,'prior_failed_json_byte_upper_bound':prior_bytes,
            'cache_hits':0,'packets':[],'new_native_values_decoded':0,'provider_requests':0,
            'json_byte_accounting':'prior_failed_upper_bound_plus_new_unique_bytes'}
        self.save(self.ledger)

    def reader(self,read):
        def get(path):
            if path.startswith('research/source-data/') or not path.endswith(('.json','.csv')):raise ValueError('Compiled JSON/CSV only; no native/archives/field files')
            return read(path)
        return get

    @contextlib.contextmanager
    def decoding(self):
        original=json.loads
        def loads(raw,*args,**kwargs):
            if args or kwargs:raise ValueError('Plain compiled JSON decoding only')
            blob=raw.encode('utf8') if isinstance(raw,str) else bytes(raw)
            key=hashlib.sha256(blob).hexdigest()
            if key in self.cache:
                self.ledger['cache_hits']+=1
                return copy.deepcopy(self.cache[key])
            tokens=numeric_tokens(blob)
            if len(blob)>2500000 or self.ledger['reserved_numeric_tokens']+tokens>self.numeric_cap or self.ledger['unique_json_bytes']+len(blob)>self.byte_cap:
                raise ValueError('Prospective descriptor query cap before JSON numeric decoding')
            self.ledger['reserved_numeric_tokens']+=tokens;self.ledger['unique_json_bytes']+=len(blob)
            self.ledger['new_numeric_tokens']+=tokens;self.ledger['new_json_bytes']+=len(blob)
            self.ledger['packets'].append({'sha256':key,'bytes':len(blob),'reserved_numeric_tokens':tokens,'status':'reserved_before_decode'})
            self.save(self.ledger)
            parsed=original(raw);self.cache[key]=copy.deepcopy(parsed)
            self.ledger['packets'][-1]['status']='decoded_and_cached'
            return parsed
        json.loads=loads
        try:yield
        finally:json.loads=original;self.save(self.ledger)
