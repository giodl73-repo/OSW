"""Recover a monthly mean and source-labelled deviation band, never dimensions."""
import hashlib
import json
import math
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/source-data/qiu-chen-nec-2010/figure2b-extraction.json'
OUTPUT='research/pacific-nec-monthly-bifurcation-extraction.json'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def vertices(drawing,expected):
    items=drawing['items']
    if len(items)!=expected-1 or any(item[0]!='l' for item in items):
        raise ValueError('Unexpected monthly path topology')
    result=[tuple(items[0][1])]
    for _,start,end in items:
        if tuple(start)!=result[-1]:raise ValueError('Disconnected monthly path')
        result.append(tuple(end))
    return result


def build():
    c=json.loads((ROOT/CONFIG).read_bytes())
    if digest(c['source_pdf_file'])!=c['source_pdf_sha256']:raise ValueError('Changed Pacific NEC source PDF')
    if c['expected_mean_vertices']!=24 or c['expected_band_vertices']!=48:raise ValueError('Expected two twelve-month repetitions')
    bounds=pymupdf.Rect(c['selection_bounds_points']);mean=[];band=[]
    with pymupdf.open(ROOT/c['source_pdf_file']) as pdf:
        for drawing in pdf[c['page_index']].get_drawings():
            if not bounds.contains(drawing['rect']):continue
            color=drawing.get('color');fill=drawing.get('fill');width=drawing.get('width')
            if drawing['type']=='s' and color and max(color)<c['mean_color_maximum'] and width is not None and c['mean_stroke_width_limits_points'][0]<width<c['mean_stroke_width_limits_points'][1]:
                mean.append(vertices(drawing,24))
            if drawing['type']=='f' and fill and all(c['band_fill_color_limits'][0]<v<c['band_fill_color_limits'][1] for v in fill):
                band.append(vertices(drawing,48))
    if len(mean)!=1 or len(band)!=1:raise ValueError('Unresolved mean or deviation band selection')
    mean=mean[0];band=band[0]
    left,right=c['axis_x_points'];top,bottom=c['axis_y_points'];north,south=c['axis_latitude_degrees_north']
    if not left<right or not top<bottom or not -90<=south<north<=90:raise ValueError('Invalid plot calibration')
    def latitude(y):return north+(y-top)*(south-north)/(bottom-top)
    def rounded(value):return math.copysign(math.floor(abs(value)*10**c['decimal_places']+.5)/10**c['decimal_places'],value)
    def interval(value):return [round(value-c['reading_allowance_degrees'],2),round(value+c['reading_allowance_degrees'],2)]
    cycles=[];step=(right-left)/24
    for index,(x,y) in enumerate(mean):
        if abs((x-left)/step-(index+.5))>c['month_bin_center_tolerance']:raise ValueError('Mean vertex does not match its calendar-month bin')
        endpoints=[(bx,by) for bx,by in band if abs(bx-x)<=c['band_x_agreement_tolerance_points']]
        if len(endpoints)!=2:raise ValueError('Missing or ambiguous monthly band boundaries')
        endpoints.sort(key=lambda point:latitude(point[1]));lower,upper=[latitude(point[1]) for point in endpoints];value=latitude(y)
        if not south<=lower<value<upper<=north:raise ValueError('Mean outside source band or axis support')
        if abs((lower+upper)/2-value)>c['band_symmetry_tolerance_degrees']:raise ValueError('Source band does not match the mean')
        cycles.append({'x':x,'y':y,'mean':value,'boundaries':endpoints,'range':[lower,upper]})
    for first,second in zip(cycles[:12],cycles[12:]):
        if any(abs(a-b)>c['cycle_agreement_tolerance_degrees'] for a,b in zip([first['mean'],*first['range']],[second['mean'],*second['range']])):
            raise ValueError('Repeated monthly means or bands disagree')
    months=[]
    for month,point in enumerate(cycles[:12],1):
        value=rounded(point['mean']);limits=[rounded(v) for v in point['range']]
        months.append({'month':month,'approximate_latitude_degrees_north':value,'raw_plot_latitude_degrees_north':point['mean'],
                       'mean_vertex_pdf_points':[point['x'],point['y']],'plot_reading_interval_degrees_north':interval(value),
                       'approximate_source_standard_deviation_band_degrees_north':limits,'raw_plot_source_standard_deviation_band_degrees_north':point['range'],
                       'source_band_boundary_pdf_points':[list(p) for p in point['boundaries']],
                       'band_endpoint_plot_reading_intervals_degrees_north':[interval(v) for v in limits]})
    acquisition='research/source-data/qiu-chen-nec-2010/acquisition.json';source=json.loads((ROOT/acquisition).read_bytes())
    if source['sha256']!=c['source_pdf_sha256']:raise ValueError('Acquisition and extraction source differ')
    audit='research/equatorial-bifurcation-endpoint-scope-audit.json'
    return {'schema':'osw.monthly-bifurcation-plot-extraction.v1','status':'editorial_source_plot_extraction_scientific_review_pending',
            'proposed_current_id':'pacific-north-equatorial','parent_current_id':'north-equatorial','metric':'regional_bifurcation_latitude','units':'degrees_north_signed',
            'source_url':source['source_url'],'source_doi':source['doi'],'source_locator':'Qiu and Chen (2010), figure 2b, printed page 2528, monthly mean line and shaded band.',
            'source_pdf_file':c['source_pdf_file'],'source_pdf_sha256':c['source_pdf_sha256'],'config_file':CONFIG,'config_sha256':digest(CONFIG),
            'acquisition_file':acquisition,'acquisition_sha256':digest(acquisition),'protocol_file':c['protocol_file'],'protocol_sha256':digest(c['protocol_file']),
            'scope_audit_file':audit,'scope_audit_sha256':digest(audit),'generator_sha256':digest('analysis/build_pacific_nec_monthly_bifurcation.py'),
            'series':[{'id':'surface_ssh','layer':'surface SSH-derived geostrophic diagnosis','source_period':{'start':'1992-10','end':'2009-12','precision':'month'},'period_note':None,'months':months}],
            'source_plot_repetitions':2,'distinct_observed_years_inferred':False,'reading_interval_kind':'editorial_graph_reading_allowance_not_measurement_uncertainty',
            'reading_allowance_degrees':c['reading_allowance_degrees'],'source_variability_envelope_extracted':True,
            'source_variability_kind':'caption_labelled_standard_deviation_range','statistical_denominator':None,'standard_deviation_multiplier':None,'confidence_probability':None,
            'is_confidence_interval':False,'monthly_averaging_weights_extracted':False,'individual_observations_extracted':False,'monthly_sample_counts_extracted':False,
            'whole_current_length_km':None,'current_width_km':None,'annual_dimension_range_km':None,'geometry':None,'rank_eligible':False,'annual_extrema_eligible':False,
            'chart_playback_eligible':True,'geographic_playback_eligible':False,
            'scope_note':'One historical monthly branching-latitude cycle and its source-labelled standard-deviation band. Reading allowances remain separate. Band is not a confidence interval, full observation envelope, annual extrema, current width, length or route geometry; individual years and band statistical conventions are not recovered.'}


if __name__=='__main__':
    (ROOT/OUTPUT).write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Built twelve Pacific NEC branching means and source-labelled deviation bands; no current dimensions admitted.')
