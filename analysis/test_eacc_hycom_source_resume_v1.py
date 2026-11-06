"""Small synthetic bodies and clocks only; no original data or network."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import io
import json

import pytest

import eacc_hycom_source_resume_v1 as resume
from eacc_hycom_cloud_acquisition_v2 import encoded, digest
from eacc_hycom_source_compilation_v1 import compile_source, pin
from test_eacc_hycom_source_compilation_v1 import source


@pytest.fixture
def basis(source, tmp_path):
    metadata, plan, responses = source
    directory = tmp_path / 'basis'; directory.mkdir(); (directory / 'responses').mkdir()
    # File bytes and canonical semantics deliberately have different endings.
    selection_raw = encoded(plan).replace(b'\n', b'\r\n')
    preflight = {'selection_sha256': digest(selection_raw), 'input_sha256': {}}
    preflight_raw = encoded(preflight)
    environment = {'source_commit': 'a'*40, 'run_id': 123, 'run_attempt': 2, 'scientific_input_sha256': {}}
    completed = [request['file'] for request in plan['requests'][:3]]
    failure = {'completed_files': completed, 'request': plan['requests'][3],
               'source_field_compilation_completed': False, 'error_type': 'TimeoutError'}
    case_failure = {'source_commit': 'a'*40, 'run_id': 123, 'new_current_widths_admitted': 0}
    files = {**metadata, 'selection.json': selection_raw, 'preflight.json': preflight_raw,
             'environment.json': encoded(environment), 'case-failure.json': encoded(case_failure),
             'responses/failure.json': encoded(failure)}
    reviewed = []
    for request in plan['requests'][:3]:
        name = request['file']; raw, receipt = responses[name]
        receipt_raw = encoded(receipt)
        files['responses/' + name] = raw
        files['responses/' + name + '.receipt.json'] = receipt_raw
        reviewed.append({'file': name, 'response': pin(raw), 'receipt_sha256': digest(receipt_raw)})
    for name, raw in files.items(): (directory / name).write_bytes(raw)
    review = {'source_responses': reviewed, 'preflight_sha256': digest(preflight_raw),
              'source_commit': 'a'*40, 'run_id': 123, 'run_attempt': 2,
              'failure': failure, 'case_failure': case_failure, 'source_compilation_completed': False}
    return directory, metadata, plan, responses, review


def clock():
    count = 0
    def now():
        nonlocal count
        value = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=1000 + count)
        count += 1
        return value
    return now


def fetcher(plan, responses, seen):
    by_url = {request['url']: responses[request['file']][0] for request in plan['requests']}
    def fetch(url, cap):
        seen.append(url)
        return {'raw': by_url[url], 'http_status': 200, 'content_type': 'text/plain', 'final_url': url}
    return fetch


def test_raw_selection_and_canonical_plan_hashes_are_distinct_and_both_validated(basis):
    directory, _, plan, _, review = basis
    assert digest((directory / 'selection.json').read_bytes()) != digest(encoded(plan))
    assert resume.verify_basis(directory, plan, review) == [request['file'] for request in plan['requests'][:3]]


def test_saved_prefix_is_reused_exactly_and_full_year_compiles_once(basis, tmp_path):
    directory, metadata, plan, responses, review = basis
    seen = []; output = tmp_path / 'continued'
    completed = resume.resume_responses(directory, output, plan, review,
        fetch=fetcher(plan, responses, seen), clock=clock())
    assert seen == [request['url'] for request in plan['requests'][3:]]
    assert completed == [request['file'] for request in plan['requests']]
    for request in plan['requests'][:3]:
        name = request['file']
        assert (output / 'responses' / name).read_bytes() == (directory / 'responses' / name).read_bytes()
        assert (output / 'responses' / (name+'.receipt.json')).read_bytes() == (directory / 'responses' / (name+'.receipt.json')).read_bytes()
    def load(name):
        return ((output / 'responses' / name).read_bytes(),
                json.loads((output / 'responses' / (name+'.receipt.json')).read_bytes()))
    fields = compile_source(metadata, plan, completed, load)
    assert len(fields['months']) == 12
    assert fields['months'][0]['sample_days'] == 27
    assert fields['months'][0]['paired_samples'] == [[25,24],[27,27]]
    assert fields['months'][0]['eastward_m_s'][0][1] is None
    lineage = json.loads((output / 'source-lineage.json').read_bytes())
    assert lineage['reused_requests'] == 3 and lineage['socket_timeout_seconds'] == 50
    assert not lineage['physical_method_changed']
    assert (directory / 'responses/failure.json').read_bytes() == encoded(review['failure'])


@pytest.mark.parametrize('change', ['body', 'receipt', 'metadata', 'selection_bytes', 'environment', 'inventory', 'failure'])
def test_corrupt_or_mixed_basis_fails_before_output_or_fetch(basis, tmp_path, change):
    directory, _, plan, _, review = basis
    name = plan['requests'][0]['file']
    targets = {'body': 'responses/'+name, 'receipt': 'responses/'+name+'.receipt.json',
               'metadata': 'metadata.das', 'selection_bytes': 'selection.json',
               'environment': 'environment.json', 'failure': 'responses/failure.json'}
    if change == 'inventory': (directory / 'unexpected.json').write_text('{}')
    elif change == 'environment':
        value=json.loads((directory/'environment.json').read_bytes());value['run_id']=999
        (directory/'environment.json').write_bytes(encoded(value))
    elif change == 'failure':
        value=deepcopy(review['failure']);value['completed_files'].reverse()
        (directory/'responses/failure.json').write_bytes(encoded(value))
    else:
        target=directory/targets[change];target.write_bytes(target.read_bytes()+b' ')
    with pytest.raises((ValueError, json.JSONDecodeError)):
        resume.resume_responses(directory, tmp_path/'bad', plan, review,
            fetch=lambda *_: pytest.fail('Unverified source must not fetch'))
    assert not (tmp_path/'bad').exists()


def test_compiled_case_cannot_be_sent_through_source_collection_again(basis, tmp_path):
    directory, _, plan, _, review = basis
    review = {**review, 'source_compilation_completed': True}
    with pytest.raises(ValueError, match='already compiled'):
        resume.resume_responses(directory, tmp_path/'bad', plan, review)


def test_continuation_output_cannot_modify_original_tree(basis):
    directory, _, plan, _, review = basis
    with pytest.raises(ValueError, match='separate'):
        resume.resume_responses(directory, directory/'new', plan, review)
    assert not (directory/'new').exists()


def test_known_metadata_byte_hash_is_not_replaced_by_semantic_equality(basis):
    directory, _, plan, _, review = basis
    review['local_transfer'] = {'selected_metadata_sha256': {'environment.json': digest((directory/'environment.json').read_bytes())}}
    (directory/'environment.json').write_bytes((directory/'environment.json').read_bytes()+b' ')
    with pytest.raises(ValueError, match='byte fingerprint'):
        resume.verify_basis(directory, plan, review)


def test_timeout_retains_prefix_and_never_retries_or_requests_later_slots(basis, tmp_path):
    directory, _, plan, responses, review = basis
    seen=[]; good=fetcher(plan,responses,seen)
    def fetch(url, cap):
        if len(seen)==1:
            seen.append(url)
            raise TimeoutError('synthetic source timeout')
        return good(url,cap)
    output=tmp_path/'partial-again'
    with pytest.raises(TimeoutError):
        resume.resume_responses(directory,output,plan,review,fetch=fetch,clock=clock())
    assert seen == [request['url'] for request in plan['requests'][3:5]]
    failure=json.loads((output/'responses/failure.json').read_bytes())
    assert failure['completed_files'] == [request['file'] for request in plan['requests'][:4]]
    assert failure['request']==plan['requests'][4] and not failure['automatic_retry']
    assert not (output/'responses'/plan['requests'][5]['file']).exists()


def test_clock_reversal_is_retained_as_failure_before_more_requests(basis, tmp_path):
    directory, _, plan, responses, review=basis;seen=[]
    with pytest.raises(ValueError, match='reverse time'):
        resume.resume_responses(directory,tmp_path/'bad-clock',plan,review,
            fetch=fetcher(plan,responses,seen),clock=lambda:datetime(2025,1,1,tzinfo=timezone.utc))
    assert len(seen)==1


def test_existing_output_is_never_overwritten(basis, tmp_path):
    directory, _, plan, _, review=basis
    output=tmp_path/'existing';output.mkdir()
    with pytest.raises(FileExistsError):
        resume.resume_responses(directory,output,plan,review,fetch=lambda *_:pytest.fail('Must not fetch'))


def test_provenance_is_saved_before_first_new_request(basis, tmp_path):
    directory, _, plan, _, review = basis
    output = tmp_path/'ready-order'
    events = []
    def ready(path):
        assert (path/'source-lineage.json').is_file()
        assert (path/'responses'/plan['requests'][0]['file']).is_file()
        (path/'environment.json').write_bytes(encoded({'synthetic':True}))
        events.append('ready')
    def fetch(*_):
        assert events == ['ready'] and (output/'environment.json').is_file()
        events.append('fetch')
        raise TimeoutError('synthetic stop')
    with pytest.raises(TimeoutError):
        resume.resume_responses(directory,output,plan,review,ready=ready,fetch=fetch,clock=clock())
    assert events == ['ready','fetch']


def test_second_explicit_continuation_reuses_the_longer_prefix(basis, tmp_path):
    directory, _, plan, responses, review = basis
    partial = tmp_path/'partial'
    environment = {'source_commit':'b'*40,'run_id':456,'run_attempt':1,'scientific_input_sha256':{}}
    def ready(path):
        (path/'environment.json').write_bytes(encoded(environment))
        (path/'resume-preflight.json').write_bytes(encoded({'synthetic':True}))
    seen = []; good = fetcher(plan,responses,seen)
    def fail_after_one(url, cap):
        if seen: raise TimeoutError('synthetic transport interruption')
        return good(url,cap)
    with pytest.raises(TimeoutError):
        resume.resume_responses(directory,partial,plan,review,ready=ready,fetch=fail_after_one,clock=clock())
    case_failure = {'run_id':456,'new_current_widths_admitted':0}
    (partial/'case-failure.json').write_bytes(encoded(case_failure))
    failure = json.loads((partial/'responses/failure.json').read_bytes())
    longer = []
    for name in failure['completed_files']:
        longer.append({'file':name,'response':pin((partial/'responses'/name).read_bytes()),
                       'receipt_sha256':digest((partial/'responses'/(name+'.receipt.json')).read_bytes())})
    reviewed = {**review,'basis_format':'continued_v1','source_responses':longer,'source_commit':'b'*40,
                'run_id':456,'run_attempt':1,'failure':failure,'case_failure':case_failure}
    assert len(resume.verify_basis(partial,plan,reviewed)) == 4
    seen = []; output = tmp_path/'second'
    resume.resume_responses(partial,output,plan,reviewed,fetch=fetcher(plan,responses,seen),
                            clock=lambda:datetime(2027,1,1,tzinfo=timezone.utc))
    assert seen == [request['url'] for request in plan['requests'][4:]]
    lineage = json.loads((output/'source-lineage.json').read_bytes())
    assert lineage['reused_requests'] == 4 and lineage['parent_lineage']['reused_requests'] == 3


def test_compact_projection_copies_exact_existing_values_without_source_arrays():
    from eacc_model_core_diagnostic_v2 import diagnose_year
    from test_eacc_model_core_diagnostic_v2 import jet
    diagnostic=diagnose_year({6:jet()})
    fields={'schema':'osw.eacc-hycom.monthly-vector-fields.v1','source_model_year':2013,
            'provider_depth_m':15,'source_metadata':{},'selection':{},
            'months':[{'month':m,'sample_days':30 if m==6 else 0,'minimum_pairs':24,
                       'eligible_cells':1 if m==6 else 0,'paired_count_min':0,'paired_count_max':30 if m==6 else 0} for m in range(1,13)]}
    projection=resume.review_projection(fields,diagnostic,{'reused_requests':3})
    assert len(projection['case_summaries'])==72 and len(projection['source_months'])==12
    original=next(c for c in diagnostic['cases'] if c['id']=='m06:offset0:step5')
    copied=next(c for c in projection['case_summaries'] if c['id']==original['id'])
    center=next(s for s in original['stations'] if s['station_arc_parameter_km']==0)
    assert copied['central_thresholds'][1]['resolved_span_km']==center['threshold_cases'][1]['resolved_span_km']
    assert 'cases' not in projection and 'eastward_m_s' not in encoded(projection).decode()
    assert projection['annual_physical_minimum_width_km'] is projection['measurement_uncertainty_km'] is None
    assert not projection['current_association_verified'] and projection['new_current_widths_admitted']==0


def test_transport_timeout_is_fifty_seconds_and_response_is_bounded(monkeypatch):
    seen=[]
    class Response:
        status=200;url='https://example.org/source';headers={'Content-Type':'text/plain','Content-Length':'3'}
        def __enter__(self):self.body=io.BytesIO(b'abc');return self
        def __exit__(self,*_):return False
        def read(self,n):return self.body.read(n)
    class Opener:
        def open(self,request,timeout):seen.append((request.full_url,timeout));return Response()
    monkeypatch.setattr(resume.urllib.request,'build_opener',lambda *_:Opener())
    assert resume.fetch_response('https://example.org/source',4)['raw']==b'abc'
    assert seen==[('https://example.org/source',50)]
