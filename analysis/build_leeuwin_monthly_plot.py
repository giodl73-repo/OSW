"""Read the pinned a101 curve from Figure 7d; never fetch or infer a footprint."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/source-data/leeuwin-deng-2008/figure7d-extraction.json'
OUTPUT='research/leeuwin-a101-monthly-plot-extraction.json'


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    config=json.loads((ROOT/CONFIG).read_text(encoding='utf-8'))
    if digest(config['source_pdf_file'])!=config['source_pdf_sha256']:raise ValueError('Changed source PDF')
    doc=pymupdf.open(ROOT/config['source_pdf_file']);pix=pymupdf.Pixmap(doc,config['image_object'])
    pix=pymupdf.Pixmap(pymupdf.csRGB,pix)
    if [pix.width,pix.height]!=config['image_size']:raise ValueError('Changed source figure dimensions')
    pixels=bytes(pix.samples)
    luminance=np.array(Image.frombytes('RGB',(pix.width,pix.height),pixels).convert('L'))
    months=[]
    for month,tick_x in enumerate(config['month_tick_x'],1):
        center=min(round(tick_x),config['maximum_sample_x']);radius=config['strip_radius_pixels']
        y0,y1=config['sample_y_limits'];mask=luminance[y0:y1,center-radius:center+radius+1]<config['dark_luminance_threshold']
        if center>config['legend_exclusion']['x_min']:mask[:config['legend_exclusion']['y_max']-y0,:]=False
        ys=np.where(mask)[0]+y0
        if not len(ys):raise ValueError(f'Missing curve month {month}')
        bands=np.split(np.unique(ys),np.where(np.diff(np.unique(ys))>1)[0]+1)
        band=max(bands,key=lambda values:sum(np.count_nonzero(ys==y) for y in values))
        selected=ys[np.isin(ys,band)];y=float(np.median(selected))
        top,bottom=config['axis_y_pixels'];high,low=config['axis_width_km']
        value=high-(y-top)*(high-low)/(bottom-top);approx=int(np.floor(value+.5));margin=config['reading_margin_km']
        anchor=next((item for item in config['prose_anchors'] if item['month']==month),None)
        if anchor and not approx-margin<=anchor['approximate_width_km']<=approx+margin:raise ValueError('Graph/prose discrepancy exceeds reading allowance')
        months.append({'month':month,'label':['January','February','March','April','May','June','July','August','September','October','November','December'][month-1],
            'approximate_width_km':approx,'raw_plot_width_km':value,'plot_reading_interval_km':[approx-margin,approx+margin],
            'reading_margin_km':margin,'tick_x_pixel':tick_x,'sample_x_pixel':center,'selected_y_median_pixel':y,
            'selected_y_band_pixels':[int(band.min()),int(band.max())],'selected_dark_pixel_count':int(len(selected)),
            'source_prose_width_km':anchor['approximate_width_km'] if anchor else None})
    audit_file='research/leeuwin-deng-2008-monthly-fitted-width-scope-audit.json'
    audit=json.loads((ROOT/audit_file).read_text(encoding='utf-8'))
    return {'schema':'osw.current-monthly-width-plot-extraction.v1','current_id':'leeuwin','status':'editorial_plot_extraction_scientific_review_pending',
        'as_of':'2026-10-04','track_id':'a101','source_pdf_file':config['source_pdf_file'],'source_pdf_sha256':config['source_pdf_sha256'],
        'source_image_rgb_sha256':hashlib.sha256(pixels).hexdigest(),'source_url':audit['source_url'],'source_citation':audit['source_citation'],
        'source_locator':'Figure 7d, printed page 144; April/September prose on page 143; method equations 1-3 on page 138.',
        'config_file':CONFIG,'config_sha256':digest(CONFIG),'protocol_file':config['protocol_file'],'protocol_sha256':digest(config['protocol_file']),
        'scope_audit_file':audit_file,'scope_audit_sha256':digest(audit_file),'generator_sha256':digest('analysis/build_leeuwin_monthly_plot.py'),
        'width_equation':audit['width_equation'],'track_angle_degrees':43.45,'averaging_order':audit['averaging_order'],
        'source_period_labels':audit['source_period_labels'],'exact_combined_averaging_period_resolved':False,
        'complete_monthly_curve_extracted':True,'months':months,'reading_interval_kind':'editorial_plot_reading_allowance_not_measurement_uncertainty',
        'is_confidence_interval':False,'whole_current_representative':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
        'whole_current_width_km':None,'annual_width_range_km':None,'section_geometry':None,'fixed_layer_bounds_m':None,'observed_period':None,
        'chart_playback_eligible':True,'geographic_playback_eligible':False,'seasonal_playback_eligible':False,
        'prose_measurement_ids':['leeuwin-a101-monthly-fit-04','leeuwin-a101-monthly-fit-09'],
        'scope_note':'Historical calendar-month means of fitted widths at one crossing. Reading intervals are graph extraction margins. July and September intervals overlap; graph readings do not establish a uniquely narrowest month. No whole-current annual extrema or current footprint inferred.'}


def main():
    data=build();(ROOT/OUTPUT).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Built 12 Leeuwin a101 graph readings:',[row['approximate_width_km'] for row in data['months']])


if __name__=='__main__':main()
