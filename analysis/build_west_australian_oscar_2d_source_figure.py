"""Independent geographic vector context; no inferred current axis or edges."""
import calendar
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from matplotlib.colors import Normalize
import numpy as np

from acquire_west_australian_oscar_2d import ROOT, digest
from build_west_australian_oscar_2d_source import REPORT, build

OPERATOR = 'analysis/build_west_australian_oscar_2d_source_figure.py'
MANIFEST = 'research/west-australian-oscar-2d-source-figure.json'
STEM = 'figures/west-australian-oscar-2d-source'


def main():
    document = json.loads((ROOT/REPORT).read_bytes())
    if document != build(): raise ValueError('Changed monthly source report')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.hashsalt': 'osw-west-australian-source-v1'})
    fig, axes = plt.subplots(6, 2, figsize=(18, 11.5))
    fig.subplots_adjust(left=.055, right=.98, top=.88, bottom=.16, hspace=.85, wspace=.13)
    fig.suptitle('West Australian offshore region · surrounding OSCAR source fields', x=.055, y=.98, ha='left', fontsize=19)
    fig.text(.055, .94, '2013 monthly paired-vector means · 60–116° E / 28–36° S · nominal 15 m · at least five pairs per cell', fontsize=12)
    lon, lat = np.meshgrid(document['longitude_degrees_east'], document['latitude_degrees_north'])
    for ax, frame in zip(axes.flat, document['months']):
        u = np.array(frame['eastward_m_s'], dtype=float); v = np.array(frame['northward_m_s'], dtype=float)
        image = ax.pcolormesh(lon, lat, v, cmap='RdBu_r', norm=Normalize(-.2, .2), shading='nearest', rasterized=True)
        stride = (slice(None, None, 2), slice(None, None, 4))
        arrows = ax.quiver(lon[stride], lat[stride], u[stride], v[stride], angles='uv', scale_units='inches', scale=2,
                           color='#182b35', width=.0025, headwidth=3.5)
        ax.axhline(-32, color='#151515', linewidth=.8, linestyle='--', path_effects=[effects.Stroke(linewidth=2, foreground='white'), effects.Normal()])
        if frame['month'] == 1:
            ax.quiverkey(arrows, .86, 1.3, .1, '0.1 m/s', labelpos='E', coordinates='axes', fontproperties={'size':9})
        ax.set_xlim(60, 116); ax.set_ylim(-36, -28)
        ax.set_xticks([60, 70, 80, 90, 100, 110, 116]); ax.set_yticks([-36, -32, -28])
        ax.set_aspect(1/np.cos(np.deg2rad(32)))
        ax.tick_params(labelsize=8)
        ax.set_title(f"{calendar.month_name[frame['month']]} · {frame['available_source_times']} source times · {frame['eligible_mean_cells']}/4225 eligible cells", loc='left', fontsize=10, pad=6)
    color_ax = fig.add_axes([.27, .105, .46, .015])
    bar = fig.colorbar(image, cax=color_ax, orientation='horizontal', extend='both')
    fig.text(.5, .133, 'Monthly mean northward component (m/s) · shared fixed scale; extremes clipped', ha='center', fontsize=10)
    fig.text(.055, .065, 'Dashed: existing 32° S comparison section. Blank: insufficient paired support. Arrows show east/north direction; display stride 4 columns / 2 rows.', fontsize=10)
    fig.text(.055, .038, 'A source viewport, not a named-current footprint. No current axis, length, width or physical seasonal range inferred. Satellite-derived upper-ocean fields.', fontsize=10)
    fig.text(.055, .013, 'Source: OSCAR version2017.0 / Earth & Space Research / NOAA OceanWatch ERDDAP. Original numerical responses retained with hashes and source license.', fontsize=9)
    assets = {}
    for suffix in ['svg', 'png']:
        path = STEM+'.'+suffix
        metadata = {'Date': None, 'Creator': 'OSW'} if suffix == 'svg' else {'Software': 'OSW'}
        fig.savefig(ROOT/path, dpi=140, metadata=metadata, facecolor='white')
        assets[suffix] = {'file': path, 'sha256': digest((ROOT/path).read_bytes()), 'bytes': (ROOT/path).stat().st_size}
    plt.close(fig)
    manifest = {'schema': 'osw.west-australian-oscar-2d-source-figure.v1', 'source_file': REPORT,
                'source_sha256': digest((ROOT/REPORT).read_bytes()), 'generator_file': OPERATOR,
                'generator_sha256': digest((ROOT/OPERATOR).read_bytes()), 'figures': assets,
                'alt': 'Twelve surrounding offshore vector maps for 2013, monthly paired means, with shared northward-component colors, fixed-scale east/north arrows and the original 32 S comparison section. Blank cells have insufficient support. No named-current boundaries or dimensions are inferred.',
                'current_geometry_admitted': False, 'source_image_redistributed': False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest, indent=2)+'\n').encode())
    print(json.dumps(assets))


if __name__ == '__main__': main()
