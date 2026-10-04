"""Audit complete width candidate series and pinned derivation."""
import json
from pathlib import Path
from build_current_section_width_series import ROOT, OUTPUT, PROTOCOL, digest, compute

def validate(document):
    if document['status'] != 'derived_width_candidate_requires_scientific_review' or document['metric'] != 'meridional_half_peak_eastward_velocity_section_span' or document['current_id'] != 'gulf-stream-system' or document['section_longitude'] != -70 or document['latitude_window'] != [35,41]:
        raise ValueError('Changed section definition or admission')
    for flag in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','is_confidence_interval']:
        if document[flag] is not False:raise ValueError('Unsupported width inference')
    if document['annual_width_range_km'] is not None:raise ValueError('Unsupported annual extrema')
    for field,path in [('protocol_sha256',PROTOCOL),('general_protocol_sha256',ROOT/'plans/ocean-current-width-measurement-protocol-v1.md'),('generator_sha256',ROOT/'analysis/build_current_section_width_series.py'),('velocity_sampler_sha256',ROOT/'analysis/build_gulf_stream_geostrophic_path.py')]:
        if document[field]!=digest(path):raise ValueError('Stale width provenance')
    expected_frames=[]
    for filename in ['ocean-current-dated-timeline.json','ocean-current-dated-timeline-2025.json']:
        expected_frames.extend(json.loads((ROOT/'research'/filename).read_text(encoding='utf-8'))['frames'])
    expected_frames.sort(key=lambda r:r['date'])
    if [r['date'] for r in document['frames']] != [r['date'] for r in expected_frames]:raise ValueError('Missing or duplicated date')
    expected_spans=[]
    for year in sorted({r['date'][:4] for r in document['frames']}):
        selected=[r for r in document['frames'] if r['date'].startswith(year) and r['approximate_section_span_km'] is not None]
        values=[r['approximate_section_span_km'] for r in selected]
        expected_spans.append({'year':int(year),'sample_count':len(selected),'rounded_sample_value_span_km':[min(values),max(values)] if values else None,'range_kind':'span_of_sampled_rounded_section_candidate_values_not_annual_extrema','source_algorithms':sorted({r['source_algorithm'] for r in selected})})
    if document['sample_value_spans']!=expected_spans:raise ValueError('Conflated sample span or annual extremes')
    for frame,expected in zip(document['frames'],expected_frames):
        path=ROOT/expected['source_subset']
        if frame['source_subset']!=expected['source_subset'] or frame['source_subset_sha256']!=digest(path) or digest(path)!=expected['source_subset_sha256']:raise ValueError('Changed source')
        source=json.loads(path.read_text(encoding='utf-8'))
        if frame['source_url']!=source['source_url'] or frame['source_algorithm']!=source['source_algorithm']:raise ValueError('Changed source attribution')
        for key,value in compute(source).items():
            if frame[key]!=value:raise ValueError(f'Changed width derivation: {key}')

if __name__=='__main__':
    validate(json.loads(OUTPUT.read_text(encoding='utf-8')))
    print('OK: 17 fixed-section width candidates; thresholds, resolution and provenance verified')
