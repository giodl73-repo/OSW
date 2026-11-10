"""Render small published scalar summaries and a gap-preserving event timeline."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/loop-manta-2023-published-metrics-v1.json'
FIGURE = ROOT / 'figures/loop-manta-2023-published-metrics-v1.svg'


def resource_limit():
    if os.name == 'nt':
        import ctypes
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        if not k.SetProcessAffinityMask(k.GetCurrentProcess(), 1): raise RuntimeError('One CPU required')
        if not k.SetPriorityClass(k.GetCurrentProcess(), 0x4000): raise RuntimeError('Reduced priority required')
    else:
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))}); os.nice(10)
    for name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[name] = '1'


def validate(data):
    if data['entity_id'] != 'current:loop': raise ValueError('Wrong current owner')
    summaries = data['length_summaries']
    if [(r['mean_km'], r['temporal_standard_deviation_km']) for r in summaries] != [(1449, 487), (1495, 466)]:
        raise ValueError('Changed published scalar transcription; review original section 4.1')
    if any(r['rank_eligible'] is not False or r['uncertainty_km'] is not None
           or r['annual_minimum_km'] is not None or r['annual_maximum_km'] is not None
           or r['axis_geometry'] is not None for r in summaries):
        raise ValueError('Contour statistics cannot gain unreviewed physical scope')
    dates = [row['date'] for row in data['separation_events']]
    if len(dates) != 12 or dates != sorted(set(dates)): raise ValueError('Incomplete or duplicate event transcription')
    for row in data['separation_events']:
        dt.date.fromisoformat(row['date'])
        if any(row[key] is not None for key in ['eddy_id', 'eddy_name', 'geometry']):
            raise ValueError('Name, position or footprint needs separate identity evidence')
    if data['event_definition']['complete_full_period_event_inventory'] is not False:
        raise ValueError('Only the twelve published overlap dates are transcribed')
    return summaries, dates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', type=Path)
    args = parser.parse_args()
    resource_limit()
    data = json.loads(SOURCE.read_bytes()); summaries, dates = validate(data)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as md
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'osw-loop-published-metrics-v1'})
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 7.6), gridspec_kw={'height_ratios': [1, 2.8]})
    fig.subplots_adjust(left=.20, right=.96, top=.87, bottom=.13, hspace=.8)
    fig.suptitle('Loop Current | published contour metrics', x=.04, ha='left', y=.97, fontsize=16, weight='bold')
    fig.text(.04, .925, 'Manta et al. (2023) | source period 1993–2021 | two methods, one altimetry product', fontsize=10)
    ax = axes[0]
    labels = ['Demeaned 0.17 m', 'Maximum velocity']
    for y, row in enumerate(summaries):
        ax.scatter(row['mean_km'], y, s=65, color=['#147d92', '#ae5b16'][y], zorder=3)
        ax.annotate(f"{row['mean_km']:,} km mean; {row['temporal_standard_deviation_km']} km temporal SD",
                    (row['mean_km'], y), xytext=(12, 0), textcoords='offset points', va='center', fontsize=10)
    ax.set_yticks([0, 1], labels); ax.set_ylim(1.6, -.6)
    ax.set_xlim(1400, 1720); ax.set_xticks([1400, 1450, 1500, 1550, 1600, 1650, 1700])
    ax.set_xlabel('Mean connecting-contour length (km)')
    ax.set_title('Temporal SD is variability, not measurement error or an annual range.', loc='left', fontsize=10, pad=15)
    ax.grid(axis='x', alpha=.2)
    ax = axes[1]
    times = [dt.date.fromisoformat(value) for value in dates]
    ax.scatter(times, list(range(12)), color='#147d92', s=30, zorder=3)
    ax.set_yticks(list(range(12)), dates); ax.set_ylim(11.6, -.6)
    ax.set_xlim(dt.date(2013, 1, 1), dt.date(2021, 1, 1))
    ax.xaxis.set_major_locator(md.YearLocator()); ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
    ax.set_title('12 reported final separations | overlap subset of 48 total events', loc='left', fontsize=11, pad=12)
    ax.grid(axis='x', alpha=.25); ax.grid(axis='y', alpha=.12)
    ax.set_xlabel('Reported calendar date; timezone unspecified')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.text(.04, .055, 'Dates are source-algorithm events. No eddy names, positions or geographic tracks are inferred.', fontsize=10)
    fig.text(.04, .027, 'Source: doi:10.3389/fmars.2023.1156159, sections 2.2, 3.1 and 4.1. OSW factual redraw.', fontsize=9, color='#425466')
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE, metadata={'Date': None, 'Creator': 'OSW'})
    if args.png:
        args.png.parent.mkdir(parents=True, exist_ok=True); fig.savefig(args.png, dpi=110)
    plt.close(fig)
    print(json.dumps({'figure': str(FIGURE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      'summary_rows': 2, 'event_rows': 12, 'raw_ocean_arrays_loaded': False}))


if __name__ == '__main__': main()
