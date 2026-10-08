"""Recover published monthly branching latitudes, never current dimensions."""
import hashlib
import json
import math
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'research/source-data/chen-madagascar-2014/figure3-extraction.json'
OUTPUT = 'research/indian-sec-monthly-bifurcation-extraction.json'


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    config = json.loads((ROOT/CONFIG).read_bytes())
    if digest(config['source_pdf_file']) != config['source_pdf_sha256']:
        raise ValueError('Changed Madagascar source PDF')
    groups = {'surface_ssh': set(), 'wod_upper400': set()}
    bounds = pymupdf.Rect(config['marker_bounds_points'])
    low, high = config['marker_size_limits_points']
    tolerance = config['marker_color_tolerance']
    with pymupdf.open(ROOT/config['source_pdf_file']) as source:
        for drawing in source[config['page_index']].get_drawings():
            rect, fill = drawing['rect'], drawing.get('fill')
            if not fill or not bounds.contains(rect) or not low < rect.width < high or not low < rect.height < high:
                continue
            if len(drawing['items']) != 4 or any(item[0] != 'c' for item in drawing['items']):
                continue
            role = ('surface_ssh' if max(fill)-min(fill) < tolerance else
                    'wod_upper400' if fill[0] > 1-tolerance and fill[1] < tolerance and fill[2] < tolerance else None)
            if role:
                # Coincident paint operations are one marker, not two samples.
                groups[role].add((round((rect.x0+rect.x1)/2,5), round((rect.y0+rect.y1)/2,5)))
    top, bottom = config['axis_y_points']
    north, south = config['axis_latitude_degrees_north']
    if not top < bottom or not -90 <= south < north <= 90:
        raise ValueError('Invalid latitude calibration')
    series = []
    for role, points in groups.items():
        points = sorted(points)
        if len(points) != config['expected_markers_per_series'] or config['duplicate_cycles'] != 2 or len(points) != 24:
            raise ValueError('Expected two plotted repetitions of twelve months: '+role)
        raw = [north+(y-top)*(south-north)/(bottom-top) for _,y in points]
        if any(abs(a-b) > config['cycle_agreement_tolerance_degrees'] for a,b in zip(raw[:12],raw[12:])):
            raise ValueError('Repeated monthly cycles disagree: '+role)
        months = []
        for month, ((x,y), value) in enumerate(zip(points[:12],raw[:12]),1):
            factor = 10**config['decimal_places']
            rounded = math.copysign(math.floor(abs(value)*factor+.5)/factor,value)
            margin = config['reading_allowance_degrees']
            months.append({'month':month,'approximate_latitude_degrees_north':rounded,
                           'raw_plot_latitude_degrees_north':value,'marker_center_pdf_points':[x,y],
                           'plot_reading_interval_degrees_north':[round(rounded-margin,2),round(rounded+margin,2)]})
        series.append({'id':role,'layer':'surface SSH-derived geostrophic diagnosis' if role=='surface_ssh' else 'upper 400 m WOD09 geostrophic mean, reference 1500 dbar',
                       'source_period':{'start':'1992-10','end':'2011-12','precision':'month'} if role=='surface_ssh' else None,
                       'period_note':None if role=='surface_ssh' else 'WOD09-based climatology; contributing observation dates not recovered here.',
                       'months':months})
    acquisition = 'research/source-data/chen-madagascar-2014/acquisition.json'
    audit = 'research/equatorial-bifurcation-endpoint-scope-audit.json'
    source = json.loads((ROOT/acquisition).read_bytes())
    return {'schema':'osw.monthly-bifurcation-plot-extraction.v1','status':'editorial_source_plot_extraction_scientific_review_pending',
            'proposed_current_id':'indian-south-equatorial','parent_current_id':'south-equatorial',
            'metric':'regional_bifurcation_latitude','units':'degrees_north_signed','source_url':source['source_url'],
            'source_doi':source['doi'],'source_locator':'Chen et al. (2014), figure 3, printed page 621, black and red markers.',
            'source_pdf_file':config['source_pdf_file'],'source_pdf_sha256':config['source_pdf_sha256'],
            'config_file':CONFIG,'config_sha256':digest(CONFIG),'acquisition_file':acquisition,'acquisition_sha256':digest(acquisition),
            'protocol_file':config['protocol_file'],'protocol_sha256':digest(config['protocol_file']),
            'scope_audit_file':audit,'scope_audit_sha256':digest(audit),'generator_sha256':digest('analysis/build_indian_sec_monthly_bifurcation.py'),
            'series':series,'source_plot_repetitions':2,'distinct_observed_years_inferred':False,
            'reading_interval_kind':'editorial_graph_reading_allowance_not_measurement_uncertainty','reading_allowance_degrees':config['reading_allowance_degrees'],
            'source_variability_envelope_extracted':False,'is_confidence_interval':False,'monthly_averaging_weights_extracted':False,
            'whole_current_length_km':None,'current_width_km':None,'annual_dimension_range_km':None,'geometry':None,
            'rank_eligible':False,'annual_extrema_eligible':False,'chart_playback_eligible':True,'geographic_playback_eligible':False,
            'scope_note':'Two historical monthly branching-latitude cycles, each repeated for plotting. Not current width, whole-current length, a dated trajectory or annual route geometry. Model curve omitted; its 400/415-m layer correspondence remains unresolved.'}


if __name__ == '__main__':
    result = build()
    (ROOT/OUTPUT).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Built two 12-month regional branching-latitude series; no current dimensions admitted.')
