"""New declared NCC sections using frozen numerics with immediate read journaling."""
import hashlib,json
from contextlib import contextmanager
from pathlib import Path
import acquire_ncc_north_joint_sections_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ncc-mid-norway-joint-sections-operator-v1.json'
OUT=Path('ncc-mid-norway-joint-sections-v1')
SECTIONS=[{'id':'section-63n','entity_id':frozen.OWNER,'fixed_axis':'latitude','latitude_degrees_north':63,'longitude_gate_degrees_east':[4.5,9.5]},{'id':'section-63p75n','entity_id':frozen.OWNER,'fixed_axis':'latitude','latitude_degrees_north':63.75,'longitude_gate_degrees_east':[6,11.5]}]
BASE_READS=frozen.JointReads


class JournalReads(BASE_READS):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.journal=self.path.parent/'field-journal';self.journal.mkdir(exist_ok=True)
    def read(self,var,it,iy,x0,x1):
        if var.name not in frozen.FIELDS:raise ValueError('Only original three declared fields may be journaled')
        name=f'{var.name}-t{it}-y{iy}-x{x0}-{x1}.json';path=self.journal/name
        if path.exists():raise ValueError('Existing successful native patch journal cannot be overwritten or replayed')
        inflight={'schema':'osw.ncc-joint-inflight-field-intent.v1','variable':var.name,'time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[x0,x1],'depth_indices_inclusive':[0,39],'status':'ENTERING_VALIDATED_READER_NOT_A_SUCCESS_CLAIM'}
        (self.path.parent/'inflight-read.json').write_bytes(frozen.encode(inflight))
        a=super().read(var,it,iy,x0,x1)
        record={'schema':'osw.ncc-joint-successful-native-field-patch.v1','variable':var.name,'source_dataset':frozen.TS if var.name=='salinity' else frozen.UV,'time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[x0,x1],'depth_indices_inclusive':[0,39],'native_shape':[40,x1-x0+1],'native_flat_depth_major_values':frozen.clean(a.ravel()),'wire_hash_claimed':False}
        raw=frozen.encode(record)
        if len(raw)>=2500000:raise ValueError('Fixed journal per-file cap exceeded')
        with path.open('xb') as handle:handle.write(raw)
        inflight.update(status='SUCCESSFUL_NATIVE_VALUES_JOURNALED',journal_file='field-journal/'+name,journal_sha256=frozen.digest(raw));(self.path.parent/'inflight-read.json').write_bytes(frozen.encode(inflight))
        return a


@contextmanager
def configured():
    old=(frozen.OPERATOR,frozen.SECTIONS,frozen.JointReads)
    frozen.OPERATOR=OPERATOR;frozen.SECTIONS=SECTIONS;frozen.JointReads=JournalReads
    try:yield
    finally:frozen.OPERATOR,frozen.SECTIONS,frozen.JointReads=old


def collect(root=ROOT,out=OUT,factory=None):
    out=Path(out)
    with configured():
        kwargs={} if factory is None else {'factory':factory}
        frozen.collect(root=root,out=out,**kwargs)
    report=json.loads((out/'source-report.json').read_bytes());ledger=json.loads((out/'transport-ledger.json').read_bytes());pieces=[]
    for file in sorted((out/'field-journal').glob('*.json')):
        raw=file.read_bytes();pieces.append({'file':'field-journal/'+file.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    if len(pieces)!=24 or len([r for r in ledger['requests'] if r['status']=='success'])!=24:raise ValueError('Every successful original field patch must be retained once')
    manifest={'schema':'osw.ncc-mid-norway-native-patch-journal-manifest.v1','operator_file':OPERATOR,'operator_sha256':frozen.digest((root/OPERATOR).read_bytes()),'source_report_sha256':frozen.digest((out/'source-report.json').read_bytes()),'transport_ledger_sha256':frozen.digest((out/'transport-ledger.json').read_bytes()),'last_field_intent_sha256':frozen.digest((out/'inflight-read.json').read_bytes()),'successful_patches':pieces,'all_successful_field_reads_retained':True,'successful_field_reads_replayed':False,'wire_hash_claimed':False,'full_goal_complete':False}
    (out/'journal-manifest.json').write_bytes(frozen.encode(manifest))
    if sum(file.stat().st_size for file in out.rglob('*') if file.is_file())>=2400000:raise ValueError('Complete source plus patch journal must fit original source batch cap')
    print(json.dumps({'new_source_counts':report['counts'],'successful_patch_journal_files':len(pieces),'new_ocean_field_reads_for_journaling':0}),flush=True)


if __name__=='__main__':collect()
