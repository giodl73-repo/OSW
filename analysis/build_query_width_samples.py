"""Project source-bound scoped samples for queries; never infer annual dimensions."""
import copy
from datetime import date

FAMILIES={
    'diagnostic:florida-monthly-width':'florida_monthly_half_peak_plot',
    'diagnostic:leeuwin-monthly-width':'leeuwin_monthly_fitted_plot',
    'diagnostic:kuroshio-seasonal-width':'kuroshio_seasonal_profile_plot',
    'diagnostic:necc-monthly-section':'necc_monthly_connected_component',
    'diagnostic:gulf-stream-widths':'gulf_stream_dated_half_peak_section',
    'diagnostic:yucatan-noaa-sections':'loop_dated_half_peak_section',
    'diagnostic:yucatan-adt-sections':'loop_dated_half_peak_section',
}


def build(diagnostics):
    rows=[]
    for diagnostic in diagnostics:
        identifier=diagnostic['id']
        if identifier not in FAMILIES:continue
        document=diagnostic['document'];family=FAMILIES[identifier]
        context={k:copy.deepcopy(v) for k,v in document.items() if k not in ['months','seasons','frames']}
        if context['whole_current_representative'] is not False or context['width_rank_eligible'] is not False or context['is_confidence_interval'] is not False or context['annual_width_range_km'] is not None:raise ValueError('Scoped samples cannot become whole-current dimensions')
        selections=[]
        if family=='kuroshio_seasonal_profile_plot':
            for phase_index,phase in enumerate(document['seasons']):
                for sample_index,sample in enumerate(phase['samples']):
                    selections.append((f'/seasons/{phase_index}/samples/{sample_index}',sample,phase,f'/seasons/{phase_index}'))
        elif family in ['gulf_stream_dated_half_peak_section','loop_dated_half_peak_section']:
            selections=[(f'/frames/{index}',sample,None,None) for index,sample in enumerate(document['frames'])]
        else:
            selections=[(f'/months/{index}',sample,None,None) for index,sample in enumerate(document['months'])]
        for path,sample,phase,phase_path in selections:
            phase_context={k:copy.deepcopy(v) for k,v in phase.items() if k!='samples'} if phase else None
            dated=family in ['gulf_stream_dated_half_peak_section','loop_dated_half_peak_section']
            day=date.fromisoformat(sample['date']) if dated else None
            label=sample['date'] if dated else phase['label']+' · '+str(sample['longitude_degrees_east'])+'° E' if phase else sample['label']
            value=sample['approximate_section_span_km'] if dated else sample.get('approximate_width_km') if family!='necc_monthly_connected_component' else sample['zero_crossing']['span_km']
            rows.append({'id':f'width-sample:{identifier.removeprefix("diagnostic:")}:{path.strip("/").replace("/",":")}',
                'entity_id':'current:'+document['current_id'],'current_id':document['current_id'],
                'label':document['current_id'].replace('-',' ').title()+' — '+label,'sample_family':family,
                'diagnostic_id':identifier,'sample_path':path,'phase_path':phase_path,
                'source_sample':copy.deepcopy(sample),'source_phase':phase_context,'source_context':copy.deepcopy(context),
                'value_km':value,'plot_reading_interval_km':copy.deepcopy(sample.get('plot_reading_interval_km')),
                'measurement_uncertainty_interval_km':None,'is_confidence_interval':False,
                'observation_date':sample['date'] if dated else None,
                'source_algorithm':sample['source_algorithm'] if dated else None,
                'diagnostic_sensitivity_interval_km':copy.deepcopy(sample['threshold_sensitivity_span_km']) if dated else None,
                'sampling_bracket_interval_km':copy.deepcopy(sample['nominal'].get('grid_bracket_span_km')) if dated else None,
                'resolution_review_required':sample['nominal'].get('resolution_review_required') if dated else None,
                'whole_current_representative':False,'width_rank_eligible':False,'annual_width_range_km':None,
                'month':day.month if dated else sample.get('month'),'year':day.year if dated else document.get('year'),'phase_label':label if dated else phase['label'] if phase else sample['label'],
                'latitude_degrees_north':document.get('section_latitude'),
                'longitude_degrees_east':document['section_longitude'] if dated else sample.get('longitude_degrees_east',document.get('section_longitude_degrees_east')),
                'metric':document['metric'] if dated else document.get('width_metric',document.get('width_equation')),
                'status':sample['nominal']['status'] if dated else sample.get('status',sample.get('zero_crossing',{}).get('status',document['status'])),
                'scope':document['scope_note'] if family=='loop_dated_half_peak_section' else 'Individual recorded-day meridional half-peak eastward-component span at 70 W. Rounded diagnostic values; finite threshold sensitivity and grid brackets are separate from measurement uncertainty. Days are not monthly means, annual extrema or streamline widths. Source processing versions differ.' if dated else document.get('scope_note','One-year local monthly-mean connected positive-zonal component. Not a whole-current width, climatology or annual physical range. Threshold sensitivity is separate from measurement uncertainty.'),
                'source_url':sample['source_url'] if dated else document.get('source_url')})
    return rows
