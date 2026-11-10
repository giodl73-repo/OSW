"""Read monthly plot positions on a published half-year-filtered width curve."""
from pathlib import Path
import hashlib,json,math
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/source-data/kuroshio-liu-gan-2012/figure7a-time-extraction.json'
OUTPUT='research/kuroshio-ecs-filtered-width-time-series.json'
PROTOCOL='plans/kuroshio-filtered-width-time-series-protocol-v1.md'
AUDIT='research/kuroshio-liu-gan-2012-stream-mean-width-scope-audit.json'
ACQUISITION='research/source-data/kuroshio-liu-gan-2012/acquisition.json'
INPUTS={CONFIG:'05a0be59242a846390472334c834c71b24cfc93302d82327d43933f3ee2a0729',
 PROTOCOL:'b9bc5e3480d3917de88df916c6a1d1325c8950a7f6c853505266f62c028b7910',
 AUDIT:'607924d8b2f54393fcb150bd29b6e08f5abc99616e72b9142f879a17ded83fcd',
 ACQUISITION:'3c067c722f79ee4688de6adb176849587ce40e1612e4cd035ba4f2993eafac0d',
 'research/source-data/kuroshio-liu-gan-2012/journal-article.pdf':'a452007ff7f3b0051f811ba8172e9ae7932642ed1916a29c779db6335772203b'}

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def validate_trace(segments,tolerance):
 if not segments:raise ValueError('Missing width curve segments')
 breaks=[]
 for index,segment in enumerate(segments):
  a,b=segment['start_pdf_points'],segment['end_pdf_points']
  if not all(math.isfinite(v) for v in a+b) or not a[0]<b[0]:raise ValueError('Non-forward or nonfinite width curve segment')
  if index:
   previous=segments[index-1]['end_pdf_points']
   if a[0]<previous[0]:raise ValueError('Overlapping or reversed source time segments')
   distance=math.dist(previous,a)
   if distance>tolerance:breaks.append({'before_segment_index':index-1,'after_segment_index':index,
    'before_end_pdf_points':previous,'after_start_pdf_points':a,'separation_pdf_points':distance,'link_added':False})
 return breaks

def read_curve(config):
 with pymupdf.open(ROOT/config['source_pdf_file']) as pdf:
  drawings=pdf[config['page_index']].get_drawings();segments=[];ticks=set()
  top,bottom=config['axis_y_points'];tolerance=config['coordinate_tolerance_points'];places=config['pdf_coordinate_decimal_places']
  for drawing in drawings:
   for item in drawing['items']:
    if item[0]!='l':continue
    a,b=item[1:]
    if (abs(a.x-b.x)<tolerance and abs(min(a.y,b.y)-top)<tolerance and abs(max(a.y,b.y)-bottom)<tolerance
        and config['axis_year_x_points'][0]-tolerance<=a.x<=config['axis_year_x_points'][-1]+tolerance):
     ticks.add(round(a.x,places))
  if sorted(ticks)!=config['axis_year_x_points']:raise ValueError('Changed labeled-year grid stems')
  for path_index,count in zip(config['curve_path_indices'],config['curve_segment_counts']):
   drawing=drawings[path_index]
   if (len(drawing['items'])!=count or drawing['fill'] is not None or drawing['dashes']!='[] 0'
       or abs(drawing['width']-config['curve_stroke_width_points'])>tolerance
       or drawing['color'] is None or len(drawing['color'])!=3
       or any(abs(a-b)>tolerance for a,b in zip(drawing['color'],config['curve_stroke_color_rgb']))):
    raise ValueError('Changed source width-curve style or path')
   for path_segment_index,item in enumerate(drawing['items']):
    if item[0]!='l':raise ValueError('Unexpected nonlinear width-curve segment')
    segments.append({'segment_index':len(segments),'source_path_index':path_index,'path_segment_index':path_segment_index,
     'start_pdf_points':[round(v,places) for v in item[1]],'end_pdf_points':[round(v,places) for v in item[2]]})
 breaks=validate_trace(segments,config['coordinate_tolerance_points'])
 return segments,breaks

def reading(segments,x,config):
 matches=[]
 for segment in segments:
  a,b=segment['start_pdf_points'],segment['end_pdf_points']
  if a[0]<=x<=b[0]:
   fraction=(x-a[0])/(b[0]-a[0]);y=a[1]+fraction*(b[1]-a[1])
   matches.append({'segment':segment,'fraction_from_segment_start':fraction,'interpolated_y_pdf_points':y})
 result={'target_x_pdf_points':x,'brackets':matches,'raw_plot_width_km':None,'approximate_width_km':None,'plot_reading_interval_km':None}
 if not matches:return dict(result,status='unresolved_no_source_segment')
 ys=[m['interpolated_y_pdf_points'] for m in matches]
 if max(ys)-min(ys)>config['coordinate_tolerance_points']:return dict(result,status='unresolved_distinct_source_crossings')
 top,bottom=config['axis_y_points'];high,low=config['axis_width_km']
 raw=high-(ys[0]-top)*(high-low)/(bottom-top)
 if not low<=raw<=high:raise ValueError('Source width outside calibrated axis')
 value=int(math.floor(raw/config['rounding_km']+.5)*config['rounding_km']);margin=config['reading_allowance_km']
 return dict(result,status='resolved_filtered_curve_plot_reading',raw_plot_width_km=raw,
  approximate_width_km=value,plot_reading_interval_km=[value-margin,value+margin])

