"""Render seven published reference points and six spectral scales, CPU1."""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/eicc-durand-2009-sampling-spectral-source-facts-v1.json'
STEM = 'figures/eicc-durand-2009-published-support-v1'


def limit_resources():
    for name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[name] = '1'
    if os.name == 'nt':
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        assert k.SetProcessAffinityMask(k.GetCurrentProcess(), 1)
        assert k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)
    else:
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(max(0, 15 - os.getpriority(os.PRIO_PROCESS, 0)))


def main():
    limit_resources()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    matplotlib.rcParams.update({'svg.hashsalt': 'osw-eicc-published-support-v1',
                                 'font.size': 10, 'font.family': 'DejaVu Sans'})
    data = json.loads((ROOT / FACTS).read_bytes())
    points, scales = data['sampling_points'], data['spectral_cross_shore_scales']
    assert len(points) == 7 and len(scales) == 6
    assert all(s['paired_current_width_km'] is None for s in scales)
    fig, (geo, spectral) = plt.subplots(1, 2, figsize=(11, 6))
    fig.subplots_adjust(left=.08, right=.98, bottom=.29, top=.78, wspace=.5)
    fig.suptitle('East India Coastal Current | published sampling and spectral support',
                 x=.05, y=.96, ha='left', fontsize=14, weight='bold')
    fig.text(.05, .905, 'Durand et al. (2009) · November 1992–July 2002 source coverage · exact published table values',
             fontsize=10, color='#425466')
    geo.set_title('Table 1: reference points\nPoints only; no coastline or route drawn', fontsize=11, pad=16)
    for p in points:
        context = p['source_point_label'] == 'G'
        geo.scatter(p['longitude_degrees_east'], p['latitude_degrees_north'], s=44,
                    color='#b35b16' if context else '#087e96', marker='D' if context else 'o', zorder=3)
        geo.annotate(p['source_point_label'], (p['longitude_degrees_east'], p['latitude_degrees_north']),
                     xytext=(6, 3), textcoords='offset points', weight='bold')
    geo.set(xlim=(78, 89), ylim=(3, 22), xlabel='Source longitude (°E)', ylabel='Source latitude (°N)')
    geo.set_aspect(1 / math.cos(math.radians(13)))
    geo.grid(alpha=.2)
    geo.text(.02, -.21, 'G / Track 142: monsoon-current outlet context;\nnot strictly on the EICC path (source §2.1).',
             transform=geo.transAxes, fontsize=9, color='#8e4b16', va='top')
    spectral.set_title('Table 3: cross-shore annual-power scales\nSpectral e-folding scales, not current widths', fontsize=11, pad=16)
    ys = list(range(6))
    spectral.scatter([s['reported_scale_km'] for s in scales], [y - .10 for y in ys], color='#087e96',
                     label='Reported annual-power e-folding scale', s=38, zorder=3)
    spectral.scatter([s['reported_theoretical_ro_over_2_km'] for s in scales], [y + .10 for y in ys],
                     edgecolors='#747d85', facecolors='none', marker='s', s=40,
                     label='Source theoretical comparison (Ro/2)', zorder=2)
    for y, row in zip(ys, scales):
        spectral.annotate(str(row['reported_scale_km']), (row['reported_scale_km'], y - .10),
                          xytext=(6, -3), textcoords='offset points', fontsize=9)
    spectral.set_yticks(ys, [f"Track {r['source_track']} ({points[y]['source_point_label']})" for y, r in enumerate(scales)])
    spectral.set(xlim=(0, 205), ylim=(5.5, -.5), xlabel='Published scale (km)')
    spectral.grid(axis='x', alpha=.2)
    spectral.legend(loc='upper left', bbox_to_anchor=(-.05, -.15), fontsize=8, frameon=False)
    for ax in (geo, spectral):
        ax.spines[['top', 'right']].set_visible(False)
    fig.text(.05, .065, 'Sampling points are maxima of variability, not axis vertices. Seafloor depths in Table 1 are not current thickness.',
             fontsize=9, color='#425466')
    fig.text(.05, .028, 'No whole-current length, paired width, annual dimension range or state intersection inferred. Source: doi:10.1029/2008JC004807',
             fontsize=9, color='#425466')
    for suffix in ['svg', 'png']:
        path = ROOT / (STEM + '.' + suffix)
        metadata = {'Date': None, 'Creator': 'OSW'} if suffix == 'svg' else {'Software': 'OSW'}
        fig.savefig(path, dpi=150, metadata=metadata)
    plt.close(fig)
    paths = [FACTS, 'analysis/render_eicc_published_support_v1.py', STEM + '.svg', STEM + '.png']
    receipt = {'schema': 'osw.eicc-published-support-figure.v1', 'status': 'RENDERED_VISUAL_REVIEW_PENDING',
               'cpu_limit': 1, 'numerical_workers': 1, 'matplotlib_version': matplotlib.__version__,
               'input_and_output_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
               'source_figure_reproduced': False, 'original_velocity_arrays_processed': False,
               'new_current_dimensions_admitted': 0, 'visual_review_complete': False}
    (ROOT / 'research/eicc-durand-2009-published-support-figure-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Rendered source table figure on one CPU; visual inspection remains required.')


if __name__ == '__main__':
    main()
