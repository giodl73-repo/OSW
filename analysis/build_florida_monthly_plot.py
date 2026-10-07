"""Extract the pinned gray monthly-width curve; do not infer map boundaries."""
import hashlib,json
from pathlib import Path
import numpy as np
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/source-data/florida-archer-2017/figure9b-extraction.json'
OUTPUT='research/florida-monthly-width-plot-extraction.json'
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def build():
    config=json.loads((ROOT/CONFIG).read_bytes())
    if digest(config['source_pdf_file'])!=config['source_pdf_sha256']:raise ValueError('Changed Florida source PDF')
    with pymupdf.open(ROOT/config['source_pdf_file']) as doc:
        pix=pymupdf.Pixmap(pymupdf.csRGB,pymupdf.Pixmap(doc,config['image_object']))
        if [pix.width,pix.height]!=config['image_size']:raise ValueError('Changed Florida figure dimensions')
        pixels=bytes(pix.samples);array=np.frombuffer(pixels,dtype=np.uint8).reshape(pix.height,pix.width,3).astype(int)
    low,high=config['gray_luminance_limits'];luminance=array.mean(2)
    mask=(array.max(2)-array.min(2)<config['gray_channel_spread_max'])&(luminance>low)&(luminance<high)
    months=[]
    for month,tick in enumerate(config['month_tick_x'],1):
        center=max(config['sample_x_limits'][0],min(config['sample_x_limits'][1],tick));radius=config['strip_radius_pixels'];y0,y1=config['sample_y_limits']
        ys=np.where(mask[y0:y1,center-radius:center+radius+1])[0]+y0
        if not len(ys):raise ValueError(f'Missing Florida curve month {month}')
        unique=np.unique(ys);bands=np.split(unique,np.where(np.diff(unique)>1)[0]+1)
        band=max(bands,key=lambda b:np.isin(ys,b).sum());selected=ys[np.isin(ys,band)]
        if len(selected)<7 or len(band)<3:raise ValueError('Florida curve insufficient pixel support')
        y=float(np.median(selected));top,bottom=config['axis_y_pixels'];upper,lower=config['axis_width_km']
        raw=upper-(y-top)*(upper-lower)/(bottom-top);approx=int(np.floor(raw+.5));margin=config['reading_margin_km']
        months.append({'month':month,'label':['January','February','March','April','May','June','July','August','September','October','November','December'][month-1],
            'approximate_width_km':approx,'raw_plot_width_km':raw,'plot_reading_interval_km':[approx-margin,approx+margin],
            'reading_margin_km':margin,'tick_x_pixel':tick,'sample_x_pixel':center,'selected_y_median_pixel':y,
            'selected_y_band_pixels':[int(band.min()),int(band.max())],'selected_gray_pixel_count':int(len(selected))})
    audit_file='research/florida-hf-radar-width-statistics-scope-audit.json';audit=json.loads((ROOT/audit_file).read_bytes())
    return {'schema':'osw.current-monthly-width-plot-extraction.v1','current_id':'florida','status':'editorial_plot_extraction_scientific_review_pending',
        'as_of':'2026-10-06','source_pdf_file':config['source_pdf_file'],'source_pdf_sha256':config['source_pdf_sha256'],
        'source_image_rgb_sha256':hashlib.sha256(pixels).hexdigest(),'source_url':audit['source_url'],'source_citation':audit['source_citation'],
        'source_locator':'Figure 9b, printed page 9199; caption and section 3.4.',
        'config_file':CONFIG,'config_sha256':digest(CONFIG),'protocol_file':config['protocol_file'],'protocol_sha256':digest(config['protocol_file']),
        'scope_audit_file':audit_file,'scope_audit_sha256':digest(audit_file),'generator_sha256':digest('analysis/build_florida_monthly_plot.py'),
        'source_period_years':[2005,2006],'section_latitude':25.42,'nominal_measurement_depth_m':.75,
        'width_metric':'paired_half_core_speed_jet_coordinate_span','velocity_component':audit['velocity_component'],
        'velocity_threshold_fraction':.5,'diagnostic_time_filter':'40 h Hanning window','boundary_rule':audit['boundary_rule'],
        'curve_role':'source_plotted_overall_average_of_monthly_means','monthly_averaging_weights_extracted':False,
        'complete_monthly_curve_extracted':True,'months':months,'reading_interval_kind':'editorial_plot_reading_allowance_not_measurement_uncertainty',
        'source_variability_envelope_role':'mean within-month standard deviation','source_variability_envelope_extracted':False,
        'is_confidence_interval':False,'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'section_geometry':None,'fixed_layer_bounds_m':None,'observed_period':None,
        'chart_playback_eligible':True,'geographic_playback_eligible':False,'seasonal_playback_eligible':False,
        'scope_note':'Historical monthly mean surface-jet widths at 25.42 N from the gray Figure 9b curve (2005-2006). +/-1 km intervals are graph-reading allowances, not within-month variation or confidence. Month labels are not dated samples. No physical annual range, fixed layer, map edges or whole-current width inferred.'}
def main():
    data=build();(ROOT/OUTPUT).write_bytes((json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode())
    print('Built Florida monthly curve:',[m['approximate_width_km'] for m in data['months']])
if __name__=='__main__':main()