def build():
 for path,pin in INPUTS.items():
  if digest(path)!=pin:raise ValueError('Changed Kuroshio filtered-curve input: '+path)
 config=json.loads((ROOT/CONFIG).read_bytes());audit=json.loads((ROOT/AUDIT).read_bytes())
 if (config['axis_year_labels']!=list(range(1993,2010)) or config['sample_years']!=list(range(1993,2009))
     or config['sample_months']!=list(range(1,13)) or len(config['axis_year_x_points'])!=17
     or any(b<=a for a,b in zip(config['axis_year_x_points'],config['axis_year_x_points'][1:]))):
  raise ValueError('Changed source year calibration or sample grid')
 segments,breaks=read_curve(config);samples=[]
 for year in config['sample_years']:
  index=config['axis_year_labels'].index(year);left,right=config['axis_year_x_points'][index:index+2]
  for month in config['sample_months']:
   fraction=(month-.5)/12;x=left+fraction*(right-left)
   samples.append({'id':f'kuroshio-ecs-filtered-width-plot-{year}-{month:02d}',
    'sample_label':f'{year}-{month:02d} (filtered plot sample)','plot_year':year+fraction,
    'plot_year_label':year,'plot_month_label':month,'sample_time_is_observation_date':False,
    **reading(segments,x,config)})
 return {'schema':'osw.filtered-current-width-plot-time-series.v1','current_id':'kuroshio',
  'status':'editorial_source_plot_readings_scientific_review_pending',
  'source_url':audit['source_url'],'source_citation':audit['source_citation'],
  'source_locator':'Figure7a and caption, printed page30/PDF6; section3.3 printed pages30–31; method section2.2.',
  'input_sha256':dict(INPUTS),'config_file':CONFIG,'protocol_file':PROTOCOL,
  'generator_file':Path(__file__).relative_to(ROOT).as_posix(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'extraction_runtime':{'pymupdf':pymupdf.VersionBind},
  'width_metric':'half_year_filtered_regional_mean_diagnosed_axis_normal_0.1m_s_threshold_width',
  'units':'km','layer':'Surface absolute geostrophic diagnosis; no fixed-depth section boundaries extracted.',
  'geographic_scope':'Source stream mean between122–130E in the East China Sea, not the whole Kuroshio.',
  'source_study_period_years':[1993,2008],'source_product':audit['product'],
  'source_temporal_resolution':audit['source_temporal_resolution'],
  'source_method_context':{key:audit[key] for key in ['original_grid_degrees','analysis_interpolation_grid_degrees',
   'grid_interpolation_is_new_observation_resolution','averaging_order','source_quality_note']},
  'source_temporal_filter':{'source_label':'1/2 year filtered mean','kernel':None,'window_alignment':None,'endpoint_treatment':None,'filter_reproduced':False},
  'sample_time_kind':'month_midpoint_positions_between_printed_year_ticks_not_exact_UTC_dates',
  'plot_coordinate_allowance_years':config['plot_coordinate_allowance_years'],
  'monthly_sampling_is_new_source_resolution':False,'samples_are_raw_monthly_means':False,
  'independent_sample_count':None,'source_curve_segment_count':len(segments),
  'source_curve_breaks':breaks,'source_curve_breaks_bridged':False,
  'source_curve_sha256':hashlib.sha256(encoded(segments)).hexdigest(),
  'source_curve_vertices_are_observations':False,'continuous_graphic_proves_complete_observation_record':False,
  'samples':samples,'sample_count':len(samples),'resolved_sample_count':sum(s['approximate_width_km'] is not None for s in samples),
  'rounding_km':config['rounding_km'],'reading_allowance_km':config['reading_allowance_km'],
  'reading_interval_kind':'editorial_graph_reading_allowance_not_source_uncertainty_or_physical_variability',
  'measurement_uncertainty_km':None,'whole_current_width_km':None,'annual_width_range_km':None,
  'fixed_layer_bounds_m':None,'observed_period':None,'geographic_boundary_coordinates':None,
  'new_inventory_width_record_admitted':False,'width_rank_eligible':False,'annual_extrema_eligible':False,
  'whole_current_representative':False,'is_confidence_interval':False,
  'seasonal_playback_eligible':False,'geographic_playback_eligible':False,'chart_playback_eligible':True,
  'scope_note':'Month-midpoint readings of the published half-year-filtered East China Sea regional mean width curve. Month labels are graphical positions, not independent monthly means or exact observation dates. Kernel and averaging details are unresolved; reading allowances are not physical uncertainty, annual extrema or whole-current widths.',
  'cautions':['Month labels identify sampled positions on the published filtered curve, not independently observed monthly means or exact timestamps.',
   'The weekly surface geostrophic diagnosis excludes ageostrophic flow. Interpolating the original one-third-degree grid to0.1degrees adds no independent observation resolution.',
   'The source half-year filter kernel, alignment, endpoint treatment and detailed weights remain unresolved.',
   'Reading intervals reflect graphical/calibration/rounding allowance, not measurement uncertainty, confidence or annual physical variation.',
   'Existing seasonal spatial profiles and218/207/210km prose means remain separate and unchanged; no new geographic edges or whole-current dimension.']}

def verify():
 result=build()
 if (ROOT/OUTPUT).read_bytes()!=encoded(result):raise ValueError('Stale Kuroshio filtered-width readings')
 return result

if __name__=='__main__':
 report=build();(ROOT/OUTPUT).write_bytes(encoded(report))
 print(json.dumps({'samples':report['sample_count'],'resolved':report['resolved_sample_count'],
  'displayed_width_range_of_sampled_curve_km':[min(s['approximate_width_km'] for s in report['samples'] if s['approximate_width_km'] is not None),max(s['approximate_width_km'] for s in report['samples'] if s['approximate_width_km'] is not None)],'raw_monthly_means':False}))
