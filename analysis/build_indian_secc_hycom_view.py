"""Standalone monthly source/diagnostic maps; no admitted current outline."""
import argparse
import calendar
from html import escape
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json

ROOT = Path(__file__).resolve().parents[1]


def build(directory, report_path, output):
    directory, report_path, output = map(Path, [directory, report_path, output])
    report = json.loads(report_path.read_bytes())
    quality = json.loads((directory/'quality.json').read_bytes())
    if report['source_quality'] != pin(directory/'quality.json') or quality['monthly_arrays'] != pin(directory/'monthly.npz'):
        raise ValueError('Map source differs from diagnostic source')
    output.mkdir(parents=True, exist_ok=True)
    with np.load(directory/'monthly.npz', allow_pickle=False) as archive:
        arrays = {n: archive[n] for n in archive.files}
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    lon, lat = np.meshgrid(arrays['lon'], arrays['lat'])
    months = []
    for index, summary in enumerate(report['monthly_summary']):
        m = index+1
        fig, ax = plt.subplots(figsize=(7, 7))
        fig.subplots_adjust(left=.13, right=.98, bottom=.16, top=.87)
        ax.set_facecolor('#bdbdbd')
        image = ax.pcolormesh(lon, lat, arrays['u_m_s'][index], cmap='RdBu_r', norm=Normalize(-.6, .6), shading='nearest')
        grid = (slice(None, None, 12), slice(None, None, 12))
        arrows = ax.quiver(lon[grid], lat[grid], arrays['u_m_s'][index][grid], arrays['v_m_s'][index][grid],
                           angles='uv', scale_units='inches', scale=1.4, width=.003, color='#242424')
        ax.quiverkey(arrows, .76, 1.05, .5, '0.5 m/s', labelpos='E')
        for c in report['cases']:
            if c['month'] != m or not c['primary_seed'] or c['normal_sample_step_km'] != 5:
                continue
            seed = c.get('original_seed_lon_lat')
            if seed:
                ax.plot(*seed, marker='x', color='black', markersize=6)
            for path in c['paths']:
                points = np.asarray(path['vertices_lon_lat'])
                ax.plot(points[:, 0], points[:, 1], color='#007840', linewidth=1.7, linestyle='--')
            for station in c['stations']:
                nominal = station['threshold_cases'][1]
                if nominal['status'] == 'paired_sampled_edges':
                    ends = list(nominal['edges'].values())
                    ax.plot([e['point'][0] for e in ends], [e['point'][1] for e in ends],
                            color='#111111', linewidth=1, marker='o', markersize=2, linestyle=':')
        ax.set_xlim(75, 85)
        ax.set_ylim(-12, 0)
        ax.set_aspect('equal')
        ax.set_xlabel('Longitude (degrees east)')
        ax.set_ylabel('Latitude (degrees north)')
        ax.set_title(f'{calendar.month_name[m]} 2013 | paired daily-00Z mean\nHYCOM GOFS3.1, provider 15 m; exploratory candidates', loc='left', fontsize=10)
        fig.colorbar(image, ax=ax, orientation='horizontal', fraction=.05, pad=.12, extend='both', label='Eastward component (m/s); negative = westward')
        name = f'month-{m:02d}.png'
        fig.savefig(output/name, dpi=120, metadata={'Software': 'OSW source diagnostic'})
        plt.close(fig)
        q = quality['months'][index]
        months.append({**summary, **q, 'image': name, 'image_pin': pin(output/name),
                       'outside_color_scale_cells': int((np.abs(arrays['u_m_s'][index]) > .6).sum())})
    rows = ''.join(f'<tr><th scope="row">{calendar.month_name[m["month"]]}</th><td>{m["sample_days"]}/{m["calendar_days"]}</td><td>{m["eligible_cells"]}</td><td>{m["both_step_primary_axis_passes"]}</td><td>{m["stronger_candidates"]}</td></tr>' for m in months)
    options = ''.join(f'<option value="{m}">{calendar.month_name[m]}</option>' for m in range(1, 13))
    text = [f'{calendar.month_name[m["month"]]}: {m["sample_days"]} of {m["calendar_days"]} daily 00Z samples; at least {m["minimum_pairs"]} valid paired samples required per cell. {m["eligible_cells"]} eligible cells; {m["outside_color_scale_cells"]} cells outside the fixed color scale. {m["both_step_primary_axis_passes"]} primary seeds pass all five axis checks at both steps; {m["stronger_candidates"]} also pass all-station paired-edge, resolution and hemisphere checks. Named-current identity remains unverified.' for m in months]
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Indian SECC: finer-grid investigation</title>
<style>body{font:17px/1.5 system-ui;margin:auto;max-width:900px;padding:1rem;color:#162633}img{display:block;width:100%;height:auto;max-width:840px}select,a{min-height:44px}select{font:inherit;padding:.4rem}a{color:#005d82}a:focus-visible,select:focus-visible{outline:3px solid #a65000;outline-offset:3px}table{border-collapse:collapse;font-size:.9rem;width:100%}td,th{text-align:left;border-bottom:1px solid #aaa;padding:.4rem}section{overflow:auto}.notice{border-left:4px solid #aa6100;padding:.7rem;background:#fff7e8}</style>
<header><a href="../../almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas">Back to current atlas</a><h1>Indian SECC: finer-grid investigation</h1></header>
<main><p class="notice">These are model source fields and local candidate tests. No named-current width, whole-current axis, annual range or state passage is admitted.</p>
<p>GOFS3.1 HYCOM+NCODA GLBv0.08 expt53.X, 2013, exact provider 15 m level. Monthly vectors average available paired daily 00Z samples; they are not full three-hourly monthly means, observations or climatology. Two daily samples are absent: August 14 and December 25.</p>
<p><label for="month">Month </label><select id="month">OPTIONS</select></p><p id="summary" aria-live="polite">FIRST</p>
<figure><img id="map" src="month-01.png" alt="January 2013 model vector field and exploratory local candidate paths; no admitted current outline." width="840" height="840"><figcaption>Plate carrée longitude/latitude coordinates. Color shows eastward component; arrows show paired vector direction and magnitude. Black crosses: fixed original seeds snapped to native latitude. Dashed green lines: short candidate mean-field streamlines. Dotted black cross sections: paired half-peak diagnostic spans at 5 km sampling, including failed axis checks. Gray means missing or inadequate paired support, without a separate land classification. No coastline is inferred from that mask.</figcaption></figure>
<h2>All months, including failures</h2><section aria-label="Monthly diagnostic outcomes"><table><thead><tr><th>Month</th><th>Sample days</th><th>Eligible cells</th><th>Both-step axis passes</th><th>Stronger candidates</th></tr></thead><tbody>ROWS</tbody></table></section>
<p>Both-step tests use 5 and 10 km profile sampling. Stronger candidates also require paired half-peak edges, four native grid spacings and southern-hemisphere edges at all five stations. Passing these gates would still require named-current association. Product, forcing, temporal support and depth interpretation differ from OSCAR; differences cannot be attributed solely to resolution.</p>
<h2>Source and methods</h2><ul><li><a href="https://www.hycom.org/dataserver/gofs-3pt1/reanalysis">Provider documentation</a></li><li><a href="source-responses.zip">Retained original source responses (ZIP)</a></li><li><a href="monthly.npz">Unrounded monthly vector arrays and pair counts (NPZ)</a></li><li><a href="quality.json">Source quality and response checksums</a></li><li><a href="../../research/indian-secc-hycom-2013-local-normal-spans.json">Every attempted normal section and failure (JSON)</a></li><li><a href="../../plans/indian-secc-hycom-local-normal-protocol-v1.md">Declared diagnostic rules</a></li></ul></main>
<script>const descriptions=TEXT;const control=document.getElementById('month');control.addEventListener('change',()=>{const month=Number(control.value);const image=document.getElementById('map');image.src=`month-${String(month).padStart(2,'0')}.png`;image.alt=control.selectedOptions[0].text+' 2013 model vector field and exploratory candidate paths; no admitted current outline.';document.getElementById('summary').textContent=descriptions[month-1];});</script></html>'''
    for filename in ['source-responses.zip', 'monthly.npz', 'quality.json']:
        html = html.replace(f'href="{filename}"', f'href="../../research/source-data/hycom-indian-secc-2013/{filename}"')
    html = html.replace('OPTIONS', options).replace('FIRST', escape(text[0])).replace('ROWS', rows).replace('TEXT', json.dumps(text))
    (output/'index.html').write_bytes(html.encode('utf8'))
    manifest = {'schema': 'osw.indian-secc-hycom-view.v1', 'source_quality': pin(directory/'quality.json'),
                'diagnostic_report': pin(report_path), 'generator': pin(Path(__file__)),
                'html': pin(output/'index.html'), 'months': months, 'current_geometry_admitted': False}
    write_json(output/'view.json', manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/indian-secc-hycom-2013')
    parser.add_argument('--report', type=Path, default=ROOT/'research/indian-secc-hycom-2013-local-normal-spans.json')
    parser.add_argument('--output', type=Path, default=ROOT/'figures/indian-secc-hycom-2013')
    args = parser.parse_args()
    build(args.directory, args.report, args.output)
