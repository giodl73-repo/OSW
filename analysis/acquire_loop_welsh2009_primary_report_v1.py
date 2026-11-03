"""Single bounded cloud custody request for the original Loop Current report."""
import hashlib,json
from contextlib import contextmanager
from pathlib import Path
import acquire_egcc_sutherland_primary_paper_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/loop-welsh2009-primary-report-acquisition-operator-v1.json'
URL='https://www.govinfo.gov/content/pkg/GOVPUB-I-1209c486df8b403de48830335b48b65f/pdf/GOVPUB-I-1209c486df8b403de48830335b48b65f.pdf'
MAX_BODY_BYTES=frozen.MAX_BODY_BYTES


@contextmanager
def configured():
    old=frozen.URL;frozen.URL=URL
    try:yield
    finally:frozen.URL=old


def acquire(op,out,transport=None):
    with configured():report=frozen.acquire(op,out,transport)
    report['schema']='osw.loop-welsh2009-primary-report-acquisition.v1'
    return report


if __name__=='__main__':
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned custody input changed: '+file)
    out=Path('loop-welsh2009-primary-report-v1');report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256']);(out/'acquisition.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
