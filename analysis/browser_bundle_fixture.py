"""Serve complete mutated packets through the local HTTP server, avoiding CDP body copies."""
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
import atexit,hashlib,json,tempfile

ROOT=Path(__file__).resolve().parents[1]

def install_bundle_fixture(page,bundle):
    directory=ROOT/'.pytest_cache/browser-bundle-fixtures';directory.mkdir(parents=True,exist_ok=True)
    if not directory.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Fixture directory must stay inside the workspace')
    raw=json.dumps(bundle,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    with tempfile.NamedTemporaryFile(dir=directory,prefix='packet-',suffix='.json',delete=False) as handle:
        handle.write(raw);path=Path(handle.name)
    relative='/'+path.relative_to(ROOT).as_posix()
    manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_bytes())
    manifest['sha256']['almanac/query-data.json']=hashlib.sha256(raw).hexdigest()
    def cleanup(*_):
        if not path.resolve().is_relative_to(directory.resolve()):raise ValueError('Unexpected fixture cleanup path')
        try:path.unlink(missing_ok=True)
        except PermissionError:pass  # A server read may still be closing; later hooks retry.
    def serve(route):
        parts=urlsplit(route.request.url)
        if parts.hostname not in ['127.0.0.1','localhost','::1']:raise ValueError('Bundle fixtures require the local workspace server')
        route.continue_(url=urlunsplit((parts.scheme,parts.netloc,relative,'','')))
    page.route('**/query-engine.manifest.json',lambda route:route.fulfill(json=manifest))
    page.route('**/query-data.json',serve)
    page.once('close',cleanup);page.context.once('close',cleanup);atexit.register(cleanup)
    return path
