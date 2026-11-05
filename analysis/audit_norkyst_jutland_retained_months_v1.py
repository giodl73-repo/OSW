"""Cloud-only reconstruction of immutable, retained March/partial-June responses."""
import hashlib
import json
import zipfile
import urllib.request
from pathlib import Path
import numpy as np
import collect_norkyst_jutland_calendar_months_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OP='research/norkyst-jutland-retained-month-audit-operator-v1.json'
SOURCE='research/source-data/norkyst-jutland-calendar-months-v1'


def no_network(*args,**kwargs):
    raise RuntimeError('Retained-source audit forbids every provider request')


def main():
    urllib.request.urlopen=no_network
    urllib.request.build_opener=no_network
    try:urllib.request.urlopen('https://invalid.example/')
    except RuntimeError:pass
    else:raise AssertionError('Network tripwire must fire')
    op=json.loads((ROOT/OP).read_bytes())
    for path,pin in op['input_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==pin,path
    plan,_=frozen.load(ROOT)
    targets={t['target_index']:t for t in plan['request_plan']}
    result={'schema':'osw.norkyst-jutland-retained-month-audit.v1','provider_requests':0,
            'source_run':41969432667,'source_run_timed_out':True,'months':[],
            'budget':plan['budget'],'input_sha256':op['input_sha256'],
            'physical_current_thickness_m':None,'volume_m3':None,'annual_range_m':None,
            'full_goal_complete':False,'runtime_changed':False}
    all_indices=[]
    for month in [3,6]:
        folder=ROOT/SOURCE/f'month-{month:02d}'
        receipt=json.loads((folder/'receipt.json').read_bytes())
        hours=plan['planned_month_hours'][str(month)]
        q=np.full((3,hours,11),np.nan);assigned=np.zeros((3,hours),dtype=bool)
        for old in plan['reused_prior_noon_profiles']:
            if int(old['date'][5:7])==month:
                values=np.array([[np.nan if v is None else v for v in old['reused_component_values']]])
                frozen.assign(q,assigned,old['point_index'],[14*24+12],values)
        archive=folder/'source-responses.zip'
        if 'raw_archive_sha256' in receipt:
            assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['raw_archive_sha256']
        with zipfile.ZipFile(archive) as z:
            assert len(z.namelist())==len(set(z.namelist()))
            rows=receipt['transport_receipts']
            assert set(z.namelist())=={r['archive_member'] for r in rows}
            for row in rows:
                assert row['status']=='received_archived_and_assigned' and row['attempts']==1
                index=row['target_index'];assert index not in all_indices;all_indices.append(index)
                target=targets[index];assert target['month']==month and target['http_url']==row['url']
                raw=z.read(row['archive_member']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                values=frozen.parse(raw,target,plan['fixed_points'][target['point_index']])
                first=(int(target['date'][-2:])-1)*24+target['first_hour']
                frozen.assign(q,assigned,target['point_index'],list(range(first,first+target['hourly_profiles'])),values)
        assert assigned.sum(axis=1).astype(int).tolist()==receipt['source_hours_assigned_per_point']
        profiles=[{'point_index':i,'statistics':frozen.statistics(q[i])} for i in range(3)]
        if 'profiles' in receipt:assert profiles==receipt['profiles']
        result['months'].append({'month':month,'expected_hours_per_point':hours,
                                'archived_responses':len(rows),
                                'source_hours_assigned_per_point':receipt['source_hours_assigned_per_point'],
                                'complete_time_support_points':int((assigned.sum(axis=1)==hours).sum()),
                                'original_complete_month_statistics_match':profiles==receipt.get('profiles'),
                                'profiles':profiles})
    assert all_indices==list(range(150))
    programme=json.loads((ROOT/SOURCE/'programme.json').read_bytes())
    assert programme['requests_attempted']==151
    result.update(archived_source_responses_reconstructed=150,
                  persisted_programme_attempts=151,
                  unretained_and_shutdown_requests_quarantined=True,
                  partial_june_cannot_supply_complete_month_means=True,
                  interpretation=[
                      'March has all calendar source hours; per-depth missing values remain missing and can still prevent a primary depth descriptor.',
                      'Partial June statistics have no complete-calendar numeric means. Retained noon profiles are reused exactly once.',
                      'Programme and monthly artifacts were captured at different shutdown instants. Persisted attempts exceed archived responses; no absence from the archive establishes that a target was unattempted.',
                      'No interrupted or uncertain June target may be retried using this audit. Future acquisition needs a durable pre-request journal and an in-process deadline before artifact upload.',
                      'Provider fixed-z component contours, temporal variability and source coverage are separate from physical thickness, uncertainty and whole-current volume.'])
    out=ROOT/'norkyst-jutland-retained-month-audit-v1';out.mkdir(exist_ok=True)
    (out/'audit.json').write_bytes(frozen.frozen.encode(result))
    print(json.dumps({'status':'PASS_RETAINED_SOURCE_RECONSTRUCTION','archived_responses':150,
                      'months':[{'month':m['month'],'assigned_hours':m['source_hours_assigned_per_point'],
                                 'primary_depth_descriptors':[p['statistics']['primary_mean_field_depth_descriptor'] for p in m['profiles']]} for m in result['months']],
                      'provider_requests':0}),flush=True)


if __name__=='__main__':main()
