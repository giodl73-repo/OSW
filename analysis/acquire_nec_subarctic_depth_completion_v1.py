"""Retrieve only the five missing sections after two terminal transport failures."""
from pathlib import Path
import hashlib
import json
import time
import acquire_zonal_current_depth_sections_v1 as collector


def run_with_io_retries(call,output,sleep=time.sleep):
    attempts=[]
    for attempt in range(1,4):
        try:
            call();attempts.append({'attempt':attempt,'status':'success'})
            return {'maximum_attempts':3,'attempts':attempts,'successful_attempt':attempt,'requests_sequential':True}
        except RuntimeError as error:
            if 'NetCDF: I/O failure' not in str(error):raise
            saved=[];archive=output/('failed-transport-attempt-'+str(attempt));archive.mkdir(parents=True,exist_ok=True)
            for p in sorted(output.glob('*.json')):
                raw=p.read_bytes();(archive/p.name).write_bytes(raw)
                saved.append({'file':p.name,'sha256':hashlib.sha256(raw).hexdigest()})
            attempts.append({'attempt':attempt,'status':'provider_io_failure','saved_partial_files':saved})
            print(json.dumps(attempts[-1]),flush=True)
            if attempt==3:raise
            sleep([2,5][attempt-1])


def main():
    collector.OPERATOR='research/nec-subarctic-depth-completion-operator-v1.json'
    collector.OUT=Path('nec-subarctic-depth-completion-v1')
    op=json.loads((collector.ROOT/collector.OPERATOR).read_bytes())
    maximum_pairs=3*len(op['sections'])*len(op['snapshot_times_utc'])*40*150
    if maximum_pairs>op['maximum_total_cell_pairs'] or maximum_pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('All retries must fit original pair/byte caps even at150rows persection')
    receipt=run_with_io_retries(collector.main,collector.OUT)
    receipt.update(worst_case_velocity_pairs_across_all_attempts=maximum_pairs,worst_case_decoded_velocity_bytes_across_all_attempts=maximum_pairs*16,
        scope='Onlythefiveoriginalmissingsections;no recovered29sections re-requested;final source manifest records the successful acquisition counters,not allwiretraffic.')
    (collector.OUT/'transport-attempts.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()
