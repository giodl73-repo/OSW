"""One bounded cloud capture of an independently identified primary paper."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/rodhe1987-depth-evidence-operator-v1.json'
URL = 'https://tellusjournal.org/articles/1809/files/submission/proof/1809-1-43436-1-10-20220928.pdf'


def acquire(op, ledger, opener=urllib.request.urlopen):
    if op['source_url'] != URL or op['maximum_requests'] != 1 or op['timeout_seconds'] != 25 or op['maximum_body_bytes'] != 2400000:
        raise ValueError('Fixed single-request document budget required')
    ledger.update(attempts=1, body_bytes=0, status='reserved', automatic_retries=0)
    request = urllib.request.Request(URL, headers={'Accept-Encoding': 'identity', 'User-Agent': 'OSW-primary-depth-evidence-v1'})
    try:
        with opener(request, timeout=25) as response:
            ledger['final_url'] = response.url
            ledger['http_status'] = response.status
            if response.status != 200 or not response.url.startswith('https://') or response.headers.get('Content-Encoding') not in [None, 'identity']:
                raise ValueError('HTTPS200 uncompressed response required')
            length = response.headers.get('Content-Length')
            if length is not None and (not length.isdigit() or int(length) > op['maximum_body_bytes']):
                raise ValueError('Declared source exceeds document budget')
            chunks = []
            while True:
                chunk = response.read(min(65536, op['maximum_body_bytes'] - ledger['body_bytes'] + 1))
                if not chunk: break
                chunks.append(chunk); ledger['body_bytes'] += len(chunk)
                if ledger['body_bytes'] > op['maximum_body_bytes']:
                    raise ValueError('Streamed document budget exceeded')
        raw = b''.join(chunks)
        if not raw.startswith(b'%PDF-') or length is not None and len(raw) != int(length):
            raise ValueError('Complete PDF response required')
        ledger.update(status='success', body_sha256=hashlib.sha256(raw).hexdigest())
        return raw
    except Exception as error:
        ledger.update(status='failed_no_retry', error_type=type(error).__name__, error_summary=str(error)[:250])
        raise


def inspect(document, op):
    if len(document) != 9:
        raise ValueError('Original nine-page article required')
    pages = [{'pdf_page_number': i + 1, 'text': page.get_text()} for i, page in enumerate(document)]
    text = ' '.join(' '.join(p['text'].split()) for p in pages)
    for term in ['The large-scale circulation in the Skagerrak', 'JOHAN RODHE', 'Jutland Current', '1975', '1977']:
        if term not in text:
            raise ValueError('Primary article identity missing: ' + term)
    if sum(len(p['text']) for p in pages) > 120000:
        raise ValueError('Bounded original article text required')
    return {'schema': 'osw.rodhe1987-primary-depth-evidence.v1',
            'doi': '10.3402/tellusa.v39i3.11757', 'source_url': URL,
            'citation': 'Rodhe,J.(1987),The large-scale circulation in the Skagerrak;interpretation of some observations,Tellus39A,245-253.',
            'license': 'CC BY4.0', 'license_evidence_url': 'https://doi.org/10.3402/tellusa.v39i3.11757',
            'pages': pages, 'candidate_entity_id': 'current:jutland',
            'depth_values_admitted': 0, 'figure_digitization_performed': False,
            'velocity_profiles_extracted': False, 'reference_inventory_changed': False,
            'runtime_changed': False, 'full_goal_complete': False}


def main():
    import pymupdf
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for path, pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Frozen source-review input changed: ' + path)
    out = ROOT / 'rodhe1987-depth-evidence-v1'; out.mkdir(exist_ok=True)
    ledger = {'schema': 'osw.primary-document-transport.v1', 'source_url': URL, 'ocean_field_requests': 0}
    try:
        raw = acquire(op, ledger)
        with pymupdf.open(stream=raw, filetype='pdf') as document:
            report = inspect(document, op)
            report['source_pdf_sha256'] = hashlib.sha256(raw).hexdigest()
            report['source_pdf_bytes'] = len(raw)
            report['input_sha256'] = op['input_sha256']
            outputs = {'article.pdf': raw, 'evidence.json': (json.dumps(report, indent=2) + '\n').encode()}
            for page in [3, 4, 5]:
                outputs['page-' + str(page) + '.png'] = document[page - 1].get_pixmap(dpi=100).tobytes('png')
        if sum(map(len, outputs.values())) > 2400000:
            raise ValueError('Bounded source evidence batch exceeded')
        for name, content in outputs.items(): (out / name).write_bytes(content)
        print(json.dumps({'status': 'source_captured_pending_scope_review', 'pages': 9, 'depth_values_admitted': 0}))
    finally:
        (out / 'transport-ledger.json').write_bytes((json.dumps(ledger, indent=2) + '\n').encode())


if __name__ == '__main__': main()
