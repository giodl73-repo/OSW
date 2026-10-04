"""Project source-bound scoped samples for queries; never infer annual dimensions."""
import copy

FAMILIES={
    'diagnostic:leeuwin-monthly-width':'leeuwin_monthly_fitted_plot',
    'diagnostic:kuroshio-seasonal-width':'kuroshio_seasonal_profile_plot',
    'diagnostic:necc-monthly-section':'necc_monthly_connected_component',
}


def build(diagnostics):
    rows=[]
    for diagnostic in diagnostics:
        identifier=diagnostic['id']
        if identifier not in FAMILIES:continue
        document=diagnostic['document'];family=FAMILIES[identifier]
        context={k:copy.deepcopy(v) for k,v in document.items() if k not in ['months','seasons']}
        if context['whole_current_representative'] is not False or context['width_rank_eligible'] is not False or context['is_confidence_interval'] is not False or context['annual_width_range_km'] is not None:raise ValueError('Scoped samples cannot become whole-current dimensions')
        selections=[]
        if family=='kuroshio_seasonal_profile_plot':
            for phase_index,phase in enumerate(document['seasons']):
                for sample_index,sample in enumerate(phase['samples']):
                    selections.append((f'/seasons/{phase_index}/samples/{sample_index}',sample,phase,f'/seasons/{phase_index}'))
        else:
            selections=[(f'/months/{index}',sample,None,None) for index,sample in enumerate(document['months'])]
        for path,sample,phase,phase_path in selections:
            phase_context={k:copy.deepcopy(v) for k,v in phase.items() if k!='samples'} if phase else None
            label=phase['label']+' · '+str(sample['longitude_degrees_east'])+'° E' if phase else sample['label']
            value=sample.get('approximate_width_km') if family!='necc_monthly_connected_component' else sample['zero_crossing']['span_km']
            rows.append({'id':f'width-sample:{identifier.removeprefix("diagnostic:")}:{path.strip("/").replace("/",":")}',
                'entity_id':'current:'+document['current_id'],'current_id':document['current_id'],
                'label':document['current_id'].replace('-',' ').title()+' — '+label,'sample_family':family,
                'diagnostic_id':identifier,'sample_path':path,'phase_path':phase_path,
                'source_sample':copy.deepcopy(sample),'source_phase':phase_context,'source_context':copy.deepcopy(context),
                'value_km':value,'plot_reading_interval_km':copy.deepcopy(sample.get('plot_reading_interval_km')),
                'measurement_uncertainty_interval_km':None,'is_confidence_interval':False,
                'whole_current_representative':False,'width_rank_eligible':False,'annual_width_range_km':None,
                'month':sample.get('month'),'year':document.get('year'),'phase_label':phase['label'] if phase else sample['label'],
                'longitude_degrees_east':sample.get('longitude_degrees_east',document.get('section_longitude_degrees_east')),
                'metric':document.get('width_metric',document.get('width_equation')),
                'status':sample.get('status',sample.get('zero_crossing',{}).get('status',document['status'])),
                'scope':document.get('scope_note','One-year local monthly-mean connected positive-zonal component. Not a whole-current width, climatology or annual physical range. Threshold sensitivity is separate from measurement uncertainty.'),
                'source_url':document.get('source_url')})
    return rows
