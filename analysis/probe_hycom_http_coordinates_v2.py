"""Projected DDS wrapper; full arrays, DAS semantics and all controls stay frozen."""
import json,subprocess,sys
from contextlib import contextmanager
from pathlib import Path
import probe_hycom_http_coordinates_v1 as frozen

ROOT=frozen.ROOT
OPERATOR='research/hycom-http-coordinate-probe-operator-v2.json'
OUT=Path('hycom-http-coordinate-probe-v2')
DDS_PROJECTION='depth,lat,lon,time'
REWRITE={url+'.dds':url+'.dds?'+DDS_PROJECTION for url in frozen.frozen.SOURCES.values()}
URLS={REWRITE.get(url,url):cap for url,cap in frozen.URLS.items()}
BASE_HTTP=frozen.HTTP


class ProjectedHTTP(BASE_HTTP):
    def get(self,url):return super().get(REWRITE.get(url,url))


@contextmanager
def configured():
    old=(frozen.OPERATOR,frozen.HTTP,frozen.URLS)
    frozen.OPERATOR=OPERATOR;frozen.HTTP=ProjectedHTTP;frozen.URLS=URLS
    try:yield
    finally:frozen.OPERATOR,frozen.HTTP,frozen.URLS=old


def validate(root):
    op=json.loads((root/OPERATOR).read_bytes())
    if op['dds_projection']!=DDS_PROJECTION or op['das_projection_applied'] is not False:raise ValueError('Exact structural DDS projection;DAS semantics unchanged')


def worker(root=ROOT,out=OUT,opener=None):
    validate(root)
    with configured():report=frozen.worker(root=root,out=out,opener=opener)
    report['coordinate_transport_backend']='bounded_HTTP_ASCII_Float64_with_projected_DDS';report['dds_projection']=DDS_PROJECTION;report['das_projection_applied']=False;frozen.frozen.write_json(Path(out)/'worker-report.json',report);return report


def probe(root=ROOT,out=OUT,runner=subprocess.run):
    validate(root)
    def wrapper_runner(command,**kwargs):
        command=list(command);command[1]=str(Path(__file__).resolve());return runner(command,**kwargs)
    with configured():frozen.probe(root=root,out=out,runner=wrapper_runner)


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':worker(out=Path(sys.argv[2]))
    elif len(sys.argv)==1:probe()
    else:raise ValueError('Only projected coordinate parent/worker invocations supported')
