"""Section threshold intervals and full native topology, with no axis tracing."""
import calendar
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection
import numpy as np
from indian_secc_positive_bands import ROOT, REPORT, FIGURE, SOURCE, build, encoded, digest

OPERATOR = 'analysis/build_indian_secc_positive_band_figure.py'
MANIFEST = 'research/indian-secc-positive-band-figure.json'


def main():
    d = json.loads((ROOT/REPORT).read_bytes())
    if encoded(d) != encoded(build()): raise ValueError('Changed section-band report')
    source = json.loads((ROOT/SOURCE).read_bytes())
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.hashsalt': 'osw-indian-secc-positive-bands-v1'})
    fig, axes = plt.subplots(6, 2, figsize=(18, 15))
    fig.subplots_adjust(left=.055, right=.98, top=.89, bottom=.18, hspace=.7, wspace=.15)
    fig.suptitle('Indian SECC investigation · connected eastward bands', x=.055, y=.98, ha='left', fontsize=20)
    fig.text(.055, .954, '2013 OSCAR monthly means · 1,452 meridional columns · nominal 15 m · native four-neighbor positive-u connectivity', fontsize=12)
    fig.text(.055, .929, 'Every anchored component also reaches the equator/north and a source edge. Connectivity alone does not isolate the named current.', fontsize=12)
    lon, lat = np.meshgrid(source['longitude_degrees_east'], source['latitude_degrees_north'])
    cmap = plt.colormaps['RdBu_r'].copy(); cmap.set_bad('#dddddd')
    for ax, month, frame, summary in zip(axes.flat, d['months'], source['months'], d['monthly_summary']):
        image = ax.pcolormesh(lon, lat, np.array(frame['eastward_m_s'], dtype=float), shading='nearest',
                              cmap=cmap, norm=Normalize(-.4, .4), rasterized=True)
        selected = set(summary['anchor_components']); selected_segments = []; other_segments = []; sensitivity = []
        for band in month['bands']:
            for i, case in enumerate(band['threshold_cases']):
                if case['status'] != 'paired_boundaries': continue
                a = case['boundaries']['low_coordinate']['coordinate']; b = case['boundaries']['high_coordinate']['coordinate']
                segment = [(band['longitude'], a), (band['longitude'], b)]
                if i != 1: sensitivity.append(segment)
                elif band['component_id'] in selected: selected_segments.append(segment)
                else: other_segments.append(segment)
        for lines, color, width, alpha in [(sensitivity, '#ffffff', .5, .5), (other_segments, '#555555', .7, .7),
                                            (selected_segments, '#111111', .9, 1)]:
            ax.add_collection(LineCollection(lines, colors=color, linewidths=width, alpha=alpha))
        for anchor in month['anchors']:
            if anchor['component_id'] is not None:
                ax.plot(anchor['longitude'], anchor['selected_peak_latitude'], 'o', markersize=4,
                        color='#ffdf00', markeredgecolor='#111111', markeredgewidth=.7)
        split = [n for n in month['bands'] if len(n['west_neighbors']) > 1 or len(n['east_neighbors']) > 1]
        ax.scatter([n['longitude'] for n in split], [n['peak_latitude'] for n in split], marker='x', s=12,
                   linewidths=.8, c='#111111')
        ax.axhline(0, color='#222222', linewidth=.6, linestyle='--')
        ax.set_xlim(50, 90); ax.set_ylim(-10, 2); ax.set_aspect('equal')
        ax.set_xticks([50, 60, 70, 80, 90]); ax.set_yticks([-10, -6, -2, 2]); ax.tick_params(labelsize=8)
        ax.set_title(f"{calendar.month_name[month['month']]} · {summary['positive_bands']} bands / {summary['connected_components']} components · {summary['anchor_component_columns']}/121 anchor columns", loc='left', fontsize=10)
    cax = fig.add_axes([.27, .105, .46, .014]); fig.colorbar(image, cax=cax, orientation='horizontal', extend='both')
    fig.text(.5, .132, 'Monthly mean eastward velocity (m/s) · shared scale; values outside ±0.4 clipped', ha='center', fontsize=11)
    fig.text(.055, .077, 'Vertical strokes: paired 50%-peak meridional component spans. Black: anchor-connected bands; gray: other bands; white: 40% / 60% cases.', fontsize=10)
    fig.text(.055, .055, 'Circles: historical search-window peaks at 80⅓ / 80⅔ E. Crosses: grid split/merge nodes. Dashed: equator. Missing cells would remain gray.', fontsize=10)
    fig.text(.055, .033, 'These are not flow-normal widths, current axes or physical outlines. Grid connectivity can join competing jets and eddies; no dimensions admitted.', fontsize=10)
    fig.text(.055, .012, 'Equirectangular degree viewport. Source: OSCAR 2017.0 / Earth & Space Research / NOAA OceanWatch. Exact original vectors and method retained.', fontsize=9)
    assets = {}
    for suffix in ['svg', 'png']:
        path = FIGURE[:-3]+suffix
        metadata = {'Date': None, 'Creator': 'OSW'} if suffix == 'svg' else {'Software': 'OSW'}
        fig.savefig(ROOT/path, dpi=140, facecolor='white', metadata=metadata)
        assets[suffix] = {'file': path, 'sha256': digest(path), 'bytes': (ROOT/path).stat().st_size}
    plt.close(fig)
    manifest = {'schema': 'osw.indian-secc-positive-band-figure.v1', 'source_file': REPORT, 'source_sha256': digest(REPORT),
                'generator_file': OPERATOR, 'generator_sha256': digest(OPERATOR), 'figures': assets,
                'alt': 'Twelve monthly source maps with all local half-peak section spans, alternative thresholds, historical peaks and split/merge markers. Every anchor-connected positive-u component also reaches the equator or north and a source boundary; these connections do not isolate a named-current axis or width.',
                'current_geometry_admitted': False, 'source_image_redistributed': False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest, indent=2)+'\n').encode()); print(json.dumps(assets))


if __name__ == '__main__': main()
