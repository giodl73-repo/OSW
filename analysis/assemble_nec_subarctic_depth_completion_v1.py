"""Cloud-only audit and byte-preserving assembly of recovered and completion sections."""
import hashlib
import json
from pathlib import Path
from acquire_zonal_current_depth_sections_v1 import validate_retained

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL='research/nec-subarctic-depth-sections-operator-v1.json'
COMPLETION='research/nec-subarctic-depth-completion-operator-v1.json'
RECOVERY='research/nec-subarctic-depth-transport-recovery-v1.json'
SEED='research/source-data/nec-subarctic-depth-sections-v1/'
OUT=Path('nec-subarctic-depth-sections-v1')
FINISH=Path('nec-subarctic-depth-completion-v1')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def parameters_equal(original,completion):
    allowed={'schema','sections','snapshot_times_utc','input_sha256','transport_completion_context'}
    if {k:v for k,v in original.items() if k not in allowed}!={k:v for k,v in completion.items() if k not in allowed}:raise ValueError('Measurement parameters changed during transport completion')


def source_key(section):return section['snapshot_time_utc'],section['entity_id'],section['section_definition']['id']


def validate_recovered(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());original=read(ORIGINAL);completion=read(COMPLETION);recovery=read(RECOVERY)
    parameters_equal(original,completion)
    expected={(t,s['entity_id'],s['id']) for t in original['snapshot_times_utc'] for s in original['sections']}
    remaining={(t,s['entity_id'],s['id']) for t in completion['snapshot_times_utc'] for s in completion['sections']}
    recovered={};definitions={(s['entity_id'],s['id']):s for s in original['sections']}
    for row in recovery['recovered_sections']:
        raw=(root/row['file']).read_bytes();section=json.loads(raw);key=source_key(section)
        if key in recovered or sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:raise ValueError('Recovered section duplicate/byte mismatch')
        if section['operator_file']!=ORIGINAL or section['operator_sha256']!=sha((root/ORIGINAL).read_bytes()):raise ValueError('Recovered original operator changed')
        if section['section_definition']!=definitions[key[1:]]:raise ValueError('Recovered original section definition changed')
        validate_retained(section,{**original,**original['currents'][section['entity_id']]})
        recovered[key]=(raw,section)
    if len(recovered)!=29 or len(remaining)!=5 or set(recovered)&remaining or set(recovered)|remaining!=expected:raise ValueError('Exact original34section partition required')
    for s in completion['sections']:
        if s!=definitions[s['entity_id'],s['id']]:raise ValueError('Completion gate changed')
    return original,completion,recovery,recovered,remaining


def assemble(root=ROOT,finish=FINISH):
    original,completion,recovery,recovered,remaining=validate_recovered(root)
    completed=json.loads((finish/'manifest.json').read_bytes());new={}
    if completed['operator_file']!=COMPLETION or completed['operator_sha256']!=sha((root/COMPLETION).read_bytes()):raise ValueError('Completion source manifest operator changed')
    definitions={(s['entity_id'],s['id']):s for s in original['sections']}
    for row in completed['sections']:
        raw=(finish/row['file']).read_bytes();section=json.loads(raw);key=source_key(section)
        if key in new or sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:raise ValueError('Completion source bytes changed')
        if section['operator_file']!=COMPLETION or section['operator_sha256']!=completed['operator_sha256'] or section['section_definition']!=definitions[key[1:]]:raise ValueError('Completion operator/geometry changed')
        validate_retained(section,{**original,**original['currents'][section['entity_id']]})
        new[key]=(raw,section)
    if set(new)!=remaining:raise ValueError('Exactly missing original five sections required')
    all_sections={**recovered,**new};entries=[];pieces={}
    for stamp in original['snapshot_times_utc']:
        for definition in original['sections']:
            raw,section=all_sections[stamp,definition['entity_id'],definition['id']]
            filename=stamp[:10]+'-'+definition['entity_id'].split(':')[1]+'-'+definition['id']+'.json'
            diagnosis=section['diagnosis'];pieces[filename]=raw
            entries.append({'file':filename,'sha256':sha(raw),'bytes':len(raw),'section_id':definition['id'],'snapshot_time_utc':stamp,
                'entity_id':definition['entity_id'],'native_columns':len(section['columns']),'selected_column_index':diagnosis['selected_column_index'],
                'horizontal_selection_status':diagnosis['horizontal_selection_status'],'selected_column_threshold_layers':diagnosis['selected_column_threshold_layers'],
                'source_operator_file':section['operator_file'],'source_operator_sha256':section['operator_sha256'],
                'transport_origin':'recovered_original_attempt2' if source_key(section) in recovered else 'completion_missing_five'})
    manifest={'schema':'osw.nec-subarctic-completed-depth-sections-manifest.v1','operator_file':ORIGINAL,'operator_sha256':sha((root/ORIGINAL).read_bytes()),
        'input_sha256':{**original['input_sha256'],ORIGINAL:sha((root/ORIGINAL).read_bytes()),COMPLETION:sha((root/COMPLETION).read_bytes()),RECOVERY:sha((root/RECOVERY).read_bytes()),
            'analysis/assemble_nec_subarctic_depth_completion_v1.py':sha((root/'analysis/assemble_nec_subarctic_depth_completion_v1.py').read_bytes())},
        'sections':entries,'recovered_original_sections':29,'newly_acquired_completion_sections':5,
        'decoded_velocity_cell_pairs':sum(e['native_columns']*40 for e in entries),'decoded_velocity_array_bytes':None,
        'velocity_counter_scope':'Cellpairs count the full retained34section target. Failedattempt2 ended before its aggregate decodedbytecounter was saved;do not infer it from JSONfloats. This is not totalwiretraffic or allfailedattemptprocessing.',
        'completion_acquisition_velocity_cell_pairs':completed['decoded_velocity_cell_pairs'],'completion_acquisition_decoded_velocity_array_bytes':completed['decoded_velocity_array_bytes'],
        'decoded_temperature_scalars':0,'decoded_temperature_array_bytes':0,'all_original_source_chunk_bytes_preserved':True,'full_goal_complete':False}
    return manifest,pieces


def main():
    manifest,pieces=assemble();OUT.mkdir(exist_ok=True)
    for filename,raw in pieces.items():(OUT/filename).write_bytes(raw)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'retained_target_sections':len(pieces),'recovered_unchanged':29,'new_completion_sections':5,'retained_cell_pairs':manifest['decoded_velocity_cell_pairs'],'physical_volume_estimates':0}))


if __name__=='__main__':main()
