"""Coverage snapshot v11; frozen v1 join rules applied to the new retained report."""
import json
from pathlib import Path
import audit_current_depth_coverage_v1 as frozen

ROOT=frozen.ROOT
OPERATOR='research/current-depth-coverage-audit-operator-v11.json'


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes());previous=frozen.OPERATOR
    try:
        frozen.OPERATOR=OPERATOR
        report,unused=frozen.build(root)
    finally:frozen.OPERATOR=previous
    report['schema']='osw.current-depth-coverage-audit.v11'
    report['previous_coverage_snapshot']=op['previous_coverage_snapshot']
    report['snapshot_reason']=op['snapshot_reason']
    raw=frozen.encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed audit output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('current-depth-coverage-audit-v11');out.mkdir(exist_ok=True);(out/'coverage.json').write_bytes(raw);print(json.dumps({'counts':report['counts'],'model_totals':report['registered_model_totals'],'balearic':next(r for r in report['currents'] if r['entity_id']=='current:balearic'),'top_backlog':report['source_cohort_backlog'][:3]}),flush=True)
