"""Cloud-only acquisition of one explicitly allowlisted public research PDF."""
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/eddy-primary-paper-acquisition-request-v1.json'
OUT = ROOT / '.pytest_cache/eddy-primary-paper-acquisition-v1'
PAPERS = {
    'haley-2023': {
        'url': 'https://mseas.mit.edu/publications/PDF/Haley_et_al_Oceans2023.pdf',
        'doi': '10.23919/OCEANS52994.2023.10337035',
    },
}


def main():
    assert os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true'
    assert os.environ.get('GITHUB_REPOSITORY') == 'giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF') == 'refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    request = json.loads((ROOT / REQUEST).read_bytes())
    assert request['schema'] == 'osw.eddy-primary-paper-acquisition-request.v1'
    assert request['execute'] is True and request['paper'] in PAPERS
    assert request['script_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert request['maximum_bytes'] == 15000000 and request['socket_timeout_seconds'] == 25
    assert request['maximum_attempts'] == request['max_cloud_jobs'] == 1
    assert all(request[k] is False for k in ['ocean_fields_permitted', 'browser_permitted', 'runtime_processing_permitted', 'installation_permitted', 'main_merge_permitted'])
    source = PAPERS[request['paper']]
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        'schema': 'osw.eddy-primary-paper-acquisition-result.v1',
        'source_commit': os.environ['GITHUB_SHA'],
        'request_sha256': hashlib.sha256((ROOT / REQUEST).read_bytes()).hexdigest(),
        'script_sha256': request['script_sha256'],
        'paper': request['paper'], 'source': source, 'attempts': 1,
        'original_assets_committed': False, 'measurements_admitted': 0,
        'ocean_field_processing': False, 'runtime_changed': False,
    }
    try:
        with urllib.request.urlopen(source['url'], timeout=25) as response:
            final_url = response.geturl()
            assert final_url.split('#')[0] == source['url'], 'Unexpected source redirect'
            raw = response.read(request['maximum_bytes'] + 1)
        assert raw.startswith(b'%PDF') and len(raw) <= request['maximum_bytes'], 'Not a bounded original PDF'
        (OUT / 'original.pdf').write_bytes(raw)
        result.update(status='ORIGINAL_PDF_RETAINED', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    except (urllib.error.URLError, TimeoutError, AssertionError, OSError) as error:
        result.update(status='ORIGINAL_PDF_UNAVAILABLE', error_type=type(error).__name__, error=str(error)[:500])
    (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
