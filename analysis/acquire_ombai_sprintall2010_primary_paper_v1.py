"""Single bounded cloud custody request for the original Ombai Strait observation paper."""
import hashlib,json
from contextlib import contextmanager
from pathlib import Path
import acquire_egcc_sutherland_primary_paper_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ombai-sprintall2010-primary-paper-acquisition-operator-v1.json'
URL='https://pordlabs.ucsd.edu/jsprintall/pub_dir/Sprintall_etal_DYNAT2010.pdf'
MAX_BODY_BYTES=frozen.MAX_BODY_BYTES


@contextmanager
def configured():
    old=frozen.URL;frozen.URL=URL
    try:yield
    finally:frozen.URL=old


def acquire(op,out,transport=None):
    with configured():report=frozen.acquire(op,out,transport)
    report['schema']='osw.ombai-sprintall2010-primary-paper-acquisition.v1'
    return report


if __name__=='__main__':
    op=json.loads((ROOT/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned custody input changed: '+file)
    out=Path('ombai-sprintall2010-primary-paper-v1');report=acquire(op,out);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),input_sha256=op['input_sha256']);(out/'acquisition.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
