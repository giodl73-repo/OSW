"""Read a frozen original figure; retain all plotted depths and reading allowances."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
INPUT='research/pacific-sec-sun-2025-migration-extraction-input-v1.json'


def extract(pdf,figure):
    config=json.loads((ROOT/INPUT).read_bytes())
    for path,key in [(pdf,'source_pdf_sha256'),(figure,'source_figure_png_sha256')]:
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=config[key]:
            raise ValueError('Original source bytes differ: '+key)
    rgb=np.asarray(Image.open(figure).convert('RGB'))
    if list(rgb.shape[1::-1])!=config['native_image_dimensions_px']:
        raise ValueError('Original figure dimensions differ')
    rule=config['bar_detection'];cal=config['axis_calibration'];zero=cal['zero_y_px'];one=cal['one_degree_y_px']
    allowance=cal['independent_each_pick_allowance_px'];rows=[]
    for panel in config['panels']:
        x0,y0,x1,y1=panel['crop_px'];crop=rgb[y0:y1,x0:x1]
        mask=np.ones(crop.shape[:2],dtype=bool)
        for channel,key in enumerate(['red_range','green_range','blue_range']):
            lo,hi=rule[key];mask&=(crop[:,:,channel]>=lo)&(crop[:,:,channel]<=hi)
        columns=np.flatnonzero(mask.sum(axis=0)>=rule['minimum_column_orange_pixels'])
        groups=np.split(columns,np.flatnonzero(np.diff(columns)>1)+1)
        if len(groups)!=12 or any(len(g)<10 for g in groups):
            raise ValueError('Expected twelve distinct source bars: '+panel['panel'])
        for depth,group in zip(config['depths_m'],groups):
            inner=group[len(group)//4:len(group)-len(group)//4]
            tops=[int(np.flatnonzero(mask[:,x])[0])+y0 for x in inner]
            bottoms=[int(np.flatnonzero(mask[:,x])[-1])+y0 for x in inner]
            if max(abs(v-zero) for v in bottoms)>3:
                raise ValueError('Bar does not reach source baseline')
            top=float(np.median(tops));value=(zero-top)/(zero-one)
            if not 0<=value<=1.2:raise ValueError('Unexpected calibrated migration')
            limits=[]
            for dt,dz,do in itertools.product([-allowance,allowance],repeat=3):
                limits.append(((zero+dz)-(top+dt))/((zero+dz)-(one+do)))
            lo=max(0,math.floor(min(limits)*100)/100);hi=math.ceil(max(limits)*100)/100
            rows.append({'id':f'pacific-sec-sun2025-{abs(panel["longitude"])}w-{depth}m-core-migration',
                'current_id':'pacific-south-equatorial','entity_id':config['entity_id'],
                'component':'southern_branch','section_longitude_degrees_east':panel['longitude'],
                'sampling_depth_m':depth,'source_panel':panel['panel'],
                'approximate_migration_degrees':round(round(value/0.02)*0.02,2),
                'plot_reading_interval_degrees':[lo,hi],'interval_includes_zero':lo==0,
                'source_pixel_bar':{'x_first':int(group[0])+x0,'x_last':int(group[-1])+x0,
                    'median_top_y':top,'median_bottom_y':float(np.median(bottoms))},
                'value_kind':'OSW_plot_reading_of_author_core_migration',
                'period_years':[1960,2020],'temporal_operator_status':'author_figure_period_only_not_reconstructed_annual_series',
                'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
                'length_rank_eligible':False,'width_rank_eligible':False,'physical_state_join_eligible':False})
    return {'schema':'osw.published-core-migration-profile-prepared.v1',
        'status':'SOURCE_PLOT_EXTRACTED_QUERY_AND_PRESENTATION_ADMISSION_PENDING',
        'source_doi':config['doi'],'source_pdf_sha256':config['source_pdf_sha256'],
        'source_figure_png_sha256':config['source_figure_png_sha256'],
        'input_sha256':hashlib.sha256((ROOT/INPUT).read_bytes()).hexdigest(),
        'units':'degree_latitude_poleward','rows':rows,
        'plot_reading_interval_is_measurement_uncertainty':False,
        'source_depth_profile_is_current_thickness':False,
        'source_derived_values_are_independent_in_situ_observations':False,
        'new_whole_current_lengths':0,'new_widths':0,'new_annual_ranges':0,
        'installed':False,'full_goal_complete':False}


def figure_svg(data):
    # Side-by-side panels retain source depth ordering; no interpolation between depths.
    from html import escape
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="820" viewBox="0 0 1000 820" role="img" aria-labelledby="title desc">',
        '<title id="title">Pacific SEC southern branch: core migration varies with depth</title>',
        '<desc id="desc">Twenty-four approximate readings of Figure2c and2f in Sun and Zhang2025. Horizontal ticks show plot-reading allowances, not confidence intervals. Neither length nor width is measured.</desc>',
        '<rect width="1000" height="820" fill="#f2f7f8"/>',
        '<g font-family="Arial,sans-serif" fill="#163b49">',
        '<text x="32" y="40" font-size="25" font-weight="bold">Pacific SEC southern branch</text>',
        '<text x="32" y="70" font-size="19">Core migration by depth · source period 1960–2020</text>']
    for lon,left in [(-170,105),(-160,575)]:
        top=145;bottom=610;width=355
        parts.append(f'<text x="{left}" y="112" font-size="21" font-weight="bold">{abs(lon)}°W section</text>')
        for val in [0,0.2,0.4,0.6,0.8,1,1.2]:
            x=left+width*val/1.2
            parts.append(f'<path d="M{x} {top}V{bottom}" stroke="#ccdce1"/><text x="{x}" y="638" text-anchor="middle" font-size="16">{val:g}</text>')
        for r in data['rows']:
            if r['section_longitude_degrees_east']!=lon:continue
            depth=r['sampling_depth_m'];y=top+(depth-50)/550*(bottom-top)
            lo,hi=r['plot_reading_interval_degrees'];x=left+width*r['approximate_migration_degrees']/1.2
            xl=left+width*lo/1.2;xh=left+width*hi/1.2
            parts.append(f'<text x="{left-12}" y="{y+5}" text-anchor="end" font-size="16">{depth}</text><path d="M{left} {y}H{left+width}" stroke="#e1eaed"/>')
            parts.append(f'<g><title>{escape(str(depth))}m: approximately {r["approximate_migration_degrees"]:.2f}°, reading interval {lo:.2f}–{hi:.2f}°</title><path d="M{xl} {y}H{xh}M{xl} {y-5}V{y+5}M{xh} {y-5}V{y+5}" stroke="#98621c" stroke-width="2"/><circle cx="{x}" cy="{y}" r="4.5" fill="#087f8c"/></g>')
        parts.append(f'<text x="{left+width/2}" y="665" text-anchor="middle" font-size="17">Poleward migration (degrees latitude)</text>')
    parts+=['<text x="30" y="130" font-size="16">Depth</text><text x="30" y="150" font-size="16">(m)</text>',
        '<text x="32" y="709" font-size="17">Dots: approximate source-plot readings. Ticks: reading allowance, not physical uncertainty.</text>',
        '<text x="32" y="737" font-size="17">Regional decadal change; no whole-current length, width, annual range or seasonal animation.</text>',
        '<text x="32" y="766" font-size="17">Underlying mapped field: 1° grid. Reading precision does not improve physical resolution.</text>',
        '<text x="32" y="796" font-size="16">Source: Sun &amp; Zhang (2025), Fig.2c,f · doi:10.1186/s40562-025-00393-7 · OSW redraw</text>',
        '</g></svg>']
    return '\n'.join(parts)+'\n'


def compact_svg(data):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="360" height="1350" viewBox="0 0 360 1350" role="img" aria-labelledby="title desc">',
        '<title id="title">Pacific SEC southern branch core migration</title>',
        '<desc id="desc">Two regional depth profiles read from Sun and Zhang2025 Figure2. Plot-reading allowances are not scientific uncertainty.</desc>',
        '<rect width="360" height="1350" fill="#f2f7f8"/>',
        '<g font-family="Arial,sans-serif" fill="#163b49">',
        '<text x="14" y="30" font-size="22" font-weight="bold">Pacific SEC · southern branch</text>',
        '<text x="14" y="58" font-size="19">Core migration by depth</text>',
        '<text x="14" y="85" font-size="18">Source period: 1960–2020</text>']
    for lon,top in [(-170,163),(-160,661)]:
        left=62;width=273;bottom=top+330
        parts.append(f'<text x="14" y="{top-38}" font-size="20" font-weight="bold">{abs(lon)}°W section</text><text x="14" y="{top-13}" font-size="17">Depth (m)</text>')
        for val in [0,0.4,0.8,1.2]:
            x=left+width*val/1.2
            parts.append(f'<path d="M{x} {top}V{bottom}" stroke="#ccdce1"/><text x="{x}" y="{bottom+27}" text-anchor="middle" font-size="17">{val:g}</text>')
        for r in data['rows']:
            if r['section_longitude_degrees_east']!=lon:continue
            depth=r['sampling_depth_m'];y=top+(depth-50)/550*330
            lo,hi=r['plot_reading_interval_degrees'];x=left+width*r['approximate_migration_degrees']/1.2
            xl=left+width*lo/1.2;xh=left+width*hi/1.2
            parts.append(f'<text x="{left-12}" y="{y+5}" text-anchor="end" font-size="17">{depth}</text><path d="M{left} {y}H{left+width}" stroke="#e1eaed"/><path d="M{xl} {y}H{xh}M{xl} {y-5}V{y+5}M{xh} {y-5}V{y+5}" stroke="#98621c" stroke-width="2"/><circle cx="{x}" cy="{y}" r="4.5" fill="#087f8c"/>')
        parts.append(f'<text x="14" y="{bottom+57}" font-size="17">Poleward migration (degrees latitude)</text>')
    lines=['Dots: approximate plot readings.','Ticks: plot-reading allowance,','not physical uncertainty.','Underlying field: 1° grid. Reading','precision adds no physical resolution.','No whole-current length or width,','annual range or seasonal animation.','Sun &amp; Zhang (2025), Fig.2c,f','doi:10.1186/s40562-025-00393-7','OSW redraw; source profiles retained.']
    for i,line in enumerate(lines):parts.append(f'<text x="14" y="{1085+24*i}" font-size="17">{line}</text>')
    return '\n'.join(parts+['</g></svg>'])+'\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-pdf',type=Path,required=True);parser.add_argument('--figure-png',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--svg',type=Path,required=True)
    parser.add_argument('--compact-svg',type=Path)
    args=parser.parse_args();data=extract(args.original_pdf,args.figure_png)
    args.output.write_bytes((json.dumps(data,indent=2)+'\n').encode());args.svg.write_bytes(figure_svg(data).encode())
    if args.compact_svg:args.compact_svg.write_bytes(compact_svg(data).encode())
    print('Retained24 source-plot migration readings; no length or width admission.')
