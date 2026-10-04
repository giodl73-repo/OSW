"""Read four source profiles; hidden pixels remain missing and never become axes."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/source-data/kuroshio-liu-gan-2012/figure6a-extraction.json'
OUTPUT='research/kuroshio-ecs-seasonal-width-profile-extraction.json'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def build():
    config=json.loads((ROOT/CONFIG).read_text(encoding='utf-8'))
    if digest(config['source_pdf_file'])!=config['source_pdf_sha256']:raise ValueError('Changed Kuroshio PDF')
    with pymupdf.open(ROOT/config['source_pdf_file']) as doc:
        if config['image_object'] not in [i[0] for i in doc[config['page_index']].get_images(full=True)]:raise ValueError('Changed source image location')
        pix=pymupdf.Pixmap(doc,config['image_object'])
        if pix.n!=3 or [pix.width,pix.height]!=config['image_size']:raise ValueError('Changed source image dimensions/color space')
        pixels=bytes(pix.samples)
    rgb=np.frombuffer(pixels,dtype=np.uint8).reshape(pix.height,pix.width,3).astype(int)
    seasons=[]
    for season,rule in config['color_rules'].items():
        samples=[]
        for longitude in config['sample_longitudes_degrees_east']:
            left,right=config['axis_x_pixels'];west,east=config['axis_longitude_degrees_east']
            tick=left+(longitude-west)/(east-west)*(right-left);center=round(tick);radius=config['strip_radius_pixels']
            y0,y1=config['sample_y_limits'];strip=rgb[y0:y1,center-radius:center+radius+1,:]
            if 'maximum_each_channel' in rule:mask=(strip<rule['maximum_each_channel']).all(axis=2)
            else:
                channel=rule['dominant_channel'];dominant=strip[:,:,channel]
                mask=dominant>rule['minimum_dominant']
                for other in range(3):
                    if other!=channel:mask &= dominant-strip[:,:,other]>rule['minimum_channel_difference']
            ys=np.where(mask)[0]+y0
            unique=np.unique(ys);bands=np.split(unique,np.where(np.diff(unique)>1)[0]+1) if len(unique) else []
            eligible=[b for b in bands if np.isin(ys,b).sum()>=config['minimum_selected_pixels']]
            raw=None;median=None;band=None;selected=0
            if len(eligible)==1:
                band=eligible[0];actual=ys[np.isin(ys,band)];median=float(np.median(actual));selected=len(actual)
                top,bottom=config['axis_y_pixels'];high,low=config['axis_width_km']
                raw=high-(median-top)*(high-low)/(bottom-top)
            approximate=None if raw is None else int(np.floor(raw/config['rounding_km']+.5)*config['rounding_km'])
            allowance=None if raw is None else [approximate-config['reading_margin_km'],approximate+config['reading_margin_km']]
            samples.append({'longitude_degrees_east':longitude,'status':'resolved_plot_reading' if raw is not None else 'unresolved_color_occlusion_or_ambiguity',
                            'approximate_width_km':approximate,'raw_plot_width_km':raw,'plot_reading_interval_km':allowance,
                            'tick_x_pixel':tick,'sample_x_pixel':center,'selected_y_median_pixel':median,
                            'selected_y_band_pixels':None if band is None else [int(band.min()),int(band.max())],
                            'selected_dark_or_color_pixel_count':selected,'candidate_band_count':len(eligible)})
        seasons.append({'id':'kuroshio-ecs-'+season+'-width-profile','label':season,'samples':samples,
                        'resolved_samples':sum(s['approximate_width_km'] is not None for s in samples),
                        'regional_mean_width_km':None,'calendar_months':None,'geographic_edge_coordinates':None})
    audit_file='research/kuroshio-liu-gan-2012-stream-mean-width-scope-audit.json'
    audit=json.loads((ROOT/audit_file).read_text(encoding='utf-8'))
    return {'schema':'osw.current-seasonal-width-profile-plot-extraction.v1','current_id':'kuroshio','as_of':'2026-10-04',
            'status':'editorial_plot_extraction_scientific_review_pending','source_pdf_file':config['source_pdf_file'],'source_pdf_sha256':config['source_pdf_sha256'],
            'source_image_rgb_sha256':hashlib.sha256(pixels).hexdigest(),'source_url':audit['source_url'],'source_citation':audit['source_citation'],
            'source_locator':'Figure 6a, printed page 30; method section 2.2, page 26; seasonal prose section 3.2, page 29.',
            'config_file':CONFIG,'config_sha256':digest(CONFIG),'protocol_file':config['protocol_file'],'protocol_sha256':digest(config['protocol_file']),
            'extraction_runtime':{'pymupdf':pymupdf.VersionBind,'numpy':np.__version__},
            'scope_audit_file':audit_file,'scope_audit_sha256':digest(audit_file),'generator_sha256':digest('analysis/build_kuroshio_seasonal_width_profiles.py'),
            'study_period_years':[1993,2008],'width_metric':'seasonal_mean_diagnosed_axis_normal_0.1m_s_threshold_span',
            'velocity_threshold_m_s':.1,'averaging_order':audit['averaging_order'],'source_quality_note':audit['source_quality_note'],
            'season_month_membership_resolved':False,'averaging_weight_detail_resolved':False,'seasons':seasons,'reading_margin_km':config['reading_margin_km'],
            'rounding_km':config['rounding_km'],'reading_interval_kind':'editorial_plot_reading_allowance_not_measurement_uncertainty',
            'regional_prose_measurement_ids':[v['id'] for v in audit['values']],'chart_playback_eligible':True,'geographic_playback_eligible':False,
            'whole_current_representative':False,'width_rank_eligible':False,'is_confidence_interval':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
            'whole_current_width_km':None,'annual_width_range_km':None,'section_geometry':None,'fixed_layer_bounds_m':None,'observed_period':None,
            'scope_note':'Sparse readings along regional seasonal profiles. Missing pixels stay missing; these samples do not supply geographic edges, spring/autumn regional means, full-current dimensions or annual physical extrema.'}

def main():
    data=build();(ROOT/OUTPUT).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Built Kuroshio seasonal profile readings:',{s['label']:s['resolved_samples'] for s in data['seasons']})

if __name__=='__main__':main()
